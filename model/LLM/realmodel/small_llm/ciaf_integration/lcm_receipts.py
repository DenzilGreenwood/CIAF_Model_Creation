"""
LCM Receipt and Capsule Manager
Handles creation, batching, and Merkle tree construction for LCM receipts
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import zlib


@dataclass
class LightweightReceipt:
    """
    Lightweight receipt for a single operation in the CIAF/LCM framework.
    """
    receipt_id: str
    operation_type: str  # DATA_CURATION, TRAIN_EPOCH, INFERENCE, etc.
    timestamp: str
    commitment_hash: str
    
    # Operation-specific data
    operation_data: Dict[str, Any] = field(default_factory=dict)
    
    # Policy reference
    policy_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert receipt to dictionary."""
        return asdict(self)
    
    def compute_receipt_hash(self) -> str:
        """Compute SHA-256 hash of the receipt."""
        receipt_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(receipt_str.encode()).hexdigest()


@dataclass
class MerkleNode:
    """Node in a Merkle tree."""
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class LCMCapsule:
    """
    LCM Capsule - batched collection of receipts with Merkle root.
    """
    capsule_id: str
    policy_id: str
    receipt_count: int
    merkle_root: str
    created_at: str
    
    # Compressed evidence
    compressed_receipts: bytes = field(default_factory=bytes)
    compression_ratio: float = 0.0
    
    # Metadata
    operation_types: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert capsule to dictionary (excluding binary data)."""
        return {
            'capsule_id': self.capsule_id,
            'policy_id': self.policy_id,
            'receipt_count': self.receipt_count,
            'merkle_root': self.merkle_root,
            'created_at': self.created_at,
            'compression_ratio': self.compression_ratio,
            'operation_types': self.operation_types,
            'compressed_size_bytes': len(self.compressed_receipts)
        }


class MerkleTreeBuilder:
    """Builds Merkle trees from receipt hashes."""
    
    @staticmethod
    def build_tree(hashes: List[str]) -> MerkleNode:
        """
        Build a Merkle tree from a list of hashes.
        
        Args:
            hashes: List of leaf hashes
            
        Returns:
            Root MerkleNode
        """
        if not hashes:
            return MerkleNode(hash=hashlib.sha256(b"").hexdigest())
        
        # Create leaf nodes
        nodes = [MerkleNode(hash=h) for h in hashes]
        
        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []
            
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                
                if i + 1 < len(nodes):
                    right = nodes[i + 1]
                else:
                    # Duplicate last node if odd number
                    right = nodes[i]
                
                # Combine hashes
                combined = left.hash + right.hash
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                parent = MerkleNode(hash=parent_hash, left=left, right=right)
                
                next_level.append(parent)
            
            nodes = next_level
        
        return nodes[0]
    
    @staticmethod
    def get_root_hash(hashes: List[str]) -> str:
        """
        Get the Merkle root hash.
        
        Args:
            hashes: List of leaf hashes
            
        Returns:
            Root hash as hex string
        """
        tree = MerkleTreeBuilder.build_tree(hashes)
        return tree.hash


class LCMReceiptManager:
    """
    Manages creation and batching of LCM receipts.
    """
    
    def __init__(self, policy_id: str, batch_size: int = 1000):
        """
        Initialize receipt manager.
        
        Args:
            policy_id: ID of governing LCM policy
            batch_size: Number of receipts per capsule
        """
        self.policy_id = policy_id
        self.batch_size = batch_size
        self.receipts: List[LightweightReceipt] = []
        self.capsules: List[LCMCapsule] = []
        
    def create_receipt(
        self,
        operation_type: str,
        commitment_hash: str,
        operation_data: Dict[str, Any]
    ) -> LightweightReceipt:
        """
        Create a new lightweight receipt.
        
        Args:
            operation_type: Type of operation (DATA_CURATION, etc.)
            commitment_hash: Hash of the operation commitment
            operation_data: Additional operation-specific data
            
        Returns:
            LightweightReceipt object
        """
        receipt_id = f"{operation_type}_{len(self.receipts)}_{datetime.now(timezone.utc).timestamp()}"
        
        receipt = LightweightReceipt(
            receipt_id=receipt_id,
            operation_type=operation_type,
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            commitment_hash=commitment_hash,
            operation_data=operation_data,
            policy_id=self.policy_id
        )
        
        self.receipts.append(receipt)
        
        # Auto-batch if we hit the batch size
        if len(self.receipts) >= self.batch_size:
            self.create_capsule()
        
        return receipt
    
    def create_capsule(self) -> Optional[LCMCapsule]:
        """
        Create an LCM capsule from accumulated receipts.
        
        Returns:
            LCMCapsule or None if no receipts available
        """
        if not self.receipts:
            return None
        
        # Compute receipt hashes for Merkle tree
        receipt_hashes = [r.compute_receipt_hash() for r in self.receipts]
        merkle_root = MerkleTreeBuilder.get_root_hash(receipt_hashes)
        
        # Compress receipts
        receipts_json = json.dumps([r.to_dict() for r in self.receipts])
        receipts_bytes = receipts_json.encode('utf-8')
        compressed = zlib.compress(receipts_bytes, level=9)
        
        compression_ratio = len(compressed) / len(receipts_bytes) if receipts_bytes else 0
        
        # Get operation types
        operation_types = list(set(r.operation_type for r in self.receipts))
        
        # Create capsule
        capsule_id = f"capsule_{len(self.capsules)}_{datetime.now(timezone.utc).timestamp()}"
        capsule = LCMCapsule(
            capsule_id=capsule_id,
            policy_id=self.policy_id,
            receipt_count=len(self.receipts),
            merkle_root=merkle_root,
            created_at=datetime.now(timezone.utc).isoformat() + 'Z',
            compressed_receipts=compressed,
            compression_ratio=compression_ratio,
            operation_types=operation_types
        )
        
        self.capsules.append(capsule)
        
        # Clear receipts
        receipt_count = len(self.receipts)
        self.receipts = []
        
        print(f"Created capsule {capsule_id} with {receipt_count} receipts")
        print(f"  Merkle root: {merkle_root}")
        print(f"  Compression: {compression_ratio:.2%}")
        
        return capsule
    
    def save_capsules(self, output_path: str):
        """
        Save all capsules to a JSON file.
        
        Args:
            output_path: Path to output file
        """
        # Flush any remaining receipts
        if self.receipts:
            self.create_capsule()
        
        capsules_data = [c.to_dict() for c in self.capsules]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'policy_id': self.policy_id,
                'total_capsules': len(self.capsules),
                'capsules': capsules_data
            }, f, indent=2)
        
        print(f"Saved {len(self.capsules)} capsules to {output_path}")


if __name__ == "__main__":
    # Example usage
    manager = LCMReceiptManager(policy_id="pretrain_slimpajama_v1", batch_size=5)
    
    # Create some test receipts
    for i in range(12):
        commitment_hash = hashlib.sha256(f"operation_{i}".encode()).hexdigest()
        
        receipt = manager.create_receipt(
            operation_type="DATA_CURATION",
            commitment_hash=commitment_hash,
            operation_data={
                'row_id': f'row_{i}',
                'decision': 'accepted',
                'quality_score': 0.75 + (i * 0.01)
            }
        )
        
        print(f"Created receipt {i+1}: {receipt.receipt_id}")
    
    # Save capsules
    manager.save_capsules("test_capsules.json")
    
    print(f"\nTotal capsules created: {len(manager.capsules)}")
