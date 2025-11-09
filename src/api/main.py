from typing import Dict, Any
import time
from fastapi import FastAPI
import platform
import psutil
from contextlib import asynccontextmanager

from src.api.routes.parse import router

def load_model() -> Dict[str, Any]:
    """
    Placeholder function to simulate loading the NLP model.
    In a real scenario, this would load the IndoBERT model from a file.
    """
    print("--> Loading NLP model...")
    # Simulate a delay for model loading
    time.sleep(2)
    model = {"name": "IndoBERT-Parser", "version": "0.1.0"}
    print("--> Model loaded successfully.")
    return model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model during startup
    app.state.model = load_model()
    yield
    # Clean up the ML model and release the resources
    app.state.model = None

app = FastAPI(
    title='Smart Expense NLP API',
    version='1.0.0',
    description='API for parsing expense text using a hybrid IndoBERT and regex approach.',
    lifespan=lifespan
)

start_time = time.time()

app.include_router(router)

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Welcome to the Smart Expense NLP API"}

@app.get("/health")
def health_check() -> Dict[str,str]:
    """
    Endpoitn health check melacak uptime, status, dan resource usage

    Returns:
        Dict[str,str]: _description_
    """
    uptime_seconds = round(time.time() - start_time,2)
    return {
        "status": "ok",
        "message": "API NLP Parser is running",
        "version": app.version,
        "uptime_seconds" : uptime_seconds,
        "system": platform.system(),
        "python.version"  : platform.python_version(),
        "cpu_usage_percent" : psutil.cpu_percent(interval=0.1),
        "memory_usge" : psutil.virtual_memory().percent
    }
