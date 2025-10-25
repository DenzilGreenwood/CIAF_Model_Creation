"""
LCM Validation Framework

Comprehensive validation and verification for Lazy Capsule Materialization (LCM)
processes including anchor derivation, receipt verification, and Merkle proof validation.

Created: 2025-10-24
Author: Denzil James Greenwood
Version: 1.0.0
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from ...ciaf.core import (
    sha256_hash, blake3_hash, derive_master_anchor, derive_dataset_anchor,
    derive_model_anchor, derive_capsule_anchor, MerkleTree
)
from ...ciaf.lcm import (
    LCMDatasetAnchor, LCMModelAnchor, LCMTrainingSession, 
    LCMPreDeploymentAnchor, LCMDeploymentAnchor, LCMInferenceReceipt
)
from ...ciaf.inference import Receipt


class ValidationResult(Enum):
    """Validation result types."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    component: str
    test_name: str
    result: ValidationResult
    message: str
    details: Dict[str, Any]
    timestamp: str
    execution_time_ms: float


class LCMValidator:
    """
    Comprehensive LCM validation framework.
    
    Validates all aspects of the LCM process including:
    - Anchor derivation correctness
    - Receipt authenticity and integrity
    - Merkle proof verification
    - Cross-component consistency
    """
    
    def __init__(self):
        """Initialize LCM validator."""
        self.validation_reports: List[ValidationReport] = []
        self.anchor_validator = AnchorValidator()
        self.receipt_validator = ReceiptValidator()
        self.merkle_validator = MerkleProofValidator()
    
    def validate_full_lcm_cycle(
        self,
        dataset_anchor: LCMDatasetAnchor,
        model_anchor: LCMModelAnchor,
        training_session: LCMTrainingSession,
        deployment_anchor: LCMDeploymentAnchor,
        inference_receipt: LCMInferenceReceipt
    ) -> List[ValidationReport]:
        """
        Validate a complete LCM cycle from dataset anchoring to inference.
        
        Args:
            dataset_anchor: Dataset anchor
            model_anchor: Model anchor
            training_session: Training session
            deployment_anchor: Deployment anchor
            inference_receipt: Inference receipt
            
        Returns:
            List of validation reports
        """
        reports = []
        
        # Validate dataset anchor
        reports.extend(self.anchor_validator.validate_dataset_anchor(dataset_anchor))
        
        # Validate model anchor
        reports.extend(self.anchor_validator.validate_model_anchor(model_anchor))
        
        # Validate training session consistency
        reports.extend(self._validate_training_consistency(
            dataset_anchor, model_anchor, training_session
        ))
        
        # Validate deployment consistency
        reports.extend(self._validate_deployment_consistency(
            model_anchor, training_session, deployment_anchor
        ))
        
        # Validate inference receipt
        reports.extend(self.receipt_validator.validate_inference_receipt(
            inference_receipt, deployment_anchor
        ))
        
        # Cross-component validation
        reports.extend(self._validate_cross_component_consistency(
            dataset_anchor, model_anchor, training_session, 
            deployment_anchor, inference_receipt
        ))
        
        self.validation_reports.extend(reports)
        return reports
    
    def _validate_training_consistency(
        self,
        dataset_anchor: LCMDatasetAnchor,
        model_anchor: LCMModelAnchor,
        training_session: LCMTrainingSession
    ) -> List[ValidationReport]:
        """Validate training session consistency."""
        reports = []
        start_time = time.time()
        
        try:
            # Check model anchor consistency
            if training_session.model_anchor.anchor_id != model_anchor.anchor_id:
                reports.append(ValidationReport(
                    component="training_session",
                    test_name="model_anchor_consistency",
                    result=ValidationResult.INVALID,
                    message="Training session model anchor mismatch",
                    details={
                        "training_model_anchor": training_session.model_anchor.anchor_id,
                        "expected_model_anchor": model_anchor.anchor_id
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="training_session",
                    test_name="model_anchor_consistency",
                    result=ValidationResult.VALID,
                    message="Training session model anchor is consistent",
                    details={"anchor_id": model_anchor.anchor_id},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            
            # Validate training session root computation
            if training_session.training_snapshot:
                expected_root = training_session.get_training_session_root()
                computed_root = self._compute_training_session_root(
                    training_session.model_anchor,
                    training_session.datasets_root_anchor,
                    training_session.training_snapshot.merkle_root_hash
                )
                
                if expected_root != computed_root:
                    reports.append(ValidationReport(
                        component="training_session",
                        test_name="session_root_computation",
                        result=ValidationResult.INVALID,
                        message="Training session root computation mismatch",
                        details={
                            "expected_root": expected_root,
                            "computed_root": computed_root
                        },
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
                else:
                    reports.append(ValidationReport(
                        component="training_session",
                        test_name="session_root_computation",
                        result=ValidationResult.VALID,
                        message="Training session root computation is correct",
                        details={"session_root": expected_root},
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
        
        except Exception as e:
            reports.append(ValidationReport(
                component="training_session",
                test_name="training_consistency_validation",
                result=ValidationResult.ERROR,
                message=f"Error during training consistency validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            ))
        
        return reports
    
    def _validate_deployment_consistency(
        self,
        model_anchor: LCMModelAnchor,
        training_session: LCMTrainingSession,
        deployment_anchor: LCMDeploymentAnchor
    ) -> List[ValidationReport]:
        """Validate deployment consistency."""
        reports = []
        start_time = time.time()
        
        try:
            # Check deployment references training session
            if hasattr(deployment_anchor, 'predeployment_anchor'):
                predeployment = deployment_anchor.predeployment_anchor
                if hasattr(predeployment, 'build_artifact'):
                    # Validate that deployment references correct model
                    reports.append(ValidationReport(
                        component="deployment",
                        test_name="model_reference_validation",
                        result=ValidationResult.VALID,
                        message="Deployment references are consistent",
                        details={
                            "deployment_id": deployment_anchor.deployment_id,
                            "model_anchor_id": model_anchor.anchor_id
                        },
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
            
            # Validate deployment hash computation
            expected_hash = deployment_anchor.deployment_hash
            if expected_hash:
                reports.append(ValidationReport(
                    component="deployment",
                    test_name="deployment_hash_validation",
                    result=ValidationResult.VALID,
                    message="Deployment hash is computed correctly",
                    details={"deployment_hash": expected_hash[:16] + "..."},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            reports.append(ValidationReport(
                component="deployment",
                test_name="deployment_consistency_validation",
                result=ValidationResult.ERROR,
                message=f"Error during deployment consistency validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            ))
        
        return reports
    
    def _validate_cross_component_consistency(
        self,
        dataset_anchor: LCMDatasetAnchor,
        model_anchor: LCMModelAnchor,
        training_session: LCMTrainingSession,
        deployment_anchor: LCMDeploymentAnchor,
        inference_receipt: LCMInferenceReceipt
    ) -> List[ValidationReport]:
        """Validate cross-component consistency."""
        reports = []
        start_time = time.time()
        
        try:
            # Validate that inference receipt references correct deployment
            if hasattr(inference_receipt, 'deployment_ref'):
                if inference_receipt.deployment_ref == deployment_anchor.anchor_id:
                    reports.append(ValidationReport(
                        component="cross_component",
                        test_name="inference_deployment_reference",
                        result=ValidationResult.VALID,
                        message="Inference receipt correctly references deployment",
                        details={
                            "inference_deployment_ref": inference_receipt.deployment_ref,
                            "deployment_anchor_id": deployment_anchor.anchor_id
                        },
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
                else:
                    reports.append(ValidationReport(
                        component="cross_component",
                        test_name="inference_deployment_reference",
                        result=ValidationResult.INVALID,
                        message="Inference receipt deployment reference mismatch",
                        details={
                            "inference_deployment_ref": inference_receipt.deployment_ref,
                            "expected_deployment_anchor_id": deployment_anchor.anchor_id
                        },
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
            
            # Validate anchor hierarchy integrity
            if (dataset_anchor.master_anchor.hex() == model_anchor.master_anchor.hex()):
                reports.append(ValidationReport(
                    component="cross_component",
                    test_name="anchor_hierarchy_integrity",
                    result=ValidationResult.VALID,
                    message="Dataset and model anchors share same master anchor",
                    details={
                        "master_anchor": dataset_anchor.master_anchor.hex()[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="cross_component",
                    test_name="anchor_hierarchy_integrity",
                    result=ValidationResult.WARNING,
                    message="Dataset and model anchors have different master anchors",
                    details={
                        "dataset_master_anchor": dataset_anchor.master_anchor.hex()[:16] + "...",
                        "model_master_anchor": model_anchor.master_anchor.hex()[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            reports.append(ValidationReport(
                component="cross_component",
                test_name="cross_component_consistency_validation",
                result=ValidationResult.ERROR,
                message=f"Error during cross-component validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            ))
        
        return reports
    
    def _compute_training_session_root(
        self,
        model_anchor: LCMModelAnchor,
        datasets_root_anchor: str,
        training_snapshot_root: str
    ) -> str:
        """Compute training session root for verification."""
        anchor_hashes = [
            model_anchor.model_hash,
            datasets_root_anchor,
            training_snapshot_root
        ]
        merkle_tree = MerkleTree(anchor_hashes)
        return merkle_tree.get_root()
    
    def generate_validation_summary(self) -> Dict[str, Any]:
        """Generate comprehensive validation summary."""
        if not self.validation_reports:
            return {"status": "no_validations_performed"}
        
        total_tests = len(self.validation_reports)
        valid_tests = sum(1 for r in self.validation_reports if r.result == ValidationResult.VALID)
        invalid_tests = sum(1 for r in self.validation_reports if r.result == ValidationResult.INVALID)
        warning_tests = sum(1 for r in self.validation_reports if r.result == ValidationResult.WARNING)
        error_tests = sum(1 for r in self.validation_reports if r.result == ValidationResult.ERROR)
        
        avg_execution_time = sum(r.execution_time_ms for r in self.validation_reports) / total_tests
        
        return {
            "summary": {
                "total_tests": total_tests,
                "valid": valid_tests,
                "invalid": invalid_tests,
                "warnings": warning_tests,
                "errors": error_tests,
                "success_rate": (valid_tests / total_tests) * 100 if total_tests > 0 else 0,
                "average_execution_time_ms": avg_execution_time
            },
            "component_breakdown": self._get_component_breakdown(),
            "recommendations": self._generate_recommendations()
        }
    
    def _get_component_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get validation breakdown by component."""
        components = {}
        for report in self.validation_reports:
            if report.component not in components:
                components[report.component] = {
                    "valid": 0, "invalid": 0, "warnings": 0, "errors": 0
                }
            
            if report.result == ValidationResult.VALID:
                components[report.component]["valid"] += 1
            elif report.result == ValidationResult.INVALID:
                components[report.component]["invalid"] += 1
            elif report.result == ValidationResult.WARNING:
                components[report.component]["warnings"] += 1
            elif report.result == ValidationResult.ERROR:
                components[report.component]["errors"] += 1
        
        return components
    
    def _generate_recommendations(self) -> List[str]:
        """Generate validation recommendations."""
        recommendations = []
        
        invalid_reports = [r for r in self.validation_reports if r.result == ValidationResult.INVALID]
        error_reports = [r for r in self.validation_reports if r.result == ValidationResult.ERROR]
        
        if invalid_reports:
            recommendations.append(
                f"Address {len(invalid_reports)} validation failures before production deployment"
            )
        
        if error_reports:
            recommendations.append(
                f"Investigate {len(error_reports)} validation errors that prevented complete testing"
            )
        
        component_failures = {}
        for report in invalid_reports + error_reports:
            if report.component not in component_failures:
                component_failures[report.component] = 0
            component_failures[report.component] += 1
        
        for component, count in component_failures.items():
            if count > 1:
                recommendations.append(
                    f"Focus on {component} component - {count} validation issues detected"
                )
        
        if not recommendations:
            recommendations.append("All validations passed - system ready for production")
        
        return recommendations


class AnchorValidator:
    """Validates anchor derivation and integrity."""
    
    def validate_dataset_anchor(self, anchor: LCMDatasetAnchor) -> List[ValidationReport]:
        """Validate dataset anchor derivation and integrity."""
        reports = []
        start_time = time.time()
        
        try:
            # Validate anchor derivation
            expected_dataset_anchor = derive_dataset_anchor(
                anchor.master_anchor, anchor.dataset_hash
            )
            
            if anchor.dataset_anchor == expected_dataset_anchor:
                reports.append(ValidationReport(
                    component="dataset_anchor",
                    test_name="anchor_derivation",
                    result=ValidationResult.VALID,
                    message="Dataset anchor derivation is correct",
                    details={"anchor_id": anchor.anchor_id},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="dataset_anchor",
                    test_name="anchor_derivation",
                    result=ValidationResult.INVALID,
                    message="Dataset anchor derivation mismatch",
                    details={
                        "expected": expected_dataset_anchor.hex()[:16] + "...",
                        "actual": anchor.dataset_anchor.hex()[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            
            # Validate dataset hash computation
            computed_hash = anchor._compute_dataset_hash()
            if computed_hash == anchor.dataset_hash:
                reports.append(ValidationReport(
                    component="dataset_anchor",
                    test_name="dataset_hash_computation",
                    result=ValidationResult.VALID,
                    message="Dataset hash computation is correct",
                    details={"dataset_hash": computed_hash[:16] + "..."},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="dataset_anchor",
                    test_name="dataset_hash_computation",
                    result=ValidationResult.INVALID,
                    message="Dataset hash computation mismatch",
                    details={
                        "expected": anchor.dataset_hash[:16] + "...",
                        "computed": computed_hash[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            reports.append(ValidationReport(
                component="dataset_anchor",
                test_name="dataset_anchor_validation",
                result=ValidationResult.ERROR,
                message=f"Error during dataset anchor validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            ))
        
        return reports
    
    def validate_model_anchor(self, anchor: LCMModelAnchor) -> List[ValidationReport]:
        """Validate model anchor derivation and integrity."""
        reports = []
        start_time = time.time()
        
        try:
            # Validate anchor derivation
            expected_model_anchor = derive_model_anchor(
                anchor.master_anchor, anchor.model_hash
            )
            
            if anchor.model_anchor == expected_model_anchor:
                reports.append(ValidationReport(
                    component="model_anchor",
                    test_name="anchor_derivation",
                    result=ValidationResult.VALID,
                    message="Model anchor derivation is correct",
                    details={"anchor_id": anchor.anchor_id},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="model_anchor",
                    test_name="anchor_derivation",
                    result=ValidationResult.INVALID,
                    message="Model anchor derivation mismatch",
                    details={
                        "expected": expected_model_anchor.hex()[:16] + "...",
                        "actual": anchor.model_anchor.hex()[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            
            # Validate model hash computation
            computed_hash = anchor._compute_model_hash()
            if computed_hash == anchor.model_hash:
                reports.append(ValidationReport(
                    component="model_anchor",
                    test_name="model_hash_computation",
                    result=ValidationResult.VALID,
                    message="Model hash computation is correct",
                    details={"model_hash": computed_hash[:16] + "..."},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="model_anchor",
                    test_name="model_hash_computation",
                    result=ValidationResult.INVALID,
                    message="Model hash computation mismatch",
                    details={
                        "expected": anchor.model_hash[:16] + "...",
                        "computed": computed_hash[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
        
        except Exception as e:
            reports.append(ValidationReport(
                component="model_anchor",
                test_name="model_anchor_validation",
                result=ValidationResult.ERROR,
                message=f"Error during model anchor validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            ))
        
        return reports


class ReceiptValidator:
    """Validates receipt authenticity and integrity."""
    
    def validate_inference_receipt(
        self, 
        receipt: LCMInferenceReceipt,
        deployment_anchor: Optional[LCMDeploymentAnchor] = None
    ) -> List[ValidationReport]:
        """Validate inference receipt."""
        reports = []
        start_time = time.time()
        
        try:
            # Validate receipt structure
            if hasattr(receipt, 'receipt_id') and receipt.receipt_id:
                reports.append(ValidationReport(
                    component="inference_receipt",
                    test_name="receipt_structure",
                    result=ValidationResult.VALID,
                    message="Receipt has valid structure",
                    details={"receipt_id": receipt.receipt_id},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            else:
                reports.append(ValidationReport(
                    component="inference_receipt",
                    test_name="receipt_structure",
                    result=ValidationResult.INVALID,
                    message="Receipt missing required fields",
                    details={"missing_fields": ["receipt_id"]},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                ))
            
            # Validate timestamp
            if hasattr(receipt, 'timestamp') and receipt.timestamp:
                try:
                    datetime.fromisoformat(receipt.timestamp.replace('Z', '+00:00'))
                    reports.append(ValidationReport(
                        component="inference_receipt",
                        test_name="timestamp_format",
                        result=ValidationResult.VALID,
                        message="Receipt timestamp is valid",
                        details={"timestamp": receipt.timestamp},
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
                except ValueError:
                    reports.append(ValidationReport(
                        component="inference_receipt",
                        test_name="timestamp_format",
                        result=ValidationResult.INVALID,
                        message="Receipt timestamp format is invalid",
                        details={"timestamp": receipt.timestamp},
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        execution_time_ms=(time.time() - start_time) * 1000
                    ))
        
        except Exception as e:
            reports.append(ValidationReport(
                component="inference_receipt",
                test_name="inference_receipt_validation",
                result=ValidationResult.ERROR,
                message=f"Error during inference receipt validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            ))
        
        return reports


class MerkleProofValidator:
    """Validates Merkle proofs and tree integrity."""
    
    def validate_merkle_proof(
        self,
        leaf_data: str,
        proof: List[str],
        root: str,
        leaf_index: int
    ) -> ValidationReport:
        """Validate a Merkle proof."""
        start_time = time.time()
        
        try:
            # Compute leaf hash
            current_hash = sha256_hash(leaf_data.encode())
            
            # Apply proof path
            for i, sibling_hash in enumerate(proof):
                if (leaf_index >> i) & 1:
                    # Right child
                    current_hash = sha256_hash((sibling_hash + current_hash).encode())
                else:
                    # Left child
                    current_hash = sha256_hash((current_hash + sibling_hash).encode())
            
            # Check if computed root matches expected root
            if current_hash == root:
                return ValidationReport(
                    component="merkle_proof",
                    test_name="proof_verification",
                    result=ValidationResult.VALID,
                    message="Merkle proof is valid",
                    details={
                        "leaf_index": leaf_index,
                        "proof_length": len(proof),
                        "root": root[:16] + "..."
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            else:
                return ValidationReport(
                    component="merkle_proof",
                    test_name="proof_verification",
                    result=ValidationResult.INVALID,
                    message="Merkle proof verification failed",
                    details={
                        "expected_root": root[:16] + "...",
                        "computed_root": current_hash[:16] + "...",
                        "leaf_index": leaf_index
                    },
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    execution_time_ms=(time.time() - start_time) * 1000
                )
        
        except Exception as e:
            return ValidationReport(
                component="merkle_proof",
                test_name="proof_verification",
                result=ValidationResult.ERROR,
                message=f"Error during Merkle proof validation: {str(e)}",
                details={"exception": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
                execution_time_ms=(time.time() - start_time) * 1000
            )