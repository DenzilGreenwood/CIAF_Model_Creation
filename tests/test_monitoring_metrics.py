"""
Test suite for CIAF Monitoring Metrics
Tests Prometheus metrics collection and middleware
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge
import time

from ciaf.monitoring.metrics import (
    REGISTRY,
    http_requests_total,
    http_request_duration_seconds,
    http_request_size_bytes,
    http_response_size_bytes,
    auth_requests_total,
    auth_request_duration_seconds,
    proof_generations_total,
    proof_generation_duration_seconds,
    proof_verifications_total,
    proof_verification_duration_seconds,
    database_connections_active,
    database_queries_total,
    database_query_duration_seconds,
    cache_hits_total,
    cache_misses_total,
    errors_total,
    rate_limit_exceeded_total,
    rate_limit_remaining,
    PrometheusMiddleware,
)


class TestMetricsRegistry:
    """Test suite for metrics registry setup"""

    def test_registry_created(self):
        """Test registry is created"""
        assert REGISTRY is not None

    def test_registry_is_collector_registry(self):
        """Test registry is proper type"""
        from prometheus_client import CollectorRegistry

        assert isinstance(REGISTRY, CollectorRegistry)


class TestHTTPMetrics:
    """Test suite for HTTP request metrics"""

    def test_http_requests_total_exists(self):
        """Test HTTP requests counter exists"""
        assert http_requests_total is not None

    def test_http_requests_total_is_counter(self):
        """Test HTTP requests is a counter"""
        assert hasattr(http_requests_total, 'inc')
        assert callable(http_requests_total.inc)

    def test_http_request_duration_exists(self):
        """Test HTTP request duration metric exists"""
        assert http_request_duration_seconds is not None

    def test_http_request_duration_is_histogram(self):
        """Test HTTP request duration is a histogram"""
        assert hasattr(http_request_duration_seconds, 'observe')
        assert callable(http_request_duration_seconds.observe)

    def test_http_request_size_exists(self):
        """Test HTTP request size metric exists"""
        assert http_request_size_bytes is not None

    def test_http_response_size_exists(self):
        """Test HTTP response size metric exists"""
        assert http_response_size_bytes is not None

    def test_http_metrics_labeled(self):
        """Test HTTP metrics accept labels"""
        # Test that we can create labeled instances
        try:
            http_requests_total.labels(method='GET', endpoint='/test', status=200)
            success = True
        except:
            success = False

        assert success


class TestAuthMetrics:
    """Test suite for authentication metrics"""

    def test_auth_requests_total_exists(self):
        """Test auth requests counter exists"""
        assert auth_requests_total is not None

    def test_auth_requests_total_is_counter(self):
        """Test auth requests is a counter"""
        assert hasattr(auth_requests_total, 'inc')

    def test_auth_request_duration_exists(self):
        """Test auth request duration metric exists"""
        assert auth_request_duration_seconds is not None

    def test_auth_metrics_labeled(self):
        """Test auth metrics accept labels"""
        try:
            auth_requests_total.labels(result='success')
            success = True
        except:
            success = False

        assert success


class TestProofMetrics:
    """Test suite for proof generation and verification metrics"""

    def test_proof_generations_total_exists(self):
        """Test proof generations counter exists"""
        assert proof_generations_total is not None

    def test_proof_generation_duration_exists(self):
        """Test proof generation duration metric exists"""
        assert proof_generation_duration_seconds is not None

    def test_proof_verifications_total_exists(self):
        """Test proof verifications counter exists"""
        assert proof_verifications_total is not None

    def test_proof_verification_duration_exists(self):
        """Test proof verification duration metric exists"""
        assert proof_verification_duration_seconds is not None

    def test_proof_metrics_labeled(self):
        """Test proof metrics accept labels"""
        try:
            proof_generations_total.labels(status='success')
            proof_verifications_total.labels(result='valid')
            success = True
        except:
            success = False

        assert success


class TestDatabaseMetrics:
    """Test suite for database metrics"""

    def test_database_connections_exists(self):
        """Test database connections gauge exists"""
        assert database_connections_active is not None

    def test_database_connections_is_gauge(self):
        """Test database connections is a gauge"""
        assert hasattr(database_connections_active, 'set')
        assert callable(database_connections_active.set)

    def test_database_queries_total_exists(self):
        """Test database queries counter exists"""
        assert database_queries_total is not None

    def test_database_query_duration_exists(self):
        """Test database query duration metric exists"""
        assert database_query_duration_seconds is not None

    def test_database_metrics_labeled(self):
        """Test database metrics accept labels"""
        try:
            database_queries_total.labels(operation='select', status='success')
            database_query_duration_seconds.labels(operation='select')
            success = True
        except:
            success = False

        assert success

    def test_database_connections_gauge_operations(self):
        """Test database connections gauge operations"""
        try:
            database_connections_active.set(5)
            database_connections_active.inc()
            database_connections_active.dec()
            success = True
        except:
            success = False

        assert success


class TestCacheMetrics:
    """Test suite for cache metrics"""

    def test_cache_hits_total_exists(self):
        """Test cache hits counter exists"""
        assert cache_hits_total is not None

    def test_cache_misses_total_exists(self):
        """Test cache misses counter exists"""
        assert cache_misses_total is not None

    def test_cache_metrics_labeled(self):
        """Test cache metrics accept labels"""
        try:
            cache_hits_total.labels(cache_type='redis')
            cache_misses_total.labels(cache_type='redis')
            success = True
        except:
            success = False

        assert success

    def test_cache_hit_miss_ratio(self):
        """Test cache hit/miss ratio can be calculated"""
        try:
            cache_hits_total.labels(cache_type='test').inc()
            cache_misses_total.labels(cache_type='test').inc()
            # Both should be incrementable
            success = True
        except:
            success = False

        assert success


class TestErrorMetrics:
    """Test suite for error metrics"""

    def test_errors_total_exists(self):
        """Test errors counter exists"""
        assert errors_total is not None

    def test_errors_is_counter(self):
        """Test errors is a counter"""
        assert hasattr(errors_total, 'inc')

    def test_errors_labeled(self):
        """Test error metrics accept labels"""
        try:
            errors_total.labels(error_type='ValueError', endpoint='/test')
            success = True
        except:
            success = False

        assert success


class TestRateLimitMetrics:
    """Test suite for rate limiting metrics"""

    def test_rate_limit_exceeded_exists(self):
        """Test rate limit exceeded counter exists"""
        assert rate_limit_exceeded_total is not None

    def test_rate_limit_remaining_exists(self):
        """Test rate limit remaining gauge exists"""
        assert rate_limit_remaining is not None

    def test_rate_limit_metrics_labeled(self):
        """Test rate limit metrics accept labels"""
        try:
            rate_limit_exceeded_total.labels(limit_type='global')
            rate_limit_remaining.labels(limit_type='per_org', identifier='org_1')
            success = True
        except:
            success = False

        assert success

    def test_rate_limit_gauge_operations(self):
        """Test rate limit gauge operations"""
        try:
            rate_limit_remaining.labels(
                limit_type='per_user', identifier='user_1'
            ).set(100)
            success = True
        except:
            success = False

        assert success


class TestPrometheusMiddleware:
    """Test suite for PrometheusMiddleware"""

    def test_middleware_exists(self):
        """Test middleware class exists"""
        assert PrometheusMiddleware is not None

    def test_middleware_is_http_middleware(self):
        """Test middleware extends BaseHTTPMiddleware"""
        from starlette.middleware.base import BaseHTTPMiddleware

        assert issubclass(PrometheusMiddleware, BaseHTTPMiddleware)

    def test_middleware_has_dispatch(self):
        """Test middleware has dispatch method"""
        assert hasattr(PrometheusMiddleware, 'dispatch')
        assert callable(PrometheusMiddleware.dispatch)

    @pytest.mark.asyncio
    async def test_middleware_dispatch_callable(self):
        """Test middleware dispatch is callable"""
        middleware = PrometheusMiddleware(app=None)

        assert callable(middleware.dispatch)

    def test_middleware_instantiation(self):
        """Test middleware can be instantiated"""
        mock_app = MagicMock()
        middleware = PrometheusMiddleware(app=mock_app)

        assert middleware is not None

    def test_middleware_has_get_endpoint_method(self):
        """Test middleware has get_endpoint method"""
        middleware = PrometheusMiddleware(app=None)

        assert hasattr(middleware, 'get_endpoint')


class TestMetricsIntegration:
    """Integration tests for metrics system"""

    def test_all_metrics_registered(self):
        """Test all metrics are registered"""
        metrics = [
            http_requests_total,
            http_request_duration_seconds,
            http_request_size_bytes,
            http_response_size_bytes,
            auth_requests_total,
            auth_request_duration_seconds,
            proof_generations_total,
            proof_generation_duration_seconds,
            proof_verifications_total,
            proof_verification_duration_seconds,
            database_connections_active,
            database_queries_total,
            database_query_duration_seconds,
            cache_hits_total,
            cache_misses_total,
            errors_total,
            rate_limit_exceeded_total,
            rate_limit_remaining,
        ]

        for metric in metrics:
            assert metric is not None

    def test_metrics_counter_operations(self):
        """Test counter operations work"""
        try:
            http_requests_total.labels(
                method='GET', endpoint='/test', status=200
            ).inc()
            http_requests_total.labels(
                method='POST', endpoint='/test', status=201
            ).inc(5)
            success = True
        except:
            success = False

        assert success

    def test_metrics_histogram_operations(self):
        """Test histogram operations work"""
        try:
            http_request_duration_seconds.labels(
                method='GET', endpoint='/test', status=200
            ).observe(0.05)
            http_request_duration_seconds.labels(
                method='POST', endpoint='/test', status=201
            ).observe(0.15)
            success = True
        except:
            success = False

        assert success

    def test_metrics_gauge_operations(self):
        """Test gauge operations work"""
        try:
            database_connections_active.set(10)
            database_connections_active.inc()
            database_connections_active.dec()
            success = True
        except:
            success = False

        assert success

    def test_metrics_label_combinations(self):
        """Test various label combinations"""
        try:
            # HTTP metrics
            for method in ['GET', 'POST', 'PUT', 'DELETE']:
                for status in [200, 201, 400, 404, 500]:
                    http_requests_total.labels(
                        method=method, endpoint='/api/test', status=status
                    )

            # Auth metrics
            for result in ['success', 'failure', 'invalid_credentials']:
                auth_requests_total.labels(result=result)

            # Proof metrics
            for status in ['success', 'failure']:
                proof_generations_total.labels(status=status)

            success = True
        except:
            success = False

        assert success
