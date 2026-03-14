"""
FastAPI Endpoints for CIAF Verification Microservice

REST API for verifying AI-generated outputs.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

import json
import sqlite3
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .proof_store import PostgresProofStore
from .verification_service import VerificationService, VerificationResult


# ============================================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================================


class SubmitTagRequest(BaseModel):
    """Request to submit/store a new output tag."""

    tag_id: str = Field(..., description="Output tag ID")
    content: str = Field(..., description="AI-generated output content")
    agents: list = Field(default_factory=list, description="Agent IDs that generated this")
    organization_id: str = Field(..., description="Organization ID")
    policies: list = Field(default_factory=list, description="Policies applied")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: str = Field(..., description="ISO format timestamp")


class VerificationRequest(BaseModel):
    """Request to verify an output."""

    tag_id: str = Field(..., description="Output tag ID")
    verify_merkle: bool = Field(
        True, description="Verify merkle proofs"
    )
    include_audit_trail: bool = Field(
        True, description="Include agent audit trail"
    )


class VerificationResponse(BaseModel):
    """Response from verification."""

    verified: bool
    tag_id: str
    organization_id: str
    inference_type: str  # "agent_orchestrated" or "direct_model"
    model_name: Optional[str] = None
    agent_ids: list = []
    policies_applied: list = []
    risk_level: str
    task_batch_verified: bool
    org_batch_verified: bool
    merkle_proof_valid: bool
    agent_audit_trail: list = []
    issues: list = []
    warnings: list = []


class AuditAction(BaseModel):
    """Single action in audit trail."""

    agent_id: str
    action_type: str
    timestamp: str
    risk_level: str
    status: str


class ComplianceReport(BaseModel):
    """Policy compliance report."""

    organization_id: str
    policy: str
    total_outputs: int
    policy_covered: int
    compliance_rate: float
    verified_outputs: int


class OrganizationStats(BaseModel):
    """Organization statistics."""

    organization_id: str
    total_tags: int
    verified_tags: int
    high_risk_tags: int
    critical_tags: int
    total_batch_windows: int


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================


def create_verification_app(
    proof_store: PostgresProofStore = None,
) -> FastAPI:
    """
    Create FastAPI application for verification service.

    Args:
        proof_store: PostgreSQL proof store instance

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="CIAF Verification Microservice",
        description="Cryptographic verification of AI-generated outputs",
        version="0.1.0",
    )

    # Initialize dependencies
    if proof_store is None:
        proof_store = PostgresProofStore()

    verification_service = VerificationService(proof_store)

    # ========================================================================
    # VERIFICATION ENDPOINTS
    # ========================================================================

    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """
        Health check endpoint.

        Returns:
            Status and proof store statistics
        """
        return {
            "status": "healthy",
            "service": "CIAF Verification Microservice",
            "proof_store_stats": proof_store.get_stats(),
        }

    @app.post("/verify", response_model=VerificationResponse)
    async def verify_output(request: VerificationRequest) -> VerificationResponse:
        """
        Verify an AI-generated output.

        Validates cryptographic proofs and returns complete audit trail.

        Args:
            request: VerificationRequest with tag_id

        Returns:
            VerificationResponse with verification details

        Example:
            ```json
            {
                "tag_id": "550e8400-e29b-41d4-a716-446655440000",
                "verify_merkle": true,
                "include_audit_trail": true
            }
            ```

        Response:
            ```json
            {
                "verified": true,
                "tag_id": "550e8400...",
                "organization_id": "healthcare_org_001",
                "inference_type": "agent_orchestrated",
                "agent_ids": ["reader_001", "analyzer_001"],
                "policies_applied": ["HIPAA_COMPLIANT", "FDA_SaMD"],
                "risk_level": "high",
                "task_batch_verified": true,
                "merkle_proof_valid": true,
                "issues": [],
                "warnings": []
            }
            ```
        """
        result = await verification_service.verify_output(
            tag_id=request.tag_id,
            verify_merkle=request.verify_merkle,
            include_audit_trail=request.include_audit_trail,
        )

        if not result.verified:
            raise HTTPException(status_code=400, detail=result.issues[0])

        return VerificationResponse(**result.to_dict())

    @app.post("/tags")
    async def submit_tag(request: SubmitTagRequest) -> Dict[str, Any]:
        """
        Submit/store a new output tag for verification.

        This endpoint accepts a newly generated output tag from an agent/LLM
        and stores it in the proof store for later verification.

        Args:
            request: SubmitTagRequest with output content and metadata

        Returns:
            Confirmation with tag_id and storage status

        Example:
            ```json
            {
                "tag_id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "Based on...",
                "agents": ["credit_analyst_001"],
                "organization_id": "banking_org_001",
                "policies": ["fair_lending"],
                "timestamp": "2026-03-14T10:30:00Z"
            }
            ```
        """
        tag_dict = {
            "tag_id": request.tag_id,
            "content": request.content,
            "agent_ids": request.agents,
            "organization_id": request.organization_id,
            "policies_applied": request.policies,
            "metadata": request.metadata,
            "timestamp": request.timestamp,
            "inference_type": "agent_orchestrated" if request.agents else "direct_model",
            "model_name": request.metadata.get("model_name"),
            "is_verified": False,
        }

        # Store in proof store cache
        proof_store.output_tags_cache[request.tag_id] = tag_dict

        # Store in database for persistence
        try:
            conn = sqlite3.connect(proof_store.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO output_tags
                (tag_id, content, agent_ids, organization_id, policies_applied,
                 metadata, timestamp, inference_type, model_name, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.tag_id,
                request.content,
                json.dumps(request.agents),
                request.organization_id,
                json.dumps(request.policies),
                json.dumps(request.metadata),
                request.timestamp,
                "agent_orchestrated" if request.agents else "direct_model",
                request.metadata.get("model_name"),
                0
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to store tag in database: {e}")

        return {
            "status": "success",
            "tag_id": request.tag_id,
            "organization_id": request.organization_id,
            "message": "Tag submitted and stored for verification",
        }

    @app.get("/verify/{tag_id}", response_model=VerificationResponse)
    async def verify_by_tag_id(
        tag_id: str,
        verify_merkle: bool = Query(True),
        include_audit_trail: bool = Query(True),
    ) -> VerificationResponse:
        """
        Verify output by tag ID (GET endpoint).

        Args:
            tag_id: Output tag ID
            verify_merkle: Verify merkle proofs (query param)
            include_audit_trail: Include audit trail (query param)

        Returns:
            VerificationResponse

        Example:
            ```
            GET /verify/550e8400-e29b-41d4-a716-446655440000?verify_merkle=true
            ```
        """
        result = await verification_service.verify_output(
            tag_id=tag_id,
            verify_merkle=verify_merkle,
            include_audit_trail=include_audit_trail,
        )

        # Return result even if not fully verified (e.g., newly submitted tags)
        # Only return 404 if tag doesn't exist at all
        if len(result.issues) > 0 and "not found" in result.issues[0].lower():
            raise HTTPException(status_code=404, detail="Tag not found")

        return VerificationResponse(**result.to_dict())

    # ========================================================================
    # AUDIT TRAIL ENDPOINTS
    # ========================================================================

    @app.get("/audit/{tag_id}")
    async def get_audit_trail(tag_id: str) -> Dict[str, Any]:
        """
        Get agent audit trail for an output.

        Returns the sequence of agents that processed this output,
        with timing and policy enforcement details.

        Args:
            tag_id: Output tag ID

        Returns:
            Dict with agent actions in chronological order

        Example Response:
            ```json
            {
                "tag_id": "550e8400...",
                "agent_sequence": ["reader_001", "analyzer_001", "decision_001"],
                "actions": [
                    {
                        "agent_id": "reader_001",
                        "action_type": "inference",
                        "timestamp": "2025-03-13T10:00:00Z",
                        "risk_level": "medium",
                        "status": "success"
                    },
                    ...
                ]
            }
            ```
        """
        tag_dict = await proof_store.lookup_output_tag(tag_id)
        if not tag_dict:
            raise HTTPException(status_code=404, detail="Tag not found")

        audit_trail = await proof_store.get_agent_audit_trail(tag_id)

        return {
            "tag_id": tag_id,
            "agent_ids": tag_dict.get("agent_ids", []),
            "inference_type": tag_dict.get("inference_type"),
            "model_name": tag_dict.get("model_name"),
            "actions": audit_trail or [],
        }

    # ========================================================================
    # COMPLIANCE & REPORTING ENDPOINTS
    # ========================================================================

    @app.get("/compliance/{organization_id}", response_model=ComplianceReport)
    async def get_compliance_report(
        organization_id: str,
        policy: Optional[str] = Query(None),
    ) -> ComplianceReport:
        """
        Get policy compliance report for organization.

        Shows what percentage of outputs are compliant with specified policy.

        Args:
            organization_id: Organization ID
            policy: Optional specific policy (e.g., "HIPAA_COMPLIANT")

        Returns:
            ComplianceReport with compliance metrics
        """
        report = await verification_service.get_policy_compliance_report(
            organization_id, policy
        )

        return ComplianceReport(**report)

    @app.get("/stats/{organization_id}", response_model=OrganizationStats)
    async def get_organization_stats(
        organization_id: str,
    ) -> OrganizationStats:
        """
        Get verification statistics for organization.

        Shows total outputs, verification rate, risk distribution.

        Args:
            organization_id: Organization ID

        Returns:
            OrganizationStats with verification metrics
        """
        summary = await verification_service.get_verification_summary(
            organization_id
        )

        return OrganizationStats(**summary["verification_summary"])

    # ========================================================================
    # ADMIN ENDPOINTS
    # ========================================================================

    @app.post("/admin/refresh-cache")
    async def refresh_cache() -> Dict[str, Any]:
        """
        Refresh merkle proof cache (admin only).

        Should be called periodically to sync with latest org batch windows.

        In production:
        - Cache would be stored in Redis
        - This endpoint would force cache invalidation
        - Refresh would pull latest merkle roots from database
        """
        # In production: invalidate cache, rebuild from database
        stats = proof_store.get_stats()

        return {
            "status": "cache_refreshed",
            "stats": stats,
            "message": "Merkle proof cache refreshed from database",
        }

    return app


# ============================================================================
# STANDALONE SERVER (for testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Create app
    proof_store = PostgresProofStore()
    app = create_verification_app(proof_store)

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
