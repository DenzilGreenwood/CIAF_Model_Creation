"""
Policy enforcement and risk assessment for CIAF core operations.

Implements PolicyEnforcer for high-risk domain detection, compliance
checking, and audit policy enforcement throughout the CIAF pipeline.

Created: 2025-09-26
Author: Denzil James Greenwood
Version: 1.0.0
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .canonicalization import Policy
from .enums import RecordType


class RiskLevel(str, Enum):
    """Risk levels for policy enforcement."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceResult(str, Enum):
    """Compliance check results."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    rule_id: str
    severity: RiskLevel
    description: str
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class RiskAssessment:
    """Risk assessment result for an operation."""
    risk_level: RiskLevel
    risk_factors: List[str]
    violations: List[PolicyViolation]
    compliance_result: ComplianceResult
    recommendations: List[str]


class PolicyRule:
    """Base class for policy rules."""
    
    def __init__(self, rule_id: str, description: str, severity: RiskLevel):
        self.rule_id = rule_id
        self.description = description
        self.severity = severity
    
    def evaluate(self, metadata: Dict[str, Any], policy: Policy) -> Optional[PolicyViolation]:
        """Evaluate rule against metadata and policy."""
        raise NotImplementedError


class HighRiskDomainRule(PolicyRule):
    """Rule to detect high-risk domains."""
    
    def __init__(self):
        super().__init__(
            "HIGH_RISK_DOMAIN",
            "Detects operations in high-risk domains",
            RiskLevel.HIGH
        )
    
    def evaluate(self, metadata: Dict[str, Any], policy: Policy) -> Optional[PolicyViolation]:
        if policy.is_high_risk():
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                description=f"Operation involves high-risk domains: {policy.domain_labels}",
                metadata={
                    "domains": policy.domain_labels,
                    "high_risk_domains": policy.high_risk_domains
                },
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        return None


class PiiDetectionRule(PolicyRule):
    """Rule to detect potential PII in metadata."""
    
    def __init__(self):
        super().__init__(
            "PII_DETECTION",
            "Detects potential personally identifiable information",
            RiskLevel.MEDIUM
        )
        
        # Common PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        }
    
    def evaluate(self, metadata: Dict[str, Any], policy: Policy) -> Optional[PolicyViolation]:
        pii_found = []
        
        # Check all string values in metadata
        for key, value in metadata.items():
            if isinstance(value, str):
                for pii_type, pattern in self.pii_patterns.items():
                    if re.search(pattern, value, re.IGNORECASE):
                        pii_found.append(f"{pii_type} in {key}")
        
        if pii_found:
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                description=f"Potential PII detected: {', '.join(pii_found)}",
                metadata={
                    "pii_types": pii_found,
                    "affected_fields": list(metadata.keys())
                },
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        return None


class TimestampValidationRule(PolicyRule):
    """Rule to validate timestamp formats and recency."""
    
    def __init__(self):
        super().__init__(
            "TIMESTAMP_VALIDATION",
            "Validates timestamp formats and recency",
            RiskLevel.LOW
        )
    
    def evaluate(self, metadata: Dict[str, Any], policy: Policy) -> Optional[PolicyViolation]:
        timestamp_str = metadata.get('timestamp')
        if not timestamp_str:
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=RiskLevel.MEDIUM,
                description="Missing required timestamp field",
                metadata={"missing_field": "timestamp"},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        try:
            # Validate ISO format
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Check if timestamp is in the future (suspicious)
            now = datetime.now(timezone.utc)
            if timestamp > now:
                return PolicyViolation(
                    rule_id=self.rule_id,
                    severity=RiskLevel.MEDIUM,
                    description="Timestamp is in the future",
                    metadata={
                        "timestamp": timestamp_str,
                        "current_time": now.isoformat()
                    },
                    timestamp=now.isoformat()
                )
        
        except (ValueError, TypeError):
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=RiskLevel.MEDIUM,
                description="Invalid timestamp format",
                metadata={"invalid_timestamp": timestamp_str},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        return None


class RequiredFieldsRule(PolicyRule):
    """Rule to enforce required fields based on record type."""
    
    def __init__(self):
        super().__init__(
            "REQUIRED_FIELDS",
            "Validates presence of required fields",
            RiskLevel.HIGH
        )
        
        # Import here to avoid circular dependency
        from .canonicalization import REQUIRED_FIELDS
        self.required_fields = REQUIRED_FIELDS
    
    def evaluate(self, metadata: Dict[str, Any], policy: Policy) -> Optional[PolicyViolation]:
        record_type_str = metadata.get('record_type')
        if not record_type_str:
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                description="Missing record_type field",
                metadata={"missing_field": "record_type"},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        try:
            record_type = RecordType(record_type_str)
        except ValueError:
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                description=f"Invalid record_type: {record_type_str}",
                metadata={"invalid_record_type": record_type_str},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        required = self.required_fields.get(record_type, [])
        missing = [field for field in required if field not in metadata]
        
        if missing:
            return PolicyViolation(
                rule_id=self.rule_id,
                severity=self.severity,
                description=f"Missing required fields: {missing}",
                metadata={
                    "missing_fields": missing,
                    "record_type": record_type_str
                },
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        return None


class PolicyEnforcer:
    """
    Central policy enforcement engine for CIAF operations.
    
    Evaluates operations against policy rules and provides risk assessment
    and compliance checking capabilities.
    """
    
    def __init__(self, additional_rules: Optional[List[PolicyRule]] = None):
        """
        Initialize policy enforcer with default and additional rules.
        
        Args:
            additional_rules: Optional list of additional policy rules
        """
        # Default rule set
        self.rules: List[PolicyRule] = [
            HighRiskDomainRule(),
            PiiDetectionRule(),
            TimestampValidationRule(),
            RequiredFieldsRule()
        ]
        
        # Add any additional rules
        if additional_rules:
            self.rules.extend(additional_rules)
        
        # Track enforcement statistics
        self.enforcement_stats = {
            'total_assessments': 0,
            'violations_found': 0,
            'high_risk_operations': 0,
            'non_compliant_operations': 0
        }
    
    def assess_risk(self, metadata: Dict[str, Any], policy: Policy) -> RiskAssessment:
        """
        Perform comprehensive risk assessment on an operation.
        
        Args:
            metadata: Operation metadata to assess
            policy: Policy configuration
            
        Returns:
            RiskAssessment with violations and recommendations
        """
        self.enforcement_stats['total_assessments'] += 1
        
        violations = []
        risk_factors = []
        
        # Evaluate all rules
        for rule in self.rules:
            violation = rule.evaluate(metadata, policy)
            if violation:
                violations.append(violation)
                risk_factors.append(violation.description)
        
        # Determine overall risk level
        if violations:
            self.enforcement_stats['violations_found'] += 1
            max_severity = max(v.severity for v in violations)
            risk_level = max_severity
        else:
            risk_level = RiskLevel.LOW
        
        # Determine compliance result
        critical_violations = [v for v in violations if v.severity == RiskLevel.CRITICAL]
        high_violations = [v for v in violations if v.severity == RiskLevel.HIGH]
        
        if critical_violations:
            compliance_result = ComplianceResult.NON_COMPLIANT
            self.enforcement_stats['non_compliant_operations'] += 1
        elif high_violations:
            compliance_result = ComplianceResult.REQUIRES_REVIEW
        else:
            compliance_result = ComplianceResult.COMPLIANT
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.enforcement_stats['high_risk_operations'] += 1
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations, policy)
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_factors=risk_factors,
            violations=violations,
            compliance_result=compliance_result,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, violations: List[PolicyViolation], policy: Policy) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        violation_types = {v.rule_id for v in violations}
        
        if 'HIGH_RISK_DOMAIN' in violation_types:
            recommendations.append("Consider additional monitoring and approval processes for high-risk domains")
            recommendations.append("Implement enhanced logging and audit trails")
        
        if 'PII_DETECTION' in violation_types:
            recommendations.append("Review and potentially redact or encrypt detected PII")
            recommendations.append("Ensure GDPR/privacy compliance measures are in place")
        
        if 'TIMESTAMP_VALIDATION' in violation_types:
            recommendations.append("Verify system clock synchronization")
            recommendations.append("Implement timestamp validation at data ingestion")
        
        if 'REQUIRED_FIELDS' in violation_types:
            recommendations.append("Implement input validation to ensure required fields")
            recommendations.append("Review data collection processes")
        
        if policy.external_timestamping:
            recommendations.append("Ensure external timestamping service is operational")
        
        return recommendations
    
    def is_operation_allowed(self, metadata: Dict[str, Any], policy: Policy) -> bool:
        """
        Quick check if operation should be allowed based on policy.
        
        Args:
            metadata: Operation metadata
            policy: Policy configuration
            
        Returns:
            True if operation is allowed, False if blocked
        """
        assessment = self.assess_risk(metadata, policy)
        return assessment.compliance_result != ComplianceResult.NON_COMPLIANT
    
    def get_enforcement_stats(self) -> Dict[str, Any]:
        """Get enforcement statistics."""
        return self.enforcement_stats.copy()
    
    def add_rule(self, rule: PolicyRule):
        """Add a new policy rule."""
        self.rules.append(rule)
    
    def remove_rule(self, rule_id: str):
        """Remove a policy rule by ID."""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]


# Factory functions for common policy configurations

def create_healthcare_policy_enforcer() -> PolicyEnforcer:
    """Create policy enforcer with healthcare-specific rules."""
    additional_rules = [
        # Add healthcare-specific rules here
    ]
    return PolicyEnforcer(additional_rules)


def create_financial_policy_enforcer() -> PolicyEnforcer:
    """Create policy enforcer with financial services-specific rules."""
    additional_rules = [
        # Add financial-specific rules here
    ]
    return PolicyEnforcer(additional_rules)


def create_gdpr_policy_enforcer() -> PolicyEnforcer:
    """Create policy enforcer with GDPR-specific rules."""
    additional_rules = [
        # Add GDPR-specific rules here
    ]
    return PolicyEnforcer(additional_rules)


class PolicyEnforcement:
    """
    Simplified policy enforcement class for industry frameworks.
    
    Provides industry-specific AI governance policy enforcement capabilities
    with simplified interface for integration with industry governance frameworks.
    """
    
    def __init__(self, 
                 industry_type: Optional[str] = None,
                 regulatory_frameworks: Optional[List[str]] = None,
                 enforcement_level: str = "standard"):
        """
        Initialize policy enforcement for industry frameworks.
        
        Args:
            industry_type: Type of industry (banking, healthcare, etc.)
            regulatory_frameworks: List of applicable regulatory frameworks
            enforcement_level: Level of enforcement (standard, strict, permissive)
        """
        self.industry_type = industry_type or "general"
        self.regulatory_frameworks = regulatory_frameworks or []
        self.enforcement_level = enforcement_level
        
        # Policy enforcement statistics
        self.enforcement_stats = {
            'policies_evaluated': 0,
            'violations_detected': 0,
            'compliance_checks': 0,
            'enforcement_actions': 0
        }
        
        # Industry-specific policy configurations
        self.policy_config = self._initialize_industry_policies()
    
    def _initialize_industry_policies(self) -> Dict[str, Any]:
        """Initialize industry-specific policy configurations."""
        base_config = {
            'bias_detection_enabled': True,
            'audit_trail_required': True,
            'transparency_required': True,
            'human_oversight_required': False,
            'risk_assessment_mandatory': True
        }
        
        # Industry-specific overrides
        industry_configs = {
            'banking': {
                'fair_lending_required': True,
                'algorithmic_trading_oversight': True,
                'credit_decision_explainability': True,
                'regulatory_reporting_required': True
            },
            'healthcare': {
                'patient_privacy_required': True,
                'clinical_validation_required': True,
                'fda_compliance_required': True,
                'patient_safety_priority': True,
                'human_oversight_required': True
            },
            'insurance': {
                'fair_pricing_required': True,
                'claims_processing_fairness': True,
                'fraud_detection_oversight': True,
                'demographic_parity_required': True
            },
            'human_resources': {
                'hiring_fairness_required': True,
                'performance_evaluation_equity': True,
                'nyc_law_144_compliance': True,
                'workplace_discrimination_prevention': True
            }
        }
        
        # Merge base config with industry-specific config
        config = base_config.copy()
        if self.industry_type in industry_configs:
            config.update(industry_configs[self.industry_type])
        
        return config
    
    def enforce_policy(self, 
                      action_type: str, 
                      data: Dict[str, Any], 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enforce policy for a specific action and data.
        
        Args:
            action_type: Type of action being performed
            data: Data being processed
            context: Additional context for policy enforcement
            
        Returns:
            Dict containing enforcement results and recommendations
        """
        self.enforcement_stats['policies_evaluated'] += 1
        
        enforcement_result = {
            'action_type': action_type,
            'enforcement_timestamp': datetime.now(timezone.utc).isoformat(),
            'policy_compliant': True,
            'violations': [],
            'warnings': [],
            'recommendations': [],
            'enforcement_level': self.enforcement_level,
            'industry_type': self.industry_type
        }
        
        # Check industry-specific policies
        violations = self._check_industry_policies(action_type, data, context)
        if violations:
            enforcement_result['violations'].extend(violations)
            enforcement_result['policy_compliant'] = False
            self.enforcement_stats['violations_detected'] += len(violations)
        
        # Check regulatory framework compliance
        regulatory_violations = self._check_regulatory_compliance(action_type, data)
        if regulatory_violations:
            enforcement_result['violations'].extend(regulatory_violations)
            enforcement_result['policy_compliant'] = False
        
        # Generate recommendations
        if enforcement_result['violations']:
            enforcement_result['recommendations'] = self._generate_enforcement_recommendations(
                enforcement_result['violations'], action_type
            )
        
        # Record enforcement action
        if not enforcement_result['policy_compliant']:
            self.enforcement_stats['enforcement_actions'] += 1
        
        return enforcement_result
    
    def _check_industry_policies(self, 
                               action_type: str, 
                               data: Dict[str, Any], 
                               context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check industry-specific policy violations."""
        violations = []
        
        # Common policy checks
        if self.policy_config.get('bias_detection_enabled'):
            if not data.get('bias_assessment_completed'):
                violations.append({
                    'policy_id': 'BIAS_DETECTION_REQUIRED',
                    'severity': 'medium',
                    'description': 'Bias assessment not completed before action',
                    'action_required': 'Complete bias assessment before proceeding'
                })
        
        if self.policy_config.get('audit_trail_required'):
            if not data.get('audit_trail_id'):
                violations.append({
                    'policy_id': 'AUDIT_TRAIL_MISSING',
                    'severity': 'high',
                    'description': 'Audit trail not established for action',
                    'action_required': 'Create audit trail before proceeding'
                })
        
        # Industry-specific checks
        if self.industry_type == 'banking':
            violations.extend(self._check_banking_policies(action_type, data))
        elif self.industry_type == 'healthcare':
            violations.extend(self._check_healthcare_policies(action_type, data))
        elif self.industry_type == 'insurance':
            violations.extend(self._check_insurance_policies(action_type, data))
        elif self.industry_type == 'human_resources':
            violations.extend(self._check_hr_policies(action_type, data))
        
        return violations
    
    def _check_banking_policies(self, action_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check banking-specific policies."""
        violations = []
        
        if action_type == 'credit_decision':
            if self.policy_config.get('fair_lending_required'):
                if not data.get('fair_lending_assessment'):
                    violations.append({
                        'policy_id': 'FAIR_LENDING_REQUIRED',
                        'severity': 'critical',
                        'description': 'Fair lending assessment required for credit decisions',
                        'action_required': 'Complete fair lending assessment'
                    })
        
        if action_type == 'algorithmic_trading':
            if self.policy_config.get('algorithmic_trading_oversight'):
                if not data.get('market_impact_assessment'):
                    violations.append({
                        'policy_id': 'TRADING_OVERSIGHT_REQUIRED',
                        'severity': 'high',
                        'description': 'Market impact assessment required for trading algorithms',
                        'action_required': 'Complete market impact assessment'
                    })
        
        return violations
    
    def _check_healthcare_policies(self, action_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check healthcare-specific policies."""
        violations = []
        
        if action_type in ['clinical_decision', 'diagnosis', 'treatment_recommendation']:
            if self.policy_config.get('clinical_validation_required'):
                if not data.get('clinical_validation_completed'):
                    violations.append({
                        'policy_id': 'CLINICAL_VALIDATION_REQUIRED',
                        'severity': 'critical',
                        'description': 'Clinical validation required for medical AI decisions',
                        'action_required': 'Complete clinical validation process'
                    })
            
            if self.policy_config.get('human_oversight_required'):
                if not data.get('physician_review_completed'):
                    violations.append({
                        'policy_id': 'PHYSICIAN_OVERSIGHT_REQUIRED',
                        'severity': 'critical',
                        'description': 'Physician oversight required for clinical decisions',
                        'action_required': 'Obtain physician review and approval'
                    })
        
        return violations
    
    def _check_insurance_policies(self, action_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check insurance-specific policies."""
        violations = []
        
        if action_type == 'premium_calculation':
            if self.policy_config.get('fair_pricing_required'):
                if not data.get('fairness_assessment'):
                    violations.append({
                        'policy_id': 'FAIR_PRICING_REQUIRED',
                        'severity': 'high',
                        'description': 'Fairness assessment required for premium calculations',
                        'action_required': 'Complete fairness assessment'
                    })
        
        return violations
    
    def _check_hr_policies(self, action_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check HR-specific policies."""
        violations = []
        
        if action_type == 'hiring_decision':
            if self.policy_config.get('hiring_fairness_required'):
                if not data.get('bias_assessment'):
                    violations.append({
                        'policy_id': 'HIRING_FAIRNESS_REQUIRED',
                        'severity': 'critical',
                        'description': 'Bias assessment required for hiring decisions',
                        'action_required': 'Complete hiring bias assessment'
                    })
        
        return violations
    
    def _check_regulatory_compliance(self, action_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check regulatory framework compliance."""
        violations = []
        
        for framework in self.regulatory_frameworks:
            if framework == 'GDPR' and 'personal_data' in str(data):
                if not data.get('gdpr_compliance_verified'):
                    violations.append({
                        'policy_id': 'GDPR_COMPLIANCE_REQUIRED',
                        'severity': 'critical',
                        'description': 'GDPR compliance verification required for personal data processing',
                        'regulatory_framework': 'GDPR'
                    })
            
            if framework == 'EU_AI_ACT' and action_type in ['high_risk_ai_system']:
                if not data.get('eu_ai_act_assessment'):
                    violations.append({
                        'policy_id': 'EU_AI_ACT_COMPLIANCE_REQUIRED',
                        'severity': 'critical',
                        'description': 'EU AI Act compliance assessment required for high-risk AI systems',
                        'regulatory_framework': 'EU_AI_ACT'
                    })
        
        return violations
    
    def _generate_enforcement_recommendations(self, 
                                            violations: List[Dict[str, Any]], 
                                            action_type: str) -> List[str]:
        """Generate enforcement recommendations based on violations."""
        recommendations = []
        
        # Collect unique recommendations
        for violation in violations:
            if violation.get('action_required'):
                recommendations.append(violation['action_required'])
        
        # Add general recommendations
        if any(v.get('severity') == 'critical' for v in violations):
            recommendations.append("Review and address critical policy violations before proceeding")
        
        if len(violations) > 3:
            recommendations.append("Consider comprehensive policy review and training")
        
        return list(set(recommendations))  # Remove duplicates
    
    def validate_compliance(self, 
                          assessment_data: Dict[str, Any], 
                          required_standards: List[str]) -> Dict[str, Any]:
        """
        Validate compliance against specified standards.
        
        Args:
            assessment_data: Data to assess for compliance
            required_standards: List of required compliance standards
            
        Returns:
            Dict containing compliance validation results
        """
        self.enforcement_stats['compliance_checks'] += 1
        
        compliance_result = {
            'validation_timestamp': datetime.now(timezone.utc).isoformat(),
            'standards_evaluated': required_standards,
            'overall_compliant': True,
            'standard_results': {},
            'compliance_score': 0.0,
            'recommendations': []
        }
        
        compliant_count = 0
        
        for standard in required_standards:
            result = self._evaluate_standard_compliance(assessment_data, standard)
            compliance_result['standard_results'][standard] = result
            
            if result['compliant']:
                compliant_count += 1
            else:
                compliance_result['overall_compliant'] = False
        
        # Calculate compliance score
        if required_standards:
            compliance_result['compliance_score'] = compliant_count / len(required_standards)
        
        # Generate recommendations for non-compliance
        if not compliance_result['overall_compliant']:
            compliance_result['recommendations'] = [
                f"Address compliance gaps in: {standard}" 
                for standard, result in compliance_result['standard_results'].items()
                if not result['compliant']
            ]
        
        return compliance_result
    
    def _evaluate_standard_compliance(self, 
                                    assessment_data: Dict[str, Any], 
                                    standard: str) -> Dict[str, Any]:
        """Evaluate compliance against a specific standard."""
        # Simplified compliance evaluation - in production would be more sophisticated
        result = {
            'compliant': True,
            'score': 1.0,
            'issues': [],
            'requirements_met': True
        }
        
        # Standard-specific evaluation logic would go here
        # This is a simplified placeholder implementation
        
        return result
    
    def get_enforcement_statistics(self) -> Dict[str, Any]:
        """Get policy enforcement statistics."""
        return {
            **self.enforcement_stats,
            'industry_type': self.industry_type,
            'regulatory_frameworks': self.regulatory_frameworks,
            'enforcement_level': self.enforcement_level,
            'policy_config': self.policy_config
        }
    
    def update_policy_config(self, updates: Dict[str, Any]) -> None:
        """Update policy configuration."""
        self.policy_config.update(updates)
    
    def add_regulatory_framework(self, framework: str) -> None:
        """Add a regulatory framework to enforcement."""
        if framework not in self.regulatory_frameworks:
            self.regulatory_frameworks.append(framework)
    
    def remove_regulatory_framework(self, framework: str) -> None:
        """Remove a regulatory framework from enforcement."""
        if framework in self.regulatory_frameworks:
            self.regulatory_frameworks.remove(framework)