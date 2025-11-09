from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any

# Pydantic models for request and response schemas
# This provides automatic data validation and API documentation
class ParseRequest(BaseModel):
    text: str
    user_id: str | None = None

class ParsedResult(BaseModel):
    item: str
    price: float

class ParseResponse(BaseModel):
    text: str
    parsed: ParsedResult
    model_info: Dict[str, Any]

router = APIRouter()

# Dependency to get the model from the app state
def get_model(request: Request) -> Dict[str, Any]:
    return request.app.state.model

@router.post("/parse", response_model=ParseResponse)
async def parse_expense(
    payload: ParseRequest,
    model: Dict[str, Any] = Depends(get_model)
):
    """
    Parses raw expense text to extract structured data.

    This endpoint uses a placeholder model. In a real scenario, it would
    call the loaded NLP model to perform Named Entity Recognition (NER).
    """
    # In a real implementation, you would call your model here:
    # result = model.predict(payload.text)
    # For now, we'll use a dummy result.
    dummy_result = {
        "item": "Nasi Goreng",
        "price": 15000.0
    }

    return {
        "text": payload.text,
        "parsed": dummy_result,
        "model_info": model  # Show which model was used
    }
