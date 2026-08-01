import json
import logging
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger("researchmind")

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates a text completion for the given prompt."""
        pass


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}. Returning fallback response.")
            return f"[Fallback] Ollama model '{self.model_name}' failed to generate: {e}"


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url or "https://api.openai.com/v1"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return f"[Fallback] OpenAI API model '{self.model_name}' failed to generate: {e}"


class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.pipeline = None
        self._initialize()

    def _initialize(self):
        try:
            import torch
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            logger.info(f"Loading local HuggingFace model: {self.model_id}...")
            # Load tokenizer and model using optimum options
            tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            )
            self.pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
            logger.info("Local HuggingFace model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace pipeline: {e}. Falling back to mock generator.")
            self.pipeline = None

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.pipeline:
            return f"[Mock HF] Generation prompt: {prompt[:100]}... (Model {self.model_id} was not loaded)"
            
        full_prompt = f"System: {system_prompt}\nUser: {prompt}\nAssistant:" if system_prompt else f"User: {prompt}\nAssistant:"
        try:
            outputs = self.pipeline(
                full_prompt, 
                max_new_tokens=512, 
                do_sample=True, 
                temperature=0.2,
                top_p=0.9
            )
            generated_text = outputs[0]["generated_text"]
            # Extract Assistant response
            if "Assistant:" in generated_text:
                return generated_text.split("Assistant:")[-1].strip()
            return generated_text[len(full_prompt):].strip()
        except Exception as e:
            logger.error(f"HF pipeline generation failed: {e}")
            return f"[Fallback] HuggingFace local pipeline error: {e}"


class EmbeddingService:
    def __init__(self, provider: str = "local", model_name: str = "all-MiniLM-L6-v2", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider  # local, ollama, openai
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url or "http://localhost:11434"
        self.local_model = None
        self._initialize_local()

    def _initialize_local(self):
        if self.provider == "local":
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local SentenceTransformer model '{self.model_name}'...")
                self.local_model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer loaded successfully.")
            except Exception as e:
                logger.warning(f"SentenceTransformer not loaded ({e}). Local execution will fall back to simulated embeddings.")
                self.local_model = None

    def get_embedding(self, text: str) -> List[float]:
        """Generates a 384-dimensional or 1536-dimensional vector for text."""
        if not text:
            return [0.0] * 384

        if self.provider == "local" and self.local_model:
            try:
                emb = self.local_model.encode(text).tolist()
                return emb
            except Exception as e:
                logger.error(f"SentenceTransformer encode failed: {e}")

        # Fallback to Ollama embedding endpoint
        if self.provider == "ollama" or (self.provider == "local" and not self.local_model):
            url = f"{self.base_url.rstrip('/')}/api/embeddings"
            payload = {
                "model": "qwen2:7b" if self.model_name == "all-MiniLM-L6-v2" else self.model_name,
                "prompt": text
            }
            try:
                response = requests.post(url, json=payload, timeout=20)
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
            except Exception as e:
                logger.debug(f"Ollama embedding failed ({e}). Attempting mock vector.")

        # Fallback to OpenAI
        if self.provider == "openai" and self.api_key:
            url = "https://api.openai.com/v1/embeddings"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"input": text, "model": "text-embedding-ada-002"}
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                logger.error(f"OpenAI embedding failed: {e}")

        # Zero-dependency deterministic fallback (TF-IDF mock vector) for testing & resilience
        # Generate a stable 384-dimensional vector based on string hash values
        import hashlib
        vector = []
        for i in range(384):
            val = int(hashlib.md5(f"{text}_{i}".encode("utf-8")).hexdigest(), 16)
            vector.append((val % 2000 - 1000) / 1000.0)
        # Normalize vector
        norm = sum(x**2 for x in vector)**0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

def get_llm_provider() -> BaseLLMProvider:
    """Helper factory for loading LLM providers based on application configurations."""
    from backend.app.core.config import settings
    if settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY:
        return OpenAIProvider(settings.LLM_API_KEY, settings.LLM_MODEL)
    elif settings.LLM_PROVIDER == "huggingface":
        return HuggingFaceProvider(settings.LLM_MODEL)
    else:
        # Default is Ollama
        return OllamaProvider(settings.LLM_MODEL, settings.LLM_BASE_URL)
