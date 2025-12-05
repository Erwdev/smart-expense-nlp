from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import os
import warnings
import torch
from dotenv import load_dotenv  # ✅ Import dotenv
from src.utils.model_loader import ModelLoader

# ✅ CRITICAL: Load .env FIRST before reading env vars
load_dotenv()

# ✅ FIX 1: Suppress truncation warnings
warnings.filterwarnings("ignore", message=".*truncate.*")
warnings.filterwarnings("ignore", message=".*max_length.*")

router = APIRouter()

# ✅ NOW this will work because .env is loaded
GDRIVE_FILE_ID = os.getenv("GDRIVE_MODEL_ID")
print(f"[PARSE.PY] GDRIVE_MODEL_ID loaded: {GDRIVE_FILE_ID}")  # ✅ Debug print

# ============================================
# Model Path Configuration
# ============================================
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..",
    "models",
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

    print(f"[STARTUP] Target model path: {MODEL_PATH}")

    try:
        # ✅ STEP 1: Download model from Google Drive if not exists
        if GDRIVE_FILE_ID:
            print(f"[STARTUP] Google Drive File ID detected: {GDRIVE_FILE_ID}")

            loader = ModelLoader(
                gdrive_file_id=GDRIVE_FILE_ID,
                model_dir=MODEL_PATH
            )

            # ============================
            #  🔥 FIX: CEK DULU SUDAH ADA MODEL?
            # ============================
            if loader.model_exists():
                print("[STARTUP] ✓ Model already exists. Skipping download.")
            else:
                print("[STARTUP] Model not found, downloading...")
                if not loader.load():
                    # kalau load gagal dan folder juga tidak ada -> error
                    if not loader.model_exists():
                        raise RuntimeError("Failed to load model from Google Drive")
                    else:
                        print("[STARTUP] ⚠ Download failed but model exists, continuing...")

        # ✅ STEP 2: Load tokenizer
        print("[STARTUP] Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            use_fast=True,
            model_max_length=512,
        )

        # ✅ STEP 3: Load model
        print("[STARTUP] Loading model...")
        model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

        # ✅ STEP 4: GPU detection
        device = -1
        if torch.cuda.is_available():
            device = 0
            print(f"[STARTUP] ✓ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"[STARTUP] ✓ CUDA version: {torch.version.cuda}")
        else:
            print("[STARTUP] ⚠ CUDA not available, using CPU")

        # ✅ STEP 5: Create pipeline
        ner_pipeline = pipeline(
            "token-classification",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=device,
        )

        print(f"[STARTUP] ✓ Model loaded successfully")
        print(f"[STARTUP] ✓ Device: {'GPU (cuda:0)' if device == 0 else 'CPU'}")
        print(f"[STARTUP] ✓ Max length: {tokenizer.model_max_length}")

        return ner_pipeline

    except Exception as e:
        print(f"[STARTUP] ✗ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        ner_pipeline = None
        return None
    
    
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

def preprocess_text(text: str) -> str:
    """Preprocess input text (same as training)"""
    normalized = text.strip()
    return normalized

# ============================================
# Endpoints
# ============================================
@router.post("/parse", response_model=ParseResponse)
async def parse_text(request: ParseRequest):
    """Parse single expense text and extract entities"""
    if ner_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Check model path: {MODEL_PATH}"
        )
    
    try:
        if not request.text or not request.text.strip():
            return ParseResponse(
                text=request.text,
                entities=[],
                entity_count=0
            )
        
        normalized_text = preprocess_text(request.text)
        
        print(f"[INFERENCE] Processing: {normalized_text}")
        entities = ner_pipeline(normalized_text)
        print(f"[INFERENCE] Found {len(entities)} entities: {entities}")
        
        MIN_CONFIDENCE = 0.5
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
    """Parse multiple texts efficiently with batch processing"""
    if ner_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Check model path: {MODEL_PATH}"
        )
    
    try:
        print(f"[BATCH INFERENCE] Processing {len(request.texts)} texts")
        
        normalized_texts = [
            preprocess_text(text) 
            for text in request.texts 
            if text.strip()
        ]
        
        if not normalized_texts:
            return BatchParseResponse(results=[], total_processed=0)
        
        batch_entities = ner_pipeline(normalized_texts)
        
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
        "gdrive_id_set": GDRIVE_FILE_ID is not None,  # ✅ Add debug info
    }
    
    if ner_pipeline is not None and tokenizer is not None:
        model_info.update({
            "device": str(ner_pipeline.device),
            "tokenizer_max_length": tokenizer.model_max_length,
            "aggregation_strategy": "simple",
            "confidence_threshold": 0.5,
        })
    
    return model_info