"""
Fallback & Retry Logic
"""
import time
from typing import Callable, Any, Optional
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential: bool = True
):
    """
    Decorator for retry with exponential backoff
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential: Use exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            delay = base_delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    
                    print(f"[RETRY] Attempt {retries}/{max_retries} failed: {e}")
                    print(f"[RETRY] Waiting {delay:.2f}s before retry...")
                    
                    time.sleep(delay)
                    
                    if exponential:
                        delay = min(delay * 2, max_delay)
                    
            raise Exception(f"Max retries ({max_retries}) exceeded")
        
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit Breaker pattern implementation
    """
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                print("[CIRCUIT] Half-open, attempting request...")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.reset()
            return result
        except Exception as e:
            self.record_failure()
            raise e
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"[CIRCUIT] OPEN after {self.failure_count} failures")
    
    def reset(self):
        self.failure_count = 0
        self.state = "CLOSED"
        print("[CIRCUIT] CLOSED - reset")