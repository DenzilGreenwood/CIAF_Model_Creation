"""
LLM Capsule Header Integration

Implements capsule header structures for comprehensive LLM audit packages
following the CIAF Capsule Header Integration specification.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass
class LLMCapsuleHeader:
    """
    Comprehensive CIAF LCM state capsule for LLM audit trails.
    Implements the eight-stage CIAF architecture for language models.
    """
    
    # Core metadata
    capsule_id: str = ""                   # Unique capsule identifier
    capsule_version: str = "1.0"           # Capsule format version
    capsule_type: str = "llm_audit_proof"  # LLM-specific capsule type
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    
    # Policy configuration (serialized)
    policy: Dict[str, Any] = field(default_factory=dict)
    
    # Eight-stage LLM audit evidence (A-H stages)
    stage_a_dataset: Optional[List[Any]] = None        # Dataset anchors
    stage_b_model: Optional[List[Any]] = None          # Model anchors
    stage_c_training: Optional[List[Any]] = None       # Training sessions
    stage_d_predeployment: Optional[List[Any]] = None  # Pre-deployment validation
    stage_e_deployment: Optional[List[Any]] = None     # Deployment anchors
    stage_f_test_evaluation: Optional[List[Any]] = None # Test evaluation results
    stage_g_inference: Optional[List[Any]] = None      # Inference receipts
    stage_h_roots: Optional[List[Any]] = None          # Merkle roots and proofs
    
    # LLM-specific aggregated metrics
    llm_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Model performance summary
    performance_summary: Dict[str, float] = field(default_factory=dict)
    benchmark_results: Dict[str, Any] = field(default_factory=dict)
    
    # Safety and alignment summary
    safety_summary: Dict[str, Any] = field(default_factory=dict)
    bias_assessment_summary: Dict[str, Any] = field(default_factory=dict)
    alignment_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Operational statistics
    inference_statistics: Dict[str, Any] = field(default_factory=dict)
    usage_patterns: Dict[str, Any] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)
    
    # Compliance and governance
    compliance_summary: Dict[str, Any] = field(default_factory=dict)
    regulatory_compliance: List[str] = field(default_factory=list)
    audit_trail_completeness: float = 0.0
    
    # Data provenance chain
    provenance_chain: List[Dict[str, Any]] = field(default_factory=list)
    data_lineage: Dict[str, Any] = field(default_factory=dict)
    
    # Quality assurance
    validation_results: Dict[str, Any] = field(default_factory=dict)
    testing_coverage: Dict[str, float] = field(default_factory=dict)
    
    # Security and privacy
    security_assessment: Dict[str, Any] = field(default_factory=dict)
    privacy_impact: Dict[str, Any] = field(default_factory=dict)
    data_protection_measures: List[str] = field(default_factory=list)
    
    # Resource utilization
    resource_consumption: Dict[str, Any] = field(default_factory=dict)
    cost_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Cryptographic verification
    merkle_proofs: List[Dict[str, Any]] = field(default_factory=list)
    signature: Optional[str] = None        # Capsule signature
    verification_chain: List[str] = field(default_factory=list)
    
    # Metadata and tags
    tags: List[str] = field(default_factory=list)
    classification: str = "unclassified"
    retention_period: Optional[str] = None
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to pretty-printed JSON for human readability."""
        return json.dumps(self.__dict__, indent=indent, sort_keys=True, default=str)
    
    def to_compact_json(self) -> str:
        """Convert to compact JSON for storage efficiency."""
        return json.dumps(self.__dict__, separators=(',', ':'), sort_keys=True, default=str)
    
    def add_stage_evidence(self, stage: str, evidence: Any) -> None:
        """Add evidence to a specific stage."""
        stage_map = {
            'A': 'stage_a_dataset',
            'B': 'stage_b_model', 
            'C': 'stage_c_training',
            'D': 'stage_d_predeployment',
            'E': 'stage_e_deployment',
            'F': 'stage_f_test_evaluation',
            'G': 'stage_g_inference',
            'H': 'stage_h_roots'
        }
        
        if stage.upper() in stage_map:
            attr_name = stage_map[stage.upper()]
            current_evidence = getattr(self, attr_name) or []
            current_evidence.append(evidence)
            setattr(self, attr_name, current_evidence)
        else:
            raise ValueError(f"Invalid stage: {stage}. Must be A-H.")
    
    def get_completeness_score(self) -> float:
        """Calculate audit trail completeness score."""
        stages = [
            self.stage_a_dataset,
            self.stage_b_model,
            self.stage_c_training,
            self.stage_d_predeployment,
            self.stage_e_deployment,
            self.stage_f_test_evaluation,
            self.stage_g_inference,
            self.stage_h_roots
        ]
        
        populated_stages = sum(1 for stage in stages if stage is not None and len(stage) > 0)
        return populated_stages / len(stages)
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of the capsule contents."""
        return {
            "capsule_id": self.capsule_id,
            "generation_date": self.generated_at,
            "completeness_score": self.get_completeness_score(),
            "total_datasets": len(self.stage_a_dataset or []),
            "total_models": len(self.stage_b_model or []),
            "total_training_sessions": len(self.stage_c_training or []),
            "total_deployments": len(self.stage_e_deployment or []),
            "total_inference_receipts": len(self.stage_g_inference or []),
            "compliance_status": self.compliance_summary.get("overall_status", "unknown"),
            "safety_score": self.safety_summary.get("overall_score", None),
            "performance_metrics": self.performance_summary,
            "resource_consumption": self.resource_consumption
        }


@dataclass 
class LLMAuditPackage:
    """
    Regulatory-ready audit package for LLM systems.
    Extends capsule functionality for external audit requirements.
    """
    
    # Package metadata
    package_id: str = ""
    package_version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    created_by: str = ""
    
    # Source capsule reference
    source_capsule: LLMCapsuleHeader = field(default_factory=LLMCapsuleHeader)
    
    # Regulatory context
    regulatory_framework: List[str] = field(default_factory=list)  # e.g., ['GDPR', 'AI_Act', 'SOX']
    jurisdiction: str = ""
    compliance_officer: str = ""
    
    # Audit scope and objectives
    audit_scope: Dict[str, Any] = field(default_factory=dict)
    audit_objectives: List[str] = field(default_factory=list)
    audit_period_start: str = ""
    audit_period_end: str = ""
    
    # Evidence summaries
    evidence_inventory: List[Dict[str, Any]] = field(default_factory=list)
    evidence_chain_verification: Dict[str, bool] = field(default_factory=dict)
    missing_evidence: List[str] = field(default_factory=list)
    
    # Risk assessment
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    identified_risks: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_measures: List[Dict[str, Any]] = field(default_factory=list)
    
    # Findings and recommendations
    audit_findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attestations and signatures
    auditor_attestation: Optional[str] = None
    management_response: Optional[str] = None
    external_auditor_signature: Optional[str] = None
    
    # Package integrity
    package_hash: Optional[str] = None
    digital_signature: Optional[str] = None
    
    def export_for_regulator(self, format_type: str = "json") -> str:
        """Export package in regulator-friendly format."""
        if format_type == "json":
            return self.to_json()
        elif format_type == "xml":
            # Implement XML export for specific regulatory requirements
            pass
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def validate_completeness(self) -> Dict[str, Any]:
        """Validate package completeness for regulatory submission."""
        validation_result = {
            "is_complete": True,
            "missing_components": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check required components
        if not self.source_capsule.capsule_id:
            validation_result["missing_components"].append("Source capsule missing")
            validation_result["is_complete"] = False
            
        if not self.regulatory_framework:
            validation_result["missing_components"].append("Regulatory framework not specified")
            validation_result["is_complete"] = False
            
        # Check evidence completeness
        completeness_score = self.source_capsule.get_completeness_score()
        if completeness_score < 0.8:
            validation_result["warnings"].append(f"Low evidence completeness: {completeness_score:.2%}")
            
        return validation_result