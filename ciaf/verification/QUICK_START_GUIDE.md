# CIAF Verification Microservice - Quick Start Guide

Get up and running with the CIAF Verification Microservice in 10 minutes.

---

## Prerequisites

- **Python:** 3.8+
- **PostgreSQL:** 12+
- **Git:** For cloning repository
- **pip:** Python package manager
- **Optional:** Docker & Docker Compose (for containerized setup)

**System Requirements:**
- 2GB RAM minimum
- 1GB disk space (proof store)
- Linux, macOS, or Windows (WSL2)

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/anthropics/CIAF-Models.git
cd CIAF_Model_Creation
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Requirements include:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `asyncpg` - PostgreSQL async driver
- `pydantic` - Data validation
- `cryptography` - Proof verification

### Step 3: Set Up PostgreSQL

**Option A: Docker (Recommended)**

```bash
docker run --name ciaf-postgres \
  -e POSTGRES_PASSWORD=ciaf_password \
  -e POSTGRES_USER=ciaf_user \
  -e POSTGRES_DB=ciaf_proofs \
  -p 5432:5432 \
  -d postgres:14
```

**Option B: Local Installation**

```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Linux (Ubuntu)
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start

# Windows (via WSL2 or native)
# Download from: https://www.postgresql.org/download/windows/
```

### Step 4: Initialize Database

```bash
# Create database and user
psql -U postgres -c "CREATE DATABASE ciaf_proofs;"
psql -U postgres -c "CREATE USER ciaf_verification WITH PASSWORD 'secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ciaf_proofs TO ciaf_verification;"

# Load schema
psql -U ciaf_verification -d ciaf_proofs < ciaf/verification/POSTGRESQL_SCHEMA.py
```

### Step 5: Configure Environment

Create `.env` file:

```bash
cat > .env << EOF
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://ciaf_verification:secure_password@localhost:5432/ciaf_proofs

# Service
VERIFICATION_SERVICE_PORT=8001
API_KEY_SECRET=sk_test_abc123def456

# Logging
LOG_LEVEL=INFO

# CIAF Core (for integration)
CIAF_API_URL=http://localhost:8000
CIAF_API_KEY=ciaf_core_key_here
EOF
```

### Step 6: Run Verification Service

```bash
cd ciaf/verification
python -m uvicorn api:create_verification_app --host 0.0.0.0 --port 8001 --reload
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### Step 7: Verify Service is Running

```bash
# In another terminal
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "CIAF Verification Microservice",
  "proof_store_stats": {
    "output_tags_count": 0
  }
}
```

✅ **Success!** Service is running.

---

## First Successful Run

### Example 1: Verify Sample Output

```python
import requests

# Initialize client
BASE_URL = "http://localhost:8001"
API_KEY = "sk_test_abc123def456"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Create a sample tag (in production, this comes from CIAF core)
sample_tag_id = "550e8400-e29b-41d4-a716-446655440000"

# Verify the output
response = requests.get(
    f"{BASE_URL}/verify/{sample_tag_id}",
    headers=headers,
    params={"include_audit_trail": True}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Verified: {result['verified']}")
    print(f"Organization: {result['organization_id']}")
    print(f"Agents: {result['agent_ids']}")
else:
    print(f"Error: {response.json()}")
```

### Example 2: Get Organization Statistics

```python
import requests

BASE_URL = "http://localhost:8001"
API_KEY = "sk_test_abc123def456"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Get stats
response = requests.get(
    f"{BASE_URL}/stats/healthcare_org_001",
    headers=headers
)

if response.status_code == 200:
    stats = response.json()
    print(f"Total outputs: {stats['total_tags']}")
    print(f"Verified: {stats['verified_tags']}")
    print(f"High-risk: {stats['high_risk_tags']}")
    print(f"Verification rate: {stats['verified_tags']/stats['total_tags']:.1%}")
```

### Example 3: Generate Compliance Report

```python
import requests

BASE_URL = "http://localhost:8001"
API_KEY = "sk_test_abc123def456"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Get HIPAA compliance
response = requests.get(
    f"{BASE_URL}/compliance/healthcare_org_001",
    headers=headers,
    params={"policy": "HIPAA_COMPLIANT"}
)

if response.status_code == 200:
    report = response.json()
    print(f"Policy: {report['policy']}")
    print(f"Total outputs: {report['total_outputs']}")
    print(f"Policy covered: {report['policy_covered']}")
    print(f"Compliance rate: {report['compliance_rate']:.1%}")
```

---

## Interactive API Documentation

The service includes **Swagger UI** for interactive API testing:

1. **Swagger UI:** http://localhost:8001/docs
2. **ReDoc:** http://localhost:8001/redoc

**To use Swagger UI:**
1. Navigate to http://localhost:8001/docs
2. Click "Authorize" button
3. Enter API key: `sk_test_abc123def456`
4. Click any endpoint to expand
5. Click "Try it out" to test
6. Enter parameters and click "Execute"

---

## Common Tasks

### Task 1: Verify an Output

```bash
curl -X GET \
  'http://localhost:8001/verify/550e8400-e29b-41d4-a716-446655440000' \
  -H "Authorization: Bearer sk_test_abc123def456"
```

### Task 2: Get Audit Trail

```bash
curl -X GET \
  'http://localhost:8001/audit/550e8400-e29b-41d4-a716-446655440000' \
  -H "Authorization: Bearer sk_test_abc123def456"
```

### Task 3: Check Compliance

```bash
curl -X GET \
  'http://localhost:8001/compliance/healthcare_org_001?policy=HIPAA_COMPLIANT' \
  -H "Authorization: Bearer sk_test_abc123def456"
```

### Task 4: Get Stats

```bash
curl -X GET \
  'http://localhost:8001/stats/healthcare_org_001' \
  -H "Authorization: Bearer sk_test_abc123def456"
```

### Task 5: Refresh Cache (Admin)

```bash
curl -X POST \
  'http://localhost:8001/admin/refresh-cache' \
  -H "Authorization: Bearer admin_key_xyz"
```

---

## Python Client Library

Create a reusable client for common operations:

```python
import requests
from typing import Dict, Any

class CIAFClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def verify(self, tag_id: str) -> Dict[str, Any]:
        """Verify output."""
        response = requests.get(
            f"{self.base_url}/verify/{tag_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def audit(self, tag_id: str) -> Dict[str, Any]:
        """Get audit trail."""
        response = requests.get(
            f"{self.base_url}/audit/{tag_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def compliance(self, org_id: str, policy: str = None) -> Dict[str, Any]:
        """Get compliance report."""
        params = {}
        if policy:
            params["policy"] = policy

        response = requests.get(
            f"{self.base_url}/compliance/{org_id}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def stats(self, org_id: str) -> Dict[str, Any]:
        """Get organization stats."""
        response = requests.get(
            f"{self.base_url}/stats/{org_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = CIAFClient("http://localhost:8001", "sk_test_abc123")

# Verify an output
result = client.verify("550e8400-e29b-41d4-a716-446655440000")
print(f"Verified: {result['verified']}")

# Get compliance
compliance = client.compliance("healthcare_org_001", "HIPAA_COMPLIANT")
print(f"Compliance rate: {compliance['compliance_rate']:.1%}")

# Get stats
stats = client.stats("healthcare_org_001")
print(f"Total: {stats['total_tags']}, Verified: {stats['verified_tags']}")
```

---

## Integration with CIAF Core

### Architecture

```
CIAF Core (Port 8000)
  ├─ Agent Registry
  ├─ Session Management
  ├─ Output Tagging
  └─ Org Batch Scheduling
        ↓ (publishes proofs)
PostgreSQL
        ↓ (queries proofs)
Verification Service (Port 8001)
  ├─ /verify/{tag_id}
  ├─ /audit/{tag_id}
  ├─ /compliance/{org}
  └─ /stats/{org}
```

### Example: End-to-End Workflow

```python
import asyncio
from ciaf.sessions import AgentSession
from ciaf.verification import PostgresProofStore, VerificationService

async def end_to_end_example():
    # Step 1: Create output with CIAF core
    session = AgentSession(
        session_id="demo_001",
        user_id="user_001",
        organization_id="healthcare_org_001"
    )

    session.start_task("Analyze patient data")

    # Record agent output
    tag = session.record_output(
        output_content="Clinical assessment: Normal",
        inference_receipt_id="lcm_123",
        agent_ids=["reader_001", "analyzer_001"],
        policies_applied=["HIPAA_COMPLIANT"],
        risk_level="low"
    )

    task = session.complete_current_task("success")
    session.end_session()

    # Step 2: Store proof
    proof_store = PostgresProofStore()
    await proof_store.connect()
    await proof_store.store_output_tag(tag)

    # Step 3: Verify
    verification_service = VerificationService(proof_store)
    result = await verification_service.verify_output(
        tag_id=tag.tag_id,
        verify_merkle=True,
        include_audit_trail=True
    )

    print(f"Verified: {result.verified}")
    print(f"Agents: {result.agent_ids}")
    print(f"Policies: {result.policies_applied}")

# Run
asyncio.run(end_to_end_example())
```

---

## Troubleshooting

### Issue: Connection Refused (Port 8001)

```
Error: Connection refused
```

**Solution:**
1. Check service is running: `ps aux | grep uvicorn`
2. Verify port is available: `lsof -i :8001`
3. Restart service: `python -m uvicorn api:create_verification_app --port 8001`

### Issue: Database Connection Error

```
Error: could not connect to server: Connection refused
```

**Solution:**
1. Check PostgreSQL is running: `psql -U postgres -c "SELECT 1"`
2. Verify connection string in `.env`
3. Restart PostgreSQL: `brew services restart postgresql`

### Issue: 404 Not Found on API Endpoint

**Solution:**
1. Verify tag_id format (should be UUID)
2. Check tag exists in database: `psql -U ciaf_verification -d ciaf_proofs -c "SELECT * FROM output_tags LIMIT 1"`
3. Ensure tag was published from CIAF core

### Issue: 401 Unauthorized

```
Error: {"detail": "Not authenticated"}
```

**Solution:**
1. Verify API key in header: `Authorization: Bearer sk_test_abc123`
2. Check `.env` file has correct `API_KEY_SECRET`
3. Use correct format: `Bearer {token}` (with space)

### Issue: Slow Responses (>1 second)

**Solution:**
1. Check database connection: `time curl http://localhost:8001/health`
2. Monitor PostgreSQL performance: `sudo pgbench`
3. Increase connection pool:
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=10
   )
   ```

---

## Development Workflow

### 1. Start Services

```bash
# Terminal 1: PostgreSQL
docker run --name ciaf-postgres -e POSTGRES_PASSWORD=ciaf -p 5432:5432 -d postgres:14

# Terminal 2: Verification service
python -m uvicorn ciaf/verification/api:create_verification_app --reload

# Terminal 3: CIAF core (if integrating)
python -m uvicorn ciaf/api:app --port 8000 --reload
```

### 2. Test Changes

```bash
# Run unit tests
pytest ciaf/verification/tests/ -v

# Run integration tests
pytest tests/integration/ -v --tb=short
```

### 3. Check Code Quality

```bash
# Lint
flake8 ciaf/verification --max-line-length=100

# Type check
mypy ciaf/verification

# Format
black ciaf/verification
```

### 4. View Logs

```bash
# Service logs
docker logs -f ciaf-postgres

# Python logs (see terminal output)
# Or configure logging:

import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Next Steps

### For Production Deployment:
1. Follow the [Production Deployment Runbook](./PRODUCTION_DEPLOYMENT.md)
2. Set up PostgreSQL with backups
3. Configure authentication (OAuth 2.0)
4. Deploy with Docker/Kubernetes
5. Set up monitoring (Prometheus/Grafana)
6. Configure alerting (PagerDuty/Slack)

### For Development:
1. Review [OpenAPI Documentation](./OPENAPI_DOCUMENTATION.md)
2. Test all 7 endpoints with Swagger UI
3. Create custom client for your use case
4. Add integration tests

### For Integration:
1. Connect CIAF core to verification service
2. Publish proofs to PostgreSQL
3. Query verification API in your application
4. Build compliance dashboards

---

## Support & Resources

- **GitHub Issues:** https://github.com/anthropics/CIAF-Models/issues
- **Documentation:** `/docs` (Swagger UI)
- **Examples:** `ciaf/verification/examples/`
- **API Spec:** `ciaf/verification/openapi.yaml`

---

## Quick Reference

| Task | Command |
|------|---------|
| Start service | `uvicorn api:create_verification_app --port 8001` |
| Health check | `curl http://localhost:8001/health` |
| Verify output | `curl http://localhost:8001/verify/{tag_id}` |
| View Swagger | Open http://localhost:8001/docs |
| Connection test | `psql -U ciaf_verification -d ciaf_proofs -c "SELECT 1"` |
| View logs | Check terminal output with `--log-level=info` |

---

Created: 2025-03-13
Version: 0.1.0
License: BUSL-1.1 (converts to Apache 2.0 on Jan 1, 2029)
