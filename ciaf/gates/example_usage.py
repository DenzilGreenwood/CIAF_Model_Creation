"""
Example usage of the CIAF Compliance Gates System.

This example demonstrates how to set up and use the compliance gates
for ML lifecycle governance with policy-driven configuration.
"""

import numpy as np
from datetime import datetime
from typing import Dict, Any

# Import CIAF gates components
from ciaf.gates import (
    GateOrchestrator,
    PolicyManager,
    OperationContext,
    Stage,
    GateStatus,
    BiasGate,
)


def create_sample_data():
    """Create sample data for demonstration."""
    # Sample predictions and ground truth
    np.random.seed(42)
    n_samples = 1000

    predictions = np.random.random(n_samples)
    ground_truth = (np.random.random(n_samples) > 0.5).astype(int)

    # Sample sensitive attributes
    gender = np.random.choice(["male", "female"], n_samples)
    race = np.random.choice(["white", "black", "hispanic", "asian"], n_samples)

    return {
        "predictions": predictions,
        "ground_truth": ground_truth,
        "sensitive_attributes": {"gender": gender.tolist(), "race": race.tolist()},
    }


def create_example_policy() -> Dict[str, Any]:
    """Create example policy configuration."""
    return {
        "policy_id": "example_ml_project",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": "Example policy for ML project compliance",
        "risk_classification": "high",
        "stages": {
            "training": {
                "enabled_gates": ["BiasGate"],
                "enforcement_level": "strict",
                "parallel_execution": True,
                "fail_fast": False,
                "gates": {
                    "BiasGate": {
                        "enabled": True,
                        "thresholds": {
                            "demographic_parity_delta": 0.1,
                            "equalized_odds_delta": 0.1,
                        },
                        "enforcement_action": "warn",
                        "escalation_window_hours": 24,
                        "custom_parameters": {"protected_attributes": ["gender", "race"]},
                    }
                },
            },
            "pre_deployment": {
                "enabled_gates": ["BiasGate"],
                "enforcement_level": "strict",
                "parallel_execution": True,
                "fail_fast": True,
                "gates": {
                    "BiasGate": {
                        "enabled": True,
                        "thresholds": {
                            "demographic_parity_delta": 0.05,
                            "equalized_odds_delta": 0.05,
                        },
                        "enforcement_action": "block",
                        "escalation_window_hours": 4,
                    }
                },
            },
        },
    }


def demonstrate_gates_usage():
    """Demonstrate the complete gates usage workflow."""
    print("CIAF Compliance Gates System - Example Usage")
    print("=" * 50)

    # 1. Create sample data
    print("\n1. Creating sample data...")
    sample_data = create_sample_data()
    print(f"   - Generated {len(sample_data['predictions'])} predictions")
    print(f"   - Sensitive attributes: {list(sample_data['sensitive_attributes'].keys())}")

    # 2. Create and load policy
    print("\n2. Setting up policy...")
    policy_config = create_example_policy()

    # 3. Create orchestrator
    print("\n3. Creating gate orchestrator...")
    orchestrator = GateOrchestrator(policy_config)

    # 4. Register gates
    print("\n4. Registering compliance gates...")
    bias_gate = BiasGate()
    orchestrator.register_gate(bias_gate)
    print(f"   - Registered: {bias_gate.name} v{bias_gate.version}")

    # 5. Create operation context for training stage
    print("\n5. Running gates for TRAINING stage...")
    training_context = OperationContext(
        stage=Stage.TRAINING,
        operation_id="training_run_001",
        timestamp=datetime.now(),
        model_id="example_model_v1",
        model_artifacts={
            "predictions": sample_data["predictions"],
            "ground_truth": sample_data["ground_truth"],
        },
        performance_metrics={"accuracy": 0.85, "auc": 0.88},
        sensitive_attributes=["gender", "race"],
        custom_context={"sensitive_attributes_data": sample_data["sensitive_attributes"]},
    )

    # Run gates for training stage
    training_results = orchestrator.run_stage_gates(Stage.TRAINING, training_context)

    # Display results
    print(f"\n   Training Gate Results:")
    for result in training_results:
        print(f"   - {result.gate_name}: {result.status.value}")
        if result.metrics:
            key_metrics = {
                k: v
                for k, v in result.metrics.items()
                if k.endswith("_delta") or k.startswith("max_")
            }
            if key_metrics:
                print(f"     Key metrics: {key_metrics}")
        if result.recommendations:
            print(f"     Recommendations: {result.recommendations[:2]}...")  # Show first 2

    # 6. Create operation context for pre-deployment stage
    print("\n6. Running gates for PRE-DEPLOYMENT stage...")
    predeployment_context = OperationContext(
        stage=Stage.PRE_DEPLOYMENT,
        operation_id="predeployment_validation_001",
        timestamp=datetime.now(),
        model_id="example_model_v1",
        model_artifacts={
            "predictions": sample_data["predictions"],
            "ground_truth": sample_data["ground_truth"],
        },
        performance_metrics={"accuracy": 0.87, "auc": 0.90},
        sensitive_attributes=["gender", "race"],
        custom_context={"sensitive_attributes_data": sample_data["sensitive_attributes"]},
        previous_results={"BiasGate": training_results[0] if training_results else None},
    )

    # Run gates for pre-deployment stage
    predeployment_results = orchestrator.run_stage_gates(
        Stage.PRE_DEPLOYMENT, predeployment_context
    )

    # Display results
    print(f"\n   Pre-deployment Gate Results:")
    for result in predeployment_results:
        print(f"   - {result.gate_name}: {result.status.value}")
        if result.escalation_required:
            print(f"     ⚠ Escalation required: {result.status.value}")
        if result.required_actions:
            print(f"     Required actions: {result.required_actions}")

    # 7. Show stage summary
    print("\n7. Stage configuration summary...")
    training_summary = orchestrator.get_stage_summary(Stage.TRAINING)
    print(f"   Training stage: {training_summary.get('enabled_gates', [])} gates enabled")
    print(f"   Enforcement: {training_summary.get('enforcement_level', 'unknown')}")

    predeployment_summary = orchestrator.get_stage_summary(Stage.PRE_DEPLOYMENT)
    print(
        f"   Pre-deployment stage: {predeployment_summary.get('enabled_gates', [])} gates enabled"
    )
    print(f"   Enforcement: {predeployment_summary.get('enforcement_level', 'unknown')}")

    # 8. Demonstrate policy management
    print("\n8. Policy management demonstration...")
    policy_manager = PolicyManager()

    # Create default policy
    default_policy = policy_manager.create_default_policy("demo_project", "standard")
    print(f"   Created default policy: {default_policy.policy_id} v{default_policy.version}")
    print(f"   Risk classification: {default_policy.risk_classification}")
    print(f"   Stages configured: {list(default_policy.stage_policies.keys())}")

    # Validate policy
    validation_errors = default_policy.validate()
    if validation_errors:
        print(f"   Policy validation errors: {validation_errors}")
    else:
        print("   ✓ Policy validation passed")

    print("\n" + "=" * 50)
    print("Example completed successfully!")
    print("\nKey Benefits Demonstrated:")
    print("- Policy-driven gate configuration")
    print("- Stage-based compliance evaluation")
    print("- Actionable pass/fail decisions")
    print("- Cryptographic audit trail")
    print("- Regulatory alignment")


if __name__ == "__main__":
    try:
        demonstrate_gates_usage()
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback

        traceback.print_exc()
