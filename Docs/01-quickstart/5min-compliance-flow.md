# The 5-Minute Compliance Flow

Generate a cryptographic proof and verify it in under 5 minutes.

## Overview

This guide walks you through the complete CIAF compliance flow:
1. **Log an Event** - Generate an AI inference output
2. **Tag Output** - Create a cryptographic proof with Ed25519 signature
3. **Store Proof** - Write to the vault with WORM (write-once) guarantee
4. **Verify Later** - Retrieve and cryptographically verify the proof

## Step 1: Log an Event

Your AI system produces an inference. In CIAF, this is the "output" we'll prove.

**Example: Medical AI Diagnosis**
```python
inference_output = {
    "patient_id": "P-2026-001",
    "diagnosis": "Type 2 Diabetes Mellitus",
    "confidence": 0.94,
    "model": "medical-classifier-v3",
    "timestamp": "2026-03-15T14:23:45Z"
}
```

CIAF automatically captures:
- **What** was output (the inference)
- **When** it was output (ISO 8601 timestamp)
- **Who** generated it (agent/model/orchestrator)
- **How** it was generated (inference type: agent_orchestrated or direct_model)

## Step 2: Tag the Output

Call the CIAF Verification API to create a proof:

```bash
curl -X POST http://localhost:8000/v1/tags/create \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "output_content": "{\"patient_id\": \"P-2026-001\", \"diagnosis\": \"Type 2 Diabetes\"}",
    "inference_type": "direct_model",
    "model_name": "medical-classifier-v3",
    "organization_id": "healthcare-org-1",
    "tags": ["HIPAA", "PHI", "Clinical Decision"]
  }'
```

**Response:**
```json
{
  "tag_id": "tag-2026-03-15-001",
  "output_content_hash": "sha256:a3f5d...",
  "signature": "ed25519:8f2c...",
  "timestamp": "2026-03-15T14:23:45Z",
  "status": "created"
}
```

What happened:
- ✅ SHA-256 hash of your output computed (tamper detection)
- ✅ Ed25519 digital signature created (non-repudiation)
- ✅ Merkle proof batched with other outputs (scalability)
- ✅ Tag stored in proof store (WORM guarantee)

## Step 3: Store in Vault

For regulated industries, submit to the **AI Evidence Vault (AI-EV)** for third-party custody:

```bash
curl -X POST http://localhost:9000/v1/proofs/submit \
  -H "X-API-Key: your_vault_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tag_id": "tag-2026-03-15-001",
    "proof_data": {
      "signature": "ed25519:8f2c...",
      "merkle_root": "mr:d47e...",
      "timestamp": "2026-03-15T14:23:45Z"
    },
    "organization_id": "healthcare-org-1"
  }'
```

**Response:**
```json
{
  "vault_id": "vault-proof-5847",
  "submission_hash": "sha256:f9e2...",
  "certificate_valid_until": "2027-03-15T00:00:00Z",
  "read_count": 0
}
```

What this means:
- ✅ Proof is now in third-party custody (independent of your system)
- ✅ 365-day certificate of authenticity generated
- ✅ Immutable audit trail created (INSERT-only log)
- ✅ Multi-tenant isolation enforced

## Step 4: Verify Later (Audit)

**24 months later, during a compliance audit...**

Your auditor can verify the original proof without your system running:

```bash
curl -X GET "http://localhost:9000/v1/proofs/verify?vault_id=vault-proof-5847" \
  -H "X-API-Key: your_vault_api_key"
```

**Response:**
```json
{
  "vault_id": "vault-proof-5847",
  "proof_data": {
    "tag_id": "tag-2026-03-15-001",
    "signature": "ed25519:8f2c...",
    "merkle_root": "mr:d47e...",
    "timestamp": "2026-03-15T14:23:45Z"
  },
  "verification_result": {
    "signature_valid": true,
    "timestamp_valid": true,
    "merkle_path_valid": true,
    "overall": "VERIFIED"
  },
  "read_count": 1,
  "certificate_valid": true
}
```

## Summary

| Step | Time | Tool | Outcome |
|------|------|------|---------|
| Log Event | < 1s | Your AI system | Inference captured |
| Tag Output | < 100ms | CIAF API | Proof created |
| Store in Vault | < 500ms | AI-EV API | Third-party custody |
| Verify Later | < 200ms | AI-EV query | Audit-ready evidence |

**Total time to compliance-ready proof: ~2 seconds**

## Next Steps

- [API Authentication](./api-auth.md) - Secure your requests
- [Environment Setup](./environment-setup.md) - Configure your system
- [LCM Philosophy](../02-lcm-deepdive/philosophy.md) - Understand why we defer proof generation
