from typing import Optional
import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from config import settings

load_dotenv()

FREE_SERVERLESS_MODELS = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct",  # principal — você já tem acesso
    "meta-llama/Meta-Llama-3-8B-Instruct",    # fallback
    "Qwen/Qwen2.5-7B-Instruct",               # fallback extra
]

class LLMService:
    def __init__(self):
        use_free_only = os.getenv("GROK_USE_FREE_ONLY", "").lower() in ["true", "1", "yes"]
        hf_token = os.getenv("HF_TOKEN") or os.getenv("LLAMA_API_KEY") or os.getenv("HF_API_KEY")

        if use_free_only:
            if hf_token:
                self.provider = "huggingface"
                self.client = InferenceClient(token=hf_token)
                self.model = settings.HF_MODEL
                self.provider_name = None  # NUNCA usa router externo
            else:
                raise ValueError("HF_TOKEN ou HF_API_KEY obrigatório")
        else:
            grok_key = os.getenv("GROK_API_KEY")
            if grok_key:
                self.provider = "grok"
                self.api_key = grok_key
                self.api_url = os.getenv("GROK_API_BASE_URL", "https://api.x.ai/v1")
                self.model = os.getenv("GROK_MODEL", "grok-beta")
            elif hf_token:
                self.provider = "huggingface"
                self.client = InferenceClient(token=hf_token)
                self.model = settings.HF_MODEL
                self.provider_name = None  # NUNCA usa router externo
            else:
                raise ValueError("GROK_API_KEY ou HF_TOKEN obrigatório")

    def _try_hf_serverless(self, messages: list, max_tokens: int = 500) -> Optional[str]:
        """Usa HF Serverless direto — sem Together, sem custo"""
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY")
        if not hf_token:
            return None

        client = InferenceClient(token=hf_token)

        for model in FREE_SERVERLESS_MODELS:
            try:
                print(f"Tentando modelo: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                content = response.choices[0].message.content
                if content:
                    print(f"Sucesso com: {model}")
                    return content
            except Exception as e:
                print(f"Modelo {model} falhou: {e}")
                continue
        return None

    async def test_connection(self) -> bool:
        try:
            if self.provider == "grok":
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"model": self.model, "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 10, "stream": False}
                r = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=payload, timeout=30)
                return r.status_code == 200
            else:
                result = self._try_hf_serverless([{"role": "user", "content": "Hello"}], max_tokens=20)
                return result is not None
        except Exception as e:
            print(f"Erro no teste de conexão: {e}")
            return False

    async def generate_prompt_from_brief(self, brief: str) -> Optional[str]:
        try:
            prompt = f"""Based on the following campaign brief, generate a detailed prompt for a video generation AI.

Campaign Brief: {brief}

Generate a creative and detailed prompt that describes a video scene with vivid details,
including visual elements, actions, duration, and any important aspects for video generation.
Keep the prompt under 500 words."""

            if self.provider == "grok":
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000, "temperature": 0.7, "stream": False}
                r = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=payload, timeout=60)
                if r.status_code == 200:
                    choices = r.json().get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                print(f"Grok erro {r.status_code}. Usando HF Serverless como fallback...")

            return self._try_hf_serverless([{"role": "user", "content": prompt}], max_tokens=500)

        except Exception as e:
            print(f"Erro ao gerar prompt: {e}")
            import traceback
            traceback.print_exc()
            return None


_llm_service_instance = None

def get_llm_service():
    global _llm_service_instance
    _llm_service_instance = LLMService()
    return _llm_service_instance

async def test_llm_connection():
    return await get_llm_service().test_connection()
