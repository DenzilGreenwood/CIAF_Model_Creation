"""
LLM Audit Manager

Main orchestrator for CIAF LCM process applied to Large Language Models.
Implements the eight-stage audit lifecycle as defined in the CIAF Data Structures 
Technical Specification.
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from ..ciaf.core.policy import LCMPolicy, get_default_policy
from ..ciaf.core.crypto import canonical_hash, sha256_hash
from ..ciaf.core.signers import get_default_signer

from .llm_anchors import LLMDatasetAnchor, LLMModelAnchor, LLMDeploymentAnchor
from .llm_receipts import LLMInferenceReceipt, LLMTrainingSession
from .llm_capsules import LLMCapsuleHeader
from .llm_compliance import LLMComplianceMonitor


class LLMAuditManager:
    """
    Comprehensive audit manager for LLM operations using CIAF LCM process.
    
    Implements the canonical eight-stage architecture:
    Stage A: Dataset Anchoring
    Stage B: Model Anchoring  
    Stage C: Training Session
    Stage D: Pre-deployment Validation
    Stage E: Deployment Anchoring
    Stage F: Test Evaluation
    Stage G: Inference Operations
    Stage H: Merkle Root Management
    """
    
    def __init__(self, policy: Optional[LCMPolicy] = None):
        """Initialize LLM audit manager with policy configuration."""
        self.policy = policy or get_default_policy()
        self.signer = get_default_signer()
        self.compliance_monitor = LLMComplianceMonitor(self.policy)
        
        # Audit trail storage
        self.dataset_anchors: Dict[str, LLMDatasetAnchor] = {}
        self.model_anchors: Dict[str, LLMModelAnchor] = {}
        self.deployment_anchors: Dict[str, LLMDeploymentAnchor] = {}
        self.training_sessions: Dict[str, LLMTrainingSession] = {}
        self.inference_receipts: List[LLMInferenceReceipt] = []
        self.capsule_headers: Dict[str, LLMCapsuleHeader] = {}
        
    def create_dataset_anchor(self, 
                            dataset_id: str,
                            dataset_content: Any,
                            metadata: Dict[str, Any]) -> LLMDatasetAnchor:
        """
        Stage A: Create dataset anchor for LLM training data.
        
        Args:
            dataset_id: Unique identifier for the dataset
            dataset_content: The actual dataset content
            metadata: Dataset metadata including provenance, quality metrics
            
        Returns:
            LLMDatasetAnchor: Cryptographically bound dataset anchor
        """
        # Compute dataset hash using canonical serialization
        dataset_hash = canonical_hash(dataset_content)
        
        # Create anchor with policy compliance validation
        anchor = LLMDatasetAnchor(
            anchor_id=f"ds_{dataset_hash[:16]}",
            dataset_id=dataset_id,
            dataset_hash=dataset_hash,
            metadata=metadata,
            policy=self.policy,
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        
        # Validate compliance before storing
        compliance_result = self.compliance_monitor.validate_dataset_anchor(anchor)
        if not compliance_result.is_compliant:
            raise ValueError(f"Dataset anchor compliance validation failed: {compliance_result.violations}")
        
        # Sign the anchor
        anchor_data = canonical_hash(asdict(anchor))
        anchor.signature = self.signer.sign(anchor_data.encode('utf-8'))
        
        # Store in audit trail
        self.dataset_anchors[anchor.anchor_id] = anchor
        
        return anchor
    
    def create_model_anchor(self,
                          model_id: str, 
                          model_state: Dict[str, Any],
                          training_config: Dict[str, Any],
                          dataset_anchor_ref: str) -> LLMModelAnchor:
        """
        Stage B: Create model anchor for LLM architecture and weights.
        
        Args:
            model_id: Unique identifier for the model
            model_state: Model weights and architecture 
            training_config: Training configuration and hyperparameters
            dataset_anchor_ref: Reference to training dataset anchor
            
        Returns:
            LLMModelAnchor: Cryptographically bound model anchor
        """
        # Verify dataset anchor exists
        if dataset_anchor_ref not in self.dataset_anchors:
            raise ValueError(f"Referenced dataset anchor not found: {dataset_anchor_ref}")
        
        # Compute model hash
        model_hash = canonical_hash(model_state)
        
        anchor = LLMModelAnchor(
            anchor_id=f"md_{model_hash[:16]}",
            model_id=model_id,
            model_hash=model_hash,
            architecture=training_config.get('architecture', {}),
            hyperparameters=training_config.get('hyperparameters', {}),
            dataset_anchor_ref=dataset_anchor_ref,
            policy=self.policy,
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        
        # Compliance validation
        compliance_result = self.compliance_monitor.validate_model_anchor(anchor)
        if not compliance_result.is_compliant:
            raise ValueError(f"Model anchor compliance validation failed: {compliance_result.violations}")
        
        # Sign and store
        anchor_data = canonical_hash(asdict(anchor))
        anchor.signature = self.signer.sign(anchor_data.encode('utf-8'))
        self.model_anchors[anchor.anchor_id] = anchor
        
        return anchor
    
    def create_training_session(self,
                              session_id: str,
                              model_anchor_ref: str,
                              training_metrics: Dict[str, Any],
                              checkpoints: List[str]) -> LLMTrainingSession:
        """
        Stage C: Create training session record for LLM training process.
        
        Args:
            session_id: Unique training session identifier
            model_anchor_ref: Reference to model being trained
            training_metrics: Training progress and performance metrics
            checkpoints: List of training checkpoint hashes
            
        Returns:
            LLMTrainingSession: Comprehensive training session record
        """
        if model_anchor_ref not in self.model_anchors:
            raise ValueError(f"Referenced model anchor not found: {model_anchor_ref}")
        
        session = LLMTrainingSession(
            session_id=session_id,
            model_anchor_ref=model_anchor_ref,
            training_metrics=training_metrics,
            checkpoints=checkpoints,
            policy=self.policy,
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        
        # Sign and store
        session_data = canonical_hash(asdict(session))
        session.signature = self.signer.sign(session_data.encode('utf-8'))
        self.training_sessions[session.session_id] = session
        
        return session
    
    def create_deployment_anchor(self,
                               deployment_id: str,
                               model_anchor_ref: str,
                               deployment_config: Dict[str, Any],
                               environment_info: Dict[str, Any]) -> LLMDeploymentAnchor:
        """
        Stage E: Create deployment anchor for LLM production deployment.
        
        Args:
            deployment_id: Unique deployment identifier
            model_anchor_ref: Reference to deployed model
            deployment_config: Deployment configuration
            environment_info: Production environment details
            
        Returns:
            LLMDeploymentAnchor: Production deployment anchor
        """
        if model_anchor_ref not in self.model_anchors:
            raise ValueError(f"Referenced model anchor not found: {model_anchor_ref}")
        
        anchor = LLMDeploymentAnchor(
            anchor_id=f"dp_{deployment_id[:16]}",
            deployment_id=deployment_id,
            model_anchor_ref=model_anchor_ref,
            deployment_config=deployment_config,
            environment_info=environment_info,
            policy=self.policy,
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        
        # Compliance validation for deployment
        compliance_result = self.compliance_monitor.validate_deployment_anchor(anchor)
        if not compliance_result.is_compliant:
            raise ValueError(f"Deployment anchor compliance validation failed: {compliance_result.violations}")
        
        # Sign and store
        anchor_data = canonical_hash(asdict(anchor))
        anchor.signature = self.signer.sign(anchor_data.encode('utf-8'))
        self.deployment_anchors[anchor.anchor_id] = anchor
        
        return anchor
    
    def record_inference(self,
                        request_id: str,
                        deployment_anchor_ref: str,
                        query: str,
                        response: str,
                        metadata: Optional[Dict[str, Any]] = None) -> LLMInferenceReceipt:
        """
        Stage G: Record LLM inference operation with lightweight receipt.
        
        Args:
            request_id: Unique request identifier
            deployment_anchor_ref: Reference to deployment anchor
            query: Input query/prompt
            response: LLM generated response
            metadata: Optional inference metadata
            
        Returns:
            LLMInferenceReceipt: Lightweight inference receipt
        """
        if deployment_anchor_ref not in self.deployment_anchors:
            raise ValueError(f"Referenced deployment anchor not found: {deployment_anchor_ref}")
        
        receipt = LLMInferenceReceipt(
            receipt_id=str(uuid.uuid4()),
            request_id=request_id,
            deployment_anchor_ref=deployment_anchor_ref,
            query_hash=sha256_hash(query.encode('utf-8')),
            response_hash=sha256_hash(response.encode('utf-8')),
            metadata=metadata or {},
            policy=self.policy,
            committed_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        
        # Sign and store
        receipt_data = canonical_hash(asdict(receipt))
        receipt.signature = self.signer.sign(receipt_data.encode('utf-8'))
        self.inference_receipts.append(receipt)
        
        return receipt
    
    def create_audit_capsule(self, capsule_id: str) -> LLMCapsuleHeader:
        """
        Stage H: Create comprehensive audit capsule with all evidence.
        
        Args:
            capsule_id: Unique capsule identifier
            
        Returns:
            LLMCapsuleHeader: Complete audit evidence package
        """
        capsule = LLMCapsuleHeader(
            capsule_id=capsule_id,
            capsule_version="1.0",
            generated_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            policy=asdict(self.policy),
            
            # Eight-stage evidence collection
            stage_a_dataset=list(self.dataset_anchors.values()),
            stage_b_model=list(self.model_anchors.values()),
            stage_c_training=list(self.training_sessions.values()),
            stage_e_deployment=list(self.deployment_anchors.values()),
            stage_g_inference=self.inference_receipts[-100:],  # Latest 100 receipts
            
            # Compliance summary
            compliance_summary=self.compliance_monitor.generate_summary()
        )
        
        # Sign complete capsule
        capsule_data = canonical_hash(asdict(capsule))
        capsule.signature = self.signer.sign(capsule_data.encode('utf-8'))
        
        self.capsule_headers[capsule_id] = capsule
        return capsule
    
    def export_audit_trail(self, format_type: str = "json") -> str:
        """Export complete audit trail in specified format."""
        if format_type == "json":
            audit_data = {
                "dataset_anchors": {k: asdict(v) for k, v in self.dataset_anchors.items()},
                "model_anchors": {k: asdict(v) for k, v in self.model_anchors.items()},
                "deployment_anchors": {k: asdict(v) for k, v in self.deployment_anchors.items()},
                "training_sessions": {k: asdict(v) for k, v in self.training_sessions.items()},
                "inference_receipts": [asdict(r) for r in self.inference_receipts],
                "capsule_headers": {k: asdict(v) for k, v in self.capsule_headers.items()}
            }
            return json.dumps(audit_data, indent=2, sort_keys=True)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")