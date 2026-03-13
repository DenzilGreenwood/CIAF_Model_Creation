# CIAF Verification Microservice - OpenAPI/Swagger Documentation

## Overview

The **CIAF Verification Microservice** provides external verification of AI-generated outputs through cryptographic proof validation. This REST API enables organizations to:

- **Verify outputs** are authentic with full audit trail
- **Query audit trails** showing which agents processed outputs
- **Generate compliance reports** for regulatory audits
- **Monitor statistics** across organization outputs

**Service Version:** 0.1.0
**Base URL:** `http://localhost:8001` (development) or `https://verify.ciaf.io` (production)
**Authentication:** API Key (header: `Authorization: Bearer <api_key>`)

---

## API Architecture

```
┌─────────────────────────────────────────────┐
│ CIAF Verification Microservice (Port 8001)  │
├─────────────────────────────────────────────┤
│ • Verify outputs by tag ID                  │
│ • Query agent audit trails                  │
│ • Generate compliance reports               │
│ • Retrieve organization statistics          │
│ • Health checks + cache management          │
└────────────┬────────────────────────────────┘
             │ (queries)
             ↓
┌─────────────────────────────────────────────┐
│ PostgreSQL Proof Store (Port 5432)          │
├─────────────────────────────────────────────┤
│ • output_tags (with merkle proofs)          │
│ • task_batches (merkle trees)               │
│ • org_batch_windows (time windows)          │
│ • agent_actions (audit trail)               │
└─────────────────────────────────────────────┘
```

---

## Data Models

### VerificationRequest

Request payload for verifying an output.

```json
{
  "tag_id": "550e8400-e29b-41d4-a716-446655440000",
  "verify_merkle": true,
  "include_audit_trail": true
}
```

**Fields:**
- `tag_id` (string, required): Unique identifier of output tag
- `verify_merkle` (boolean, optional, default: true): Verify cryptographic merkle proofs
- `include_audit_trail` (boolean, optional, default: true): Include agent action history

---

### VerificationResponse

Response containing complete verification results.

```json
{
  "verified": true,
  "tag_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "healthcare_org_001",
  "inference_type": "agent_orchestrated",
  "model_name": null,
  "agent_ids": ["healthcare_reader_001", "analysis_agent_001", "recommendation_agent_001"],
  "policies_applied": ["HIPAA_COMPLIANT", "FDA_SaMD", "ISO_14971"],
  "risk_level": "high",
  "task_batch_verified": true,
  "org_batch_verified": true,
  "merkle_proof_valid": true,
  "agent_audit_trail": [
    {
      "agent_id": "healthcare_reader_001",
      "action_type": "inference",
      "timestamp": "2025-03-13T10:00:00Z",
      "risk_level": "low",
      "status": "success"
    },
    {
      "agent_id": "analysis_agent_001",
      "action_type": "analysis",
      "timestamp": "2025-03-13T10:01:30Z",
      "risk_level": "medium",
      "status": "success"
    }
  ],
  "issues": [],
  "warnings": []
}
```

**Fields:**
- `verified` (boolean): Whether output is authentic
- `tag_id` (string): Output tag ID
- `organization_id` (string): Organization that generated output
- `inference_type` (string): "agent_orchestrated" or "direct_model"
- `model_name` (string, nullable): Model name (for direct_model inference)
- `agent_ids` (array): Agent IDs involved (for agent_orchestrated)
- `policies_applied` (array): Policies enforced during generation
- `risk_level` (string): "low", "medium", "high", "critical"
- `task_batch_verified` (boolean): Task-level merkle proof valid
- `org_batch_verified` (boolean): Org-level merkle proof valid
- `merkle_proof_valid` (boolean): Overall cryptographic proof valid
- `agent_audit_trail` (array): Sequence of agent actions (if requested)
- `issues` (array): Verification failures detected
- `warnings` (array): Non-blocking issues found

---

### AuditAction

Single action in agent audit trail.

```json
{
  "agent_id": "healthcare_reader_001",
  "action_type": "inference",
  "timestamp": "2025-03-13T10:00:00Z",
  "risk_level": "low",
  "status": "success"
}
```

**Fields:**
- `agent_id` (string): Which agent performed action
- `action_type` (string): "inference", "analysis", "decision", "escalation"
- `timestamp` (string): ISO 8601 timestamp
- `risk_level` (string): "low", "medium", "high", "critical"
- `status` (string): "success", "failure", "partial"

---

### ComplianceReport

Policy compliance metrics for organization.

```json
{
  "organization_id": "healthcare_org_001",
  "policy": "HIPAA_COMPLIANT",
  "total_outputs": 1250,
  "policy_covered": 1245,
  "compliance_rate": 0.996,
  "verified_outputs": 1240
}
```

**Fields:**
- `organization_id` (string): Organization ID
- `policy` (string): Policy name (e.g., "HIPAA_COMPLIANT")
- `total_outputs` (integer): Total outputs from organization
- `policy_covered` (integer): Outputs where policy was applied
- `compliance_rate` (float): Percentage (0.0-1.0) of outputs compliant
- `verified_outputs` (integer): Outputs successfully verified

---

### OrganizationStats

Organization-level verification statistics.

```json
{
  "organization_id": "healthcare_org_001",
  "total_tags": 2500,
  "verified_tags": 2485,
  "high_risk_tags": 145,
  "critical_tags": 8,
  "total_batch_windows": 42
}
```

**Fields:**
- `organization_id` (string): Organization ID
- `total_tags` (integer): Total output tags created
- `verified_tags` (integer): Successfully verified
- `high_risk_tags` (integer): Count of high-risk outputs
- `critical_tags` (integer): Count of critical-risk outputs
- `total_batch_windows` (integer): Number of org batch windows

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Service availability and proof store statistics.

**Authorization:** None

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "service": "CIAF Verification Microservice",
  "proof_store_stats": {
    "output_tags_count": 10500,
    "task_batches_count": 2450,
    "org_batch_windows_count": 410,
    "agent_actions_count": 125000,
    "verification_cache_hits": 98500,
    "last_sync": "2025-03-13T14:32:00Z"
  }
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8001/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "service": "CIAF Verification Microservice",
  "proof_store_stats": {
    "output_tags_count": 10500
  }
}
```

---

### 2. Verify Output (POST)

**Endpoint:** `POST /verify`

**Description:** Verify AI-generated output with complete audit trail.

**Authorization:** Bearer token (required in production)

**Request Body:** `VerificationRequest`

**Response:** `200 OK` or `400 Bad Request`

**Response Model:** `VerificationResponse`

**Example Request:**
```bash
curl -X POST http://localhost:8001/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer abc123xyz" \
  -d '{
    "tag_id": "550e8400-e29b-41d4-a716-446655440000",
    "verify_merkle": true,
    "include_audit_trail": true
  }'
```

**Example Response (Success):**
```json
{
  "verified": true,
  "tag_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "healthcare_org_001",
  "inference_type": "agent_orchestrated",
  "model_name": null,
  "agent_ids": ["healthcare_reader_001", "analysis_agent_001"],
  "policies_applied": ["HIPAA_COMPLIANT", "FDA_SaMD"],
  "risk_level": "high",
  "task_batch_verified": true,
  "org_batch_verified": true,
  "merkle_proof_valid": true,
  "agent_audit_trail": [
    {
      "agent_id": "healthcare_reader_001",
      "action_type": "inference",
      "timestamp": "2025-03-13T10:00:00Z",
      "risk_level": "low",
      "status": "success"
    }
  ],
  "issues": [],
  "warnings": []
}
```

**Example Response (Failure):**
```json
{
  "detail": "Tag not found or merkle proof invalid"
}
```

**Status Codes:**
- `200 OK` - Verification complete (check `verified` field)
- `400 Bad Request` - Invalid tag_id or verification failed
- `401 Unauthorized` - Missing or invalid API key
- `500 Internal Server Error` - Database error

**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:8001/verify',
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer abc123xyz'
    },
    json={
        'tag_id': '550e8400-e29b-41d4-a716-446655440000',
        'verify_merkle': True,
        'include_audit_trail': True
    }
)

result = response.json()
print(f"Verified: {result['verified']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Agents: {result['agent_ids']}")
```

---

### 3. Verify Output (GET)

**Endpoint:** `GET /verify/{tag_id}`

**Description:** Verify output by tag ID (GET method for browser-friendly access).

**Authorization:** Bearer token (optional for GET, required in production)

**Path Parameters:**
- `tag_id` (string, required): Output tag ID

**Query Parameters:**
- `verify_merkle` (boolean, optional, default: true): Verify merkle proofs
- `include_audit_trail` (boolean, optional, default: true): Include audit trail

**Response:** `200 OK` or `404 Not Found`

**Response Model:** `VerificationResponse`

**Example Request:**
```bash
curl -X GET \
  'http://localhost:8001/verify/550e8400-e29b-41d4-a716-446655440000?verify_merkle=true&include_audit_trail=true' \
  -H "Authorization: Bearer abc123xyz"
```

**Example Response:**
```json
{
  "verified": true,
  "tag_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "healthcare_org_001",
  ...
}
```

**Status Codes:**
- `200 OK` - Tag found and verified
- `404 Not Found` - Tag not found in database
- `401 Unauthorized` - Missing or invalid API key
- `500 Internal Server Error` - Database error

**JavaScript Example:**
```javascript
async function verifyOutput(tagId) {
  const response = await fetch(
    `/verify/${tagId}?verify_merkle=true&include_audit_trail=true`,
    {
      headers: {
        'Authorization': 'Bearer abc123xyz'
      }
    }
  );

  const result = await response.json();
  console.log(`Verified: ${result.verified}`);
  console.log(`Agents: ${result.agent_ids.join(', ')}`);
  return result;
}
```

---

### 4. Get Audit Trail

**Endpoint:** `GET /audit/{tag_id}`

**Description:** Get agent audit trail for an output (which agents processed it, in what order).

**Authorization:** Bearer token (required)

**Path Parameters:**
- `tag_id` (string, required): Output tag ID

**Response:** `200 OK` or `404 Not Found`

**Response Schema:**
```json
{
  "tag_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_ids": ["healthcare_reader_001", "analysis_agent_001", "recommendation_agent_001"],
  "inference_type": "agent_orchestrated",
  "model_name": null,
  "actions": [
    {
      "agent_id": "healthcare_reader_001",
      "action_type": "inference",
      "timestamp": "2025-03-13T10:00:00Z",
      "risk_level": "low",
      "status": "success"
    },
    {
      "agent_id": "analysis_agent_001",
      "action_type": "analysis",
      "timestamp": "2025-03-13T10:01:30Z",
      "risk_level": "medium",
      "status": "success"
    },
    {
      "agent_id": "recommendation_agent_001",
      "action_type": "decision",
      "timestamp": "2025-03-13T10:02:15Z",
      "risk_level": "high",
      "status": "success"
    }
  ]
}
```

**Example Request:**
```bash
curl -X GET \
  'http://localhost:8001/audit/550e8400-e29b-41d4-a716-446655440000' \
  -H "Authorization: Bearer abc123xyz"
```

**Status Codes:**
- `200 OK` - Audit trail retrieved
- `404 Not Found` - Tag not found
- `401 Unauthorized` - Invalid credentials
- `500 Internal Server Error` - Database error

**Use Cases:**
- Regulatory audits (prove which agents touched data)
- Non-repudiation (prove output came from specific agents)
- Compliance verification (verify policy enforcement)
- Incident investigation (trace output history)

---

### 5. Get Compliance Report

**Endpoint:** `GET /compliance/{organization_id}`

**Description:** Get policy compliance report for organization.

**Authorization:** Bearer token (required)

**Path Parameters:**
- `organization_id` (string, required): Organization ID

**Query Parameters:**
- `policy` (string, optional): Filter by specific policy (e.g., "HIPAA_COMPLIANT")

**Response:** `200 OK` or `404 Not Found`

**Response Model:** `ComplianceReport`

**Example Requests:**

All policies:
```bash
curl -X GET \
  'http://localhost:8001/compliance/healthcare_org_001' \
  -H "Authorization: Bearer abc123xyz"
```

Specific policy:
```bash
curl -X GET \
  'http://localhost:8001/compliance/healthcare_org_001?policy=HIPAA_COMPLIANT' \
  -H "Authorization: Bearer abc123xyz"
```

**Example Response:**
```json
{
  "organization_id": "healthcare_org_001",
  "policy": "HIPAA_COMPLIANT",
  "total_outputs": 2500,
  "policy_covered": 2485,
  "compliance_rate": 0.994,
  "verified_outputs": 2480
}
```

**Interpretation:**
- `compliance_rate = policy_covered / total_outputs`
- 99.4% of outputs had HIPAA policy applied
- 99.2% of those were successfully verified

**Status Codes:**
- `200 OK` - Report generated
- `404 Not Found` - Organization not found
- `401 Unauthorized` - Invalid credentials

**Regulatory Use Cases:**
- SOC 2 audits (demonstrate policy enforcement)
- HIPAA compliance verification (prove security policies applied)
- Fair lending audits (show ECOA/ECOA compliance checks)
- FDA SaMD audits (document validation policies)

---

### 6. Get Organization Statistics

**Endpoint:** `GET /stats/{organization_id}`

**Description:** Get verification statistics for organization.

**Authorization:** Bearer token (required)

**Path Parameters:**
- `organization_id` (string, required): Organization ID

**Response:** `200 OK` or `404 Not Found`

**Response Model:** `OrganizationStats`

**Example Request:**
```bash
curl -X GET \
  'http://localhost:8001/stats/healthcare_org_001' \
  -H "Authorization: Bearer abc123xyz"
```

**Example Response:**
```json
{
  "organization_id": "healthcare_org_001",
  "total_tags": 2500,
  "verified_tags": 2485,
  "high_risk_tags": 145,
  "critical_tags": 8,
  "total_batch_windows": 42
}
```

**Metrics Interpretation:**
- `verified_tags / total_tags = 99.4%` verification rate
- `145 high_risk_tags` require additional review
- `8 critical_tags` need immediate attention
- `42 batch_windows` = 7 days × 24 hours ÷ 6-hour windows

**Status Codes:**
- `200 OK` - Statistics retrieved
- `404 Not Found` - Organization not found
- `401 Unauthorized` - Invalid credentials

**Monitoring Use Cases:**
- Dashboard metrics (verification success rate)
- Risk trending (critical outputs per day)
- SLA monitoring (verify within 24h)
- Capacity planning (batch windows per day)

---

### 7. Refresh Cache (Admin)

**Endpoint:** `POST /admin/refresh-cache`

**Description:** Refresh merkle proof cache from database (admin only).

**Authorization:** Admin API key (required)

**Request Body:** Empty

**Response:** `200 OK`

**Example Request:**
```bash
curl -X POST \
  'http://localhost:8001/admin/refresh-cache' \
  -H "Authorization: Bearer admin_key_xyz"
```

**Example Response:**
```json
{
  "status": "cache_refreshed",
  "stats": {
    "output_tags_count": 10500,
    "task_batches_count": 2450,
    "org_batch_windows_count": 410,
    "agent_actions_count": 125000,
    "cache_entries": 10500,
    "cache_hit_rate": 0.938
  },
  "message": "Merkle proof cache refreshed from database"
}
```

**Production Implementation:**

In production, this endpoint would:
1. Invalidate Redis cache
2. Reload all org batch window merkle roots
3. Rebuild task batch merkle proof trees
4. Update verification statistics
5. Return cache metrics

**Caching Strategy:**
```python
# Development: In-memory cache
cache: Dict[str, MerkleProof] = {}

# Production: Redis cache
import redis
cache = redis.Redis(host='localhost', port=6379)

# Cache patterns
- output_tags: 5-minute TTL (frequently verified)
- merkle_proofs: 1-hour TTL (org windows immutable)
- org_stats: 1-hour TTL (compute expensive)
```

**When to Call:**
- After org batch window creation
- When deploying new batch window merkle trees
- On-demand during maintenance windows
- Scheduled daily (2 AM UTC)

---

## Authentication & Authorization

### API Key Authentication

All production endpoints require bearer token in `Authorization` header:

```bash
Authorization: Bearer <api_key>
```

**Example:**
```bash
curl -X GET http://localhost:8001/verify/tag_id \
  -H "Authorization: Bearer sk_live_abc123def456ghi789"
```

### Permission Scopes

```
read:verify              - Can verify outputs
read:audit               - Can access audit trails
read:compliance          - Can view compliance reports
read:stats               - Can view organization stats
admin:refresh            - Can refresh cache (admin only)
```

**Example Protected Endpoint:**
```python
from fastapi import Security, HTTPException
from security import get_api_key

@app.get("/verify/{tag_id}")
async def verify(tag_id: str, api_key: str = Security(get_api_key)):
    # Check permission scopes
    if "read:verify" not in api_key.scopes:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    ...
```

---

## Error Handling

### HTTP Status Codes

| Status | Meaning | When |
|--------|---------|------|
| 200 | OK | Verification successful |
| 400 | Bad Request | Invalid tag_id format |
| 401 | Unauthorized | Missing/invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Tag not found in database |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Database error |
| 503 | Service Unavailable | Proof store offline |

### Error Response Format

```json
{
  "detail": "Tag not found or merkle proof invalid",
  "code": "TAG_NOT_FOUND",
  "timestamp": "2025-03-13T14:32:00Z"
}
```

### Common Error Scenarios

**Invalid Tag ID:**
```
Status: 400
Detail: "Invalid tag ID format (expected UUID)"
```

**Tag Not Found:**
```
Status: 404
Detail: "Tag not found in proof store"
```

**Merkle Proof Invalid:**
```
Status: 400
Detail: "Merkle proof could not be validated against batch root"
```

**Database Connection Error:**
```
Status: 503
Detail: "Proof store temporarily unavailable"
```

---

## Rate Limiting

Production rate limits (per API key):

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/verify` | 1000 req | 1 minute |
| `/audit` | 500 req | 1 minute |
| `/compliance` | 100 req | 1 hour |
| `/stats` | 100 req | 1 hour |
| `/admin` | 10 req | 1 hour |

**Rate Limit Headers:**
```
RateLimit-Limit: 1000
RateLimit-Remaining: 847
RateLimit-Reset: 1678791600
```

---

## Usage Examples

### Python Client

```python
import requests
import json
from typing import Dict, Any

class CIAFVerificationClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def verify_output(self, tag_id: str) -> Dict[str, Any]:
        """Verify output by tag ID."""
        response = requests.get(
            f"{self.base_url}/verify/{tag_id}",
            headers=self.headers,
            params={"include_audit_trail": True}
        )
        response.raise_for_status()
        return response.json()

    def get_audit_trail(self, tag_id: str) -> Dict[str, Any]:
        """Get agent audit trail."""
        response = requests.get(
            f"{self.base_url}/audit/{tag_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_compliance_report(
        self,
        organization_id: str,
        policy: str = None
    ) -> Dict[str, Any]:
        """Get policy compliance report."""
        params = {}
        if policy:
            params["policy"] = policy

        response = requests.get(
            f"{self.base_url}/compliance/{organization_id}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get organization statistics."""
        response = requests.get(
            f"{self.base_url}/stats/{organization_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = CIAFVerificationClient(
    base_url="http://localhost:8001",
    api_key="sk_test_abc123"
)

# Verify an output
result = client.verify_output("550e8400-e29b-41d4-a716-446655440000")
print(f"Verified: {result['verified']}")
print(f"Agents: {result['agent_ids']}")
print(f"Compliance: {result['policies_applied']}")

# Get audit trail
audit = client.get_audit_trail("550e8400-e29b-41d4-a716-446655440000")
for action in audit["actions"]:
    print(f"{action['agent_id']}: {action['action_type']} @ {action['timestamp']}")

# Check compliance
compliance = client.get_compliance_report("healthcare_org_001", policy="HIPAA_COMPLIANT")
print(f"Compliance Rate: {compliance['compliance_rate']:.1%}")
```

### JavaScript/Node.js Client

```javascript
class CIAFVerificationClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async verifyOutput(tagId) {
    const response = await fetch(
      `${this.baseUrl}/verify/${tagId}?include_audit_trail=true`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getAuditTrail(tagId) {
    const response = await fetch(
      `${this.baseUrl}/audit/${tagId}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getComplianceReport(organizationId, policy = null) {
    let url = `${this.baseUrl}/compliance/${organizationId}`;
    if (policy) url += `?policy=${policy}`;

    const response = await fetch(url, { headers: this.headers });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getStats(organizationId) {
    const response = await fetch(
      `${this.baseUrl}/stats/${organizationId}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

// Usage
const client = new CIAFVerificationClient(
  'http://localhost:8001',
  'sk_test_abc123'
);

// Verify output
const result = await client.verifyOutput('550e8400-e29b-41d4-a716-446655440000');
console.log(`Verified: ${result.verified}`);
console.log(`Agents: ${result.agent_ids.join(', ')}`);

// Get stats
const stats = await client.getStats('healthcare_org_001');
console.log(`Verified: ${stats.verified_tags}/${stats.total_tags}`);
```

### cURL Examples

**Verify output:**
```bash
curl -X GET \
  'http://localhost:8001/verify/550e8400-e29b-41d4-a716-446655440000' \
  -H "Authorization: Bearer sk_test_abc123" \
  -H "Content-Type: application/json"
```

**Get audit trail:**
```bash
curl -X GET \
  'http://localhost:8001/audit/550e8400-e29b-41d4-a716-446655440000' \
  -H "Authorization: Bearer sk_test_abc123"
```

**Get compliance report:**
```bash
curl -X GET \
  'http://localhost:8001/compliance/healthcare_org_001?policy=HIPAA_COMPLIANT' \
  -H "Authorization: Bearer sk_test_abc123"
```

**Get stats:**
```bash
curl -X GET \
  'http://localhost:8001/stats/healthcare_org_001' \
  -H "Authorization: Bearer sk_test_abc123"
```

**Refresh cache (admin):**
```bash
curl -X POST \
  'http://localhost:8001/admin/refresh-cache' \
  -H "Authorization: Bearer admin_key_xyz" \
  -H "Content-Type: application/json"
```

---

## Deployment

### Local Development

```bash
cd ciaf-verification-service

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Start service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker Production

```bash
# Build image
docker build -t ciaf-verification:latest .

# Run with PostgreSQL
docker run -d \
  --name verification-service \
  -p 8001:8001 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@postgres:5432/ciaf_proofs" \
  -e API_KEY_SECRET="your_secret_here" \
  --network ciaf-network \
  ciaf-verification:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ciaf-verification
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ciaf-verification
  template:
    metadata:
      labels:
        app: ciaf-verification
    spec:
      containers:
      - name: verification
        image: ciaf-verification:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ciaf-secrets
              key: database-url
        - name: API_KEY_SECRET
          valueFrom:
            secretKeyRef:
              name: ciaf-secrets
              key: api-key-secret
```

---

## Performance & Monitoring

### Response Times (SLA)

| Operation | Target | Typical |
|-----------|--------|---------|
| `/verify` | <100ms | 45ms |
| `/audit` | <50ms | 20ms |
| `/compliance` | <500ms | 250ms |
| `/stats` | <500ms | 300ms |

### Metrics to Monitor

```python
# Query counts (per minute)
verification_queries: Counter
audit_queries: Counter
compliance_queries: Counter

# Response latencies
verify_latency: Histogram
audit_latency: Histogram

# Cache performance
cache_hit_rate: Gauge (target: >95%)
cache_memory_usage: Gauge

# Database performance
query_duration: Histogram
connection_pool_usage: Gauge (target: <80%)

# Errors
verification_errors: Counter
database_errors: Counter
authentication_failures: Counter
```

### Health Check Configuration

```bash
# Kubernetes liveness probe
curl -f http://localhost:8001/health || exit 1

# Docker health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1
```

---

## Security Considerations

### Data Protection

- **In Transit:** TLS 1.3 for all endpoints
- **At Rest:** PostgreSQL encryption (pgcrypto extension)
- **Proofs:** Merkle roots immutable, stored separately

### Access Control

- **Authentication:** OAuth 2.0 with JWT tokens
- **Authorization:** Scope-based (read:verify, admin:refresh)
- **Rate Limiting:** Per-API-key rate limits

### Audit & Compliance

- **Request Logging:** All verifications logged with timestamp, result, user
- **Access Logs:** Who queried what, when
- **Compliance:** SOC 2 Type II, ISO 27001 ready

---

## Support & Documentation

- **Repository:** https://github.com/anthropics/CIAF-Models
- **Issues:** Report bugs and feature requests on GitHub
- **Documentation:** Full developer guide at `/docs`
- **Swagger UI:** Interactive API explorer at `/docs` (automatic)
- **ReDoc:** Alternative documentation at `/redoc`

---

Generated: 2025-03-13
Version: 0.1.0
License: BUSL-1.1 (converts to Apache 2.0 Jan 1, 2029)
