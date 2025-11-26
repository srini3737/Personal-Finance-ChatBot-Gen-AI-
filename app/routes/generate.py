from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from app.models import get_llm_client, BaseLLMClient
from app.services.prompt_templates import get_persona_prompt, get_general_prompt

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request model for text generation."""
    prompt: str
    persona: Optional[str] = None
    stream: bool = False
    max_tokens: int = 512


class GenerateResponse(BaseModel):
    """Response model for text generation."""
    answer: str
    model: str
    meta: Dict[str, Any] = {}


@router.post("/api/generate", response_model=GenerateResponse)
async def generate_response(
    request: GenerateRequest
):
    """
    Generate persona-aware financial advice using IBM Granite (prod) or Mock (local).
    
    Supported personas:
    - student: College student with limited income
    - salaried: Professional with steady income
    - parent: Parent managing family finances
    - freelancer: Freelancer with variable income
    - retiree: Retiree on fixed income
    
    Example request:
    ```json
    {
      "prompt": "How can I save money on a tight budget?",
      "persona": "student",
      "stream": false,
      "max_tokens": 512
    }
    ```
    
    Example response:
    ```json
    {
      "answer": "As a student, focus on building good financial habits early...",
      "model": "ibm-granite",
      "meta": {
        "persona": "student",
        "confidence": 0.95
      }
    }
    ```
    """
    # Get chat-specific LLM client (Granite in prod, Mock in local)
    llm_client = get_llm_client(purpose="chat")
    
    try:
        # Generate appropriate prompt based on persona
        if request.persona:
            full_prompt = get_persona_prompt(request.prompt, request.persona)
        else:
            full_prompt = get_general_prompt(request.prompt)
        
        # Get LLM response
        response = await llm_client.generate(
            full_prompt,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        # For now, we don't support streaming in the response
        # (would need SSE or WebSocket for that)
        if request.stream:
            # Collect all chunks
            chunks = []
            async for chunk in response:
                chunks.append(chunk)
            response = "".join(chunks)
        
        # Try to parse JSON response
        try:
            parsed = _parse_json_response(response)
            answer = parsed.get("answer", response)
            meta = {
                "persona": request.persona or "general",
                "confidence": parsed.get("confidence", 0.8)
            }
            if "persona_context" in parsed:
                meta["persona_context"] = parsed["persona_context"]
        except:
            # If not JSON, use raw response
            answer = response
            meta = {"persona": request.persona or "general"}
        
        return {
            "answer": answer,
            "model": llm_client.model_name,
            "meta": meta
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


def _parse_json_response(response: str) -> Dict[str, Any]:
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
