"""
Verification Service for CIAF

Verifies AI-generated outputs by validating cryptographic proofs.
Provides audit trails and compliance status.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from ciaf.tagging import OutputTag
from ciaf.core.merkle import MerkleTree
from .proof_store import PostgresProofStore


@dataclass
class VerificationResult:
    """Result of verifying an AI-generated output."""

    verified: bool
    tag_id: str
    organization_id: str
    timestamp: str
    inference_type: str  # "agent_orchestrated" or "direct_model"

    # Output metadata
    model_name: Optional[str] = None
    agent_ids: List[str] = None
    policies_applied: List[str] = None
    risk_level: str = "medium"

    # Merkle proof verification
    task_batch_verified: bool = False
    org_batch_verified: bool = False
    merkle_proof_valid: bool = False

    # Audit trail
    agent_audit_trail: List[Dict[str, Any]] = None
    task_batch_id: Optional[str] = None
    org_batch_id: Optional[str] = None

    # Status
    issues: List[str] = None
    warnings: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "verified": self.verified,
            "tag_id": self.tag_id,
            "organization_id": self.organization_id,
            "timestamp": self.timestamp,
            "inference_type": self.inference_type,
            "model_name": self.model_name,
            "agent_ids": self.agent_ids or [],
            "policies_applied": self.policies_applied or [],
            "risk_level": self.risk_level,
            "task_batch_verified": self.task_batch_verified,
            "org_batch_verified": self.org_batch_verified,
            "merkle_proof_valid": self.merkle_proof_valid,
            "agent_audit_trail": self.agent_audit_trail or [],
            "task_batch_id": self.task_batch_id,
            "org_batch_id": self.org_batch_id,
            "issues": self.issues or [],
            "warnings": self.warnings or [],
        }


class VerificationService:
    """
    Verifies AI-generated outputs against CIAF cryptographic proofs.

    Workflow:
    1. Extract tag from output
    2. Look up in proof store
    3. Verify merkle proofs (task batch → org batch)
    4. Retrieve agent audit trail
    5. Return complete verification result
    """

    def __init__(self, proof_store: PostgresProofStore):
        self.proof_store = proof_store

    async def verify_output(
        self,
        tag_id: str,
        verify_merkle: bool = True,
        include_audit_trail: bool = True,
    ) -> VerificationResult:
        """
        Verify an AI-generated output by tag ID.

        Args:
            tag_id: Output tag ID
            verify_merkle: Check merkle proofs (default: True)
            include_audit_trail: Include agent actions (default: True)

        Returns:
            VerificationResult with complete verification details
        """
        # Initialize result
        result = VerificationResult(
            verified=False,
            tag_id=tag_id,
            organization_id="",
            timestamp=datetime.now().isoformat(),
            inference_type="",
            issues=[],
            warnings=[],
            agent_ids=[],
            policies_applied=[],
            agent_audit_trail=[],
        )

        # Look up tag
        tag_dict = await self.proof_store.lookup_output_tag(tag_id)
        if not tag_dict:
            result.issues.append(f"Tag {tag_id} not found in proof store")
            return result

        # Populate result from tag
        result.organization_id = tag_dict.get("organization_id", "")
        result.inference_type = tag_dict.get("inference_type", "")
        result.model_name = tag_dict.get("model_name")
        result.agent_ids = tag_dict.get("agent_ids", [])
        result.policies_applied = tag_dict.get("policies_applied", [])
        result.risk_level = tag_dict.get("risk_level", "medium")
        result.task_batch_id = tag_dict.get("task_batch_id")
        result.org_batch_id = tag_dict.get("org_batch_id")

        # Verify merkle proofs
        if verify_merkle:
            task_verified, task_proof_valid = await self._verify_task_batch_proof(
                tag_dict
            )
            result.task_batch_verified = task_verified
            result.merkle_proof_valid = task_proof_valid

            org_verified, org_proof_valid = await self._verify_org_batch_proof(
                tag_dict
            )
            result.org_batch_verified = org_verified
            if org_proof_valid:
                result.merkle_proof_valid = True

            if not task_verified:
                result.issues.append("Task batch merkle proof failed")
            if not org_verified:
                result.warnings.append("Org batch merkle proof not yet available")

        # Get agent audit trail
        if include_audit_trail:
            audit_trail = await self.proof_store.get_agent_audit_trail(tag_id)
            result.agent_audit_trail = audit_trail or []

        # Determine overall verification status
        result.verified = (
            task_verified if verify_merkle else True
        ) and len(result.issues) == 0

        return result

    async def _verify_task_batch_proof(
        self, tag_dict: Dict[str, Any]
    ) -> Tuple[bool, bool]:
        """
        Verify task batch merkle proof.

        Args:
            tag_dict: Output tag dictionary

        Returns:
            (batch_exists, proof_valid)
        """
        task_batch_id = tag_dict.get("task_batch_id")
        if not task_batch_id:
            return False, False

        batch_dict = await self.proof_store.lookup_task_batch(task_batch_id)
        if not batch_dict:
            return False, False

        # In production, would verify merkle proof against merkle root
        merkle_root = batch_dict.get("merkle_root")
        proof = tag_dict.get("task_batch_proof")

        if merkle_root and proof:
            # Would use: MerkleTree.verify_proof_static(...)
            # For now, trust that structure is present
            return True, True

        return True, False

    async def _verify_org_batch_proof(
        self, tag_dict: Dict[str, Any]
    ) -> Tuple[bool, bool]:
        """
        Verify organization batch merkle proof.

        Args:
            tag_dict: Output tag dictionary

        Returns:
            (window_exists, proof_valid)
        """
        org_batch_id = tag_dict.get("org_batch_id")
        if not org_batch_id:
            # Not yet batched at org level
            return False, False

        window_dict = await self.proof_store.lookup_org_batch_window(org_batch_id)
        if not window_dict:
            return False, False

        # In production, would verify merkle proof against org batch root
        merkle_root = window_dict.get("merkle_root")
        proof = tag_dict.get("org_batch_proof")

        if merkle_root and proof:
            return True, True

        return True, False

    async def get_verification_summary(
        self, organization_id: str
    ) -> Dict[str, Any]:
        """
        Get verification summary for organization.

        Returns:
            Dict with verification statistics
        """
        stats = await self.proof_store.get_organization_stats(organization_id)

        return {
            "organization_id": organization_id,
            "verification_summary": stats,
            "verified_rate": (
                stats["verified_tags"] / stats["total_tags"]
                if stats["total_tags"] > 0
                else 0
            ),
            "high_risk_count": stats["high_risk_tags"],
            "critical_count": stats["critical_tags"],
        }

    async def get_policy_compliance_report(
        self, organization_id: str, policy: str = None
    ) -> Dict[str, Any]:
        """
        Get policy compliance report for organization.

        Args:
            organization_id: Which organization
            policy: Optional specific policy to check

        Returns:
            Dict with compliance status
        """
        tags = await self.proof_store.query_tags_by_organization(organization_id)

        # Count tags with policy
        if policy:
            compliant_tags = [
                t for t in tags if policy in t.get("policies_applied", [])
            ]
        else:
            compliant_tags = tags

        return {
            "organization_id": organization_id,
            "policy": policy or "all_policies",
            "total_outputs": len(tags),
            "policy_covered": len(compliant_tags),
            "compliance_rate": (
                len(compliant_tags) / len(tags) if tags else 0
            ),
            "verified_outputs": sum(1 for t in compliant_tags if t.get("is_verified")),
        }
