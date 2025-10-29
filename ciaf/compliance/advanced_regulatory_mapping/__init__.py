"""
Regulatory Mapping Framework

Comprehensive mapping of CIAF LCM evidence packages to regulatory requirements
including EU AI Act, NIST AI RMF, and ISO/IEC 42001.

Created: 2025-10-24
Author: Denzil James Greenwood
Version: 1.0.0
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RegulatoryFramework(Enum):
    """Major regulatory frameworks for AI systems."""
    EU_AI_ACT = "eu_ai_act"
    NIST_AI_RMF = "nist_ai_rmf"
    ISO_IEC_42001 = "iso_iec_42001"
    GDPR = "gdpr"
    SOX = "sarbanes_oxley"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    FTC_FAIRNESS = "ftc_fairness"
    CCPA = "ccpa"
    PIPEDA = "pipeda"


class ComplianceLevel(Enum):
    """Levels of compliance support."""
    FULL_COMPLIANCE = "full_compliance"
    SUBSTANTIAL_COMPLIANCE = "substantial_compliance"
    PARTIAL_COMPLIANCE = "partial_compliance"
    FRAMEWORK_SUPPORT = "framework_support"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class RegulatoryRequirement:
    """Definition of a regulatory requirement."""
    requirement_id: str
    framework: RegulatoryFramework
    article_section: str
    title: str
    description: str
    compliance_level: ComplianceLevel
    lcm_evidence_mapping: List[str]
    implementation_notes: str
    verification_methods: List[str]
    audit_trail_requirements: List[str]


@dataclass
class ComplianceMapping:
    """Mapping between LCM components and regulatory requirements."""
    lcm_component: str
    regulatory_requirements: List[RegulatoryRequirement]
    evidence_package: Dict[str, Any]
    compliance_score: float
    gap_analysis: List[str]
    recommendations: List[str]


class RegulatoryMappingFramework:
    """
    Comprehensive regulatory mapping framework for CIAF LCM.
    
    Maps LCM evidence packages to major regulatory frameworks including
    EU AI Act, NIST AI RMF, ISO/IEC 42001, and other relevant standards.
    """
    
    def __init__(self):
        """Initialize regulatory mapping framework."""
        self.regulatory_requirements = self._initialize_regulatory_requirements()
        self.lcm_compliance_mappings = self._initialize_lcm_mappings()
    
    def _initialize_regulatory_requirements(self) -> Dict[str, RegulatoryRequirement]:
        """Initialize comprehensive regulatory requirements database."""
        requirements = {}
        
        # EU AI Act Requirements
        requirements["eu_ai_act_art10"] = RegulatoryRequirement(
            requirement_id="eu_ai_act_art10",
            framework=RegulatoryFramework.EU_AI_ACT,
            article_section="Article 10",
            title="Data and data governance",
            description="Training, validation and testing data sets shall be subject to appropriate data governance and management practices",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "dataset_anchor_chain",
                "data_lineage_receipts",
                "training_session_validation",
                "merkle_proof_integrity"
            ],
            implementation_notes="LCM dataset anchors provide cryptographic data governance with tamper-evident lineage tracking",
            verification_methods=[
                "cryptographic_anchor_verification",
                "merkle_tree_validation",
                "audit_trail_inspection"
            ],
            audit_trail_requirements=[
                "complete_data_lineage",
                "access_control_logs",
                "modification_detection"
            ]
        )
        
        requirements["eu_ai_act_art15"] = RegulatoryRequirement(
            requirement_id="eu_ai_act_art15",
            framework=RegulatoryFramework.EU_AI_ACT,
            article_section="Article 15",
            title="Accuracy, robustness and cybersecurity",
            description="High-risk AI systems shall be designed and developed to achieve appropriate levels of accuracy, robustness and cybersecurity",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "model_anchor_signatures",
                "training_metrics_validation",
                "deployment_security_attestation",
                "inference_verification_receipts"
            ],
            implementation_notes="LCM provides cryptographic evidence of model integrity and security controls",
            verification_methods=[
                "digital_signature_validation",
                "performance_metrics_verification",
                "security_assessment_review"
            ],
            audit_trail_requirements=[
                "model_performance_tracking",
                "security_incident_logging",
                "robustness_testing_records"
            ]
        )
        
        requirements["eu_ai_act_art16"] = RegulatoryRequirement(
            requirement_id="eu_ai_act_art16",
            framework=RegulatoryFramework.EU_AI_ACT,
            article_section="Article 16",
            title="Quality management system",
            description="Providers of high-risk AI systems shall put in place a quality management system",
            compliance_level=ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            lcm_evidence_mapping=[
                "end_to_end_audit_chain",
                "quality_metrics_tracking",
                "compliance_validation_receipts",
                "continuous_monitoring_evidence"
            ],
            implementation_notes="LCM audit chains support quality management system documentation and verification",
            verification_methods=[
                "audit_chain_validation",
                "quality_metrics_assessment",
                "compliance_documentation_review"
            ],
            audit_trail_requirements=[
                "quality_procedure_documentation",
                "quality_control_records",
                "corrective_action_tracking"
            ]
        )
        
        # NIST AI RMF Requirements
        requirements["nist_ai_rmf_govern"] = RegulatoryRequirement(
            requirement_id="nist_ai_rmf_govern",
            framework=RegulatoryFramework.NIST_AI_RMF,
            article_section="GOVERN Function",
            title="Governance and oversight structures",
            description="Governance and oversight processes are in place for AI systems and risks",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "governance_anchor_signatures",
                "oversight_validation_receipts",
                "policy_enforcement_evidence",
                "stakeholder_approval_chains"
            ],
            implementation_notes="LCM supports governance through cryptographic policy enforcement and oversight validation",
            verification_methods=[
                "governance_signature_verification",
                "policy_compliance_checking",
                "oversight_documentation_review"
            ],
            audit_trail_requirements=[
                "governance_decision_records",
                "oversight_activity_logs",
                "policy_enforcement_evidence"
            ]
        )
        
        requirements["nist_ai_rmf_map"] = RegulatoryRequirement(
            requirement_id="nist_ai_rmf_map",
            framework=RegulatoryFramework.NIST_AI_RMF,
            article_section="MAP Function",
            title="Context and risk identification",
            description="AI systems and their risks are mapped and understood in context",
            compliance_level=ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            lcm_evidence_mapping=[
                "risk_assessment_anchors",
                "context_mapping_receipts",
                "impact_analysis_validation",
                "stakeholder_identification_evidence"
            ],
            implementation_notes="LCM provides cryptographic evidence of risk mapping and context analysis",
            verification_methods=[
                "risk_assessment_validation",
                "context_analysis_review",
                "impact_assessment_verification"
            ],
            audit_trail_requirements=[
                "risk_identification_records",
                "context_analysis_documentation",
                "stakeholder_mapping_evidence"
            ]
        )
        
        requirements["nist_ai_rmf_measure"] = RegulatoryRequirement(
            requirement_id="nist_ai_rmf_measure",
            framework=RegulatoryFramework.NIST_AI_RMF,
            article_section="MEASURE Function",
            title="Performance measurement and monitoring",
            description="AI system performance and risks are measured and monitored",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "performance_metrics_receipts",
                "monitoring_data_anchors",
                "measurement_validation_chains",
                "continuous_assessment_evidence"
            ],
            implementation_notes="LCM receipts provide tamper-evident performance measurement and monitoring evidence",
            verification_methods=[
                "metrics_integrity_verification",
                "monitoring_data_validation",
                "measurement_audit_review"
            ],
            audit_trail_requirements=[
                "performance_measurement_logs",
                "monitoring_system_records",
                "assessment_result_documentation"
            ]
        )
        
        # ISO/IEC 42001 Requirements
        requirements["iso_42001_s8"] = RegulatoryRequirement(
            requirement_id="iso_42001_s8",
            framework=RegulatoryFramework.ISO_IEC_42001,
            article_section="Section 8",
            title="Operation and AI system lifecycle",
            description="Organizations shall plan, implement and control AI system lifecycle processes",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "lifecycle_stage_anchors",
                "operation_control_receipts",
                "process_validation_chains",
                "lifecycle_audit_evidence"
            ],
            implementation_notes="LCM provides comprehensive lifecycle tracking with cryptographic process validation",
            verification_methods=[
                "lifecycle_stage_verification",
                "process_control_validation",
                "operation_audit_review"
            ],
            audit_trail_requirements=[
                "lifecycle_process_documentation",
                "operation_control_records",
                "process_validation_evidence"
            ]
        )
        
        requirements["iso_42001_s9"] = RegulatoryRequirement(
            requirement_id="iso_42001_s9",
            framework=RegulatoryFramework.ISO_IEC_42001,
            article_section="Section 9",
            title="Performance evaluation and monitoring",
            description="Organizations shall monitor, measure, analyze and evaluate AI system performance",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "performance_evaluation_receipts",
                "monitoring_result_anchors",
                "analysis_validation_chains",
                "evaluation_audit_evidence"
            ],
            implementation_notes="LCM receipts enable comprehensive performance evaluation with cryptographic integrity",
            verification_methods=[
                "evaluation_result_verification",
                "monitoring_data_validation",
                "analysis_audit_review"
            ],
            audit_trail_requirements=[
                "performance_evaluation_records",
                "monitoring_result_documentation",
                "analysis_methodology_evidence"
            ]
        )
        
        # GDPR Requirements (Data Protection)
        requirements["gdpr_art25"] = RegulatoryRequirement(
            requirement_id="gdpr_art25",
            framework=RegulatoryFramework.GDPR,
            article_section="Article 25",
            title="Data protection by design and by default",
            description="Data protection shall be integrated into processing activities by design and by default",
            compliance_level=ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            lcm_evidence_mapping=[
                "privacy_preserving_anchors",
                "data_minimization_receipts",
                "consent_validation_chains",
                "privacy_impact_evidence"
            ],
            implementation_notes="LCM supports privacy by design through cryptographic data protection mechanisms",
            verification_methods=[
                "privacy_mechanism_verification",
                "data_minimization_validation",
                "consent_audit_review"
            ],
            audit_trail_requirements=[
                "privacy_design_documentation",
                "data_protection_implementation_records",
                "privacy_assessment_evidence"
            ]
        )
        
        requirements["gdpr_art32"] = RegulatoryRequirement(
            requirement_id="gdpr_art32",
            framework=RegulatoryFramework.GDPR,
            article_section="Article 32",
            title="Security of processing",
            description="Appropriate technical and organizational measures to ensure security of processing",
            compliance_level=ComplianceLevel.FULL_COMPLIANCE,
            lcm_evidence_mapping=[
                "security_control_anchors",
                "encryption_validation_receipts",
                "access_control_chains",
                "security_audit_evidence"
            ],
            implementation_notes="LCM cryptographic controls provide strong security of processing evidence",
            verification_methods=[
                "security_control_verification",
                "encryption_validation",
                "access_control_audit"
            ],
            audit_trail_requirements=[
                "security_measure_documentation",
                "security_incident_records",
                "security_assessment_evidence"
            ]
        )
        
        return requirements
    
    def _initialize_lcm_mappings(self) -> Dict[str, ComplianceMapping]:
        """Initialize LCM component compliance mappings."""
        mappings = {}
        
        # Dataset Anchor Compliance
        dataset_requirements = [
            self.regulatory_requirements["eu_ai_act_art10"],
            self.regulatory_requirements["gdpr_art25"],
            self.regulatory_requirements["gdpr_art32"],
            self.regulatory_requirements["nist_ai_rmf_map"]
        ]
        
        mappings["dataset_anchor"] = ComplianceMapping(
            lcm_component="dataset_anchor",
            regulatory_requirements=dataset_requirements,
            evidence_package={
                "anchor_derivation_proof": "cryptographic_dataset_binding",
                "data_lineage_chain": "complete_provenance_tracking",
                "access_control_evidence": "authorized_access_validation",
                "privacy_protection_proof": "data_minimization_enforcement"
            },
            compliance_score=0.92,
            gap_analysis=[
                "Enhanced privacy-preserving computation support needed",
                "Additional cross-border transfer documentation required"
            ],
            recommendations=[
                "Implement differential privacy mechanisms",
                "Add GDPR Article 44-49 transfer documentation"
            ]
        )
        
        # Model Anchor Compliance
        model_requirements = [
            self.regulatory_requirements["eu_ai_act_art15"],
            self.regulatory_requirements["eu_ai_act_art16"],
            self.regulatory_requirements["nist_ai_rmf_govern"],
            self.regulatory_requirements["iso_42001_s8"]
        ]
        
        mappings["model_anchor"] = ComplianceMapping(
            lcm_component="model_anchor",
            regulatory_requirements=model_requirements,
            evidence_package={
                "model_integrity_proof": "cryptographic_model_binding",
                "training_validation_chain": "comprehensive_training_audit",
                "performance_metrics_evidence": "validated_accuracy_records",
                "security_assessment_proof": "cybersecurity_validation"
            },
            compliance_score=0.95,
            gap_analysis=[
                "Bias testing documentation could be enhanced",
                "Robustness testing evidence needs standardization"
            ],
            recommendations=[
                "Integrate automated bias detection in model anchoring",
                "Standardize robustness testing protocols"
            ]
        )
        
        # Training Session Compliance
        training_requirements = [
            self.regulatory_requirements["eu_ai_act_art10"],
            self.regulatory_requirements["eu_ai_act_art15"],
            self.regulatory_requirements["nist_ai_rmf_measure"],
            self.regulatory_requirements["iso_42001_s8"]
        ]
        
        mappings["training_session"] = ComplianceMapping(
            lcm_component="training_session",
            regulatory_requirements=training_requirements,
            evidence_package={
                "training_data_validation": "dataset_anchor_verification",
                "training_process_audit": "complete_training_log",
                "model_performance_validation": "metrics_validation_chain",
                "resource_attestation": "infrastructure_validation"
            },
            compliance_score=0.89,
            gap_analysis=[
                "Training environment standardization needed",
                "Enhanced hyperparameter audit trail required"
            ],
            recommendations=[
                "Implement standardized training environment attestation",
                "Add detailed hyperparameter change tracking"
            ]
        )
        
        # Deployment Anchor Compliance
        deployment_requirements = [
            self.regulatory_requirements["eu_ai_act_art15"],
            self.regulatory_requirements["eu_ai_act_art16"],
            self.regulatory_requirements["nist_ai_rmf_govern"],
            self.regulatory_requirements["iso_42001_s9"]
        ]
        
        mappings["deployment_anchor"] = ComplianceMapping(
            lcm_component="deployment_anchor",
            regulatory_requirements=deployment_requirements,
            evidence_package={
                "deployment_authorization": "multi_party_approval_chain",
                "security_validation": "comprehensive_security_assessment",
                "infrastructure_attestation": "deployment_environment_validation",
                "monitoring_setup": "continuous_monitoring_evidence"
            },
            compliance_score=0.91,
            gap_analysis=[
                "Incident response integration needed",
                "Performance degradation detection requires enhancement"
            ],
            recommendations=[
                "Integrate incident response workflow validation",
                "Add automated performance degradation alerts"
            ]
        )
        
        # Inference Receipt Compliance
        inference_requirements = [
            self.regulatory_requirements["eu_ai_act_art15"],
            self.regulatory_requirements["nist_ai_rmf_measure"],
            self.regulatory_requirements["iso_42001_s9"],
            self.regulatory_requirements["gdpr_art32"]
        ]
        
        mappings["inference_receipt"] = ComplianceMapping(
            lcm_component="inference_receipt",
            regulatory_requirements=inference_requirements,
            evidence_package={
                "inference_validation": "cryptographic_output_verification",
                "input_data_protection": "privacy_preserving_processing",
                "performance_monitoring": "real_time_metrics_validation",
                "audit_trail_evidence": "complete_inference_log"
            },
            compliance_score=0.87,
            gap_analysis=[
                "Real-time compliance monitoring needed",
                "Enhanced output explanation capabilities required"
            ],
            recommendations=[
                "Implement real-time compliance validation",
                "Add automated output explanation generation"
            ]
        )
        
        return mappings
    
    def generate_regulatory_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive regulatory compliance report."""
        report = {
            "executive_summary": self._generate_executive_summary(),
            "framework_coverage": self._analyze_framework_coverage(),
            "compliance_scores": self._calculate_compliance_scores(),
            "gap_analysis": self._consolidate_gap_analysis(),
            "recommendations": self._prioritize_recommendations(),
            "evidence_mapping": self._document_evidence_mapping(),
            "audit_readiness": self._assess_audit_readiness()
        }
        
        return report
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of compliance status."""
        total_requirements = len(self.regulatory_requirements)
        covered_requirements = sum(
            1 for mapping in self.lcm_compliance_mappings.values()
            for req in mapping.regulatory_requirements
        )
        
        avg_compliance_score = sum(
            mapping.compliance_score for mapping in self.lcm_compliance_mappings.values()
        ) / len(self.lcm_compliance_mappings)
        
        frameworks_covered = set(
            req.framework for mapping in self.lcm_compliance_mappings.values()
            for req in mapping.regulatory_requirements
        )
        
        return {
            "overall_compliance_score": avg_compliance_score,
            "requirements_coverage": f"{covered_requirements}/{total_requirements}",
            "frameworks_addressed": len(frameworks_covered),
            "framework_list": [fw.value for fw in frameworks_covered],
            "compliance_status": "substantial_compliance" if avg_compliance_score >= 0.8 else "partial_compliance",
            "audit_readiness": "high" if avg_compliance_score >= 0.9 else "medium",
            "key_strengths": [
                "Comprehensive cryptographic evidence generation",
                "End-to-end audit trail capability",
                "Multi-framework compliance support",
                "Automated evidence collection and validation"
            ],
            "priority_areas": [
                "Privacy-preserving computation enhancement",
                "Real-time compliance monitoring",
                "Cross-jurisdictional transfer documentation",
                "Automated bias detection integration"
            ]
        }
    
    def _analyze_framework_coverage(self) -> Dict[str, Any]:
        """Analyze coverage across regulatory frameworks."""
        framework_coverage = {}
        
        for framework in RegulatoryFramework:
            framework_requirements = [
                req for req in self.regulatory_requirements.values()
                if req.framework == framework
            ]
            
            covered_requirements = [
                req for mapping in self.lcm_compliance_mappings.values()
                for req in mapping.regulatory_requirements
                if req.framework == framework
            ]
            
            if framework_requirements:
                coverage_percentage = len(covered_requirements) / len(framework_requirements)
                
                framework_coverage[framework.value] = {
                    "total_requirements": len(framework_requirements),
                    "covered_requirements": len(covered_requirements),
                    "coverage_percentage": coverage_percentage,
                    "compliance_level": self._determine_framework_compliance_level(coverage_percentage),
                    "key_requirements": [req.article_section for req in covered_requirements],
                    "gap_count": len(framework_requirements) - len(covered_requirements)
                }
        
        return framework_coverage
    
    def _determine_framework_compliance_level(self, coverage_percentage: float) -> str:
        """Determine compliance level based on coverage percentage."""
        if coverage_percentage >= 0.95:
            return "full_compliance"
        elif coverage_percentage >= 0.80:
            return "substantial_compliance"
        elif coverage_percentage >= 0.60:
            return "partial_compliance"
        elif coverage_percentage >= 0.30:
            return "framework_support"
        else:
            return "not_applicable"
    
    def _calculate_compliance_scores(self) -> Dict[str, float]:
        """Calculate compliance scores by component and framework."""
        scores = {}
        
        # Component-level scores
        for component, mapping in self.lcm_compliance_mappings.items():
            scores[f"component_{component}"] = mapping.compliance_score
        
        # Framework-level scores
        framework_scores = {}
        for framework in RegulatoryFramework:
            framework_mappings = [
                mapping for mapping in self.lcm_compliance_mappings.values()
                if any(req.framework == framework for req in mapping.regulatory_requirements)
            ]
            
            if framework_mappings:
                framework_scores[framework.value] = sum(
                    mapping.compliance_score for mapping in framework_mappings
                ) / len(framework_mappings)
        
        scores.update(framework_scores)
        return scores
    
    def _consolidate_gap_analysis(self) -> Dict[str, List[str]]:
        """Consolidate gap analysis across all components."""
        gaps_by_category = {
            "privacy_protection": [],
            "security_controls": [],
            "audit_capabilities": [],
            "performance_monitoring": [],
            "documentation": [],
            "automation": []
        }
        
        for component, mapping in self.lcm_compliance_mappings.items():
            for gap in mapping.gap_analysis:
                # Categorize gaps
                if any(keyword in gap.lower() for keyword in ["privacy", "gdpr", "consent"]):
                    gaps_by_category["privacy_protection"].append(f"{component}: {gap}")
                elif any(keyword in gap.lower() for keyword in ["security", "cyber", "encryption"]):
                    gaps_by_category["security_controls"].append(f"{component}: {gap}")
                elif any(keyword in gap.lower() for keyword in ["audit", "trail", "documentation"]):
                    gaps_by_category["audit_capabilities"].append(f"{component}: {gap}")
                elif any(keyword in gap.lower() for keyword in ["monitoring", "performance", "metrics"]):
                    gaps_by_category["performance_monitoring"].append(f"{component}: {gap}")
                elif any(keyword in gap.lower() for keyword in ["document", "standard", "protocol"]):
                    gaps_by_category["documentation"].append(f"{component}: {gap}")
                else:
                    gaps_by_category["automation"].append(f"{component}: {gap}")
        
        return gaps_by_category
    
    def _prioritize_recommendations(self) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on compliance impact."""
        all_recommendations = []
        
        for component, mapping in self.lcm_compliance_mappings.items():
            for recommendation in mapping.recommendations:
                # Calculate priority based on compliance score and regulatory impact
                priority_score = (1 - mapping.compliance_score) * len(mapping.regulatory_requirements)
                
                all_recommendations.append({
                    "recommendation": recommendation,
                    "component": component,
                    "priority_score": priority_score,
                    "affected_frameworks": [req.framework.value for req in mapping.regulatory_requirements],
                    "implementation_complexity": "medium",  # Default complexity
                    "estimated_compliance_improvement": 0.05  # Default improvement
                })
        
        # Sort by priority score (descending)
        all_recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return all_recommendations[:10]  # Return top 10 recommendations
    
    def _document_evidence_mapping(self) -> Dict[str, Any]:
        """Document evidence mapping for audit purposes."""
        evidence_mapping = {
            "lcm_component_evidence": {},
            "regulatory_requirement_evidence": {},
            "cross_reference_matrix": {}
        }
        
        # Map LCM components to evidence
        for component, mapping in self.lcm_compliance_mappings.items():
            evidence_mapping["lcm_component_evidence"][component] = {
                "evidence_package": mapping.evidence_package,
                "compliance_score": mapping.compliance_score,
                "applicable_requirements": [req.requirement_id for req in mapping.regulatory_requirements]
            }
        
        # Map regulatory requirements to evidence
        for req_id, requirement in self.regulatory_requirements.items():
            evidence_mapping["regulatory_requirement_evidence"][req_id] = {
                "framework": requirement.framework.value,
                "article_section": requirement.article_section,
                "lcm_evidence": requirement.lcm_evidence_mapping,
                "verification_methods": requirement.verification_methods,
                "audit_requirements": requirement.audit_trail_requirements
            }
        
        # Create cross-reference matrix
        for component, mapping in self.lcm_compliance_mappings.items():
            evidence_mapping["cross_reference_matrix"][component] = {}
            for requirement in mapping.regulatory_requirements:
                evidence_mapping["cross_reference_matrix"][component][requirement.requirement_id] = {
                    "compliance_level": requirement.compliance_level.value,
                    "evidence_strength": "strong" if requirement.compliance_level in [
                        ComplianceLevel.FULL_COMPLIANCE, ComplianceLevel.SUBSTANTIAL_COMPLIANCE
                    ] else "moderate"
                }
        
        return evidence_mapping
    
    def _assess_audit_readiness(self) -> Dict[str, Any]:
        """Assess audit readiness across regulatory frameworks."""
        audit_readiness = {
            "overall_readiness": "high",
            "framework_readiness": {},
            "evidence_completeness": {},
            "audit_preparation_checklist": []
        }
        
        # Assess readiness by framework
        for framework in RegulatoryFramework:
            framework_requirements = [
                req for req in self.regulatory_requirements.values()
                if req.framework == framework
            ]
            
            if framework_requirements:
                covered_count = sum(
                    1 for mapping in self.lcm_compliance_mappings.values()
                    for req in mapping.regulatory_requirements
                    if req.framework == framework
                )
                
                readiness_score = covered_count / len(framework_requirements)
                
                if readiness_score >= 0.9:
                    readiness_level = "high"
                elif readiness_score >= 0.7:
                    readiness_level = "medium"
                else:
                    readiness_level = "low"
                
                audit_readiness["framework_readiness"][framework.value] = {
                    "readiness_level": readiness_level,
                    "readiness_score": readiness_score,
                    "evidence_gaps": len(framework_requirements) - covered_count
                }
        
        # Assess evidence completeness
        for component, mapping in self.lcm_compliance_mappings.items():
            audit_readiness["evidence_completeness"][component] = {
                "evidence_packages": len(mapping.evidence_package),
                "verification_methods": len(set(
                    method for req in mapping.regulatory_requirements
                    for method in req.verification_methods
                )),
                "audit_trail_coverage": len(set(
                    trail for req in mapping.regulatory_requirements
                    for trail in req.audit_trail_requirements
                )),
                "completeness_score": mapping.compliance_score
            }
        
        # Generate audit preparation checklist
        audit_readiness["audit_preparation_checklist"] = [
            "Verify all cryptographic signatures and anchors",
            "Validate Merkle tree integrity across all components",
            "Review audit trail completeness for each regulatory requirement",
            "Confirm evidence package availability and accessibility",
            "Test verification methods and procedures",
            "Prepare regulatory mapping documentation",
            "Validate cross-jurisdictional compliance mechanisms",
            "Review and update incident response procedures",
            "Confirm key management and rotation procedures",
            "Prepare compliance demonstration scenarios"
        ]
        
        return audit_readiness