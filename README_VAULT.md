# CIAF Vault 1.0 - Enterprise Cryptographic Proof Custodian

**The industry standard for third-party AI governance proof verification.**

CIAF Vault is a production-grade, enterprise-ready platform for storing and verifying cryptographic proofs of AI system outputs. It serves as an independent, trusted custodian that regulators, enterprises, and auditors can query directly—eliminating the need to trust individual organizations' claims about their AI systems.

> **Think of it as a notary public for AI outputs.** When an organization generates an AI output, they submit it to CIAF Vault. The vault digitally certifies it, stores it immutably, and makes it independently verifiable by anyone with an API key.

---

## 🎯 Why CIAF Vault Matters

### The Problem
```
Traditional Verification:
Organization: "Our AI system made this decision fairly."
Regulator: "How do we know?"
Organization: "Trust us."
❌ No independent verification possible
```

### The Solution
```
With CIAF Vault:
Organization: "Our AI system made this decision fairly."
↓ [Submit to CIAF Vault]
CIAF Vault: "Proof accepted, certified, and stored immutably"
↓
Regulator: "Verify this proof"
↓ [Query CIAF Vault directly]
CIAF Vault: "✓ Verified. This output came from Agent_X at timestamp_Y with policies_Z"
✅ Independent, cryptographic verification
```

---

## 🏛️ Key Features

### 1. **WORM (Write-Once-Read-Many) Storage**
- Proofs are immutable after submission
- No modifications allowed - entire audit trail preserved
- Tamper-evident storage with cryptographic signing

### 2. **Multi-Tenant Isolation**
- Complete data separation between organizations
- Row-level security enforcement
- No organization can access another's proofs

### 3. **Comprehensive Audit Logging**
- Every access logged and immutable
- Tracks: WHO accessed WHAT WHEN and WHY
- Fulfills SOC 2 requirements

### 4. **API Key Authentication**
- Organization-specific API keys
- Expiration and revocation support
- Rate limiting per key

### 5. **Cryptographic Proof Generation**
- Ed25519 digital signatures
- SHA-256 content hashing
- Verification certificates (valid 1 year)

### 6. **Regulatory Compliance Ready**
- SOC 2 Type II audit trail
- HIPAA-compatible (PHI isolation available)
- GDPR-compliant data handling
- SEC-ready reporting

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ciaf-models.git
cd CIAF_Model_Creation

# Install dependencies
pip install -r requirements.txt

# Create organization
python ciaf_vault_cli.py org create banking_org_001 "My Banking Organization"

# Create API key
python ciaf_vault_cli.py key create banking_org_001 --description "Initial key" --expires-in 365

# Save the key securely!
```

### Running the Vault

```bash
# Using Docker Compose (Recommended)
docker-compose -f docker-compose.full.yml up vault

# Or standalone
python -m uvicorn ciaf.vault.api:vault_api --host 0.0.0.0 --port 8002
```

### Your First Proof

```python
import requests

# Initialize
api_key = "your_api_key_from_cli"
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "http://localhost:8002"

# Submit proof
response = requests.post(
    f"{base_url}/submit",
    json={
        "content": "Based on analysis, approved with 95% confidence...",
        "agent_ids": ["credit_analyst_001"],
        "policies_applied": ["fair_lending", "risk_assessment"],
        "timestamp": "2026-03-14T10:30:00Z"
    },
    headers=headers
)

receipt = response.json()
print(f"✓ Proof stored: {receipt['proof_id']}")
print(f"Verify at: {receipt['verification_url']}")

# Verify proof
response = requests.get(
    f"{base_url}/verify/{receipt['proof_id']}",
    headers=headers
)

proof = response.json()
print(f"✓ Verified: {proof['verified']}")
print(f"Read count: {proof['read_count']}")
```

---

## 📋 API Reference

### Authentication
All endpoints require `Authorization: Bearer {API_KEY}` header.

### Core Endpoints

#### 1. Submit Proof (WORM)
```
POST /submit
```

**Request:**
```json
{
  "content": "AI output content",
  "agent_ids": ["agent_001"],
  "policies_applied": ["policy_1", "policy_2"],
  "timestamp": "2026-03-14T10:30:00Z",
  "metadata": {}
}
```

**Response:**
```json
{
  "receipt_id": "uuid",
  "proof_id": "uuid",
  "organization_id": "org_001",
  "timestamp": "2026-03-14T10:30:00Z",
  "verification_url": "https://vault.ciaf.io/verify/{proof_id}"
}
```

#### 2. Verify Proof (Read-Only)
```
GET /verify/{proof_id}
```

**Response:**
```json
{
  "proof_id": "uuid",
  "organization_id": "org_001",
  "timestamp": "2026-03-14T10:30:00Z",
  "verified": true,
  "read_count": 5
}
```

#### 3. Generate Certificate
```
POST /certificate/{proof_id}
```

**Response:**
```json
{
  "certificate_id": "uuid",
  "proof_id": "uuid",
  "generated_at": "2026-03-14T10:31:00Z",
  "valid_until": "2027-03-14T10:31:00Z",
  "issuer": "CIAF Vault",
  "signature": "cryptographic_signature"
}
```

#### 4. Get Audit Trail
```
GET /audit-trail?start_time=...&end_time=...&action=...&limit=100
```

**Response:**
```json
{
  "entries": [
    {
      "entry_id": "uuid",
      "action": "verify_proof",
      "timestamp": "2026-03-14T10:31:00Z",
      "result": "success"
    }
  ],
  "total": 1,
  "organization_id": "org_001"
}
```

#### 5. Get Organization Proofs
```
GET /organization/proofs?start_time=...&end_time=...&limit=100
```

**Response:**
```json
{
  "organization_id": "org_001",
  "proofs": [
    {
      "proof_id": "uuid",
      "timestamp": "2026-03-14T10:30:00Z",
      "verified": true,
      "read_count": 5
    }
  ],
  "total": 1
}
```

---

## 🔐 Security & Compliance

### WORM Enforcement
- ✅ Proofs immutable after creation
- ✅ Only reads and read-count increments allowed
- ✅ SHA-256 content hashing prevents duplicates

### Multi-Tenant Isolation
- ✅ Complete data separation
- ✅ No cross-org visibility
- ✅ API key validates org membership

### Audit Trail
- ✅ Every API call logged
- ✅ Includes: actor, timestamp, action, result, IP address
- ✅ Immutable audit log for forensics

### Cryptographic Signing
- ✅ Ed25519 signatures on all receipts/certificates
- ✅ Vault maintains master signing key
- ✅ Public key available for verification

### Regulatory Compliance
- ✅ SOC 2 Type II audit trail ready
- ✅ HIPAA-compatible (with opt-in encryption)
- ✅ GDPR data deletion support
- ✅ SEC reporting capabilities

---

## 🛠️ CLI Management

### Organization Management
```bash
# Create organization
python ciaf_vault_cli.py org create banking_org "Bank Name"

# Show organization details
python ciaf_vault_cli.py org show banking_org
```

### API Key Management
```bash
# Create API key (get raw key output!)
python ciaf_vault_cli.py key create banking_org --expires-in 365

# List keys
python ciaf_vault_cli.py key list banking_org

# Revoke key
python ciaf_vault_cli.py key revoke {key_id}
```

### Vault Management
```bash
# Show vault statistics
python ciaf_vault_cli.py vault info
# Output:
# CIAF Vault Statistics
# ==================================================
# Total Proofs: 1,234
# Total Organizations: 5
# Active Organizations: 5
# Total Reads: 12,345
# Avg Reads per Proof: 10.02
```

---

## 📊 Vault Statistics

### Available Metrics
- `total_proofs` - Total proofs stored
- `total_organizations` - Organizations with proofs
- `active_organizations` - Organizations active last 30 days
- `total_reads` - Total verification queries
- `avg_reads_per_proof` - Average reads per proof

### Endpoint
```
GET /stats
```

---

## 🌍 Multi-Region Deployment (Future)

### Planned Features
- [ ] Multi-region replication
- [ ] Cross-region failover
- [ ] Blockchain write-through (Ethereum)
- [ ] GraphQL API
- [ ] Webhook notifications
- [ ] Advanced search (Elasticsearch)

---

## 📖 Use Cases

### 1. **Banking - Fair Lending Verification**
```
Bank submits credit decision proof
→ Vault stores with fair_lending policy
→ Regulator queries vault: "Did this follow fair lending?"
→ Vault: "Yes, verified ✓"
```

### 2. **Healthcare - HIPAA Compliance**
```
Healthcare org submits clinical decision
→ Vault encrypts PHI portion
→ Generates HIPAA-compliant certificate
→ Auditor queries: "What agents accessed this?"
→ Vault returns: Full audit trail
```

### 3. **AI Governance - MultiAgent Verification**
```
Multiple agents collaborate on decision
→ Each agent submits proof with agent_id
→ Vault links proofs in chain
→ Regulator: "Show complete agent chain for this decision"
→ Vault: "Agent_A → Agent_B → Agent_C, all verified ✓"
```

---

## 🚢 Production Deployment

### Docker Compose
```bash
# Start complete vault stack
docker-compose -f docker-compose.full.yml up -d vault

# Check health
curl http://localhost:8002/health

# View logs
docker logs ciaf-vault
```

### Environment Variables
```bash
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8002
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Database Location
```bash
~/.ciaf/vault/vault.db      # Vault data (WORM)
~/.ciaf/vault/audit.db      # Audit logs
~/.ciaf/vault/auth.db       # API keys & organizations
~/.ciaf/vault/vault_key.pem # Signing key (KEEP SECURE!)
```

---

## 📊 Monitoring & Observability

### Health Check (Every 10s)
```
GET /health
Response: {"status": "healthy", "service": "CIAF Vault", "version": "1.0.0"}
```

### Vault Statistics
```
GET /stats
Response: Complete vault metrics
```

### Audit Summary
```
GET /audit-summary
Response: Organization audit activity summary
```

---

## 🔓 SOC 2 Readiness Checklist

- ✅ Immutable audit trail (WORM)
- ✅ API authentication (API keys)
- ✅ Access logging (every call logged)
- ✅ Data isolation (multi-tenant)
- ✅ Encryption in transit (HTTPS)
- ✅ Encryption at rest (filesystem encryption)
- ✅ Backup capability (database backups)
- ✅ Incident response (audit trail for forensics)

---

## 💼 Regulatory Compliance Matrix

| Requirement | Status | Implementation |
|-------------|--------|-----------------|
| Data Immutability | ✅ | WORM enforcement |
| Access Control | ✅ | API keys + org isolation |
| Audit Trail | ✅ | Immutable logging |
| Encryption (Transit) | ✅ | HTTPS/TLS |
| Encryption (Rest) | ✅ | SQLite encryption ready |
| Data Retention | ✅ | Policy-configurable |
| Data Deletion  | ✅ | GDPR-compliant |
| Multi-Region | ⏳ | Planned |
| Disaster Recovery | ✅ | Backup strategy |
| Incident Response | ✅ | Audit forensics |

---

## 🤝 Support & Governance

### For Regulators
- Email: regulators@ciaf.io
- Audit requests: audits@ciaf.io
- Technical support: support@ciaf.io

### For Organizations
- Technical documentation: https://vault.ciaf.io/docs
- API reference: https://vault.ciaf.io/api
- Status page: https://status.ciaf.io

---

## 📄 License

Licensed under the Business Source License (BUSL 1.1), converting to Apache 2.0 on January 1, 2029.

**Commercial licenses available.** Contact: licensing@ciaf.io

---

## 🎯 What's Next?

1. **Deploy vault in your environment**
2. **Create organization and API key**
3. **Submit your first proof**
4. **Verify through our API**
5. **Share verification URLs with regulators**

---

**Built with ❤️ by Denzil James Greenwood**

CIAF Vault v1.0.0 | Production Ready | Enterprise Grade
