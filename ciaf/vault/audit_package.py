"""
CIAF Audit Package Generator - Create ZIP files for external verification

Generates complete, self-contained audit packages for auditors and legal teams
to perform independent verification without connecting to CIAF systems.

Package Contents:
├── manifest.json (Evidence Manifest for each proof)
├── certificates/ (PDF certificates)
├── proofs/ (JSON proof batches)
├── audit-trail.json (Immutable audit logs)
├── verification-scripts/ (Independent verification tools)
│   ├── verify_hashes.py (Check SHA-256 integrity)
│   ├── verify_merkle_trees.py (Check batch completeness)
│   ├── verify_signatures.py (Check Ed25519 signatures)
│   ├── full_audit.sh (Master verification script)
│   └── README.md (Instructions for auditors)
└── metadata.json (Package information)
"""

import json
import zipfile
import io
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path


VERIFICATION_SCRIPTS = {
    "verify_hashes.py": '''#!/usr/bin/env python3
"""Verify all output hashes in all batch files."""

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
        for output in proof.get('outputs', []):
            content = output.get('output_content', '')
            expected = output.get('content_hash', '')

            computed = hashlib.sha256(content.encode()).hexdigest()
            computed_with_prefix = f"sha256:{computed}"

            if computed_with_prefix != expected:
                batch_errors += 1
                error_log.append({
                    'file': batch_file.name,
                    'output_id': output.get('output_id', 'unknown'),
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
    print("\\n" + "=" * 60)
    print("Hash Verification Report")
    print("=" * 60)
    print(f"✅ Verified: {verified:,}")
    print(f"❌ Errors:   {errors:,}")

    if errors > 0:
        print("\\nError details:")
        for err in error_log[:10]:  # Show first 10
            print(f"  {err['file']}: {err['output_id']}")
            print(f"    Expected: {err['expected'][:32]}...")
            print(f"    Got:      {err['got'][:32]}...")

    return errors == 0

if __name__ == '__main__':
    success = verify_all_hashes('./proofs')
    sys.exit(0 if success else 1)
''',

    "verify_merkle_trees.py": '''#!/usr/bin/env python3
"""Verify Merkle tree structures for batch completeness."""

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
    leaf_hashes = [o.get('content_hash', '') for o in proof.get('outputs', [])]

    # Rebuild tree
    rebuilt_root = rebuild_merkle_tree(leaf_hashes)

    # Get expected root
    merkle_tree = proof.get('merkle_tree', {})
    expected_root = merkle_tree.get('root', '').replace('mr:', '')

    # Compare
    is_valid = rebuilt_root == expected_root

    return {
        'file': batch_file.name,
        'valid': is_valid,
        'outputs': len(leaf_hashes),
        'expected_root': expected_root[:32] + '...' if expected_root else 'N/A',
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
print("\\n" + "=" * 60)
valid_count = sum(1 for r in results if r['valid'])
print(f"✅ Valid:   {valid_count}/{len(results)}")
print(f"❌ Invalid: {len(results) - valid_count}/{len(results)}")

if valid_count == len(results):
    print("\\n✅ ALL MERKLE TREES VALID")
    print("No outputs were added, removed, or reordered.")
else:
    print("\\n⚠️  MERKLE TREE TAMPERING DETECTED")
    for r in results:
        if not r['valid']:
            print(f"  {r['file']}: Expected {r['expected_root']}, got {r['rebuilt_root']}")
''',

    "verify_signatures.py": '''#!/usr/bin/env python3
"""Verify Ed25519 signatures of Merkle roots."""

import json
from pathlib import Path

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not available")
    print("Install with: pip install cryptography")

def verify_signature(batch_file, public_key):
    """Verify Ed25519 signature of Merkle root."""

    with open(batch_file) as f:
        proof = json.load(f)

    merkle_root = proof.get('merkle_tree', {}).get('root', '').replace('mr:', '')
    signature_hex = proof.get('digital_signature', {}).get('signature', '').replace('ed25519:', '')

    if not merkle_root or not signature_hex:
        return False

    try:
        signature_bytes = bytes.fromhex(signature_hex)
        public_key.verify(signature_bytes, merkle_root.encode())
        return True
    except Exception:
        return False

if __name__ == '__main__':
    if not CRYPTO_AVAILABLE:
        print("Cannot verify signatures without cryptography library")
        exit(1)

    # Load public key (once)
    public_key_file = 'public_key.pem'
    if not Path(public_key_file).exists():
        print(f"Error: {public_key_file} not found")
        print("Please provide the organization's Ed25519 public key")
        exit(1)

    with open(public_key_file, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())

    # Verify all batches
    print("Verifying Ed25519 signatures...")

    valid = 0
    invalid = 0

    for batch_file in sorted(Path('./proofs').glob('*.json')):
        if verify_signature(str(batch_file), public_key):
            print(f"✅ {batch_file.name}")
            valid += 1
        else:
            print(f"❌ {batch_file.name} - SIGNATURE INVALID!")
            invalid += 1

    # Summary
    print("\\n" + "=" * 60)
    print(f"✅ Valid:   {valid}/{valid + invalid}")
    print(f"❌ Invalid: {invalid}/{valid + invalid}")

    if invalid == 0:
        print("\\n✅ ALL SIGNATURES VALID")
        print("All batches were signed by the organization.")
        print("Non-repudiation established.")
    else:
        print("\\n⚠️  SIGNATURE TAMPERING DETECTED")
        print("Someone modified the Merkle root after signing!")
''',

    "full_audit.sh": '''#!/bin/bash
# Master auditor verification script

set -e  # Exit on any error

SOURCE_DIR="./proofs"
REPORT="audit_verification_report.txt"

echo "🔍 Starting CIAF Proof Audit Verification"
echo "=========================================="
echo "Date: $(date)"
echo "Source: $SOURCE_DIR"
echo ""
echo "This verification is independent and offline."
echo "No connection to CIAF systems required."
echo ""
echo "=========================================="
echo ""

# Step 1: Hash verification
echo "[1/3] Verifying output hashes..."
if command -v python3 &> /dev/null; then
    python3 verify_hashes.py | tee -a "$REPORT"
else
    echo "Warning: Python 3 not found, skipping hash verification"
fi

echo ""

# Step 2: Merkle tree verification
echo "[2/3] Verifying Merkle tree structures..."
if command -v python3 &> /dev/null; then
    python3 verify_merkle_trees.py | tee -a "$REPORT"
else
    echo "Warning: Python 3 not found, skipping Merkle verification"
fi

echo ""

# Step 3: Signature verification
echo "[3/3] Verifying Ed25519 signatures..."
if command -v python3 &> /dev/null; then
    python3 verify_signatures.py | tee -a "$REPORT"
else
    echo "Warning: Python 3 not found, skipping signature verification"
fi

echo ""
echo "=========================================="
echo "AUDIT VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "Report saved to: $REPORT"
''',

    "README.md": '''# CIAF Audit Package - External Verification Guide

This is a self-contained audit package for independent verification of AI inference outputs
without connecting to CIAF systems.

## Quick Start

### 1. Verify Hashes (Individual Output Integrity)

```bash
python3 verify_hashes.py
```

This checks that each output hasn't been modified:
- Recomputes SHA-256 hash for each output
- Compares to stored hash
- Reports any tampering detected

### 2. Verify Merkle Trees (Batch Completeness)

```bash
python3 verify_merkle_trees.py
```

This checks that no outputs were added, removed, or reordered:
- Rebuilds Merkle tree from leaf hashes
- Compares root to signed root
- Reports any batch-level tampering

### 3. Verify Signatures (Non-Repudiation)

```bash
python3 verify_signatures.py
```

This checks that the organization signed the proof:
- Uses Ed25519 public key
- Verifies signature on Merkle root
- Proves organization cannot deny signing

**Note:** You'll need the organization's public key (public_key.pem)

### Run Full Audit

```bash
bash full_audit.sh
```

This runs all three verifications and generates a complete audit report.

## Package Contents

```
├── manifest.json          - Evidence Manifest (legal standard)
├── metadata.json          - Package information and statistics
├── proofs/               - JSON proof batches
├── certificates/         - PDF verification certificates
├── audit-trail.json      - Immutable audit logs
├── verification-scripts/
│   ├── verify_hashes.py          - Hash integrity verification
│   ├── verify_merkle_trees.py    - Batch completeness verification
│   ├── verify_signatures.py      - Signature verification
│   ├── full_audit.sh             - Master verification script
│   └── README.md (this file)
└── public_key.pem        - Organization's Ed25519 public key
```

## What Each Verification Proves

| Test | Proves | Result |
|------|--------|--------|
| **Hash Verification** | Outputs unchanged | No tampering at output level |
| **Merkle Tree Verification** | No outputs added/removed/reordered | Batch is complete |
| **Signature Verification** | Organization signed the batch | Non-repudiation established |

## Legal Admissibility

This audit demonstrates:

✅ **Federal Rule 901** - Authentication of evidence (cryptographic proof)
✅ **Federal Rule 902** - Self-authenticating documents (signed proof)
✅ **Daubert Standard** - Scientific reliability (peer-reviewed crypto)
✅ **Chain of Custody** - Unbroken evidence trail (immutable audit logs)

## System Requirements

- Python 3.7+
- bash (for full_audit.sh)
- cryptography library: `pip install cryptography`

## Troubleshooting

### "verify_signatures.py: No such file"

Make sure you're in the verification-scripts directory:

```bash
cd verification-scripts
python3 verify_signatures.py
```

### "public_key.pem not found"

You need the organization's Ed25519 public key. Request from:
- The organization's compliance officer
- CIAF support
- The certificate or receipt issued with the proof

### "Hash mismatch detected"

This is a security incident. An output was modified after being proven.

**Action:**
1. Stop the audit
2. Document which output hash mismatched
3. Contact CIAF security team
4. Escalate to legal team

## More Information

- See `manifest.json` for complete proof details
- See `audit-trail.json` for operation history
- See `certificates/` for PDF certificates

## Support

For questions about verification methodology:
- See the CIAF Vault documentation
- Contact your audit firm
- Escalate to CIAF compliance team
'''
}


class AuditPackageGenerator:
    """
    Generates complete audit packages for external verification.

    Creates self-contained ZIP files that auditors can verify
    independently without CIAF system access.
    """

    @staticmethod
    def create_audit_package(
        organization_id: str,
        proofs: List[Dict[str, Any]],
        audit_trail: List[Dict[str, Any]],
        certificates: Dict[str, bytes],
        manifests: Dict[str, Dict[str, Any]],
        public_key_pem: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Create a complete audit package ZIP.

        Args:
            organization_id: Organization ID
            proofs: List of proof dictionaries
            audit_trail: List of audit trail entries
            certificates: Dict of {proof_id: pdf_bytes}
            manifests: Dict of {proof_id: manifest_dict}
            public_key_pem: Organization's Ed25519 public key (PEM format)
            metadata: Additional metadata for the package

        Returns:
            ZIP file bytes
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. Metadata
            if metadata is None:
                metadata = {}

            metadata.update({
                "package_id": f"audit-{organization_id}-{datetime.now(timezone.utc).isoformat()[:19]}",
                "organization_id": organization_id,
                "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                "proof_count": len(proofs),
                "audit_entry_count": len(audit_trail),
                "verification_status": "pending",
            })

            zf.writestr(
                "metadata.json",
                json.dumps(metadata, indent=2, default=str)
            )

            # 2. Evidence Manifests
            for proof_id, manifest in manifests.items():
                zf.writestr(
                    f"manifest.json",
                    json.dumps(manifest, indent=2, default=str)
                )

            # 3. Proof batches
            for i, proof in enumerate(proofs):
                proof_id = proof.get('proof_id', f'proof-{i}')
                zf.writestr(
                    f"proofs/{proof_id}.json",
                    json.dumps(proof, indent=2, default=str)
                )

            # 4. Certificates
            for proof_id, cert_bytes in certificates.items():
                zf.writestr(
                    f"certificates/{proof_id}.pdf",
                    cert_bytes
                )

            # 5. Audit trail
            zf.writestr(
                "audit-trail.json",
                json.dumps(audit_trail, indent=2, default=str)
            )

            # 6. Verification scripts
            for script_name, script_content in VERIFICATION_SCRIPTS.items():
                zf.writestr(
                    f"verification-scripts/{script_name}",
                    script_content
                )

            # 7. Public key (if provided)
            if public_key_pem:
                zf.writestr(
                    "verification-scripts/public_key.pem",
                    public_key_pem
                )

        return zip_buffer.getvalue()

    @staticmethod
    def create_batch_verification_package(
        batch_id: str,
        proof_data: Dict[str, Any],
        batch_hash: str,
        merkle_root: str,
        signature: str,
        public_key_pem: Optional[str] = None,
    ) -> bytes:
        """
        Create a lightweight verification package for a single batch.

        Args:
            batch_id: Batch identifier
            proof_data: Proof batch data
            batch_hash: Hash of proof content
            merkle_root: Merkle root of batch
            signature: Ed25519 signature
            public_key_pem: Organization's public key

        Returns:
            ZIP file bytes
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Metadata
            metadata = {
                "batch_id": batch_id,
                "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                "batch_hash": batch_hash,
                "merkle_root": merkle_root,
                "signature_algorithm": "Ed25519",
            }
            zf.writestr("metadata.json", json.dumps(metadata, indent=2))

            # Proof
            zf.writestr("proof.json", json.dumps(proof_data, indent=2, default=str))

            # Verification script for single batch
            verify_single = '''#!/usr/bin/env python3
import json
import hashlib
from pathlib import Path

# Verify this batch
with open("proof.json") as f:
    proof = json.load(f)

# Extract and verify hash
content = json.dumps(proof, sort_keys=True)
computed_hash = hashlib.sha256(content.encode()).hexdigest()
expected_hash = proof.get("batch_hash", "")

if computed_hash == expected_hash:
    print("✅ BATCH HASH VALID - No tampering detected")
else:
    print("❌ BATCH HASH MISMATCH - Tampering detected!")
    print(f"Expected: {expected_hash}")
    print(f"Got:      {computed_hash}")
'''
            zf.writestr("verify_batch.py", verify_single)

            # Public key
            if public_key_pem:
                zf.writestr("public_key.pem", public_key_pem)

        return zip_buffer.getvalue()


__all__ = ["AuditPackageGenerator"]
