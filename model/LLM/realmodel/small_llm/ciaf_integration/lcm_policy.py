"""
LCM Policy Module
Defines governance policies for pretraining data with CIAF/LCM integration
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import json
import hashlib


class DomainType(Enum):
    """Domain types for CIAF classification."""
    AUTONOMOUS_SYSTEMS = "autonomous_systems"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    GENERAL_PURPOSE = "general_purpose"
    RESEARCH = "research"


class CollectionMode(Enum):
    """Evidence collection modes."""
    COMPREHENSIVE = "comprehensive"
    SELECTIVE = "selective"
    MINIMAL = "minimal"


class EvidenceType(Enum):
    """Types of evidence collected."""
    RAW_TEXT = "raw_text"
    QUALITY_SCORE = "quality_score"
    SOURCE_DATASET = "source_dataset"
    CURATION_DECISION = "curation_decision"
    TRAINING_METRICS = "training_metrics"
    MODEL_WEIGHTS = "model_weights"
    INFERENCE_OUTPUT = "inference_output"


@dataclass
class LCMPolicy:
    """
    Lightweight Consensus Mechanism (LCM) Policy for data governance.
    
    Defines the rules and parameters for evidence collection, retention,
    and compliance verification in the CIAF framework.
    """
    policy_id: str
    policy_name: str
    domain_type: DomainType
    collection_mode: CollectionMode
    evidence_types: List[EvidenceType]
    retention_period_days: int
    regulatory_frameworks: List[str]
    
    # Additional metadata
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + 'Z')
    description: str = ""
    
    # Compression and batching settings
    receipt_batch_size: int = 1000
    enable_compression: bool = True
    merkle_tree_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            'policy_id': self.policy_id,
            'policy_name': self.policy_name,
            'domain_type': self.domain_type.value,
            'collection_mode': self.collection_mode.value,
            'evidence_types': [et.value for et in self.evidence_types],
            'retention_period_days': self.retention_period_days,
            'regulatory_frameworks': self.regulatory_frameworks,
            'version': self.version,
            'created_at': self.created_at,
            'description': self.description,
            'receipt_batch_size': self.receipt_batch_size,
            'enable_compression': self.enable_compression,
            'merkle_tree_enabled': self.merkle_tree_enabled
        }
    
    def compute_policy_hash(self) -> str:
        """
        Compute SHA-256 hash of the policy for anchoring.
        
        Returns:
            Hexadecimal hash string
        """
        policy_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(policy_str.encode()).hexdigest()
    
    def save(self, output_path: str):
        """
        Save policy to JSON file.
        
        Args:
            output_path: Path to output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, input_path: str) -> 'LCMPolicy':
        """
        Load policy from JSON file.
        
        Args:
            input_path: Path to input file
            
        Returns:
            LCMPolicy object
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert string enums back to enum types
        data['domain_type'] = DomainType(data['domain_type'])
        data['collection_mode'] = CollectionMode(data['collection_mode'])
        data['evidence_types'] = [EvidenceType(et) for et in data['evidence_types']]
        
        return cls(**data)


def create_pretraining_policy(
    policy_id: str = "pretrain_slimpajama_v1",
    output_path: str = None
) -> LCMPolicy:
    """
    Create the standard LCM policy for SlimPajama-6B pretraining.
    
    Args:
        policy_id: Custom policy ID (default: pretrain_slimpajama_v1)
        output_path: Optional path to save policy JSON
    
    Returns:
        LCMPolicy configured for pretraining data governance
    """
    policy = LCMPolicy(
        policy_id=policy_id,
        policy_name="SlimPajama-6B Pretraining Policy",
        domain_type=DomainType.RESEARCH,
        collection_mode=CollectionMode.SELECTIVE,
        evidence_types=[
            EvidenceType.RAW_TEXT,
            EvidenceType.QUALITY_SCORE,
            EvidenceType.SOURCE_DATASET,
            EvidenceType.CURATION_DECISION
        ],
        retention_period_days=365,
        regulatory_frameworks=[
            "EU AI Act",
            "NIST AI RMF",
            "ISO/IEC 42001"
        ],
        description="Governance policy for SlimPajama-6B dataset curation and pretraining. "
                   "Ensures full provenance tracking from raw data through model training.",
        receipt_batch_size=1000,
        enable_compression=True,
        merkle_tree_enabled=True
    )
    
    # Save if path provided
    if output_path:
        policy.save(output_path)
    
    return policy


if __name__ == "__main__":
    # Create and display the pretraining policy
    policy = create_pretraining_policy()
    
    print("LCM Policy for Pretraining")
    print("=" * 60)
    print(f"Policy ID: {policy.policy_id}")
    print(f"Policy Name: {policy.policy_name}")
    print(f"Domain: {policy.domain_type.value}")
    print(f"Collection Mode: {policy.collection_mode.value}")
    print(f"Evidence Types: {[et.value for et in policy.evidence_types]}")
    print(f"Retention Period: {policy.retention_period_days} days")
    print(f"Regulatory Frameworks: {policy.regulatory_frameworks}")
    print(f"\nPolicy Hash: {policy.compute_policy_hash()}")
    
    # Save to file
    output_path = "../config/lcm_policy_pretrain.json"
    policy.save(output_path)
    print(f"\nPolicy saved to: {output_path}")
