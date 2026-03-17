# Phase 2 Implementation Plan: Modern Wrapper Testing

**Status**: Ready to implement
**Target Module**: modern_wrapper.py (902 lines, currently 6% coverage)
**Expected Tests**: 100-150 tests
**Estimated Time**: 6-8 hours
**Expected Coverage**: 6% → 60%+

---

## Overview

The ModernCIAFModelWrapper is a complex, protocol-based wrapper using dependency injection and policy-driven configuration. It has 15+ methods across 902 lines covering:

1. **Initialization & Configuration** (lines 90-191)
   - Model setup with validation
   - Policy configuration
   - Framework initialization
   - Enhancement configuration
   - Compliance setup

2. **Core Operations** (lines 193-681)
   - Training workflow (177 lines)
   - Prediction workflow (200 lines)
   - Verification
   - Model info retrieval

3. **Internal Operations** (lines 765-900)
   - Audit logging
   - Mock object creation
   - Serialization/deserialization
   - String representation

---

## Test Categories & Estimates

### 1. Initialization Tests (15-20 tests)
- Empty model_name validation
- Valid initialization with defaults
- Custom policy initialization
- Framework initialization (present/absent)
- Protocol availability detection
- Enhancement configuration success/failure
- Compliance configuration
- Audit entry creation

**Lines Covered**: 90-191 (~100 lines)

### 2. Training Tests (25-35 tests)
- Basic training workflow
- Training with custom parameters
- Training data validation
- Training snapshot creation
- Model version handling
- State management
- Error handling during training
- Audit trail for training

**Lines Covered**: 237-413 (~175 lines)

### 3. Prediction Tests (25-35 tests)
- Basic prediction
- Single vs batch predictions
- Prediction validation
- Receipt generation
- Model version in predictions
- Error handling
- Performance optimization
- Audit trail

**Lines Covered**: 415-613 (~200 lines)

### 4. Verification Tests (10-15 tests)
- Receipt verification
- Integrity checking
- Error handling
- Audit logging

**Lines Covered**: 615-679 (~65 lines)

### 5. Model Info Tests (10-15 tests)
- Info retrieval
- Framework info inclusion
- Enhancement info
- Audit info

**Lines Covered**: 681-763 (~80 lines)

### 6. Serialization Tests (10-15 tests)
- Pickle serialization
- State preservation
- State restoration
- Protocol state

**Lines Covered**: 841-902 (~60 lines)

### 7. Utility & Internal Tests (10-15 tests)
- Audit entry creation
- Mock snapshot creation
- Mock receipt creation
- String representation

**Lines Covered**: 765-840 (~75 lines)

### 8. Integration & Edge Cases (10-15 tests)
- Full workflows
- Protocol fallback scenarios
- Enhancement failures
- Compliance failures
- Missing frameworks
- Error recovery

**Lines Covered**: Various (comprehensive coverage)

---

## Test File Structure

```python
tests/test_wrappers_modern_wrapper.py

├── TestModernWrapperInitialization (15-20 tests)
│   ├── test_init_valid_basic
│   ├── test_init_empty_model_name
│   ├── test_init_custom_policy
│   ├── test_init_framework_initialization
│   ├── test_init_protocol_availability
│   ├── test_init_enhancement_config_success
│   ├── test_init_enhancement_config_failure
│   └── ... (more)
│
├── TestModernWrapperTraining (25-35 tests)
│   ├── test_train_basic
│   ├── test_train_with_custom_params
│   ├── test_train_data_validation
│   ├── test_train_snapshot_creation
│   ├── test_train_version_handling
│   ├── test_train_state_update
│   ├── test_train_error_handling
│   └── ... (more)
│
├── TestModernWrapperPrediction (25-35 tests)
│   ├── test_predict_basic
│   ├── test_predict_single
│   ├── test_predict_batch
│   ├── test_predict_validation
│   ├── test_predict_receipt_generation
│   ├── test_predict_version_handling
│   ├── test_predict_error_handling
│   └── ... (more)
│
├── TestModernWrapperVerification (10-15 tests)
│   ├── test_verify_basic
│   ├── test_verify_integrity
│   ├── test_verify_error_handling
│   └── ... (more)
│
├── TestModernWrapperInfo (10-15 tests)
│   ├── test_get_model_info_basic
│   ├── test_get_model_info_with_framework
│   ├── test_get_model_info_complete
│   └── ... (more)
│
├── TestModernWrapperSerialization (10-15 tests)
│   ├── test_pickle_basic_state
│   ├── test_state_preservation
│   ├── test_state_restoration
│   └── ... (more)
│
├── TestModernWrapperUtilities (10-15 tests)
│   ├── test_audit_entry_creation
│   ├── test_mock_snapshot_creation
│   ├── test_mock_receipt_creation
│   ├── test_string_representation
│   └── ... (more)
│
└── TestModernWrapperIntegration (10-15 tests)
    ├── test_full_workflow
    ├── test_protocol_fallback
    ├── test_enhancement_failure_handling
    ├── test_compliance_failure_handling
    └── ... (more)
```

---

## Implementation Strategy

### Phase 2a: Foundation (Hours 1-2)
1. Create test file structure
2. Set up fixtures and mocks
3. Create base fixtures for:
   - Valid model
   - Valid policy
   - Valid framework
   - Mock objects

### Phase 2b: Initialization (Hours 2-3)
4. Test __init__ method thoroughly
5. Cover all initialization branches
6. Error case handling

### Phase 2c: Training (Hours 3-5)
7. Test train method
8. Cover training workflows
9. State management
10. Error handling

### Phase 2d: Prediction (Hours 5-7)
11. Test predict method
12. Cover prediction workflows
13. Receipt generation
14. Error handling

### Phase 2e: Verification & Info (Hours 7-7.5)
15. Test verify method
16. Test get_model_info
17. Small utility tests

### Phase 2f: Serialization & Integration (Hours 7.5-8)
18. Test serialization
19. Integration tests
20. Full workflow tests

---

## Key Testing Patterns

### 1. Fixture Setup
```python
@pytest.fixture
def mock_model():
    """Create mock ML model"""
    model = MagicMock()
    model.fit = MagicMock(return_value=None)
    model.predict = MagicMock(return_value=np.array([1.0, 2.0, 3.0]))
    return model

@pytest.fixture
def valid_policy():
    """Create valid wrapper policy"""
    from ciaf.wrappers.policy import get_default_wrapper_policy
    return get_default_wrapper_policy()

@pytest.fixture
def modern_wrapper(mock_model, valid_policy):
    """Create ModernCIAFModelWrapper instance"""
    return ModernCIAFModelWrapper(
        model=mock_model,
        model_name="test_model",
        policy=valid_policy
    )
```

### 2. Protocol Mocking
```python
@pytest.fixture
def mock_framework():
    """Mock CIAF framework"""
    framework = MagicMock()
    framework.assess_compliance = MagicMock(return_value={...})
    return framework

@pytest.fixture
def mock_protocol_implementations(valid_policy):
    """Mock protocol implementations in policy"""
    policy = valid_policy
    policy.model_adapter = MagicMock()
    policy.inference_handler = MagicMock()
    # ... other protocols
    return policy
```

### 3. Error Simulation
```python
def test_train_with_model_error(modern_wrapper):
    """Test training handles model errors"""
    modern_wrapper.model.fit.side_effect = ValueError("Model error")

    with pytest.raises(ValueError):
        modern_wrapper.train(...)
```

### 4. State Verification
```python
def test_predict_updates_state(modern_wrapper):
    """Test prediction updates wrapper state"""
    initial_receipt = modern_wrapper.last_receipt

    modern_wrapper.predict(...)

    assert modern_wrapper.last_receipt != initial_receipt
    assert modern_wrapper.audit_entries[-1]['operation'] == 'prediction'
```

---

## Expected Outcomes

**After Phase 2:**
- ✅ 100-150 new tests for modern_wrapper.py
- ✅ Coverage: 6% → 60%+
- ✅ All major workflows tested
- ✅ Error handling validated
- ✅ State management verified
- ✅ Integration patterns established

**Overall Coverage Progress:**
- Phase 1: 39% → 41% (+276 tests)
- Phase 2: 41% → 50%+ (+100-150 tests)
- Remaining: 50% → 80% (Phases 3-5)

---

## Next Steps After Implementation

1. Run coverage report: `python track_coverage.py --detailed`
2. Verify modern_wrapper coverage > 60%
3. Move to Phase 2b: universal_model_adapter.py
4. Continue with other Phase 2 targets

---

## Quick Reference

**File**: `/d/Github/CIAF_Models/CIAF_Model_Creation/ciaf/wrappers/modern_wrapper.py`
**Current Coverage**: 6% (23 lines out of 389)
**Template to Use**: MANAGER_TEST_TEMPLATE from TEST_TEMPLATES.py
**Test File**: tests/test_wrappers_modern_wrapper.py
**Estimated Tests**: 100-150
**Estimated Time**: 6-8 hours
