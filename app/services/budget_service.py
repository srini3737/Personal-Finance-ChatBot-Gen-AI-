import json
import logging
from typing import Dict, Any
from app.models.base_model import BaseLLMClient
from app.services.prompt_templates import get_budget_summary_prompt

logger = logging.getLogger(__name__)


class BudgetService:
    """Service for budget analysis and summary generation."""
    
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
    
    async def generate_summary(
        self,
        income_data: Dict[str, float],
        expense_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate budget summary with LLM analysis.
        
        Args:
            income_data: Dictionary of income sources and amounts
            expense_data: Dictionary of expense categories and amounts
        
        Returns:
            Dictionary with budget summary including totals, savings rate, and suggestions
        """
        # Calculate basic totals
        total_income = sum(income_data.values())
        total_expenses = sum(expense_data.values())
        
        # Generate prompt
        prompt = get_budget_summary_prompt(income_data, expense_data)
        
        try:
            # Get LLM response
            response = await self.llm_client.generate(prompt, max_tokens=800, stream=False)
            
            # Parse JSON response
            summary = self._parse_json_response(response)
            
            # Validate and ensure required fields
            summary = self._validate_summary(summary, total_income, total_expenses)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating budget summary: {e}")
            # Return fallback summary
            return self._generate_fallback_summary(income_data, expense_data)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling potential extra text."""
        # Try to find JSON in the response
        response = response.strip()
        
        # If response starts with ```json, extract the JSON
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
    
    def _validate_summary(
        self,
        summary: Dict[str, Any],
        total_income: float,
        total_expenses: float
    ) -> Dict[str, Any]:
        """Validate and ensure all required fields are present."""
        # Ensure required fields exist
        if "total_income" not in summary:
            summary["total_income"] = total_income
        if "total_expenses" not in summary:
            summary["total_expenses"] = total_expenses
        if "savings_rate" not in summary:
            savings = total_income - total_expenses
            summary["savings_rate"] = (savings / total_income * 100) if total_income > 0 else 0
        if "category_percentages" not in summary:
            summary["category_percentages"] = {}
        if "suggestion_list" not in summary:
            summary["suggestion_list"] = []
        
        return summary
    
    def _generate_fallback_summary(
        self,
        income_data: Dict[str, float],
        expense_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate basic summary without LLM."""
        total_income = sum(income_data.values())
        total_expenses = sum(expense_data.values())
        savings = total_income - total_expenses
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        
        # Calculate category percentages
        category_percentages = {}
        if total_expenses > 0:
            for category, amount in expense_data.items():
                category_percentages[category] = (amount / total_expenses * 100)
        
        # Generate basic suggestions
        suggestions = []
        if savings_rate >= 20:
            suggestions.append(f"Excellent! Your savings rate of {savings_rate:.1f}% is above the recommended 20%.")
        elif savings_rate >= 10:
            suggestions.append(f"Good job! Your savings rate of {savings_rate:.1f}% is healthy. Try to reach 20% if possible.")
        else:
            suggestions.append(f"Your savings rate of {savings_rate:.1f}% could be improved. Aim for at least 10-20%.")
        
        # Find highest expense category
        if expense_data:
            highest_category = max(expense_data.items(), key=lambda x: x[1])
            suggestions.append(f"{highest_category[0]} is your largest expense at ${highest_category[1]:.2f}. Review if this can be optimized.")
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings_rate": savings_rate,
            "category_percentages": category_percentages,
            "suggestion_list": suggestions
        }
