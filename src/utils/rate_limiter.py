"""
Rate Limiter Middleware
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import threading

class RateLimiter:
    """
    Token bucket rate limiter
    """
    def __init__(self, rate: int = 10, per: int = 60):
        """
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance: Dict[str, float] = defaultdict(lambda: float(rate))
        self.last_check: Dict[str, float] = defaultdict(time.time)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> Tuple[bool, float]:
        """
        Check if request is allowed
        Returns: (allowed: bool, retry_after: float)
        """
        with self.lock:
            current = time.time()
            time_passed = current - self.last_check[key]
            self.last_check[key] = current
            
            # Refill tokens
            self.allowance[key] += time_passed * (self.rate / self.per)
            
            if self.allowance[key] > self.rate:
                self.allowance[key] = float(self.rate)
            
            if self.allowance[key] < 1.0:
                # Not allowed - calculate retry after
                retry_after = (1.0 - self.allowance[key]) * (self.per / self.rate)
                return False, retry_after
            else:
                self.allowance[key] -= 1.0
                return True, 0.0

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Middleware for rate limiting
    """
    def __init__(self, app, rate: int = 10, per: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(rate=rate, per=per)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        allowed, retry_after = self.limiter.is_allowed(client_ip)
        
        if not allowed:
            return HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {retry_after:.2f} seconds",
                headers={"Retry-After": str(int(retry_after) + 1)}
            )
        
        response = await call_next(request)
        return response