"""
Core interfaces and data structures for the CIAF Compliance Gates System.

This module defines the fundamental protocols and types used throughout the gate system,
providing a consistent interface for policy-driven ML lifecycle governance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union
from datetime import datetime
import numpy as np
import pandas as pd


class GateStatus(Enum):
    """Normative gate evaluation outcomes with clear pass/fail semantics."""

    PASS = "PASS"  # Compliance criteria satisfied, operation may proceed
    WARN = "WARN"  # Minor issues detected, proceed with caution/monitoring
    FAIL = "FAIL"  # Critical compliance violation, block operation
    REVIEW = "REVIEW"  # Human oversight required, escalate to reviewer


class Stage(Enum):
    """ML lifecycle stages where compliance gates are enforced."""

    DATASET = "dataset"  # Data ingestion and preprocessing
    TRAINING = "training"  # Model training and validation
    PRE_DEPLOYMENT = "pre_deployment"  # Pre-release validation and testing
    INFERENCE = "inference"  # Production inference operations


@dataclass
class OperationContext:
    """
    Comprehensive context object passed to gates for evaluation.

    Contains all necessary information for compliance assessment including
    model artifacts, data characteristics, regulatory requirements, and
    operational metadata.
    """

    # Stage and operation metadata
    stage: Stage
    operation_id: str
    timestamp: datetime
    model_id: Optional[str] = None
    dataset_id: Optional[str] = None

    # Model artifacts and metrics
    model_artifacts: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    training_metadata: Dict[str, Any] = field(default_factory=dict)

    # Data characteristics
    data_schema: Optional[Dict[str, Any]] = None
    data_statistics: Dict[str, Any] = field(default_factory=dict)
    sensitive_attributes: List[str] = field(default_factory=list)

    # Compliance context
    regulatory_frameworks: List[str] = field(default_factory=list)
    risk_classification: Optional[str] = None
    stakeholder_requirements: Dict[str, Any] = field(default_factory=dict)

    # Previous gate results for dependency checking
    previous_results: Dict[str, "GateResult"] = field(default_factory=dict)

    # Additional context for specialized gates
    custom_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    """
    Comprehensive gate evaluation result with cryptographic evidence.

    Contains evaluation outcome, detailed metrics, evidence references,
    and cryptographic proof for audit trail generation.
    """

    # Core evaluation outcome
    status: GateStatus
    gate_name: str
    timestamp: datetime

    # Detailed evaluation metrics and evidence
    metrics: Dict[str, Union[float, int, str, bool]] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)

    # Compliance details
    policy_version: Optional[str] = None
    thresholds_applied: Dict[str, float] = field(default_factory=dict)
    regulatory_alignment: Dict[str, str] = field(default_factory=dict)

    # Remediation and recommendations
    recommendations: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    escalation_required: bool = False

    # HITL and review context
    reviewer_required: bool = False
    review_priority: Optional[str] = None
    review_deadline: Optional[datetime] = None

    # Cryptographic attestation
    evidence_hash: Optional[str] = None
    signature: Optional[str] = None
    merkle_path: Optional[List[str]] = None

    # Error handling
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None


class ComplianceGate(Protocol):
    """
    Protocol defining the interface for all compliance gates.

    Provides consistent evaluation interface while allowing flexible
    implementation of specialized compliance checks across different
    domains (bias, explainability, uncertainty, etc.).
    """

    name: str
    description: str
    version: str
    supported_stages: List[Stage]

    def evaluate(self, ctx: OperationContext) -> GateResult:
        """
        Evaluate compliance criteria against the provided operation context.

        Args:
            ctx: Complete operation context with model artifacts, data, and metadata

        Returns:
            GateResult with evaluation outcome, metrics, and evidence

        Raises:
            GateEvaluationError: If evaluation cannot be completed
        """
        ...

    def validate_context(self, ctx: OperationContext) -> bool:
        """
        Validate that the operation context contains required information.

        Args:
            ctx: Operation context to validate

        Returns:
            True if context is valid for this gate
        """
        ...

    def get_required_artifacts(self) -> List[str]:
        """
        Get list of required artifacts/metrics for this gate.

        Returns:
            List of required artifact keys
        """
        ...


class PolicyDrivenGate(ComplianceGate, Protocol):
    """
    Extended protocol for gates that support policy-driven configuration.

    Allows runtime configuration of thresholds, enabled checks, and
    enforcement actions without modifying gate implementation code.
    """

    def configure(self, policy_config: Dict[str, Any]) -> None:
        """
        Configure gate behavior based on policy settings.

        Args:
            policy_config: Policy configuration dictionary
        """
        ...

    def get_configuration_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for policy configuration options.

        Returns:
            JSON schema describing valid configuration parameters
        """
        ...


@dataclass
class GateConfiguration:
    """Configuration settings for individual gates within a policy."""

    gate_name: str
    enabled: bool = True
    thresholds: Dict[str, float] = field(default_factory=dict)
    enforcement_action: str = "block"  # block, warn, escalate
    required_reviewers: List[str] = field(default_factory=list)
    escalation_window_hours: int = 24
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StagePolicy:
    """Policy configuration for a specific ML lifecycle stage."""

    stage: Stage
    enabled_gates: List[str] = field(default_factory=list)
    gate_configurations: Dict[str, GateConfiguration] = field(default_factory=dict)
    enforcement_level: str = "strict"  # strict, permissive, advisory
    parallel_execution: bool = True
    fail_fast: bool = False
    audit_requirements: Dict[str, Any] = field(default_factory=dict)


class GateEvaluationError(Exception):
    """Exception raised when gate evaluation cannot be completed."""

    def __init__(self, gate_name: str, message: str, context: Optional[Dict[str, Any]] = None):
        self.gate_name = gate_name
        self.context = context or {}
        super().__init__(f"Gate '{gate_name}' evaluation failed: {message}")


class PolicyValidationError(Exception):
    """Exception raised when policy configuration is invalid."""

    def __init__(self, message: str, policy_section: Optional[str] = None):
        self.policy_section = policy_section
        super().__init__(f"Policy validation failed: {message}")


# Type aliases for commonly used collections
GateResults = Dict[str, GateResult]
StageResults = Dict[Stage, GateResults]
PolicyConfiguration = Dict[str, Any]
