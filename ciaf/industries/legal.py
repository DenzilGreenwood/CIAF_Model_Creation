"""
Legal AI Governance Framework
=============================

Comprehensive AI governance for legal and professional services including:
- Legal decision support and case analysis
- Contract review and legal document generation
- Attorney-client privilege protection
- Professional responsibility compliance (ABA Model Rules)
- Legal bias detection and conflict of interest prevention
- Legal research validation and citation verification
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from ciaf.core.interfaces import AIGovernanceFramework
from ciaf.compliance.bias_validator import BiasValidator
from ciaf.compliance.audit_trails import AuditTrail
from ciaf.compliance.validators import ComplianceValidator

class LegalPrivilegeLevel(Enum):
    """Attorney-client privilege protection levels"""
    PRIVILEGED = "privileged"
    WORK_PRODUCT = "work_product"
    CONFIDENTIAL = "confidential"
    PUBLIC = "public"

class LegalPracticeArea(Enum):
    """Legal practice areas"""
    CORPORATE = "corporate"
    LITIGATION = "litigation"
    CRIMINAL = "criminal"
    EMPLOYMENT = "employment"
    INTELLECTUAL_PROPERTY = "intellectual_property"

@dataclass
class LegalDecisionAssessment:
    """Legal decision support assessment"""
    decision_id: str
    case_id: str
    practice_area: LegalPracticeArea
    legal_question: str
    ai_recommendation: str
    confidence_score: float
    supporting_precedents: List[str]
    jurisdiction: str
    ethical_considerations: List[str]
    privilege_level: LegalPrivilegeLevel
    attorney_review_required: bool
    assessment_timestamp: datetime
    reviewing_attorney_id: str
    
    def requires_human_oversight(self) -> bool:
        """Determine if human attorney oversight is required"""
        return (self.confidence_score < 0.85 or
                self.practice_area in [LegalPracticeArea.CRIMINAL] or
                len(self.ethical_considerations) > 0)

@dataclass
class ConflictOfInterestResult:
    """Conflict of interest screening result"""
    screening_id: str
    client_id: str
    matter_description: str
    potential_conflicts: List[Dict[str, Any]]
    conflict_severity: str
    waiver_possible: bool
    recommended_actions: List[str]
    screening_timestamp: datetime
    screener_id: str
    
    def has_disqualifying_conflict(self) -> bool:
        """Check if conflicts are disqualifying"""
        return (self.conflict_severity in ["actual", "imputed"] and 
                not self.waiver_possible)

class LegalAIGovernanceFramework(AIGovernanceFramework):
    """
    Legal AI Governance Framework for legal and professional services
    """
    
    def __init__(self, law_firm_id: str, primary_jurisdiction: str, **kwargs):
        super().__init__(**kwargs)
        self.law_firm_id = law_firm_id
        self.primary_jurisdiction = primary_jurisdiction
        self.bias_validator = BiasValidator()
        self.audit_trail = AuditTrail()
        self.compliance_validator = ComplianceValidator()
        
        self.professional_standards = [
            "ABA_Model_Rules", "State_Bar_Rules", "Federal_Rules_Evidence",
            "GDPR_Legal_Services", "ISO_27001_Legal"
        ]
        
        self.legal_decisions = {}
        self.conflict_screenings = {}
    
    def assess_legal_decision(
        self,
        decision_id: str,
        case_id: str,
        practice_area: LegalPracticeArea,
        legal_question: str,
        ai_recommendation: str,
        confidence_score: float,
        **kwargs
    ) -> LegalDecisionAssessment:
        """Assess AI-generated legal decision or recommendation"""
        
        # Identify supporting precedents
        supporting_precedents = self._identify_supporting_precedents(
            legal_question, practice_area
        )
        
        # Assess ethical considerations
        ethical_considerations = self._assess_ethical_considerations(
            practice_area, ai_recommendation
        )
        
        # Determine privilege level
        privilege_level = self._determine_privilege_level(legal_question, practice_area)
        
        # Assess need for attorney review
        attorney_review_required = (
            confidence_score < 0.85 or
            len(ethical_considerations) > 0 or
            practice_area == LegalPracticeArea.CRIMINAL
        )
        
        assessment = LegalDecisionAssessment(
            decision_id=decision_id,
            case_id=case_id,
            practice_area=practice_area,
            legal_question=legal_question,
            ai_recommendation=ai_recommendation,
            confidence_score=confidence_score,
            supporting_precedents=supporting_precedents,
            jurisdiction=kwargs.get('jurisdiction', self.primary_jurisdiction),
            ethical_considerations=ethical_considerations,
            privilege_level=privilege_level,
            attorney_review_required=attorney_review_required,
            assessment_timestamp=datetime.now(),
            reviewing_attorney_id=kwargs.get('reviewing_attorney_id', 'pending')
        )
        
        self.legal_decisions[decision_id] = assessment
        
        self.audit_trail.log_event(
            event_type="legal_decision_assessment",
            details={
                "decision_id": decision_id,
                "practice_area": practice_area.value,
                "confidence_score": confidence_score,
                "attorney_review_required": attorney_review_required
            }
        )
        
        return assessment
    
    def screen_conflicts_of_interest(
        self,
        screening_id: str,
        client_id: str,
        matter_description: str,
        **kwargs
    ) -> ConflictOfInterestResult:
        """Screen for conflicts of interest"""
        
        # Identify potential conflicts
        potential_conflicts = self._identify_potential_conflicts(
            client_id, matter_description
        )
        
        # Assess conflict severity
        conflict_severity = self._assess_conflict_severity(potential_conflicts)
        
        # Determine if waiver is possible
        waiver_possible = self._assess_waiver_possibility(conflict_severity)
        
        # Generate recommendations
        recommended_actions = self._generate_conflict_recommendations(
            conflict_severity, waiver_possible
        )
        
        result = ConflictOfInterestResult(
            screening_id=screening_id,
            client_id=client_id,
            matter_description=matter_description,
            potential_conflicts=potential_conflicts,
            conflict_severity=conflict_severity,
            waiver_possible=waiver_possible,
            recommended_actions=recommended_actions,
            screening_timestamp=datetime.now(),
            screener_id=kwargs.get('screener_id', 'conflict_system')
        )
        
        self.conflict_screenings[screening_id] = result
        
        self.audit_trail.log_event(
            event_type="conflict_screening",
            details={
                "screening_id": screening_id,
                "client_id": client_id,
                "conflict_severity": conflict_severity,
                "conflicts_found": len(potential_conflicts)
            }
        )
        
        return result
    
    def _identify_supporting_precedents(
        self,
        legal_question: str,
        practice_area: LegalPracticeArea
    ) -> List[str]:
        """Identify supporting legal precedents"""
        precedents = []
        
        if practice_area == LegalPracticeArea.CORPORATE:
            precedents = ["Delaware General Corp. Law", "Business Judgment Rule"]
        elif practice_area == LegalPracticeArea.EMPLOYMENT:
            precedents = ["Title VII", "ADA", "FMLA"]
        elif practice_area == LegalPracticeArea.INTELLECTUAL_PROPERTY:
            precedents = ["35 U.S.C. § 101", "Alice Corp. v. CLS Bank"]
        
        return precedents
    
    def _assess_ethical_considerations(
        self,
        practice_area: LegalPracticeArea,
        ai_recommendation: str
    ) -> List[str]:
        """Assess ethical considerations"""
        considerations = []
        
        if "uncertain" in ai_recommendation.lower():
            considerations.append("competence_verification_required")
        
        if practice_area == LegalPracticeArea.CRIMINAL:
            considerations.append("heightened_client_consultation_required")
        
        return considerations
    
    def _determine_privilege_level(
        self,
        legal_question: str,
        practice_area: LegalPracticeArea
    ) -> LegalPrivilegeLevel:
        """Determine attorney-client privilege level"""
        
        if "strategy" in legal_question.lower() or practice_area == LegalPracticeArea.LITIGATION:
            return LegalPrivilegeLevel.WORK_PRODUCT
        elif "advice" in legal_question.lower():
            return LegalPrivilegeLevel.PRIVILEGED
        else:
            return LegalPrivilegeLevel.CONFIDENTIAL
    
    def _identify_potential_conflicts(
        self,
        client_id: str,
        matter_description: str
    ) -> List[Dict[str, Any]]:
        """Identify potential conflicts of interest"""
        conflicts = []
        
        if "merger" in matter_description.lower():
            conflicts.append({
                "type": "adverse_client_interest",
                "description": "Potential adverse interest in merger",
                "severity": "high"
            })
        
        return conflicts
    
    def _assess_conflict_severity(self, potential_conflicts: List[Dict[str, Any]]) -> str:
        """Assess severity of identified conflicts"""
        if not potential_conflicts:
            return "none"
        
        severity_levels = [conflict.get("severity", "low") for conflict in potential_conflicts]
        
        if "high" in severity_levels:
            return "actual"
        else:
            return "potential"
    
    def _assess_waiver_possibility(self, conflict_severity: str) -> bool:
        """Assess if conflict waiver is possible"""
        return conflict_severity != "actual"
    
    def _generate_conflict_recommendations(
        self,
        conflict_severity: str,
        waiver_possible: bool
    ) -> List[str]:
        """Generate conflict resolution recommendations"""
        recommendations = []
        
        if conflict_severity == "none":
            recommendations.append("proceed_with_representation")
        elif waiver_possible:
            recommendations.extend(["obtain_informed_consent", "document_waiver"])
        else:
            recommendations.append("decline_representation")
        
        return recommendations