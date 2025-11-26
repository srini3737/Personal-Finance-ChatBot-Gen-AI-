from typing import Union, AsyncIterator
import httpx
from app.models.base_model import BaseLLMClient
from app.config import settings


class OllamaGraniteClient(BaseLLMClient):
    """IBM Granite client via Ollama for production use."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self._model_name = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using Ollama API."""
        
        try:
            if stream:
                return self._stream_generate(prompt, max_tokens)
            else:
                return await self._non_stream_generate(prompt, max_tokens)
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    async def _non_stream_generate(self, prompt: str, max_tokens: int) -> str:
        """Non-streaming generation."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
            }
        }
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    async def _stream_generate(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        """Streaming generation."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
            }
        }
        
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
