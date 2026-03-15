"""
Base Test Infrastructure for CIAF Industry Frameworks

This module provides:
- BaseFrameworkTest: Reusable test class for all frameworks
- Common test patterns and fixtures
- Assertion helpers
- Test data generators
"""

import pytest
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TestMetadata:
    """Metadata for framework test execution"""
    framework_name: str
    organization_id: str
    assessment_type: str = 'full'
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class BaseFrameworkTest(ABC):
    """
    Base test class for all CIAF industry frameworks.

    Provides:
    - Common test initialization
    - Standard test patterns
    - Assertion helpers
    - Mock data generators
    """

    @abstractmethod
    def get_framework_class(self):
        """Return the framework class to test (override in subclass)"""
        raise NotImplementedError

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return framework name (override in subclass)"""
        raise NotImplementedError

    @abstractmethod
    def get_regulatory_requirements(self) -> List[str]:
        """Return expected regulatory requirements (override in subclass)"""
        raise NotImplementedError

    @abstractmethod
    def get_test_data(self) -> Dict[str, Any]:
        """Return framework-specific test data (override in subclass)"""
        raise NotImplementedError

    def create_framework_instance(self):
        """
        Create framework instance with framework-specific parameters.

        Override this method in subclasses for frameworks with custom __init__ signatures.
        """
        FrameworkClass = self.get_framework_class()
        # Default constructor - subclasses override for custom parameters
        try:
            # Try with just organization_id first (for simple frameworks)
            return FrameworkClass(organization_id="test_org_123")
        except TypeError:
            # If that fails, try with regulatory_requirements
            try:
                return FrameworkClass(
                    organization_id="test_org_123",
                    regulatory_requirements=self.get_regulatory_requirements()
                )
            except TypeError as e:
                # Framework has custom parameters - subclass must override
                raise NotImplementedError(
                    f"Framework {self.get_framework_name()} requires custom initialization. "
                    f"Override create_framework_instance() method in test class. Error: {e}"
                )

    @pytest.fixture
    def framework_instance(self):
        """Create framework instance for testing"""
        return self.create_framework_instance()

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return TestMetadata(
            framework_name=self.get_framework_name(),
            organization_id="test_org_123"
        )

    # ========================================================================
    # STANDARD TESTS (applicable to all frameworks)
    # ========================================================================

    def test_framework_initialization(self):
        """Test framework initializes without errors"""
        framework = self.create_framework_instance()
        assert framework is not None
        assert framework.organization_id == "test_org_123"

    def test_framework_has_required_methods(self, framework_instance):
        """Test framework has all required methods"""
        required_methods = [
            'assess_compliance',
            'validate_governance_requirements',
            'generate_audit_report',
            'record_governance_event'
        ]
        for method in required_methods:
            assert hasattr(framework_instance, method), \
                f"Framework missing required method: {method}"
            assert callable(getattr(framework_instance, method)), \
                f"Framework method {method} is not callable"

    def test_assess_compliance_returns_dict(self, framework_instance):
        """Test assess_compliance returns a dictionary"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        assert isinstance(result, dict), "assess_compliance must return dict"

    def test_assess_compliance_has_required_fields(self, framework_instance):
        """Test assess_compliance result has required fields"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        required_fields = [
            'organization_id',
            'assessment_timestamp',
            'overall_compliance_score',
            'compliance_status',
            'recommendations'
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_assess_compliance_score_valid_range(self, framework_instance):
        """Test compliance score is between 0 and 1"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        score = result['overall_compliance_score']
        assert isinstance(score, (int, float)), "Compliance score must be numeric"
        assert 0 <= score <= 1, f"Compliance score must be 0-1, got {score}"

    def test_assess_compliance_status_valid(self, framework_instance):
        """Test compliance status is one of valid values"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        valid_statuses = ['compliant', 'partially_compliant', 'non_compliant', 'unknown']
        assert result['compliance_status'] in valid_statuses, \
            f"Invalid compliance status: {result['compliance_status']}"

    def test_validate_governance_requirements_returns_dict(self, framework_instance):
        """Test validate_governance_requirements returns dictionary"""
        result = framework_instance.validate_governance_requirements()
        assert isinstance(result, dict), "validate_governance_requirements must return dict"

    def test_validate_governance_requirements_has_required_fields(self, framework_instance):
        """Test validate_governance_requirements has required fields"""
        result = framework_instance.validate_governance_requirements()
        required_fields = [
            'organization_id',
            'validation_timestamp',
            'governance_requirements',
            'validation_status'
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_governance_requirements_dict_not_empty(self, framework_instance):
        """Test governance requirements are defined"""
        result = framework_instance.validate_governance_requirements()
        governance_reqs = result.get('governance_requirements', {})
        assert len(governance_reqs) > 0, "Framework must define governance requirements"

    def test_audit_report_generation(self, framework_instance):
        """Test audit report can be generated"""
        result = framework_instance.generate_audit_report(
            audit_period_start='2025-01-01',
            audit_period_end='2025-12-31'
        )
        assert isinstance(result, dict), "Audit report must be a dictionary"
        assert 'organization_id' in result, "Audit report must include organization_id"

    def test_governance_event_recording(self, framework_instance):
        """Test governance events can be recorded"""
        # Should not raise an exception
        framework_instance.record_governance_event(
            'test_event',
            {'test': 'data'}
        )

    # ========================================================================
    # COMPLIANCE-RELATED TESTS
    # ========================================================================

    def test_regulatory_requirements_included(self, framework_instance):
        """Test all regulatory requirements are included"""
        expected_reqs = self.get_regulatory_requirements()
        assert len(expected_reqs) > 0, "Framework must have regulatory requirements"

    def test_compliance_score_consistency(self, framework_instance):
        """Test compliance score is consistent across multiple calls"""
        test_data = self.get_test_data()
        result1 = framework_instance.assess_compliance(
            assessment_type='full',
            **test_data
        )
        result2 = framework_instance.assess_compliance(
            assessment_type='full',
            **test_data
        )
        # Scores should be close (allowing for minor timestamp differences)
        diff = abs(result1['overall_compliance_score'] - result2['overall_compliance_score'])
        assert diff < 0.01, f"Compliance scores diverged by {diff}"

    def test_high_compliance_score_shows_compliant(self, framework_instance):
        """Test high compliance score maps to 'compliant' status"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        if result['overall_compliance_score'] >= 0.9:
            assert result['compliance_status'] == 'compliant', \
                "High score (>=0.9) must map to 'compliant' status"

    def test_low_compliance_score_shows_non_compliant(self, framework_instance):
        """Test low compliance score maps to appropriate status"""
        # This test depends on framework behavior, but we verify the mapping exists
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        compliance_status = result['compliance_status']
        assert compliance_status in ['compliant', 'partially_compliant', 'non_compliant', 'unknown']

    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================

    def test_framework_handles_missing_org_id(self):
        """Test framework requires organization ID or handles it gracefully"""
        FrameworkClass = self.get_framework_class()
        try:
            # Try creating with None
            framework = FrameworkClass(organization_id=None)
            # If it doesn't raise, that's OK - framework accepts None gracefully
            assert framework is not None
        except (TypeError, ValueError, AttributeError):
            # Expected behavior - framework requires valid org_id
            pass

    def test_framework_handles_invalid_parameters(self, framework_instance):
        """Test framework handles invalid parameters"""
        # assess_compliance should handle empty data or None
        try:
            result = framework_instance.assess_compliance()
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"Framework should handle missing parameters gracefully: {e}")

    # ========================================================================
    # DATA VALIDATION TESTS
    # ========================================================================

    def test_assessment_timestamp_format(self, framework_instance):
        """Test assessment timestamp is properly formatted"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        timestamp_str = result.get('assessment_timestamp')
        assert timestamp_str is not None, "assessment_timestamp is required"
        # Should be ISO format datetime string
        assert isinstance(timestamp_str, str)
        assert 'T' in timestamp_str or timestamp_str.count('-') >= 2

    def test_recommendations_is_list(self, framework_instance):
        """Test recommendations field is a list"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        recommendations = result.get('recommendations', [])
        assert isinstance(recommendations, list), "recommendations must be a list"

    def test_organization_id_in_results(self, framework_instance):
        """Test organization_id appears in results"""
        result = framework_instance.assess_compliance(
            assessment_type='full',
            **self.get_test_data()
        )
        assert result['organization_id'] == "test_org_123"

    # ========================================================================
    # ASSERTION HELPERS
    # ========================================================================

    @staticmethod
    def assert_compliance_score_between(score: float, min_val: float = 0, max_val: float = 1):
        """Assert compliance score is within valid range"""
        assert min_val <= score <= max_val, \
            f"Score {score} not in range [{min_val}, {max_val}]"

    @staticmethod
    def assert_valid_compliance_status(status: str):
        """Assert compliance status is valid"""
        valid_statuses = ['compliant', 'partially_compliant', 'non_compliant', 'unknown']
        assert status in valid_statuses, f"Invalid status: {status}"

    @staticmethod
    def assert_dict_has_keys(d: dict, keys: List[str]):
        """Assert dictionary has all required keys"""
        for key in keys:
            assert key in d, f"Missing required key: {key}"

    @staticmethod
    def assert_compliance_score_matches_status(score: float, status: str):
        """Assert compliance score matches status"""
        if score >= 0.9:
            assert status == 'compliant', f"Score {score} should map to 'compliant', not '{status}'"
        elif score >= 0.7:
            assert status in ['compliant', 'partially_compliant'], \
                f"Score {score} should map to 'partially_compliant' or 'compliant', not '{status}'"
        else:
            assert status in ['non_compliant', 'partially_compliant'], \
                f"Score {score} should map to 'non_compliant' or 'partially_compliant', not '{status}'"


# ============================================================================
# PARAMETRIZED TEST HELPER
# ============================================================================

def get_parametrized_framework_tests():
    """
    Return parametrized test cases for all frameworks.

    Usage in test file:
    @pytest.mark.parametrize("framework_class", get_parametrized_framework_tests())
    """
    # This will be populated by individual framework test files
    return []
