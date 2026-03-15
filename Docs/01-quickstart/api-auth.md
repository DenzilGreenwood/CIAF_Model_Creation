# API Authentication Guide

Secure your CIAF API requests with JWT tokens and API keys.

## Authentication Methods

CIAF uses **two complementary authentication systems**:

| System | Purpose | Where | Expiry |
|--------|---------|-------|--------|
| **JWT Tokens** | Verification API access | Authorization header | 24 hours |
| **API Keys** | Vault access (third-party) | X-API-Key header | No expiry (rotate annually) |

## JWT Token Flow (Verification API)

### 1. Obtain a Token

**At application startup**, exchange credentials for a JWT:

```bash
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-app-service-account",
    "password": "your-secure-password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "refresh_eyJ..."
}
```

### 2. Use the Token

Include the token in all subsequent requests:

```bash
curl -X POST http://localhost:8000/v1/tags/create \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 3. Refresh Before Expiry

10 minutes before token expires, get a new one:

```bash
curl -X POST http://localhost:8000/v1/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## API Key Flow (Vault Access)

### 1. Request an API Key

Contact your CIAF administrator:

```
Request: "I need API key for vault access for healthcare-org-1"
Response: X-API-Key: vault_key_abc123...xyz
```

API keys are:
- ✅ Long-lived (no auto-expiry)
- ✅ Organization-scoped
- ⚠️ **Should be rotated annually**
- ⚠️ **Must be stored securely** (environment variables, not code)

### 2. Use the API Key

Include in all Vault requests:

```bash
curl -X POST http://localhost:9000/v1/proofs/submit \
  -H "X-API-Key: vault_key_abc123...xyz" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Code Examples

### Python with Requests

```python
import requests
import os
from datetime import datetime, timedelta

class CIAFClient:
    def __init__(self, base_url="http://localhost:8000",
                 username="service-account",
                 password="password"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.token_expires_at = None

    def _ensure_token(self):
        """Get a fresh token if needed."""
        if self.token is None or datetime.now() >= self.token_expires_at:
            self._refresh_token()

    def _refresh_token(self):
        """Exchange credentials for JWT."""
        resp = requests.post(
            f"{self.base_url}/v1/auth/token",
            json={"username": self.username, "password": self.password}
        )
        data = resp.json()
        self.token = data["access_token"]
        self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 600)
        print(f"✅ Token refreshed, valid until {self.token_expires_at}")

    def create_tag(self, output_content, inference_type, model_name, organization_id):
        """Create a cryptographic proof tag."""
        self._ensure_token()

        resp = requests.post(
            f"{self.base_url}/v1/tags/create",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "output_content": output_content,
                "inference_type": inference_type,
                "model_name": model_name,
                "organization_id": organization_id,
                "tags": ["Production"]
            }
        )
        return resp.json()

# Usage
client = CIAFClient()
tag = client.create_tag(
    output_content='{"diagnosis": "diabetes"}',
    inference_type="direct_model",
    model_name="medical-classifier-v3",
    organization_id="healthcare-org-1"
)
print(f"Created tag: {tag['tag_id']}")
```

### TypeScript with Fetch

```typescript
class CIAFClient {
  private baseUrl: string;
  private token: string | null = null;
  private tokenExpiresAt: Date | null = null;

  constructor(
    baseUrl = "http://localhost:8000",
    private username = "service-account",
    private password = "password"
  ) {
    this.baseUrl = baseUrl;
  }

  private async ensureToken(): Promise<void> {
    if (!this.token || new Date() >= this.tokenExpiresAt!) {
      await this.refreshToken();
    }
  }

  private async refreshToken(): Promise<void> {
    const response = await fetch(`${this.baseUrl}/v1/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: this.username,
        password: this.password
      })
    });

    const data = await response.json();
    this.token = data.access_token;
    this.tokenExpiresAt = new Date(Date.now() + (data.expires_in - 600) * 1000);
    console.log(`✅ Token refreshed, valid until ${this.tokenExpiresAt}`);
  }

  async createTag(
    outputContent: string,
    inferenceType: string,
    modelName: string,
    organizationId: string
  ) {
    await this.ensureToken();

    const response = await fetch(`${this.baseUrl}/v1/tags/create`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        output_content: outputContent,
        inference_type: inferenceType,
        model_name: modelName,
        organization_id: organizationId,
        tags: ["Production"]
      })
    });

    return response.json();
  }
}

// Usage
const client = new CIAFClient();
const tag = await client.createTag(
  '{"diagnosis": "diabetes"}',
  "direct_model",
  "medical-classifier-v3",
  "healthcare-org-1"
);
console.log(`Created tag: ${tag.tag_id}`);
```

## Security Best Practices

### ✅ DO

- Store API keys in environment variables: `export VAULT_API_KEY=...`
- Rotate API keys annually
- Use HTTPS in production (TLS 1.2+)
- Keep tokens in memory during request lifecycle
- Implement token refresh 10 minutes before expiry
- Log authentication failures (but not tokens)

### ❌ DON'T

- Hardcode credentials in source code
- Share API keys via email or Slack
- Store credentials in .env files committed to git
- Use tokens in URLs (query parameters)
- Reuse the same API key across different services
- Keep tokens longer than necessary in memory

## Error Handling

### Invalid Credentials

```
GET /v1/tags/create
Authorization: Bearer invalid_token
```

**Response (401):**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "AUTH_001"
}
```

**Fix:** Call `/v1/auth/refresh` or `/v1/auth/token` for new credentials.

### Token Expired

```
GET /v1/tags/verify?tag_id=tag-123
Authorization: Bearer eyJ... (24+ hours old)
```

**Response (401):**
```json
{
  "error": "Token Expired",
  "message": "Token expired at 2026-03-16T14:23:45Z",
  "code": "AUTH_002"
}
```

**Fix:** Automatically refresh with `/v1/auth/refresh` in middleware.

### API Key Invalid

```
POST /v1/proofs/submit
X-API-Key: invalid_key_123
```

**Response (401):**
```json
{
  "error": "Invalid API Key",
  "message": "API key not found or revoked",
  "code": "VAULT_AUTH_001"
}
```

**Fix:** Verify key with CIAF administrator, ensure not rotated.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Token always expires | Reduce request latency, increase token timeout |
| 401 Unauthorized | Check token in Authorization header (Bearer schema) |
| API key rejected | Verify key organization matches request org_id |
| Token refresh fails | Credentials may have been revoked, contact admin |

## Next Steps

- [5-Minute Flow](./5min-compliance-flow.md) - Put auth into action
- [Environment Setup](./environment-setup.md) - Configure your development environment
