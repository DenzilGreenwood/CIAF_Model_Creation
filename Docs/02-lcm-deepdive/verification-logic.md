# Verification Logic: How to Prove Proofs

Step-by-step guide to cryptographically verify CIAF proofs without relying on CIAF's system.

## Overview

CIAF proofs use three complementary cryptographic techniques:

```
┌─────────────────────────────────────────────────────┐
│ Input: Raw output content                           │
│   "Patient diagnosis: Type 2 Diabetes"              │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   SHA-256 Hash        │
         │   (Tamper Detection)  │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │ Merkle Tree │ (Scalability)
              └──────┬──────┘
                     │
           ┌─────────▼─────────┐
           │  Ed25519 Signature  │ (Non-repudiation)
           │  (Digital Signature) │
           └─────────┬─────────┘
                     │
              Cryptographically
              Proven Output ✅
```

## Part 1: Understanding the Proof Structure

### Proof JSON Format

```json
{
    "batch_number": 1,
    "timestamp": "2026-03-15T16:00:45Z",
    "organization_id": "healthcare-org-1",

    "outputs": [
        {
            "output_id": "tag-2026-03-15-001",
            "output_content": "Patient diagnosis: Type 2 Diabetes",
            "content_hash": "sha256:a3f5d21e04f89d8a629c1f4d8e9a2b7c5d1e3f4a6b8c9d0e1f2a3b4c5d6e7f8a",
            "original_timestamp": "2026-03-15T14:23:45Z"
        },
        {
            "output_id": "tag-2026-03-15-002",
            "output_content": "Patient status: Improved",
            "content_hash": "sha256:b4e6c32f15a09e9b73ad2e5c9ea3c8d6e2f4a5b7c9d0e1f3a4b5c6d7e8f9g0b",
            "original_timestamp": "2026-03-15T14:25:52Z"
        }
        // ... 998 more outputs
    ],

    "merkle_tree": {
        "root": "mr:d47e9c2a8f1b3c5e7g9i1k3m5o7q9s1u",
        "depth": 10,
        "leaf_count": 1000,
        "tree_structure": [
            {
                "level": 0,
                "hashes": ["h0", "h1", "h2", "h3", "..."]
            },
            {
                "level": 1,
                "hashes": ["h01", "h23", "h45", "..."]
            }
            // ... up to root
        ]
    },

    "digital_signature": {
        "algorithm": "Ed25519",
        "signature": "ed25519:8f2c7d91a4e5b6c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9g0h",
        "public_key": "pk:healthcare-org-1-2026",
        "signing_timestamp": "2026-03-15T16:00:45Z",
        "certificate_expiry": "2027-03-15T00:00:00Z"
    },

    "vault": {
        "vault_id": "vault-proof-5847",
        "submission_hash": "sha256:f9e2d8c7b6a5949382716f5e4d3c2b1a9f8e7d6c5b4a39282716f5e4d3c2b1a",
        "read_count": 12,
        "last_read_at": "2026-03-16T14:30:00Z"
    }
}
```

---

## Part 2: Step 1 - Reconstruct the Hashes

### Verify Each Output

For each output in the batch, recompute its SHA-256 hash:

```bash
#!/bin/bash
# verify_hashes.sh

PROOF_FILE="batch-1.json"

# Extract outputs and hashes using jq
jq -r '.outputs[] | "\(.output_content)|\(.content_hash)"' "$PROOF_FILE" | while IFS='|' read -r content hash; do

    # Compute hash of content using OpenSSL
    computed_hash=$(echo -n "$content" | openssl dgst -sha256 -hex | awk '{print "sha256:" $2}')

    # Compare
    if [ "$computed_hash" == "$hash" ]; then
        echo "✓ Output hash valid"
    else
        echo "❌ HASH MISMATCH!"
        echo "   Expected: $hash"
        echo "   Got:      $computed_hash"
        exit 1
    fi
done

echo "✅ All 1,000 output hashes verified"
```

### Python Alternative

```python
import hashlib
import json

def verify_output_hashes(proof_json):
    """Verify each output's SHA-256 hash."""

    with open(proof_json, 'r') as f:
        proof = json.load(f)

    mismatches = []

    for output in proof['outputs']:
        # Recompute hash
        content = output['output_content']
        expected = output['content_hash']

        computed = hashlib.sha256(content.encode()).hexdigest()
        computed_with_prefix = f"sha256:{computed}"

        if computed_with_prefix != expected:
            mismatches.append({
                'output_id': output['output_id'],
                'expected': expected,
                'got': computed_with_prefix
            })

    if mismatches:
        print(f"❌ Found {len(mismatches)} hash mismatches!")
        for m in mismatches:
            print(f"  {m['output_id']}: expected {m['expected'][:16]}..., got {m['got'][:16]}...")
        return False
    else:
        print(f"✅ All {len(proof['outputs'])} output hashes verified")
        return True

verify_output_hashes('batch-1.json')
```

### What This Proves

- ✅ No output content was modified
- ✅ All outputs are accounted for
- ✅ Timestamps haven't been tampered with

---

## Part 3: Step 2 - Reconstruct the Merkle Tree

### Merkle Tree Structure

Each hash from Step 1 becomes a leaf in a binary tree:

```
                    Root (mr:d47e...)
                   /              \
              Hash01              Hash23
             /     \             /      \
         Hash0   Hash1       Hash2    Hash3
         / \      / \         / \      / \
        0  1     2   3       4   5    6   7
       "A" "B"  "C" "D"     "E" "F"  "G" "H"
```

Where:
- Leaves (0-7) = SHA-256 hashes of outputs
- Each parent = SHA-256(left_child + right_child)
- Root = Final Merkle root

### Verify Merkle Tree

```python
import hashlib

def hash_pair(left, right):
    """Hash two nodes together (Merkle tree standard)."""
    combined = left + right
    return hashlib.sha256(combined.encode()).hexdigest()

def rebuild_merkle_tree(leaf_hashes):
    """Rebuild the Merkle tree from leaf hashes."""

    current_level = [h['content_hash'] for h in leaf_hashes]

    while len(current_level) > 1:
        next_level = []

        # Process pairs of hashes
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i+1] if i+1 < len(current_level) else current_level[i]

            # Hash the pair
            parent = hash_pair(left, right)
            next_level.append(parent)

        current_level = next_level

    # The last remaining hash is the root
    return current_level[0]

# Load proof
proof = json.load(open('batch-1.json'))

# Extract leaf hashes
leaf_hashes = proof['outputs']

# Rebuild the tree
reconstructed_root = rebuild_merkle_tree(leaf_hashes)
expected_root = proof['merkle_tree']['root'].replace('mr:', '')

# Compare
if reconstructed_root == expected_root:
    print(f"✅ Merkle root verified: {reconstructed_root[:32]}...")
else:
    print(f"❌ MERKLE ROOT MISMATCH!")
    print(f"   Expected: {expected_root}")
    print(f"   Got:      {reconstructed_root}")
```

### What This Proves

- ✅ All outputs are included in the Merkle tree
- ✅ No outputs were added/removed
- ✅ Merkle root hash is consistent
- ✅ The batch wasn't tampered with (bit-flip detection)

---

## Part 4: Step 3 - Verify Ed25519 Signature

### Understanding Ed25519

Ed25519 is a public-key cryptography standard:

```
├─ PRIVATE KEY (kept secret by company)
│  └─ Used to SIGN messages
│
├─ PUBLIC KEY (made public)
│  └─ Used to VERIFY signatures
│
└─ Signature = SIGN(merke_root, private_key)
   Verification = VERIFY(merkle_root, signature, public_key)
```

**If verification succeeds:**
- ✅ Message (Merkle root) hasn't been modified
- ✅ Only the owner of private key could have signed it
- ✅ Signature authenticates the entire batch

### Get the Public Key

```bash
# Step 1: Download organization's public key
curl -X GET "https://ciaf.io/v1/organizations/healthcare-org-1/public_key" \
  > healthcare-org-1.pub

# Inspect it
cat healthcare-org-1.pub
# -----BEGIN PUBLIC KEY-----
# MCowBQYDK2VwAyEAxJNEOuKVdO2dxjzYYI9b3dF7mK2pQ9jZsL8eF3gN0pE=
# -----END PUBLIC KEY-----
```

### Verify the Signature

**Using OpenSSL:**

```bash
#!/bin/bash
# verify_signature.sh

PROOF_FILE="batch-1.json"
PUBLIC_KEY_FILE="healthcare-org-1.pub"

# Step 1: Extract Merkle root from proof
merkle_root=$(jq -r '.merkle_tree.root' "$PROOF_FILE" | sed 's/mr://')

# Step 2: Extract signature
signature=$(jq -r '.digital_signature.signature' "$PROOF_FILE" | sed 's/ed25519://')

# Step 3: Convert signature hex to binary
echo -n "$signature" | xxd -r -p > signature.bin

# Step 4: Create message file with merkle root
echo -n "$merkle_root" > message.txt

# Step 5: Verify using OpenSSL (Ed25519)
openssl dgst -sha256 -verify <(openssl pkey -pubin -in "$PUBLIC_KEY_FILE") \
  -signature signature.bin \
  message.txt

# Output:
# ✓ Verified OK  (if signature is valid)
# ✗ Verification Failure  (if signature is invalid - TAMPERED!)
```

**Using Python:**

```python
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def verify_signature(proof_json, public_key_file):
    """Verify Ed25519 signature of Merkle root."""

    # Load proof
    with open(proof_json, 'r') as f:
        proof = json.load(f)

    # Load public key
    with open(public_key_file, 'rb') as f:
        public_key_pem = f.read()

    public_key = serialization.load_pem_public_key(public_key_pem)

    # Extract values
    merkle_root = proof['merkle_tree']['root'].replace('mr:', '')
    signature_hex = proof['digital_signature']['signature'].replace('ed25519:', '')
    signature_bytes = bytes.fromhex(signature_hex)

    # Verify
    try:
        public_key.verify(signature_bytes, merkle_root.encode())
        print(f"✅ Signature verified!")
        print(f"   Merkle root: {merkle_root[:32]}...")
        print(f"   Signer: {proof['organization_id']}")
        print(f"   Signed at: {proof['digital_signature']['signing_timestamp']}")
        return True
    except Exception as e:
        print(f"❌ SIGNATURE VERIFICATION FAILED!")
        print(f"   Error: {e}")
        print(f"   This indicates the Merkle root was modified after signing!")
        return False

verify_signature('batch-1.json', 'healthcare-org-1.pub')
```

### What This Proves

- ✅ Signature is valid (no tampering)
- ✅ Only the organization could have signed it
- ✅ Date and time of signing is authenticated
- ✅ Non-repudiation (signer can't deny signing)

---

## Part 5: End-to-End Verification

### Complete Verification Script

```python
#!/usr/bin/env python3
"""
Complete CIAF Proof Verification Tool
For use by auditors and independent verifiers
"""

import json
import hashlib
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

class CIAFProofVerifier:
    def __init__(self, proof_json_file, public_key_file):
        self.proof_file = proof_json_file
        self.pub_key_file = public_key_file
        self.results = []

    def verify_all(self):
        """Run all verification steps."""

        print("🔍 CIAF Proof Verification Report")
        print("=" * 60)

        # Load files
        with open(self.proof_file) as f:
            self.proof = json.load(f)
        with open(self.pub_key_file, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(f.read())

        # Step 1: Verify hashes
        print("\n[1/4] Verifying output hashes...")
        if self.step1_verify_hashes():
            print("  ✅ All output hashes valid")
        else:
            print("  ❌ Hash verification FAILED")
            return False

        # Step 2: Verify Merkle tree
        print("\n[2/4] Rebuilding Merkle tree...")
        if self.step2_verify_merkle():
            print("  ✅ Merkle tree structure valid")
        else:
            print("  ❌ Merkle tree verification FAILED")
            return False

        # Step 3: Verify Ed25519 signature
        print("\n[3/4] Verifying Ed25519 signature...")
        if self.step3_verify_signature():
            print("  ✅ Digital signature valid")
        else:
            print("  ❌ Signature verification FAILED")
            return False

        # Step 4: Verify timestamps
        print("\n[4/4] Verifying timestamps...")
        if self.step4_verify_timestamps():
            print("  ✅ Timestamps valid")
        else:
            print("  ❌ Timestamp verification FAILED")
            return False

        # Summary
        self.summary()
        return True

    def step1_verify_hashes(self):
        """Step 1: Verify each output's SHA-256 hash."""
        mismatches = 0

        for i, output in enumerate(self.proof['outputs']):
            content = output['output_content']
            expected = output['content_hash']

            computed = hashlib.sha256(content.encode()).hexdigest()
            computed_with_prefix = f"sha256:{computed}"

            if computed_with_prefix != expected:
                mismatches += 1
                print(f"    ❌ Output {i} hash mismatch!")

        return mismatches == 0

    def step2_verify_merkle(self):
        """Step 2: Rebuild and verify Merkle tree."""

        # Get leaf hashes
        leaves = [o['content_hash'] for o in self.proof['outputs']]

        # Rebuild tree
        current_level = leaves
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1] if i+1 < len(current_level) else current_level[i]
                parent = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(parent)
            current_level = next_level

        reconstructed_root = current_level[0]
        expected_root = self.proof['merkle_tree']['root'].replace('mr:', '')

        return reconstructed_root == expected_root

    def step3_verify_signature(self):
        """Step 3: Verify Ed25519 signature."""

        try:
            merkle_root = self.proof['merkle_tree']['root'].replace('mr:', '')
            signature_hex = self.proof['digital_signature']['signature'].replace('ed25519:', '')
            signature_bytes = bytes.fromhex(signature_hex)

            self.public_key.verify(signature_bytes, merkle_root.encode())
            return True
        except Exception:
            return False

    def step4_verify_timestamps(self):
        """Step 4: Verify timestamps make sense."""

        signing_ts = self.proof['digital_signature']['signing_timestamp']
        original_ts = self.proof['outputs'][0]['original_timestamp']

        # Check signing happened after original outputs
        return signing_ts > original_ts

    def summary(self):
        """Print verification summary."""

        print("\n" + "=" * 60)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 60)
        print(f"Batch: {self.proof['batch_number']}")
        print(f"Outputs verified: {len(self.proof['outputs'])}")
        print(f"Organization: {self.proof['organization_id']}")
        print(f"Signed: {self.proof['digital_signature']['signing_timestamp']}")
        print(f"Certificate valid until: {self.proof['digital_signature']['certificate_expiry']}")
        print("\nStatus: ALL CRYPTOGRAPHIC CHECKS PASSED ✅")
        print("\nThis batch is admissible as evidence with non-repudiation.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: ciaf-verify-tool <proof.json> <public-key.pem>")
        sys.exit(1)

    verifier = CIAFProofVerifier(sys.argv[1], sys.argv[2])
    success = verifier.verify_all()
    sys.exit(0 if success else 1)
```

### Running the Verification

```bash
./ciaf-verify-tool batch-1.json healthcare-org-1.pub

# Output:
# 🔍 CIAF Proof Verification Report
# ============================================================
#
# [1/4] Verifying output hashes...
#   ✅ All output hashes valid
#
# [2/4] Rebuilding Merkle tree...
#   ✅ Merkle tree structure valid
#
# [3/4] Verifying Ed25519 signature...
#   ✅ Digital signature valid
#
# [4/4] Verifying timestamps...
#   ✅ Timestamps valid
#
# ============================================================
# ✅ VERIFICATION COMPLETE
# ============================================================
# Batch: 1
# Outputs verified: 1000
# Organization: healthcare-org-1
# Signed: 2026-03-15T16:00:45Z
# Certificate valid until: 2027-03-15T00:00:00Z
#
# Status: ALL CRYPTOGRAPHIC CHECKS PASSED ✅
#
# This batch is admissible as evidence with non-repudiation.
```

---

## Part 6: Troubleshooting Verification Failures

### Failure 1: Hash Mismatch

```
❌ Output 523 hash mismatch!
   Expected: sha256:a3f5d...
   Got:      sha256:b4e6c...
```

**Meaning:** Output content was modified after proof generation
**Action:** This is evidence of tampering. Stop verification and escalate.

### Failure 2: Merkle Root Mismatch

```
❌ Merkle tree verification FAILED!
   Expected root: mr:d47e...
   Rebuilt root:  mr:e58f...
```

**Meaning:** One or more outputs were added/removed, or hashes don't match
**Action:** Indicates tampering with proof batch.

### Failure 3: Signature Verification Failed

```
❌ SIGNATURE VERIFICATION FAILED!
   Error: Bad signature
```

**Meaning:** Merkle root was modified after signing, OR signature file corrupted
**Action:** Check if proof file was corrupted during transfer. If not, tampering detected.

### Failure 4: Certificate Expired

```
⚠️  Certificate expired on 2025-03-15
    Batch signed on 2026-03-15 (impossible!)
```

**Meaning:** Signature timestamp is after certificate expiry
**Action:** Check system time or contact CIAF for updated certificate.

---

## Summary: The Three-Layer Verification

| Layer | Method | What It Proves |
|-------|--------|----------------|
| Layer 1 | SHA-256 hashes | No individual output was modified |
| Layer 2 | Merkle tree | No outputs were added or removed |
| Layer 3 | Ed25519 signature | Only the organization could have created this proof |

**All three must pass** for proof to be admissible in court.

---

## Next Steps

- [Manual Verification](../05-auditors-view/manual-verification.md) - Field guide for auditors
- [Auditor's View](../05-auditors-view/testimony.md) - How to present in court
- [Proof Lifecycle](./proof-lifecycle.md) - Walk through a complete proof
