from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import os
import warnings

# ✅ FIX 1: Suppress truncation warnings (biar log bersih)
warnings.filterwarnings("ignore", message=".*truncate.*")
warnings.filterwarnings("ignore", message=".*max_length.*")

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

# Global variables
ner_pipeline = None
tokenizer = None
model = None

def load_ner_model():
    """Load NER model with EXACT same preprocessing as training"""
    global ner_pipeline, tokenizer, model
    
    print(f"[STARTUP] Looking for model at: {MODEL_PATH}")
    
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        print("[STARTUP] Loading tokenizer and model...")
        
        # ✅ FIX 2: Load tokenizer with explicit config
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            use_fast=True,
            model_max_length=512,  # ✅ Set max length in tokenizer
        )
        
        # Load model
        model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
        
        # ✅ FIX 3: Create pipeline with ONLY valid parameters
        ner_pipeline = pipeline(
            "token-classification",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",  # Merge B-/I- subwords
            device=0 if os.environ.get("CUDA_VISIBLE_DEVICES") else -1,  # GPU if available
        )
        
        print(f"[STARTUP] ✓ Model loaded successfully")
        print(f"[STARTUP] ✓ Device: {'GPU' if ner_pipeline.device.type == 'cuda' else 'CPU'}")
        print(f"[STARTUP] ✓ Max length: {tokenizer.model_max_length}")
        return ner_pipeline
        
    except Exception as e:
        print(f"[STARTUP] ✗ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
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
# Helper Function: Preprocess Text
# ============================================
def preprocess_text(text: str) -> str:
    """
    Preprocess input text (same as training)
    - Strip whitespace
    - Optionally normalize case (commented out by default)
    """
    # ✅ FIX 4: Match training preprocessing
    normalized = text.strip()
    # Optional: normalized = normalized.lower()  # Uncomment if training used lowercase
    return normalized

# ============================================
# Endpoints
# ============================================
@router.post("/parse", response_model=ParseResponse)
async def parse_text(request: ParseRequest):
    """
    Parse single expense text and extract entities
    
    Preprocessing pipeline:
    1. Strip whitespace
    2. Tokenize with IndoBERT tokenizer (auto truncation at 512)
    3. Model inference (token classification)
    4. Aggregate subwords (B-/I- → single entity)
    5. Filter by confidence threshold
    """
    if ner_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Check model path: {MODEL_PATH}"
        )
    
    try:
        # ✅ FIX 5: Input validation
        if not request.text or not request.text.strip():
            return ParseResponse(
                text=request.text,
                entities=[],
                entity_count=0
            )
        
        # Preprocess
        normalized_text = preprocess_text(request.text)
        
        # 🚀 INFERENCE
        # Pipeline will automatically:
        # - Tokenize with tokenizer.model_max_length=512
        # - Truncate if needed
        # - Run inference
        # - Aggregate with strategy="simple"
        print(f"[INFERENCE] Processing: {normalized_text}")
        entities = ner_pipeline(normalized_text)
        print(f"[INFERENCE] Found {len(entities)} entities: {entities}")
        
        # ✅ FIX 6: Post-processing filter (remove low confidence)
        MIN_CONFIDENCE = 0.5  # Adjust threshold as needed
        filtered_entities = [
            Entity(
                entity_group=ent["entity_group"],
                score=round(ent["score"], 4),
                word=ent["word"],
                start=ent["start"],
                end=ent["end"]
            )
            for ent in entities
            if ent["score"] >= MIN_CONFIDENCE  # ✅ Filter low confidence
        ]
        
        return ParseResponse(
            text=normalized_text,
            entities=filtered_entities,
            entity_count=len(filtered_entities)
        )
    
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@router.post("/batch-parse", response_model=BatchParseResponse)
async def batch_parse(request: BatchParseRequest):
    """
    Parse multiple texts efficiently with batch processing
    """
    if ner_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Check model path: {MODEL_PATH}"
        )
    
    try:
        # ✅ FIX 7: Batch processing optimization
        print(f"[BATCH INFERENCE] Processing {len(request.texts)} texts")
        
        # Normalize inputs
        normalized_texts = [
            preprocess_text(text) 
            for text in request.texts 
            if text.strip()
        ]
        
        if not normalized_texts:
            return BatchParseResponse(results=[], total_processed=0)
        
        # ✅ Batch inference (pipeline handles batching efficiently)
        batch_entities = ner_pipeline(normalized_texts)
        
        # Format results
        results = []
        MIN_CONFIDENCE = 0.5
        
        for idx, (text, entities) in enumerate(zip(normalized_texts, batch_entities)):
            print(f"[BATCH] {idx+1}/{len(normalized_texts)}: {text} → {len(entities)} entities")
            
            filtered_entities = [
                Entity(
                    entity_group=ent["entity_group"],
                    score=round(ent["score"], 4),
                    word=ent["word"],
                    start=ent["start"],
                    end=ent["end"]
                )
                for ent in entities
                if ent["score"] >= MIN_CONFIDENCE
            ]
            
            results.append(ParseResponse(
                text=text,
                entities=filtered_entities,
                entity_count=len(filtered_entities)
            ))
        
        print(f"[BATCH INFERENCE] ✓ Completed {len(results)} texts")
        return BatchParseResponse(
            results=results,
            total_processed=len(results)
        )
    
    except Exception as e:
        print(f"[ERROR] Batch inference failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Batch parsing error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check with detailed model info"""
    model_info = {
        "status": "healthy" if ner_pipeline is not None else "unhealthy",
        "model_loaded": ner_pipeline is not None,
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH),
    }
    
    # ✅ FIX 8: Add preprocessing config info
    if ner_pipeline is not None and tokenizer is not None:
        model_info.update({
            "device": str(ner_pipeline.device),
            "tokenizer_max_length": tokenizer.model_max_length,
            "aggregation_strategy": "simple",
            "confidence_threshold": 0.5,
        })
    
    return model_info