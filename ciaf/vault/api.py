"""
CIAF Vault API - Enterprise-grade REST endpoints for cryptographic proof custody.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .core import VaultManager, ProofReceipt, VerificationCertificate
from .audit import AuditLogger, AuditEntry
from .authentication import APIKeyManager, Tenant


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SubmitProofRequest(BaseModel):
    """Request to submit proof to vault."""
    content: str = Field(..., description="Proof content")
    agent_ids: List[str] = Field(..., description="Agents involved")
    policies_applied: List[str] = Field(..., description="Policies applied")
    timestamp: str = Field(..., description="ISO timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProofResponse(BaseModel):
    """Response from vault operations."""
    proof_id: str
    organization_id: str
    timestamp: str
    verified: bool
    read_count: int


class ReceiptResponse(BaseModel):
    """API receipt for submitted proof."""
    receipt_id: str
    proof_id: str
    organization_id: str
    timestamp: str
    verification_url: str


class CertificateResponse(BaseModel):
    """Verification certificate response."""
    certificate_id: str
    proof_id: str
    generated_at: str
    valid_until: str
    issuer: str


class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    entry_id: str
    action: str
    timestamp: str
    result: str


class VaultStatsResponse(BaseModel):
    """Vault statistics."""
    total_proofs: int
    total_organizations: int
    active_organizations: int
    total_reads: int


# ============================================================================
# VAULT API APPLICATION
# ============================================================================

def create_vault_api() -> FastAPI:
    """Create vault API application."""
    app = FastAPI(
        title="CIAF Vault API",
        description="Enterprise cryptographic proof custodian",
        version="1.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize vault components
    vault = VaultManager()
    audit = AuditLogger()
    auth = APIKeyManager()

    # ========================================================================
    # AUTHENTICATION MIDDLEWARE
    # ========================================================================

    async def verify_api_key(authorization: Optional[str] = Header(None)):
        """Verify API key from Authorization header."""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing API key")

        api_key = authorization.replace("Bearer ", "")
        result = auth.verify_api_key(api_key)

        if not result:
            raise HTTPException(status_code=401, detail="Invalid API key")

        return result

    # ========================================================================
    # HEALTH & STATUS
    # ========================================================================

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        """Health check."""
        return {
            "status": "healthy",
            "service": "CIAF Vault",
            "version": "1.0.0"
        }

    @app.get("/stats")
    async def stats() -> VaultStatsResponse:
        """Get vault statistics."""
        stats_data = vault.get_vault_stats()
        return VaultStatsResponse(**stats_data)

    # ========================================================================
    # PROOF SUBMISSION
    # ========================================================================

    @app.post("/submit", response_model=ReceiptResponse)
    async def submit_proof(
        request: SubmitProofRequest,
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ) -> ReceiptResponse:
        """
        Submit proof to vault (WORM).

        Proof becomes immutable after submission.
        Returns verification receipt and URL.
        """
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            # Submit to vault
            receipt = vault.submit_proof(
                organization_id=org_id,
                content=request.content,
                agent_ids=request.agent_ids,
                policies_applied=request.policies_applied,
                timestamp=request.timestamp
            )

            # Log action
            audit.log_action(
                entry_id=entry_id,
                action="submit_proof",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={
                    "proof_id": receipt.proof_id,
                    "agent_count": len(request.agent_ids),
                    "policy_count": len(request.policies_applied)
                },
                proof_id=receipt.proof_id,
                ip_address=client_request.client.host if client_request else None
            )

            return ReceiptResponse(
                receipt_id=receipt.receipt_id,
                proof_id=receipt.proof_id,
                organization_id=receipt.organization_id,
                timestamp=receipt.timestamp,
                verification_url=receipt.verification_url
            )

        except Exception as e:
            # Log failure
            audit.log_action(
                entry_id=entry_id,
                action="submit_proof",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                ip_address=client_request.client.host if client_request else None
            )
            raise HTTPException(status_code=400, detail=str(e))

    # ========================================================================
    # PROOF VERIFICATION
    # ========================================================================

    @app.get("/verify/{proof_id}", response_model=ProofResponse)
    async def verify_proof(
        proof_id: str,
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ) -> ProofResponse:
        """
        Verify proof from vault (read-only).

        Increments read counter for audit trail.
        Returns proof details if valid.
        """
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            # Verify proof
            proof = vault.verify_proof(proof_id, org_id)

            if not proof:
                raise HTTPException(status_code=404, detail="Proof not found")

            # Log action
            audit.log_action(
                entry_id=entry_id,
                action="verify_proof",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={"read_count": proof.read_count},
                proof_id=proof_id,
                ip_address=client_request.client.host if client_request else None
            )

            return ProofResponse(
                proof_id=proof.proof_id,
                organization_id=proof.organization_id,
                timestamp=proof.timestamp,
                verified=proof.verified,
                read_count=proof.read_count
            )

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="verify_proof",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                proof_id=proof_id,
                ip_address=client_request.client.host if client_request else None
            )
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # CERTIFICATE GENERATION
    # ========================================================================

    @app.post("/certificate/{proof_id}", response_model=CertificateResponse)
    async def generate_certificate(
        proof_id: str,
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ) -> CertificateResponse:
        """Generate verification certificate for proof."""
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            # Verify proof exists
            proof = vault.verify_proof(proof_id, org_id)
            if not proof:
                raise HTTPException(status_code=404, detail="Proof not found")

            # Generate certificate
            cert = vault.generate_certificate(proof_id, org_id)

            # Log action
            audit.log_action(
                entry_id=entry_id,
                action="generate_certificate",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={"certificate_id": cert.certificate_id},
                proof_id=proof_id,
                ip_address=client_request.client.host if client_request else None
            )

            return CertificateResponse(
                certificate_id=cert.certificate_id,
                proof_id=cert.proof_id,
                generated_at=cert.generated_at,
                valid_until=cert.valid_until,
                issuer=cert.issuer
            )

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="generate_certificate",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                proof_id=proof_id,
                ip_address=client_request.client.host if client_request else None
            )
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # AUDIT TRAIL
    # ========================================================================

    @app.get("/audit-trail")
    async def get_audit_trail(
        start_time: Optional[str] = Query(None),
        end_time: Optional[str] = Query(None),
        action: Optional[str] = Query(None),
        limit: int = Query(100),
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ) -> Dict[str, Any]:
        """Get audit trail for organization."""
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            entries = audit.get_audit_trail(
                org_id,
                start_time=start_time,
                end_time=end_time,
                action_filter=action,
                limit=limit
            )

            audit.log_action(
                entry_id=entry_id,
                action="query_audit_trail",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={"entry_count": len(entries)},
                ip_address=client_request.client.host if client_request else None
            )

            return {
                "entries": [e.to_dict() for e in entries],
                "total": len(entries),
                "organization_id": org_id
            }

        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="query_audit_trail",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                ip_address=client_request.client.host if client_request else None
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/audit-summary")
    async def audit_summary(
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ) -> Dict[str, Any]:
        """Get audit summary for organization."""
        org_id, key_id = api_key_result

        summary = audit.get_audit_summary(org_id)
        return {
            "organization_id": org_id,
            "summary": summary
        }

    # ========================================================================
    # ORGANIZATION / TENANT ENDPOINTS
    # ========================================================================

    @app.get("/organization")
    async def get_organization(
        api_key_result: tuple = Depends(verify_api_key)
    ) -> Dict[str, Any]:
        """Get organization details."""
        org_id, key_id = api_key_result
        org = auth.get_organization(org_id)

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        return {
            "org_id": org.org_id,
            "name": org.name,
            "created_at": org.created_at,
            "api_key_count": org.api_key_count,
            "last_activity": org.last_activity
        }

    @app.get("/organization/proofs")
    async def get_organization_proofs(
        start_time: Optional[str] = Query(None),
        end_time: Optional[str] = Query(None),
        limit: int = Query(100),
        api_key_result: tuple = Depends(verify_api_key)
    ) -> Dict[str, Any]:
        """Get all proofs for organization."""
        org_id, key_id = api_key_result

        proofs = vault.get_organization_proofs(
            org_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        return {
            "organization_id": org_id,
            "proofs": [p.to_dict() for p in proofs],
            "total": len(proofs)
        }

    return app


# Create singleton instance
vault_api = create_vault_api()
