from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from app.models import get_llm_client, BaseLLMClient
from app.services.budget_service import BudgetService

router = APIRouter()


class BudgetRequest(BaseModel):
    """Request model for budget summary."""
    income: Dict[str, float]
    expenses: Dict[str, float]


class BudgetResponse(BaseModel):
    """Response model for budget summary."""
    total_income: float
    total_expenses: float
    savings_rate: float
    category_percentages: Dict[str, float]
    suggestion_list: list[str]


@router.post("/api/budget-summary", response_model=BudgetResponse)
async def create_budget_summary(
    request: BudgetRequest
):
    """
    Generate budget summary with analysis and suggestions using Groq (prod) or Mock (local).
    
    Example request:
    ```json
    {
      "income": {
        "Salary": 5000,
        "Freelance": 500
      },
      "expenses": {
        "Rent": 1200,
        "Groceries": 400,
        "Transportation": 200,
        "Entertainment": 150,
        "Utilities": 100
      }
    }
    ```
    """
    # Get budget-specific LLM client (Groq in prod, Mock in local)
    llm_client = get_llm_client(purpose="budget_summary")
    
    try:
        service = BudgetService(llm_client)
        summary = await service.generate_summary(request.income, request.expenses)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating budget summary: {str(e)}")
