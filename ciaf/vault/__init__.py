"""
CIAF Vault - Enterprise-grade cryptographic proof custodian

Third-party independent verification infrastructure for AI governance.
Trusted vault for storing, managing, and verifying cryptographic proofs
of AI system outputs across regulated industries.

New Features:
- Evidence Manifest generation (legal standard for auditors)
- PDF Certificate export (verification certificates)
- ZIP Audit Package export (complete verification packages for external auditors)

Version: 1.0.0
Author: Denzil James Greenwood
"""

try:
    from .core import VaultManager, ProofReceipt, VerificationCertificate
    from .custody import CustodyManager, ImmutableProof
    from .audit import AuditLogger, AuditEntry
    from .authentication import APIKeyManager, Tenant
    from .manifest import EvidenceManifest, EvidenceManifestGenerator, EventType
    from .certificate_generator import CertificatePDFGenerator
    from .audit_package import AuditPackageGenerator
except ImportError:
    pass

__version__ = "1.0.0"
__all__ = [
    "VaultManager",
    "ProofReceipt",
    "VerificationCertificate",
    "CustodyManager",
    "ImmutableProof",
    "AuditLogger",
    "AuditEntry",
    "APIKeyManager",
    "Tenant",
    "EvidenceManifest",
    "EvidenceManifestGenerator",
    "EventType",
    "CertificatePDFGenerator",
    "AuditPackageGenerator",
]

