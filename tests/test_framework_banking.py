"""
Comprehensive Test Suite for Banking & Financial Services AI Governance Framework

Tests cover:
- Fair lending compliance validation
- Credit decision governance
- Algorithmic trading oversight
- Regulatory compliance assessment
- Governance requirement validation
- Audit trail generation
- Multi-organization isolation
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List

from ciaf.industries.banking import BankingAIGovernanceFramework
from tests.conftest_frameworks import BaseFrameworkTest


class TestBankingFramework(BaseFrameworkTest):
    """Comprehensive test suite for Banking AI Governance Framework"""

    def get_framework_class(self):
        """Return Banking framework class"""
        return BankingAIGovernanceFramework

    def get_framework_name(self) -> str:
        """Return framework name"""
        return "Banking"

    def get_regulatory_requirements(self) -> List[str]:
        """Return banking regulatory requirements"""
        return ['FCRA', 'ECOA', 'GDPR', 'EU_AI_ACT', 'BASEL_III', 'MiFID_II']

    def get_test_data(self) -> Dict[str, Any]:
        """Return banking-specific test data"""
        return {
            'application_data': {
                'application_id': 'APP123456',
                'applicant_income': 75000,
                'credit_history_length': 15,
                'current_debt': 25000,
                'employment_status': 'employed',
                'race': 'not_disclosed',
                'gender': 'not_disclosed',
                'age': 35,
                'collateral_value': 150000,
                'loan_amount': 200000,
                'loan_purpose': 'home_purchase'
            },
            'trading_data': {
                'algorithm_id': 'ALGO_TRADING_001',
                'daily_volume': 5000000,
                'volatility_index': 0.15,
                'market_impact': 0.02,
                'slippage': 0.001,
                'circuit_breaker_activations': 0,
                'velocity': 1000
            }
        }

    # ========================================================================
    # BANKING-SPECIFIC TESTS
    # ========================================================================

    def test_fair_lending_validation(self, framework_instance):
        """Test fair lending compliance validation"""
        test_data = self.get_test_data()
        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )

        assert hasattr(result, 'is_compliant'), "Result must have is_compliant"
        assert hasattr(result, 'bias_metrics'), "Result must have bias_metrics"
        assert hasattr(result, 'disparate_impact_ratio'), "Result must have disparate_impact_ratio"
        assert hasattr(result, 'compliance_score'), "Result must have compliance_score"

        assert isinstance(result.is_compliant, bool)
        assert isinstance(result.bias_metrics, dict)
        assert isinstance(result.disparate_impact_ratio, float)
        assert isinstance(result.compliance_score, float)
        assert 0 <= result.disparate_impact_ratio <= 1
        assert 0 <= result.compliance_score <= 1

    def test_credit_decision_with_governance(self, framework_instance):
        """Test credit decision includes governance oversight"""
        test_data = self.get_test_data()
        result = framework_instance.make_credit_decision_with_governance(
            application_data=test_data['application_data'],
            model_version='v2.1'
        )

        # Validate result fields
        assert hasattr(result, 'decision')
        assert hasattr(result, 'credit_score')
        assert hasattr(result, 'explanation')
        assert hasattr(result, 'fairness_validation')
        assert hasattr(result, 'audit_trail_id')
        assert hasattr(result, 'human_review_required')

        # Validate field types
        assert result.decision in ['approved', 'denied', 'conditional']
        assert isinstance(result.credit_score, (int, float))
        assert isinstance(result.explanation, str)
        assert isinstance(result.audit_trail_id, str)
        assert isinstance(result.human_review_required, bool)

    def test_algorithmic_trading_monitoring(self, framework_instance):
        """Test algorithmic trading oversight"""
        test_data = self.get_test_data()
        result = framework_instance.monitor_algorithmic_trading(
            trading_algorithm_id='ALGO_TRADING_001',
            trading_data=test_data['trading_data']
        )

        # Validate result fields
        assert hasattr(result, 'trading_algorithm_id')
        assert hasattr(result, 'market_impact_assessment')
        assert hasattr(result, 'risk_metrics')
        assert hasattr(result, 'regulatory_compliance')
        assert hasattr(result, 'halt_trading_recommended')

        # Validate field types
        assert isinstance(result.trading_algorithm_id, str)
        assert isinstance(result.market_impact_assessment, dict)
        assert isinstance(result.risk_metrics, dict)
        assert isinstance(result.regulatory_compliance, dict)
        assert isinstance(result.halt_trading_recommended, bool)

    def test_fair_lending_protected_attributes(self, framework_instance):
        """Test fair lending checks protected attributes"""
        test_data = self.get_test_data()
        protected_attrs = ['race', 'gender', 'age']

        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data'],
            protected_attributes=protected_attrs
        )

        # All protected attributes should be in analysis
        for attr in protected_attrs:
            assert attr in result.protected_attribute_analysis or \
                   len(result.protected_attribute_analysis) > 0

    def test_disparate_impact_ratio_valid(self, framework_instance):
        """Test disparate impact ratio follows 80% rule"""
        test_data = self.get_test_data()
        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )

        # Disparate impact should follow 80% rule (>0.8 is compliant-friendly)
        assert 0 <= result.disparate_impact_ratio <= 1
        # Higher ratio means more equitable treatment
        if result.disparate_impact_ratio < 0.8:
            assert result.remediation_required, "Low DI ratio should flag remediation"

    def test_compliance_assessment_includes_trading(self, framework_instance):
        """Test compliance assessment includes trading oversight"""
        test_data = self.get_test_data()
        result = framework_instance.assess_compliance(
            assessment_type='full',
            application_data=test_data['application_data'],
            trading_data=test_data['trading_data']
        )

        assert 'fair_lending_compliance' in result
        assert 'trading_oversight' in result

        # Both should have non-None values when data provided
        assert result['fair_lending_compliance'] is not None
        assert result['trading_oversight'] is not None

    def test_compliance_assessment_partial_data(self, framework_instance):
        """Test compliance assessment works with partial data"""
        test_data = self.get_test_data()

        # Only credit data
        result1 = framework_instance.assess_compliance(
            assessment_type='full',
            application_data=test_data['application_data']
        )
        assert result1['fair_lending_compliance'] is not None
        assert result1['trading_oversight'] is None

        # Only trading data
        result2 = framework_instance.assess_compliance(
            assessment_type='full',
            trading_data=test_data['trading_data']
        )
        assert result2['fair_lending_compliance'] is None
        assert result2['trading_oversight'] is not None

    def test_governance_requirements_includes_fair_lending(self, framework_instance):
        """Test governance requirements cover fair lending"""
        result = framework_instance.validate_governance_requirements()

        governance_reqs = result['governance_requirements']
        assert 'fair_lending_enforcement' in governance_reqs
        assert governance_reqs['fair_lending_enforcement'].get('enabled') == True

    def test_governance_requirements_includes_trading_oversight(self, framework_instance):
        """Test governance requirements cover algorithmic trading"""
        result = framework_instance.validate_governance_requirements()

        governance_reqs = result['governance_requirements']
        assert 'algorithmic_trading_oversight' in governance_reqs
        assert governance_reqs['algorithmic_trading_oversight'].get('enabled') == True

    def test_regulatory_requirements_validated(self, framework_instance):
        """Test all regulatory requirements are validated"""
        result = framework_instance.validate_governance_requirements()

        governance_reqs = result['governance_requirements']
        assert 'regulatory_coverage' in governance_reqs

        regulatory_coverage = governance_reqs['regulatory_coverage']
        assert 'required' in regulatory_coverage
        assert 'implemented' in regulatory_coverage
        assert 'compliant' in regulatory_coverage

    # ========================================================================
    # BIAS AND FAIRNESS TESTS
    # ========================================================================

    def test_bias_metrics_included_in_compliance(self, framework_instance):
        """Test bias metrics are included in compliance assessment"""
        test_data = self.get_test_data()
        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )

        assert result.bias_metrics is not None
        assert len(result.bias_metrics) > 0

    def test_compliance_score_reflects_bias(self, framework_instance):
        """Test compliance score reflects bias metrics"""
        test_data = self.get_test_data()
        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )

        # Score should be negatively correlated with bias
        if result.compliance_score < 0.7:
            assert result.remediation_required or not result.is_compliant

    def test_protected_attributes_always_checked(self, framework_instance):
        """Test all protected attributes are checked"""
        test_data = self.get_test_data()

        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )

        # Default protected attributes should be checked
        # Common protected attributes: race, gender, age, religion, national_origin
        assert len(result.protected_attribute_analysis) >= 3

    # ========================================================================
    # AUDIT AND TRAIL TESTS
    # ========================================================================

    def test_credit_decision_creates_audit_trail(self, framework_instance):
        """Test credit decisions are logged in audit trail"""
        test_data = self.get_test_data()
        result = framework_instance.make_credit_decision_with_governance(
            application_data=test_data['application_data'],
            model_version='v2.1'
        )

        # Audit trail ID should be created
        assert result.audit_trail_id is not None
        assert len(result.audit_trail_id) > 0

    def test_human_review_flag_set_appropriately(self, framework_instance):
        """Test human review flag is set based on risk"""
        test_data = self.get_test_data()
        result = framework_instance.make_credit_decision_with_governance(
            application_data=test_data['application_data'],
            model_version='v2.1'
        )

        # Should be boolean
        assert isinstance(result.human_review_required, bool)

        # Review required if:
        # - Fair lending not compliant
        # - High risk score
        # - Conditional decision
        if not result.fairness_validation.is_compliant:
            assert result.human_review_required

    # ========================================================================
    # ISOLATION AND SECURITY TESTS
    # ========================================================================

    def test_organization_isolation(self):
        """Test different organizations don't interfere"""
        framework1 = BankingAIGovernanceFramework(
            organization_id='org_1',
            regulatory_requirements=self.get_regulatory_requirements()
        )
        framework2 = BankingAIGovernanceFramework(
            organization_id='org_2',
            regulatory_requirements=self.get_regulatory_requirements()
        )

        result1 = framework1.assess_compliance(assessment_type='full')
        result2 = framework2.assess_compliance(assessment_type='full')

        # Results should have different org IDs
        assert result1['organization_id'] == 'org_1'
        assert result2['organization_id'] == 'org_2'

    def test_framework_instances_independent(self):
        """Test framework instances are truly independent"""
        framework1 = BankingAIGovernanceFramework(
            organization_id='org_1',
            fair_lending_enforcement=True,
            algorithmic_trading_oversight=True
        )
        framework2 = BankingAIGovernanceFramework(
            organization_id='org_2',
            fair_lending_enforcement=False,
            algorithmic_trading_oversight=False
        )

        # Configurations should be independent
        assert framework1.fair_lending_enforcement == True
        assert framework2.fair_lending_enforcement == False

    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================

    def test_compliance_assessment_completes_quickly(self, framework_instance):
        """Test compliance assessment doesn't take excessive time"""
        import time
        test_data = self.get_test_data()

        start = time.time()
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **test_data
        )
        end = time.time()

        duration = end - start
        assert duration < 5.0, f"Compliance assessment took {duration}s (target: <5s)"

    def test_fair_lending_validation_completes_quickly(self, framework_instance):
        """Test fair lending validation is performant"""
        import time
        test_data = self.get_test_data()

        start = time.time()
        result = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )
        end = time.time()

        duration = end - start
        assert duration < 2.0, f"Fair lending validation took {duration}s (target: <2s)"

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_end_to_end_credit_workflow(self, framework_instance):
        """Test complete credit decision workflow"""
        test_data = self.get_test_data()

        # Step 1: Validate fair lending
        fair_lending = framework_instance.validate_fair_lending(
            application_data=test_data['application_data']
        )
        assert fair_lending is not None

        # Step 2: Make credit decision
        decision = framework_instance.make_credit_decision_with_governance(
            application_data=test_data['application_data'],
            model_version='v2.1'
        )
        assert decision is not None
        assert decision.fairness_validation == fair_lending

        # Step 3: Generate compliance assessment
        compliance = framework_instance.assess_compliance(
            assessment_type='full',
            application_data=test_data['application_data']
        )
        assert compliance is not None
        assert 'fair_lending_compliance' in compliance

    def test_end_to_end_trading_workflow(self, framework_instance):
        """Test complete algorithmic trading workflow"""
        test_data = self.get_test_data()

        # Step 1: Monitor trading
        trading = framework_instance.monitor_algorithmic_trading(
            trading_algorithm_id='ALGO_TRADING_001',
            trading_data=test_data['trading_data']
        )
        assert trading is not None

        # Step 2: Include in compliance assessment
        compliance = framework_instance.assess_compliance(
            assessment_type='full',
            trading_data=test_data['trading_data']
        )
        assert compliance is not None
        assert 'trading_oversight' in compliance

        # Step 3: Generate audit report
        report = framework_instance.generate_audit_report(
            audit_period_start='2025-01-01',
            audit_period_end='2025-12-31'
        )
        assert report is not None


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("assessment_type", ['full', 'basic', 'minimal'])
def test_assessment_types(assessment_type):
    """Test different assessment types"""
    framework = BankingAIGovernanceFramework(
        organization_id='test_org',
        regulatory_requirements=['FCRA', 'ECOA']
    )
    result = framework.assess_compliance(assessment_type=assessment_type)
    assert result is not None
    assert result['assessment_type'] == assessment_type


@pytest.mark.parametrize("model_version", ['v1.0', 'v2.0', 'v2.1', 'v3.0'])
def test_multiple_model_versions(model_version):
    """Test credit decisions with different model versions"""
    framework = BankingAIGovernanceFramework(organization_id='test_org')
    test_data = {
        'application_id': 'APP123456',
        'applicant_income': 75000,
        'credit_history_length': 15,
        'current_debt': 25000,
        'employment_status': 'employed'
    }

    result = framework.make_credit_decision_with_governance(
        application_data=test_data,
        model_version=model_version
    )
    assert result is not None


@pytest.mark.parametrize("org_id", ['banking_corp_1', 'banking_corp_2', 'fintech_startup'])
def test_multiple_organizations(org_id):
    """Test multiple organizations work independently"""
    framework = BankingAIGovernanceFramework(organization_id=org_id)
    result = framework.assess_compliance(assessment_type='full')
    assert result['organization_id'] == org_id
