"""
Prometheus metrics middleware for FastAPI
Collects and exposes metrics for monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from contextlib import contextmanager
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# Create registry
REGISTRY = CollectorRegistry()

# ========== METRICS DEFINITIONS ==========

# API Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=REGISTRY
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

# Authentication metrics
auth_requests_total = Counter(
    'auth_requests_total',
    'Total authentication requests',
    ['result'],  # success, failure, invalid_credentials
    registry=REGISTRY
)

auth_request_duration_seconds = Histogram(
    'auth_request_duration_seconds',
    'Authentication request duration',
    ['result'],
    registry=REGISTRY
)

# Verification metrics
proof_generations_total = Counter(
    'proof_generations_total',
    'Total proof generations',
    ['status'],  # success, failure
    registry=REGISTRY
)

proof_generation_duration_seconds = Histogram(
    'proof_generation_duration_seconds',
    'Proof generation duration in seconds',
    ['content_type'],
    registry=REGISTRY
)

proof_verifications_total = Counter(
    'proof_verifications_total',
    'Total proof verifications',
    ['result'],  # valid, invalid, expired
    registry=REGISTRY
)

proof_verification_duration_seconds = Histogram(
    'proof_verification_duration_seconds',
    'Proof verification duration in seconds',
    registry=REGISTRY
)

# Database metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections',
    registry=REGISTRY
)

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'status'],  # operation: select, insert, update, delete
    registry=REGISTRY
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    registry=REGISTRY
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type'],
    registry=REGISTRY
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type'],
    registry=REGISTRY
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint'],
    registry=REGISTRY
)

# Rate limiting metrics
rate_limit_exceeded_total = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['limit_type'],  # global, per_org, per_user
    registry=REGISTRY
)

rate_limit_remaining = Gauge(
    'rate_limit_remaining',
    'Rate limit remaining quota',
    ['limit_type', 'identifier'],
    registry=REGISTRY
)

# ========== MIDDLEWARE ==========

class PrometheusMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for Prometheus metrics"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Record metrics for each request"""
        method = request.method
        path = request.url.path
        endpoint = self.get_endpoint(path)

        # Measure request
        start_time = time.time()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            errors_total.labels(error_type=type(e).__name__, endpoint=endpoint).inc()
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint, status=status
            ).observe(duration)

        return response

    @staticmethod
    def get_endpoint(path: str) -> str:
        """Normalize path for metrics (avoid high cardinality)"""
        # Remove IDs to reduce cardinality
        import re
        normalized = re.sub(r'/[0-9a-f\-]+', '/{id}', path)
        return normalized[:100]  # Limit length


# ========== CONTEXT MANAGERS ==========

@contextmanager
def measure_operation(operation_name: str):
    """Context manager to measure operation duration"""
    start_time = time.time()
    try:
        yield
        status = 'success'
    except Exception:
        status = 'failure'
        raise
    finally:
        duration = time.time() - start_time
        database_query_duration_seconds.labels(operation=operation_name).observe(duration)
        database_queries_total.labels(operation=operation_name, status=status).inc()


# ========== METRIC RECORDING FUNCTIONS ==========

def record_auth_attempt(success: bool, duration: float = 0):
    """Record authentication attempt"""
    result = 'success' if success else 'failure'
    auth_requests_total.labels(result=result).inc()
    auth_request_duration_seconds.labels(result=result).observe(duration)


def record_proof_generation(success: bool, duration: float = 0, content_type: str = 'unknown'):
    """Record proof generation"""
    status = 'success' if success else 'failure'
    proof_generations_total.labels(status=status).inc()
    proof_generation_duration_seconds.labels(content_type=content_type).observe(duration)


def record_proof_verification(valid: bool, duration: float = 0):
    """Record proof verification"""
    result = 'valid' if valid else 'invalid'
    proof_verifications_total.labels(result=result).inc()
    proof_verification_duration_seconds.observe(duration)


def record_cache_access(hit: bool, cache_type: str = 'default'):
    """Record cache access"""
    if hit:
        cache_hits_total.labels(cache_type=cache_type).inc()
    else:
        cache_misses_total.labels(cache_type=cache_type).inc()


def record_rate_limit_exceeded(limit_type: str, identifier: str = 'unknown'):
    """Record rate limit exceeded"""
    rate_limit_exceeded_total.labels(limit_type=limit_type).inc()


# ========== USAGE EXAMPLE ==========

"""
# In your FastAPI app:
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest

app = FastAPI()

# Add middleware
app.add_middleware(PrometheusMiddleware)

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain; charset=utf-8"
    )

# In your verification endpoint:
@app.post("/verify")
async def submit_verification(request: VerificationRequest):
    start = time.time()
    try:
        # Generate proof
        proof = generate_proof(request.content)
        record_proof_generation(True, time.time() - start)
        return {"proof_id": proof.id}
    except Exception as e:
        record_proof_generation(False, time.time() - start)
        raise

# In your auth endpoint:
@app.post("/auth/login")
async def login(email: str, password: str):
    start = time.time()
    is_valid = verify_credentials(email, password)
    record_auth_attempt(is_valid, time.time() - start)
    return {"token": "xyz"}
"""
