"""
CIAF Model Anchors
Tracks model versions, configurations, and weights with cryptographic provenance
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


@dataclass
class ModelAnchor:
    """
    CIAF Model Anchor - cryptographic anchor for a model configuration.
    """
    anchor_id: str
    model_type: str
    config_hash: str
    initial_weights_hash: str
    created_at: str
    
    # Configuration details
    config_data: Dict[str, Any] = field(default_factory=dict)
    
    # Tokenizer reference
    tokenizer_anchor_id: Optional[str] = None
    
    # Metadata
    description: str = ""
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, output_path: str):
        """Save anchor to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class ModelVersionAnchor:
    """
    CIAF Model Version Anchor - tracks a specific trained checkpoint.
    """
    version_anchor_id: str
    base_model_anchor_id: str
    training_session_id: str
    checkpoint_step: int
    tokens_seen: int
    weights_hash: str
    created_at: str
    
    # Evaluation metrics (if available)
    eval_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Training info
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    
    # Checkpoint metadata
    checkpoint_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, output_path: str):
        """Save version anchor to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class TokenizerAnchor:
    """
    CIAF Tokenizer Anchor - tracks tokenizer provenance.
    """
    anchor_id: str
    tokenizer_type: str
    vocab_size: int
    tokenizer_files_hash: str
    created_at: str
    
    # Training data reference (if trained)
    training_data_anchors: List[str] = field(default_factory=list)
    
    # Tokenizer metadata
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, output_path: str):
        """Save anchor to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


class ModelAnchorManager:
    """
    Manages creation and tracking of model anchors in CIAF framework.
    """
    
    def __init__(self, anchors_dir: str = "./anchors"):
        """
        Initialize model anchor manager.
        
        Args:
            anchors_dir: Directory to store anchor files
        """
        self.anchors_dir = Path(anchors_dir)
        self.anchors_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_anchors: Dict[str, ModelAnchor] = {}
        self.version_anchors: Dict[str, ModelVersionAnchor] = {}
        self.tokenizer_anchors: Dict[str, TokenizerAnchor] = {}
    
    @staticmethod
    def compute_config_hash(config: Dict[str, Any]) -> str:
        """Compute hash of model configuration."""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    @staticmethod
    def compute_weights_hash(weights_path: str) -> str:
        """
        Compute hash of model weights file.
        
        Args:
            weights_path: Path to weights file
            
        Returns:
            SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(weights_path, "rb") as f:
            # Read in chunks for large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def create_model_anchor(
        self,
        model_type: str,
        config: Dict[str, Any],
        initial_weights_path: Optional[str] = None,
        tokenizer_anchor_id: Optional[str] = None,
        description: str = ""
    ) -> ModelAnchor:
        """
        Create a new model anchor.
        
        Args:
            model_type: Type of model (e.g., "gpt_ciaf_v1")
            config: Model configuration dictionary
            initial_weights_path: Optional path to initial weights file
            tokenizer_anchor_id: Optional tokenizer anchor reference
            description: Human-readable description
            
        Returns:
            ModelAnchor object
        """
        # Compute hashes
        config_hash = self.compute_config_hash(config)
        
        if initial_weights_path:
            weights_hash = self.compute_weights_hash(initial_weights_path)
        else:
            # Use config hash as placeholder for uninitialized model
            weights_hash = "uninitialized_" + config_hash[:16]
        
        # Create anchor ID
        timestamp = datetime.utcnow().timestamp()
        anchor_id = f"model_{model_type}_{timestamp}_{config_hash[:8]}"
        
        # Create anchor
        anchor = ModelAnchor(
            anchor_id=anchor_id,
            model_type=model_type,
            config_hash=config_hash,
            initial_weights_hash=weights_hash,
            created_at=datetime.utcnow().isoformat() + 'Z',
            config_data=config,
            tokenizer_anchor_id=tokenizer_anchor_id,
            description=description
        )
        
        # Store and save
        self.model_anchors[anchor_id] = anchor
        anchor.save(str(self.anchors_dir / f"{anchor_id}.json"))
        
        print(f"Created model anchor: {anchor_id}")
        return anchor
    
    def create_version_anchor(
        self,
        base_model_anchor_id: str,
        training_session_id: str,
        checkpoint_step: int,
        tokens_seen: int,
        checkpoint_path: str,
        eval_metrics: Optional[Dict[str, float]] = None,
        training_loss: Optional[float] = None,
        validation_loss: Optional[float] = None
    ) -> ModelVersionAnchor:
        """
        Create a model version anchor for a checkpoint.
        
        Args:
            base_model_anchor_id: Base model anchor ID
            training_session_id: Training session ID
            checkpoint_step: Training step at checkpoint
            tokens_seen: Total tokens seen during training
            checkpoint_path: Path to checkpoint file
            eval_metrics: Optional evaluation metrics
            training_loss: Optional training loss
            validation_loss: Optional validation loss
            
        Returns:
            ModelVersionAnchor object
        """
        # Compute weights hash
        weights_hash = self.compute_weights_hash(checkpoint_path)
        
        # Create version anchor ID
        version_anchor_id = f"{base_model_anchor_id}_v{checkpoint_step}_{weights_hash[:8]}"
        
        # Create anchor
        anchor = ModelVersionAnchor(
            version_anchor_id=version_anchor_id,
            base_model_anchor_id=base_model_anchor_id,
            training_session_id=training_session_id,
            checkpoint_step=checkpoint_step,
            tokens_seen=tokens_seen,
            weights_hash=weights_hash,
            created_at=datetime.utcnow().isoformat() + 'Z',
            eval_metrics=eval_metrics or {},
            training_loss=training_loss,
            validation_loss=validation_loss,
            checkpoint_path=checkpoint_path
        )
        
        # Store and save
        self.version_anchors[version_anchor_id] = anchor
        anchor.save(str(self.anchors_dir / f"{version_anchor_id}.json"))
        
        print(f"Created version anchor: {version_anchor_id}")
        return anchor
    
    def create_tokenizer_anchor(
        self,
        tokenizer_type: str,
        vocab_size: int,
        tokenizer_files_path: str,
        training_data_anchors: Optional[List[str]] = None,
        description: str = ""
    ) -> TokenizerAnchor:
        """
        Create a tokenizer anchor.
        
        Args:
            tokenizer_type: Type of tokenizer (e.g., "BPE", "WordPiece")
            vocab_size: Vocabulary size
            tokenizer_files_path: Path to tokenizer files directory
            training_data_anchors: Optional list of data anchor IDs used for training
            description: Human-readable description
            
        Returns:
            TokenizerAnchor object
        """
        # Compute hash of tokenizer files
        tokenizer_path = Path(tokenizer_files_path)
        combined_hash = hashlib.sha256()
        
        # Hash all files in directory
        for file_path in sorted(tokenizer_path.glob("*")):
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    combined_hash.update(f.read())
        
        files_hash = combined_hash.hexdigest()
        
        # Create anchor ID
        timestamp = datetime.utcnow().timestamp()
        anchor_id = f"tokenizer_{tokenizer_type}_{timestamp}_{files_hash[:8]}"
        
        # Create anchor
        anchor = TokenizerAnchor(
            anchor_id=anchor_id,
            tokenizer_type=tokenizer_type,
            vocab_size=vocab_size,
            tokenizer_files_hash=files_hash,
            created_at=datetime.utcnow().isoformat() + 'Z',
            training_data_anchors=training_data_anchors or [],
            description=description
        )
        
        # Store and save
        self.tokenizer_anchors[anchor_id] = anchor
        anchor.save(str(self.anchors_dir / f"{anchor_id}.json"))
        
        print(f"Created tokenizer anchor: {anchor_id}")
        return anchor


if __name__ == "__main__":
    # Example usage
    manager = ModelAnchorManager(anchors_dir="./test_anchors")
    
    # Create model anchor
    config = {
        "d_model": 1024,
        "n_layer": 20,
        "n_head": 16,
        "vocab_size": 32768
    }
    
    model_anchor = manager.create_model_anchor(
        model_type="gpt_ciaf_v1",
        config=config,
        description="Medium GPT model for SlimPajama-6B"
    )
    
    print(f"\nModel Anchor ID: {model_anchor.anchor_id}")
    print(f"Config Hash: {model_anchor.config_hash}")
