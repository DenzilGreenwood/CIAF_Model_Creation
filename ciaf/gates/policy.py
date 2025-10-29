"""
Policy management and configuration for compliance gates.

This module provides flexible policy-driven configuration of gate behavior,
thresholds, and enforcement actions without requiring model code changes.
"""

import json
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .interfaces import Stage, GateConfiguration, StagePolicy, PolicyValidationError


@dataclass
class GatePolicy:
    """
    Comprehensive policy configuration for compliance gates system.

    Defines gate behaviors, thresholds, enforcement actions, and
    regulatory requirements across all ML lifecycle stages.
    """

    # Policy metadata
    policy_id: str
    version: str
    created_at: datetime
    updated_at: datetime
    description: str = ""

    # Regulatory context
    applicable_regulations: List[str] = field(default_factory=list)
    risk_classification: str = "standard"  # low, standard, high, critical

    # Stage-specific configurations
    stage_policies: Dict[Stage, StagePolicy] = field(default_factory=dict)

    # Global policy settings
    global_enforcement_level: str = "strict"  # strict, permissive, advisory
    default_escalation_window_hours: int = 24
    require_cryptographic_receipts: bool = True

    # Reviewer and notification settings
    default_reviewers: List[str] = field(default_factory=list)
    notification_channels: Dict[str, Any] = field(default_factory=dict)

    # Audit and compliance settings
    audit_retention_days: int = 2555  # 7 years default
    compliance_reporting_frequency: str = "monthly"

    def get_stage_policy(self, stage: Stage) -> Optional[StagePolicy]:
        """Get policy configuration for a specific stage."""
        return self.stage_policies.get(stage)

    def add_stage_policy(self, stage_policy: StagePolicy) -> None:
        """Add or update policy for a specific stage."""
        self.stage_policies[stage_policy.stage] = stage_policy
        self.updated_at = datetime.now()

    def get_gate_configuration(self, stage: Stage, gate_name: str) -> Optional[GateConfiguration]:
        """Get configuration for a specific gate at a specific stage."""
        stage_policy = self.get_stage_policy(stage)
        if stage_policy:
            return stage_policy.gate_configurations.get(gate_name)
        return None

    def is_gate_enabled(self, stage: Stage, gate_name: str) -> bool:
        """Check if a gate is enabled for a specific stage."""
        stage_policy = self.get_stage_policy(stage)
        if stage_policy:
            return gate_name in stage_policy.enabled_gates
        return False

    def validate(self) -> List[str]:
        """
        Validate policy configuration for consistency and completeness.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate policy metadata
        if not self.policy_id:
            errors.append("Policy ID is required")

        if not self.version:
            errors.append("Policy version is required")

        # Validate risk classification
        valid_risk_levels = {"low", "standard", "high", "critical"}
        if self.risk_classification not in valid_risk_levels:
            errors.append(f"Invalid risk classification: {self.risk_classification}")

        # Validate enforcement level
        valid_enforcement = {"strict", "permissive", "advisory"}
        if self.global_enforcement_level not in valid_enforcement:
            errors.append(f"Invalid enforcement level: {self.global_enforcement_level}")

        # Validate stage policies
        for stage, stage_policy in self.stage_policies.items():
            stage_errors = self._validate_stage_policy(stage, stage_policy)
            errors.extend(stage_errors)

        return errors

    def _validate_stage_policy(self, stage: Stage, stage_policy: StagePolicy) -> List[str]:
        """Validate a specific stage policy."""
        errors = []

        # Check that enabled gates have configurations
        for gate_name in stage_policy.enabled_gates:
            if gate_name not in stage_policy.gate_configurations:
                errors.append(
                    f"Stage {stage.value}: Gate {gate_name} enabled but no configuration provided"
                )

        # Validate gate configurations
        for gate_name, gate_config in stage_policy.gate_configurations.items():
            config_errors = self._validate_gate_configuration(stage, gate_name, gate_config)
            errors.extend(config_errors)

        return errors

    def _validate_gate_configuration(
        self, stage: Stage, gate_name: str, gate_config: GateConfiguration
    ) -> List[str]:
        """Validate a specific gate configuration."""
        errors = []

        # Validate enforcement action
        valid_actions = {"block", "warn", "escalate"}
        if gate_config.enforcement_action not in valid_actions:
            errors.append(
                f"Stage {stage.value}, Gate {gate_name}: Invalid enforcement action {gate_config.enforcement_action}"
            )

        # Validate escalation window
        if gate_config.escalation_window_hours <= 0:
            errors.append(
                f"Stage {stage.value}, Gate {gate_name}: Escalation window must be positive"
            )

        # Validate thresholds (gate-specific validation would be more complex)
        for threshold_name, threshold_value in gate_config.thresholds.items():
            if not isinstance(threshold_value, (int, float)):
                errors.append(
                    f"Stage {stage.value}, Gate {gate_name}: Threshold {threshold_name} must be numeric"
                )

        return errors


class PolicyManager:
    """
    Manages policy lifecycle including loading, validation, versioning, and updates.

    Provides centralized policy management with support for multiple policy formats,
    version control, and runtime policy updates.
    """

    def __init__(self, policy_store_path: Optional[str] = None):
        self.policy_store_path = policy_store_path
        self.active_policies: Dict[str, GatePolicy] = {}
        self.policy_history: Dict[str, List[GatePolicy]] = {}

    def load_policy_from_file(self, file_path: Union[str, Path]) -> GatePolicy:
        """
        Load policy configuration from file (JSON or YAML).

        Args:
            file_path: Path to policy configuration file

        Returns:
            Loaded and validated policy

        Raises:
            PolicyValidationError: If policy is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise PolicyValidationError(f"Policy file not found: {file_path}")

        try:
            with open(file_path, "r") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    policy_data = yaml.safe_load(f)
                else:
                    policy_data = json.load(f)

            return self._create_policy_from_dict(policy_data)

        except Exception as e:
            raise PolicyValidationError(f"Failed to load policy from {file_path}: {e}")

    def load_policy_from_dict(self, policy_data: Dict[str, Any]) -> GatePolicy:
        """
        Load policy configuration from dictionary.

        Args:
            policy_data: Policy configuration dictionary

        Returns:
            Loaded and validated policy
        """
        return self._create_policy_from_dict(policy_data)

    def save_policy_to_file(self, policy: GatePolicy, file_path: Union[str, Path]) -> None:
        """
        Save policy configuration to file.

        Args:
            policy: Policy to save
            file_path: Output file path
        """
        file_path = Path(file_path)

        # Convert policy to dictionary
        policy_dict = self._policy_to_dict(policy)

        try:
            with open(file_path, "w") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(policy_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(policy_dict, f, indent=2, default=str)

        except Exception as e:
            raise PolicyValidationError(f"Failed to save policy to {file_path}: {e}")

    def register_policy(self, policy: GatePolicy) -> None:
        """
        Register a policy for active use.

        Args:
            policy: Policy to register

        Raises:
            PolicyValidationError: If policy is invalid
        """
        # Validate policy first
        errors = policy.validate()
        if errors:
            raise PolicyValidationError(f"Policy validation failed: {'; '.join(errors)}")

        # Store current policy as history if exists
        if policy.policy_id in self.active_policies:
            self._archive_policy(policy.policy_id)

        # Register new policy
        self.active_policies[policy.policy_id] = policy

        # Initialize history if needed
        if policy.policy_id not in self.policy_history:
            self.policy_history[policy.policy_id] = []

    def get_active_policy(self, policy_id: str) -> Optional[GatePolicy]:
        """Get currently active policy by ID."""
        return self.active_policies.get(policy_id)

    def get_policy_history(self, policy_id: str) -> List[GatePolicy]:
        """Get version history for a policy."""
        return self.policy_history.get(policy_id, [])

    def create_default_policy(
        self, policy_id: str = "default", risk_classification: str = "standard"
    ) -> GatePolicy:
        """
        Create a default policy configuration with common settings.

        Args:
            policy_id: Policy identifier
            risk_classification: Risk level (low/standard/high/critical)

        Returns:
            Default policy configuration
        """
        now = datetime.now()

        # Create default gate configurations for each stage
        default_stage_policies = {}

        for stage in Stage:
            enabled_gates = self._get_default_gates_for_stage(stage, risk_classification)
            gate_configurations = self._get_default_gate_configurations(
                enabled_gates, risk_classification
            )

            default_stage_policies[stage] = StagePolicy(
                stage=stage,
                enabled_gates=enabled_gates,
                gate_configurations=gate_configurations,
                enforcement_level=(
                    "strict" if risk_classification in ["high", "critical"] else "permissive"
                ),
                parallel_execution=True,
                fail_fast=risk_classification == "critical",
            )

        policy = GatePolicy(
            policy_id=policy_id,
            version="1.0.0",
            created_at=now,
            updated_at=now,
            description=f"Default policy for {risk_classification} risk classification",
            applicable_regulations=self._get_default_regulations(risk_classification),
            risk_classification=risk_classification,
            stage_policies=default_stage_policies,
            global_enforcement_level=(
                "strict" if risk_classification in ["high", "critical"] else "permissive"
            ),
            default_escalation_window_hours=24 if risk_classification != "critical" else 4,
            require_cryptographic_receipts=True,
        )

        return policy

    def update_policy_version(self, policy_id: str, updates: Dict[str, Any]) -> GatePolicy:
        """
        Create new version of existing policy with updates.

        Args:
            policy_id: ID of policy to update
            updates: Dictionary of updates to apply

        Returns:
            New policy version
        """
        current_policy = self.get_active_policy(policy_id)
        if not current_policy:
            raise PolicyValidationError(f"Policy {policy_id} not found")

        # Archive current version
        self._archive_policy(policy_id)

        # Create new version
        policy_dict = self._policy_to_dict(current_policy)

        # Apply updates recursively
        self._deep_update(policy_dict, updates)

        # Update version and timestamp
        old_version = policy_dict.get("version", "1.0.0")
        new_version = self._increment_version(old_version)
        policy_dict["version"] = new_version
        policy_dict["updated_at"] = datetime.now().isoformat()

        # Create new policy instance
        new_policy = self._create_policy_from_dict(policy_dict)

        # Register new version
        self.register_policy(new_policy)

        return new_policy

    def _create_policy_from_dict(self, policy_data: Dict[str, Any]) -> GatePolicy:
        """Create policy instance from dictionary data."""
        # Parse dates
        created_at = datetime.fromisoformat(
            policy_data.get("created_at", datetime.now().isoformat())
        )
        updated_at = datetime.fromisoformat(
            policy_data.get("updated_at", datetime.now().isoformat())
        )

        # Parse stage policies
        stage_policies = {}
        stages_data = policy_data.get("stage_policies", {})

        for stage_name, stage_data in stages_data.items():
            try:
                stage = Stage(stage_name)

                # Parse gate configurations
                gate_configs = {}
                for gate_name, gate_data in stage_data.get("gate_configurations", {}).items():
                    gate_configs[gate_name] = GateConfiguration(
                        gate_name=gate_name,
                        enabled=gate_data.get("enabled", True),
                        thresholds=gate_data.get("thresholds", {}),
                        enforcement_action=gate_data.get("enforcement_action", "block"),
                        required_reviewers=gate_data.get("required_reviewers", []),
                        escalation_window_hours=gate_data.get("escalation_window_hours", 24),
                        custom_parameters=gate_data.get("custom_parameters", {}),
                    )

                stage_policies[stage] = StagePolicy(
                    stage=stage,
                    enabled_gates=stage_data.get("enabled_gates", []),
                    gate_configurations=gate_configs,
                    enforcement_level=stage_data.get("enforcement_level", "strict"),
                    parallel_execution=stage_data.get("parallel_execution", True),
                    fail_fast=stage_data.get("fail_fast", False),
                    audit_requirements=stage_data.get("audit_requirements", {}),
                )

            except ValueError:
                continue  # Skip invalid stage names

        return GatePolicy(
            policy_id=policy_data["policy_id"],
            version=policy_data["version"],
            created_at=created_at,
            updated_at=updated_at,
            description=policy_data.get("description", ""),
            applicable_regulations=policy_data.get("applicable_regulations", []),
            risk_classification=policy_data.get("risk_classification", "standard"),
            stage_policies=stage_policies,
            global_enforcement_level=policy_data.get("global_enforcement_level", "strict"),
            default_escalation_window_hours=policy_data.get("default_escalation_window_hours", 24),
            require_cryptographic_receipts=policy_data.get("require_cryptographic_receipts", True),
            default_reviewers=policy_data.get("default_reviewers", []),
            notification_channels=policy_data.get("notification_channels", {}),
            audit_retention_days=policy_data.get("audit_retention_days", 2555),
            compliance_reporting_frequency=policy_data.get(
                "compliance_reporting_frequency", "monthly"
            ),
        )

    def _policy_to_dict(self, policy: GatePolicy) -> Dict[str, Any]:
        """Convert policy instance to dictionary."""
        result = asdict(policy)

        # Convert Stage enums to strings
        stage_policies = {}
        for stage, stage_policy in policy.stage_policies.items():
            stage_policies[stage.value] = asdict(stage_policy)
            stage_policies[stage.value]["stage"] = stage.value

        result["stage_policies"] = stage_policies

        # Convert datetime objects to ISO strings
        result["created_at"] = policy.created_at.isoformat()
        result["updated_at"] = policy.updated_at.isoformat()

        return result

    def _archive_policy(self, policy_id: str) -> None:
        """Move active policy to history."""
        if policy_id in self.active_policies:
            if policy_id not in self.policy_history:
                self.policy_history[policy_id] = []
            self.policy_history[policy_id].append(self.active_policies[policy_id])

    def _get_default_gates_for_stage(self, stage: Stage, risk_classification: str) -> List[str]:
        """Get default gate list for a stage based on risk classification."""
        base_gates = {
            Stage.DATASET: ["BiasGate", "ComplianceMappingGate"],
            Stage.TRAINING: ["BiasGate", "UncertaintyGate"],
            Stage.PRE_DEPLOYMENT: [
                "BiasGate",
                "ExplainabilityGate",
                "RobustnessGate",
                "ComplianceMappingGate",
            ],
            Stage.INFERENCE: ["UncertaintyGate", "HITLGate"],
        }

        gates = base_gates.get(stage, []).copy()

        # Add additional gates for higher risk classifications
        if risk_classification in ["high", "critical"]:
            if stage == Stage.DATASET:
                gates.append("UncertaintyGate")
            if stage == Stage.TRAINING:
                gates.extend(["ExplainabilityGate", "ComplianceMappingGate"])
            if stage == Stage.INFERENCE:
                gates.extend(["BiasGate", "ExplainabilityGate"])

        return gates

    def _get_default_gate_configurations(
        self, gate_names: List[str], risk_classification: str
    ) -> Dict[str, GateConfiguration]:
        """Get default configurations for gates."""
        configs = {}

        for gate_name in gate_names:
            enforcement_action = "block" if risk_classification in ["high", "critical"] else "warn"
            escalation_window = 4 if risk_classification == "critical" else 24

            # Gate-specific default thresholds
            thresholds = {}
            if gate_name == "BiasGate":
                thresholds = {
                    "demographic_parity_delta": (
                        0.05 if risk_classification in ["high", "critical"] else 0.1
                    )
                }
            elif gate_name == "UncertaintyGate":
                thresholds = {"max_epistemic_uncertainty": 0.1, "max_aleatoric_uncertainty": 0.2}
            elif gate_name == "RobustnessGate":
                thresholds = {
                    "min_adversarial_accuracy": (
                        0.8 if risk_classification in ["high", "critical"] else 0.7
                    )
                }

            configs[gate_name] = GateConfiguration(
                gate_name=gate_name,
                enabled=True,
                thresholds=thresholds,
                enforcement_action=enforcement_action,
                escalation_window_hours=escalation_window,
            )

        return configs

    def _get_default_regulations(self, risk_classification: str) -> List[str]:
        """Get default applicable regulations based on risk classification."""
        base_regs = ["GDPR", "NIST AI RMF"]

        if risk_classification in ["high", "critical"]:
            base_regs.extend(["EU AI Act", "ISO 27001"])

        return base_regs

    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _increment_version(self, version: str) -> str:
        """Increment semantic version string."""
        try:
            parts = version.split(".")
            if len(parts) >= 3:
                parts[2] = str(int(parts[2]) + 1)
            elif len(parts) == 2:
                parts.append("1")
            else:
                return "1.0.1"
            return ".".join(parts)
        except:
            return "1.0.1"
