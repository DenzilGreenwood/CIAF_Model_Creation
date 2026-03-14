# CIAF Verification Microservice Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn python-dotenv pydantic sqlalchemy psycopg2-binary redis requests click cryptography numpy pandas jsonschema ecdsa python-jose passlib typing-extensions tqdm prometheus-client structlog aiohttp websockets


# Copy application code
COPY ciaf /app/ciaf
COPY ciaf/verification /app/verification_service

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", \
     "verification_service.api:create_verification_app", \
     "--host", "0.0.0.0", \
     "--port", "8001", \
     "--log-level", "info"]
