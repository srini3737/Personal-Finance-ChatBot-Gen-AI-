from abc import ABC, abstractmethod
from typing import Union, AsyncIterator


class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Either a complete string response or an async iterator for streaming
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model being used."""
        pass
