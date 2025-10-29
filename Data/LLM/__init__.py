"""
CIAF LLM Audit System

This module implements the Lazy Capsule Materialization (LCM) process specifically
for Large Language Model (LLM) audit and governance as defined in the CIAF
technical specifications.

Components:
- LLM Dataset Anchoring
- Model Anchor Management 
- Training Session Tracking
- Deployment Anchor Creation
- Inference Receipt Generation
- Capsule Header Integration
- Compliance Monitoring
"""

from .llm_audit_manager import LLMAuditManager
from .llm_anchors import LLMDatasetAnchor, LLMModelAnchor, LLMDeploymentAnchor
from .llm_receipts import LLMInferenceReceipt, LLMTrainingSession
from .llm_capsules import LLMCapsuleHeader
from .llm_compliance import LLMComplianceMonitor

__version__ = "1.0.0"
__author__ = "Denzil James Greenwood"

__all__ = [
    "LLMAuditManager",
    "LLMDatasetAnchor", 
    "LLMModelAnchor",
    "LLMDeploymentAnchor",
    "LLMInferenceReceipt",
    "LLMTrainingSession", 
    "LLMCapsuleHeader",
    "LLMComplianceMonitor"
]