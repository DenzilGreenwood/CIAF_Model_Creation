"""
CIAF Vault API - Enterprise-grade REST endpoints for cryptographic proof custody.
"""

import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field

from .core import VaultManager, ProofReceipt, VerificationCertificate
from .audit import AuditLogger, AuditEntry
from .authentication import APIKeyManager, Tenant
from .manifest import EvidenceManifestGenerator, EventType
from .certificate_generator import CertificatePDFGenerator
from .audit_package import AuditPackageGenerator
from ciaf.verification.rate_limiting import RateLimitMiddleware


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


class PublicKeyResponse(BaseModel):
    """Public key for signature verification."""
    key_id: str
    algorithm: str
    public_key_pem: str
    valid_from: str
    valid_until: str


class KeyRotationResponse(BaseModel):
    """Key rotation result."""
    new_version: str
    old_version: str
    rotated_at: str
    reason: str
    public_key_pem: str


class KeyVersionResponse(BaseModel):
    """Key version info."""
    key_version: str
    created_at: str
    rotated_at: Optional[str]
    is_active: int
    reason: Optional[str]


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

    # Rate Limiting (DoS protection)
    app.add_middleware(
        RateLimitMiddleware,
        global_limit=1000,      # 1000 requests/minute globally
        org_limit=100,          # 100 requests/minute per organization
        user_limit=30,          # 30 requests/minute per user
        window_seconds=60
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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
                ip_address=client_request.client.host if (client_request and client_request.client) else None
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

    # ========================================================================
    # EXPORT & DOWNLOADS
    # ========================================================================

    @app.get("/export/manifest/{proof_id}.json")
    async def export_manifest(
        proof_id: str,
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ) -> Dict[str, Any]:
        """
        Export Evidence Manifest for a proof (JSON).

        Evidence Manifest is the standardized format for legal/auditor teams
        to verify proofs independently without CIAF system access.

        Legal admissibility:
        ✅ Federal Rule 901 (Authentication)
        ✅ Federal Rule 902 (Self-Authenticating)
        ✅ Daubert Standard (Scientific reliability)
        ✅ Chain of Custody (Unbroken evidence trail)
        """
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            # Retrieve proof
            proof = vault.verify_proof(proof_id, org_id)
            if not proof:
                raise HTTPException(status_code=404, detail="Proof not found")

            # Create Evidence Manifest
            manifest = EvidenceManifestGenerator.create_manifest(
                event_type=EventType.INFERENCE_DECISION,
                subject_identity=f"urn:ciaf:proof:{proof_id}",
                payload_hash=proof.content_hash,
                merkle_root=proof.merkle_root or "",
                metadata={
                    "timestamp": proof.timestamp,
                    "created_at": proof.created_at,
                    "read_count": proof.read_count,
                },
                organization_id=org_id,
                proof_id=proof_id,
            )

            # Log action
            audit.log_action(
                entry_id=entry_id,
                action="export_manifest",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={"manifest_id": manifest.manifest_id},
                proof_id=proof_id,
                ip_address=client_request.client.host if (client_request and client_request.client) else None
            )

            return manifest.to_dict()

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="export_manifest",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                proof_id=proof_id,
                ip_address=client_request.client.host if (client_request and client_request.client) else None
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/export/certificate/{proof_id}.pdf")
    async def export_certificate_pdf(
        proof_id: str,
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ):
        """
        Export verification certificate as PDF.

        PDF includes:
        - Certificate metadata and validity dates
        - Proof details (hash, timestamp)
        - Issuer signature information
        - QR code for verification URL
        - Legal admissibility statement

        Designed for auditors, legal teams, and compliance officers.
        """
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            # Retrieve proof and certificate
            proof = vault.verify_proof(proof_id, org_id)
            if not proof:
                raise HTTPException(status_code=404, detail="Proof not found")

            cert = vault.generate_certificate(proof_id, org_id)

            # Generate PDF
            pdf_generator = CertificatePDFGenerator()
            pdf_bytes = pdf_generator.generate_certificate_pdf(
                certificate_id=cert.certificate_id,
                proof_id=proof_id,
                organization_id=org_id,
                content_hash=proof.content_hash,
                issued_at=cert.generated_at,
                valid_until=cert.valid_until,
                verification_url=f"https://vault.ciaf.io/verify/{proof_id}",
                signature=cert.signature,
                merkle_root=proof.merkle_root,
                read_count=proof.read_count,
            )

            # Log action
            audit.log_action(
                entry_id=entry_id,
                action="export_certificate_pdf",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={"certificate_id": cert.certificate_id},
                proof_id=proof_id,
                ip_address=client_request.client.host if (client_request and client_request.client) else None
            )

            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=certificate-{proof_id}.pdf"
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="export_certificate_pdf",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                proof_id=proof_id,
                ip_address=client_request.client.host if (client_request and client_request.client) else None
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/export/audit-package")
    async def export_audit_package(
        start_time: Optional[str] = Query(None),
        end_time: Optional[str] = Query(None),
        limit: int = Query(100),
        api_key_result: tuple = Depends(verify_api_key),
        client_request: Request = None
    ):
        """
        Export complete audit package as ZIP for external verification.

        ZIP package includes:
        - manifest.json (Evidence Manifest for each proof)
        - certificates/ (PDF verification certificates)
        - proofs/ (JSON proof batches)
        - audit-trail.json (Immutable audit logs)
        - verification-scripts/ (Python/Bash scripts for auditors)
        - metadata.json (Package information)

        Auditors can extract and run verification scripts independently
        without connecting to CIAF systems.

        Package structure enables:
        ✅ Hash verification (SHA-256 integrity)
        ✅ Merkle tree verification (batch completeness)
        ✅ Signature verification (Ed25519 non-repudiation)
        ✅ Chain of custody proof
        ✅ Federal Rules of Evidence compliance
        """
        org_id, key_id = api_key_result
        entry_id = str(uuid.uuid4())

        try:
            # Retrieve organization proofs
            proofs = vault.get_organization_proofs(
                org_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )

            if not proofs:
                raise HTTPException(status_code=404, detail="No proofs found for organization")

            # Retrieve audit trail
            audit_entries = audit.get_audit_trail(
                org_id,
                start_time=start_time,
                end_time=end_time,
                limit=1000
            )

            # Generate manifests and certificates
            manifests = {}
            certificates = {}
            proof_dicts = []

            for proof in proofs:
                # Create manifest
                manifest = EvidenceManifestGenerator.create_manifest(
                    event_type=EventType.INFERENCE_DECISION,
                    subject_identity=f"urn:ciaf:proof:{proof.proof_id}",
                    payload_hash=proof.content_hash,
                    merkle_root=proof.merkle_root or "",
                    metadata={
                        "timestamp": proof.timestamp,
                        "created_at": proof.created_at,
                        "read_count": proof.read_count,
                    },
                    organization_id=org_id,
                    proof_id=proof.proof_id,
                )
                manifests[proof.proof_id] = manifest.to_dict()

                # Generate certificate
                cert = vault.generate_certificate(proof.proof_id, org_id)
                pdf_generator = CertificatePDFGenerator()
                cert_pdf = pdf_generator.generate_certificate_pdf(
                    certificate_id=cert.certificate_id,
                    proof_id=proof.proof_id,
                    organization_id=org_id,
                    content_hash=proof.content_hash,
                    issued_at=cert.generated_at,
                    valid_until=cert.valid_until,
                    verification_url=f"https://vault.ciaf.io/verify/{proof.proof_id}",
                    signature=cert.signature,
                    merkle_root=proof.merkle_root,
                    read_count=proof.read_count,
                )
                certificates[proof.proof_id] = cert_pdf

                # Add proof to list
                proof_dicts.append(proof.to_dict())

            # Get vault public key for signature verification
            public_key_pem = vault.get_public_key_pem()

            # Generate audit package ZIP
            zip_bytes = AuditPackageGenerator.create_audit_package(
                organization_id=org_id,
                proofs=proof_dicts,
                audit_trail=[e.to_dict() for e in audit_entries],
                certificates=certificates,
                manifests=manifests,
                public_key_pem=public_key_pem,
                metadata={
                    "organization_id": org_id,
                    "proof_count": len(proofs),
                    "time_period": {
                        "start": start_time,
                        "end": end_time,
                    }
                }
            )

            # Log action
            audit.log_action(
                entry_id=entry_id,
                action="export_audit_package",
                organization_id=org_id,
                actor=key_id,
                result="success",
                details={
                    "proof_count": len(proofs),
                    "file_size_bytes": len(zip_bytes),
                },
                ip_address=client_request.client.host if (client_request and client_request.client) else None
            )

            return StreamingResponse(
                iter([zip_bytes]),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=ciaf-audit-package-{org_id}.zip"
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="export_audit_package",
                organization_id=org_id,
                actor=key_id,
                result="failure",
                details={"error": str(e)},
                ip_address=client_request.client.host if (client_request and client_request.client) else None
            )
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # KEY MANAGEMENT ENDPOINTS
    # ========================================================================

    @app.get("/public-key", response_model=PublicKeyResponse)
    async def get_public_key() -> PublicKeyResponse:
        """
        Get vault's public key for independent signature verification.

        This endpoint allows auditors and external systems to verify all
        signatures issued by this vault without relying on CIAF systems.

        Returns:
            PublicKeyResponse with vault's public key and metadata
        """
        entry_id = str(uuid.uuid4())
        try:
            public_pem = vault.get_public_key_pem()
            key_version = vault.get_key_version()

            audit.log_action(
                entry_id=entry_id,
                action="export_public_key",
                organization_id="system",
                actor="public",
                result="success",
                details={"key_version": key_version}
            )

            return PublicKeyResponse(
                key_id=f"vault-key-{key_version}",
                algorithm="Ed25519",
                public_key_pem=public_pem,
                valid_from=datetime.now().isoformat(),
                valid_until="2099-12-31T23:59:59Z"  # Long validity for public key
            )
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="export_public_key",
                organization_id="system",
                actor="public",
                result="failure",
                details={"error": str(e)}
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/admin/rotate-key", response_model=KeyRotationResponse)
    async def rotate_signing_key(
        api_key: str = Header(...),
        reason: str = Query(default="Scheduled rotation")
    ) -> KeyRotationResponse:
        """
        Rotate vault's signing key to a new version (admin-only).

        This endpoint requires admin API key and should only be called
        by authorized administrators during maintenance windows.

        Args:
            api_key: Admin API key for authentication
            reason: Reason for key rotation

        Returns:
            KeyRotationResponse with new key version and public key
        """
        entry_id = str(uuid.uuid4())
        try:
            # Validate admin key (in production, check against admin key store)
            if not api_key.startswith("admin-"):
                raise HTTPException(status_code=403, detail="Admin key required")

            result = vault.rotate_key(reason=reason)

            audit.log_action(
                entry_id=entry_id,
                action="rotate_key",
                organization_id="system",
                actor="admin",
                result="success",
                details={
                    "new_version": result["new_version"],
                    "reason": reason
                }
            )

            return KeyRotationResponse(**result)

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="rotate_key",
                organization_id="system",
                actor="admin",
                result="failure",
                details={"error": str(e)}
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/admin/key-versions", response_model=List[KeyVersionResponse])
    async def list_key_versions(api_key: str = Header(...)) -> List[KeyVersionResponse]:
        """
        Get all key versions and their status (admin-only).

        Returns:
            List of key versions with metadata
        """
        entry_id = str(uuid.uuid4())
        try:
            if not api_key.startswith("admin-"):
                raise HTTPException(status_code=403, detail="Admin key required")

            versions = vault.get_key_versions()

            audit.log_action(
                entry_id=entry_id,
                action="list_key_versions",
                organization_id="system",
                actor="admin",
                result="success",
                details={"version_count": len(versions)}
            )

            return [KeyVersionResponse(**v) for v in versions]

        except HTTPException:
            raise
        except Exception as e:
            audit.log_action(
                entry_id=entry_id,
                action="list_key_versions",
                organization_id="system",
                actor="admin",
                result="failure",
                details={"error": str(e)}
            )
            raise HTTPException(status_code=500, detail=str(e))

    return app


# Create singleton instance
vault_api = create_vault_api()
