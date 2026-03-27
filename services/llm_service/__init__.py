from typing import Optional
import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from config import settings

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        """
        Initialize the LLM Service with priority for free providers first
        """
        # First, check if GROK_USE_FREE_ONLY is set to true, which means to skip Grok entirely
        use_free_only = os.getenv("GROK_USE_FREE_ONLY", "").lower() in ["true", "1", "yes"]
        
        # If free-only mode is enabled, skip Grok and go straight to HuggingFace
        if use_free_only:
            hf_token = os.getenv("HF_TOKEN") or os.getenv("LLAMA_API_KEY") or os.getenv("HF_API_KEY")
            if hf_token:
                self.provider = "huggingface"
                self.model = settings.HF_MODEL
                self.provider_name = settings.HF_PROVIDER
                # Configurar o InferenceClient com provider explícito para evitar auto-router
                self.client = InferenceClient(
                    provider=self.provider_name,
                    api_key=hf_token
                )
            else:
                raise ValueError("In free-only mode, HF_TOKEN, LLAMA_API_KEY or HF_API_KEY must be set")
        else:
            # Try to use Grok first
            grok_key = os.getenv("GROK_API_KEY")
            if grok_key:
                self.provider = "grok"
                self.api_key = grok_key
                self.api_url = os.getenv("GROK_API_BASE_URL", "https://api.x.ai/v1")
                self.model = os.getenv("GROK_MODEL", "grok-beta")
            else:
                # If no Grok key, try HuggingFace
                hf_token = os.getenv("HF_TOKEN") or os.getenv("LLAMA_API_KEY") or os.getenv("HF_API_KEY")
                if hf_token:
                    self.provider = "huggingface"
                    self.model = settings.HF_MODEL
                    self.provider_name = settings.HF_PROVIDER
                    # Configurar o InferenceClient com provider explícito para evitar auto-router
                    self.client = InferenceClient(
                        provider=self.provider_name,
                        api_key=hf_token
                    )
                else:
                    raise ValueError("Either GROK_API_KEY or (HF_TOKEN/LLAMA_API_KEY/HF_API_KEY) must be set")

    async def test_connection(self) -> bool:
        """
        Test the connection to the appropriate LLM API with a simple request
        """
        try:
            if self.provider == "grok":
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10,
                    "stream": False
                }

                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                return response.status_code == 200
            else:  # huggingface
                # Test using the InferenceClient with chat completions
                try:
                    # Construir a URL correta com o provider para testes
                    if self.provider_name:
                        # Fazer uma chamada direta para o endpoint do provedor
                        hf_api_key = os.getenv("HF_API_KEY")
                        api_url = f"https://router.huggingface.co/{self.provider_name}/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {hf_api_key}", "Content-Type": "application/json"}
                        
                        payload = {
                            "model": self.model,
                            "messages": [{"role": "user", "content": "Hello"}],
                            "max_tokens": 20,
                            "temperature": 0.7
                        }
                        
                        response = requests.post(api_url, headers=headers, json=payload)
                        return response.status_code == 200
                    else:
                        # Teste padrão com o InferenceClient
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=20
                        )
                        return response is not None
                except Exception as e:
                    print(f"Error testing HuggingFace connection: {e}")
                    return False
        except Exception as e:
            print(f"Error testing {self.provider} connection: {e}")
            return False

    async def generate_prompt_from_brief(self, brief: str) -> Optional[str]:
        """
        Generate a video prompt from a campaign brief using the configured LLM provider
        """
        try:
            prompt = f"""
                Based on the following campaign brief, generate a detailed prompt for a video generation AI.
                
                Campaign Brief: {brief}
                
                Generate a creative and detailed prompt that describes a video scene with vivid details,
                including visual elements, actions, duration, and any important aspects for video generation.
                Keep the prompt under 500 words.
            """

            if self.provider == "grok":
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "stream": False
                }

                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    choices = result.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                        
                    print(f"Warning: Unexpected Grok API response format: {result}")
                else:
                    error_detail = response.text
                    print(f"Error: Grok API returned status code {response.status_code}")
                    print(f"Response: {error_detail}")
                    
                    # Check if it's a credit/licensing issue
                    if response.status_code == 403:
                        print("This error may indicate that your team does not have credits or proper licensing.")
                        print("Falling back to Hugging Face Llama as free alternative...")
                        # Attempt to use HuggingFace temporarily
                        hf_token = os.getenv("HF_TOKEN") or os.getenv("LLAMA_API_KEY") or os.getenv("HF_API_KEY")
                        if hf_token:
                            client = InferenceClient(token=hf_token)
                            model = settings.HF_MODEL
                            provider_name = settings.HF_PROVIDER
                            
                            response = client.chat.completions.create(
                                model=model,
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=500,
                                temperature=0.7
                            )
                            
                            return response.choices[0].message.content
                        else:
                            print("No HuggingFace token available for fallback")
            else:  # huggingface
                # Primeiro tentar com o endpoint do provedor específico
                if self.provider_name:
                    try:
                        hf_api_key = os.getenv("HF_API_KEY")
                        api_url = f"https://router.huggingface.co/{self.provider_name}/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {hf_api_key}", "Content-Type": "application/json"}
                        
                        payload = {
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 500,
                            "temperature": 0.7,
                            "top_p": 0.95
                        }
                        
                        response = requests.post(api_url, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            result = response.json()
                            choices = result.get("choices", [])
                            if choices:
                                return choices[0].get("message", {}).get("content", "")
                            else:
                                print(f"Unexpected router.huggingface.co API response format: {result}")
                        else:
                            print(f"Router.huggingface.co API error: {response.status_code}, {response.text}")
                            if response.status_code == 404:
                                print("Model may not be served by this provider. Trying direct InferenceClient...")
                    except Exception as e:
                        print(f"Error with router.huggingface.co endpoint: {e}")
                
                # Se o provedor falhar ou não estiver configurado, usar o InferenceClient padrão
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500,
                        temperature=0.7,
                        top_p=0.95
                    )
                    
                    return response.choices[0].message.content
                except Exception as e:
                    print(f"HuggingFace API error: {e}")
                    # Se o modelo não estiver disponível com o provedor, tentar com um modelo alternativo
                    try:
                        # Usar modelo Llama 3.2 leve e suportado via HF
                        response = self.client.chat.completions.create(
                            model="meta-llama/Llama-3.2-3B-Instruct",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=500,
                            temperature=0.7
                        )
                        return response.choices[0].message.content
                    except Exception as fallback_error:
                        print(f"All attempts to generate prompt failed: {fallback_error}")
                        return None

            return None
        except Exception as e:
            print(f"Error generating prompt from brief: {e}")
            import traceback
            traceback.print_exc()
            return None

# Create a global instance of LLMService
_llm_service_instance = None

def get_llm_service():
    """
    Get or create the singleton instance of LLMService
    """
    global _llm_service_instance
    # Forçar reconstrução da instância para garantir que as configurações estejam atualizadas
    _llm_service_instance = LLMService()
    return _llm_service_instance

async def test_llm_connection():
    """
    Test the connection to the LLM service
    """
    llm_service = get_llm_service()
    return await llm_service.test_connection()