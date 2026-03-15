# OpenAPI Documentation Guide

**Complete guide for OpenAPI/Swagger documentation in CIAF.**

---

## Overview

CIAF uses **FastAPI's built-in OpenAPI** support (via Swagger UI) for auto-generating API documentation. No manual maintenance needed—docs update automatically when code changes.

---

## Accessing Documentation

### Interactive API Explorer (Swagger UI)

```
http://localhost:8001/docs
```

Features:
- ✅ Try endpoints directly in browser
- ✅ View request/response schemas
- ✅ Test authentication
- ✅ Export Swagger JSON

### Alternative Documentation (ReDoc)

```
http://localhost:8001/redoc
```

Features:
- Better for reading-only documentation
- Search across all endpoints
- Organized by tags

### Raw OpenAPI Schema

```
http://localhost:8001/openapi.json
```

Use this to:
- Integrate with frontend code generators
- Import into Postman/Insomnia
- Feed to AI/LLMs for auto-client generation

---

## How It Works

FastAPI automatically generates OpenAPI documentation from:

1. **Pydantic Models** - Request/response schemas
2. **Function Docstrings** - Endpoint descriptions
3. **Type Hints** - Parameter types
4. **HTTP Methods** - GET, POST, etc.

Example:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="CIAF Verification Service",
    description="Verify AI-generated outputs with cryptographic proofs",
    version="1.0.0"
)

class VerificationRequest(BaseModel):
    """Request to verify an output."""
    tag_id: str = Field(..., description="Output tag ID")
    verify_merkle: bool = Field(True, description="Check merkle proof")

@app.post("/verify", response_model=VerificationResponse)
async def verify_output(request: VerificationRequest) -> VerificationResponse:
    """
    Verify an AI output against stored proofs.

    - **tag_id**: The unique identifier for this output
    - **verify_merkle**: Whether to verify the merkle proof

    Returns:
        VerificationResponse with verification results
    """
    # Implementation
    pass
```

✅ FastAPI automatically generates:
- Endpoint documentation
- Request/response schemas
- Parameter descriptions
- Error codes (4xx, 5xx)

---

## Best Practices

### 1. Write Clear Descriptions

```python
class OutputTag(BaseModel):
    """
    An AI output tagged with cryptographic proof.

    This represents a piece of AI-generated content that has been
    timestamped and digitally signed for auditability.
    """
    tag_id: str = Field(..., description="Unique output identifier (UUID)")
    content_hash: str = Field(..., description="SHA-256 hash of output content")
    timestamp: datetime = Field(..., description="ISO 8601 format")
```

### 2. Document Endpoints with Examples

```python
@app.post("/verify", tags=["Verification"])
async def verify_output(request: VerificationRequest) -> VerificationResponse:
    """
    Verify an AI-generated output against its stored proof.

    **Request Example:**
    ```json
    {
        "tag_id": "tag-abc-123",
        "verify_merkle": true,
        "include_audit_trail": true
    }
    ```

    **Response Example (Success):**
    ```json
    {
        "tag_id": "tag-abc-123",
        "verified": true,
        "timestamp": "2026-03-15T10:30:00Z",
        "agent_ids": ["agent-1", "agent-2"],
        "policies_applied": ["hipaa"]
    }
    ```

    **Error Responses:**
    - 404: Tag not found
    - 401: Unauthorized
    - 422: Invalid request
    """
    pass
```

### 3. Use Tags for Organization

```python
@app.get("/verify/{tag_id}", tags=["Verification"])
async def get_verification(tag_id: str) -> VerificationResponse:
    """Get verification for a specific tag."""
    pass

@app.post("/verify", tags=["Verification"])
async def verify_output(request: VerificationRequest) -> VerificationResponse:
    """Verify a new output."""
    pass

@app.get("/audit/{tag_id}", tags=["Audit"])
async def get_audit_trail(tag_id: str) -> AuditTrail:
    """Retrieve immutable audit trail for a tag."""
    pass
```

### 4. Document Error Cases

```python
from fastapi import HTTPException

@app.post(
    "/verify",
    response_model=VerificationResponse,
    responses={
        200: {
            "description": "Verification successful",
            "content": {
                "application/json": {
                    "example": {
                        "tag_id": "tag-123",
                        "verified": True,
                        "timestamp": "2026-03-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Tag not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag tag-123 not found"}
                }
            }
        },
        401: {
            "description": "Unauthorized - missing API key",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing authorization header"}
                }
            }
        }
    }
)
async def verify_output(request: VerificationRequest) -> VerificationResponse:
    """Verify an AI output."""
    pass
```

---

## Configuration

### FastAPI Setup (with OpenAPI customization)

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="CIAF Verification Service",
    description="Cryptographic proof verification for AI systems",
    version="1.0.0",
    terms_of_service="https://ai-ei.ai/terms",
    contact={
        "name": "CIAF Support",
        "url": "https://ai-ei.ai/support",
        "email": "support@ai-ei.ai",
    },
    license_info={
        "name": "BUSL-1.1",
        "url": "https://ai-ei.ai/license",
    },
)

def custom_openapi():
    """Customize OpenAPI schema."""
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title="CIAF Verification API",
            version="1.0.0",
            description="AI output verification with cryptographic proofs",
            routes=app.routes,
        )
        # Add custom servers
        app.openapi_schema["servers"] = [
            {
                "url": "https://api.ai-ei.ai",
                "description": "Production API",
            },
            {
                "url": "https://staging-api.ai-ei.ai",
                "description": "Staging API",
            },
            {
                "url": "http://localhost:8001",
                "description": "Local Development",
            },
        ]
    return app.openapi_schema

app.openapi = custom_openapi
```

### Security Schemes

```python
from fastapi.security import APIKeyHeader, HTTPBearer

security_schemes = {
    "api_key": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API key for CIAF service"
    },
    "bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token for authentication"
    }
}

# Apply to endpoints
@app.post(
    "/verify",
    security=[HTTPBearer()],
    tags=["Verification"]
)
async def verify_output(request: VerificationRequest) -> VerificationResponse:
    """Verify an output (requires authentication)."""
    pass
```

---

## Generating Client Libraries

### From OpenAPI Schema

FastAPI makes it easy to generate client libraries in multiple languages:

**Option 1: Use OpenAPI Generator (online)**

1. Go to: https://editor.swagger.io/
2. Paste OpenAPI URL: `http://localhost:8001/openapi.json`
3. Generate → Python / TypeScript / JavaScript / Go

**Option 2: Use OpenAPI Generator (CLI)**

```bash
# Install
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate -i http://localhost:8001/openapi.json \
  -g python \
  -o ./ciaf_client_sdk_python

# Generate TypeScript client
openapi-generator-cli generate -i http://localhost:8001/openapi.json \
  -g typescript-fetch \
  -o ./ciaf_client_sdk_ts
```

**Option 3: Pydantic + FastAPI (Python auto-client)**

```python
# Auto-generate Python client from Pydantic models
from ciaf_client import AsyncAPIClient

client = AsyncAPIClient(base_url="http://localhost:8001")
response = await client.verify_output(
    tag_id="tag-123",
    verify_merkle=True
)
```

---

## Testing Documentation

### Manual Testing via Swagger UI

1. Open http://localhost:8001/docs
2. Find `/verify` endpoint
3. Click "Try it out"
4. Enter request body:
   ```json
   {
       "tag_id": "test-tag-123",
       "verify_merkle": true,
       "include_audit_trail": true
   }
   ```
5. Click "Execute"
6. View response

### Automated Documentation Tests

```bash
# Export OpenAPI schema
curl http://localhost:8001/openapi.json > openapi.json

# Validate schema
npm install -g swagger-cli
swagger-cli validate openapi.json

# Check for required fields
npx openapi-enforcer openapi.json

# Generate Postman collection
npx openapi-to-postman -s openapi.json -o CIAF.postman_collection.json
```

---

## Deployment

### DockerCompose Configuration

```yaml
services:
  api:
    image: ciaf-verification:latest
    environment:
      OPENAPI_TITLE: "CIAF Verification API"
      OPENAPI_VERSION: "1.0.0"
      OPENAPI_DOCS_URL: "/docs"
      OPENAPI_REDOC_URL: "/redoc"
      OPENAPI_OPENAPI_JSON_URL: "/openapi.json"
    ports:
      - "8001:8001"
```

### Nginx Configuration (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name api.ai-ei.ai;

    location /docs {
        proxy_pass http://localhost:8001/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8001/openapi.json;
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
    }
}
```

---

## Monitoring Documentation Quality

### Endpoint Coverage

```bash
# Check all endpoints are documented
python -c "
from ciaf.verification.api import app

for route in app.routes:
    if hasattr(route, 'methods'):
        doc = route.endpoint.__doc__ or 'NO DOCUMENTATION'
        print(f'{route.path} ({route.methods}) - {doc[:50]}...')
"
```

### Missing Descriptions

```python
# Linter to ensure all endpoints have descriptions
import ast
import inspect

def check_documentation(app):
    """Verify all endpoints have docstrings and Field descriptions."""
    issues = []

    for route in app.routes:
        if not route.endpoint.__doc__:
            issues.append(f"Missing docstring: {route.path}")

    return issues

if check_documentation(app):
    print("⚠️  Documentation issues found")
```

---

## Reference

### Useful Links

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenAPI Spec**: https://spec.openapis.org/
- **Swagger UI**: https://swagger.io/tools/swagger-ui/
- **ReDoc**: https://redocly.com/docs/redoc/

### OpenAPI Versions

| Version | Release | Status |
|---------|---------|--------|
| 3.1.0 | Feb 2021 | ✅ Latest |
| 3.0.0 | Jul 2020 | ✅ Supported |
| 2.0 (Swagger) | Apr 2015 | ⚠️ Deprecated |

---

**Status**: ✅ Auto-Generated, Always Current

**Last Updated**: 2026-03-15
**Author**: CIAF Engineering Team + Claude AI
