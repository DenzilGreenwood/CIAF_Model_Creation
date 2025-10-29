"""
Cryptographic receipt generation and audit trail management for compliance gates.

This module provides tamper-evident receipt generation for gate evaluation results,
enabling comprehensive audit trails and regulatory compliance documentation.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .interfaces import GateResult, Stage


@dataclass
class GateReceipt:
    """Cryptographic receipt for gate evaluation result."""

    receipt_id: str
    gate_name: str
    stage: Stage
    timestamp: datetime
    status: str

    # Content hash and signature
    content_hash: str
    signature: Optional[str] = None

    # Merkle tree integration
    merkle_leaf_hash: str = ""
    merkle_path: List[str] = field(default_factory=list)
    batch_root: Optional[str] = None

    # Metadata
    policy_version: Optional[str] = None
    metrics_summary: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class ReviewReceipt:
    """Receipt for human review decisions with reviewer identity."""

    review_id: str
    gate_receipt_id: str
    reviewer_id: str
    review_timestamp: datetime

    # Review decision
    decision: str  # approve, reject, escalate
    rationale: str

    # Cryptographic evidence
    content_hash: str

    # Optional fields with defaults
    conditions: List[str] = field(default_factory=list)
    reviewer_signature: Optional[str] = None

    # Audit trail linkage
    parent_receipt_hash: str = ""
    linked_receipts: List[str] = field(default_factory=list)


class GateReceiptGenerator:
    """
    Generates cryptographic receipts for gate evaluation results.

    Provides tamper-evident documentation of compliance decisions with
    cryptographic signatures and Merkle tree integration for batch validation.
    """

    def __init__(self, signing_key: Optional[str] = None):
        self.signing_key = signing_key
        self.merkle_leaves: List[str] = []

    def create_gate_receipt(
        self, gate_result: GateResult, stage: Stage, policy_version: Optional[str] = None
    ) -> GateReceipt:
        """
        Create cryptographic receipt for gate evaluation result.

        Args:
            gate_result: Gate evaluation result
            stage: ML lifecycle stage
            policy_version: Policy version used for evaluation

        Returns:
            Cryptographic receipt with content hash and signature
        """
        receipt_id = str(uuid.uuid4())

        # Create receipt content for hashing
        receipt_content = {
            "receipt_id": receipt_id,
            "gate_name": gate_result.gate_name,
            "stage": stage.value,
            "timestamp": gate_result.timestamp.isoformat(),
            "status": gate_result.status.value,
            "metrics": gate_result.metrics,
            "evidence_refs": gate_result.evidence_refs,
            "policy_version": policy_version,
            "thresholds_applied": gate_result.thresholds_applied,
            "regulatory_alignment": gate_result.regulatory_alignment,
        }

        # Generate content hash
        content_json = json.dumps(receipt_content, sort_keys=True)
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()

        # Generate Merkle leaf hash
        merkle_leaf_hash = self._generate_merkle_leaf(receipt_id, content_hash)
        self.merkle_leaves.append(merkle_leaf_hash)

        # Create receipt
        receipt = GateReceipt(
            receipt_id=receipt_id,
            gate_name=gate_result.gate_name,
            stage=stage,
            timestamp=gate_result.timestamp,
            status=gate_result.status.value,
            content_hash=content_hash,
            merkle_leaf_hash=merkle_leaf_hash,
            policy_version=policy_version,
            metrics_summary=self._create_metrics_summary(gate_result),
            evidence_refs=gate_result.evidence_refs.copy(),
        )

        # Add signature if signing key available
        if self.signing_key:
            receipt.signature = self._sign_receipt(receipt)

        return receipt

    def create_review_receipt(
        self,
        gate_receipt: GateReceipt,
        reviewer_id: str,
        decision: str,
        rationale: str,
        conditions: Optional[List[str]] = None,
    ) -> ReviewReceipt:
        """
        Create receipt for human review decision.

        Args:
            gate_receipt: Original gate receipt being reviewed
            reviewer_id: Identity of human reviewer
            decision: Review decision (approve/reject/escalate)
            rationale: Reviewer's rationale for decision
            conditions: Any conditions or requirements

        Returns:
            Review receipt with cryptographic linkage to original
        """
        review_id = str(uuid.uuid4())
        review_timestamp = datetime.now()
        conditions = conditions or []

        # Create review content
        review_content = {
            "review_id": review_id,
            "gate_receipt_id": gate_receipt.receipt_id,
            "reviewer_id": reviewer_id,
            "review_timestamp": review_timestamp.isoformat(),
            "decision": decision,
            "rationale": rationale,
            "conditions": conditions,
            "parent_receipt_hash": gate_receipt.content_hash,
        }

        # Generate content hash
        content_json = json.dumps(review_content, sort_keys=True)
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()

        return ReviewReceipt(
            review_id=review_id,
            gate_receipt_id=gate_receipt.receipt_id,
            reviewer_id=reviewer_id,
            review_timestamp=review_timestamp,
            decision=decision,
            rationale=rationale,
            conditions=conditions,
            content_hash=content_hash,
            parent_receipt_hash=gate_receipt.content_hash,
        )

    def finalize_batch(self) -> Optional[str]:
        """
        Finalize current batch of receipts and generate Merkle root.

        Returns:
            Merkle root hash for the batch, or None if no receipts
        """
        if not self.merkle_leaves:
            return None

        # Simple Merkle tree construction
        current_level = self.merkle_leaves.copy()

        while len(current_level) > 1:
            next_level = []

            # Pair up hashes and combine
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                combined = hashlib.sha256(f"{left}{right}".encode()).hexdigest()
                next_level.append(combined)

            current_level = next_level

        batch_root = current_level[0] if current_level else None

        # Clear batch for next round
        self.merkle_leaves.clear()

        return batch_root

    def verify_receipt(self, receipt: GateReceipt) -> bool:
        """
        Verify the integrity of a gate receipt.

        Args:
            receipt: Receipt to verify

        Returns:
            True if receipt is valid and untampered
        """
        try:
            # Reconstruct content for verification
            receipt_content = {
                "receipt_id": receipt.receipt_id,
                "gate_name": receipt.gate_name,
                "stage": receipt.stage.value,
                "timestamp": receipt.timestamp.isoformat(),
                "status": receipt.status,
                "metrics": receipt.metrics_summary,
                "evidence_refs": receipt.evidence_refs,
                "policy_version": receipt.policy_version,
            }

            # Verify content hash
            content_json = json.dumps(receipt_content, sort_keys=True)
            expected_hash = hashlib.sha256(content_json.encode()).hexdigest()

            return expected_hash == receipt.content_hash

        except Exception:
            return False

    def get_audit_trail(
        self,
        gate_receipts: List[GateReceipt],
        review_receipts: Optional[List[ReviewReceipt]] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit trail from receipts.

        Args:
            gate_receipts: List of gate evaluation receipts
            review_receipts: Optional list of review receipts

        Returns:
            Structured audit trail with timeline and evidence
        """
        review_receipts = review_receipts or []

        # Build timeline of events
        timeline = []

        for receipt in gate_receipts:
            timeline.append(
                {
                    "timestamp": receipt.timestamp.isoformat(),
                    "type": "gate_evaluation",
                    "gate_name": receipt.gate_name,
                    "stage": receipt.stage.value,
                    "status": receipt.status,
                    "receipt_id": receipt.receipt_id,
                    "content_hash": receipt.content_hash,
                }
            )

        for review in review_receipts:
            timeline.append(
                {
                    "timestamp": review.review_timestamp.isoformat(),
                    "type": "human_review",
                    "reviewer_id": review.reviewer_id,
                    "decision": review.decision,
                    "gate_receipt_id": review.gate_receipt_id,
                    "review_id": review.review_id,
                    "content_hash": review.content_hash,
                }
            )

        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])

        # Generate summary statistics
        gate_stats = {}
        for receipt in gate_receipts:
            status = receipt.status
            gate_stats[status] = gate_stats.get(status, 0) + 1

        review_stats = {}
        for review in review_receipts:
            decision = review.decision
            review_stats[decision] = review_stats.get(decision, 0) + 1

        return {
            "audit_trail_id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "timeline": timeline,
            "summary": {
                "total_gates": len(gate_receipts),
                "total_reviews": len(review_receipts),
                "gate_outcomes": gate_stats,
                "review_decisions": review_stats,
            },
            "cryptographic_evidence": {
                "receipt_hashes": [r.content_hash for r in gate_receipts],
                "review_hashes": [r.content_hash for r in review_receipts],
                "merkle_leaves": [r.merkle_leaf_hash for r in gate_receipts if r.merkle_leaf_hash],
            },
        }

    def _generate_merkle_leaf(self, receipt_id: str, content_hash: str) -> str:
        """Generate Merkle tree leaf hash for receipt."""
        leaf_content = f"{receipt_id}:{content_hash}"
        return hashlib.sha256(leaf_content.encode()).hexdigest()

    def _create_metrics_summary(self, gate_result: GateResult) -> Dict[str, Any]:
        """Create summary of key metrics from gate result."""
        summary = {}

        # Extract key metrics based on common patterns
        for key, value in gate_result.metrics.items():
            if isinstance(value, (int, float, bool)):
                summary[key] = value
            elif isinstance(value, str) and len(value) < 100:
                summary[key] = value

        return summary

    def _sign_receipt(self, receipt: GateReceipt) -> str:
        """Generate signature for receipt (placeholder implementation)."""
        # In production, this would use proper cryptographic signing
        signature_content = f"{receipt.receipt_id}:{receipt.content_hash}:{self.signing_key}"
        return hashlib.sha256(signature_content.encode()).hexdigest()


class ComplianceAuditTrail:
    """
    Manages comprehensive audit trails for compliance gate operations.

    Provides long-term storage and retrieval of gate receipts with
    cryptographic verification and regulatory reporting capabilities.
    """

    def __init__(self):
        self.receipts: Dict[str, GateReceipt] = {}
        self.reviews: Dict[str, ReviewReceipt] = {}
        self.batch_roots: List[str] = []

    def add_gate_receipt(self, receipt: GateReceipt) -> None:
        """Add gate receipt to audit trail."""
        self.receipts[receipt.receipt_id] = receipt

    def add_review_receipt(self, review: ReviewReceipt) -> None:
        """Add review receipt to audit trail."""
        self.reviews[review.review_id] = review

    def get_receipts_by_stage(self, stage: Stage) -> List[GateReceipt]:
        """Get all receipts for a specific lifecycle stage."""
        return [r for r in self.receipts.values() if r.stage == stage]

    def get_receipts_by_gate(self, gate_name: str) -> List[GateReceipt]:
        """Get all receipts for a specific gate."""
        return [r for r in self.receipts.values() if r.gate_name == gate_name]

    def get_reviews_for_receipt(self, receipt_id: str) -> List[ReviewReceipt]:
        """Get all reviews for a specific gate receipt."""
        return [r for r in self.reviews.values() if r.gate_receipt_id == receipt_id]

    def verify_integrity(self) -> bool:
        """Verify integrity of all stored receipts."""
        generator = GateReceiptGenerator()

        for receipt in self.receipts.values():
            if not generator.verify_receipt(receipt):
                return False

        return True

    def export_audit_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Export comprehensive audit report for regulatory compliance.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Structured audit report with compliance evidence
        """
        # Filter receipts by date range
        filtered_receipts = []
        for receipt in self.receipts.values():
            if start_date and receipt.timestamp < start_date:
                continue
            if end_date and receipt.timestamp > end_date:
                continue
            filtered_receipts.append(receipt)

        # Get associated reviews
        receipt_ids = {r.receipt_id for r in filtered_receipts}
        filtered_reviews = [r for r in self.reviews.values() if r.gate_receipt_id in receipt_ids]

        # Generate audit trail
        generator = GateReceiptGenerator()
        audit_trail = generator.get_audit_trail(filtered_receipts, filtered_reviews)

        # Add compliance summary
        audit_trail["compliance_summary"] = self._generate_compliance_summary(filtered_receipts)
        audit_trail["regulatory_evidence"] = self._generate_regulatory_evidence(filtered_receipts)

        return audit_trail

    def _generate_compliance_summary(self, receipts: List[GateReceipt]) -> Dict[str, Any]:
        """Generate compliance summary from receipts."""
        summary = {
            "total_evaluations": len(receipts),
            "pass_rate": 0,
            "fail_rate": 0,
            "review_rate": 0,
            "stages_covered": set(),
            "gates_evaluated": set(),
        }

        if receipts:
            pass_count = sum(1 for r in receipts if r.status == "PASS")
            fail_count = sum(1 for r in receipts if r.status == "FAIL")
            review_count = sum(1 for r in receipts if r.status == "REVIEW")

            total = len(receipts)
            summary["pass_rate"] = pass_count / total
            summary["fail_rate"] = fail_count / total
            summary["review_rate"] = review_count / total

            summary["stages_covered"] = list({r.stage.value for r in receipts})
            summary["gates_evaluated"] = list({r.gate_name for r in receipts})

        return summary

    def _generate_regulatory_evidence(self, receipts: List[GateReceipt]) -> Dict[str, Any]:
        """Generate regulatory evidence documentation."""
        evidence = {
            "cryptographic_proofs": [r.content_hash for r in receipts],
            "policy_versions": list({r.policy_version for r in receipts if r.policy_version}),
            "evidence_references": [],
            "audit_timestamps": [r.timestamp.isoformat() for r in receipts],
        }

        # Collect evidence references
        for receipt in receipts:
            evidence["evidence_references"].extend(receipt.evidence_refs)

        evidence["evidence_references"] = list(set(evidence["evidence_references"]))

        return evidence
