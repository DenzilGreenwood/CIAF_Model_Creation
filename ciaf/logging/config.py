"""
Structured JSON logging configuration
Enables JSON-structured logs for Loki and ELK stack
"""
import logging
import json
import sys
from datetime import datetime, timezone
from pythonjsonlogger.json import JsonFormatter
import uuid
import os


class ContextFilter(logging.Filter):
    """Add context information to log records"""

    def __init__(self):
        super().__init__()
        self.trace_id = None
        self.span_id = None
        self.request_id = None

    def filter(self, record):
        """Add context to record"""
        # Generate IDs if not present
        if not self.trace_id:
            self.trace_id = str(uuid.uuid4())
        if not self.span_id:
            self.span_id = str(uuid.uuid4())[:12]
        if not self.request_id:
            self.request_id = os.environ.get('REQUEST_ID', str(uuid.uuid4())[:8])

        # Add context to record
        record.trace_id = self.trace_id
        record.span_id = self.span_id
        record.request_id = self.request_id
        record.timestamp = datetime.now(timezone.utc).isoformat()
        record.hostname = os.environ.get('HOSTNAME', 'unknown')
        record.service = os.environ.get('SERVICE_NAME', 'ciaf')

        return True


def setup_logging(
    level: str = 'INFO',
    log_file: str = None,
    service_name: str = 'ciaf'
):
    """
    Setup structured JSON logging

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file to write logs to
        service_name: Service name for logging
    """
    # Set environment for context filter
    os.environ['SERVICE_NAME'] = service_name

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # JSON formatter
    formatter = JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s %(trace_id)s %(span_id)s %(request_id)s',
        timestamp=True
    )

    # Add context filter
    context_filter = ContextFilter()

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)

    # Module-specific loggers
    setup_module_loggers(level, context_filter, formatter)

    return root_logger


def setup_module_loggers(level: str, context_filter: ContextFilter, formatter):
    """Setup logging for specific modules"""
    modules = [
        'ciaf.auth',
        'ciaf.verification',
        'ciaf.lcm',
        'ciaf.compliance',
        'ciaf.vault',
    ]

    for module in modules:
        logger = logging.getLogger(module)
        logger.setLevel(getattr(logging, level))
        logger.addFilter(context_filter)


def get_logger(name: str):
    """Get logger with given name"""
    logger = logging.getLogger(name)
    logger.addFilter(ContextFilter())
    return logger


# ========== USAGE EXAMPLE ==========

"""
# In your FastAPI app:

from ciaf.logging.config import setup_logging, get_logger

# Setup logging at startup
setup_logging(level='INFO', service_name='verification-service')

# Get logger in modules
logger = get_logger(__name__)

# Use logger
logger.info("Processing verification", extra={
    "user_id": "user123",
    "proof_id": "proof_xyz",
    "status": "verified"
})

logger.warning("High latency detected", extra={
    "duration_ms": 1500,
    "threshold_ms": 1000
})

logger.error("Verification failed", extra={
    "error_type": "SignatureVerificationError",
    "content_hash": "abc123"
}, exc_info=True)  # Includes exception traceback

# Output (JSON):
{
  "timestamp": "2026-03-15T10:30:45.123456Z",
  "level": "INFO",
  "name": "ciaf.verification",
  "message": "Processing verification",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "550e8400e29b",
  "request_id": "550e8400",
  "hostname": "ciaf-verification",
  "service": "verification-service",
  "user_id": "user123",
  "proof_id": "proof_xyz",
  "status": "verified"
}
"""
