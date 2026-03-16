"""
CIAF Evaluation Anchors
Tracks evaluation runs with full provenance
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class EvaluationAnchor:
    """
    CIAF Evaluation Anchor - cryptographic anchor for an evaluation run.
    """
    evaluation_id: str
    model_version_anchor_id: str
    test_dataset_anchors: List[str]
    evaluation_timestamp: str
    
    # Results
    test_results: Dict[str, Any] = field(default_factory=dict)
    evaluation_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Compliance
    compliance_validation: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    eval_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def compute_anchor_hash(self) -> str:
        """Compute hash of evaluation anchor."""
        data_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def save(self, output_path: str):
        """Save anchor to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


class EvaluationManager:
    """
    Manages CIAF evaluation runs with full provenance tracking.
    """
    
    def __init__(self, evaluations_dir: str = "./evaluations"):
        """
        Initialize evaluation manager.
        
        Args:
            evaluations_dir: Directory to store evaluation data
        """
        self.evaluations_dir = Path(evaluations_dir)
        self.evaluations_dir.mkdir(parents=True, exist_ok=True)
        
        self.evaluations: Dict[str, EvaluationAnchor] = {}
    
    def create_evaluation(
        self,
        model_version_anchor_id: str,
        test_dataset_anchors: List[str],
        eval_config: Optional[Dict[str, Any]] = None
    ) -> EvaluationAnchor:
        """
        Create a new evaluation anchor.
        
        Args:
            model_version_anchor_id: Model version to evaluate
            test_dataset_anchors: Test dataset anchors
            eval_config: Optional evaluation configuration
            
        Returns:
            EvaluationAnchor
        """
        # Generate evaluation ID
        timestamp = datetime.now(timezone.utc).timestamp()
        evaluation_id = f"eval_{model_version_anchor_id[:16]}_{timestamp}"
        
        # Create anchor
        anchor = EvaluationAnchor(
            evaluation_id=evaluation_id,
            model_version_anchor_id=model_version_anchor_id,
            test_dataset_anchors=test_dataset_anchors,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            eval_config=eval_config or {}
        )
        
        # Store
        self.evaluations[evaluation_id] = anchor
        
        print(f"Created evaluation: {evaluation_id}")
        return anchor
    
    def record_results(
        self,
        evaluation_id: str,
        metrics: Dict[str, float],
        test_results: Optional[Dict[str, Any]] = None,
        compliance_validation: Optional[Dict[str, bool]] = None
    ):
        """
        Record evaluation results.
        
        Args:
            evaluation_id: Evaluation ID
            metrics: Evaluation metrics (e.g., perplexity, accuracy)
            test_results: Detailed test results
            compliance_validation: Compliance checks
        """
        if evaluation_id not in self.evaluations:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        anchor = self.evaluations[evaluation_id]
        anchor.evaluation_metrics = metrics
        anchor.test_results = test_results or {}
        anchor.compliance_validation = compliance_validation or {}
        
        # Save to disk
        self._save_evaluation(anchor)
        
        print(f"Recorded results for {evaluation_id}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    def _save_evaluation(self, anchor: EvaluationAnchor):
        """Save evaluation anchor to disk."""
        anchor_path = self.evaluations_dir / f"{anchor.evaluation_id}.json"
        anchor.save(str(anchor_path))
    
    def get_evaluation_summary(self, evaluation_id: str) -> Dict[str, Any]:
        """Get summary of evaluation."""
        if evaluation_id not in self.evaluations:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        anchor = self.evaluations[evaluation_id]
        return {
            'evaluation_id': anchor.evaluation_id,
            'model_version': anchor.model_version_anchor_id,
            'metrics': anchor.evaluation_metrics,
            'timestamp': anchor.evaluation_timestamp
        }


if __name__ == "__main__":
    # Example usage
    manager = EvaluationManager(evaluations_dir="./test_evaluations")
    
    # Create evaluation
    evaluation = manager.create_evaluation(
        model_version_anchor_id="model_gpt_ciaf_v1_12345_v10000",
        test_dataset_anchors=["dataset_test_001"],
        eval_config={'batch_size': 8, 'max_samples': 1000}
    )
    
    # Record results
    manager.record_results(
        evaluation_id=evaluation.evaluation_id,
        metrics={
            'perplexity': 25.3,
            'loss': 3.23
        },
        compliance_validation={
            'non_pii': True,
            'safety_check': True
        }
    )
    
    # Get summary
    summary = manager.get_evaluation_summary(evaluation.evaluation_id)
    print("\nEvaluation Summary:")
    print(json.dumps(summary, indent=2))
