"""
Training Module
Simple training loop for GPT model on SlimPajama-6B
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from tqdm import tqdm
from typing import Dict, Any, Optional
import json
from datetime import datetime, timezone

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from model import GPTModel, GPTModelConfig
from data import SlimPajamaDataLoader


class Trainer:
    """
    Simple trainer for GPT model.
    Handles training loop, validation, and checkpointing.
    """
    
    def __init__(
        self,
        model: GPTModel,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        device: str = "cuda",
        checkpoint_dir: str = "./checkpoints",
        log_interval: int = 100,
        val_interval: int = 500,
        gradient_accumulation_steps: int = 4,
        max_grad_norm: float = 1.0
    ):
        """
        Initialize trainer.
        
        Args:
            model: GPT model to train
            train_loader: Training data loader
            val_loader: Validation data loader
            optimizer: Optimizer (will create AdamW if None)
            device: Device to train on
            checkpoint_dir: Directory for checkpoints
            log_interval: Steps between logging
            val_interval: Steps between validation
            gradient_accumulation_steps: Gradient accumulation steps
            max_grad_norm: Maximum gradient norm for clipping
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Create optimizer if not provided
        if optimizer is None:
            self.optimizer = AdamW(
                self.model.parameters(),
                lr=3e-4,
                betas=(0.9, 0.95),
                weight_decay=0.1
            )
        else:
            self.optimizer = optimizer
        
        self.log_interval = log_interval
        self.val_interval = val_interval
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.max_grad_norm = max_grad_norm
        
        # Training state
        self.global_step = 0
        self.current_epoch = 0
        self.best_val_loss = float('inf')
        self.training_history = []
        
    def train_step(self, batch: torch.Tensor) -> float:
        """
        Perform a single training step.
        
        Args:
            batch: Input token IDs (batch_size, seq_len)
            
        Returns:
            Loss value
        """
        self.model.train()
        
        # Move batch to device
        input_ids = batch.to(self.device)
        
        # Forward pass
        logits = self.model(input_ids)
        
        # Compute loss (shift for next token prediction)
        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = input_ids[:, 1:].contiguous()
        
        loss = nn.functional.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100
        )
        
        # Backward pass with gradient accumulation
        loss = loss / self.gradient_accumulation_steps
        loss.backward()
        
        return loss.item() * self.gradient_accumulation_steps
    
    def validation_step(self) -> Dict[str, float]:
        """
        Perform validation.
        
        Returns:
            Dictionary with validation metrics
        """
        if self.val_loader is None:
            return {}
        
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch.to(self.device)
                
                # Forward pass
                logits = self.model(input_ids)
                
                # Compute loss
                shift_logits = logits[:, :-1, :].contiguous()
                shift_labels = input_ids[:, 1:].contiguous()
                
                loss = nn.functional.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                    ignore_index=-100
                )
                
                total_loss += loss.item()
                num_batches += 1
                
                # Limit validation batches
                if num_batches >= 50:
                    break
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        
        return {
            'val_loss': avg_loss,
            'val_perplexity': torch.exp(torch.tensor(avg_loss)).item()
        }
    
    def train_epoch(self):
        """Train for one epoch."""
        self.model.train()
        epoch_loss = 0.0
        num_batches = 0
        
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch}")
        
        for batch_idx, batch in enumerate(progress_bar):
            # Training step
            loss = self.train_step(batch)
            epoch_loss += loss
            num_batches += 1
            
            # Optimizer step (with gradient accumulation)
            if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.max_grad_norm
                )
                
                # Optimizer step
                self.optimizer.step()
                self.optimizer.zero_grad()
                
                self.global_step += 1
                
                # Logging
                if self.global_step % self.log_interval == 0:
                    avg_loss = epoch_loss / num_batches
                    progress_bar.set_postfix({
                        'loss': f'{avg_loss:.4f}',
                        'step': self.global_step
                    })
                
                # Validation
                if self.global_step % self.val_interval == 0:
                    val_metrics = self.validation_step()
                    if val_metrics:
                        print(f"\nValidation at step {self.global_step}:")
                        print(f"  Loss: {val_metrics['val_loss']:.4f}")
                        print(f"  Perplexity: {val_metrics['val_perplexity']:.2f}")
                        
                        # Save best model
                        if val_metrics['val_loss'] < self.best_val_loss:
                            self.best_val_loss = val_metrics['val_loss']
                            self.save_checkpoint('best_model.pt')
                            print(f"  Saved best model (val_loss={self.best_val_loss:.4f})")
                    
                    self.model.train()
        
        avg_epoch_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
        return avg_epoch_loss
    
    def train(self, num_epochs: int):
        """
        Train for multiple epochs.
        
        Args:
            num_epochs: Number of epochs to train
        """
        print(f"Starting training for {num_epochs} epochs")
        print(f"  Device: {self.device}")
        print(f"  Global step: {self.global_step}")
        print(f"  Gradient accumulation: {self.gradient_accumulation_steps}")
        print()
        
        for epoch in range(num_epochs):
            self.current_epoch = epoch
            
            # Train epoch
            epoch_loss = self.train_epoch()
            
            # Validation
            val_metrics = self.validation_step()
            
            # Log epoch summary
            print(f"\nEpoch {epoch} Summary:")
            print(f"  Train Loss: {epoch_loss:.4f}")
            if val_metrics:
                print(f"  Val Loss: {val_metrics['val_loss']:.4f}")
                print(f"  Val Perplexity: {val_metrics['val_perplexity']:.2f}")
            
            # Save epoch history
            history_entry = {
                'epoch': epoch,
                'global_step': self.global_step,
                'train_loss': epoch_loss,
                **val_metrics,
                'timestamp': datetime.now(timezone.utc).isoformat() + 'Z'
            }
            self.training_history.append(history_entry)
            
            # Save checkpoint
            self.save_checkpoint(f'epoch_{epoch}.pt')
            print()
        
        print("Training complete!")
        self.save_training_history()
    
    def save_checkpoint(self, filename: str):
        """
        Save model checkpoint.
        
        Args:
            filename: Checkpoint filename
        """
        checkpoint_path = self.checkpoint_dir / filename
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'global_step': self.global_step,
            'epoch': self.current_epoch,
            'best_val_loss': self.best_val_loss
        }, checkpoint_path)
    
    def load_checkpoint(self, filename: str):
        """
        Load model checkpoint.
        
        Args:
            filename: Checkpoint filename
        """
        checkpoint_path = self.checkpoint_dir / filename
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.global_step = checkpoint['global_step']
        self.current_epoch = checkpoint['epoch']
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        
        print(f"Loaded checkpoint from {checkpoint_path}")
        print(f"  Global step: {self.global_step}")
        print(f"  Epoch: {self.current_epoch}")
    
    def save_training_history(self):
        """Save training history to JSON."""
        history_path = self.checkpoint_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        print(f"Saved training history to {history_path}")


def create_trainer(
    model: GPTModel,
    train_loader: DataLoader,
    val_loader: Optional[DataLoader] = None,
    learning_rate: float = 3e-4,
    device: str = "cuda",
    checkpoint_dir: str = "./checkpoints"
) -> Trainer:
    """
    Create a trainer instance.
    
    Args:
        model: GPT model
        train_loader: Training data loader
        val_loader: Validation data loader
        learning_rate: Learning rate
        device: Device to train on
        checkpoint_dir: Checkpoint directory
        
    Returns:
        Trainer instance
    """
    optimizer = AdamW(
        model.parameters(),
        lr=learning_rate,
        betas=(0.9, 0.95),
        weight_decay=0.1
    )
    
    return Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        device=device,
        checkpoint_dir=checkpoint_dir
    )


if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("Trainer Test")
    print("="*80)
    
    # Create model
    from model import create_small_model
    model = create_small_model()
    
    # Create data loaders
    from data import create_dataloaders
    train_loader, val_loader = create_dataloaders(
        batch_size=8,
        max_length=512,
        num_workers=0
    )
    
    # Create trainer
    trainer = create_trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    # Train for 1 epoch (demo)
    trainer.train(num_epochs=1)
