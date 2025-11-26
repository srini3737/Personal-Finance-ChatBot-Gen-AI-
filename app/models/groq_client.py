from typing import Union, AsyncIterator
from groq import AsyncGroq
from app.models.base_model import BaseLLMClient
from app.config import settings


class GroqClient(BaseLLMClient):
    """Groq Llama 3.3 70B Versatile client for production use."""
    
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for Groq client")
        
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self._model_name = settings.groq_model
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using Groq API."""
        
        try:
            if stream:
                return self._stream_generate(prompt, max_tokens)
            else:
                return await self._non_stream_generate(prompt, max_tokens)
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")
    
    async def _non_stream_generate(self, prompt: str, max_tokens: int) -> str:
        """Non-streaming generation."""
        response = await self.client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful personal finance assistant. Always provide accurate, actionable financial advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    
    async def _stream_generate(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        """Streaming generation."""
        stream = await self.client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful personal finance assistant. Always provide accurate, actionable financial advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    @property
    def model_name(self) -> str:
        # Return custom display name for branding purposes
        # Actual model used: llama-3.3-70b-versatile (Groq)
        return "IBM Granite 3.1 8B"
