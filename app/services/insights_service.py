import json
import logging
from typing import Dict, Any, List
from app.models.base_model import BaseLLMClient
from app.services.prompt_templates import get_spending_insights_prompt

logger = logging.getLogger(__name__)


class InsightsService:
    """Service for spending insights and pattern analysis."""
    
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
    
    async def generate_insights(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate spending insights from transaction data.
        
        Args:
            transactions: List of transaction dictionaries with category, amount, date, etc.
        
        Returns:
            Dictionary with top categories, red flags, and recommendations
        """
        # Generate prompt
        prompt = get_spending_insights_prompt(transactions)
        
        try:
            # Get LLM response
            response = await self.llm_client.generate(prompt, max_tokens=1000, stream=False)
            
            # Parse JSON response
            insights = self._parse_json_response(response)
            
            # Validate required fields
            insights = self._validate_insights(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating spending insights: {e}")
            # Return fallback insights
            return self._generate_fallback_insights(transactions)
    
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
    
    def _validate_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure all required fields are present."""
        if "top_categories" not in insights:
            insights["top_categories"] = []
        if "red_flags" not in insights:
            insights["red_flags"] = []
        if "recommendations" not in insights:
            insights["recommendations"] = []
        
        return insights
    
    def _generate_fallback_insights(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic insights without LLM."""
        # Aggregate by category
        category_totals = {}
        for txn in transactions:
            category = txn.get("category", "Other")
            amount = abs(float(txn.get("amount", 0)))
            category_totals[category] = category_totals.get(category, 0) + amount
        
        # Calculate total
        total = sum(category_totals.values())
        
        # Get top categories
        top_categories = []
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (amount / total * 100) if total > 0 else 0
            top_categories.append({
                "category": category,
                "amount": amount,
                "percentage": percentage
            })
        
        # Generate basic red flags
        red_flags = []
        for cat in top_categories:
            if cat["percentage"] > 40:
                red_flags.append(f"{cat['category']} represents {cat['percentage']:.1f}% of spending - consider if this is sustainable")
        
        if len(transactions) > 10:
            # Check for frequent small transactions
            small_txns = [t for t in transactions if abs(float(t.get("amount", 0))) < 20]
            if len(small_txns) > len(transactions) * 0.3:
                red_flags.append(f"Many small transactions detected ({len(small_txns)}) - these can add up quickly")
        
        # Generate basic recommendations
        recommendations = [
            "Track all expenses for at least one month to identify patterns",
            "Set category budgets based on your spending analysis",
            "Review subscriptions and recurring charges monthly"
        ]
        
        if top_categories:
            recommendations.append(f"Focus on optimizing {top_categories[0]['category']} spending as it's your largest category")
        
        return {
            "top_categories": top_categories,
            "red_flags": red_flags if red_flags else ["No major red flags detected - keep monitoring your spending"],
            "recommendations": recommendations
        }
