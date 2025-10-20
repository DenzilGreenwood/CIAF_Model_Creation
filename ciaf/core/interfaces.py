"""
Interfaces (typing.Protocol) for the Cognitive Insight Audit Framework.

This module defines contracts for swappable components like signers, RNG sources,
Merkle trees, anchor derivers, and anchor stores. Using Protocol allows for
clean dependency injection and testing.

Created: 2025-09-26
Author: Denzil James Greenwood
Version: 1.0.0
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable, Optional, List, Tuple, Dict, Any, Union


@runtime_checkable
class Signer(Protocol):
    """Protocol for digital signature implementations."""
    key_id: str
    
    def sign(self, data: bytes) -> str:
        """Sign data and return signature string."""
        ...
    
    def verify(self, data: bytes, signature: str) -> bool:
        """Verify signature against data."""
        ...


@runtime_checkable
class RNG(Protocol):
    """Protocol for random number generation sources."""
    
    def random_bytes(self, n: int) -> bytes:
        """Generate n cryptographically secure random bytes."""
        ...


@runtime_checkable
class Merkle(Protocol):
    """Protocol for Merkle tree implementations."""
    
    def add_leaf(self, leaf_hash: str) -> str:
        """Add leaf and return new root."""
        ...
    
    def get_root(self) -> str:
        """Get the current Merkle root hash."""
        ...
    
    def get_proof(self, leaf_hash: str) -> List[Tuple[str, str]]:
        """Get inclusion proof for a leaf as list of (hash, position) tuples."""
        ...
    
    def get_merkle_path(self, leaf_hash: str) -> List[Tuple[str, str]]:
        """Alias for get_proof to maintain backward compatibility."""
        ...
    
    def verify_proof(self, leaf_hash: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """Verify Merkle inclusion proof."""
        ...


@runtime_checkable
class AnchorDeriver(Protocol):
    """Protocol for hierarchical anchor derivation."""
    
    def derive_master_anchor(self, password: str, salt: bytes) -> bytes:
        """Derive master anchor from password and salt."""
        ...
    
    def derive_dataset_anchor(self, master_anchor: bytes, dataset_hash: str) -> bytes:
        """Derive dataset anchor from master anchor and dataset hash."""
        ...
    
    def derive_model_anchor(self, master_anchor: bytes, model_hash: str) -> bytes:
        """Derive model anchor from master anchor and model hash."""
        ...
    
    def derive_capsule_anchor(self, dataset_anchor: bytes, capsule_id: str) -> bytes:
        """Derive capsule anchor from dataset anchor and capsule ID."""
        ...


@runtime_checkable
class AnchorStore(Protocol):
    """Protocol for anchor storage implementations."""
    
    def append_anchor(self, anchor: Dict[str, Any]) -> None:
        """Append a new anchor to the store (WORM semantics)."""
        ...
    
    def get_latest_anchor(self) -> Optional[Dict[str, Any]]:
        """Get the most recent anchor from the store."""
        ...


@runtime_checkable
class AIGovernanceFramework(ABC):
    """
    Abstract Base Class for AI Governance Frameworks
    
    Provides the foundational governance layer for the Cognitive Insight Audit Framework (CIAF).
    All industry-specific AI governance implementations must inherit from this class and implement
    the required abstract methods while leveraging shared governance infrastructure.
    
    Key Responsibilities:
    - Organization-level governance configuration and management
    - Standardized compliance assessment and reporting
    - Integration with CIAF cryptographic audit trails
    - Cross-industry governance metrics and transparency
    - Policy enforcement and bias detection coordination
    
    Usage Pattern:
        class MyIndustryFramework(AIGovernanceFramework):
            def __init__(self, organization_id: str, **kwargs):
                super().__init__(organization_id)
                # Industry-specific initialization
            
            def assess_compliance(self, **kwargs):
                # Industry-specific implementation
    """
    
    def __init__(self, organization_id: str, framework_version: str = "1.0.0"):
        """
        Initialize the AI governance framework
        
        Args:
            organization_id: Unique identifier for the organization
            framework_version: Version of the governance framework implementation
        """
        self.organization_id = organization_id
        self.framework_version = framework_version
        self.created_at = datetime.now(timezone.utc)
        self.governance_config = {}
        self.compliance_history = []
        self.audit_metadata = {}
    
    @abstractmethod
    def assess_compliance(self, **kwargs) -> Dict[str, Any]:
        """
        Perform comprehensive compliance assessment
        
        Must be implemented by each industry-specific framework to provide
        sector-appropriate compliance validation and scoring.
        
        Returns:
            Dict containing compliance assessment results, scores, and recommendations
        """
        ...
    
    @abstractmethod
    def validate_governance_requirements(self, **kwargs) -> Dict[str, Any]:
        """
        Validate industry-specific governance requirements
        
        Must be implemented to check compliance with sector-specific regulations,
        standards, and governance policies.
        
        Returns:
            Dict containing validation results and compliance status
        """
        ...
    
    @abstractmethod
    def generate_audit_report(self, **kwargs) -> Dict[str, Any]:
        """
        Generate comprehensive audit report
        
        Must be implemented to produce industry-appropriate audit documentation
        with cryptographic verification and compliance tracking.
        
        Returns:
            Dict containing audit report with verification metadata
        """
        ...
    
    def record_governance_event(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """
        Record a governance event in the audit trail
        
        Args:
            event_type: Type of governance event (assessment, validation, etc.)
            event_data: Event-specific data and metadata
            
        Returns:
            Event ID for tracking and reference
        """
        event_id = f"{self.organization_id}_{event_type}_{datetime.now(timezone.utc).isoformat()}"
        
        governance_event = {
            'event_id': event_id,
            'organization_id': self.organization_id,
            'event_type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'framework_version': self.framework_version,
            'data': event_data
        }
        
        self.compliance_history.append(governance_event)
        return event_id
    
    def get_compliance_score(self) -> float:
        """
        Calculate overall compliance score based on assessment history
        
        Returns:
            Compliance score between 0.0 and 1.0
        """
        if not self.compliance_history:
            return 0.0
        
        # Basic scoring - can be overridden by industry implementations
        recent_assessments = self.compliance_history[-10:]  # Last 10 assessments
        scores = []
        
        for assessment in recent_assessments:
            if 'compliance_score' in assessment.get('data', {}):
                scores.append(assessment['data']['compliance_score'])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def update_governance_config(self, config_updates: Dict[str, Any]) -> None:
        """
        Update governance configuration parameters
        
        Args:
            config_updates: Dictionary of configuration updates
        """
        self.governance_config.update(config_updates)
        self.record_governance_event('config_update', config_updates)
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Get summary of governance and audit activities
        
        Returns:
            Dict containing audit summary and compliance metrics
        """
        return {
            'organization_id': self.organization_id,
            'framework_version': self.framework_version,
            'created_at': self.created_at.isoformat(),
            'total_events': len(self.compliance_history),
            'compliance_score': self.get_compliance_score(),
            'last_assessment': self.compliance_history[-1] if self.compliance_history else None,
            'governance_config': self.governance_config
        }