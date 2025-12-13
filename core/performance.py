"""
Performance monitoring utilities
"""
import time
import functools
from core.logger import get_logger

logger = get_logger(__name__)

def monitor_performance(func_name=None):
    """Decorator to monitor function performance"""
    def decorator(func):
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Performance: {name} executed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Performance: {name} failed after {execution_time:.4f}s - {e}")
                raise
        return wrapper
    return decorator

class PerformanceTracker:
    """Context manager for tracking performance"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        if exc_type is None:
            logger.info(f"Operation '{self.operation_name}' completed in {execution_time:.4f}s")
        else:
            logger.error(f"Operation '{self.operation_name}' failed after {execution_time:.4f}s")