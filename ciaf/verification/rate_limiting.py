"""
Rate Limiting Middleware for FastAPI
Implements per-organization and per-user rate limiting
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import asyncio


class RateLimitStore:
    """In-memory rate limit store with automatic cleanup"""

    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.cleanup_task = None

    async def start_cleanup(self, interval: int = 300):
        """Start background cleanup task (removes old entries)"""
        while True:
            await asyncio.sleep(interval)
            self._cleanup_expired()

    def _cleanup_expired(self):
        """Remove entries older than 1 hour"""
        now = datetime.now()
        expired_keys = []

        for key, timestamps in self.requests.items():
            # Keep timestamps from last hour only
            self.requests[key] = [ts for ts in timestamps if (now - ts).seconds < 3600]

            if not self.requests[key]:
                expired_keys.append(key)

        for key in expired_keys:
            del self.requests[key]

    def add_request(self, key: str) -> bool:
        """Track a request, return True if within limit"""
        now = datetime.now()
        if key not in self.requests:
            self.requests[key] = []

        # Clean up old timestamps
        self.requests[key] = [ts for ts in self.requests[key] if (now - ts).seconds < 60]

        return True  # Request added


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware that enforces per-organization and per-user limits

    Configured rates:
    - Global: 1000 requests/minute for all users
    - Per-Organization: 100 requests/minute per org
    - Per-User: 30 requests/minute per user
    """

    def __init__(
        self,
        app,
        global_limit: int = 1000,
        org_limit: int = 100,
        user_limit: int = 30,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.global_limit = global_limit
        self.org_limit = org_limit
        self.user_limit = user_limit
        self.window_seconds = window_seconds
        self.store = RateLimitStore()

    async def dispatch(self, request: Request, call_next) -> tuple:
        # Skip rate limiting for health checks and non-API requests
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Extract identifiers
        client_ip = request.client.host if request.client else "unknown"
        org_id = request.headers.get("X-Organization-ID", "default")

        # Try to get user from JWT token (if authenticated)
        user_id = "anonymous"
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # In production, extract user from JWT
            user_id = f"user_{auth_header[-8:]}"

        # Check rate limits
        now = datetime.now()

        # Global limit key
        global_key = "global"
        if global_key not in self.store.requests:
            self.store.requests[global_key] = []

        # Clean and check global limit
        self.store.requests[global_key] = [
            ts for ts in self.store.requests[global_key]
            if (now - ts).seconds < self.window_seconds
        ]

        if len(self.store.requests[global_key]) >= self.global_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Global rate limit exceeded",
                    "limit": self.global_limit,
                    "window_seconds": self.window_seconds,
                    "retry_after": self.window_seconds,
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        # Organization limit key
        org_key = f"org_{org_id}"
        if org_key not in self.store.requests:
            self.store.requests[org_key] = []

        # Clean and check org limit
        self.store.requests[org_key] = [
            ts for ts in self.store.requests[org_key]
            if (now - ts).seconds < self.window_seconds
        ]

        if len(self.store.requests[org_key]) >= self.org_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Organization rate limit exceeded for {org_id}",
                    "limit": self.org_limit,
                    "window_seconds": self.window_seconds,
                    "retry_after": self.window_seconds,
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        # User limit key
        user_key = f"user_{user_id}_{client_ip}"
        if user_key not in self.store.requests:
            self.store.requests[user_key] = []

        # Clean and check user limit
        self.store.requests[user_key] = [
            ts for ts in self.store.requests[user_key]
            if (now - ts).seconds < self.window_seconds
        ]

        if len(self.store.requests[user_key]) >= self.user_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "User rate limit exceeded",
                    "limit": self.user_limit,
                    "window_seconds": self.window_seconds,
                    "retry_after": self.window_seconds,
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        # Record this request in all limits
        self.store.requests[global_key].append(now)
        self.store.requests[org_key].append(now)
        self.store.requests[user_key].append(now)

        # Get response
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["RateLimit-Limit"] = str(self.user_limit)
        response.headers["RateLimit-Remaining"] = str(
            self.user_limit - len(self.store.requests[user_key])
        )
        response.headers["RateLimit-Reset"] = str(
            int((now + timedelta(seconds=self.window_seconds)).timestamp())
        )

        return response


class QuotaMiddleware(BaseHTTPMiddleware):
    """
    Quota management middleware - tracks monthly usage per organization
    """

    def __init__(self, app, monthly_quota: int = 100000):
        super().__init__(app)
        self.monthly_quota = monthly_quota
        self.usage: Dict[str, Dict] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        org_id = request.headers.get("X-Organization-ID", "default")
        now = datetime.now()

        # Initialize quota entry if not exists
        if org_id not in self.usage:
            self.usage[org_id] = {
                "month": now.month,
                "year": now.year,
                "requests": 0,
            }

        # Check if we're in a new month
        if (self.usage[org_id]["month"] != now.month or
            self.usage[org_id]["year"] != now.year):
            # Reset quota
            self.usage[org_id] = {
                "month": now.month,
                "year": now.year,
                "requests": 0,
            }

        # Check quota
        usage = self.usage[org_id]["requests"]
        if usage >= self.monthly_quota:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "quota_exceeded",
                    "message": f"Monthly quota of {self.monthly_quota} exceeded",
                    "used": usage,
                    "quota": self.monthly_quota,
                    "reset_date": f"{now.month}/01/{now.year + (1 if now.month == 12 else 0)}",
                },
            )

        response = await call_next(request)

        # Increment usage
        self.usage[org_id]["requests"] += 1

        # Add quota headers to response
        remaining = self.monthly_quota - self.usage[org_id]["requests"]
        response.headers["Quota-Limit"] = str(self.monthly_quota)
        response.headers["Quota-Used"] = str(self.usage[org_id]["requests"])
        response.headers["Quota-Remaining"] = str(remaining)

        return response
