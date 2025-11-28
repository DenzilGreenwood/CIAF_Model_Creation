"""
Training utilities for the language model.
Includes optimizer setup, learning rate scheduling, and training loop.
"""
import os
import math
import time
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from typing import Optional, Dict, Tuple
from pathlib import Path

from model import LanguageModel
from config import ModelConfig
from dataset import InfiniteDataLoader


class LearningRateScheduler:
    """Learning rate scheduler with warmup and cosine decay."""
    
    def __init__(
        self,
        optimizer: torch.optim.Optimizer,
        warmup_steps: int,
        max_steps: int,
        min_lr: float,
        max_lr: float,
    ):
        """
        Initialize learning rate scheduler.
        
        Args:
            optimizer: PyTorch optimizer
            warmup_steps: Number of warmup steps
            max_steps: Maximum number of training steps
            min_lr: Minimum learning rate
            max_lr: Maximum learning rate
        """
        self.optimizer = optimizer
        self.warmup_steps = warmup_steps
        self.max_steps = max_steps
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.current_step = 0
    
    def get_lr(self) -> float:
        """Calculate learning rate for current step."""
        if self.current_step < self.warmup_steps:
            # Linear warmup
            lr = self.max_lr * (self.current_step / self.warmup_steps)
        else:
            # Cosine decay
            progress = (self.current_step - self.warmup_steps) / (self.max_steps - self.warmup_steps)
            progress = min(1.0, progress)
            lr = self.min_lr + 0.5 * (self.max_lr - self.min_lr) * (
                1 + math.cos(math.pi * progress)
            )
        return lr
    
    def step(self):
        """Update learning rate."""
        self.current_step += 1
        lr = self.get_lr()
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        return lr


class Trainer:
    """Trainer for the language model."""
    
    def __init__(
        self,
        model: LanguageModel,
        config: ModelConfig,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        checkpoint_dir: str = "checkpoints",
    ):
        """
        Initialize trainer.
        
        Args:
            model: Language model to train
            config: Model configuration
            train_loader: Training data loader
            val_loader: Validation data loader (optional)
            checkpoint_dir: Directory to save checkpoints
        """
        self.model = model
        self.config = config
        self.train_loader = InfiniteDataLoader(train_loader)
        self.val_loader = val_loader
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Move model to device
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"Using device: {self.device}")
        
        # Setup optimizer
        self.optimizer = self._create_optimizer()
        
        # Setup learning rate scheduler
        self.scheduler = LearningRateScheduler(
            self.optimizer,
            warmup_steps=config.warmup_steps,
            max_steps=config.max_steps,
            min_lr=config.min_lr,
            max_lr=config.learning_rate,
        )
        
        # Training state
        self.step = 0
        self.best_val_loss = float('inf')
        
        # Compile model if requested (PyTorch 2.0+)
        if config.compile_model and hasattr(torch, 'compile'):
            print("Compiling model...")
            self.model = torch.compile(self.model)
    
    def _create_optimizer(self) -> torch.optim.Optimizer:
        """Create AdamW optimizer with weight decay."""
        # Separate parameters for weight decay
        decay_params = []
        no_decay_params = []
        
        for name, param in self.model.named_parameters():
            if not param.requires_grad:
                continue
            
            # No weight decay for biases and layer norms
            if 'bias' in name or 'ln' in name or 'layernorm' in name:
                no_decay_params.append(param)
            else:
                decay_params.append(param)
        
        optimizer_groups = [
            {'params': decay_params, 'weight_decay': self.config.weight_decay},
            {'params': no_decay_params, 'weight_decay': 0.0},
        ]
        
        optimizer = AdamW(
            optimizer_groups,
            lr=self.config.learning_rate,
            betas=(self.config.beta1, self.config.beta2),
        )
        
        return optimizer
    
    def train_step(self, batch: Dict[str, torch.Tensor]) -> float:
        """
        Perform a single training step.
        
        Args:
            batch: Dictionary with 'input_ids' and 'labels'
            
        Returns:
            Loss value
        """
        self.model.train()
        
        # Move batch to device
        input_ids = batch['input_ids'].to(self.device)
        labels = batch['labels'].to(self.device)
        
        # Forward pass
        logits, loss = self.model(input_ids, targets=labels)
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        if self.config.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.grad_clip)
        
        # Optimizer step
        self.optimizer.step()
        self.optimizer.zero_grad()
        
        # Update learning rate
        self.scheduler.step()
        
        return loss.item()
    
    @torch.no_grad()
    def evaluate(self) -> float:
        """
        Evaluate model on validation set.
        
        Returns:
            Average validation loss
        """
        if self.val_loader is None:
            return 0.0
        
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        for batch in self.val_loader:
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            _, loss = self.model(input_ids, targets=labels)
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        return avg_loss
    
    def save_checkpoint(self, filename: str = "checkpoint.pt") -> None:
        """
        Save model checkpoint.
        
        Args:
            filename: Name of checkpoint file
        """
        checkpoint = {
            'step': self.step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'best_val_loss': self.best_val_loss,
        }
        
        filepath = self.checkpoint_dir / filename
        torch.save(checkpoint, filepath)
        print(f"Checkpoint saved to {filepath}")
    
    def load_checkpoint(self, filepath: str) -> None:
        """
        Load model checkpoint.
        
        Args:
            filepath: Path to checkpoint file
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.step = checkpoint['step']
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        
        print(f"Checkpoint loaded from {filepath} (step {self.step})")
    
    def train(self, max_steps: Optional[int] = None) -> None:
        """
        Main training loop.
        
        Args:
            max_steps: Maximum number of training steps (uses config if None)
        """
        if max_steps is None:
            max_steps = self.config.max_steps
        
        print(f"Starting training for {max_steps:,} steps...")
        print(f"Gradient accumulation steps: {self.config.gradient_accumulation_steps}")
        
        start_time = time.time()
        accumulated_loss = 0.0
        log_interval = 10
        
        while self.step < max_steps:
            # Training step
            batch = next(self.train_loader)
            loss = self.train_step(batch)
            accumulated_loss += loss
            
            self.step += 1
            
            # Logging
            if self.step % log_interval == 0:
                avg_loss = accumulated_loss / log_interval
                lr = self.scheduler.get_lr()
                elapsed = time.time() - start_time
                tokens_per_sec = (
                    log_interval * self.config.batch_size * 
                    self.config.max_seq_len / elapsed
                )
                
                print(
                    f"Step {self.step:6d} | "
                    f"Loss: {avg_loss:.4f} | "
                    f"LR: {lr:.2e} | "
                    f"Tokens/s: {tokens_per_sec:.0f}"
                )
                
                accumulated_loss = 0.0
                start_time = time.time()
            
            # Evaluation
            if self.step % self.config.eval_every == 0 and self.val_loader is not None:
                val_loss = self.evaluate()
                print(f"Validation loss at step {self.step}: {val_loss:.4f}")
                
                # Save best model
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.save_checkpoint("best_model.pt")
                    print(f"New best validation loss: {val_loss:.4f}")
            
            # Checkpointing
            if self.step % self.config.save_every == 0:
                self.save_checkpoint(f"checkpoint_step_{self.step}.pt")
        
        print(f"Training complete! Final step: {self.step}")
        self.save_checkpoint("final_model.pt")


if __name__ == "__main__":
    # Example usage
    from config import TINY_CONFIG
    from dataset import TextDataset, TextDataLoader
    from tokenizer import BPETokenizer
    
    # Create sample data
    sample_text = "Hello world! " * 1000
    
    # Initialize tokenizer
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(sample_text, verbose=False)
    
    # Create dataset
    tokens = tokenizer.encode(sample_text)
    train_tokens, val_tokens = tokens[:int(0.9*len(tokens))], tokens[int(0.9*len(tokens)):]
    
    data_loader = TextDataLoader(tokenizer, batch_size=4, seq_len=64)
    train_loader = data_loader.create_dataloader(train_tokens)
    val_loader = data_loader.create_dataloader(val_tokens, shuffle=False)
    
    # Create model
    config = TINY_CONFIG
    config.max_steps = 100
    config.eval_every = 50
    config.save_every = 50
    
    model = LanguageModel(config)
    
    # Create trainer
    trainer = Trainer(model, config, train_loader, val_loader)
    
    # Train
    trainer.train()
