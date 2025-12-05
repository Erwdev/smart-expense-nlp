from typing import Dict, Any
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import platform
import psutil
from contextlib import asynccontextmanager
from src.api.routes import parse
import uvicorn
from dotenv import load_dotenv
import os 


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 Load NER model during startup
    print("\n" + "="*60)
    print("STARTUP: Loading NER Model")
    print("="*60)
    parse.load_ner_model()  # Call the function from parse.py
    print("="*60 + "\n")
    
    yield
    
    # Cleanup
    print("\n" + "="*60)
    print("SHUTDOWN: Cleaning up resources")
    print("="*60)
    parse.ner_pipeline = None

start_time = time.time()

app = FastAPI(
    title='Smart Expense NLP API',
    version='1.0.0',
    description='API for parsing expense text using IndoBERT NER model.',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup_event():
#     print("[STARTUP] Initializing NLP model...")
#     parse.load_ner_model()
#     print("[STARTUP] Application ready")

# Include routes
app.include_router(parse.router, prefix="/api", tags=["NER"])

@app.get("/")
async def root():
    return {
        "message": "Smart Expense NER API",
        "status": "running",
        "model_loaded": parse.ner_pipeline is not None,
        "endpoints": {
            "parse": "/api/parse",
            "batch_parse": "/api/batch-parse",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Endpoint health check melacak uptime, status, dan resource usage
    """
    uptime_seconds = round(time.time() - start_time, 2)
    return {
        "status": "ok",
        "message": "API is running",
        "version": app.version,
        "uptime_seconds": uptime_seconds,
        "model_loaded": parse.ner_pipeline is not None,
        "system": platform.system(),
        "python_version": platform.python_version(),
        "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
        "memory_usage_percent": psutil.virtual_memory().percent
    }

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)