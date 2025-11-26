from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.models import get_llm_client, BaseLLMClient
from app.services.nlu_service import NLUService

router = APIRouter()


class NLURequest(BaseModel):
    """Request model for NLU analysis."""
    text: str
    persona: str = "general"


class Entity(BaseModel):
    """Entity model."""
    type: str
    value: str
    text: str


class NLUResponse(BaseModel):
    """Response model for NLU analysis."""
    sentiment: str
    entities: List[Entity]
    keywords: List[str]


@router.post("/api/nlu", response_model=NLUResponse)
async def analyze_text(
    request: NLURequest,
    llm_client: BaseLLMClient = Depends(get_llm_client)
):
    """
    Analyze financial text for sentiment, entities, and keywords.
    
    Example request:
    ```json
    {
      "text": "I spent $500 on groceries last week",
      "persona": "student"
    }
    ```
    
    Example response:
    ```json
    {
      "sentiment": "neutral",
      "entities": [
        {
          "type": "MONEY",
          "value": "500",
          "text": "$500"
        },
        {
          "type": "CATEGORY",
          "value": "groceries",
          "text": "groceries"
        }
      ],
      "keywords": ["spent", "groceries", "week"]
    }
    ```
    """
    try:
        service = NLUService(llm_client)
        result = await service.analyze_text(request.text, request.persona)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in NLU analysis: {str(e)}")
