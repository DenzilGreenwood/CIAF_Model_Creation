"""
Evaluation Harness for GPT Model
Computes perplexity and other metrics with CIAF integration
"""

import sys
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm
import math
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from model.gpt_model import GPTModel
from ciaf_integration.evaluation_anchors import EvaluationManager


class ModelEvaluator:
    """
    Evaluates GPT model with CIAF provenance tracking.
    """
    
    def __init__(
        self,
        model: GPTModel,
        model_version_anchor_id: str,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize evaluator.
        
        Args:
            model: GPT model instance
            model_version_anchor_id: CIAF model version anchor ID
            device: Device to evaluate on
        """
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.model_version_anchor_id = model_version_anchor_id
        
        # CIAF evaluation manager
        self.eval_manager = EvaluationManager()
    
    @torch.no_grad()
    def compute_perplexity(
        self,
        test_loader: DataLoader,
        max_batches: Optional[int] = None
    ) -> float:
        """
        Compute perplexity on test set.
        
        Args:
            test_loader: Test data loader
            max_batches: Optional maximum number of batches
            
        Returns:
            Perplexity value
        """
        total_loss = 0.0
        total_tokens = 0
        num_batches = 0
        
        for batch in tqdm(test_loader, desc="Computing perplexity"):
            if max_batches and num_batches >= max_batches:
                break
            
            input_ids = batch.to(self.device)
            
            # Forward pass
            _, loss = self.model(input_ids, labels=input_ids)
            
            # Accumulate loss
            batch_size, seq_len = input_ids.shape
            num_tokens = batch_size * seq_len
            
            total_loss += loss.item() * num_tokens
            total_tokens += num_tokens
            num_batches += 1
        
        # Compute average loss and perplexity
        avg_loss = total_loss / total_tokens if total_tokens > 0 else 0.0
        perplexity = math.exp(avg_loss) if avg_loss < 100 else float('inf')
        
        return perplexity
    
    @torch.no_grad()
    def compute_loss(
        self,
        test_loader: DataLoader,
        max_batches: Optional[int] = None
    ) -> float:
        """
        Compute average loss on test set.
        
        Args:
            test_loader: Test data loader
            max_batches: Optional maximum number of batches
            
        Returns:
            Average loss
        """
        total_loss = 0.0
        num_batches = 0
        
        for batch in tqdm(test_loader, desc="Computing loss"):
            if max_batches and num_batches >= max_batches:
                break
            
            input_ids = batch.to(self.device)
            
            # Forward pass
            _, loss = self.model(input_ids, labels=input_ids)
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        return avg_loss
    
    def evaluate(
        self,
        test_loader: DataLoader,
        test_dataset_anchors: list,
        max_batches: Optional[int] = None,
        eval_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Run full evaluation and create CIAF evaluation anchor.
        
        Args:
            test_loader: Test data loader
            test_dataset_anchors: List of test dataset anchor IDs
            max_batches: Optional maximum number of batches
            eval_config: Optional evaluation configuration
            
        Returns:
            Dictionary of metrics
        """
        print(f"Evaluating model: {self.model_version_anchor_id}")
        print(f"Device: {self.device}")
        
        # Create evaluation anchor
        evaluation = self.eval_manager.create_evaluation(
            model_version_anchor_id=self.model_version_anchor_id,
            test_dataset_anchors=test_dataset_anchors,
            eval_config=eval_config or {}
        )
        
        # Compute metrics
        print("\nComputing metrics...")
        loss = self.compute_loss(test_loader, max_batches)
        perplexity = self.compute_perplexity(test_loader, max_batches)
        
        metrics = {
            'loss': loss,
            'perplexity': perplexity,
            'bits_per_byte': loss / math.log(2)  # Convert nats to bits
        }
        
        # Additional compliance checks (placeholders)
        compliance_validation = {
            'non_pii_test_set': True,
            'safety_check': True,
            'bias_check': True
        }
        
        # Record results
        self.eval_manager.record_results(
            evaluation_id=evaluation.evaluation_id,
            metrics=metrics,
            test_results={
                'num_batches': len(test_loader) if not max_batches else min(max_batches, len(test_loader)),
                'device': self.device
            },
            compliance_validation=compliance_validation
        )
        
        print("\nEvaluation Results:")
        print(f"  Loss: {loss:.4f}")
        print(f"  Perplexity: {perplexity:.2f}")
        print(f"  Bits per byte: {metrics['bits_per_byte']:.4f}")
        
        return metrics
    
    @torch.no_grad()
    def generate_sample(
        self,
        prompt_ids: torch.Tensor,
        max_length: int = 100,
        temperature: float = 0.8,
        top_k: int = 50
    ) -> torch.Tensor:
        """
        Generate text sample from prompt.
        
        Args:
            prompt_ids: Prompt token IDs (1, seq_len)
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            
        Returns:
            Generated token IDs
        """
        generated = prompt_ids.clone()
        
        for _ in range(max_length):
            # Get logits for next token
            logits, _ = self.model(generated[:, -self.model.config.max_seq_len:])
            logits = logits[:, -1, :] / temperature
            
            # Top-k filtering
            if top_k > 0:
                indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                logits[indices_to_remove] = float('-inf')
            
            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Append to sequence
            generated = torch.cat([generated, next_token], dim=1)
            
            # Check for EOS token (simplified)
            if next_token.item() == 0:  # Assuming 0 is EOS
                break
        
        return generated


if __name__ == "__main__":
    print("Model Evaluation Harness with CIAF Integration")
    print("=" * 60)
    print("\nThis is a template evaluation script.")
    print("To use:")
    print("1. Load your trained model checkpoint")
    print("2. Prepare test data with CIAF dataset anchors")
    print("3. Run evaluation with full provenance tracking")
    print("4. Results are automatically tracked in CIAF evaluation anchors")
    print("\nSee README.md for detailed instructions.")
