"""
LCM Inference Manager
Tracks inference requests with cryptographic receipts
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class InferenceReceipt:
    """
    Receipt for a single inference request.
    """
    receipt_id: str
    deployment_anchor_id: str
    timestamp: str
    
    # Input/Output hashes
    input_hash: str
    output_hash: str
    
    # Inference metadata
    prompt_length: int
    generation_length: int
    generation_params: Dict[str, Any] = field(default_factory=dict)
    
    # Optional confidence/quality scores
    confidence_score: Optional[float] = None
    
    # Compliance assertions
    compliance_assertions: List[str] = field(default_factory=list)
    
    # Commitment hash
    commitment_hash: str = ""
    
    def compute_commitment_hash(self) -> str:
        """Compute commitment hash for this receipt."""
        data = self.to_dict()
        data.pop('commitment_hash', None)
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DeploymentAnchor:
    """
    Anchor for a deployed model instance.
    """
    deployment_id: str
    model_version_anchor_id: str
    deployment_timestamp: str
    
    # Deployment configuration
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance and governance
    compliance_policy: List[str] = field(default_factory=list)
    use_restrictions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, output_path: str):
        """Save to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


class InferenceManager:
    """
    Manages inference requests with CIAF/LCM provenance tracking.
    """
    
    def __init__(
        self,
        deployment_anchor_id: str,
        receipts_dir: str = "./inference_receipts"
    ):
        """
        Initialize inference manager.
        
        Args:
            deployment_anchor_id: Deployment anchor ID
            receipts_dir: Directory to store receipts
        """
        self.deployment_anchor_id = deployment_anchor_id
        self.receipts_dir = Path(receipts_dir)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        
        self.receipts: List[InferenceReceipt] = []
        self.receipt_count = 0
    
    @staticmethod
    def compute_text_hash(text: str) -> str:
        """Compute SHA-256 hash of text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def create_inference_receipt(
        self,
        input_text: str,
        output_text: str,
        generation_params: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None,
        compliance_assertions: Optional[List[str]] = None
    ) -> InferenceReceipt:
        """
        Create an inference receipt.
        
        Args:
            input_text: Input prompt text
            output_text: Generated output text
            generation_params: Generation parameters (temperature, top_k, etc.)
            confidence_score: Optional confidence score
            compliance_assertions: Optional compliance assertions
            
        Returns:
            InferenceReceipt
        """
        # Compute hashes
        input_hash = self.compute_text_hash(input_text)
        output_hash = self.compute_text_hash(output_text)
        
        # Create receipt ID
        self.receipt_count += 1
        receipt_id = f"{self.deployment_anchor_id}_inference_{self.receipt_count}_{datetime.now(timezone.utc).timestamp()}"
        
        # Create receipt
        receipt = InferenceReceipt(
            receipt_id=receipt_id,
            deployment_anchor_id=self.deployment_anchor_id,
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            input_hash=input_hash,
            output_hash=output_hash,
            prompt_length=len(input_text),
            generation_length=len(output_text),
            generation_params=generation_params or {},
            confidence_score=confidence_score,
            compliance_assertions=compliance_assertions or [
                "non_clinical_use",
                "no_pii_input",
                "no_pii_output"
            ]
        )
        
        # Compute commitment hash
        receipt.commitment_hash = receipt.compute_commitment_hash()
        
        # Store receipt
        self.receipts.append(receipt)
        
        # Save to disk
        self._save_receipt(receipt)
        
        return receipt
    
    def _save_receipt(self, receipt: InferenceReceipt):
        """Save receipt to disk."""
        receipt_path = self.receipts_dir / f"{receipt.receipt_id}.json"
        with open(receipt_path, 'w', encoding='utf-8') as f:
            json.dump(receipt.to_dict(), f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get inference statistics."""
        total_receipts = len(self.receipts)
        
        if total_receipts == 0:
            return {
                'total_inferences': 0,
                'avg_prompt_length': 0,
                'avg_generation_length': 0
            }
        
        avg_prompt_length = sum(r.prompt_length for r in self.receipts) / total_receipts
        avg_generation_length = sum(r.generation_length for r in self.receipts) / total_receipts
        
        return {
            'total_inferences': total_receipts,
            'avg_prompt_length': avg_prompt_length,
            'avg_generation_length': avg_generation_length
        }


def create_deployment_anchor(
    model_version_anchor_id: str,
    deployment_config: Optional[Dict[str, Any]] = None,
    compliance_policy: Optional[List[str]] = None,
    use_restrictions: Optional[List[str]] = None,
    output_path: str = "./deployment_anchor.json"
) -> DeploymentAnchor:
    """
    Create a deployment anchor for a model.
    
    Args:
        model_version_anchor_id: Model version anchor ID
        deployment_config: Deployment configuration
        compliance_policy: Compliance policies
        use_restrictions: Use restrictions
        output_path: Path to save anchor
        
    Returns:
        DeploymentAnchor
    """
    timestamp = datetime.now(timezone.utc).timestamp()
    deployment_id = f"deployment_{model_version_anchor_id[:16]}_{timestamp}"
    
    anchor = DeploymentAnchor(
        deployment_id=deployment_id,
        model_version_anchor_id=model_version_anchor_id,
        deployment_timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
        deployment_config=deployment_config or {},
        compliance_policy=compliance_policy or [
            "EU AI Act Compliance",
            "Non-Clinical Use Only",
            "No Personal Data Processing"
        ],
        use_restrictions=use_restrictions or [
            "Research purposes only",
            "No production deployment without review",
            "Must track all inferences"
        ]
    )
    
    # Save anchor
    anchor.save(output_path)
    print(f"Created deployment anchor: {deployment_id}")
    
    return anchor


if __name__ == "__main__":
    # Example usage
    
    # Create deployment anchor
    deployment = create_deployment_anchor(
        model_version_anchor_id="model_gpt_ciaf_v1_12345_v10000",
        deployment_config={
            'device': 'cuda',
            'batch_size': 1,
            'max_length': 512
        },
        output_path="./test_deployment_anchor.json"
    )
    
    # Create inference manager
    manager = InferenceManager(
        deployment_anchor_id=deployment.deployment_id,
        receipts_dir="./test_inference_receipts"
    )
    
    # Simulate inference
    receipt = manager.create_inference_receipt(
        input_text="What is machine learning?",
        output_text="Machine learning is a field of artificial intelligence...",
        generation_params={'temperature': 0.8, 'top_k': 50},
        confidence_score=0.92
    )
    
    print(f"\nCreated inference receipt:")
    print(f"  Receipt ID: {receipt.receipt_id}")
    print(f"  Input hash: {receipt.input_hash[:16]}...")
    print(f"  Output hash: {receipt.output_hash[:16]}...")
    print(f"  Commitment: {receipt.commitment_hash[:16]}...")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"\nInference Statistics:")
    print(json.dumps(stats, indent=2))
