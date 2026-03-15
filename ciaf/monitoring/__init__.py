"""
CIAF Monitoring and Observability Module
Includes metrics, logging, and tracing infrastructure
"""

from ciaf.monitoring.metrics import (
    PrometheusMiddleware,
    REGISTRY,
    record_auth_attempt,
    record_proof_generation,
    record_proof_verification,
    record_cache_access,
    record_rate_limit_exceeded,
)

from ciaf.logging.config import (
    setup_logging,
    get_logger,
    ContextFilter,
)

__all__ = [
    'PrometheusMiddleware',
    'REGISTRY',
    'record_auth_attempt',
    'record_proof_generation',
    'record_proof_verification',
    'record_cache_access',
    'record_rate_limit_exceeded',
    'setup_logging',
    'get_logger',
    'ContextFilter',
]

__version__ = '1.0.0'
