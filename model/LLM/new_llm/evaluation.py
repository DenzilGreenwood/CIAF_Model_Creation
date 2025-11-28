"""
Evaluation metrics for language models.
Includes perplexity, BLEU, accuracy, and other metrics.
"""
import math
import torch
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import Counter

from model import LanguageModel
from tokenizer import BPETokenizer
from torch.utils.data import DataLoader


class Evaluator:
    """Comprehensive evaluation metrics for language models."""
    
    def __init__(
        self,
        model: LanguageModel,
        tokenizer: BPETokenizer,
        device: str = "cuda",
    ):
        """
        Initialize evaluator.
        
        Args:
            model: Language model to evaluate
            tokenizer: Tokenizer
            device: Device to run evaluation on
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
    
    @torch.no_grad()
    def compute_perplexity(
        self,
        dataloader: DataLoader,
        max_batches: Optional[int] = None,
    ) -> float:
        """
        Compute perplexity on a dataset.
        
        Args:
            dataloader: DataLoader with evaluation data
            max_batches: Maximum number of batches to evaluate (None = all)
            
        Returns:
            Perplexity value
        """
        total_loss = 0.0
        total_tokens = 0
        
        for i, batch in enumerate(dataloader):
            if max_batches and i >= max_batches:
                break
            
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            _, loss = self.model(input_ids, targets=labels)
            
            # Count valid tokens (not padding)
            valid_tokens = (labels != -100).sum().item()
            total_loss += loss.item() * valid_tokens
            total_tokens += valid_tokens
        
        if total_tokens == 0:
            return float('inf')
        
        avg_loss = total_loss / total_tokens
        perplexity = math.exp(avg_loss)
        
        return perplexity
    
    @torch.no_grad()
    def compute_accuracy(
        self,
        dataloader: DataLoader,
        top_k: int = 1,
        max_batches: Optional[int] = None,
    ) -> float:
        """
        Compute top-k accuracy on a dataset.
        
        Args:
            dataloader: DataLoader with evaluation data
            top_k: Consider top k predictions
            max_batches: Maximum number of batches to evaluate
            
        Returns:
            Accuracy as a percentage
        """
        total_correct = 0
        total_tokens = 0
        
        for i, batch in enumerate(dataloader):
            if max_batches and i >= max_batches:
                break
            
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            logits, _ = self.model(input_ids)
            
            # Get top-k predictions
            top_k_preds = torch.topk(logits, k=top_k, dim=-1).indices
            
            # Check if true label is in top-k
            labels_expanded = labels.unsqueeze(-1).expand_as(top_k_preds)
            correct = (top_k_preds == labels_expanded).any(dim=-1)
            
            # Mask out padding tokens
            valid_mask = labels != -100
            correct = correct & valid_mask
            
            total_correct += correct.sum().item()
            total_tokens += valid_mask.sum().item()
        
        if total_tokens == 0:
            return 0.0
        
        accuracy = 100.0 * total_correct / total_tokens
        return accuracy
    
    def compute_bleu(
        self,
        references: List[str],
        hypotheses: List[str],
        max_n: int = 4,
    ) -> Dict[str, float]:
        """
        Compute BLEU score for generated text.
        
        Args:
            references: List of reference texts
            hypotheses: List of generated texts
            max_n: Maximum n-gram order
            
        Returns:
            Dictionary with BLEU scores
        """
        assert len(references) == len(hypotheses), "Mismatched number of references and hypotheses"
        
        bleu_scores = {}
        
        for n in range(1, max_n + 1):
            precision = self._compute_ngram_precision(references, hypotheses, n)
            bleu_scores[f'bleu_{n}'] = precision
        
        # Compute cumulative BLEU-4
        if max_n >= 4:
            bleu_4 = math.exp(
                sum(math.log(bleu_scores[f'bleu_{i}'] + 1e-10) for i in range(1, 5)) / 4
            )
            bleu_scores['bleu_4_cumulative'] = bleu_4
        
        return bleu_scores
    
    def _compute_ngram_precision(
        self,
        references: List[str],
        hypotheses: List[str],
        n: int,
    ) -> float:
        """Compute n-gram precision."""
        total_match = 0
        total_count = 0
        
        for ref, hyp in zip(references, hypotheses):
            ref_tokens = self.tokenizer.encode(ref)
            hyp_tokens = self.tokenizer.encode(hyp)
            
            ref_ngrams = self._get_ngrams(ref_tokens, n)
            hyp_ngrams = self._get_ngrams(hyp_tokens, n)
            
            # Count matches
            for ngram in hyp_ngrams:
                if ngram in ref_ngrams:
                    total_match += min(hyp_ngrams[ngram], ref_ngrams[ngram])
            
            total_count += sum(hyp_ngrams.values())
        
        if total_count == 0:
            return 0.0
        
        return total_match / total_count
    
    @staticmethod
    def _get_ngrams(tokens: List[int], n: int) -> Counter:
        """Extract n-grams from token list."""
        ngrams = Counter()
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams[ngram] += 1
        return ngrams
    
    @torch.no_grad()
    def compute_loss_distribution(
        self,
        dataloader: DataLoader,
        num_bins: int = 50,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute distribution of token-level losses.
        
        Args:
            dataloader: DataLoader with evaluation data
            num_bins: Number of histogram bins
            
        Returns:
            Tuple of (bin_edges, histogram_values)
        """
        all_losses = []
        
        for batch in dataloader:
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            logits, _ = self.model(input_ids)
            
            # Compute per-token loss
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                labels.view(-1),
                reduction='none',
            )
            
            # Filter out padding
            valid_mask = labels.view(-1) != -100
            valid_losses = loss[valid_mask].cpu().numpy()
            all_losses.extend(valid_losses)
        
        # Create histogram
        hist, bin_edges = np.histogram(all_losses, bins=num_bins)
        
        return bin_edges, hist
    
    def compute_token_statistics(
        self,
        dataloader: DataLoader,
    ) -> Dict[str, any]:
        """
        Compute various token-level statistics.
        
        Args:
            dataloader: DataLoader with evaluation data
            
        Returns:
            Dictionary with statistics
        """
        token_counts = Counter()
        total_tokens = 0
        
        for batch in dataloader:
            labels = batch['labels']
            valid_tokens = labels[labels != -100]
            
            for token_id in valid_tokens.tolist():
                token_counts[token_id] += 1
                total_tokens += 1
        
        # Compute statistics
        vocab_coverage = len(token_counts) / self.model.config.vocab_size
        most_common = token_counts.most_common(10)
        
        return {
            'total_tokens': total_tokens,
            'unique_tokens': len(token_counts),
            'vocab_coverage': vocab_coverage,
            'most_common_tokens': [
                (token_id, count, count / total_tokens)
                for token_id, count in most_common
            ],
            'avg_token_frequency': total_tokens / len(token_counts) if token_counts else 0,
        }
    
    @torch.no_grad()
    def compute_calibration_error(
        self,
        dataloader: DataLoader,
        num_bins: int = 10,
    ) -> float:
        """
        Compute Expected Calibration Error (ECE).
        
        Args:
            dataloader: DataLoader with evaluation data
            num_bins: Number of confidence bins
            
        Returns:
            ECE value
        """
        bin_boundaries = torch.linspace(0, 1, num_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        confidences = []
        accuracies = []
        
        for batch in dataloader:
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            logits, _ = self.model(input_ids)
            probs = torch.softmax(logits, dim=-1)
            
            # Get predicted probabilities and predictions
            conf, pred = torch.max(probs, dim=-1)
            
            # Check correctness
            correct = (pred == labels).float()
            
            # Filter padding
            valid_mask = labels != -100
            confidences.extend(conf[valid_mask].cpu().tolist())
            accuracies.extend(correct[valid_mask].cpu().tolist())
        
        confidences = torch.tensor(confidences)
        accuracies = torch.tensor(accuracies)
        
        ece = 0.0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.float().mean()
            
            if prop_in_bin.item() > 0:
                accuracy_in_bin = accuracies[in_bin].mean()
                avg_confidence_in_bin = confidences[in_bin].mean()
                ece += torch.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece.item()
    
    def generate_evaluation_report(
        self,
        dataloader: DataLoader,
        save_path: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Generate comprehensive evaluation report.
        
        Args:
            dataloader: DataLoader with evaluation data
            save_path: Optional path to save report
            
        Returns:
            Dictionary with all evaluation metrics
        """
        print("Computing evaluation metrics...")
        
        report = {
            'perplexity': self.compute_perplexity(dataloader),
            'top_1_accuracy': self.compute_accuracy(dataloader, top_k=1),
            'top_5_accuracy': self.compute_accuracy(dataloader, top_k=5),
            'token_statistics': self.compute_token_statistics(dataloader),
            'calibration_error': self.compute_calibration_error(dataloader),
        }
        
        print(f"\nEvaluation Report:")
        print(f"Perplexity: {report['perplexity']:.2f}")
        print(f"Top-1 Accuracy: {report['top_1_accuracy']:.2f}%")
        print(f"Top-5 Accuracy: {report['top_5_accuracy']:.2f}%")
        print(f"Calibration Error: {report['calibration_error']:.4f}")
        print(f"Unique Tokens: {report['token_statistics']['unique_tokens']}")
        print(f"Vocab Coverage: {report['token_statistics']['vocab_coverage']:.2%}")
        
        if save_path:
            import json
            with open(save_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to {save_path}")
        
        return report


if __name__ == "__main__":
    # Example usage
    from config import TINY_CONFIG
    from dataset import TextDataLoader
    
    # Create sample data
    sample_text = "Hello world! " * 100
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(sample_text, verbose=False)
    
    # Create model
    model = LanguageModel(TINY_CONFIG)
    
    # Create evaluator
    evaluator = Evaluator(model, tokenizer, device="cpu")
    
    # Create dataset
    tokens = tokenizer.encode(sample_text)
    data_loader = TextDataLoader(tokenizer, batch_size=4, seq_len=32)
    loader = data_loader.create_dataloader(tokens)
    
    # Compute metrics
    perplexity = evaluator.compute_perplexity(loader)
    print(f"Perplexity: {perplexity:.2f}")
    
    accuracy = evaluator.compute_accuracy(loader)
    print(f"Accuracy: {accuracy:.2f}%")
    
    # Generate full report
    report = evaluator.generate_evaluation_report(loader)
