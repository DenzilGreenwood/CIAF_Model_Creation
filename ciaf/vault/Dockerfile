FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install base requirements
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    cryptography==41.0.7 \
    pydantic==2.5.0

# Copy vault code - self-contained
COPY ciaf/vault /app/vault/

# Create vault directory
RUN mkdir -p /app/.ciaf/vault

# Expose port
EXPOSE 8002

# Run vault API
CMD ["python", "-m", "uvicorn", "vault.api:vault_api", "--host", "0.0.0.0", "--port", "8002"]

