from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline
import os

router = APIRouter()

# ============================================
# Model Path Configuration
# ============================================
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..",
    "models_exported",
    "indobert-expense-ner-model",
    "models_exported",
    "indobert-expense-ner-silver-final"
)
MODEL_PATH = os.path.normpath(MODEL_PATH)

# Global variable untuk pipeline (akan di-load di startup)
ner_pipeline = None

def load_ner_model():
    """
    Load NER model at startup
    Returns loaded pipeline or None if failed
    """
    global ner_pipeline
    
    print(f"[STARTUP] Looking for model at: {MODEL_PATH}")
    print(f"[STARTUP] Model exists: {os.path.exists(MODEL_PATH)}")
    
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        print("[STARTUP] Loading NER model...")
        ner_pipeline = pipeline(
            "token-classification",
            model=MODEL_PATH,
            tokenizer=MODEL_PATH,
            aggregation_strategy="simple"
        )
        print(f"[STARTUP] ✓ Model loaded successfully")
        return ner_pipeline
    except Exception as e:
        print(f"[STARTUP] ✗ Failed to load model: {e}")
        ner_pipeline = None
        return None

# Request/Response Models
class ParseRequest(BaseModel):
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "grab food 60rb"
            }
        }

class BatchParseRequest(BaseModel):
    texts: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "grab food 60rb",
                    "beli pulsa 25k",
                    "parkir 10k"
                ]
            }
        }

class Entity(BaseModel):
    entity_group: str
    score: float
    word: str
    start: int
    end: int

class ParseResponse(BaseModel):
    text: str
    entities: List[Entity]
    entity_count: int
    
class BatchParseResponse(BaseModel):
    results: List[ParseResponse]
    total_processed: int

# ============================================
# Endpoints - INFERENCE happens here
# ============================================
@router.post("/parse", response_model=ParseResponse)
async def parse_text(request: ParseRequest):
    """
    Parse single expense text and extract entities (PRICE, QTY, etc.)
    
    🔄 INFERENCE FLOW:
    1. Tokenize input text
    2. Run model forward pass
    3. Decode predictions to entities
    4. Return formatted result
    """
    if ner_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Check model path: {MODEL_PATH}"
        )
    
    try:
        # 🚀 INFERENCE HAPPENS HERE
        print(f"[INFERENCE] Processing: {request.text}")
        entities = ner_pipeline(request.text)
        print(f"[INFERENCE] Found {len(entities)} entities")
        
        # Format response
        formatted_entities = [
            Entity(
                entity_group=ent["entity_group"],
                score=round(ent["score"], 4),
                word=ent["word"],
                start=ent["start"],
                end=ent["end"]
            )
            for ent in entities
        ]
        
        return ParseResponse(
            text=request.text,
            entities=formatted_entities,
            entity_count=len(formatted_entities)
        )
    
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

@router.post("/batch-parse", response_model=BatchParseResponse)
async def batch_parse(request: BatchParseRequest):
    """
    Parse multiple expense texts in one request
    
    🔄 BATCH INFERENCE FLOW:
    1. Loop through all texts
    2. Run inference for each text
    3. Aggregate results
    """
    if ner_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Check model path: {MODEL_PATH}"
        )
    
    try:
        results = []
        print(f"[BATCH INFERENCE] Processing {len(request.texts)} texts")
        
        for idx, text in enumerate(request.texts):
            # 🚀 INFERENCE HAPPENS HERE (for each text)
            print(f"[BATCH INFERENCE] {idx+1}/{len(request.texts)}: {text}")
            entities = ner_pipeline(text)
            
            formatted_entities = [
                Entity(
                    entity_group=ent["entity_group"],
                    score=round(ent["score"], 4),
                    word=ent["word"],
                    start=ent["start"],
                    end=ent["end"]
                )
                for ent in entities
            ]
            
            results.append(ParseResponse(
                text=text,
                entities=formatted_entities,
                entity_count=len(formatted_entities)
            ))
        
        print(f"[BATCH INFERENCE] Completed {len(results)} texts")
        return BatchParseResponse(
            results=results,
            total_processed=len(results)
        )
    
    except Exception as e:
        print(f"[ERROR] Batch inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch parsing error: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Check API and model health status
    """
    return {
        "status": "healthy" if ner_pipeline is not None else "unhealthy",
        "model_loaded": ner_pipeline is not None,
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH)
    }