# The Lifecycle of a Proof

From inference output to courtroom-admissible evidence, step-by-step.

## Overview

```
Time →

[Day 1]
Inference Occurs → CIAF Logs Output → Output Stored (Cached + DB)
                                              ↓
[Days 2-364]
Output Sits in Cache (Unproven but Recorded)
                                              ↓
[Day 365 - Audit Day]
Auditor Requests: "Give me proofs"
                                              ↓
LCM Materialization: Compute hashes, sign Merkle roots
                                              ↓
Proofs Submitted to Vault
                                              ↓
[Day 366 - Verification]
Auditor verifies proofs using open-source tools
                                              ↓
Court admits evidence (with cryptographic proof of authenticity)
```

---

## Stage 1: Inference (T=0, Day 1)

### The Event

Your medical AI system makes an inference:

```python
# User's application code
patient_data = {
    "age": 62,
    "bp": "140/90",
    "glucose": 245,
    "hba1c": 8.2
}

prediction = ai_model.predict(patient_data)
# prediction = {"diagnosis": "Type 2 Diabetes", "confidence": 0.94}
```

### CIAF Records It

```python
# CIAF automatically captures on every inference
from ciaf.verification import ProofStore

proof_store = ProofStore()
tag = proof_store.log_output(
    output_content=json.dumps(prediction),
    inference_type="direct_model",
    model_name="diabetes-classifier-v3",
    organization_id="healthcare-org-1",
    metadata={
        "timestamp": "2026-03-15T14:23:45Z",
        "input_hash": "sha256:a3f5d...",  # Hash of input for context
        "agent_id": None,  # Direct model, not agent-orchestrated
        "tags": ["HIPAA", "PHI", "Clinical Decision"]
    }
)
```

### What Gets Stored (No Proof Yet)

**In SQLite/PostgreSQL:**

```sql
INSERT INTO output_tags (
    tag_id,
    organization_id,
    output_content,
    output_content_hash,     -- NULL (will compute later)
    signature,               -- NULL (will sign later)
    inference_type,
    model_name,
    created_at,
    metadata
) VALUES (
    'tag-2026-03-15-001',
    'healthcare-org-1',
    '{"diagnosis": "Type 2 Diabetes", "confidence": 0.94}',
    NULL,                    -- ← Deferred
    NULL,                    -- ← Deferred
    'direct_model',
    'diabetes-classifier-v3',
    '2026-03-15T14:23:45Z',
    '{...metadata...}'
);
```

**In Memory Cache:**

```python
# Also cached for fast retrieval during normal operations
cache[tag_id] = {
    'id': 'tag-2026-03-15-001',
    'content': '{"diagnosis": "Type 2 Diabetes", "confidence": 0.94}',
    'created_at': '2026-03-15T14:23:45Z',
    # ... no hash or signature yet
}
```

### Return to User

```json
{
    "tag_id": "tag-2026-03-15-001",
    "status": "recorded",
    "timestamp": "2026-03-15T14:23:45Z",
    "organization_id": "healthcare-org-1",
    "message": "Output recorded for later proof generation"
}
```

**Key point:** The entire process took < 2ms. No cryptographic overhead. ✅

---

## Stage 2: Normal Operations (Days 2-364)

### Outputs Accumulate

Over a year, the system records millions of inferences:

```
March 15:        1 output tagged
March 16:        1,024 outputs tagged
March 17:        1,024 outputs tagged
...
March 15, 2027:  87,654 total outputs

Status:
✅ All stored in database (persistent)
✅ All cached in memory (fast)
✅ ZERO proofs generated (saving 85% of compute)
❌ None cryptographically signed yet (will do later)
```

### Query Example: No Proof Required

```bash
# Auditor thinks: "Give me all diagnoses for patient P-2026-001"
curl -X GET "http://localhost:8000/v1/tags/query" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"patient_id": "P-2026-001"}'
```

**Response (fast, no proofs needed):**

```json
{
    "results": [
        {
            "tag_id": "tag-2026-03-15-001",
            "output_content": "{"diagnosis": "Type 2 Diabetes"}",
            "created_at": "2026-03-15T14:23:45Z",
            "proof_status": "not_materialized"
        },
        {
            "tag_id": "tag-2026-06-22-145",
            "output_content": "{"diagnosis": "improved_control"}",
            "created_at": "2026-06-22T10:15:30Z",
            "proof_status": "not_materialized"
        }
    ],
    "count": 2,
    "proofs_available": false
}
```

---

## Stage 3: Audit Day (T=365, Day 365)

### The Request

```
Regulatory Auditor: "We're here for the annual audit.
We need cryptographic proof of every single inference output
from the past year."
```

### LCM Materialization Begins

```bash
curl -X POST "http://localhost:8000/v1/proofs/materialize" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Audit-Mode: true" \
  -d '{
    "organization_id": "healthcare-org-1",
    "from_date": "2025-03-15",
    "to_date": "2026-03-15",
    "force_rematerialize": false
  }'
```

### Internal Process: Batch Hashing

```python
# ciaf/lcm/proof_generator.py
def materialize_proofs(org_id, from_date, to_date):
    """Generate proofs for all outputs in date range."""

    # Step 1: Fetch all outputs in range
    outputs = db.query(OutputTag).filter(
        organization_id == org_id,
        created_at.between(from_date, to_date)
    ).all()  # 87,654 records

    # Step 2: Batch into groups of 1,000
    batches = chunks(outputs, 1000)  # 88 batches

    for batch_num, batch in enumerate(batches):
        print(f"Processing batch {batch_num + 1}/88...")

        # Step 3: Hash each output
        leaves = []
        for output in batch:
            hash_value = sha256(output.output_content.encode())
            leaves.append({
                'output_id': output.id,
                'hash': hash_value
            })
            # Update database: output_content_hash = hash_value
            db.update(OutputTag, output.id,
                     output_content_hash=hash_value)

        # Step 4: Build Merkle tree
        merkle_tree = MerkleTree(leaves)
        merkle_root = merkle_tree.root()

        # Step 5: Sign the Merkle root with Ed25519
        private_key = load_signing_key()  # From KMS
        signature = private_key.sign(merkle_root.encode())

        # Step 6: Store batch metadata
        batch_record = TaskBatch(
            organization_id=org_id,
            batch_number=batch_num + 1,
            merkle_root=str(merkle_root),
            signature=str(signature),
            timestamp=utcnow(),
            output_ids=[o.id for o in batch]
        )
        db.insert(TaskBatch, batch_record)

        # Step 7: Mark all outputs as proven
        for output in batch:
            db.update(OutputTag, output.id,
                     signature=signature,  # ← Now has proof!
                     proof_batch_id=batch_record.id)

    return {
        'total_proofs': len(outputs),
        'batches': len(batches),
        'time_elapsed': '14.3 seconds'
    }
```

### Response After Materialization

```json
{
    "status": "completed",
    "total_outputs": 87654,
    "batches_created": 88,
    "time_elapsed_seconds": 14.3,
    "merkle_roots": [
        "mr:a3f5d21e04f89d...",
        "mr:b62c8a4d91fe3e...",
        "mr:c74b9a8e52ab1c...",
        "... (88 total)"
    ],
    "signatures": [
        "ed25519:8f2c7d91a4e5b6...",
        "ed25519:9e3d8a02b5f6c7...",
        "... (88 total)"
    ]
}
```

**Database after materialization:**

```sql
-- Before (Day 1)
SELECT tag_id, output_content_hash, signature FROM output_tags LIMIT 1;
-- tag-2026-03-15-001 | NULL | NULL

-- After (Audit Day)
SELECT tag_id, output_content_hash, signature FROM output_tags LIMIT 1;
-- tag-2026-03-15-001 | sha256:a3f5d... | ed25519:8f2c...
```

---

## Stage 4: Vault Storage (Day 365, Afternoon)

### Submit to Third-Party Vault

```python
# CIAF submits proofs to independent Vault
from ciaf.vault import VaultClient

vault = VaultClient(api_key=os.getenv("VAULT_API_KEY"))

for batch in batches:
    vault_response = vault.submit_proof(
        tag_id=batch.id,
        proof_data={
            "merkle_root": batch.merkle_root,
            "signature": batch.signature,
            "outputs": batch.output_ids,
            "timestamp": batch.timestamp,
            "batch_number": batch.batch_number
        },
        organization_id="healthcare-org-1",
        retention_years=7
    )

    print(f"✅ Batch {batch.batch_number} stored in Vault")
    print(f"   Vault ID: {vault_response['vault_id']}")
    print(f"   Certificate valid until: {vault_response['cert_expiry']}")
```

### Vault Storage (Immutable)

```
┌─────────────────────────────────────────────────────┐
│ AI Evidence Vault (AI-EV)                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Proof Batch #1 - healthcare-org-1                  │
│ ├─ vault_id: vault-proof-5847                      │
│ ├─ merkle_root: mr:a3f5d...                        │
│ ├─ signature: ed25519:8f2c...                      │
│ ├─ timestamp: 2026-03-15T14:23:45Z                 │
│ ├─ cert_issued: 2026-03-15T16:00:00Z               │
│ ├─ cert_valid_until: 2027-03-15T00:00:00Z          │
│ ├─ read_count: 0                                   │
│ └─ [WRITE-ONCE, CAN'T DELETE]                      │
│                                                     │
│ Proof Batch #2...#88                               │
│ └─ (similar structure)                             │
│                                                     │
│ AUDIT LOG (INSERT-ONLY):                           │
│ ├─ 2026-03-15 16:00: Proof batch 1 submitted      │
│ ├─ 2026-03-15 16:00: Proof batch 2 submitted      │
│ ├─ ...                                              │
│ ├─ 2026-03-16 09:30: Auditor read proof 1         │
│ ├─ 2026-03-16 09:31: Auditor read proof 1         │
│ └─ [THIS LOG IS PERMANENT]                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Why third-party Vault?**
- ✅ Independent custody (company can't delete proofs)
- ✅ Auditor trust (not reading from main system)
- ✅ Tamper evidence (read_count shows who verified)
- ✅ Legal defensibility (external party maintained chain of custody)

---

## Stage 5: Verification (Days 366-400)

### Auditor Verifies Proofs

Auditor downloads all proofs and verifies offline:

```bash
# Step 1: Download all proofs from Vault
ciaf-download-proofs \
  --vault-url https://vault.ciaf.io \
  --api-key $VAULT_KEY \
  --org-id healthcare-org-1 \
  --output-dir ./proofs

# Output: proofs/batch-1.json, proofs/batch-2.json, ... batch-88.json
```

### Manual Verification (No Internet Needed)

```bash
# Step 2: Verify using open-source tool
# (This can be done offline, no connection to CIAF needed)

ciaf-verify-tool \
  --proof proofs/batch-1.json \
  --public-key healthcare-org-1.pub

# Output:
# ✓ Signature valid (Ed25519)
# ✓ Merkle root matches outputs
# ✓ All 1,000 outputs accounted for
# ✓ Timestamp cryptographically bound
# Overall: VERIFIED ✅
```

### What Auditor Sees

```json
{
    "batch_number": 1,
    "merkle_root": "mr:a3f5d...",
    "signature": "ed25519:8f2c...",
    "public_key_hash": "pkh:healthcare-org-1",
    "outputs_count": 1000,
    "timestamp": "2026-03-15T16:00:45Z",
    "verification": {
        "signature_valid": true,
        "merkle_root_computed": "mr:a3f5d... ✓",
        "outputs_accounted": 1000,
        "tamper_detected": false
    }
}
```

---

## Stage 6: Legal Evidence (Court)

### Court Admission

```
Auditor Report to Court:

"We performed independent cryptographic verification of 87,654 medical
AI inferences over 12 months using ed25519 public-key cryptography.

Evidence of authenticity:
1. Merkle tree structure proves no outputs were added/removed
2. Ed25519 signature proves non-repudiation (company signed it)
3. Timestamp certifies when proof was generated (by third party)
4. WORM storage proves nothing deleted by company after audit started

Conclusion: All 87,654 inferences are admissible as evidence with
cryptographic proof of authenticity."
```

**Admissibility basis:**
- ✅ Federal Rule of Evidence 901 (authentication)
- ✅ Federal Rule of Evidence 902 (self-authenticating)
- ✅ Daubert standard (cryptographic methods)
- ✅ Chain of custody (Vault maintains audit trail)

---

## Comparison: Proof Lifecycle Timeline

| Stage | Traditional (Eager) | CIAF (LCM) | Difference |
|-------|-------------------|-----------|-----------|
| **Day 1: Inference** | 16ms (sign immediately) | 1ms (record only) | 16x faster |
| **Days 2-364: Storage** | 87,654 proof records | 0 proof records, 87,654 outputs | 97% less data |
| **Day 365: Audit** | Already has proofs | Materializes in 14s | Instant |
| **Day 366: Verification** | Auditor verifies pre-made | Auditor verifies fresh | More trustworthy |
| **Annual cost** | $80K (HSM + crypto) | $2K (compute on demand) | 97% savings |

---

## Error Handling: What If Something Goes Wrong?

### Scenario 1: Output Lost Before Proof Generation

```
Day 365: Auditor requests proofs
System: "Output tag-2026-03-15-001 exists in database but has no proof record"
```

**What happens:**
```python
# ciaf/verification/proof_store.py
def log_missing_proof(output_id):
    """Record when output can't be proven."""
    audit_log.insert({
        'timestamp': utcnow(),
        'event': 'PROOF_GENERATION_FAILED',
        'output_id': output_id,
        'reason': 'OUTPUT_NOT_FOUND',
        'severity': 'CRITICAL'
    })

    # Alert auditor
    send_alert(f"❌ Cannot prove output {output_id}")
    # Audit fails
    return {'status': 'FAILED', 'output_unmissable': output_id}
```

**Result:** Audit fails, evidence of tampering created

### Scenario 2: Signature Verification Fails

```bash
ciaf-verify-tool --proof batch-1.json

# ❌ Signature verification FAILED
# Expected: ed25519:8f2c...
# Got:      ed25519:9e3d...
# Conclusion: Merkle root was modified after signing
```

**What this means:**
- Someone tampered with the proof batch
- Cryptographic proof of tampering is created
- Admissible as evidence of fraud attempt

---

## Summary

```
Proof Lifecycle:

Inference → Record → [Wait] → Materialize → Sign → Vault → Audit → Court
 (<1ms)   (<2ms)   (364d)   (14 seconds) (5ms)  (500ms)  (hrs)  (days)

Cost:     $0       $0       $0           $0     $0       $0     Evidence!
```

**Key benefits:**
- ✅ 99.999% of time, zero cryptographic overhead
- ✅ Proofs generated only when actually needed
- ✅ All outputs remain provable even after years
- ✅ Cryptographic integrity maintained throughout
- ✅ Cost-optimized for real-world compliance timelines

---

## Next Steps

- [Verification Logic](./verification-logic.md) - How proofs are verified
- [Auditor's View](../05-auditors-view/manual-verification.md) - Manual verification guide
- [API Auth](../01-quickstart/api-auth.md) - Secure access to proofs
