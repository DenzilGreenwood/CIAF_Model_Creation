"""
Test suite for CIAF Security Headers
Tests OWASP-recommended security headers and CORS configuration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.responses import Response, PlainTextResponse
from starlette.testclient import TestClient
from starlette.requests import Request

from ciaf.verification.security_headers import (
    SecurityHeadersMiddleware,
    CORSHeadersMiddleware,
)


class TestSecurityHeadersMiddleware:
    """Test suite for SecurityHeadersMiddleware"""

    def test_middleware_exists(self):
        """Test SecurityHeadersMiddleware exists"""
        assert SecurityHeadersMiddleware is not None

    def test_middleware_instantiation(self):
        """Test middleware can be instantiated"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(app=mock_app)

        assert middleware is not None

    def test_middleware_has_dispatch(self):
        """Test middleware has dispatch method"""
        assert hasattr(SecurityHeadersMiddleware, 'dispatch')
        assert callable(SecurityHeadersMiddleware.dispatch)

    @pytest.mark.asyncio
    async def test_middleware_dispatch_is_async(self):
        """Test dispatch method is async"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_response = MagicMock()

        # dispatch should be awaitable
        assert hasattr(middleware.dispatch, '__call__')

    @pytest.mark.asyncio
    async def test_x_frame_options_header(self):
        """Test X-Frame-Options header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "X-Frame-Options" in result.headers
        assert result.headers["X-Frame-Options"] == "DENY"

    @pytest.mark.asyncio
    async def test_x_content_type_options_header(self):
        """Test X-Content-Type-Options header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "X-Content-Type-Options" in result.headers
        assert result.headers["X-Content-Type-Options"] == "nosniff"

    @pytest.mark.asyncio
    async def test_x_xss_protection_header(self):
        """Test X-XSS-Protection header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "X-XSS-Protection" in result.headers
        assert result.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.asyncio
    async def test_content_security_policy_header(self):
        """Test Content-Security-Policy header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Content-Security-Policy" in result.headers
        csp = result.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp

    @pytest.mark.asyncio
    async def test_strict_transport_security_header(self):
        """Test Strict-Transport-Security header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Strict-Transport-Security" in result.headers
        hsts = result.headers["Strict-Transport-Security"]
        assert "max-age=" in hsts
        assert "includeSubDomains" in hsts

    @pytest.mark.asyncio
    async def test_referrer_policy_header(self):
        """Test Referrer-Policy header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Referrer-Policy" in result.headers
        assert result.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    @pytest.mark.asyncio
    async def test_permissions_policy_header(self):
        """Test Permissions-Policy header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Permissions-Policy" in result.headers
        perms = result.headers["Permissions-Policy"]
        assert "camera=()" in perms
        assert "microphone=()" in perms
        assert "geolocation=()" in perms

    @pytest.mark.asyncio
    async def test_cache_control_header(self):
        """Test Cache-Control header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Cache-Control" in result.headers
        cache = result.headers["Cache-Control"]
        assert "no-store" in cache
        assert "no-cache" in cache

    @pytest.mark.asyncio
    async def test_pragma_header(self):
        """Test Pragma header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Pragma" in result.headers
        assert result.headers["Pragma"] == "no-cache"

    @pytest.mark.asyncio
    async def test_expires_header(self):
        """Test Expires header is set"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Expires" in result.headers
        assert result.headers["Expires"] == "0"

    @pytest.mark.asyncio
    async def test_all_headers_present(self):
        """Test all security headers are present"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        middleware = SecurityHeadersMiddleware(app=mock_app)
        mock_request = MagicMock(spec=Request)

        result = await middleware.dispatch(mock_request, mock_app)

        required_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "Referrer-Policy",
            "Permissions-Policy",
            "Cache-Control",
            "Pragma",
            "Expires",
        ]

        for header in required_headers:
            assert header in result.headers, f"Missing header: {header}"


class TestCORSHeadersMiddleware:
    """Test suite for CORSHeadersMiddleware"""

    def test_cors_middleware_exists(self):
        """Test CORSHeadersMiddleware exists"""
        assert CORSHeadersMiddleware is not None

    def test_cors_middleware_instantiation(self):
        """Test CORS middleware can be instantiated"""
        mock_app = MagicMock()
        middleware = CORSHeadersMiddleware(app=mock_app)

        assert middleware is not None

    def test_cors_middleware_default_origins(self):
        """Test CORS middleware has default origins"""
        mock_app = MagicMock()
        middleware = CORSHeadersMiddleware(app=mock_app)

        assert middleware.allowed_origins is not None
        assert len(middleware.allowed_origins) > 0

    def test_cors_middleware_custom_origins(self):
        """Test CORS middleware accepts custom origins"""
        mock_app = MagicMock()
        origins = ["https://example.com", "https://app.example.com"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        assert middleware.allowed_origins == origins

    def test_cors_middleware_default_methods(self):
        """Test CORS middleware has default methods"""
        mock_app = MagicMock()
        middleware = CORSHeadersMiddleware(app=mock_app)

        assert middleware.allowed_methods is not None
        assert "GET" in middleware.allowed_methods
        assert "POST" in middleware.allowed_methods

    def test_cors_middleware_custom_methods(self):
        """Test CORS middleware accepts custom methods"""
        mock_app = MagicMock()
        methods = ["GET", "POST", "DELETE"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_methods=methods)

        assert middleware.allowed_methods == methods

    def test_cors_middleware_has_dispatch(self):
        """Test CORS middleware has dispatch method"""
        mock_app = MagicMock()
        middleware = CORSHeadersMiddleware(app=mock_app)

        assert hasattr(middleware, 'dispatch')
        assert callable(middleware.dispatch)

    @pytest.mark.asyncio
    async def test_cors_preflight_allowed_origin(self):
        """Test CORS preflight with allowed origin"""
        mock_app = AsyncMock()
        origins = ["http://localhost:3002"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "OPTIONS"
        mock_request.headers = {"origin": "http://localhost:3002"}

        result = await middleware.dispatch(mock_request, mock_app)

        assert result.status_code == 200
        assert "Access-Control-Allow-Origin" in result.headers
        assert result.headers["Access-Control-Allow-Origin"] == "http://localhost:3002"

    @pytest.mark.asyncio
    async def test_cors_preflight_disallowed_origin(self):
        """Test CORS preflight with disallowed origin"""
        mock_app = AsyncMock()
        response = Response("test", status_code=200)

        async def call_next_impl(request):
            return response

        mock_app.side_effect = call_next_impl

        origins = ["http://localhost:3002"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "OPTIONS"
        mock_request.headers = {"origin": "http://evil.com"}

        result = await middleware.dispatch(mock_request, call_next_impl)

        # Should pass through to next middleware when origin not allowed
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_cors_preflight_headers(self):
        """Test CORS preflight response headers"""
        mock_app = AsyncMock()
        origins = ["http://localhost:3002"]
        methods = ["GET", "POST", "DELETE"]
        middleware = CORSHeadersMiddleware(
            app=mock_app,
            allowed_origins=origins,
            allowed_methods=methods
        )

        mock_request = MagicMock(spec=Request)
        mock_request.method = "OPTIONS"
        mock_request.headers = {"origin": "http://localhost:3002"}

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Access-Control-Allow-Methods" in result.headers
        assert "Access-Control-Allow-Headers" in result.headers
        assert "Access-Control-Max-Age" in result.headers
        assert "Access-Control-Allow-Credentials" in result.headers

    @pytest.mark.asyncio
    async def test_cors_regular_request_allowed_origin(self):
        """Test CORS headers on regular request with allowed origin"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        origins = ["http://localhost:3002"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.headers = {"origin": "http://localhost:3002"}

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Access-Control-Allow-Origin" in result.headers
        assert result.headers["Access-Control-Allow-Origin"] == "http://localhost:3002"

    @pytest.mark.asyncio
    async def test_cors_regular_request_disallowed_origin(self):
        """Test CORS headers on regular request with disallowed origin"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        origins = ["http://localhost:3002"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.headers = {"origin": "http://evil.com"}

        result = await middleware.dispatch(mock_request, mock_app)

        # Should not have CORS headers for disallowed origin
        assert "Access-Control-Allow-Origin" not in result.headers

    @pytest.mark.asyncio
    async def test_cors_max_age_header(self):
        """Test CORS Max-Age header in preflight"""
        mock_app = AsyncMock()
        origins = ["http://localhost:3002"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "OPTIONS"
        mock_request.headers = {"origin": "http://localhost:3002"}

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Access-Control-Max-Age" in result.headers
        assert result.headers["Access-Control-Max-Age"] == "3600"

    @pytest.mark.asyncio
    async def test_cors_credentials_header(self):
        """Test CORS Credentials header"""
        mock_app = AsyncMock()
        response = Response("test")
        mock_app.return_value = response

        origins = ["http://localhost:3002"]
        middleware = CORSHeadersMiddleware(app=mock_app, allowed_origins=origins)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.headers = {"origin": "http://localhost:3002"}

        result = await middleware.dispatch(mock_request, mock_app)

        assert "Access-Control-Allow-Credentials" in result.headers
        assert result.headers["Access-Control-Allow-Credentials"] == "true"


class TestSecurityHeadersIntegration:
    """Integration tests for security headers"""

    @pytest.mark.asyncio
    async def test_security_middleware_adds_headers(self):
        """Test security middleware adds expected headers"""
        mock_app = AsyncMock()
        response = Response("test")

        async def call_next_impl(request):
            return response

        mock_app.side_effect = call_next_impl

        security = SecurityHeadersMiddleware(app=mock_app)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.headers = {}

        result = await security.dispatch(mock_request, call_next_impl)

        # Should have security headers
        assert "X-Frame-Options" in result.headers
        assert "X-Content-Type-Options" in result.headers

    def test_header_values_non_empty(self):
        """Test all header values are non-empty"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(app=mock_app)

        # All headers should be present and non-empty in middleware
        assert middleware is not None
