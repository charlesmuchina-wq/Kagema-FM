"""
Security Middleware for Dragon KARAU AI
Implements rate limiting, CORS policies, request logging, and authentication
"""
import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize MongoDB for logging
mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
db = mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]


# Rate Limiter Configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Industry standard: 100 requests per minute
    storage_uri="memory://",  # Use memory storage (can be upgraded to Redis for production)
    headers_enabled=True
)


# CORS Configuration
def get_cors_origins():
    """Get CORS origins from environment or use defaults"""
    env_origins = os.getenv('CORS_ORIGINS', '')
    
    if env_origins:
        # Parse comma-separated origins from environment
        return [origin.strip() for origin in env_origins.split(',')]
    
    # Default origins for development
    # In production, set CORS_ORIGINS in .env to specific domains
    return [
        "http://localhost:3000",
        "http://localhost:8001",
        "https://localhost:3000",
        "https://localhost:8001",
        # Add your production domains here or set in .env
        # "https://yourapp.com",
        # "https://www.yourapp.com",
        # "https://api.yourapp.com"
    ]


# Request Logging Middleware
class RequestLoggingMiddleware:
    """Middleware to log all API requests"""
    
    def __init__(self):
        self.request_count = 0
    
    async def log_request(
        self,
        request: Request,
        response_status: int,
        response_time_ms: float,
        error: Optional[str] = None
    ):
        """Log request to database"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow(),
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'client_ip': get_remote_address(request),
                'user_agent': request.headers.get('user-agent', 'Unknown'),
                'response_status': response_status,
                'response_time_ms': response_time_ms,
                'error': error,
                'request_id': f"req_{self.request_count}"
            }
            
            # Insert log entry
            await db.api_request_logs.insert_one(log_entry)
            
            self.request_count += 1
            
            # Log suspicious activity
            if response_status >= 400:
                logger.warning(f"⚠️  {request.method} {request.url.path} -> {response_status} from {log_entry['client_ip']}")
            
            # Log to console for real-time monitoring
            if response_status >= 500:
                logger.error(f"❌ SERVER ERROR: {request.method} {request.url.path} -> {response_status}")
            
        except Exception as e:
            logger.error(f"❌ Request logging error: {e}")
    
    async def get_request_stats(self, hours: int = 24) -> dict:
        """Get request statistics for last N hours"""
        try:
            from datetime import timedelta
            
            since = datetime.utcnow() - timedelta(hours=hours)
            
            pipeline = [
                {'$match': {'timestamp': {'$gte': since}}},
                {
                    '$group': {
                        '_id': {
                            'path': '$path',
                            'status': '$response_status'
                        },
                        'count': {'$sum': 1},
                        'avg_response_time': {'$avg': '$response_time_ms'}
                    }
                },
                {'$sort': {'count': -1}},
                {'$limit': 50}
            ]
            
            stats = await db.api_request_logs.aggregate(pipeline).to_list(length=50)
            
            # Get total requests
            total_requests = await db.api_request_logs.count_documents({'timestamp': {'$gte': since}})
            
            # Get error rate
            error_requests = await db.api_request_logs.count_documents({
                'timestamp': {'$gte': since},
                'response_status': {'$gte': 400}
            })
            
            return {
                'period_hours': hours,
                'total_requests': total_requests,
                'error_requests': error_requests,
                'error_rate': round((error_requests / total_requests * 100), 2) if total_requests > 0 else 0,
                'top_endpoints': stats
            }
            
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return {'error': str(e)}


# Authentication Utilities
class SimpleAuth:
    """Simple authentication for sensitive endpoints"""
    
    def __init__(self):
        # Load API keys from environment
        self.admin_api_key = os.getenv('ADMIN_API_KEY', '')
        self.crawler_api_key = os.getenv('CRAWLER_API_KEY', '')
        
        if not self.admin_api_key:
            logger.warning("⚠️  ADMIN_API_KEY not set - admin endpoints are unprotected!")
        if not self.crawler_api_key:
            logger.warning("⚠️  CRAWLER_API_KEY not set - crawler endpoints are unprotected!")
    
    async def verify_admin_key(self, request: Request) -> bool:
        """Verify admin API key from header"""
        if not self.admin_api_key:
            # If no key is set, allow access (development mode)
            return True
        
        api_key = request.headers.get('X-API-Key') or request.query_params.get('api_key')
        
        if not api_key:
            return False
        
        return api_key == self.admin_api_key
    
    async def verify_crawler_key(self, request: Request) -> bool:
        """Verify crawler API key from header"""
        if not self.crawler_api_key:
            # If no key is set, allow access (development mode)
            return True
        
        api_key = request.headers.get('X-API-Key') or request.query_params.get('api_key')
        
        if not api_key:
            return False
        
        return api_key == self.crawler_api_key
    
    async def require_admin_auth(self, request: Request):
        """Dependency for admin endpoints"""
        if not await self.verify_admin_key(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key. Provide X-API-Key header or api_key query parameter."
            )
        return True
    
    async def require_crawler_auth(self, request: Request):
        """Dependency for crawler endpoints"""
        if not await self.verify_crawler_key(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing crawler API key"
            )
        return True


# Security Headers Middleware
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# IP Blacklist/Whitelist (for production)
class IPFilter:
    """Filter requests by IP address"""
    
    def __init__(self):
        self.blacklist = set()
        self.whitelist = set()
        
        # Load from environment or database
        env_blacklist = os.getenv('IP_BLACKLIST', '')
        if env_blacklist:
            self.blacklist = set(ip.strip() for ip in env_blacklist.split(','))
        
        env_whitelist = os.getenv('IP_WHITELIST', '')
        if env_whitelist:
            self.whitelist = set(ip.strip() for ip in env_whitelist.split(','))
    
    async def check_ip(self, request: Request) -> bool:
        """Check if IP is allowed"""
        client_ip = get_remote_address(request)
        
        # If whitelist is set, only allow whitelisted IPs
        if self.whitelist and client_ip not in self.whitelist:
            logger.warning(f"🚫 Blocked non-whitelisted IP: {client_ip}")
            return False
        
        # Block blacklisted IPs
        if client_ip in self.blacklist:
            logger.warning(f"🚫 Blocked blacklisted IP: {client_ip}")
            return False
        
        return True
    
    async def add_to_blacklist(self, ip: str):
        """Add IP to blacklist"""
        self.blacklist.add(ip)
        await db.ip_blacklist.update_one(
            {'ip': ip},
            {'$set': {'ip': ip, 'added_at': datetime.utcnow()}},
            upsert=True
        )
        logger.info(f"🚫 Added {ip} to blacklist")
    
    async def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist"""
        self.blacklist.discard(ip)
        await db.ip_blacklist.delete_one({'ip': ip})
        logger.info(f"✅ Removed {ip} from blacklist")


# Initialize singletons
request_logger = RequestLoggingMiddleware()
auth = SimpleAuth()
ip_filter = IPFilter()


# Export for use in server.py
__all__ = [
    'limiter',
    'get_cors_origins',
    'request_logger',
    'auth',
    'ip_filter',
    'add_security_headers',
    '_rate_limit_exceeded_handler',
    'RateLimitExceeded'
]
