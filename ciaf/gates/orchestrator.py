"""
Gate orchestration and policy enforcement for ML lifecycle governance.

This module provides the core orchestration logic for running compliance gates
across ML lifecycle stages with policy-driven configuration and enforcement.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
import json
import hashlib
import uuid

from .interfaces import (
    ComplianceGate,
    GateResult,
    GateStatus,
    OperationContext,
    Stage,
    StagePolicy,
    GateConfiguration,
    GateEvaluationError,
    PolicyValidationError,
)


logger = logging.getLogger(__name__)


class PolicyEnforcer:
    """
    Enforces gate evaluation results according to policy configuration.

    Handles blocking operations, escalating to human reviewers, and
    generating appropriate notifications and audit records.
    """

    def __init__(self, policy_config: Dict[str, Any]):
        self.policy_config = policy_config
        self.escalation_handlers: Dict[str, Callable] = {}
        self.notification_handlers: Dict[str, Callable] = {}

    def enforce_result(
        self, stage: Stage, gate_result: GateResult, gate_config: GateConfiguration
    ) -> bool:
        """
        Enforce gate result according to policy configuration.

        Args:
            stage: ML lifecycle stage
            gate_result: Gate evaluation result
            gate_config: Gate-specific policy configuration

        Returns:
            True if operation should proceed, False if blocked
        """
        if gate_result.status == GateStatus.PASS:
            return True

        if gate_result.status == GateStatus.WARN:
            self._handle_warning(stage, gate_result, gate_config)
            return True

        if gate_result.status == GateStatus.FAIL:
            return self._handle_failure(stage, gate_result, gate_config)

        if gate_result.status == GateStatus.REVIEW:
            return self._handle_review_required(stage, gate_result, gate_config)

        return False

    def _handle_warning(self, stage: Stage, result: GateResult, config: GateConfiguration) -> None:
        """Handle warning-level gate results."""
        logger.warning(
            f"Gate {result.gate_name} warning at {stage.value}: {result.recommendations}"
        )

        # Send notifications if configured
        self._send_notifications("warning", stage, result, config)

    def _handle_failure(self, stage: Stage, result: GateResult, config: GateConfiguration) -> bool:
        """Handle failure-level gate results."""
        logger.error(f"Gate {result.gate_name} failed at {stage.value}: {result.required_actions}")

        enforcement_action = config.enforcement_action

        if enforcement_action == "block":
            self._send_notifications("failure_blocked", stage, result, config)
            return False

        elif enforcement_action == "warn":
            self._send_notifications("failure_warning", stage, result, config)
            return True

        elif enforcement_action == "escalate":
            return self._escalate_failure(stage, result, config)

        return False

    def _handle_review_required(
        self, stage: Stage, result: GateResult, config: GateConfiguration
    ) -> bool:
        """Handle review-required gate results."""
        logger.info(f"Gate {result.gate_name} requires human review at {stage.value}")

        # Check if immediate reviewers are available
        if self._can_get_immediate_review(config):
            return self._request_immediate_review(stage, result, config)

        # Otherwise, escalate for async review
        return self._escalate_for_review(stage, result, config)

    def _escalate_failure(
        self, stage: Stage, result: GateResult, config: GateConfiguration
    ) -> bool:
        """Escalate failure to appropriate handlers."""
        escalation_type = f"{stage.value}_failure"

        if escalation_type in self.escalation_handlers:
            return self.escalation_handlers[escalation_type](result, config)

        # Default: block operation
        return False

    def _escalate_for_review(
        self, stage: Stage, result: GateResult, config: GateConfiguration
    ) -> bool:
        """Escalate for human review with deadline tracking."""
        review_deadline = datetime.now() + timedelta(hours=config.escalation_window_hours)

        # Create review ticket/request
        review_id = self._create_review_request(stage, result, config, review_deadline)

        # For critical operations, may block pending review
        if result.review_priority == "critical":
            return False

        # For non-critical, may proceed with monitoring
        return True

    def _send_notifications(
        self, notification_type: str, stage: Stage, result: GateResult, config: GateConfiguration
    ) -> None:
        """Send appropriate notifications for gate results."""
        if notification_type in self.notification_handlers:
            self.notification_handlers[notification_type](stage, result, config)

    def _can_get_immediate_review(self, config: GateConfiguration) -> bool:
        """Check if immediate human review is available."""
        # Implementation would check reviewer availability
        return len(config.required_reviewers) > 0

    def _request_immediate_review(
        self, stage: Stage, result: GateResult, config: GateConfiguration
    ) -> bool:
        """Request immediate human review (synchronous)."""
        # Implementation would present review interface
        # For now, return False to be conservative
        return False

    def _create_review_request(
        self, stage: Stage, result: GateResult, config: GateConfiguration, deadline: datetime
    ) -> str:
        """Create asynchronous review request."""
        import uuid

        review_id = str(uuid.uuid4())

        # Implementation would create review ticket in tracking system
        logger.info(f"Created review request {review_id} for {result.gate_name} at {stage.value}")

        return review_id


class GateOrchestrator:
    """
    Orchestrates compliance gate execution across ML lifecycle stages.

    Provides policy-driven gate execution with cryptographic receipt generation,
    parallel processing, and comprehensive error handling.
    """

    def __init__(self, policy_config: Dict[str, Any]):
        self.policy_config = policy_config
        self.gates: Dict[str, ComplianceGate] = {}
        self.stage_policies: Dict[Stage, StagePolicy] = {}
        self.receipt_generator = None  # Will be initialized when needed
        self.policy_enforcer = PolicyEnforcer(policy_config)
        self.batch_hashes: List[str] = []  # Simple list for Merkle leaves

        self._load_policies()

    def register_gate(self, gate: ComplianceGate) -> None:
        """Register a compliance gate for use in orchestration."""
        self.gates[gate.name] = gate
        logger.info(f"Registered gate: {gate.name}")

    def run_stage_gates(self, stage: Stage, ctx: OperationContext) -> List[GateResult]:
        """
        Run all enabled gates for a specific ML lifecycle stage.

        Args:
            stage: ML lifecycle stage
            ctx: Operation context with model artifacts and metadata

        Returns:
            List of gate evaluation results

        Raises:
            PolicyValidationError: If stage policy is invalid
            GateEvaluationError: If gate execution fails critically
        """
        if stage not in self.stage_policies:
            raise PolicyValidationError(f"No policy configured for stage: {stage.value}")

        stage_policy = self.stage_policies[stage]
        results: List[GateResult] = []

        # Get enabled gates for this stage
        enabled_gates = self._get_enabled_gates(stage, stage_policy)

        if not enabled_gates:
            logger.info(f"No gates enabled for stage: {stage.value}")
            return results

        logger.info(f"Running {len(enabled_gates)} gates for stage: {stage.value}")

        # Execute gates (parallel or sequential based on policy)
        if stage_policy.parallel_execution:
            results = self._run_gates_parallel(enabled_gates, ctx, stage_policy)
        else:
            results = self._run_gates_sequential(enabled_gates, ctx, stage_policy)

        # Generate receipts and enforce policy
        self._process_gate_results(stage, results, stage_policy)

        return results

    def _get_enabled_gates(
        self, stage: Stage, stage_policy: StagePolicy
    ) -> List[Tuple[ComplianceGate, GateConfiguration]]:
        """Get list of enabled gates with their configurations for a stage."""
        enabled_gates = []

        for gate_name in stage_policy.enabled_gates:
            if gate_name not in self.gates:
                logger.warning(f"Gate {gate_name} not registered, skipping")
                continue

            gate = self.gates[gate_name]

            # Check if gate supports this stage
            if stage not in gate.supported_stages:
                logger.warning(f"Gate {gate_name} does not support stage {stage.value}, skipping")
                continue

            # Get gate configuration
            gate_config = stage_policy.gate_configurations.get(
                gate_name, GateConfiguration(gate_name=gate_name)
            )

            if gate_config.enabled:
                enabled_gates.append((gate, gate_config))

        return enabled_gates

    def _run_gates_parallel(
        self,
        enabled_gates: List[Tuple[ComplianceGate, GateConfiguration]],
        ctx: OperationContext,
        stage_policy: StagePolicy,
    ) -> List[GateResult]:
        """Run gates in parallel for better performance."""
        results = []

        with ThreadPoolExecutor(max_workers=min(len(enabled_gates), 4)) as executor:
            # Submit all gate evaluations
            future_to_gate = {
                executor.submit(self._evaluate_gate_safe, gate, gate_config, ctx): (
                    gate,
                    gate_config,
                )
                for gate, gate_config in enabled_gates
            }

            # Collect results as they complete
            for future in as_completed(future_to_gate):
                gate, gate_config = future_to_gate[future]

                try:
                    result = future.result()
                    results.append(result)

                    # Handle fail-fast policy
                    if (
                        stage_policy.fail_fast
                        and result.status in {GateStatus.FAIL, GateStatus.REVIEW}
                        and not self.policy_enforcer.enforce_result(ctx.stage, result, gate_config)
                    ):
                        logger.error(f"Fail-fast triggered by gate {gate.name}")
                        # Cancel remaining futures
                        for remaining_future in future_to_gate:
                            remaining_future.cancel()
                        break

                except Exception as e:
                    logger.error(f"Gate {gate.name} execution failed: {e}")
                    # Create error result
                    error_result = GateResult(
                        status=GateStatus.FAIL,
                        gate_name=gate.name,
                        timestamp=datetime.now(),
                        error_message=str(e),
                    )
                    results.append(error_result)

        return results

    def _run_gates_sequential(
        self,
        enabled_gates: List[Tuple[ComplianceGate, GateConfiguration]],
        ctx: OperationContext,
        stage_policy: StagePolicy,
    ) -> List[GateResult]:
        """Run gates sequentially with dependency handling."""
        results = []

        for gate, gate_config in enabled_gates:
            try:
                result = self._evaluate_gate_safe(gate, gate_config, ctx)
                results.append(result)

                # Update context with this result for dependent gates
                ctx.previous_results[gate.name] = result

                # Handle fail-fast policy
                if (
                    stage_policy.fail_fast
                    and result.status in {GateStatus.FAIL, GateStatus.REVIEW}
                    and not self.policy_enforcer.enforce_result(ctx.stage, result, gate_config)
                ):
                    logger.error(f"Fail-fast triggered by gate {gate.name}")
                    break

            except Exception as e:
                logger.error(f"Gate {gate.name} execution failed: {e}")
                error_result = GateResult(
                    status=GateStatus.FAIL,
                    gate_name=gate.name,
                    timestamp=datetime.now(),
                    error_message=str(e),
                )
                results.append(error_result)

                if stage_policy.fail_fast:
                    break

        return results

    def _evaluate_gate_safe(
        self, gate: ComplianceGate, gate_config: GateConfiguration, ctx: OperationContext
    ) -> GateResult:
        """Safely evaluate a gate with error handling and timing."""
        start_time = datetime.now()

        try:
            # Validate context
            if not gate.validate_context(ctx):
                return GateResult(
                    status=GateStatus.FAIL,
                    gate_name=gate.name,
                    timestamp=start_time,
                    error_message="Invalid operation context for gate",
                )

            # Configure gate if it supports policy-driven configuration
            if hasattr(gate, "configure"):
                gate.configure(gate_config.custom_parameters)

            # Evaluate gate
            result = gate.evaluate(ctx)

            # Add execution timing
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return GateResult(
                status=GateStatus.FAIL,
                gate_name=gate.name,
                timestamp=start_time,
                error_message=f"Gate evaluation error: {str(e)}",
                execution_time_ms=execution_time,
            )

    def _process_gate_results(
        self, stage: Stage, results: List[GateResult], stage_policy: StagePolicy
    ) -> None:
        """Process gate results by generating receipts and enforcing policy."""
        for result in results:
            # Generate cryptographic receipt
            self._emit_receipt(stage, result)

            # Enforce policy
            gate_config = stage_policy.gate_configurations.get(
                result.gate_name, GateConfiguration(gate_name=result.gate_name)
            )

            should_proceed = self.policy_enforcer.enforce_result(stage, result, gate_config)

            if not should_proceed:
                logger.warning(f"Operation blocked by gate {result.gate_name}")

    def _emit_receipt(self, stage: Stage, result: GateResult) -> None:
        """Generate and store cryptographic receipt for gate result."""
        try:
            # Create receipt data
            receipt_data = {
                "stage": stage.value,
                "gate_name": result.gate_name,
                "status": result.status.value,
                "timestamp": result.timestamp.isoformat(),
                "metrics": result.metrics,
                "evidence_refs": result.evidence_refs,
                "policy_version": result.policy_version,
            }

            # Generate simple hash for receipt
            receipt_json = json.dumps(receipt_data, sort_keys=True)
            receipt_hash = hashlib.sha256(receipt_json.encode()).hexdigest()

            # Add to batch for Merkle tree
            self.batch_hashes.append(receipt_hash)

            # Update result with cryptographic evidence
            result.evidence_hash = receipt_hash
            result.signature = hashlib.sha256(f"{receipt_hash}:signature_key".encode()).hexdigest()

            logger.debug(f"Generated receipt for gate {result.gate_name}: {receipt_hash}")

        except Exception as e:
            logger.error(f"Failed to generate receipt for gate {result.gate_name}: {e}")

    def _load_policies(self) -> None:
        """Load stage policies from configuration."""
        try:
            stages_config = self.policy_config.get("stages", {})

            for stage_name, stage_config in stages_config.items():
                try:
                    stage = Stage(stage_name)

                    # Create gate configurations
                    gate_configs = {}
                    for gate_name, gate_config_data in stage_config.get("gates", {}).items():
                        gate_configs[gate_name] = GateConfiguration(
                            gate_name=gate_name,
                            enabled=gate_config_data.get("enabled", True),
                            thresholds=gate_config_data.get("thresholds", {}),
                            enforcement_action=gate_config_data.get("enforcement_action", "block"),
                            required_reviewers=gate_config_data.get("required_reviewers", []),
                            escalation_window_hours=gate_config_data.get(
                                "escalation_window_hours", 24
                            ),
                            custom_parameters=gate_config_data.get("custom_parameters", {}),
                        )

                    # Create stage policy
                    self.stage_policies[stage] = StagePolicy(
                        stage=stage,
                        enabled_gates=stage_config.get("enabled_gates", []),
                        gate_configurations=gate_configs,
                        enforcement_level=stage_config.get("enforcement_level", "strict"),
                        parallel_execution=stage_config.get("parallel_execution", True),
                        fail_fast=stage_config.get("fail_fast", False),
                        audit_requirements=stage_config.get("audit_requirements", {}),
                    )

                    logger.info(f"Loaded policy for stage {stage.value}")

                except ValueError as e:
                    logger.error(f"Invalid stage name {stage_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to load stage policies: {e}")
            raise PolicyValidationError(f"Policy loading failed: {e}")

    def get_stage_summary(self, stage: Stage) -> Dict[str, any]:
        """Get summary of configured gates and policies for a stage."""
        if stage not in self.stage_policies:
            return {"error": f"No policy configured for stage {stage.value}"}

        stage_policy = self.stage_policies[stage]

        return {
            "stage": stage.value,
            "enabled_gates": stage_policy.enabled_gates,
            "enforcement_level": stage_policy.enforcement_level,
            "parallel_execution": stage_policy.parallel_execution,
            "fail_fast": stage_policy.fail_fast,
            "registered_gates": list(self.gates.keys()),
            "gate_configurations": {
                name: {
                    "enabled": config.enabled,
                    "enforcement_action": config.enforcement_action,
                    "thresholds": config.thresholds,
                }
                for name, config in stage_policy.gate_configurations.items()
            },
        }
