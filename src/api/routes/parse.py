from fastapi import APIRouter

router = APIRouter()

@router.post("/parse")
async def parse_expense(payload: dict):
    """
    Dummy endpoint buat parsing teks struk.
    Nanti bisa diganti pake model NLP / regex pipeline.
    """
    text = payload.get("text", "")
    return {
        "text": text,
        "parsed": {"item": "N/A", "price": 0},
        "status": "under development"
    }