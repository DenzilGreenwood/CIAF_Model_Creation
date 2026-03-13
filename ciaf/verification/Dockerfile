# CIAF Verification Microservice Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ciaf/verification /app/verification-service
COPY ciaf/__init__.py /app/ciaf/
COPY ciaf/agents /app/ciaf/agents
COPY ciaf/tagging /app/ciaf/tagging
COPY ciaf/sessions /app/ciaf/sessions
COPY ciaf/org_batching /app/ciaf/org_batching

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", \
     "verification_service.api:create_verification_app", \
     "--host", "0.0.0.0", \
     "--port", "8001", \
     "--log-level", "info"]
