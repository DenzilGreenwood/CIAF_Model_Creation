"""
Evaluation Module
Evaluates GPT model performance with perplexity and loss metrics
"""

import sys
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm
import math
from typing import Dict, Any, Optional, List

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from model import GPTModel


class ModelEvaluator:
    """
    Evaluates GPT model performance.
    """
    
    def __init__(
        self,
        model: GPTModel,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize evaluator.
        
        Args:
            model: GPT model instance
            device: Device to evaluate on
        """
        self.model = model.to(device)
        self.model.eval()
        self.device = device
    
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
            logits = self.model(input_ids)
            
            # Compute loss (shift for next token prediction)
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = input_ids[:, 1:].contiguous()
            
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
                reduction='sum'
            )
            
            # Accumulate loss
            batch_size, seq_len = input_ids.shape
            num_tokens = batch_size * (seq_len - 1)
            
            total_loss += loss.item()
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
            logits = self.model(input_ids)
            
            # Compute loss
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = input_ids[:, 1:].contiguous()
            
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100
            )
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        return avg_loss
    
    @torch.no_grad()
    def generate_samples(
        self,
        prompts: List[str],
        tokenizer,
        max_length: int = 100,
        temperature: float = 1.0,
        top_k: int = 50
    ) -> List[str]:
        """
        Generate text samples from prompts.
        
        Args:
            prompts: List of prompt strings
            tokenizer: Tokenizer instance
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            
        Returns:
            List of generated texts
        """
        self.model.eval()
        generated_texts = []
        
        for prompt in prompts:
            # Encode prompt
            input_ids = tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate
            for _ in range(max_length):
                # Forward pass
                logits = self.model(input_ids)
                
                # Get next token logits
                next_token_logits = logits[:, -1, :] / temperature
                
                # Top-k sampling
                if top_k > 0:
                    top_k_values, top_k_indices = torch.topk(next_token_logits, top_k)
                    next_token_logits = torch.full_like(next_token_logits, float('-inf'))
                    next_token_logits.scatter_(1, top_k_indices, top_k_values)
                
                # Sample next token
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append to input
                input_ids = torch.cat([input_ids, next_token], dim=1)
                
                # Check for EOS
                if next_token.item() == tokenizer.tokenizer.eos_token_id:
                    break
            
            # Decode
            generated_text = tokenizer.decode(input_ids[0])
            generated_texts.append(generated_text)
        
        return generated_texts
    
    def evaluate_all(
        self,
        test_loader: DataLoader,
        max_batches: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compute all evaluation metrics.
        
        Args:
            test_loader: Test data loader
            max_batches: Optional maximum number of batches
            
        Returns:
            Dictionary with all metrics
        """
        print("Running full evaluation...")
        
        # Compute metrics
        perplexity = self.compute_perplexity(test_loader, max_batches)
        loss = self.compute_loss(test_loader, max_batches)
        
        metrics = {
            'perplexity': perplexity,
            'loss': loss,
            'num_batches_evaluated': max_batches if max_batches else len(test_loader)
        }
        
        print("\nEvaluation Results:")
        print(f"  Perplexity: {perplexity:.2f}")
        print(f"  Loss: {loss:.4f}")
        
        return metrics


def create_evaluator(
    model: GPTModel,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> ModelEvaluator:
    """
    Create an evaluator instance.
    
    Args:
        model: GPT model
        device: Device to evaluate on
        
    Returns:
        ModelEvaluator instance
    """
    return ModelEvaluator(model=model, device=device)


if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("Evaluator Test")
    print("="*80)
    
    # Create model
    from model import create_small_model
    model = create_small_model()
    
    # Create data loader
    from data import create_dataloaders
    _, test_loader = create_dataloaders(
        batch_size=8,
        max_length=512,
        num_workers=0
    )
    
    # Create evaluator
    evaluator = create_evaluator(
        model=model,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    # Evaluate (limited batches for demo)
    metrics = evaluator.evaluate_all(test_loader, max_batches=10)
    print(f"\nFinal metrics: {metrics}")
