"""Type definitions for CIAF Client."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    PENDING = "pending"
    FAILED = "failed"


@dataclass
class VerificationResult:
    tag_id: str
    status: VerificationStatus
    risk_level: RiskLevel
    verified_at: datetime
    agents: List[str]
    policies: List[str]
    merkle_proof_valid: bool
    content_hash: str
    issues: List[str]
    warnings: List[str]


@dataclass
class AuditAction:
    action_id: str
    agent_id: str
    action_type: str
    resource: str
    timestamp: datetime
    status: str
    details: Dict[str, Any]


@dataclass
class ComplianceReport:
    organization_id: str
    period_start: datetime
    period_end: datetime
    total_outputs: int
    verified_outputs: int
    compliance_rate: float
    high_risk_count: int
    critical_count: int
    policies_covered: List[str]
    gaps: List[str]
