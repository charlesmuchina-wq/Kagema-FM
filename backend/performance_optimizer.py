"""
Backend Performance Optimization Utilities
Preemptive measures for improved server performance
"""

import asyncio
import time
import logging
from functools import wraps
from typing import Dict, Any, List
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    
    def __init__(self):
        self.request_cache = {}
        self.cache_ttl = {}
        self.rate_limits = defaultdict(list)
        self.performance_metrics = defaultdict(list)
    
    def cache_response(self, ttl_seconds: int = 300):
        """Cache API responses to reduce database calls"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Check if we have a cached response
                if cache_key in self.request_cache:
                    cached_time = self.cache_ttl.get(cache_key, 0)
                    if time.time() - cached_time < ttl_seconds:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return self.request_cache[cache_key]
                
                # Execute function and cache result
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Store in cache
                self.request_cache[cache_key] = result
                self.cache_ttl[cache_key] = time.time()
                
                logger.debug(f"{func.__name__} executed in {execution_time:.2f}ms (cached)")
                return result
                
            return wrapper
        return decorator
    
    def rate_limit(self, max_requests: int = 100, window_seconds: int = 60):
        """Rate limiting for API endpoints"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                client_id = getattr(args[0] if args else None, 'client', {}).get('host', 'unknown')
                current_time = time.time()
                
                # Clean old requests outside the window
                self.rate_limits[client_id] = [
                    req_time for req_time in self.rate_limits[client_id] 
                    if current_time - req_time < window_seconds
                ]
                
                # Check rate limit
                if len(self.rate_limits[client_id]) >= max_requests:
                    logger.warning(f"Rate limit exceeded for {client_id}")
                    raise Exception(f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds")
                
                # Add current request
                self.rate_limits[client_id].append(current_time)
                
                return await func(*args, **kwargs)
                
            return wrapper
        return decorator
    
    def monitor_performance(self):
        """Monitor API performance metrics"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = 0  # Could add psutil for memory monitoring
                
                try:
                    result = await func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Store performance metrics
                    self.performance_metrics[func.__name__].append({
                        'execution_time': execution_time,
                        'timestamp': time.time(),
                        'status': 'success'
                    })
                    
                    logger.info(f"✅ {func.__name__}: {execution_time:.2f}ms")
                    return result
                    
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.performance_metrics[func.__name__].append({
                        'execution_time': execution_time,
                        'timestamp': time.time(),
                        'status': 'error',
                        'error': str(e)
                    })
                    
                    logger.error(f"❌ {func.__name__}: {execution_time:.2f}ms - {e}")
                    raise
                    
            return wrapper
        return decorator
    
    async def batch_database_operations(self, operations: List[Dict[str, Any]], batch_size: int = 10):
        """Batch database operations to reduce connection overhead"""
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                self._execute_operation(op) for op in batch
            ], return_exceptions=True)
            results.extend(batch_results)
        
        return results
    
    async def _execute_operation(self, operation: Dict[str, Any]):
        """Execute a single database operation"""
        # This would be implemented based on your database driver
        pass
    
    def preload_critical_data(self, data_loaders: List[callable]):
        """Preload frequently accessed data"""
        async def preload():
            logger.info("🚀 Preloading critical data...")
            
            preload_tasks = [loader() for loader in data_loaders]
            results = await asyncio.gather(*preload_tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"✅ Preloaded {successful}/{len(data_loaders)} data sources")
            
        return preload()
    
    def cleanup_cache(self, max_age_seconds: int = 3600):
        """Clean up old cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, cached_time in self.cache_ttl.items():
            if current_time - cached_time > max_age_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.request_cache[key]
            del self.cache_ttl[key]
        
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        report = {}
        
        for endpoint, metrics in self.performance_metrics.items():
            if not metrics:
                continue
                
            execution_times = [m['execution_time'] for m in metrics if m['status'] == 'success']
            error_count = len([m for m in metrics if m['status'] == 'error'])
            
            if execution_times:
                report[endpoint] = {
                    'total_requests': len(metrics),
                    'successful_requests': len(execution_times),
                    'error_count': error_count,
                    'avg_response_time': sum(execution_times) / len(execution_times),
                    'min_response_time': min(execution_times),
                    'max_response_time': max(execution_times),
                    'error_rate': (error_count / len(metrics)) * 100
                }
        
        return report
    
    def compress_response(self, data: Any) -> bytes:
        """Compress response data for faster transmission"""
        import gzip
        
        if isinstance(data, dict) or isinstance(data, list):
            json_str = json.dumps(data, separators=(',', ':'))
        else:
            json_str = str(data)
        
        return gzip.compress(json_str.encode('utf-8'))

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Utility functions for common use cases
def cached_api_response(ttl: int = 300):
    return performance_optimizer.cache_response(ttl)

def rate_limited_api(max_requests: int = 100, window: int = 60):
    return performance_optimizer.rate_limit(max_requests, window)

def monitored_api():
    return performance_optimizer.monitor_performance()

async def cleanup_performance_cache():
    """Scheduled cleanup task"""
    performance_optimizer.cleanup_cache()
    logger.info("🔧 Performance cache cleanup completed")

# Auto-cleanup every 10 minutes
async def start_performance_monitor():
    while True:
        await asyncio.sleep(600)  # 10 minutes
        await cleanup_performance_cache()