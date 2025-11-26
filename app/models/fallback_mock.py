import json
from typing import Union, AsyncIterator
from app.models.base_model import BaseLLMClient


class FallbackMockClient(BaseLLMClient):
    """Deterministic mock LLM client for local development."""
    
    def __init__(self):
        self._model_name = "mock-local"
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """Generate deterministic mock responses based on prompt keywords."""
        
        response = self._get_mock_response(prompt)
        
        if stream:
            return self._stream_response(response)
        return response
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate mock response based on prompt content."""
        prompt_lower = prompt.lower()
        
        # Budget summary response
        if "budget" in prompt_lower or "income" in prompt_lower or "expenses" in prompt_lower:
            return json.dumps({
                "total_income": 5000.0,
                "total_expenses": 3500.0,
                "savings_rate": 30.0,
                "category_percentages": {
                    "Housing": 35.0,
                    "Food": 20.0,
                    "Transportation": 15.0,
                    "Entertainment": 10.0,
                    "Utilities": 10.0,
                    "Other": 10.0
                },
                "suggestion_list": [
                    "Your savings rate of 30% is excellent! Keep it up.",
                    "Consider reducing entertainment expenses to increase savings.",
                    "Housing takes up 35% of expenses - this is within recommended limits."
                ]
            }, indent=2)
        
        # Spending insights response
        elif "spending" in prompt_lower or "insights" in prompt_lower or "red flag" in prompt_lower:
            return json.dumps({
                "top_categories": [
                    {"category": "Housing", "amount": 1225.0, "percentage": 35.0},
                    {"category": "Food", "amount": 700.0, "percentage": 20.0},
                    {"category": "Transportation", "amount": 525.0, "percentage": 15.0}
                ],
                "red_flags": [
                    "Entertainment spending increased 40% compared to last month",
                    "Multiple late-night food delivery charges detected"
                ],
                "recommendations": [
                    "Set a monthly budget cap for entertainment at $300",
                    "Meal prep on weekends to reduce food delivery costs",
                    "Consider carpooling or public transit to reduce transportation costs"
                ]
            }, indent=2)
        
        # NLU response
        elif "sentiment" in prompt_lower or "entities" in prompt_lower or "nlu" in prompt_lower:
            return json.dumps({
                "sentiment": "neutral",
                "entities": [
                    {"type": "MONEY", "value": "500", "text": "$500"},
                    {"type": "CATEGORY", "value": "groceries", "text": "groceries"}
                ],
                "keywords": ["spent", "groceries", "money"]
            }, indent=2)
        
        # Persona-aware financial advice
        elif "student" in prompt_lower:
            return json.dumps({
                "answer": "As a student, focus on building good financial habits early. Consider these tips: 1) Use student discounts whenever possible, 2) Cook meals instead of eating out, 3) Buy used textbooks or use library resources, 4) Start a small emergency fund even if it's just $20/month, 5) Avoid credit card debt - only spend what you have.",
                "persona_context": "student",
                "confidence": 0.95
            }, indent=2)
        
        elif "parent" in prompt_lower:
            return json.dumps({
                "answer": "As a parent, balancing family expenses with savings is crucial. Key strategies: 1) Set up a 529 college savings plan for your children, 2) Build a 6-month emergency fund for family security, 3) Take advantage of tax credits like Child Tax Credit, 4) Buy in bulk for household essentials, 5) Consider term life insurance to protect your family's future.",
                "persona_context": "parent",
                "confidence": 0.95
            }, indent=2)
        
        elif "salaried" in prompt_lower:
            return json.dumps({
                "answer": "With a steady salary, you can build strong financial foundations. Recommendations: 1) Maximize your 401(k) employer match - it's free money, 2) Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings, 3) Build an emergency fund covering 3-6 months of expenses, 4) Consider investing in index funds for long-term growth, 5) Review and negotiate your salary annually.",
                "persona_context": "salaried",
                "confidence": 0.95
            }, indent=2)
        
        # Default general advice
        else:
            return json.dumps({
                "answer": "Here are some general personal finance tips: 1) Track all your expenses to understand spending patterns, 2) Create and stick to a monthly budget, 3) Build an emergency fund with 3-6 months of expenses, 4) Pay off high-interest debt first, 5) Start investing early to benefit from compound interest, 6) Review your financial goals quarterly and adjust as needed.",
                "confidence": 0.85
            }, indent=2)
    
    async def _stream_response(self, response: str) -> AsyncIterator[str]:
        """Simulate streaming by yielding chunks of the response."""
        chunk_size = 20
        for i in range(0, len(response), chunk_size):
            yield response[i:i + chunk_size]
    
    @property
    def model_name(self) -> str:
        return self._model_name
