"""
CIAF Compliance Gates System

A comprehensive, policy-driven framework for ML lifecycle governance with normative
pass/fail semantics, cryptographic attestation, and regulatory alignment.

This module provides:
- Protocol-based gate interfaces for consistency and extensibility
- Stage-based orchestration across ML lifecycle (Dataset → Training → Pre-deployment → Inference)
- Specialized gate implementations for bias, explainability, uncertainty, robustness
- Cryptographic receipt generation with Merkle batching for audit trails
- Policy-driven configuration enabling governance without model code changes
- HITL escalation workflows for human oversight integration

Key Components:
- interfaces.py: Core protocols and data structures
- orchestrator.py: Lifecycle stage orchestration and policy enforcement
- implementations/: Specialized gate catalog (bias, explainability, uncertainty, etc.)
- policy.py: Configuration management and threshold settings
- receipts.py: Cryptographic attestation and audit trail generation

Architecture Pattern:
The gate system maintains strict separation between model evaluation and governance,
keeping models portable while providing comprehensive compliance automation.
"""

from .interfaces import ComplianceGate, GateResult, GateStatus, OperationContext, Stage

from .orchestrator import GateOrchestrator, PolicyEnforcer

from .policy import GatePolicy, PolicyManager

from .receipts import GateReceiptGenerator, ReviewReceipt, ComplianceAuditTrail

# Import specialized gate implementations
from .implementations.bias_gate import BiasGate

# Note: Other gates to be implemented
# from .implementations import (
#     ExplainabilityGate,
#     UncertaintyGate,
#     RobustnessGate,
#     HITLGate,
#     ComplianceMappingGate
# )

__all__ = [
    # Core interfaces
    "ComplianceGate",
    "GateResult",
    "GateStatus",
    "OperationContext",
    "Stage",
    # Orchestration
    "GateOrchestrator",
    "PolicyEnforcer",
    # Policy management
    "GatePolicy",
    "PolicyManager",
    # Receipts and audit
    "GateReceiptGenerator",
    "ReviewReceipt",
    "ComplianceAuditTrail",
    # Gate implementations (implemented)
    "BiasGate",
    # Gate implementations (to be implemented)
    # 'ExplainabilityGate',
    # 'UncertaintyGate',
    # 'RobustnessGate',
    # 'HITLGate',
    # 'ComplianceMappingGate'
]

# Version and metadata
__version__ = "1.2.0"
__author__ = "CIAF Development Team"
__description__ = "Policy-driven compliance gates for ML lifecycle governance"
