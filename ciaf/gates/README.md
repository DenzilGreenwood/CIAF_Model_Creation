# CIAF Compliance Gates System

A comprehensive, policy-driven framework for ML lifecycle governance with normative pass/fail semantics, cryptographic attestation, and regulatory alignment.

## Overview

The CIAF Compliance Gates System transforms compliance from a reactive documentation exercise into proactive, actionable governance throughout the ML lifecycle. It provides:

- **Normative Decisions**: Clear PASS/WARN/FAIL/REVIEW outcomes at each stage
- **Policy-Driven Configuration**: Adjust thresholds and enforcement without model code changes
- **Cryptographic Audit Trails**: Tamper-evident receipts for regulatory compliance
- **Regulatory Alignment**: Built-in mapping to GDPR, EU AI Act, NIST AI RMF
- **Enterprise Ready**: Parallel execution, error handling, HITL escalation

## Architecture

### Core Components

```
ciaf/gates/
├── interfaces.py       # Core protocols and data structures
├── orchestrator.py     # Gate execution and policy enforcement
├── policy.py          # Policy management and configuration
├── receipts.py        # Cryptographic receipt generation
└── implementations/   # Specialized gate catalog
    ├── bias_gate.py         # Bias/fairness evaluation ✅
    ├── explainability_gate.py # SHAP/LIME validation 🔄
    ├── uncertainty_gate.py    # Confidence bounds 🔄
    ├── robustness_gate.py     # Adversarial testing 🔄
    ├── hitl_gate.py          # Human oversight 🔄
    └── compliance_mapping_gate.py # Regulatory artifacts 🔄
```

### Design Pattern

1. **Gate Interface (Policy-Driven)**
   ```python
   class ComplianceGate(Protocol):
       name: str
       def evaluate(self, ctx: OperationContext) -> GateResult: ...
   ```

2. **Orchestrator per Lifecycle Stage**
   ```python
   class GateOrchestrator:
       def run_stage_gates(self, stage: Stage, ctx: OperationContext) -> List[GateResult]:
           # Policy-driven gate execution with enforcement
   ```

3. **Cryptographic Receipts**
   ```python
   # Each gate emits LightweightReceipt → Merkle batching → signed chain
   receipt = generator.create_gate_receipt(gate_result, stage, policy_version)
   ```

## Quick Start

### 1. Basic Usage

```python
from ciaf.gates import GateOrchestrator, PolicyManager, OperationContext, Stage
from ciaf.gates.implementations import BiasGate

# Create policy
policy_manager = PolicyManager()
policy = policy_manager.create_default_policy("my_project", "high")

# Setup orchestrator
orchestrator = GateOrchestrator(policy.to_dict())
orchestrator.register_gate(BiasGate())

# Create context
context = OperationContext(
    stage=Stage.TRAINING,
    operation_id="training_001",
    timestamp=datetime.now(),
    model_artifacts={"predictions": predictions, "ground_truth": labels},
    custom_context={"sensitive_attributes_data": sensitive_attrs}
)

# Run gates
results = orchestrator.run_stage_gates(Stage.TRAINING, context)

# Check results
for result in results:
    print(f"{result.gate_name}: {result.status.value}")
    if result.status != GateStatus.PASS:
        print(f"Actions required: {result.required_actions}")
```

### 2. Policy Configuration

```python
# Create custom policy
policy_config = {
    "policy_id": "ml_project_v1",
    "version": "1.0.0",
    "risk_classification": "high",
    "stages": {
        "training": {
            "enabled_gates": ["BiasGate"],
            "gates": {
                "BiasGate": {
                    "thresholds": {
                        "demographic_parity_delta": 0.05
                    },
                    "enforcement_action": "block"
                }
            }
        }
    }
}
```

## Gate Catalog

### BiasGate ✅ (Implemented)

Comprehensive bias and fairness evaluation across protected attributes.

**Metrics:**
- Demographic parity (prediction rate equality)
- Equalized odds (TPR/FPR equality)  
- Predictive parity (precision equality)
- Group representation analysis

**Stages:** All stages (DATASET → TRAINING → PRE_DEPLOYMENT → INFERENCE)

**Configuration:**
```python
"BiasGate": {
    "thresholds": {
        "demographic_parity_delta": 0.1,
        "equalized_odds_delta": 0.1,
        "min_representation_rate": 0.05
    },
    "enforcement_action": "block",  # block, warn, escalate
    "custom_parameters": {
        "protected_attributes": ["gender", "race", "age_group"]
    }
}
```

**Actions:**
- **Dataset Stage**: Data collection recommendations, augmentation strategies
- **Training Stage**: Fairness-aware training, threshold adjustment, resampling
- **Pre-deployment**: Post-processing calibration, fairness constraints
- **Inference**: Bias monitoring, drift detection, model retraining triggers

### ExplainabilityGate 🔄 (Planned)

LIME/SHAP explanation coverage and stability validation.

**Metrics:**
- Feature importance stability across seeds
- Explanation coverage (% of decisions explained)
- Counterfactual validity
- Regulatory explanation requirements

**Actions:** Feature audit requirements, explanation documentation

### UncertaintyGate 🔄 (Planned)

MC-dropout/ensemble confidence bound validation.

**Metrics:**
- Epistemic uncertainty quantification
- Aleatoric uncertainty bounds
- Prediction confidence calibration
- Out-of-distribution detection

**Actions:** Auto-escalate to HITL if confidence too low, uncertainty documentation

### RobustnessGate 🔄 (Planned)

Adversarial robustness and out-of-distribution testing.

**Metrics:**
- Adversarial accuracy under attack
- OOD detection performance
- Input perturbation sensitivity
- Robustness certification bounds

**Actions:** Fail deployment if robustness below threshold, adversarial training

### HITLGate 🔄 (Planned)

Human-in-the-loop escalation and review workflows.

**Metrics:**
- Risk scoring for human review
- Reviewer assignment logic
- Escalation window compliance
- Review decision tracking

**Actions:** Route to appropriate reviewers, enforce review deadlines

### ComplianceMappingGate 🔄 (Planned)

Regulatory framework artifact validation.

**Metrics:**
- EU AI Act documentation completeness
- NIST AI RMF function coverage
- GDPR Article 22 compliance
- Industry-specific requirements

**Actions:** Block if required artifacts missing, generate compliance reports

## ML Lifecycle Integration

### Light Model Hooks

Add minimal instrumentation to training/inference:

```python
# Training loop example
for epoch in range(num_epochs):
    # ... training code ...
    
    # Surface metrics for gates
    epoch_metrics = {
        "confusion_matrix_by_group": compute_group_confusion_matrices(),
        "feature_importance": model.get_feature_importance(),
        "prediction_confidence": prediction_confidence_scores
    }
    
    # CIAF gates evaluation (external to model)
    if epoch % gate_check_frequency == 0:
        gate_context = create_gate_context(epoch_metrics, sensitive_attrs)
        gate_results = orchestrator.run_stage_gates(Stage.TRAINING, gate_context)
        
        # Handle gate results
        for result in gate_results:
            if result.status == GateStatus.FAIL:
                handle_compliance_failure(result)
```

### CIAF Evaluation Layer

All compliance logic lives in CIAF, keeping models portable:

```python
# In CIAF gates system
class BiasGate:
    def evaluate(self, ctx: OperationContext) -> GateResult:
        # Extract model metrics from context
        predictions = ctx.model_artifacts["predictions"]
        sensitive_attrs = ctx.custom_context["sensitive_attributes_data"]
        
        # Perform bias evaluation
        fairness_metrics = self._calculate_fairness_metrics(predictions, sensitive_attrs)
        
        # Make pass/fail decision
        status = self._determine_compliance_status(fairness_metrics)
        
        return GateResult(status=status, metrics=fairness_metrics, ...)
```

## Policy Management

### Risk-Based Defaults

```python
# Automatically configure gates based on risk classification
policy = policy_manager.create_default_policy("project", "critical")

# Critical risk projects get:
# - Stricter thresholds (demographic_parity_delta: 0.05 vs 0.1)
# - More gates enabled (all stages get bias + explainability + robustness)
# - Faster escalation windows (4 hours vs 24 hours)
# - Block enforcement (vs warn for lower risk)
```

### Policy Evolution

```python
# Update policy without code changes
updated_policy = policy_manager.update_policy_version("project_v1", {
    "stages": {
        "pre_deployment": {
            "gates": {
                "BiasGate": {
                    "thresholds": {
                        "demographic_parity_delta": 0.03  # Stricter threshold
                    }
                }
            }
        }
    }
})
```

## Cryptographic Audit Trails

### Receipt Generation

```python
# Each gate evaluation generates tamper-evident receipt
receipt = receipt_generator.create_gate_receipt(
    gate_result=bias_result,
    stage=Stage.TRAINING,
    policy_version="1.2.0"
)

# Receipt contains:
# - Content hash of evaluation data
# - Cryptographic signature
# - Merkle tree integration for batch verification
# - Regulatory evidence references
```

### Audit Trail Export

```python
# Generate regulatory compliance report
audit_trail = compliance_audit.export_audit_report(
    start_date=project_start,
    end_date=deployment_date
)

# Report includes:
# - Complete timeline of gate evaluations
# - Cryptographic proof chain
# - Policy versions used
# - Human review decisions
# - Regulatory alignment documentation
```

## Regulatory Alignment

### Built-in Compliance Mapping

| Gate | GDPR | EU AI Act | NIST AI RMF | ISO 27001 |
|------|------|-----------|-------------|-----------|
| BiasGate | Article 22 | Article 10 | MEASURE 2.11 | A.8.2.3 |
| ExplainabilityGate | Article 22 | Article 13 | GOVERN 2.1 | A.8.1.1 |
| UncertaintyGate | Article 25 | Article 9 | MEASURE 2.8 | A.8.2.1 |
| RobustnessGate | Article 25 | Article 15 | MEASURE 2.13 | A.8.2.2 |

### Automated Evidence Generation

```python
# Gates automatically generate regulatory evidence
gate_result = bias_gate.evaluate(context)

# Result includes regulatory alignment
assert gate_result.regulatory_alignment == {
    "GDPR": "Article 22 - Automated Decision Making",
    "EU AI Act": "Article 10 - Accuracy, Robustness and Cybersecurity", 
    "NIST AI RMF": "MEASURE 2.11 - Fairness"
}
```

## Development Status

### ✅ Completed
- Core interfaces and protocols
- Orchestration framework with policy enforcement
- Policy management system with versioning
- Cryptographic receipt generation and audit trails
- BiasGate implementation with comprehensive fairness metrics
- Integration architecture with existing CIAF modules
- Example usage and documentation

### 🔄 In Progress
- Additional specialized gate implementations
- Integration testing with CIAF components
- Performance optimization for large-scale deployments

### 📋 Planned
- Advanced HITL workflow integration
- Visualization dashboards for gate results
- Additional regulatory framework mappings
- Cloud deployment and scaling optimizations

## Contributing

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for detailed architecture and implementation notes.

### Adding New Gates

1. Implement the `ComplianceGate` protocol
2. Add configuration schema for policy-driven behavior
3. Include regulatory alignment mapping
4. Add comprehensive tests and documentation
5. Update gate catalog in this README

### Policy Extensions

1. Define new configuration parameters in gate configuration schema
2. Update policy validation logic
3. Add default values for different risk classifications
4. Document regulatory implications

## License

This implementation is part of the CIAF framework and follows the same licensing terms.