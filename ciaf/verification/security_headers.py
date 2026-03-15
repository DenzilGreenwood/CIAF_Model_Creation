"""
Security Headers Middleware for FastAPI
Implements OWASP recommended security headers for API protection
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all HTTP responses
    Reference: https://owasp.org/www-community/attacks/
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent X-Frame-Options clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filtering in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy - Strict by default
        # Adjust for your specific use cases
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # Strict Transport Security - HTTPS only
        # Note: Set max-age to appropriate value for your deployment
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Referrer Policy - Don't leak referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Feature Policy / Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "payment=(), "
            "usb=(), "
            "vr=(), "
            "xr-spatial-tracking=()"
        )

        # Prevent cache of sensitive data
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds CORS headers with security considerations
    Should be configured appropriately for your deployment
    """

    def __init__(self, app, allowed_origins: list = None, allowed_methods: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3002", "http://localhost:8001"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]

    async def dispatch(self, request: Request, call_next) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            origin = request.headers.get("origin")
            if origin in self.allowed_origins:
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                        "Access-Control-Max-Age": "3600",
                        "Access-Control-Allow-Credentials": "true",
                    },
                )

        response = await call_next(request)

        # Add CORS headers to response
        origin = request.headers.get("origin")
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response
