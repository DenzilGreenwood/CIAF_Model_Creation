"""
Bias and fairness compliance gate implementation.

This module implements comprehensive bias detection and fairness validation
for ML models with support for multiple fairness metrics and automated
corrective action recommendations.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from sklearn.metrics import confusion_matrix

from ..interfaces import (
    ComplianceGate,
    GateResult,
    GateStatus,
    OperationContext,
    Stage,
    PolicyDrivenGate,
)

logger = logging.getLogger(__name__)


class BiasGate:
    """
    Comprehensive bias and fairness compliance gate.

    Evaluates multiple fairness metrics including demographic parity,
    equalized odds, and predictive parity with configurable thresholds
    and automated corrective action recommendations.
    """

    name: str = "BiasGate"
    description: str = "Evaluates fairness and bias across protected attributes"
    version: str = "1.2.0"
    supported_stages: List[Stage] = [
        Stage.DATASET,
        Stage.TRAINING,
        Stage.PRE_DEPLOYMENT,
        Stage.INFERENCE,
    ]

    def __init__(self):
        self.thresholds = {
            "demographic_parity_delta": 0.1,
            "equalized_odds_delta": 0.1,
            "predictive_parity_delta": 0.1,
            "max_group_imbalance": 0.8,
            "min_representation_rate": 0.05,
        }
        self.protected_attributes = ["gender", "race", "age_group", "ethnicity"]
        self.enforcement_actions = {
            "demographic_parity": ["retrain", "rebalance", "threshold_adjust"],
            "equalized_odds": ["retrain", "postprocess"],
            "predictive_parity": ["calibration", "threshold_adjust"],
        }

    def evaluate(self, ctx: OperationContext) -> GateResult:
        """
        Evaluate bias and fairness metrics for the operation context.

        Args:
            ctx: Operation context with model and data artifacts

        Returns:
            Gate evaluation result with fairness metrics and recommendations
        """
        start_time = datetime.now()

        try:
            # Validate context has required data
            if not self.validate_context(ctx):
                return GateResult(
                    status=GateStatus.FAIL,
                    gate_name=self.name,
                    timestamp=start_time,
                    error_message="Invalid context: missing required bias evaluation data",
                )

            # Extract evaluation data based on stage
            evaluation_data = self._extract_evaluation_data(ctx)

            if not evaluation_data:
                return GateResult(
                    status=GateStatus.WARN,
                    gate_name=self.name,
                    timestamp=start_time,
                    metrics={"warning": "insufficient_data"},
                    recommendations=["Ensure sufficient data is available for bias evaluation"],
                )

            # Perform bias evaluation
            bias_metrics = self._evaluate_bias_metrics(evaluation_data, ctx)

            # Determine overall status
            status, violations = self._determine_status(bias_metrics)

            # Generate recommendations
            recommendations = self._generate_recommendations(violations, bias_metrics, ctx.stage)

            # Generate evidence references
            evidence_refs = self._generate_evidence_refs(evaluation_data, bias_metrics)

            return GateResult(
                status=status,
                gate_name=self.name,
                timestamp=start_time,
                metrics=bias_metrics,
                evidence_refs=evidence_refs,
                thresholds_applied=self.thresholds.copy(),
                recommendations=recommendations,
                required_actions=self._get_required_actions(violations),
                escalation_required=status in {GateStatus.FAIL, GateStatus.REVIEW},
                reviewer_required=status == GateStatus.REVIEW,
                regulatory_alignment={
                    "GDPR": "Article 22 - Automated Decision Making",
                    "EU AI Act": "Article 10 - Accuracy, Robustness and Cybersecurity",
                    "NIST AI RMF": "MEASURE 2.11 - Fairness",
                },
            )

        except Exception as e:
            logger.error(f"BiasGate evaluation failed: {e}")
            return GateResult(
                status=GateStatus.FAIL,
                gate_name=self.name,
                timestamp=start_time,
                error_message=f"Bias evaluation error: {str(e)}",
            )

    def validate_context(self, ctx: OperationContext) -> bool:
        """
        Validate that context contains required information for bias evaluation.

        Args:
            ctx: Operation context to validate

        Returns:
            True if context is valid for bias evaluation
        """
        if ctx.stage == Stage.DATASET:
            # Need dataset statistics and sensitive attributes
            return (
                "dataset_statistics" in ctx.custom_context
                and ctx.sensitive_attributes
                and "label_distribution" in ctx.data_statistics
            )

        elif ctx.stage in {Stage.TRAINING, Stage.PRE_DEPLOYMENT}:
            # Need model predictions and ground truth with sensitive attributes
            return (
                "predictions" in ctx.model_artifacts
                and "ground_truth" in ctx.model_artifacts
                and "sensitive_attributes_data" in ctx.custom_context
            )

        elif ctx.stage == Stage.INFERENCE:
            # Need recent predictions with sensitive attributes for monitoring
            return (
                "recent_predictions" in ctx.custom_context
                and "sensitive_attributes_data" in ctx.custom_context
            )

        return False

    def get_required_artifacts(self) -> List[str]:
        """Get list of required artifacts for bias evaluation."""
        return [
            "predictions",
            "ground_truth",
            "sensitive_attributes_data",
            "dataset_statistics",
            "label_distribution",
        ]

    def configure(self, policy_config: Dict[str, Any]) -> None:
        """Configure gate behavior based on policy settings."""
        if "thresholds" in policy_config:
            self.thresholds.update(policy_config["thresholds"])

        if "protected_attributes" in policy_config:
            self.protected_attributes = policy_config["protected_attributes"]

    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get JSON schema for policy configuration options."""
        return {
            "type": "object",
            "properties": {
                "thresholds": {
                    "type": "object",
                    "properties": {
                        "demographic_parity_delta": {"type": "number", "minimum": 0, "maximum": 1},
                        "equalized_odds_delta": {"type": "number", "minimum": 0, "maximum": 1},
                        "predictive_parity_delta": {"type": "number", "minimum": 0, "maximum": 1},
                        "max_group_imbalance": {"type": "number", "minimum": 0, "maximum": 1},
                        "min_representation_rate": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                },
                "protected_attributes": {"type": "array", "items": {"type": "string"}},
            },
        }

    def _extract_evaluation_data(self, ctx: OperationContext) -> Optional[Dict[str, Any]]:
        """Extract relevant data for bias evaluation based on stage."""
        evaluation_data = {}

        if ctx.stage == Stage.DATASET:
            # Extract dataset-level statistics
            evaluation_data = {
                "stage": "dataset",
                "statistics": ctx.data_statistics.copy(),
                "sensitive_attributes": ctx.sensitive_attributes.copy(),
                "dataset_info": ctx.custom_context.get("dataset_statistics", {}),
            }

        elif ctx.stage in {Stage.TRAINING, Stage.PRE_DEPLOYMENT}:
            # Extract model predictions and ground truth
            predictions = ctx.model_artifacts.get("predictions")
            ground_truth = ctx.model_artifacts.get("ground_truth")
            sensitive_data = ctx.custom_context.get("sensitive_attributes_data")

            if predictions is not None and ground_truth is not None and sensitive_data is not None:
                evaluation_data = {
                    "stage": ctx.stage.value,
                    "predictions": predictions,
                    "ground_truth": ground_truth,
                    "sensitive_attributes": sensitive_data,
                    "performance_metrics": ctx.performance_metrics.copy(),
                }

        elif ctx.stage == Stage.INFERENCE:
            # Extract recent inference data for monitoring
            recent_predictions = ctx.custom_context.get("recent_predictions")
            sensitive_data = ctx.custom_context.get("sensitive_attributes_data")

            if recent_predictions is not None and sensitive_data is not None:
                evaluation_data = {
                    "stage": "inference",
                    "predictions": recent_predictions,
                    "sensitive_attributes": sensitive_data,
                    "inference_metadata": ctx.custom_context.get("inference_metadata", {}),
                }

        return evaluation_data if evaluation_data else None

    def _evaluate_bias_metrics(
        self, evaluation_data: Dict[str, Any], ctx: OperationContext
    ) -> Dict[str, Any]:
        """Evaluate comprehensive bias and fairness metrics."""
        metrics = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "stage": evaluation_data["stage"],
        }

        if evaluation_data["stage"] == "dataset":
            metrics.update(self._evaluate_dataset_bias(evaluation_data))

        elif evaluation_data["stage"] in {"training", "pre_deployment"}:
            metrics.update(self._evaluate_model_bias(evaluation_data))

        elif evaluation_data["stage"] == "inference":
            metrics.update(self._evaluate_inference_bias(evaluation_data))

        return metrics

    def _evaluate_dataset_bias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate bias in dataset representation and labeling."""
        metrics = {}

        statistics = data.get("statistics", {})

        # Group representation analysis
        if "group_distributions" in statistics:
            group_dist = statistics["group_distributions"]

            # Calculate representation rates
            total_samples = sum(group_dist.values())
            representation_rates = {
                group: count / total_samples for group, count in group_dist.items()
            }

            metrics["group_representation_rates"] = representation_rates
            metrics["min_representation_rate"] = min(representation_rates.values())
            metrics["max_representation_rate"] = max(representation_rates.values())
            metrics["representation_imbalance"] = (
                metrics["max_representation_rate"] - metrics["min_representation_rate"]
            )

            # Check for underrepresented groups
            underrepresented = [
                group
                for group, rate in representation_rates.items()
                if rate < self.thresholds["min_representation_rate"]
            ]
            metrics["underrepresented_groups"] = underrepresented

        # Label distribution analysis by groups
        if "label_distributions_by_group" in statistics:
            label_dist = statistics["label_distributions_by_group"]

            # Calculate positive label rates by group
            positive_rates = {}
            for group, labels in label_dist.items():
                if isinstance(labels, dict) and "positive" in labels and "total" in labels:
                    positive_rates[group] = (
                        labels["positive"] / labels["total"] if labels["total"] > 0 else 0
                    )

            if positive_rates:
                metrics["positive_label_rates_by_group"] = positive_rates
                rates_values = list(positive_rates.values())
                metrics["label_rate_min"] = min(rates_values)
                metrics["label_rate_max"] = max(rates_values)
                metrics["demographic_parity_delta"] = max(rates_values) - min(rates_values)

        return metrics

    def _evaluate_model_bias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate bias in model predictions and performance."""
        metrics = {}

        predictions = data["predictions"]
        ground_truth = data["ground_truth"]
        sensitive_attrs = data["sensitive_attributes"]

        # Convert to numpy arrays if needed
        if isinstance(predictions, list):
            predictions = np.array(predictions)
        if isinstance(ground_truth, list):
            ground_truth = np.array(ground_truth)

        # Get unique groups from sensitive attributes
        unique_groups = set()
        for attr_name in self.protected_attributes:
            if attr_name in sensitive_attrs:
                unique_groups.update(sensitive_attrs[attr_name])

        group_metrics = {}

        for attr_name in self.protected_attributes:
            if attr_name not in sensitive_attrs:
                continue

            attr_values = sensitive_attrs[attr_name]
            unique_values = list(set(attr_values))

            if len(unique_values) < 2:
                continue

            # Calculate metrics by group
            group_stats = {}
            for group_value in unique_values:
                group_mask = np.array(attr_values) == group_value

                if np.sum(group_mask) == 0:
                    continue

                group_preds = predictions[group_mask]
                group_truth = ground_truth[group_mask]

                # Basic metrics
                group_stats[group_value] = {
                    "count": int(np.sum(group_mask)),
                    "positive_prediction_rate": (
                        float(np.mean(group_preds > 0.5)) if len(group_preds) > 0 else 0
                    ),
                    "true_positive_rate": self._calculate_tpr(group_truth, group_preds),
                    "false_positive_rate": self._calculate_fpr(group_truth, group_preds),
                    "precision": self._calculate_precision(group_truth, group_preds),
                    "accuracy": self._calculate_accuracy(group_truth, group_preds),
                }

            group_metrics[attr_name] = group_stats

            # Calculate fairness metrics
            if len(group_stats) >= 2:
                # Demographic parity
                pred_rates = [stats["positive_prediction_rate"] for stats in group_stats.values()]
                metrics[f"{attr_name}_demographic_parity_delta"] = max(pred_rates) - min(pred_rates)

                # Equalized odds (TPR difference)
                tpr_values = [
                    stats["true_positive_rate"]
                    for stats in group_stats.values()
                    if stats["true_positive_rate"] is not None
                ]
                if len(tpr_values) >= 2:
                    metrics[f"{attr_name}_equalized_odds_tpr_delta"] = max(tpr_values) - min(
                        tpr_values
                    )

                # False positive rate parity
                fpr_values = [
                    stats["false_positive_rate"]
                    for stats in group_stats.values()
                    if stats["false_positive_rate"] is not None
                ]
                if len(fpr_values) >= 2:
                    metrics[f"{attr_name}_equalized_odds_fpr_delta"] = max(fpr_values) - min(
                        fpr_values
                    )

                # Predictive parity (precision difference)
                precision_values = [
                    stats["precision"]
                    for stats in group_stats.values()
                    if stats["precision"] is not None
                ]
                if len(precision_values) >= 2:
                    metrics[f"{attr_name}_predictive_parity_delta"] = max(precision_values) - min(
                        precision_values
                    )

        metrics["group_performance_metrics"] = group_metrics

        # Overall fairness summary
        all_dp_deltas = [v for k, v in metrics.items() if k.endswith("_demographic_parity_delta")]
        if all_dp_deltas:
            metrics["max_demographic_parity_delta"] = max(all_dp_deltas)

        all_eo_deltas = [v for k, v in metrics.items() if k.endswith("_equalized_odds_tpr_delta")]
        if all_eo_deltas:
            metrics["max_equalized_odds_delta"] = max(all_eo_deltas)

        return metrics

    def _evaluate_inference_bias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate bias drift in inference predictions."""
        metrics = {"inference_bias_monitoring": True}

        predictions = data["predictions"]
        sensitive_attrs = data["sensitive_attributes"]

        # Monitor prediction rate differences over time
        for attr_name in self.protected_attributes:
            if attr_name not in sensitive_attrs:
                continue

            attr_values = sensitive_attrs[attr_name]
            unique_values = list(set(attr_values))

            if len(unique_values) < 2:
                continue

            # Calculate current prediction rates by group
            group_pred_rates = {}
            for group_value in unique_values:
                group_mask = np.array(attr_values) == group_value
                if np.sum(group_mask) > 0:
                    group_preds = np.array(predictions)[group_mask]
                    group_pred_rates[group_value] = float(np.mean(group_preds > 0.5))

            if len(group_pred_rates) >= 2:
                pred_rates = list(group_pred_rates.values())
                metrics[f"{attr_name}_current_demographic_parity_delta"] = max(pred_rates) - min(
                    pred_rates
                )

        return metrics

    def _calculate_tpr(self, y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
        """Calculate True Positive Rate."""
        try:
            y_pred_binary = (y_pred > 0.5).astype(int)
            cm = confusion_matrix(y_true, y_pred_binary, labels=[0, 1])
            if cm.shape == (2, 2) and (cm[1, 0] + cm[1, 1]) > 0:
                return float(cm[1, 1] / (cm[1, 0] + cm[1, 1]))
        except:
            pass
        return None

    def _calculate_fpr(self, y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
        """Calculate False Positive Rate."""
        try:
            y_pred_binary = (y_pred > 0.5).astype(int)
            cm = confusion_matrix(y_true, y_pred_binary, labels=[0, 1])
            if cm.shape == (2, 2) and (cm[0, 0] + cm[0, 1]) > 0:
                return float(cm[0, 1] / (cm[0, 0] + cm[0, 1]))
        except:
            pass
        return None

    def _calculate_precision(self, y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
        """Calculate Precision."""
        try:
            y_pred_binary = (y_pred > 0.5).astype(int)
            cm = confusion_matrix(y_true, y_pred_binary, labels=[0, 1])
            if cm.shape == (2, 2) and (cm[0, 1] + cm[1, 1]) > 0:
                return float(cm[1, 1] / (cm[0, 1] + cm[1, 1]))
        except:
            pass
        return None

    def _calculate_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
        """Calculate Accuracy."""
        try:
            y_pred_binary = (y_pred > 0.5).astype(int)
            return float(np.mean(y_true == y_pred_binary))
        except:
            pass
        return None

    def _determine_status(self, metrics: Dict[str, Any]) -> Tuple[GateStatus, List[str]]:
        """Determine gate status based on bias metrics."""
        violations = []

        # Check demographic parity violations
        max_dp_delta = metrics.get("max_demographic_parity_delta")
        if max_dp_delta is not None and max_dp_delta > self.thresholds["demographic_parity_delta"]:
            violations.append(
                f"demographic_parity_violation: delta={max_dp_delta:.3f} exceeds threshold {self.thresholds['demographic_parity_delta']}"
            )

        # Check equalized odds violations
        max_eo_delta = metrics.get("max_equalized_odds_delta")
        if max_eo_delta is not None and max_eo_delta > self.thresholds["equalized_odds_delta"]:
            violations.append(
                f"equalized_odds_violation: delta={max_eo_delta:.3f} exceeds threshold {self.thresholds['equalized_odds_delta']}"
            )

        # Check representation violations
        min_repr_rate = metrics.get("min_representation_rate")
        if min_repr_rate is not None and min_repr_rate < self.thresholds["min_representation_rate"]:
            violations.append(
                f"representation_violation: min_rate={min_repr_rate:.3f} below threshold {self.thresholds['min_representation_rate']}"
            )

        # Check for underrepresented groups
        underrepresented = metrics.get("underrepresented_groups", [])
        if underrepresented:
            violations.append(f"underrepresented_groups: {underrepresented}")

        # Determine overall status
        if not violations:
            return GateStatus.PASS, violations

        # Check severity of violations
        critical_violations = [
            v
            for v in violations
            if "demographic_parity_violation" in v or "equalized_odds_violation" in v
        ]

        if critical_violations:
            # High-impact fairness violations require review
            if any(
                float(v.split("delta=")[1].split(" ")[0]) > 0.2
                for v in critical_violations
                if "delta=" in v
            ):
                return GateStatus.REVIEW, violations
            else:
                return GateStatus.FAIL, violations
        else:
            # Minor violations get warning
            return GateStatus.WARN, violations

    def _generate_recommendations(
        self, violations: List[str], metrics: Dict[str, Any], stage: Stage
    ) -> List[str]:
        """Generate actionable recommendations based on violations."""
        recommendations = []

        if not violations:
            recommendations.append(
                "No bias violations detected. Continue monitoring fairness metrics."
            )
            return recommendations

        # Stage-specific recommendations
        if stage == Stage.DATASET:
            if any("representation_violation" in v for v in violations):
                recommendations.append("Collect additional data for underrepresented groups")
                recommendations.append("Consider data augmentation techniques for minority groups")

            if any("underrepresented_groups" in v for v in violations):
                recommendations.append(
                    "Review data collection strategy to ensure inclusive sampling"
                )

        elif stage in {Stage.TRAINING, Stage.PRE_DEPLOYMENT}:
            if any("demographic_parity_violation" in v for v in violations):
                recommendations.append(
                    "Apply fairness-aware training techniques (e.g., adversarial debiasing)"
                )
                recommendations.append(
                    "Adjust decision thresholds per group to achieve demographic parity"
                )
                recommendations.append("Consider re-sampling or re-weighting training data")

            if any("equalized_odds_violation" in v for v in violations):
                recommendations.append(
                    "Apply post-processing calibration to equalize TPR/FPR across groups"
                )
                recommendations.append("Retrain model with fairness constraints")

        elif stage == Stage.INFERENCE:
            recommendations.append(
                "Implement bias monitoring and alerting for production inference"
            )
            recommendations.append("Consider model retraining if bias drift persists")
            recommendations.append("Review recent data distribution changes")

        return recommendations

    def _get_required_actions(self, violations: List[str]) -> List[str]:
        """Get required actions based on violations."""
        actions = []

        if any("demographic_parity_violation" in v for v in violations):
            actions.append("Document fairness violation in compliance log")
            actions.append("Implement bias mitigation before deployment")

        if any("representation_violation" in v for v in violations):
            actions.append("Address data representation issues")

        if any("equalized_odds_violation" in v for v in violations):
            actions.append("Apply fairness post-processing techniques")

        return actions

    def _generate_evidence_refs(
        self, evaluation_data: Dict[str, Any], metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate evidence references for audit trail."""
        evidence_refs = []

        # Add data source references
        if evaluation_data.get("stage") == "dataset":
            evidence_refs.append("dataset_bias_analysis")
            evidence_refs.append("group_representation_analysis")

        elif evaluation_data.get("stage") in {"training", "pre_deployment"}:
            evidence_refs.append("model_fairness_evaluation")
            evidence_refs.append("group_performance_metrics")

        elif evaluation_data.get("stage") == "inference":
            evidence_refs.append("inference_bias_monitoring")

        # Add metric-specific references
        if "max_demographic_parity_delta" in metrics:
            evidence_refs.append("demographic_parity_calculation")

        if "max_equalized_odds_delta" in metrics:
            evidence_refs.append("equalized_odds_calculation")

        return evidence_refs
