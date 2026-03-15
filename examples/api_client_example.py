#!/usr/bin/env python3
"""
CIAF Vault API - Complete Usage Example

This script demonstrates how to use the CIAF Vault API to:
1. Submit cryptographic proofs
2. Verify proofs with read counting
3. Generate verification certificates
4. Query audit trails
5. Get organization statistics

Requirements:
  pip install requests

Usage:
  python api_client_example.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
VAULT_API_URL = "http://localhost:8002"
API_KEY = "test-api-key-org-1"  # Set this from environment/config in production


class VaultAPIClient:
    """Simple client for CIAF Vault API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, timeout=10, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """Check vault service health."""
        return self._request("GET", "/health")

    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics."""
        return self._request("GET", "/stats")

    def submit_proof(
        self,
        content: str,
        agent_ids: list,
        policies_applied: list,
        metadata: Dict = None,
    ) -> Dict[str, Any]:
        """Submit a proof to the vault."""
        payload = {
            "content": content,
            "agent_ids": agent_ids,
            "policies_applied": policies_applied,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        return self._request("POST", "/submit", json=payload)

    def verify_proof(self, proof_id: str) -> Dict[str, Any]:
        """Verify a proof (increments read counter)."""
        return self._request("GET", f"/verify/{proof_id}")

    def generate_certificate(self, proof_id: str) -> Dict[str, Any]:
        """Generate verification certificate for proof."""
        return self._request("POST", f"/certificate/{proof_id}")

    def get_audit_trail(self, action_filter: str = None, limit: int = 100):
        """Get audit trail for organization."""
        params = {"limit": limit}
        if action_filter:
            params["action"] = action_filter
        return self._request("GET", "/audit-trail", params=params)

    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit summary."""
        return self._request("GET", "/audit-summary")

    def get_organization(self) -> Dict[str, Any]:
        """Get organization details."""
        return self._request("GET", "/organization")

    def get_organization_proofs(self, limit: int = 100) -> Dict[str, Any]:
        """Get all proofs for organization."""
        return self._request("GET", "/organization/proofs", params={"limit": limit})


def main():
    """Run example workflows."""
    print("=" * 80)
    print("CIAF VAULT API - USAGE EXAMPLES")
    print("=" * 80)
    print()

    client = VaultAPIClient(VAULT_API_URL, API_KEY)

    # Example 1: Health Check
    print("📋 1. Health Check")
    print("-" * 80)
    health = client.health_check()
    if health:
        print(f"✅ Service Status: {health.get('status')}")
        print(f"   Service: {health.get('service')}")
        print(f"   Version: {health.get('version')}")
    print()

    # Example 2: Get Statistics
    print("📊 2. Vault Statistics")
    print("-" * 80)
    stats = client.get_stats()
    if stats:
        print(f"✅ Total Proofs: {stats.get('total_proofs')}")
        print(f"   Total Organizations: {stats.get('total_organizations')}")
        print(f"   Active Organizations: {stats.get('active_organizations')}")
        print(f"   Total Reads: {stats.get('total_reads')}")
    print()

    # Example 3: Organization Details
    print("🏢 3. Organization Details")
    print("-" * 80)
    org = client.get_organization()
    if org:
        print(f"✅ Organization ID: {org.get('org_id')}")
        print(f"   Name: {org.get('name')}")
        print(f"   Created: {org.get('created_at')}")
        print(f"   API Keys: {org.get('api_key_count')}")
        print(f"   Last Activity: {org.get('last_activity')}")
    print()

    # Example 4: Submit Proof
    print("📝 4. Submit Proof (Write-Once)")
    print("-" * 80)
    proof_content = json.dumps(
        {
            "model": "gpt-4",
            "task": "classification",
            "output": "result: positive",
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat(),
        }
    )

    receipt = client.submit_proof(
        content=proof_content,
        agent_ids=["agent-classifier", "agent-validator"],
        policies_applied=["policy-gdpr", "policy-mlops"],
        metadata={"domain": "billing", "risk_level": "low"},
    )

    proof_id = None
    if receipt:
        proof_id = receipt.get("proof_id")
        print(f"✅ Proof Submitted!")
        print(f"   Proof ID: {proof_id}")
        print(f"   Receipt ID: {receipt.get('receipt_id')}")
        print(f"   Timestamp: {receipt.get('timestamp')}")
        print(f"   Verify URL: {receipt.get('verification_url')}")
    print()

    # Example 5: Verify Proof (multiple times to show read counting)
    if proof_id:
        print("🔍 5. Verify Proof (Multiple Reads)")
        print("-" * 80)
        for i in range(3):
            verification = client.verify_proof(proof_id)
            if verification:
                print(
                    f"   Read #{i+1}: Read Count = {verification.get('read_count')}"
                )
        print(f"✅ Proof verified {i+1} times (read counter incremented)")
        print()

        # Example 6: Generate Certificate
        print("🎖️  6. Generate Verification Certificate")
        print("-" * 80)
        cert = client.generate_certificate(proof_id)
        if cert:
            print(f"✅ Certificate Generated!")
            print(f"   Certificate ID: {cert.get('certificate_id')}")
            print(f"   Valid Until: {cert.get('valid_until')}")
            print(f"   Issuer: {cert.get('issuer')}")
        print()

    # Example 7: Audit Trail
    print("📜 7. Audit Trail")
    print("-" * 80)
    audit = client.get_audit_trail(action_filter="submit_proof", limit=5)
    if audit:
        entries = audit.get("entries", [])
        print(f"✅ Audit Entries (Total: {audit.get('total')})")
        for entry in entries[:3]:
            print(f"   - {entry.get('action')} at {entry.get('timestamp')}")
    print()

    # Example 8: Audit Summary
    print("📈 8. Audit Summary")
    print("-" * 80)
    summary = client.get_audit_summary()
    if summary:
        summary_data = summary.get("summary", {})
        print(f"✅ Audit Summary")
        for key, value in summary_data.items():
            print(f"   {key}: {value}")
    print()

    # Example 9: Get Organization Proofs
    print("📚 9. Organization Proofs")
    print("-" * 80)
    proofs = client.get_organization_proofs(limit=10)
    if proofs:
        proof_list = proofs.get("proofs", [])
        print(f"✅ Organization has {proofs.get('total')} proofs (showing first 3)")
        for proof in proof_list[:3]:
            print(f"   - {proof.get('proof_id')} (reads: {proof.get('read_count')})")
    print()

    print("=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)
    print()
    print("📚 Key Takeaways:")
    print("  1. Submit: Creates immutable proof (WORM - write-once-read-many)")
    print("  2. Verify: Read-only operation (increments read counter)")
    print("  3. Certificate: Cryptographic proof of verification")
    print("  4. Audit: Complete audit trail of all operations")
    print("  5. Organization: View all proofs and statistics")
    print()
    print("🔐 Security Features:")
    print("  - API key authentication (Bearer token)")
    print("  - WORM guarantee (proofs cannot be modified)")
    print("  - Read counting for audit purposes")
    print("  - Cryptographic certificates (Ed25519 signed)")
    print("  - Immutable audit trails")
    print()


if __name__ == "__main__":
    main()
