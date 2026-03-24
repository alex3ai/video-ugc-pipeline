from typing import Optional
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

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
                self.client = InferenceClient(
                    token=hf_token
                )
                self.model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B")
                self.provider_name = os.getenv("HF_PROVIDER", "featherless-ai")
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
                    self.client = InferenceClient(
                        token=hf_token
                    )
                    self.model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B")
                    self.provider_name = os.getenv("HF_PROVIDER", "featherless-ai")
                else:
                    raise ValueError("Either GROK_API_KEY or (HF_TOKEN/LLAMA_API_KEY/HF_API_KEY) must be set")

    async def test_connection(self) -> bool:
        """
        Test the connection to the appropriate LLM API with a simple request
        """
        try:
            if self.provider == "grok":
                import requests
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
                # Test using the InferenceClient
                test_result = self.client.text_generation(
                    "Hello, how are you?",
                    model=self.model,
                    max_new_tokens=10
                )
                
                return test_result is not None
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
                import requests
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
                            model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B")
                            
                            result = client.text_generation(
                                prompt,
                                model=model,
                                max_new_tokens=500,
                                temperature=0.7
                            )
                            
                            return result
                        else:
                            print("No HuggingFace token available for fallback")
            else:  # huggingface
                result = self.client.text_generation(
                    prompt,
                    model=self.model,
                    max_new_tokens=500,
                    temperature=0.7,
                    top_p=0.95
                )
                
                return result

            return None
        except Exception as e:
            print(f"Error generating prompt from brief: {e}")
            return None


def get_llm_service():
    """
    Get or create LLMService instance (lazy initialization)
    """
    global _llm_service_instance
    if '_llm_service_instance' not in globals():
        _llm_service_instance = LLMService()
    return _llm_service_instance


def test_llm_connection():
    """
    Test function to verify the connection to the configured LLM API
    """
    try:
        import asyncio

        async def _test():
            service = get_llm_service()
            return await service.test_connection()

        return asyncio.run(_test())
    except Exception as e:
        print(f"Error during connection test: {e}")
        return False