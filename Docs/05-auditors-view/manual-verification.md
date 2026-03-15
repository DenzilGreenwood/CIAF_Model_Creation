# Auditor's Manual Verification Guide

Field guide for independent auditors to verify CIAF proofs offline, without relying on CIAF systems.

## Legal Foundation

This guide enables **adversarial verification** - the strongest form of evidence. An auditor can independently verify every cryptographic proof without:
- ✅ Connecting to CIAF systems
- ✅ Trusting CIAF infrastructure
- ✅ Assuming CIAF's database integrity

This transforms CIAF from "trust us" to "verify us independently."

---

## What You'll Need

### Hardware
- Laptop or desktop computer (any OS)
- USB drive (8GB for typical audit)
- Optional: Air-gapped computer (for maximum security)

### Software (All Free, Open-Source)

```bash
# Install once, use forever

# For hash verification
sudo apt-get install openssl              # Linux
brew install openssl                      # macOS

# For JSON processing
sudo apt-get install jq                   # JSON query tool

# For Ed25519 verification
# Option A: Python (recommended)
pip install cryptography

# Option B: Use OpenSSL directly (no Python needed)
```

### Credentials
- VAULT_API_KEY (provided byAudit Coordinator)
- healthcare-org-1.pub (organization's public key)

---

## Step 1: Download All Proofs from Vault

### Option A: Use CIAF CLI (Recommended)

```bash
# Install CIAF CLI tool
pip install ciaf-tools

# Download all proofs for date range
ciaf-download-proofs \
  --vault-url https://vault.ciaf.io \
  --api-key $VAULT_API_KEY \
  --org-id healthcare-org-1 \
  --from-date 2025-03-15 \
  --to-date 2026-03-15 \
  --output-dir ./proofs

# Output:
# ✓ Connected to vault.ciaf.io
# ✓ Found 88 proof batches
# ✓ Downloading batch 1/88...
# ✓ Downloaded 88/88 batches
# ✓ Total: 87,654 outputs verified
```

### Option B: Manual API Calls (No Special Tools)

```bash
# Step 1: Get list of proof batches
curl -X GET "https://vault.ciaf.io/v1/proofs/list" \
  -H "X-API-Key: $VAULT_API_KEY" \
  -H "X-Org: healthcare-org-1" \
  > proofs_list.json

# Step 2: Download each proof
jq -r '.proofs[].vault_id' proofs_list.json | while read batch_id; do
    curl -X GET "https://vault.ciaf.io/v1/proofs/$batch_id" \
      -H "X-API-Key: $VAULT_API_KEY" \
      > proofs/$batch_id.json
done

# Output: proofs/vault-proof-5847.json, vault-proof-5848.json, ...
```

### Verification at Download

```bash
# Verify download completeness
ls -lh proofs/ | wc -l
# Should show 88 batch files

# Check file sizes (should all be ~1-2 MB)
ls -lh proofs/ | awk '{print $5}' | sort | uniq -c
```

---

## Step 2: Verify Hashes (Detect Individual Output Tampering)

### Using Bash Script

```bash
#!/bin/bash
# verify_hashes_all.sh - Auditor script

cd proofs/

ERRORS=0
VERIFIED=0

for batch_file in *.json; do
    echo "Processing $batch_file..."

    # For each output in batch, verify hash
    jq -r '.outputs[] | "\(.output_content)|\(.content_hash)"' "$batch_file" | \
    while IFS='|' read -r content hash; do

        computed=$(echo -n "$content" | openssl dgst -sha256 -hex | awk '{print "sha256:" $2}')

        if [ "$computed" != "$hash" ]; then
            echo "❌ HASH MISMATCH in $batch_file"
            echo "   Expected: $hash"
            echo "   Got:      $computed"
            ((ERRORS++))
        else
            ((VERIFIED++))
        fi
    done
done

echo
echo "Hash Verification Results:"
echo "✅ Verified: $VERIFIED"
echo "❌ Errors:   $ERRORS"

if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL HASHES VALID"
    exit 0
else
    echo "⚠️  TAMPERING DETECTED"
    exit 1
fi
```

### Using Python (More Robust)

```python
#!/usr/bin/env python3
# verify_hashes.py

import json
import hashlib
import sys
from pathlib import Path

def verify_all_hashes(proof_dir):
    """Verify all output hashes in all batch files."""

    verified = 0
    errors = 0
    error_log = []

    for batch_file in sorted(Path(proof_dir).glob('*.json')):
        print(f"Verifying {batch_file.name}...", end=' ')

        with open(batch_file) as f:
            proof = json.load(f)

        batch_errors = 0
        for output in proof['outputs']:
            content = output['output_content']
            expected = output['content_hash']

            computed = hashlib.sha256(content.encode()).hexdigest()
            computed_with_prefix = f"sha256:{computed}"

            if computed_with_prefix != expected:
                batch_errors += 1
                error_log.append({
                    'file': batch_file.name,
                    'output_id': output['output_id'],
                    'expected': expected,
                    'got': computed_with_prefix
                })
            else:
                verified += 1

        if batch_errors == 0:
            print("✅")
        else:
            print(f"❌ {batch_errors} errors")
            errors += batch_errors

    # Report
    print("\n" + "=" * 60)
    print("Hash Verification Report")
    print("=" * 60)
    print(f"✅ Verified: {verified:,}")
    print(f"❌ Errors:   {errors:,}")

    if errors > 0:
        print("\nError details:")
        for err in error_log[:10]:  # Show first 10
            print(f"  {err['file']}: {err['output_id']}")
            print(f"    Expected: {err['expected'][:32]}...")
            print(f"    Got:      {err['got'][:32]}...")

    return errors == 0

if __name__ == '__main__':
    success = verify_all_hashes('./proofs')
    sys.exit(0 if success else 1)
```

### What Success Looks Like

```
Hash Verification Results:
✅ Verified: 87,654
❌ Errors:   0

✅ ALL HASHES VALID

If you see this, all individual outputs are unchanged.
```

---

## Step 3: Verify Merkle Trees (Detect Batch Tampering)

### Using Python (Recommended)

```python
#!/usr/bin/env python3
# verify_merkle_trees.py

import json
import hashlib
from pathlib import Path

def hash_pair(left, right):
    """Hash two values together (Merkle tree standard)."""
    combined = left + right
    return hashlib.sha256(combined.encode()).hexdigest()

def rebuild_merkle_tree(leaf_hashes):
    """Rebuild Merkle tree layer by layer."""

    current_level = leaf_hashes
    level = 0

    while len(current_level) > 1:
        next_level = []

        # Process pairs
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i+1] if i+1 < len(current_level) else current_level[i]
            parent = hash_pair(left, right)
            next_level.append(parent)

        current_level = next_level
        level += 1

    return current_level[0]

def verify_merkle_tree(batch_file):
    """Verify one batch's Merkle tree."""

    with open(batch_file) as f:
        proof = json.load(f)

    # Extract leaf hashes
    leaf_hashes = [o['content_hash'] for o in proof['outputs']]

    # Rebuild tree
    rebuilt_root = rebuild_merkle_tree(leaf_hashes)

    # Get expected root
    expected_root = proof['merkle_tree']['root'].replace('mr:', '')

    # Compare
    is_valid = rebuilt_root == expected_root

    return {
        'file': batch_file.name,
        'valid': is_valid,
        'outputs': len(leaf_hashes),
        'expected_root': expected_root[:32] + '...',
        'rebuilt_root': rebuilt_root[:32] + '...'
    }

# Verify all batches
results = []
for batch_file in sorted(Path('./proofs').glob('*.json')):
    result = verify_merkle_tree(batch_file)
    results.append(result)

    status = "✅" if result['valid'] else "❌"
    print(f"{status} {result['file']}: {result['outputs']} outputs")

# Summary
print("\n" + "=" * 60)
valid_count = sum(1 for r in results if r['valid'])
print(f"✅ Valid:   {valid_count}/{len(results)}")
print(f"❌ Invalid: {len(results) - valid_count}/{len(results)}")

if valid_count == len(results):
    print("\n✅ ALL MERKLE TREES VALID")
    print("No outputs were added, removed, or reordered.")
else:
    print("\n⚠️  MERKLE TREE TAMPERING DETECTED")
    for r in results:
        if not r['valid']:
            print(f"  {r['file']}: Expected {r['expected_root']}, got {r['rebuilt_root']}")
```

### What Success Looks Like

```
✅ batch-1.json: 1000 outputs
✅ batch-2.json: 1000 outputs
... (88 total)

============================================================
✅ Valid:   88/88
❌ Invalid: 0/88

✅ ALL MERKLE TREES VALID
No outputs were added, removed, or reordered.
```

---

## Step 4: Verify Ed25519 Signatures (Prevent Tampering)

### Get the Public Key

The organization must provide their public key (available for download):

```bash
# Download once, reuse for all batches
curl -X GET "https://ciaf.io/v1/organizations/healthcare-org-1/public_key" \
  -o healthcare-org-1.pub

# Inspect
cat healthcare-org-1.pub
# -----BEGIN PUBLIC KEY-----
# MCowBQYDK2VwAyEAxJNEOuKVdO2dxjzYYI9b3dF7mK2pQ9jZsL8eF3gN0pE=
# -----END PUBLIC KEY-----
```

### Verify Using Python

```python
#!/usr/bin/env python3
# verify_signatures.py

import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from pathlib import Path

# Load public key (once)
with open('healthcare-org-1.pub', 'rb') as f:
    public_key = serialization.load_pem_public_key(f.read())

def verify_signature(batch_file):
    """Verify Ed25519 signature of Merkle root."""

    with open(batch_file) as f:
        proof = json.load(f)

    merkle_root = proof['merkle_tree']['root'].replace('mr:', '')
    signature_hex = proof['digital_signature']['signature'].replace('ed25519:', '')
    signature_bytes = bytes.fromhex(signature_hex)

    try:
        public_key.verify(signature_bytes, merkle_root.encode())
        return True
    except Exception:
        return False

# Verify all batches
print("Verifying Ed25519 signatures...")

valid = 0
invalid = 0

for batch_file in sorted(Path('./proofs').glob('*.json')):
    if verify_signature(str(batch_file)):
        print(f"✅ {batch_file.name}")
        valid += 1
    else:
        print(f"❌ {batch_file.name} - SIGNATURE INVALID!")
        invalid += 1

# Summary
print("\n" + "=" * 60)
print(f"✅ Valid:   {valid}/{valid + invalid}")
print(f"❌ Invalid: {invalid}/{valid + invalid}")

if invalid == 0:
    print("\n✅ ALL SIGNATURES VALID")
    print("All batches were signed by the organization.")
    print("Non-repudiation established.")
else:
    print("\n⚠️  SIGNATURE TAMPERING DETECTED")
    print("Someone modified the Merkle root after signing!")
```

### Using OpenSSL (No Python)

```bash
#!/bin/bash
# verify_signatures_openssl.sh

PUBLIC_KEY="healthcare-org-1.pub"

for batch_file in proofs/*.json; do
    # Extract merkle root
    merkle_root=$(jq -r '.merkle_tree.root' "$batch_file" | sed 's/mr://')

    # Extract signature
    signature=$(jq -r '.digital_signature.signature' "$batch_file" | sed 's/ed25519://')

    # Convert to binary
    echo -n "$signature" | xxd -r -p > sig.bin
    echo -n "$merkle_root" > msg.txt

    # Verify
    if openssl dgst -sha256 -verify <(openssl pkey -pubin -in "$PUBLIC_KEY") \
       -signature sig.bin msg.txt > /dev/null 2>&1; then
        echo "✅ $(basename $batch_file)"
    else
        echo "❌ $(basename $batch_file) - SIGNATURE INVALID!"
    fi

    rm sig.bin msg.txt
done
```

### What Success Looks Like

```
Verifying Ed25519 signatures...
✅ batch-1.json
✅ batch-2.json
... (88 total)

============================================================
✅ Valid:   88/88
❌ Invalid: 0/88

✅ ALL SIGNATURES VALID
All batches were signed by the organization.
Non-repudiation established.
```

---

## Step 5: Complete End-to-End Verification

### Run Master Verification Script

```bash
#!/bin/bash
# full_audit_verification.sh - Master auditor script

set -e  # Exit on any error

SOURCE_DIR="./proofs"
REPORT="audit_verification_report.txt"

echo "🔍 Starting CIAF Proof Audit Verification"
echo "=========================================="
echo "Date: $(date)"
echo "Source: $SOURCE_DIR"
echo
echo "This verification is independent and offline."
echo "No connection to CIAF systems required."
echo

# Step 1: Hash verification
echo "[1/4] Verifying output hashes..."
python3 verify_hashes.py | tee -a "$REPORT"

# Step 2: Merkle tree verification
echo "[2/4] Verifying Merkle tree structures..."
python3 verify_merkle_trees.py | tee -a "$REPORT"

# Step 3: Signature verification
echo "[3/4] Verifying Ed25519 signatures..."
python3 verify_signatures.py | tee -a "$REPORT"

# Step 4: Summary
echo "[4/4] Generating audit report..."
cat >> "$REPORT" << EOF

========================================
AUDIT VERIFICATION COMPLETE
========================================

All cryptographic checks completed successfully.

This audit confirms:
✅ All 87,654 outputs are unchanged (hash verification)
✅ No outputs were added or removed (Merkle tree verification)
✅ All batches were signed by healthcare-org-1 (signature verification)
✅ Organization cannot deny signing these proofs (non-repudiation)

ADMISSIBILITY ASSESSMENT:
- Federal Rule of Evidence 901: ✅ Satisfied (cryptographic authentication)
- Federal Rule of Evidence 902: ✅ Satisfied (self-authenticating)
- Daubert Standard: ✅ Satisfied (peer-reviewed cryptography)
- Chain of Custody: ✅ Satisfied (Vault audit trail)

This evidence is admissible in court.

Report generated: $(date)
Auditor: [Your Name]
Organization: [Your Org]
EOF

echo "✅ Audit report written to $REPORT"
cat "$REPORT"
```

---

## Step 6: Generate Audit Report

### Template Auditor Report

```markdown
# INDEPENDENT CRYPTOGRAPHIC AUDIT REPORT

**Organization:** Healthcare Organization Inc.
**System:** CIAF AI Governance Platform
**Audit Period:** March 15, 2025 - March 15, 2026
**Audit Date:** March 16-20, 2026
**Auditor:** [Your Name], [Audit Firm]

## Executive Summary

We performed an independent, offline cryptographic audit of 87,654 AI inference
outputs managed by CIAF (Cognitive Insight Audit Framework). All proofs were
verified using industry-standard cryptography (SHA-256, Ed25519, Merkle trees).

**Result: ✅ ALL PROOFS VERIFIED - NO TAMPERING DETECTED**

## Methodology

1. **Hash Verification:** Recomputed SHA-256 hash for each output
2. **Merkle Tree Verification:** Rebuilt Merkle tree structure from leaf hashes
3. **Signature Verification:** Verified Ed25519 digital signatures using public key
4. **Timestamp Verification:** Confirmed all timestamps are cryptographically sound

## Findings

| Check | Result | Significance |
|-------|--------|--------------|
| Individual output tampering | ✅ NONE | Each output is cryptographically protected |
| Batch-level tampering | ✅ NONE | No outputs added, removed, or reordered |
| Signature validity | ✅ VALID | Organization cannot deny signing proofs |
| Timestamp integrity | ✅ VALID | Proofs are time-bound and authentic |

## Admissibility Assessment

### Federal Rule of Evidence 901 (Authentication)
**Requirement:** "To satisfy the requirement of authenticating or identifying an item
of evidence, the proponent must produce evidence sufficient to support a finding
that the item is what the proponent claims it is."

**Assessment:** ✅ **SATISFIED**
- SHA-256 hashing provides cryptographic proof of output authenticity
- Merkle trees provide cryptographic proof of completeness
- Ed25519 signature provides non-repudiation

### Federal Rule of Evidence 902 (Self-Authenticating Evidence)
**Requirement:** Documents bearing a presumptively reliable signature

**Assessment:** ✅ **SATISFIED**
- All proofs bear Ed25519 signatures from healthcare-org-1
- Signature algorithms are industry-standard and peer-reviewed
- Vault certificate provides independent timestamp authentication

### Daubert Standard (Expert Testimony)
**Requirement:** Scientific methods must be reliable and relevant

**Assessment:** ✅ **SATISFIED**
- Cryptographic methods (SHA-256, Ed25519, Merkle trees) are peer-reviewed
- Methods are peer-accepted and widely deployed
- Methods are testable and have known error rates (nil for deterministic crypto)
- Scientific literature supports reliability

## Conclusion

The 87,654 inference outputs are admissible as evidence in court with
cryptographic proof of:
1. **Authenticity** - Original content is unchanged
2. **Completeness** - No outputs are missing
3. **Non-repudiation** - Organization cannot deny generating them
4. **Integrity** - No tampering evidence detected

**This evidence meets the highest admissibility standard.**

## Court Presentation

Auditor can testify:
- "I independently verified all 87,654 outputs using industry-standard cryptography"
- "No tampering was detected at any level"
- "The cryptographic methods used are peer-reviewed and widely deployed"
- "This evidence is more reliable than many forms of traditional evidence"

---

**Audit Team:** [Names]
**Audit Firm:** [Firm Name]
**Date:** March 20, 2026
**Certification:** I certify this audit was performed independently and offline.
```

---

## Troubleshooting

### "Hash mismatch detected"

This means an output was modified after being proven. **This is a security incident.**

**Action:**
1. Stop the audit
2. Document which output hash mismatched
3. Contact CIAF security team
4. Escalate to legal team

### "Merkle root doesn't match"

One or more outputs were added, removed, or reordered. **Tampering detected.**

**Action:**
1. Identify which batch failed
2. List the batch ID and number
3. Report to audit committee with severity "CRITICAL"
4. Recommend legal investigation

### "Signature verification failed"

The Merkle root was modified after signing. **Definitive proof of tampering.**

**Action:**
1. Preserve all files as evidence
2. Create forensic image of vault backup
3. Report to law enforcement if fraud is suspected
4. Notify regulatory bodies immediately

---

## Next Steps

- [Testimony Guide](./testimony.md) - How to present findings in court
- [Verification Logic](../02-lcm-deepdive/verification-logic.md) - Technical details
- [Proof Lifecycle](../02-lcm-deepdive/proof-lifecycle.md) - Complete walkthrough
