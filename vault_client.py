"""
CIAF Vault Python Client SDK

Easy integration for submitting and verifying proofs.
"""

import requests
from typing import Dict, Any, Optional, List
from datetime import datetime


class VaultClient:
    """Client for interacting with CIAF Vault."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8002"):
        """
        Initialize vault client.

        Args:
            api_key: Your organization's API key
            base_url: Vault server URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def submit_proof(
        self,
        content: str,
        agent_ids: List[str],
        policies_applied: List[str],
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit proof to vault (immutable).

        Args:
            content: Proof content
            agent_ids: Agents involved
            policies_applied: Policies applied
            timestamp: ISO timestamp (defaults to now)
            metadata: Optional metadata

        Returns:
            Receipt with proof_id and verification_url
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()

        payload = {
            "content": content,
            "agent_ids": agent_ids,
            "policies_applied": policies_applied,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }

        response = requests.post(
            f"{self.base_url}/submit",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def verify_proof(self, proof_id: str) -> Dict[str, Any]:
        """
        Verify proof from vault.

        Args:
            proof_id: Proof ID to verify

        Returns:
            Proof details with verification status
        """
        response = requests.get(
            f"{self.base_url}/verify/{proof_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def generate_certificate(self, proof_id: str) -> Dict[str, Any]:
        """
        Generate verification certificate for proof.

        Args:
            proof_id: Proof ID

        Returns:
            Certificate with signature
        """
        response = requests.post(
            f"{self.base_url}/certificate/{proof_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_audit_trail(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get organization's audit trail.

        Args:
            start_time: ISO timestamp filter
            end_time: ISO timestamp filter
            action: Action type filter
            limit: Max entries to return

        Returns:
            Audit entries
        """
        params = {"limit": limit}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if action:
            params["action"] = action

        response = requests.get(
            f"{self.base_url}/audit-trail",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_audit_summary(self) -> Dict[str, Any]:
        """Get organization's audit summary."""
        response = requests.get(
            f"{self.base_url}/audit-summary",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_organization(self) -> Dict[str, Any]:
        """Get organization details."""
        response = requests.get(
            f"{self.base_url}/organization",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_organization_proofs(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get all proofs for organization.

        Args:
            start_time: ISO timestamp filter
            end_time: ISO timestamp filter
            limit: Max proofs to return

        Returns:
            List of proofs
        """
        params = {"limit": limit}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        response = requests.get(
            f"{self.base_url}/organization/proofs",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check vault health (no auth required)."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics (no auth required)."""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = VaultClient(api_key="your_api_key_here")

    # Submit proof
    receipt = client.submit_proof(
        content="Credit approved with 95% confidence",
        agent_ids=["credit_analyst_001"],
        policies_applied=["fair_lending", "risk_assessment"]
    )
    print(f"✓ Proof submitted: {receipt['proof_id']}")

    # Verify proof
    proof = client.verify_proof(receipt['proof_id'])
    print(f"✓ Verified: {proof['verified']}")

    # Generate certificate
    cert = client.generate_certificate(receipt['proof_id'])
    print(f"✓ Certificate: {cert['certificate_id']}")

    # Get audit trail
    audit = client.get_audit_trail(limit=10)
    print(f"✓ Audit entries: {audit['total']}")

    # Get organization details
    org = client.get_organization()
    print(f"✓ Organization: {org['org_id']}")
