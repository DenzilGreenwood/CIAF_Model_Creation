"""
Defense & Aerospace AI Governance Framework
==========================================

Comprehensive AI governance for defense and aerospace systems including:
- Military AI systems safety and reliability requirements
- Autonomous weapons systems governance and international law compliance
- National security AI classification and access control
- Defense contractor AI oversight and supply chain security
- Military personnel AI training and human-machine teaming
- Intelligence AI systems and data protection
- Cybersecurity for defense AI infrastructure
- International defense AI cooperation and export controls

Key Components:
- Military AI safety certification and testing protocols
- Autonomous systems human oversight and control requirements
- Classified AI systems security and compartmentalization
- Defense industrial base AI governance and vendor management
- Military ethics and rules of engagement for AI systems
- Intelligence community AI oversight and civil liberties protection
- Defense AI interoperability and allied cooperation frameworks
- Export control compliance for defense AI technologies
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from ciaf.core.interfaces import AIGovernanceFramework
from ciaf.compliance.bias_validator import BiasValidator
from ciaf.compliance.audit_trails import AuditTrail
from ciaf.compliance.validators import ComplianceValidator

class DefenseAIApplication(Enum):
    """Types of defense AI applications"""
    AUTONOMOUS_WEAPONS = "autonomous_weapons"
    SURVEILLANCE_RECONNAISSANCE = "surveillance_reconnaissance"
    INTELLIGENCE_ANALYSIS = "intelligence_analysis"
    COMMAND_CONTROL = "command_control"
    LOGISTICS_SUPPLY_CHAIN = "logistics_supply_chain"
    CYBERSECURITY_DEFENSE = "cybersecurity_defense"
    PILOT_ASSISTANCE = "pilot_assistance"
    TARGET_IDENTIFICATION = "target_identification"
    THREAT_ASSESSMENT = "threat_assessment"
    TRAINING_SIMULATION = "training_simulation"
    COMMUNICATIONS_JAMMING = "communications_jamming"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"

class ClassificationLevel(Enum):
    """Security classification levels"""
    UNCLASSIFIED = "unclassified"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    SPECIAL_ACCESS_PROGRAM = "special_access_program"
    COMPARTMENTED_INFORMATION = "compartmented_information"

class AutonomyLevel(Enum):
    """Levels of autonomy in defense AI systems"""
    HUMAN_OPERATED = "human_operated"           # Full human control
    HUMAN_DELEGATED = "human_delegated"         # Human delegates specific tasks
    HUMAN_SUPERVISED = "human_supervised"       # Human monitors and can intervene
    HUMAN_INITIATED = "human_initiated"         # Human starts process, AI continues
    HUMAN_GOVERNED = "human_governed"           # Human sets rules, AI operates within
    FULLY_AUTONOMOUS = "fully_autonomous"       # No human intervention required

class ThreatLevel(Enum):
    """Defense threat assessment levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXISTENTIAL = "existential"

@dataclass
class MilitaryAISafetyAssessment:
    """Assessment of military AI system safety and reliability"""
    assessment_id: str
    system_id: str
    ai_application: DefenseAIApplication
    classification_level: ClassificationLevel
    autonomy_level: AutonomyLevel
    safety_certification_status: Dict[str, bool]
    reliability_metrics: Dict[str, float]
    failure_mode_analysis: Dict[str, Any]
    human_oversight_requirements: Dict[str, bool]
    kill_switch_mechanisms: Dict[str, bool]
    testing_validation_results: Dict[str, float]
    environmental_robustness: Dict[str, float]
    adversarial_resilience: Dict[str, float]
    interoperability_compliance: Dict[str, bool]
    rules_of_engagement_integration: Dict[str, bool]
    international_law_compliance: Dict[str, bool]
    ethical_constraints_implementation: List[str]
    civilian_harm_prevention: Dict[str, float]
    collateral_damage_assessment: Dict[str, Any]
    assessment_timestamp: datetime
    safety_assessor_id: str
    
    def calculate_military_safety_score(self) -> float:
        """Calculate military AI system safety score"""
        
        # Safety certification status
        certification_score = sum(self.safety_certification_status.values()) / len(self.safety_certification_status) if self.safety_certification_status else 0.0
        
        # Reliability metrics
        avg_reliability = sum(self.reliability_metrics.values()) / len(self.reliability_metrics) if self.reliability_metrics else 0.0
        
        # Human oversight compliance
        oversight_score = sum(self.human_oversight_requirements.values()) / len(self.human_oversight_requirements) if self.human_oversight_requirements else 0.0
        
        # Kill switch availability (critical for high autonomy)
        kill_switch_score = sum(self.kill_switch_mechanisms.values()) / len(self.kill_switch_mechanisms) if self.kill_switch_mechanisms else 0.0
        
        # International law compliance
        law_compliance_score = sum(self.international_law_compliance.values()) / len(self.international_law_compliance) if self.international_law_compliance else 0.0
        
        # Civilian harm prevention
        civilian_protection_score = sum(self.civilian_harm_prevention.values()) / len(self.civilian_harm_prevention) if self.civilian_harm_prevention else 0.0
        
        # Weight scores based on autonomy level
        if self.autonomy_level in [AutonomyLevel.FULLY_AUTONOMOUS, AutonomyLevel.HUMAN_GOVERNED]:
            # Higher autonomy requires higher safety standards
            return (
                certification_score * 0.2 +
                avg_reliability * 0.2 +
                oversight_score * 0.15 +
                kill_switch_score * 0.15 +
                law_compliance_score * 0.15 +
                civilian_protection_score * 0.15
            )
        else:
            # Lower autonomy, standard safety weighting
            return (
                certification_score * 0.25 +
                avg_reliability * 0.25 +
                oversight_score * 0.2 +
                law_compliance_score * 0.15 +
                civilian_protection_score * 0.15
            )

@dataclass
class SecurityClassificationAssessment:
    """Assessment of defense AI security and classification compliance"""
    assessment_id: str
    system_id: str
    classification_level: ClassificationLevel
    access_control_implementation: Dict[str, bool]
    compartmentalization_compliance: Dict[str, bool]
    clearance_level_verification: Dict[str, bool]
    need_to_know_enforcement: Dict[str, bool]
    data_encryption_standards: Dict[str, bool]
    secure_communication_protocols: Dict[str, bool]
    physical_security_measures: Dict[str, bool]
    personnel_security_screening: Dict[str, bool]
    foreign_national_restrictions: Dict[str, bool]
    technology_transfer_controls: Dict[str, bool]
    export_control_compliance: Dict[str, bool]
    counterintelligence_measures: Dict[str, bool]
    supply_chain_security: Dict[str, float]
    insider_threat_mitigation: Dict[str, float]
    breach_detection_capabilities: Dict[str, float]
    incident_response_procedures: List[str]
    security_audit_results: Dict[str, float]
    assessment_timestamp: datetime
    security_officer_id: str
    
    def calculate_security_compliance_score(self) -> float:
        """Calculate security classification compliance score"""
        
        # Access control and compartmentalization
        access_score = sum(self.access_control_implementation.values()) / len(self.access_control_implementation) if self.access_control_implementation else 0.0
        compartment_score = sum(self.compartmentalization_compliance.values()) / len(self.compartmentalization_compliance) if self.compartmentalization_compliance else 0.0
        
        # Personnel security
        clearance_score = sum(self.clearance_level_verification.values()) / len(self.clearance_level_verification) if self.clearance_level_verification else 0.0
        personnel_score = sum(self.personnel_security_screening.values()) / len(self.personnel_security_screening) if self.personnel_security_screening else 0.0
        
        # Technical security
        encryption_score = sum(self.data_encryption_standards.values()) / len(self.data_encryption_standards) if self.data_encryption_standards else 0.0
        communication_score = sum(self.secure_communication_protocols.values()) / len(self.secure_communication_protocols) if self.secure_communication_protocols else 0.0
        
        # Supply chain and export control
        supply_chain_score = sum(self.supply_chain_security.values()) / len(self.supply_chain_security) if self.supply_chain_security else 0.0
        export_control_score = sum(self.export_control_compliance.values()) / len(self.export_control_compliance) if self.export_control_compliance else 0.0
        
        # Threat detection and response
        threat_detection_score = sum(self.insider_threat_mitigation.values()) / len(self.insider_threat_mitigation) if self.insider_threat_mitigation else 0.0
        breach_detection_score = sum(self.breach_detection_capabilities.values()) / len(self.breach_detection_capabilities) if self.breach_detection_capabilities else 0.0
        
        return (
            access_score * 0.15 +
            compartment_score * 0.15 +
            clearance_score * 0.1 +
            personnel_score * 0.1 +
            encryption_score * 0.1 +
            communication_score * 0.1 +
            supply_chain_score * 0.1 +
            export_control_score * 0.1 +
            threat_detection_score * 0.05 +
            breach_detection_score * 0.05
        )

@dataclass
class AutonomousWeaponsAssessment:
    """Assessment of autonomous weapons systems compliance"""
    assessment_id: str
    weapons_system_id: str
    autonomy_level: AutonomyLevel
    human_oversight_requirements: Dict[str, bool]
    meaningful_human_control: Dict[str, bool]
    target_discrimination_capability: float
    civilian_protection_measures: Dict[str, float]
    proportionality_assessment: Dict[str, float]
    rules_of_engagement_compliance: Dict[str, bool]
    international_humanitarian_law: Dict[str, bool]
    ethical_kill_switch_implementation: bool
    operator_training_requirements: List[str]
    accountability_mechanisms: List[str]
    legal_review_completion: Dict[str, bool]
    command_responsibility_chain: Dict[str, str]
    post_action_review_procedures: List[str]
    civilian_casualty_tracking: Dict[str, Any]
    weapons_review_board_approval: bool
    international_treaty_compliance: Dict[str, bool]
    assessment_timestamp: datetime
    weapons_assessor_id: str
    
    def calculate_autonomous_weapons_compliance_score(self) -> float:
        """Calculate autonomous weapons system compliance score"""
        
        # Human control and oversight
        human_oversight_score = sum(self.human_oversight_requirements.values()) / len(self.human_oversight_requirements) if self.human_oversight_requirements else 0.0
        human_control_score = sum(self.meaningful_human_control.values()) / len(self.meaningful_human_control) if self.meaningful_human_control else 0.0
        
        # Target discrimination and civilian protection
        discrimination_score = self.target_discrimination_capability
        civilian_protection_score = sum(self.civilian_protection_measures.values()) / len(self.civilian_protection_measures) if self.civilian_protection_measures else 0.0
        
        # International law compliance
        roe_compliance_score = sum(self.rules_of_engagement_compliance.values()) / len(self.rules_of_engagement_compliance) if self.rules_of_engagement_compliance else 0.0
        ihl_compliance_score = sum(self.international_humanitarian_law.values()) / len(self.international_humanitarian_law) if self.international_humanitarian_law else 0.0
        
        # Legal and ethical review
        legal_review_score = sum(self.legal_review_completion.values()) / len(self.legal_review_completion) if self.legal_review_completion else 0.0
        weapons_review_score = 1.0 if self.weapons_review_board_approval else 0.0
        
        # Kill switch requirement (mandatory for high autonomy)
        kill_switch_score = 1.0 if self.ethical_kill_switch_implementation else 0.0
        
        # Higher autonomy levels require stricter compliance
        if self.autonomy_level in [AutonomyLevel.FULLY_AUTONOMOUS, AutonomyLevel.HUMAN_GOVERNED]:
            return (
                human_oversight_score * 0.2 +
                human_control_score * 0.2 +
                discrimination_score * 0.15 +
                civilian_protection_score * 0.15 +
                ihl_compliance_score * 0.1 +
                kill_switch_score * 0.1 +
                legal_review_score * 0.05 +
                weapons_review_score * 0.05
            )
        else:
            return (
                human_oversight_score * 0.15 +
                human_control_score * 0.15 +
                discrimination_score * 0.2 +
                civilian_protection_score * 0.2 +
                ihl_compliance_score * 0.15 +
                legal_review_score * 0.075 +
                weapons_review_score * 0.075 +
                kill_switch_score * 0.05
            )

@dataclass
class IntelligenceAIAssessment:
    """Assessment of AI systems used in intelligence operations"""
    assessment_id: str
    intelligence_system_id: str
    classification_level: ClassificationLevel
    collection_authorization_compliance: Dict[str, bool]
    privacy_protection_measures: Dict[str, bool]
    us_person_protections: Dict[str, bool]  # For US systems
    oversight_mechanism_implementation: Dict[str, bool]
    data_minimization_compliance: Dict[str, bool]
    retention_limitation_adherence: Dict[str, int]
    dissemination_controls: Dict[str, bool]
    bias_detection_intelligence: Dict[str, float]
    analytical_tradecraft_standards: Dict[str, bool]
    source_reliability_assessment: Dict[str, float]
    confidence_level_reporting: Dict[str, bool]
    alternative_analysis_provision: Dict[str, bool]
    civil_liberties_protection: Dict[str, bool]
    congressional_notification_compliance: List[str]
    inspector_general_oversight: Dict[str, bool]
    foreign_intelligence_targeting: Dict[str, bool]
    assessment_timestamp: datetime
    intelligence_officer_id: str
    
    def calculate_intelligence_compliance_score(self) -> float:
        """Calculate intelligence AI system compliance score"""
        
        # Collection authorization
        authorization_score = sum(self.collection_authorization_compliance.values()) / len(self.collection_authorization_compliance) if self.collection_authorization_compliance else 0.0
        
        # Privacy and civil liberties protection
        privacy_score = sum(self.privacy_protection_measures.values()) / len(self.privacy_protection_measures) if self.privacy_protection_measures else 0.0
        us_person_score = sum(self.us_person_protections.values()) / len(self.us_person_protections) if self.us_person_protections else 1.0  # N/A for non-US
        civil_liberties_score = sum(self.civil_liberties_protection.values()) / len(self.civil_liberties_protection) if self.civil_liberties_protection else 0.0
        
        # Data handling compliance
        minimization_score = sum(self.data_minimization_compliance.values()) / len(self.data_minimization_compliance) if self.data_minimization_compliance else 0.0
        dissemination_score = sum(self.dissemination_controls.values()) / len(self.dissemination_controls) if self.dissemination_controls else 0.0
        
        # Analytical quality and bias
        tradecraft_score = sum(self.analytical_tradecraft_standards.values()) / len(self.analytical_tradecraft_standards) if self.analytical_tradecraft_standards else 0.0
        bias_score = 1.0 - (sum(self.bias_detection_intelligence.values()) / len(self.bias_detection_intelligence)) if self.bias_detection_intelligence else 1.0
        
        # Oversight and accountability
        oversight_score = sum(self.oversight_mechanism_implementation.values()) / len(self.oversight_mechanism_implementation) if self.oversight_mechanism_implementation else 0.0
        ig_oversight_score = sum(self.inspector_general_oversight.values()) / len(self.inspector_general_oversight) if self.inspector_general_oversight else 0.0
        
        return (
            authorization_score * 0.15 +
            privacy_score * 0.15 +
            us_person_score * 0.1 +
            civil_liberties_score * 0.1 +
            minimization_score * 0.1 +
            dissemination_score * 0.1 +
            tradecraft_score * 0.1 +
            bias_score * 0.1 +
            oversight_score * 0.05 +
            ig_oversight_score * 0.05
        )

class DefenseAIGovernanceFramework(AIGovernanceFramework):
    """
    Defense & Aerospace AI Governance Framework
    
    Implements comprehensive governance for defense AI systems with focus on:
    - Military AI safety certification and reliability requirements
    - Autonomous weapons systems compliance with international law
    - National security classification and access control systems
    - Defense contractor oversight and supply chain security
    - Intelligence AI civil liberties and privacy protection
    - Military ethics and rules of engagement integration
    - International defense cooperation and export control compliance
    - Cybersecurity for critical defense AI infrastructure
    """
    
    def __init__(self, defense_organization_id: str, classification_level: ClassificationLevel, **kwargs):
        super().__init__(**kwargs)
        self.defense_organization_id = defense_organization_id
        self.classification_level = classification_level
        self.bias_validator = BiasValidator()
        self.audit_trail = AuditTrail()
        self.compliance_validator = ComplianceValidator()
        
        # Defense and security regulatory frameworks
        self.regulatory_standards = [
            "DoD_AI_Strategy",                    # Department of Defense AI Strategy
            "JAIC_AI_Principles",                # Joint AI Center principles
            "International_Humanitarian_Law",     # Geneva Conventions, etc.
            "Rules_of_Engagement",               # Military ROE compliance
            "ITAR_Export_Controls",              # International Traffic in Arms Regulations
            "EAR_Export_Controls",               # Export Administration Regulations
            "NISPOM_Security_Standards",         # National Industrial Security Program
            "FISMA_Cybersecurity",               # Federal Information Security Management Act
            "Intelligence_Oversight_Rules",       # Intelligence community oversight
            "Civil_Liberties_Protection",        # Civil liberties and privacy protection
            "NATO_STANAG_Standards",             # NATO standardization agreements
            "Autonomous_Weapons_Protocols",      # Emerging autonomous weapons protocols
            "Defense_Contractor_Standards"       # Defense industrial base requirements
        ]
        
        self.safety_assessments = {}
        self.security_assessments = {}
        self.weapons_assessments = {}
        self.intelligence_assessments = {}
        
    def assess_military_ai_safety(
        self,
        assessment_id: str,
        system_id: str,
        ai_application: DefenseAIApplication,
        autonomy_level: AutonomyLevel,
        **kwargs
    ) -> MilitaryAISafetyAssessment:
        """
        Assess military AI system safety and reliability
        
        Args:
            assessment_id: Unique assessment identifier
            system_id: Military AI system identifier
            ai_application: Type of defense AI application
            autonomy_level: Level of system autonomy
            
        Returns:
            MilitaryAISafetyAssessment: Safety assessment result
        """
        
        # Assess safety certification status
        safety_certification_status = self._assess_safety_certification_status(
            system_id, ai_application
        )
        
        # Collect reliability metrics
        reliability_metrics = self._collect_military_reliability_metrics(system_id)
        
        # Conduct failure mode analysis
        failure_mode_analysis = self._conduct_failure_mode_analysis(
            system_id, ai_application
        )
        
        # Assess human oversight requirements
        human_oversight_requirements = self._assess_human_oversight_requirements(
            system_id, autonomy_level
        )
        
        # Check kill switch mechanisms
        kill_switch_mechanisms = self._check_kill_switch_mechanisms(
            system_id, autonomy_level
        )
        
        # Collect testing and validation results
        testing_validation_results = self._collect_testing_validation_results(system_id)
        
        # Assess environmental robustness
        environmental_robustness = self._assess_environmental_robustness(system_id)
        
        # Assess adversarial resilience
        adversarial_resilience = self._assess_adversarial_resilience(system_id)
        
        # Check interoperability compliance
        interoperability_compliance = self._check_interoperability_compliance(system_id)
        
        # Assess rules of engagement integration
        roe_integration = self._assess_roe_integration(system_id, ai_application)
        
        # Check international law compliance
        international_law_compliance = self._check_international_law_compliance(
            system_id, ai_application
        )
        
        # Identify ethical constraints
        ethical_constraints = self._identify_ethical_constraints(
            system_id, ai_application
        )
        
        # Assess civilian harm prevention
        civilian_harm_prevention = self._assess_civilian_harm_prevention(
            system_id, ai_application
        )
        
        # Conduct collateral damage assessment
        collateral_damage_assessment = self._conduct_collateral_damage_assessment(
            system_id, ai_application
        )
        
        assessment = MilitaryAISafetyAssessment(
            assessment_id=assessment_id,
            system_id=system_id,
            ai_application=ai_application,
            classification_level=self.classification_level,
            autonomy_level=autonomy_level,
            safety_certification_status=safety_certification_status,
            reliability_metrics=reliability_metrics,
            failure_mode_analysis=failure_mode_analysis,
            human_oversight_requirements=human_oversight_requirements,
            kill_switch_mechanisms=kill_switch_mechanisms,
            testing_validation_results=testing_validation_results,
            environmental_robustness=environmental_robustness,
            adversarial_resilience=adversarial_resilience,
            interoperability_compliance=interoperability_compliance,
            rules_of_engagement_integration=roe_integration,
            international_law_compliance=international_law_compliance,
            ethical_constraints_implementation=ethical_constraints,
            civilian_harm_prevention=civilian_harm_prevention,
            collateral_damage_assessment=collateral_damage_assessment,
            assessment_timestamp=datetime.now(),
            safety_assessor_id=kwargs.get('safety_assessor_id', 'military_safety_assessor')
        )
        
        self.safety_assessments[assessment_id] = assessment
        
        # Log military AI safety assessment
        self.audit_trail.log_event(
            event_type="military_ai_safety_assessment",
            details={
                "assessment_id": assessment_id,
                "system_id": system_id,
                "ai_application": ai_application.value,
                "autonomy_level": autonomy_level.value,
                "safety_score": assessment.calculate_military_safety_score(),
                "classification_level": self.classification_level.value,
                "international_law_compliant": all(international_law_compliance.values())
            }
        )
        
        return assessment
    
    # Helper methods for implementation details
    
    def _assess_safety_certification_status(
        self,
        system_id: str,
        ai_application: DefenseAIApplication
    ) -> Dict[str, bool]:
        """Assess military AI safety certification status"""
        
        return {
            "functional_safety_certified": True,
            "reliability_testing_complete": True,
            "security_clearance_verified": True,
            "operational_testing_passed": False,
            "interoperability_certified": True,
            "environmental_testing_complete": True
        }
    
    def _collect_military_reliability_metrics(self, system_id: str) -> Dict[str, float]:
        """Collect military system reliability metrics"""
        
        return {
            "mean_time_between_failures": 8760.0,  # hours
            "availability": 0.995,
            "mission_success_rate": 0.98,
            "false_alarm_rate": 0.02,
            "detection_accuracy": 0.95
        }
    
    def _conduct_failure_mode_analysis(
        self,
        system_id: str,
        ai_application: DefenseAIApplication
    ) -> Dict[str, Any]:
        """Conduct failure mode and effects analysis"""
        
        return {
            "single_point_failures": ["communication_loss", "sensor_degradation"],
            "failure_probabilities": {"critical": 0.001, "major": 0.01, "minor": 0.05},
            "mitigation_strategies": ["redundancy", "graceful_degradation", "human_takeover"],
            "recovery_procedures": ["automatic_restart", "manual_intervention", "system_shutdown"]
        }
    
    # Additional helper methods would continue here for all assessment functions...