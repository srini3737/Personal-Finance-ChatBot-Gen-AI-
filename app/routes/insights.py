from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.models import get_llm_client, BaseLLMClient
from app.services.insights_service import InsightsService

router = APIRouter()


class Transaction(BaseModel):
    """Transaction model."""
    category: str
    amount: float
    date: str
    merchant: str = ""
    description: str = ""


class InsightsRequest(BaseModel):
    """Request model for spending insights."""
    transactions: List[Transaction]


class CategoryInsight(BaseModel):
    """Top category insight."""
    category: str
    amount: float
    percentage: float


class InsightsResponse(BaseModel):
    """Response model for spending insights."""
    top_categories: List[CategoryInsight]
    red_flags: List[str]
    recommendations: List[str]


@router.post("/api/spending-insights", response_model=InsightsResponse)
async def get_spending_insights(
    request: InsightsRequest
):
    """
    Analyze spending patterns and provide insights using Groq (prod) or Mock (local).
    
    Example request:
    ```json
    {
      "transactions": [
        {
          "category": "Food",
          "amount": 45.50,
          "date": "2024-01-15",
          "merchant": "Grocery Store",
          "description": "Weekly groceries"
        },
        {
          "category": "Entertainment",
          "amount": 60.00,
          "date": "2024-01-16",
          "merchant": "Movie Theater",
          "description": "Movie tickets"
        }
      ]
    }
    ```
    """
    # Get insights-specific LLM client (Groq in prod, Mock in local)
    llm_client = get_llm_client(purpose="spending_insights")
    
    try:
        # Convert Pydantic models to dicts
        transactions_data = [txn.model_dump() for txn in request.transactions]
        
        service = InsightsService(llm_client)
        insights = await service.generate_insights(transactions_data)
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")
