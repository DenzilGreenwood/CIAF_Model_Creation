"""
CIAF Training Session Manager
Tracks training runs with full provenance and epoch-level receipts
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TrainingSessionAnchor:
    """
    CIAF Training Session Anchor - root anchor for a complete training run.
    """
    session_id: str
    model_anchor_id: str
    dataset_anchors: List[str]
    policy_id: str
    
    # Hyperparameters
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    
    # Session metadata
    training_start: str = ""
    training_end: Optional[str] = None
    status: str = "initialized"  # initialized, running, completed, failed
    
    # High-level stats
    total_steps: int = 0
    total_tokens_trained: int = 0
    final_loss: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, output_path: str):
        """Save to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class EpochReceipt:
    """
    Receipt for a single training epoch or checkpoint interval.
    """
    receipt_id: str
    session_id: str
    epoch: int
    global_step: int
    tokens_seen: int
    timestamp: str
    
    # Metrics
    training_loss: float
    validation_loss: Optional[float] = None
    learning_rate: float = 0.0
    gradient_norm: Optional[float] = None
    
    # Additional metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Commitment hash
    commitment_hash: str = ""
    
    def compute_commitment_hash(self) -> str:
        """Compute commitment hash for this receipt."""
        data = self.to_dict()
        data.pop('commitment_hash', None)  # Remove existing hash
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TrainingSessionManager:
    """
    Manages CIAF training sessions with epoch-level provenance tracking.
    """
    
    def __init__(self, sessions_dir: str = "./training_sessions"):
        """
        Initialize training session manager.
        
        Args:
            sessions_dir: Directory to store session data
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.active_session: Optional[TrainingSessionAnchor] = None
        self.epoch_receipts: List[EpochReceipt] = []
    
    def create_session(
        self,
        model_anchor_id: str,
        dataset_anchors: List[str],
        policy_id: str,
        hyperparameters: Dict[str, Any],
        session_name: Optional[str] = None
    ) -> TrainingSessionAnchor:
        """
        Create a new training session.
        
        Args:
            model_anchor_id: Model anchor ID
            dataset_anchors: List of dataset anchor IDs (train, val, etc.)
            policy_id: LCM policy ID
            hyperparameters: Training hyperparameters
            session_name: Optional custom session name
            
        Returns:
            TrainingSessionAnchor
        """
        # Generate session ID
        timestamp = datetime.now(timezone.utc).timestamp()
        if session_name:
            session_id = f"{session_name}_{timestamp}"
        else:
            session_id = f"session_{model_anchor_id[:16]}_{timestamp}"
        
        # Create session anchor
        session = TrainingSessionAnchor(
            session_id=session_id,
            model_anchor_id=model_anchor_id,
            dataset_anchors=dataset_anchors,
            policy_id=policy_id,
            hyperparameters=hyperparameters,
            training_start=datetime.now(timezone.utc).isoformat() + 'Z',
            status="initialized"
        )
        
        # Save session
        self.active_session = session
        self._save_session(session)
        
        print(f"Created training session: {session_id}")
        print(f"  Model: {model_anchor_id}")
        print(f"  Datasets: {len(dataset_anchors)} anchors")
        print(f"  Policy: {policy_id}")
        
        return session
    
    def start_session(self):
        """Mark session as running."""
        if self.active_session:
            self.active_session.status = "running"
            self.active_session.training_start = datetime.now(timezone.utc).isoformat() + 'Z'
            self._save_session(self.active_session)
            print(f"Started training session: {self.active_session.session_id}")
    
    def commit_epoch_results(
        self,
        epoch: int,
        global_step: int,
        tokens_seen: int,
        training_loss: float,
        validation_loss: Optional[float] = None,
        learning_rate: float = 0.0,
        gradient_norm: Optional[float] = None,
        additional_metrics: Optional[Dict[str, float]] = None
    ) -> EpochReceipt:
        """
        Commit results for an epoch and create a receipt.
        
        Args:
            epoch: Epoch number
            global_step: Global training step
            tokens_seen: Total tokens processed
            training_loss: Average training loss
            validation_loss: Optional validation loss
            learning_rate: Current learning rate
            gradient_norm: Optional gradient norm
            additional_metrics: Optional additional metrics
            
        Returns:
            EpochReceipt
        """
        if not self.active_session:
            raise RuntimeError("No active training session")
        
        # Create receipt
        receipt_id = f"{self.active_session.session_id}_epoch{epoch}_step{global_step}"
        
        receipt = EpochReceipt(
            receipt_id=receipt_id,
            session_id=self.active_session.session_id,
            epoch=epoch,
            global_step=global_step,
            tokens_seen=tokens_seen,
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            training_loss=training_loss,
            validation_loss=validation_loss,
            learning_rate=learning_rate,
            gradient_norm=gradient_norm,
            metrics=additional_metrics or {}
        )
        
        # Compute commitment hash
        receipt.commitment_hash = receipt.compute_commitment_hash()
        
        # Store receipt
        self.epoch_receipts.append(receipt)
        
        # Update session stats
        self.active_session.total_steps = global_step
        self.active_session.total_tokens_trained = tokens_seen
        self.active_session.final_loss = training_loss
        
        # Save
        self._save_session(self.active_session)
        self._save_receipt(receipt)
        
        print(f"Epoch {epoch} - Step {global_step}:")
        print(f"  Loss: {training_loss:.4f}" + (f" / Val: {validation_loss:.4f}" if validation_loss else ""))
        print(f"  Tokens: {tokens_seen:,}")
        print(f"  Commitment: {receipt.commitment_hash[:16]}...")
        
        return receipt
    
    def complete_session(self):
        """Mark session as completed."""
        if self.active_session:
            self.active_session.status = "completed"
            self.active_session.training_end = datetime.now(timezone.utc).isoformat() + 'Z'
            self._save_session(self.active_session)
            print(f"Completed training session: {self.active_session.session_id}")
    
    def fail_session(self, error_message: str = ""):
        """Mark session as failed."""
        if self.active_session:
            self.active_session.status = "failed"
            self.active_session.training_end = datetime.now(timezone.utc).isoformat() + 'Z'
            if error_message:
                self.active_session.hyperparameters['error'] = error_message
            self._save_session(self.active_session)
            print(f"Session failed: {self.active_session.session_id}")
    
    def _save_session(self, session: TrainingSessionAnchor):
        """Save session to disk."""
        session_path = self.sessions_dir / f"{session.session_id}.json"
        session.save(str(session_path))
    
    def _save_receipt(self, receipt: EpochReceipt):
        """Save epoch receipt to disk."""
        receipts_dir = self.sessions_dir / "receipts"
        receipts_dir.mkdir(exist_ok=True)
        
        receipt_path = receipts_dir / f"{receipt.receipt_id}.json"
        with open(receipt_path, 'w', encoding='utf-8') as f:
            json.dump(receipt.to_dict(), f, indent=2)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        if not self.active_session:
            return {}
        
        return {
            'session_id': self.active_session.session_id,
            'status': self.active_session.status,
            'total_steps': self.active_session.total_steps,
            'total_tokens': self.active_session.total_tokens_trained,
            'final_loss': self.active_session.final_loss,
            'epochs_tracked': len(self.epoch_receipts)
        }


if __name__ == "__main__":
    # Example usage
    manager = TrainingSessionManager(sessions_dir="./test_sessions")
    
    # Create session
    session = manager.create_session(
        model_anchor_id="model_gpt_ciaf_v1_12345",
        dataset_anchors=["dataset_train_001", "dataset_val_001"],
        policy_id="pretrain_slimpajama_v1",
        hyperparameters={
            'learning_rate': 1e-4,
            'batch_size': 4,
            'grad_accumulation_steps': 32,
            'optimizer': 'adamw',
            'weight_decay': 0.1,
            'warmup_steps': 1000
        },
        session_name="slimpajama_gpt_run01"
    )
    
    # Start training
    manager.start_session()
    
    # Simulate some epochs
    for epoch in range(3):
        manager.commit_epoch_results(
            epoch=epoch,
            global_step=epoch * 1000,
            tokens_seen=epoch * 1000000,
            training_loss=3.5 - (epoch * 0.3),
            validation_loss=3.6 - (epoch * 0.25),
            learning_rate=1e-4,
            gradient_norm=0.5
        )
    
    # Complete session
    manager.complete_session()
    
    # Print summary
    summary = manager.get_session_summary()
    print("\nSession Summary:")
    print(json.dumps(summary, indent=2))
