"""
Performance Profiling Utilities
"""
import time
import psutil
import functools
from typing import Callable, Dict, Any
from contextlib import contextmanager

class PerformanceProfiler:
    """
    Profile function execution time and resource usage
    """
    def __init__(self):
        self.metrics: Dict[str, list] = {
            "execution_time": [],
            "cpu_percent": [],
            "memory_mb": []
        }
    
    @contextmanager
    def profile(self, name: str = "function"):
        """Context manager for profiling"""
        process = psutil.Process()
        
        # Start metrics
        start_time = time.time()
        start_cpu = process.cpu_percent()
        start_mem = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            # End metrics
            end_time = time.time()
            end_cpu = process.cpu_percent()
            end_mem = process.memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            cpu_usage = end_cpu - start_cpu
            memory_usage = end_mem - start_mem
            
            # Store metrics
            self.metrics["execution_time"].append(execution_time)
            self.metrics["cpu_percent"].append(cpu_usage)
            self.metrics["memory_mb"].append(memory_usage)
            
            print(f"\n[PROFILE] {name}")
            print(f"  ⏱  Execution Time: {execution_time*1000:.2f}ms")
            print(f"  💻 CPU Usage: {cpu_usage:.2f}%")
            print(f"  🧠 Memory: {memory_usage:.2f}MB")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get profiling summary statistics"""
        if not self.metrics["execution_time"]:
            return {}
        
        import statistics
        
        return {
            "execution_time_ms": {
                "mean": statistics.mean(self.metrics["execution_time"]) * 1000,
                "median": statistics.median(self.metrics["execution_time"]) * 1000,
                "min": min(self.metrics["execution_time"]) * 1000,
                "max": max(self.metrics["execution_time"]) * 1000,
                "stdev": statistics.stdev(self.metrics["execution_time"]) * 1000 if len(self.metrics["execution_time"]) > 1 else 0
            },
            "cpu_percent": {
                "mean": statistics.mean(self.metrics["cpu_percent"]),
                "max": max(self.metrics["cpu_percent"])
            },
            "memory_mb": {
                "mean": statistics.mean(self.metrics["memory_mb"]),
                "max": max(self.metrics["memory_mb"])
            },
            "total_calls": len(self.metrics["execution_time"])
        }
    
    def reset(self):
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key] = []

def profile_function(func: Callable) -> Callable:
    """Decorator to profile a function"""
    profiler = PerformanceProfiler()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with profiler.profile(func.__name__):
            result = func(*args, **kwargs)
        return result
    
    wrapper.profiler = profiler
    return wrapper