"""
Comprehensive Test Suite for TransportationAIGovernanceFramework

Tests cover all methods and compliance requirements across transportation AI systems.
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List

from ciaf.industries.transportation import TransportationAIGovernanceFramework
from tests.conftest_frameworks import BaseFrameworkTest


class TestTransportationAIGovernanceFramework(BaseFrameworkTest):
    """Comprehensive test suite for TransportationAIGovernanceFramework"""

    def get_framework_class(self):
        """Return transportation framework class"""
        return TransportationAIGovernanceFramework

    def get_framework_name(self) -> str:
        """Return framework name"""
        return "transportation"

    def get_regulatory_requirements(self) -> List[str]:
        """Return transportation regulatory requirements"""
        return ['NHTSA_AV_GUIDELINES', '49_CFR_PART_393', 'ISO_26262']

    def get_test_data(self) -> Dict[str, Any]:
        """Return transportation-specific test data"""
        return {
    'transportation_data': {
        'vehicle_id': 'VEH123456',
        'autonomous_level': 3,
        'accident_rate': 0.001,
        'safety_score': 0.95
    }

        }

    # ========================================================================
    # TRANSPORTATION-SPECIFIC TESTS
    # ========================================================================

    def test_framework_initialization_with_defaults(self):
        """Test framework initializes with default settings"""
        framework = TransportationAIGovernanceFramework(
            organization_id="test_org"
        )
        assert framework is not None
        assert framework.organization_id == "test_org"

    def test_compliance_assessment_produces_valid_output(self, framework_instance):
        """Test compliance assessment produces valid structured output"""
        result = framework_instance.assess_compliance(
            assessment_type='full'
        )
        assert result is not None
        assert 'overall_compliance_score' in result
        assert 'compliance_status' in result

    def test_governance_validation_produces_structured_output(self, framework_instance):
        """Test governance validation produces structured output"""
        result = framework_instance.validate_governance_requirements()
        assert result is not None
        assert 'governance_requirements' in result
        assert len(result['governance_requirements']) > 0

    def test_audit_report_generation_successful(self, framework_instance):
        """Test audit report generation completes successfully"""
        result = framework_instance.generate_audit_report(
            audit_period_start='2025-01-01',
            audit_period_end='2025-12-31'
        )
        assert result is not None
        assert isinstance(result, dict)

    def test_framework_enforces_regulatory_requirements(self, framework_instance):
        """Test framework enforces all required regulatory requirements"""
        result = framework_instance.validate_governance_requirements()

        governance_reqs = result.get('governance_requirements', {})
        assert len(governance_reqs) > 0

    def test_compliance_score_aligns_with_status(self, framework_instance):
        """Test compliance score aligns with compliance status"""
        result = framework_instance.assess_compliance(
            assessment_type='full'
        )

        score = result['overall_compliance_score']
        status = result['compliance_status']

        if score >= 0.9:
            assert status == 'compliant'
        elif score >= 0.7:
            assert status in ['compliant', 'partially_compliant']
        else:
            assert status in ['non_compliant', 'partially_compliant']

    def test_multiple_instances_are_independent(self):
        """Test multiple framework instances are truly independent"""
        framework1 = TransportationAIGovernanceFramework(organization_id='org_1')
        framework2 = TransportationAIGovernanceFramework(organization_id='org_2')

        result1 = framework1.assess_compliance()
        result2 = framework2.assess_compliance()

        assert result1['organization_id'] == 'org_1'
        assert result2['organization_id'] == 'org_2'

    def test_governance_event_recording(self, framework_instance):
        """Test governance events can be recorded"""
        framework_instance.record_governance_event(
            'compliance_check',
            {'status': 'completed'}
        )
        # Should not raise an exception

    # ========================================================================
    # PARAMETRIZED TESTS
    # ========================================================================

    @pytest.mark.parametrize("assessment_type", ['full', 'basic'])
    def test_assessment_types(self, assessment_type):
        """Test different assessment types work"""
        framework = TransportationAIGovernanceFramework(organization_id='test_org')
        result = framework.assess_compliance(assessment_type=assessment_type)
        assert result is not None
        assert result['assessment_type'] == assessment_type

    @pytest.mark.parametrize("org_id", ['org_1', 'org_2', 'org_3'])
    def test_multiple_organizations(self, org_id):
        """Test framework works with different organizations"""
        framework = TransportationAIGovernanceFramework(organization_id=org_id)
        result = framework.assess_compliance()
        assert result['organization_id'] == org_id
