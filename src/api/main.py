from typing import Dict
import time 
from fastapi import FastAPI
import platform 
import psutil

from src.api.routes.parse import router
app = FastAPI(title= 'Smart Expense NLP API', version='1.0.0', description='API for parsing expense text using INDOBERT and regex combination.')


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