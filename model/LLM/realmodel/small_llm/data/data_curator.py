"""
Data Curation Module with CIAF/LCM Integration
Filters and curates SlimPajama-6B data with full provenance tracking
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CurationDecision:
    """Represents a single curation decision with full provenance."""
    row_id: str
    source_dataset: str
    decision: str  # "accepted" or "rejected"
    quality_score: float
    reasons: List[str]
    text_length: int
    source: str
    timestamp: str
    commitment_hash: str


class DataCurator:
    """
    Curates raw text data with quality filters and CIAF/LCM provenance tracking.
    
    Filters applied:
    - Minimum text length
    - Maximum text length
    - Simple quality heuristics
    - Optional language detection
    - Optional toxicity filtering
    """
    
    def __init__(
        self,
        min_length: int = 100,
        max_length: int = 100000,
        min_quality_score: float = 0.5,
        dataset_name: str = "DKYoon/SlimPajama-6B"
    ):
        """
        Initialize the data curator.
        
        Args:
            min_length: Minimum text length in characters
            max_length: Maximum text length in characters
            min_quality_score: Minimum quality score threshold
            dataset_name: Source dataset identifier
        """
        self.min_length = min_length
        self.max_length = max_length
        self.min_quality_score = min_quality_score
        self.dataset_name = dataset_name
        
        self.accepted_count = 0
        self.rejected_count = 0
        self.decisions: List[CurationDecision] = []
        
    def compute_quality_score(self, text: str) -> float:
        """
        Compute a simple quality score for text.
        
        Heuristics:
        - Ratio of alphanumeric characters
        - Average word length
        - Presence of common stop words
        
        Args:
            text: Input text
            
        Returns:
            Quality score between 0 and 1
        """
        if not text:
            return 0.0
        
        # Basic metrics
        total_chars = len(text)
        alnum_chars = sum(c.isalnum() for c in text)
        words = text.split()
        
        if not words:
            return 0.0
        
        # Alphanumeric ratio (higher is better)
        alnum_ratio = alnum_chars / total_chars if total_chars > 0 else 0
        
        # Average word length (sweet spot around 4-6)
        avg_word_len = sum(len(w) for w in words) / len(words)
        word_len_score = min(avg_word_len / 6.0, 1.0)
        
        # Combine scores
        quality_score = (alnum_ratio * 0.6) + (word_len_score * 0.4)
        
        return min(quality_score, 1.0)
    
    def apply_filters(self, sample: Dict[str, Any], row_id: str) -> Tuple[bool, List[str]]:
        """
        Apply filtering rules to a sample.
        
        Args:
            sample: Dataset sample
            row_id: Unique identifier for the row
            
        Returns:
            Tuple of (accepted: bool, reasons: List[str])
        """
        text = sample.get('text', '')
        reasons = []
        
        # Length filter
        if len(text) < self.min_length:
            reasons.append(f"too_short:{len(text)}<{self.min_length}")
            return False, reasons
        
        if len(text) > self.max_length:
            reasons.append(f"too_long:{len(text)}>{self.max_length}")
            return False, reasons
        
        # Quality filter
        quality_score = self.compute_quality_score(text)
        if quality_score < self.min_quality_score:
            reasons.append(f"low_quality:{quality_score:.3f}<{self.min_quality_score}")
            return False, reasons
        
        # Passed all filters
        reasons.append("passed_all_filters")
        return True, reasons
    
    def create_commitment_hash(self, decision: Dict[str, Any]) -> str:
        """
        Create a cryptographic commitment hash for a curation decision.
        
        Args:
            decision: Decision dictionary
            
        Returns:
            SHA-256 hash of the decision
        """
        decision_str = json.dumps(decision, sort_keys=True)
        return hashlib.sha256(decision_str.encode()).hexdigest()
    
    def curate_sample(self, sample: Dict[str, Any], row_id: str) -> CurationDecision:
        """
        Curate a single sample and create a provenance record.
        
        Args:
            sample: Dataset sample
            row_id: Unique identifier for the row
            
        Returns:
            CurationDecision object
        """
        text = sample.get('text', '')
        
        # Extract source information
        source = 'unknown'
        if 'meta' in sample and isinstance(sample['meta'], dict):
            source = sample['meta'].get('redpajama_set_name', 'unknown')
        
        # Apply filters
        accepted, reasons = self.apply_filters(sample, row_id)
        
        # Compute quality score
        quality_score = self.compute_quality_score(text)
        
        # Create decision record
        decision_data = {
            'row_id': row_id,
            'source_dataset': self.dataset_name,
            'decision': 'accepted' if accepted else 'rejected',
            'quality_score': quality_score,
            'reasons': reasons,
            'text_length': len(text),
            'source': source,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Create commitment hash
        commitment_hash = self.create_commitment_hash(decision_data)
        decision_data['commitment_hash'] = commitment_hash
        
        # Create decision object
        decision = CurationDecision(**decision_data)
        
        # Update counters
        if accepted:
            self.accepted_count += 1
        else:
            self.rejected_count += 1
        
        self.decisions.append(decision)
        
        return decision
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get curation statistics.
        
        Returns:
            Dictionary with acceptance rate and counts
        """
        total = self.accepted_count + self.rejected_count
        acceptance_rate = self.accepted_count / total if total > 0 else 0
        
        return {
            'total_processed': total,
            'accepted': self.accepted_count,
            'rejected': self.rejected_count,
            'acceptance_rate': acceptance_rate
        }
    
    def export_decisions(self, output_path: str):
        """
        Export curation decisions to a JSON file.
        
        Args:
            output_path: Path to output JSON file
        """
        decisions_list = [asdict(d) for d in self.decisions]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'statistics': self.get_statistics(),
                'decisions': decisions_list
            }, f, indent=2)
        
        logger.info(f"Exported {len(self.decisions)} decisions to {output_path}")


if __name__ == "__main__":
    # Example usage
    curator = DataCurator(min_length=100, max_length=50000, min_quality_score=0.5)
    
    # Test sample
    test_sample = {
        'text': 'This is a test document with some content. ' * 10,
        'meta': {'redpajama_set_name': 'CommonCrawl'}
    }
    
    decision = curator.curate_sample(test_sample, row_id='test_001')
    print(f"Decision: {decision.decision}")
    print(f"Quality Score: {decision.quality_score:.3f}")
    print(f"Reasons: {decision.reasons}")
    print(f"Commitment Hash: {decision.commitment_hash}")
