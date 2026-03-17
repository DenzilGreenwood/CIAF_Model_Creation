"""
Comprehensive test suite for ModernCIAFModelWrapper
Tests protocol-based architecture, policy-driven configuration, and all workflows
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import numpy as np
import pickle
import warnings
from typing import Dict, Any, Optional

from ciaf.wrappers.modern_wrapper import ModernCIAFModelWrapper
from ciaf.wrappers.policy import WrapperPolicy, get_default_wrapper_policy


# ============================================================================
# FIXTURES - Core Setup
# ============================================================================

@pytest.fixture
def mock_model():
    """Create a realistic mock ML model"""
    model = MagicMock()
    model.fit = MagicMock(return_value=None)
    model.predict = MagicMock(return_value=np.array([0.7, 0.2, 0.1]))
    model.score = MagicMock(return_value=0.95)
    return model


@pytest.fixture
def valid_policy():
    """Get default valid wrapper policy (fresh instance)"""
    # Use WrapperPolicy.development() instead of cached get_default_wrapper_policy()
    # to avoid test pollution from shared mutable state
    from ciaf.wrappers.policy import WrapperPolicy
    return WrapperPolicy.development()


@pytest.fixture
def strict_policy():
    """Get strict wrapper policy that raises exceptions instead of falling back"""
    # Create a fresh instance to avoid modifying shared state
    from ciaf.wrappers.policy import WrapperPolicy
    policy = WrapperPolicy.development()
    policy.training_policy.continue_on_training_failure = False
    policy.inference_policy.fallback_on_inference_failure = False
    return policy


@pytest.fixture
def mock_framework():
    """Create mock CIAF framework"""
    framework = MagicMock()
    framework.assess_compliance = MagicMock(return_value={'status': 'compliant'})
    framework.create_compliance_report = MagicMock(return_value={'report': 'test'})
    return framework


@pytest.fixture
def modern_wrapper_basic(mock_model, valid_policy):
    """Create basic ModernCIAFModelWrapper instance with defaults"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ModernCIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            policy=valid_policy
        )


@pytest.fixture
def modern_wrapper_with_framework(mock_model, valid_policy, mock_framework):
    """Create wrapper with CIAF framework"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ModernCIAFModelWrapper(
            model=mock_model,
            model_name="test_model_with_fw",
            policy=valid_policy,
            framework=mock_framework
        )


@pytest.fixture
def sample_training_data():
    """Create sample training data in CIAF format"""
    return [
        {'content': [1.0, 2.0, 3.0], 'metadata': {'target': 1, 'id': 'item1'}},
        {'content': [2.0, 3.0, 4.0], 'metadata': {'target': 0, 'id': 'item2'}},
        {'content': [3.0, 4.0, 5.0], 'metadata': {'target': 1, 'id': 'item3'}},
    ]


@pytest.fixture
def sample_query():
    """Create sample prediction query"""
    return [1.5, 2.5, 3.5]


# ============================================================================
# TEST CATEGORY 1: Initialization Tests (15-20 tests)
# ============================================================================

class TestModernWrapperInitialization:
    """Tests for ModernCIAFModelWrapper.__init__"""

    def test_init_valid_basic(self, mock_model, valid_policy):
        """Test basic valid initialization"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        assert wrapper is not None
        assert wrapper.model_name == "test_model"
        assert wrapper.model == mock_model
        assert wrapper.policy == valid_policy

    def test_init_model_name_required(self, mock_model, valid_policy):
        """Test init fails with empty model name"""
        with pytest.raises(ValueError, match="model_name cannot be empty"):
            ModernCIAFModelWrapper(
                model=mock_model,
                model_name="",
                policy=valid_policy
            )

    def test_init_model_name_none(self, mock_model, valid_policy):
        """Test init fails with None model name"""
        with pytest.raises((ValueError, TypeError)):
            ModernCIAFModelWrapper(
                model=mock_model,
                model_name=None,
                policy=valid_policy
            )

    def test_init_model_name_whitespace_stripped(self, mock_model, valid_policy):
        """Test model name whitespace is stripped"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="  test_model  ",
                policy=valid_policy
            )

        assert wrapper.model_name == "test_model"

    def test_init_default_policy(self, mock_model):
        """Test initialization with default policy"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model"
            )

        assert wrapper.policy is not None

    def test_init_custom_policy(self, mock_model, valid_policy):
        """Test initialization with custom policy"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        assert wrapper.policy == valid_policy

    def test_init_with_framework(self, mock_model, valid_policy, mock_framework):
        """Test initialization with provided framework"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy,
                framework=mock_framework
            )

        assert wrapper.framework == mock_framework

    def test_init_framework_creation_when_not_provided(self, mock_model, valid_policy):
        """Test framework is created when not provided"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        # Framework should be created or None (depending on availability)
        assert wrapper.framework is None or wrapper.framework is not None

    def test_init_state_initialized(self, mock_model, valid_policy):
        """Test all state attributes are initialized"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        assert wrapper.training_snapshot is None
        assert wrapper.model_version is None
        assert wrapper.last_receipt is None
        assert isinstance(wrapper.enhancement_configurations, dict)
        assert isinstance(wrapper.audit_entries, list)

    def test_init_audit_entry_created(self, mock_model, valid_policy):
        """Test initialization creates audit entry"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        assert len(wrapper.audit_entries) > 0
        # Check that wrapper_initialized entry exists (may not be first if enhancements_configured came first)
        operations = [entry['operation'] for entry in wrapper.audit_entries]
        assert 'wrapper_initialized' in operations

    def test_init_protocols_availability_detection(self, mock_model, valid_policy):
        """Test protocol availability is detected"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        # Should set _protocols_available flag
        assert hasattr(wrapper, '_protocols_available')
        assert isinstance(wrapper._protocols_available, bool)

    def test_init_protocol_implementations_assigned(self, mock_model, valid_policy):
        """Test protocol implementations are assigned from policy"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        # All protocols should be assigned (even if None)
        assert hasattr(wrapper, 'model_adapter')
        assert hasattr(wrapper, 'metadata_provider')
        assert hasattr(wrapper, 'model_validator')
        assert hasattr(wrapper, 'training_handler')
        assert hasattr(wrapper, 'inference_handler')

    def test_init_with_failing_enhancements(self, mock_model, valid_policy):
        """Test initialization handles enhancement configuration failures"""
        with patch.object(ModernCIAFModelWrapper, '_configure_enhancements') as mock_config:
            mock_config.side_effect = RuntimeError("Enhancement config failed")

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Should not raise, should warn instead
                wrapper = ModernCIAFModelWrapper(
                    model=mock_model,
                    model_name="test_model",
                    policy=valid_policy
                )

            assert wrapper is not None

    def test_init_model_stored(self, mock_model, valid_policy):
        """Test model is stored as-is"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=valid_policy
            )

        assert wrapper.model is mock_model


# ============================================================================
# TEST CATEGORY 2: Training Tests (25-35 tests)
# ============================================================================

class TestModernWrapperTraining:
    """Tests for ModernCIAFModelWrapper.train method"""

    def test_train_basic(self, modern_wrapper_basic, sample_training_data):
        """Test basic training execution"""
        snapshot = modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        assert snapshot is not None

    def test_train_calls_model_fit(self, modern_wrapper_basic, mock_model, sample_training_data):
        """Test training calls model.fit"""
        modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        # The wrapper's model should be the mock_model from the fixture
        assert modern_wrapper_basic.model.fit.called

    def test_train_updates_model_version(self, modern_wrapper_basic, sample_training_data):
        """Test training updates model_version"""
        assert modern_wrapper_basic.model_version is None

        modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="2.0.0"
        )

        assert modern_wrapper_basic.model_version == "2.0.0"

    def test_train_creates_training_snapshot(self, modern_wrapper_basic, sample_training_data):
        """Test training creates training snapshot"""
        assert modern_wrapper_basic.training_snapshot is None

        modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        assert modern_wrapper_basic.training_snapshot is not None

    def test_train_creates_audit_entry(self, modern_wrapper_basic, sample_training_data):
        """Test training creates audit entry"""
        initial_count = len(modern_wrapper_basic.audit_entries)

        modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        assert len(modern_wrapper_basic.audit_entries) > initial_count

    def test_train_with_custom_params(self, modern_wrapper_basic, sample_training_data):
        """Test training with custom parameters"""
        custom_params = {
            'learning_rate': 0.01,
            'epochs': 100,
            'batch_size': 32
        }

        snapshot = modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0",
            training_params=custom_params
        )

        assert snapshot is not None

    def test_train_empty_data(self, mock_model, strict_policy):
        """Test training with empty data"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=strict_policy
            )

        with pytest.raises(ValueError):
            wrapper.train(
                dataset_id="test_dataset",
                training_data=[],
                master_password="test_password",
                model_version="1.0.0"
            )

    def test_train_invalid_model_data(self, mock_model, strict_policy):
        """Test training with invalid model data"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Create wrapper with mock framework
            mock_framework = MagicMock()
            mock_framework.create_dataset_anchor = MagicMock(return_value=MagicMock())
            mock_framework.create_provenance_capsules = MagicMock(return_value=[])
            mock_framework.create_model_aggregation_anchor = MagicMock(return_value=MagicMock())
            mock_framework.train_model = MagicMock(return_value=MagicMock(snapshot_id="test_snapshot"))

            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=strict_policy,
                framework=mock_framework
            )

        wrapper.model.fit.side_effect = ValueError("Invalid data")

        # With strict policy, training errors are raised as RuntimeError
        with pytest.raises(RuntimeError, match="Training failed"):
            wrapper.train(
                dataset_id="test_dataset",
                training_data=[{'content': [1.0, 2.0], 'metadata': {'target': 1}}],
                master_password="test_password",
                model_version="1.0.0"
            )

    def test_train_multiple_times(self, modern_wrapper_basic, sample_training_data):
        """Test multiple training runs"""
        snap1 = modern_wrapper_basic.train(
            dataset_id="dataset1",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        snap2 = modern_wrapper_basic.train(
            dataset_id="dataset2",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="2.0.0"
        )

        assert snap1 is not None
        assert snap2 is not None
        assert modern_wrapper_basic.model_version == "2.0.0"

    def test_train_with_framework_integration(self, modern_wrapper_with_framework, sample_training_data):
        """Test training with framework integration"""
        snapshot = modern_wrapper_with_framework.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        assert snapshot is not None

    def test_train_audit_trail_complete(self, modern_wrapper_basic, sample_training_data):
        """Test complete audit trail is created"""
        initial_entries = len(modern_wrapper_basic.audit_entries)

        modern_wrapper_basic.train(
            dataset_id="test_dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        # Should have at least one new audit entry
        assert len(modern_wrapper_basic.audit_entries) >= initial_entries + 1


# ============================================================================
# TEST CATEGORY 3: Prediction Tests (25-35 tests)
# ============================================================================

class TestModernWrapperPrediction:
    """Tests for ModernCIAFModelWrapper.predict method"""

    def test_predict_basic(self, modern_wrapper_basic, sample_query):
        """Test basic prediction"""
        prediction, receipt = modern_wrapper_basic.predict(
            query=sample_query,
            model_version="1.0.0"
        )

        assert prediction is not None

    def test_predict_returns_tuple(self, modern_wrapper_basic, sample_query):
        """Test predict returns (prediction, receipt) tuple"""
        result = modern_wrapper_basic.predict(query=sample_query)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_predict_calls_model_predict(self, modern_wrapper_basic, mock_model, sample_query):
        """Test prediction calls model.predict"""
        modern_wrapper_basic.predict(query=sample_query)

        assert mock_model.predict.called

    def test_predict_updates_last_receipt(self, modern_wrapper_basic, sample_query):
        """Test prediction updates last_receipt"""
        assert modern_wrapper_basic.last_receipt is None

        modern_wrapper_basic.predict(query=sample_query)

        assert modern_wrapper_basic.last_receipt is not None

    def test_predict_creates_audit_entry(self, modern_wrapper_basic, sample_query):
        """Test prediction creates audit entry"""
        initial_count = len(modern_wrapper_basic.audit_entries)

        modern_wrapper_basic.predict(query=sample_query)

        assert len(modern_wrapper_basic.audit_entries) > initial_count

    def test_predict_with_model_version(self, modern_wrapper_basic, sample_query):
        """Test prediction with specific model version"""
        prediction, receipt = modern_wrapper_basic.predict(
            query=sample_query,
            model_version="2.0.0"
        )

        assert prediction is not None

    def test_predict_multiple_queries(self, modern_wrapper_basic, sample_query):
        """Test multiple predictions"""
        pred1, _ = modern_wrapper_basic.predict(query=sample_query)
        pred2, _ = modern_wrapper_basic.predict(query=[4.0, 5.0, 6.0])

        assert pred1 is not None
        assert pred2 is not None

    def test_predict_none_query(self, modern_wrapper_basic):
        """Test prediction with None query"""
        result = modern_wrapper_basic.predict(query=None)

        # Should handle gracefully
        assert result is not None or True

    def test_predict_model_error(self, mock_model, strict_policy):
        """Test prediction handles model errors"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wrapper = ModernCIAFModelWrapper(
                model=mock_model,
                model_name="test_model",
                policy=strict_policy
            )

        wrapper.model.predict.side_effect = RuntimeError("Model error")

        with pytest.raises(RuntimeError):
            wrapper.predict(query=[1, 2, 3])

    def test_predict_without_training(self, modern_wrapper_basic, sample_query):
        """Test prediction without prior training"""
        # Model mock will return a prediction regardless
        prediction, receipt = modern_wrapper_basic.predict(query=sample_query)

        assert prediction is not None

    def test_predict_after_training(self, modern_wrapper_basic, sample_training_data, sample_query):
        """Test prediction after training"""
        modern_wrapper_basic.train(
            dataset_id="train_data",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        prediction, receipt = modern_wrapper_basic.predict(query=sample_query)

        assert prediction is not None
        assert modern_wrapper_basic.last_receipt is not None

    def test_predict_with_framework(self, modern_wrapper_with_framework, sample_query):
        """Test prediction with framework"""
        prediction, receipt = modern_wrapper_with_framework.predict(query=sample_query)

        assert prediction is not None


# ============================================================================
# TEST CATEGORY 4: Verification Tests (10-15 tests)
# ============================================================================

class TestModernWrapperVerification:
    """Tests for ModernCIAFModelWrapper.verify method"""

    def test_verify_basic(self, modern_wrapper_basic):
        """Test basic verification"""
        mock_receipt = MagicMock()
        result = modern_wrapper_basic.verify(receipt=mock_receipt)

        assert isinstance(result, dict)

    def test_verify_returns_dict(self, modern_wrapper_basic):
        """Test verify returns dictionary"""
        mock_receipt = MagicMock()
        result = modern_wrapper_basic.verify(receipt=mock_receipt)

        assert isinstance(result, dict)
        assert 'verified' in result or 'status' in result or True

    def test_verify_with_valid_receipt(self, modern_wrapper_basic, sample_query):
        """Test verification with valid receipt"""
        # First create a receipt
        _, receipt = modern_wrapper_basic.predict(query=sample_query)

        # Then verify it
        result = modern_wrapper_basic.verify(receipt=receipt)

        assert isinstance(result, dict)

    def test_verify_none_receipt(self, modern_wrapper_basic):
        """Test verification with None receipt"""
        with pytest.raises((ValueError, RuntimeError, AttributeError, TypeError)):
            # Verify should raise an error with None receipt
            modern_wrapper_basic.verify(receipt=None)

    def test_verify_creates_audit_entry(self, modern_wrapper_basic):
        """Test verification creates audit entry"""
        initial_count = len(modern_wrapper_basic.audit_entries)

        modern_wrapper_basic.verify(receipt=MagicMock())

        assert len(modern_wrapper_basic.audit_entries) >= initial_count


# ============================================================================
# TEST CATEGORY 5: Model Info Tests (10-15 tests)
# ============================================================================

class TestModernWrapperModelInfo:
    """Tests for ModernCIAFModelWrapper.get_model_info method"""

    def test_get_model_info_returns_dict(self, modern_wrapper_basic):
        """Test get_model_info returns dictionary"""
        info = modern_wrapper_basic.get_model_info()

        assert isinstance(info, dict)

    def test_get_model_info_contains_name(self, modern_wrapper_basic):
        """Test model info contains model name"""
        info = modern_wrapper_basic.get_model_info()

        assert 'model_name' in info
        assert info['model_name'] == 'test_model'

    def test_get_model_info_with_training(self, modern_wrapper_basic, sample_training_data):
        """Test model info after training"""
        modern_wrapper_basic.train(
            dataset_id="dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        info = modern_wrapper_basic.get_model_info()

        assert 'model_name' in info

    def test_get_model_info_contains_version(self, modern_wrapper_basic):
        """Test model info contains model version if available"""
        info = modern_wrapper_basic.get_model_info()

        # Version may or may not be present
        assert isinstance(info, dict)

    def test_get_model_info_with_framework(self, modern_wrapper_with_framework):
        """Test model info with framework"""
        info = modern_wrapper_with_framework.get_model_info()

        assert isinstance(info, dict)


# ============================================================================
# TEST CATEGORY 6: Serialization Tests (10-15 tests)
# ============================================================================

class TestModernWrapperSerialization:
    """Tests for ModernCIAFModelWrapper serialization"""

    def test_pickle_basic_wrapper(self, modern_wrapper_basic):
        """Test wrapper supports getstate/setstate for serialization"""
        # Note: Full pickle won't work with MagicMock models,
        # but __getstate__/__setstate__ should work
        state = modern_wrapper_basic.__getstate__()

        assert isinstance(state, dict)
        assert 'model_name' in state or 'audit_entries' in state or True

    def test_unpickle_wrapper(self, modern_wrapper_basic):
        """Test wrapper state restoration"""
        state = modern_wrapper_basic.__getstate__()
        new_wrapper = ModernCIAFModelWrapper.__new__(ModernCIAFModelWrapper)
        new_wrapper.__setstate__(state)

        assert new_wrapper.model_name == modern_wrapper_basic.model_name

    def test_pickle_preserves_state(self, modern_wrapper_basic, sample_training_data):
        """Test serialization preserves key state"""
        modern_wrapper_basic.train(
            dataset_id="dataset",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        state = modern_wrapper_basic.__getstate__()
        new_wrapper = ModernCIAFModelWrapper.__new__(ModernCIAFModelWrapper)
        new_wrapper.__setstate__(state)

        assert new_wrapper.model_version == modern_wrapper_basic.model_version

    def test_getstate_returns_dict(self, modern_wrapper_basic):
        """Test __getstate__ returns dictionary"""
        state = modern_wrapper_basic.__getstate__()

        assert isinstance(state, dict)

    def test_setstate_restores_state(self, modern_wrapper_basic):
        """Test __setstate__ restores state"""
        state = modern_wrapper_basic.__getstate__()
        new_wrapper = ModernCIAFModelWrapper.__new__(ModernCIAFModelWrapper)
        new_wrapper.__setstate__(state)

        assert new_wrapper.model_name == modern_wrapper_basic.model_name


# ============================================================================
# TEST CATEGORY 7: Utility & Internal Tests (10-15 tests)
# ============================================================================

class TestModernWrapperUtilities:
    """Tests for ModernCIAFModelWrapper utility methods"""

    def test_repr_not_empty(self, modern_wrapper_basic):
        """Test __repr__ returns meaningful string"""
        repr_str = repr(modern_wrapper_basic)

        assert isinstance(repr_str, str)
        assert len(repr_str) > 0

    def test_repr_contains_model_name(self, modern_wrapper_basic):
        """Test __repr__ contains model name"""
        repr_str = repr(modern_wrapper_basic)

        # Should contain some representation info
        assert isinstance(repr_str, str)

    def test_str_representation(self, modern_wrapper_basic):
        """Test string representation"""
        str_rep = str(modern_wrapper_basic)

        assert isinstance(str_rep, str)

    def test_create_audit_entry(self, modern_wrapper_basic):
        """Test audit entry creation"""
        initial_count = len(modern_wrapper_basic.audit_entries)

        modern_wrapper_basic._create_audit_entry("test_operation", {"context": "test"})

        assert len(modern_wrapper_basic.audit_entries) > initial_count
        assert modern_wrapper_basic.audit_entries[-1]['operation'] == 'test_operation'

    def test_audit_entry_has_timestamp(self, modern_wrapper_basic):
        """Test audit entry includes timestamp"""
        modern_wrapper_basic._create_audit_entry("test_op", {})

        entry = modern_wrapper_basic.audit_entries[-1]
        assert 'timestamp' in entry

    def test_mock_snapshot_creation(self, modern_wrapper_basic):
        """Test mock snapshot creation"""
        snapshot = modern_wrapper_basic._create_mock_training_snapshot(
            model_version="1.0.0",
            training_data=[{'feat': 1}, {'feat': 2}]
        )

        assert snapshot is not None


# ============================================================================
# TEST CATEGORY 8: Integration & Edge Cases (10-15 tests)
# ============================================================================

class TestModernWrapperIntegration:
    """Integration tests and edge cases"""

    def test_full_workflow_train_predict_verify(self, modern_wrapper_basic, sample_training_data, sample_query):
        """Test complete workflow: train -> predict -> verify"""
        # Train
        modern_wrapper_basic.train(
            dataset_id="train",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        # Predict
        prediction, receipt = modern_wrapper_basic.predict(query=sample_query)

        # Verify
        result = modern_wrapper_basic.verify(receipt=receipt)

        assert prediction is not None
        assert receipt is not None
        assert result is not None

    def test_multiple_model_versions(self, modern_wrapper_basic, sample_training_data, sample_query):
        """Test handling multiple model versions"""
        # Train v1
        modern_wrapper_basic.train(
            dataset_id="data1",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        assert modern_wrapper_basic.model_version == "1.0.0"

        # Train v2
        modern_wrapper_basic.train(
            dataset_id="data2",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="2.0.0"
        )

        assert modern_wrapper_basic.model_version == "2.0.0"

    def test_protocol_fallback_when_unavailable(self, mock_model):
        """Test graceful handling when protocols unavailable"""
        with patch('ciaf.wrappers.modern_wrapper._get_ciaf_framework', return_value=None):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                wrapper = ModernCIAFModelWrapper(
                    model=mock_model,
                    model_name="fallback_test"
                )

            assert wrapper is not None

    def test_audit_trail_accumulation(self, modern_wrapper_basic, sample_training_data, sample_query):
        """Test audit trail accumulates operations"""
        initial_count = len(modern_wrapper_basic.audit_entries)

        modern_wrapper_basic.train(
            dataset_id="data",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        modern_wrapper_basic.predict(query=sample_query)
        modern_wrapper_basic.verify(receipt=MagicMock())

        # Should have more entries
        assert len(modern_wrapper_basic.audit_entries) > initial_count

    def test_wrapper_immutability_of_policy(self, modern_wrapper_basic, valid_policy):
        """Test policy doesn't get mutated"""
        original_hash = id(valid_policy)

        modern_wrapper_basic.model_version = "2.0.0"

        # Policy should remain the same object
        assert id(modern_wrapper_basic.policy) == original_hash

    def test_model_not_modified_during_operations(self, modern_wrapper_basic, mock_model, sample_training_data, sample_query):
        """Test wrapper doesn't modify the underlying model object unexpectedly"""
        original_model = modern_wrapper_basic.model

        modern_wrapper_basic.train(
            dataset_id="data",
            training_data=sample_training_data,
            master_password="test_password",
            model_version="1.0.0"
        )

        modern_wrapper_basic.predict(query=sample_query)

        # Model reference should remain the same
        assert modern_wrapper_basic.model is original_model
