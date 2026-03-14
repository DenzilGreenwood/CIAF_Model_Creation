"""
CIAF Vault - Enterprise-grade cryptographic proof custodian

Third-party independent verification infrastructure for AI governance.
Trusted vault for storing, managing, and verifying cryptographic proofs
of AI system outputs across regulated industries.

Version: 1.0.0
Author: Denzil James Greenwood
"""

try:
    from .core import VaultManager, ProofReceipt, VerificationCertificate
    from .custody import CustodyManager, ImmutableProof
    from .audit import AuditLogger, AuditEntry
    from .authentication import APIKeyManager, Tenant
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
]

