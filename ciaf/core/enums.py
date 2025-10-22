"""
Enums for the Cognitive Insight Audit Framework.

This module centralizes all enum definitions for record types, algorithms,
and other categorical constants used throughout the CIAF core.

Created: 2025-09-26
Author: Denzil James Greenwood
Version: 1.0.0
"""

from enum import Enum


class RecordType(str, Enum):
    """Types of audit records."""
    DATASET = "dataset"
    MODEL = "model"
    INFERENCE = "inference"
    ANCHOR = "anchor"
    MONITORING = "monitoring"
    COMPLIANCE = "compliance"


class HashAlgorithm(str, Enum):
    """Supported hash algorithms for algorithm agility."""
    SHA256 = "sha256"
    SHA3_256 = "sha3-256"
    BLAKE3 = "blake3"


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms."""
    ED25519 = "ed25519"  # Production default
    MOCK = "mock"        # Legacy/testing only ## DEPRECATED ## DO NOT USE


class ConsentStatus(str, Enum):
    """Standardized consent status values across CIAF."""
    
    # Active consent states
    GRANTED = "granted"
    ACTIVE = "active"
    VALID = "valid"
    
    # Negative consent states  
    DENIED = "denied"
    REFUSED = "refused"
    WITHDRAWN = "withdrawn"
    REVOKED = "revoked"
    
    # Pending/transitional states
    PENDING = "pending"
    REQUESTED = "requested"
    UNDER_REVIEW = "under_review"
    
    # Expired/invalid states
    EXPIRED = "expired"
    INVALID = "invalid"
    NOT_PROVIDED = "not_provided"
    
    # Unknown/error states
    UNKNOWN = "unknown"
    ERROR = "error"


class ConsentType(str, Enum):
    """Types of consent in different contexts."""
    
    # GDPR consent types
    EXPLICIT = "explicit"
    IMPLIED = "implied"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    
    # Age-specific consent
    PARENTAL = "parental"
    STUDENT = "student"
    GUARDIAN = "guardian"
    
    # Domain-specific consent
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    BIOMETRIC = "biometric"
    MEDICAL = "medical"
    RESEARCH = "research"


class ConsentScope(str, Enum):
    """Scope of consent application."""
    
    DATA_PROCESSING = "data_processing"
    DATA_SHARING = "data_sharing"
    MARKETING_COMMUNICATIONS = "marketing_communications"
    ANALYTICS_TRACKING = "analytics_tracking"
    BIOMETRIC_COLLECTION = "biometric_collection"
    RESEARCH_PARTICIPATION = "research_participation"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PERSONALIZATION = "personalization"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"
    CROSS_BORDER_TRANSFER = "cross_border_transfer"