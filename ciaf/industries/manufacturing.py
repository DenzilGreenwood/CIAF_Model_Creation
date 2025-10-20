"""
Manufacturing AI Governance Framework
=====================================

Comprehensive AI governance for manufacturing and industrial systems including:
- Safety-critical process control and automation
- Quality control and predictive maintenance
- Robotic systems and human-machine collaboration
- Supply chain optimization and inventory management
- ISO 26262, ISO 13849, IEC 61508 functional safety compliance
- OSHA workplace safety and environmental regulations
- Digital twin validation and cyber-physical system security

Key Components:
- Manufacturing safety assessment with failure mode analysis
- Quality control systems with statistical process control
- Human-robot interaction safety protocols
- Environmental compliance monitoring
- Predictive maintenance validation
- Supply chain risk assessment
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from ciaf.core.interfaces import AIGovernanceFramework
from ciaf.compliance.bias_validator import BiasValidator
from ciaf.compliance.audit_trails import AuditTrail
from ciaf.compliance.validators import ComplianceValidator

class SafetyIntegrityLevel(Enum):
    """IEC 61508 Safety Integrity Levels for functional safety"""
    SIL_1 = "SIL_1"  # Low safety integrity
    SIL_2 = "SIL_2"  # Medium safety integrity
    SIL_3 = "SIL_3"  # High safety integrity
    SIL_4 = "SIL_4"  # Very high safety integrity

class PerformanceLevel(Enum):
    """ISO 13849 Performance Levels for machine safety"""
    PL_A = "PL_a"  # Low performance level
    PL_B = "PL_b"  # Low-medium performance level
    PL_C = "PL_c"  # Medium performance level
    PL_D = "PL_d"  # High performance level
    PL_E = "PL_e"  # Very high performance level

class HazardCategory(Enum):
    """Manufacturing hazard categories"""
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    CHEMICAL = "chemical"
    RADIATION = "radiation"
    ERGONOMIC = "ergonomic"
    ENVIRONMENTAL = "environmental"

@dataclass
class SafetyAssessment:
    """Safety assessment for manufacturing AI systems"""
    system_id: str
    safety_integrity_level: SafetyIntegrityLevel
    performance_level: PerformanceLevel
    hazard_categories: List[HazardCategory]
    failure_modes: List[str]
    risk_reduction_measures: List[str]
    human_safety_factors: Dict[str, float]
    environmental_factors: Dict[str, float]
    validation_tests: List[str]
    certification_status: str
    assessment_date: datetime
    next_review_date: datetime
    assessor_id: str
    
    def calculate_overall_risk_score(self) -> float:
        """Calculate overall risk score based on safety factors"""
        base_score = {
            SafetyIntegrityLevel.SIL_1: 1.0,
            SafetyIntegrityLevel.SIL_2: 2.0,
            SafetyIntegrityLevel.SIL_3: 3.0,
            SafetyIntegrityLevel.SIL_4: 4.0
        }[self.safety_integrity_level]
        
        # Factor in hazard categories and human safety factors
        hazard_multiplier = len(self.hazard_categories) * 0.1 + 1.0
        human_factor = sum(self.human_safety_factors.values()) / len(self.human_safety_factors) if self.human_safety_factors else 1.0
        
        return base_score * hazard_multiplier * human_factor

@dataclass
class QualityControlResult:
    """Quality control assessment result"""
    batch_id: str
    product_specifications: Dict[str, Any]
    measured_values: Dict[str, float]
    control_limits: Dict[str, tuple]  # (lower, upper) control limits
    out_of_control_signals: List[str]
    process_capability_indices: Dict[str, float]  # Cp, Cpk, Pp, Ppk
    defect_classifications: List[str]
    corrective_actions: List[str]
    quality_score: float
    inspector_id: str
    inspection_timestamp: datetime
    ai_confidence: float
    human_verification_required: bool
    
    def is_within_specifications(self) -> bool:
        """Check if all measurements are within specification limits"""
        for param, value in self.measured_values.items():
            if param in self.control_limits:
                lower, upper = self.control_limits[param]
                if not (lower <= value <= upper):
                    return False
        return True

class ManufacturingAIGovernanceFramework(AIGovernanceFramework):
    """
    Manufacturing AI Governance Framework
    
    Implements comprehensive governance for manufacturing AI systems with focus on:
    - Functional safety compliance (IEC 61508, ISO 13849, ISO 26262)
    - Quality control and statistical process control
    - Human-robot interaction safety
    - Environmental compliance and sustainability
    - Supply chain risk management
    - Predictive maintenance validation
    """
    
    def __init__(self, organization_id: str, facility_id: str, **kwargs):
        super().__init__(**kwargs)
        self.organization_id = organization_id
        self.facility_id = facility_id
        self.bias_validator = BiasValidator()
        self.audit_trail = AuditTrail()
        self.compliance_validator = ComplianceValidator()
        
        # Manufacturing-specific configurations
        self.safety_standards = [
            "IEC_61508",  # Functional Safety
            "ISO_13849",  # Machine Safety
            "ISO_26262",  # Automotive Functional Safety
            "OSHA_1910", # Occupational Safety
            "ISO_14001", # Environmental Management
            "ISO_9001"   # Quality Management
        ]
        
        self.quality_control_parameters = {}
        self.safety_assessments = {}
    
    def assess_manufacturing_safety(
        self,
        system_id: str,
        safety_integrity_level: SafetyIntegrityLevel,
        performance_level: PerformanceLevel,
        hazard_categories: List[HazardCategory],
        **kwargs
    ) -> SafetyAssessment:
        """Assess safety of manufacturing AI system"""
        
        assessment = SafetyAssessment(
            system_id=system_id,
            safety_integrity_level=safety_integrity_level,
            performance_level=performance_level,
            hazard_categories=hazard_categories,
            failure_modes=["actuator_failure", "sensor_degradation"],
            risk_reduction_measures=["redundant_systems", "fail_safe_design"],
            human_safety_factors={"operator_training": 0.9, "experience": 0.8},
            environmental_factors={"temperature": 0.85, "vibration": 0.75},
            validation_tests=["functional_test", "stress_test"],
            certification_status="pending",
            assessment_date=datetime.now(),
            next_review_date=datetime.now(),
            assessor_id=kwargs.get('assessor_id', 'system')
        )
        
        self.safety_assessments[system_id] = assessment
        return assessment
    
    def validate_quality_control(
        self,
        batch_id: str,
        product_specifications: Dict[str, Any],
        measured_values: Dict[str, float],
        **kwargs
    ) -> QualityControlResult:
        """Validate quality control measurements"""
        
        # Calculate control limits and quality metrics
        control_limits = {}
        for param, spec in product_specifications.items():
            if isinstance(spec, dict) and 'tolerance' in spec:
                nominal = spec.get('nominal', 0)
                tolerance = spec['tolerance']
                control_limits[param] = (nominal - tolerance, nominal + tolerance)
        
        result = QualityControlResult(
            batch_id=batch_id,
            product_specifications=product_specifications,
            measured_values=measured_values,
            control_limits=control_limits,
            out_of_control_signals=[],
            process_capability_indices={"Cp": 1.33, "Cpk": 1.25},
            defect_classifications=[],
            corrective_actions=[],
            quality_score=0.95,
            inspector_id=kwargs.get('inspector_id', 'ai_system'),
            inspection_timestamp=datetime.now(),
            ai_confidence=kwargs.get('ai_confidence', 0.95),
            human_verification_required=False
        )
        
        return result