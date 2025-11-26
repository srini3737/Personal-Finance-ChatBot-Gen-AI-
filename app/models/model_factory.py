from app.models.base_model import BaseLLMClient
from app.models.groq_client import GroqClient
from app.models.ollama_granite import OllamaGraniteClient
from app.models.fallback_mock import FallbackMockClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating LLM clients based on environment configuration and purpose."""
    
    _groq_instance: BaseLLMClient = None
    _granite_instance: BaseLLMClient = None
    _mock_instance: BaseLLMClient = None
    
    @classmethod
    def get_client(cls, purpose: str = "general") -> BaseLLMClient:
        """
        Get the appropriate LLM client based on APP_ENV.
        
        In prod mode: All purposes use Groq (chat, budget, insights, general)
        In local mode: Always returns Mock client regardless of purpose.
        
        Args:
            purpose: The intended use case - "chat", "budget_summary", "spending_insights", or "general"
        
        Returns:
            BaseLLMClient instance appropriate for the environment
        """
        # Local mode - always use mock
        if settings.app_env == "local":
            if cls._mock_instance is None:
                logger.info("Using Mock LLM client (local mode)")
                cls._mock_instance = FallbackMockClient()
            return cls._mock_instance
        
        # Production mode - all purposes use Groq
        # (Chat, budget, insights, and general all use Groq)
        if cls._groq_instance is None:
            if settings.groq_api_key:
                try:
                    logger.info(f"Initializing Groq client for {purpose}")
                    cls._groq_instance = GroqClient()
                    logger.info("Successfully initialized Groq client")
                except Exception as e:
                    logger.error(f"Failed to initialize Groq client: {e}")
                    logger.warning(f"Falling back to Mock client for {purpose}")
                    if cls._mock_instance is None:
                        cls._mock_instance = FallbackMockClient()
                    return cls._mock_instance
            else:
                logger.warning(f"No Groq API key found for {purpose}, using Mock client")
                if cls._mock_instance is None:
                    cls._mock_instance = FallbackMockClient()
                return cls._mock_instance
        return cls._groq_instance
    
    @classmethod
    def reset(cls):
        """Reset all singleton instances (useful for testing)."""
        cls._groq_instance = None
        cls._granite_instance = None
        cls._mock_instance = None


def get_llm_client(purpose: str = "general") -> BaseLLMClient:
    """
    Dependency injection function for FastAPI with purpose-based routing.
    
    Args:
        purpose: The intended use case - "chat", "budget_summary", "spending_insights", or "general"
    
    Returns:
        BaseLLMClient instance appropriate for the purpose
    """
    return ModelFactory.get_client(purpose=purpose)

