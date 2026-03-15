# 🔌 Artificial Intelligence Evidence Vault API - Complete Reference Guide

Complete guide to using the AI-EV API for cryptographic proof custody and verification.

## Quick Start

### 1. Start Docker
```bash
# Windows
docker-setup.bat

# Mac/Linux
./docker-setup.sh

# All platforms
docker-compose up -d
```

### 2. Run Example
```bash
python examples/api_client_example.py
```

### 3. Try API
```bash
curl http://localhost:8002/health
```

---

## API Endpoints

### Health & Status

#### Health Check
```
GET /health
```

Returns service status and version.

**Response:**
```json
{
  "status": "healthy",
  "service": "Artificial Intelligence Evidence Vault",
  "version": "1.0.0"
}
```

**cURL:**
```bash
curl http://localhost:8002/health
```

#### Statistics
```
GET /stats
```

Returns vault statistics.

**Response:**
```json
{
  "total_proofs": 42,
  "total_organizations": 3,
  "active_organizations": 2,
  "total_reads": 156
}
```

**cURL:**
```bash
curl http://localhost:8002/stats
```

---

### Proof Management

#### Submit Proof (Write)
```
POST /submit
Authorization: Bearer <api-key>
Content-Type: application/json
```

Submit a proof to the vault (immutable WORM storage).

**Request:**
```json
{
  "content": "AI model inference output",
  "agent_ids": ["agent-classifier", "agent-validator"],
  "policies_applied": ["policy-gdpr", "policy-mlops"],
  "timestamp": "2026-03-14T00:00:00Z",
  "metadata": {
    "model_name": "gpt-4",
    "domain": "billing",
    "risk_level": "low"
  }
}
```

**Response:**
```json
{
  "receipt_id": "receipt-uuid",
  "proof_id": "proof-uuid",
  "organization_id": "org-1",
  "timestamp": "2026-03-14T00:00:00Z",
  "verification_url": "http://vault/verify/proof-uuid"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8002/submit \
  -H "Authorization: Bearer test-api-key-org-1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "My proof content",
    "agent_ids": ["agent-1"],
    "policies_applied": ["policy-1"],
    "timestamp": "2026-03-14T00:00:00Z"
  }'
```

#### Verify Proof (Read)
```
GET /verify/{proof_id}
Authorization: Bearer <api-key>
```

Verify a proof and increment read counter.

**Response:**
```json
{
  "proof_id": "proof-uuid",
  "organization_id": "org-1",
  "timestamp": "2026-03-14T00:00:00Z",
  "verified": true,
  "read_count": 5
}
```

**cURL:**
```bash
curl http://localhost:8002/verify/proof-uuid \
  -H "Authorization: Bearer test-api-key-org-1"
```

**Key Features:**
- Read-only operation (no modification)
- Increments read counter for audit
- Returns verification status
- Tracks access pattern

---

### Certificate Management

#### Generate Certificate
```
POST /certificate/{proof_id}
Authorization: Bearer <api-key>
```

Generate cryptographic verification certificate for proof.

**Response:**
```json
{
  "certificate_id": "cert-uuid",
  "proof_id": "proof-uuid",
  "generated_at": "2026-03-14T00:00:00Z",
  "valid_until": "2027-03-14T00:00:00Z",
  "issuer": "Artificial Intelligence Evidence Vault"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8002/certificate/proof-uuid \
  -H "Authorization: Bearer test-api-key-org-1"
```

---

### Audit Trail

#### Get Audit Trail
```
GET /audit-trail
Authorization: Bearer <api-key>
Query Parameters:
  - action: Filter by action type (optional)
  - start_time: Start timestamp (optional)
  - end_time: End timestamp (optional)
  - limit: Result limit (default: 100)
```

Retrieve audit trail for organization.

**Response:**
```json
{
  "entries": [
    {
      "entry_id": "entry-uuid",
      "action": "submit_proof",
      "timestamp": "2026-03-14T00:00:00Z",
      "result": "success",
      "details": {}
    }
  ],
  "total": 42,
  "organization_id": "org-1"
}
```

**cURL:**
```bash
# All entries
curl http://localhost:8002/audit-trail \
  -H "Authorization: Bearer test-api-key-org-1"

# Filter by action
curl "http://localhost:8002/audit-trail?action=submit_proof&limit=10" \
  -H "Authorization: Bearer test-api-key-org-1"

# Date range
curl "http://localhost:8002/audit-trail?start_time=2026-03-01T00:00:00Z&end_time=2026-03-15T00:00:00Z" \
  -H "Authorization: Bearer test-api-key-org-1"
```

#### Get Audit Summary
```
GET /audit-summary
Authorization: Bearer <api-key>
```

Get summary statistics of audit trail.

**Response:**
```json
{
  "organization_id": "org-1",
  "summary": {
    "total_actions": 156,
    "submit_proof": 42,
    "verify_proof": 98,
    "generate_certificate": 16
  }
}
```

**cURL:**
```bash
curl http://localhost:8002/audit-summary \
  -H "Authorization: Bearer test-api-key-org-1"
```

---

### Organization

#### Get Organization Details
```
GET /organization
Authorization: Bearer <api-key>
```

Get organization information.

**Response:**
```json
{
  "org_id": "org-1",
  "name": "Banking Organization",
  "created_at": "2026-01-01T00:00:00Z",
  "api_key_count": 5,
  "last_activity": "2026-03-14T12:00:00Z"
}
```

**cURL:**
```bash
curl http://localhost:8002/organization \
  -H "Authorization: Bearer test-api-key-org-1"
```

#### Get Organization Proofs
```
GET /organization/proofs
Authorization: Bearer <api-key>
Query Parameters:
  - start_time: Filter by start (optional)
  - end_time: Filter by end (optional)
  - limit: Result limit (default: 100)
```

Get all proofs for organization.

**Response:**
```json
{
  "organization_id": "org-1",
  "proofs": [
    {
      "proof_id": "proof-uuid",
      "timestamp": "2026-03-14T00:00:00Z",
      "read_count": 5,
      "verified": true
    }
  ],
  "total": 42
}
```

**cURL:**
```bash
# All proofs
curl http://localhost:8002/organization/proofs \
  -H "Authorization: Bearer test-api-key-org-1"

# With limit
curl "http://localhost:8002/organization/proofs?limit=10" \
  -H "Authorization: Bearer test-api-key-org-1"

# Date range
curl "http://localhost:8002/organization/proofs?start_time=2026-03-01T00:00:00Z&limit=50" \
  -H "Authorization: Bearer test-api-key-org-1"
```

---

## Authentication

### API Key Format
```
Header: Authorization: Bearer <api-key>
```

### Example
```bash
curl http://localhost:8002/health \
  -H "Authorization: Bearer test-api-key-org-1"
```

### Environment Variable
```bash
export CIAF_API_KEY="test-api-key-org-1"

curl http://localhost:8002/health \
  -H "Authorization: Bearer $CIAF_API_KEY"
```

---

## Error Handling

### Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Proof submitted successfully |
| 400 | Bad Request | Invalid JSON or missing fields |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Proof ID doesn't exist |
| 500 | Server Error | Internal server error |

### Error Response
```json
{
  "detail": "Proof not found"
}
```

### Handling Errors
```python
import requests

try:
    response = requests.get(
        "http://localhost:8002/verify/invalid-id",
        headers={"Authorization": "Bearer test-api-key-org-1"}
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Proof not found")
    elif e.response.status_code == 401:
        print("Invalid API key")
```

---

## Complete Python Example

```python
import requests
import json
from datetime import datetime

# Configuration
API_KEY = "test-api-key-org-1"
VAULT_URL = "http://localhost:8002"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 1. Health check
response = requests.get(f"{VAULT_URL}/health")
print(f"Status: {response.json()['status']}")

# 2. Submit proof
proof_data = {
    "content": "AI model inference result",
    "agent_ids": ["agent-1", "agent-2"],
    "policies_applied": ["policy-gdpr"],
    "timestamp": datetime.now().isoformat()
}

response = requests.post(
    f"{VAULT_URL}/submit",
    json=proof_data,
    headers=headers
)
receipt = response.json()
proof_id = receipt["proof_id"]
print(f"Proof ID: {proof_id}")

# 3. Verify proof
response = requests.get(
    f"{VAULT_URL}/verify/{proof_id}",
    headers=headers
)
proof = response.json()
print(f"Read count: {proof['read_count']}")

# 4. Generate certificate
response = requests.post(
    f"{VAULT_URL}/certificate/{proof_id}",
    headers=headers
)
cert = response.json()
print(f"Certificate ID: {cert['certificate_id']}")

# 5. Get audit trail
response = requests.get(
    f"{VAULT_URL}/audit-trail",
    headers=headers,
    params={"limit": 10}
)
audit = response.json()
print(f"Total entries: {audit['total']}")
```

---

## Use Cases

### 1. Healthcare - HIPAA Compliance
```python
# Submit patient diagnosis proof
proof = {
    "content": json.dumps({
        "patient_id": "HASH123",
        "diagnosis_code": "E11.22",
        "confidence": 0.98,
        "model": "clinical-classifier-v2"
    }),
    "agent_ids": ["clinical-nlp", "validator"],
    "policies_applied": ["HIPAA", "GDPR", "DATA-MINIMIZATION"],
    "timestamp": datetime.now().isoformat()
}
```

### 2. Banking - AML Verification
```python
# Submit transaction risk assessment
proof = {
    "content": json.dumps({
        "transaction_id": "TXN456",
        "risk_score": 0.35,
        "risk_level": "low",
        "model": "aml-detector-v3"
    }),
    "agent_ids": ["aml-scorer", "aml-validator"],
    "policies_applied": ["AML", "KYC", "OFAC"],
    "timestamp": datetime.now().isoformat()
}
```

### 3. AI Governance - Model Audit
```python
# Submit inference for audit trail
proof = {
    "content": json.dumps({
        "model_version": "v4.2.1",
        "input_hash": "SHA256...",
        "output": "classification",
        "timestamp": datetime.now().isoformat(),
        "metrics": {"latency_ms": 125, "confidence": 0.95}
    }),
    "agent_ids": ["model-server", "audit-logger"],
    "policies_applied": ["MODEL-AUDIT", "GOVERNANCE"],
    "timestamp": datetime.now().isoformat()
}
```

---

## Performance

### Expected Response Times
- Health check: <50ms
- Submit proof: <100ms
- Verify proof: <50ms
- Audit trail (100 entries): <200ms

### Throughput
- Submit: ~1000 proofs/second
- Verify: ~5000 ops/second
- Database: PostgreSQL optimized

---

## Security

### Encryption
- TLS/SSL in production
- Ed25519 signatures on certificates
- SHA-256 hashing of proofs

### WORM Guarantee
- Write-once-read-many storage
- No deletion or modification
- Immutable audit trail

### Access Control
- API key authentication
- Per-organization isolation
- Read count auditing

---

## Rate Limiting

Currently no rate limits in development.

Production settings:
- 1000 requests/minute per API key
- 100 concurrent connections
- Contact support for higher limits

---

**Status:** ✅ Ready to Use
**Last Updated:** 2026-03-14
