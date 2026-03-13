"""
CIAF Verification Microservice

External verification of AI-generated outputs using cryptographic proofs.
Provides REST API for output verification, audit trails, and compliance reports.

Created: 2025-03-13
Author: Denzil James Greenwood
Version: 0.1.0
"""

from .proof_store import PostgresProofStore
from .verification_service import (
    VerificationService,
    VerificationResult,
)
from .api import (
    create_verification_app,
    VerificationRequest,
    VerificationResponse,
    AuditAction,
    ComplianceReport,
    OrganizationStats,
)

__all__ = [
    "PostgresProofStore",
    "VerificationService",
    "VerificationResult",
    "create_verification_app",
    "VerificationRequest",
    "VerificationResponse",
    "AuditAction",
    "ComplianceReport",
    "OrganizationStats",
]

__version__ = "0.1.0"
