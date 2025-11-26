import json
import logging
from typing import Dict, Any
from app.models.base_model import BaseLLMClient
from app.services.prompt_templates import get_nlu_prompt

logger = logging.getLogger(__name__)


class NLUService:
    """Service for natural language understanding of financial text."""
    
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
    
    async def analyze_text(
        self,
        text: str,
        persona: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze financial text for sentiment, entities, and keywords.
        
        Args:
            text: User input text to analyze
            persona: User persona for context
        
        Returns:
            Dictionary with sentiment, entities, and keywords
        """
        # Generate prompt
        prompt = get_nlu_prompt(text)
        
        try:
            # Get LLM response
            response = await self.llm_client.generate(prompt, max_tokens=500, stream=False)
            
            # Parse JSON response
            result = self._parse_json_response(response)
            
            # Validate required fields
            result = self._validate_nlu_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in NLU analysis: {e}")
            # Return fallback analysis
            return self._generate_fallback_nlu(text)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling potential extra text."""
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Try to parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise
    
    def _validate_nlu_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure all required fields are present."""
        if "sentiment" not in result:
            result["sentiment"] = "neutral"
        if "entities" not in result:
            result["entities"] = []
        if "keywords" not in result:
            result["keywords"] = []
        
        # Ensure sentiment is valid
        if result["sentiment"] not in ["positive", "negative", "neutral"]:
            result["sentiment"] = "neutral"
        
        return result
    
    def _generate_fallback_nlu(self, text: str) -> Dict[str, Any]:
        """Generate basic NLU analysis without LLM."""
        import re
        
        text_lower = text.lower()
        
        # Simple sentiment analysis
        positive_words = ["save", "saved", "profit", "gain", "earned", "bonus", "raise", "good", "great"]
        negative_words = ["spent", "loss", "debt", "owe", "expensive", "broke", "problem", "worry"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Extract money amounts
        entities = []
        money_pattern = r'\$?\d+(?:,\d{3})*(?:\.\d{2})?'
        money_matches = re.finditer(money_pattern, text)
        for match in money_matches:
            value = match.group().replace('$', '').replace(',', '')
            entities.append({
                "type": "MONEY",
                "value": value,
                "text": match.group()
            })
        
        # Extract potential categories
        categories = ["groceries", "rent", "food", "gas", "entertainment", "utilities", 
                     "shopping", "dining", "transport", "healthcare", "education"]
        for category in categories:
            if category in text_lower:
                entities.append({
                    "type": "CATEGORY",
                    "value": category,
                    "text": category
                })
        
        # Extract keywords (simple word tokenization)
        words = re.findall(r'\b\w+\b', text_lower)
        # Filter out common words
        stop_words = {"i", "me", "my", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        keywords = [w for w in words if w not in stop_words and len(w) > 3][:7]
        
        return {
            "sentiment": sentiment,
            "entities": entities,
            "keywords": keywords
        }
