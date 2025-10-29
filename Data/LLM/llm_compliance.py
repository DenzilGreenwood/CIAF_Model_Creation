"""
LLM Compliance Monitoring

Implements compliance monitoring and validation for LLM operations
following CIAF policy framework and regulatory requirements.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    PENDING = "pending"
    NOT_APPLICABLE = "not_applicable"


class RegulatoryFramework(Enum):
    """Supported regulatory frameworks."""
    GDPR = "gdpr"
    AI_ACT = "ai_act"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST_AI_RMF = "nist_ai_rmf"
    CUSTOM = "custom"


@dataclass
class ComplianceViolation:
    """Represents a compliance violation."""
    violation_id: str
    framework: str
    requirement: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation_steps: List[str] = field(default_factory=list)
    status: str = "open"  # 'open', 'investigating', 'resolved', 'accepted_risk'


@dataclass
class ComplianceResult:
    """Result of compliance validation."""
    is_compliant: bool
    framework: str
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessment_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    assessment_version: str = "1.0"


class LLMComplianceMonitor:
    """
    Comprehensive compliance monitoring for LLM operations.
    Validates adherence to CIAF policies and regulatory frameworks.
    """
    
    def __init__(self, policy: Any, frameworks: Optional[List[RegulatoryFramework]] = None):
        """Initialize compliance monitor with policy and regulatory frameworks."""
        self.policy = policy
        self.frameworks = frameworks or [RegulatoryFramework.NIST_AI_RMF]
        self.violation_history: List[ComplianceViolation] = []
        self.compliance_cache: Dict[str, ComplianceResult] = {}
        
        # Load compliance rules for each framework
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance rules for supported frameworks."""
        return {
            RegulatoryFramework.GDPR.value: {
                "data_minimization": {
                    "description": "Process only necessary personal data",
                    "checks": ["data_purpose_limitation", "storage_limitation"]
                },
                "consent_management": {
                    "description": "Obtain and manage user consent",
                    "checks": ["explicit_consent", "consent_withdrawal"]
                },
                "data_protection_by_design": {
                    "description": "Implement privacy by design",
                    "checks": ["privacy_impact_assessment", "data_protection_measures"]
                }
            },
            RegulatoryFramework.AI_ACT.value: {
                "high_risk_ai_requirements": {
                    "description": "Requirements for high-risk AI systems",
                    "checks": ["risk_management", "data_governance", "transparency"]
                },
                "human_oversight": {
                    "description": "Ensure adequate human oversight",
                    "checks": ["human_in_the_loop", "meaningful_control"]
                },
                "accuracy_robustness": {
                    "description": "Ensure AI system accuracy and robustness",
                    "checks": ["performance_monitoring", "error_handling"]
                }
            },
            RegulatoryFramework.NIST_AI_RMF.value: {
                "governance": {
                    "description": "Establish AI governance structures",
                    "checks": ["governance_framework", "accountability", "documentation"]
                },
                "bias_management": {
                    "description": "Identify and manage AI bias",
                    "checks": ["bias_assessment", "fairness_metrics", "mitigation_strategies"]
                },
                "security": {
                    "description": "Ensure AI system security",
                    "checks": ["threat_modeling", "security_controls", "incident_response"]
                },
                "explainability": {
                    "description": "Provide AI system explainability",
                    "checks": ["interpretability", "transparency", "auditability"]
                }
            }
        }
    
    def validate_dataset_anchor(self, anchor: Any) -> ComplianceResult:
        """Validate dataset anchor compliance."""
        violations = []
        warnings = []
        recommendations = []
        
        # Check data privacy classification
        if hasattr(anchor, 'privacy_classification'):
            if anchor.privacy_classification == "unclassified" and anchor.contains_pii:
                violations.append(ComplianceViolation(
                    violation_id=f"data_privacy_{anchor.anchor_id}",
                    framework="GDPR",
                    requirement="Data Classification",
                    severity="high",
                    description="Dataset contains PII but is classified as unclassified",
                    evidence={"anchor_id": anchor.anchor_id, "contains_pii": anchor.contains_pii}
                ))
        
        # Check data retention policy
        if hasattr(anchor, 'data_retention_policy'):
            if not anchor.data_retention_policy:
                warnings.append("Data retention policy not specified")
                recommendations.append("Define clear data retention policy")
        
        # Check preprocessing transparency
        if hasattr(anchor, 'preprocessing_steps'):
            if not anchor.preprocessing_steps:
                warnings.append("Preprocessing steps not documented")
                recommendations.append("Document all data preprocessing steps for transparency")
        
        return ComplianceResult(
            is_compliant=len(violations) == 0,
            framework="multi-framework",
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def validate_model_anchor(self, anchor: Any) -> ComplianceResult:
        """Validate model anchor compliance."""
        violations = []
        warnings = []
        recommendations = []
        
        # Check bias assessment
        if hasattr(anchor, 'bias_assessment'):
            if not anchor.bias_assessment:
                violations.append(ComplianceViolation(
                    violation_id=f"bias_assessment_{anchor.anchor_id}",
                    framework="NIST_AI_RMF",
                    requirement="Bias Management",
                    severity="medium",
                    description="Model bias assessment not performed",
                    evidence={"anchor_id": anchor.anchor_id}
                ))
        
        # Check safety evaluation
        if hasattr(anchor, 'safety_evaluation'):
            if not anchor.safety_evaluation:
                warnings.append("Safety evaluation not documented")
                recommendations.append("Perform comprehensive safety evaluation")
        
        # Check model documentation
        if hasattr(anchor, 'architecture'):
            if not anchor.architecture:
                warnings.append("Model architecture not fully documented")
        
        return ComplianceResult(
            is_compliant=len(violations) == 0,
            framework="multi-framework",
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def validate_deployment_anchor(self, anchor: Any) -> ComplianceResult:
        """Validate deployment anchor compliance."""
        violations = []
        warnings = []
        recommendations = []
        
        # Check access controls
        if hasattr(anchor, 'access_controls'):
            if not anchor.access_controls:
                violations.append(ComplianceViolation(
                    violation_id=f"access_control_{anchor.anchor_id}",
                    framework="ISO_27001",
                    requirement="Access Control",
                    severity="high",
                    description="No access controls defined for deployment",
                    evidence={"anchor_id": anchor.anchor_id}
                ))
        
        # Check monitoring configuration
        if hasattr(anchor, 'monitoring_config'):
            if not anchor.monitoring_config:
                warnings.append("Monitoring configuration not specified")
                recommendations.append("Configure comprehensive monitoring for production deployment")
        
        # Check content filtering
        if hasattr(anchor, 'content_filtering'):
            if not anchor.content_filtering:
                warnings.append("Content filtering not configured")
                recommendations.append("Implement content filtering to prevent harmful outputs")
        
        return ComplianceResult(
            is_compliant=len(violations) == 0,
            framework="multi-framework",
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def validate_inference_receipt(self, receipt: Any) -> ComplianceResult:
        """Validate inference receipt compliance."""
        violations = []
        warnings = []
        recommendations = []
        
        # Check safety scoring
        if hasattr(receipt, 'safety_score'):
            if receipt.safety_score is not None and receipt.safety_score < 0.5:
                violations.append(ComplianceViolation(
                    violation_id=f"safety_score_{receipt.receipt_id}",
                    framework="AI_ACT",
                    requirement="Safety Requirements",
                    severity="medium",
                    description=f"Low safety score detected: {receipt.safety_score}",
                    evidence={"receipt_id": receipt.receipt_id, "safety_score": receipt.safety_score}
                ))
        
        # Check for content flags
        if hasattr(receipt, 'content_flags'):
            if receipt.content_flags:
                violations.append(ComplianceViolation(
                    violation_id=f"content_flags_{receipt.receipt_id}",
                    framework="AI_ACT",
                    requirement="Content Safety",
                    severity="high",
                    description=f"Content safety flags detected: {receipt.content_flags}",
                    evidence={"receipt_id": receipt.receipt_id, "flags": receipt.content_flags}
                ))
        
        return ComplianceResult(
            is_compliant=len(violations) == 0,
            framework="multi-framework",
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        total_violations = len(self.violation_history)
        critical_violations = sum(1 for v in self.violation_history if v.severity == "critical")
        high_violations = sum(1 for v in self.violation_history if v.severity == "high")
        
        framework_breakdown = {}
        for violation in self.violation_history:
            framework = violation.framework
            if framework not in framework_breakdown:
                framework_breakdown[framework] = {"total": 0, "critical": 0, "high": 0, "open": 0}
            framework_breakdown[framework]["total"] += 1
            if violation.severity == "critical":
                framework_breakdown[framework]["critical"] += 1
            elif violation.severity == "high":
                framework_breakdown[framework]["high"] += 1
            if violation.status == "open":
                framework_breakdown[framework]["open"] += 1
        
        return {
            "report_generated": datetime.utcnow().isoformat() + 'Z',
            "summary": {
                "total_violations": total_violations,
                "critical_violations": critical_violations,
                "high_violations": high_violations,
                "overall_compliance_score": max(0, 1 - (critical_violations * 0.3 + high_violations * 0.1))
            },
            "framework_breakdown": framework_breakdown,
            "recent_violations": [
                {
                    "id": v.violation_id,
                    "framework": v.framework,
                    "severity": v.severity,
                    "description": v.description,
                    "detected_at": v.detected_at
                } for v in sorted(self.violation_history, key=lambda x: x.detected_at, reverse=True)[:10]
            ],
            "recommendations": self._generate_top_recommendations()
        }
    
    def _generate_top_recommendations(self) -> List[str]:
        """Generate top compliance recommendations."""
        recommendations = []
        
        # Analyze violation patterns
        violation_patterns = {}
        for violation in self.violation_history:
            if violation.status == "open":
                key = f"{violation.framework}:{violation.requirement}"
                violation_patterns[key] = violation_patterns.get(key, 0) + 1
        
        # Generate recommendations based on patterns
        if violation_patterns:
            top_pattern = max(violation_patterns, key=violation_patterns.get)
            framework, requirement = top_pattern.split(":", 1)
            recommendations.append(f"Priority focus needed on {requirement} compliance for {framework}")
        
        recommendations.extend([
            "Implement automated compliance monitoring dashboards",
            "Establish regular compliance review cycles",
            "Enhance documentation of AI system decisions",
            "Strengthen data governance processes",
            "Improve bias detection and mitigation procedures"
        ])
        
        return recommendations[:5]
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate compliance summary for capsule headers."""
        report = self.generate_compliance_report()
        
        return {
            "compliance_score": report["summary"]["overall_compliance_score"],
            "total_violations": report["summary"]["total_violations"],
            "critical_violations": report["summary"]["critical_violations"],
            "frameworks_assessed": list(self.compliance_rules.keys()),
            "last_assessment": datetime.utcnow().isoformat() + 'Z',
            "status": "compliant" if report["summary"]["critical_violations"] == 0 else "non_compliant"
        }