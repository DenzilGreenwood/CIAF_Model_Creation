"""
Utility functions for the language model.
"""
import os
import random
import numpy as np
import torch
from typing import Optional


def set_seed(seed: int = 42):
    """
    Set random seed for reproducibility.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # Make CUDA operations deterministic
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def count_parameters(model: torch.nn.Module) -> int:
    """
    Count total trainable parameters in a model.
    
    Args:
        model: PyTorch model
        
    Returns:
        Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def format_number(num: int) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return str(num)


def estimate_memory_usage(model: torch.nn.Module, batch_size: int = 1, seq_len: int = 1024) -> dict:
    """
    Estimate memory usage for model training.
    
    Args:
        model: PyTorch model
        batch_size: Training batch size
        seq_len: Sequence length
        
    Returns:
        Dictionary with memory estimates in MB
    """
    # Model parameters
    param_memory = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 ** 2)
    
    # Gradients (same size as parameters)
    grad_memory = param_memory
    
    # Optimizer states (2x for Adam: momentum and variance)
    optimizer_memory = 2 * param_memory
    
    # Activations (rough estimate)
    # Assume average activation size per layer
    d_model = model.config.d_model
    n_layers = model.config.n_layers
    activation_memory = (batch_size * seq_len * d_model * n_layers * 4) / (1024 ** 2)
    
    total_memory = param_memory + grad_memory + optimizer_memory + activation_memory
    
    return {
        'parameters_mb': param_memory,
        'gradients_mb': grad_memory,
        'optimizer_mb': optimizer_memory,
        'activations_mb': activation_memory,
        'total_mb': total_memory,
        'total_gb': total_memory / 1024,
    }


def get_device(prefer_cuda: bool = True) -> torch.device:
    """
    Get the best available device.
    
    Args:
        prefer_cuda: Whether to prefer CUDA if available
        
    Returns:
        PyTorch device
    """
    if prefer_cuda and torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"Using CUDA: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        device = torch.device('cpu')
        print("Using CPU")
    
    return device


def save_text_file(text: str, filepath: str):
    """
    Save text to file.
    
    Args:
        text: Text to save
        filepath: Path to save file
    """
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)


def load_text_file(filepath: str) -> str:
    """
    Load text from file.
    
    Args:
        filepath: Path to file
        
    Returns:
        Loaded text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def create_attention_mask(seq_lengths: torch.Tensor, max_len: int) -> torch.Tensor:
    """
    Create attention mask from sequence lengths.
    
    Args:
        seq_lengths: Tensor of sequence lengths (batch_size,)
        max_len: Maximum sequence length
        
    Returns:
        Attention mask of shape (batch_size, max_len)
    """
    batch_size = seq_lengths.size(0)
    mask = torch.arange(max_len, device=seq_lengths.device).expand(batch_size, max_len)
    mask = mask < seq_lengths.unsqueeze(1)
    return mask


def calculate_eta(elapsed_time: float, current_step: int, total_steps: int) -> str:
    """
    Calculate estimated time remaining.
    
    Args:
        elapsed_time: Time elapsed so far (seconds)
        current_step: Current training step
        total_steps: Total training steps
        
    Returns:
        Formatted ETA string
    """
    if current_step == 0:
        return "N/A"
    
    time_per_step = elapsed_time / current_step
    remaining_steps = total_steps - current_step
    remaining_time = time_per_step * remaining_steps
    
    hours = int(remaining_time // 3600)
    minutes = int((remaining_time % 3600) // 60)
    seconds = int(remaining_time % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class AverageMeter:
    """Computes and stores the average and current value."""
    
    def __init__(self, name: str = "", fmt: str = ":f"):
        self.name = name
        self.fmt = fmt
        self.reset()
    
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
    
    def update(self, val, n: int = 1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
    
    def __str__(self):
        fmtstr = f"{{name}} {{val{self.fmt}}} ({{avg{self.fmt}}})"
        return fmtstr.format(**self.__dict__)


def print_model_summary(model: torch.nn.Module):
    """
    Print a summary of the model architecture.
    
    Args:
        model: PyTorch model
    """
    print("\n" + "=" * 80)
    print("MODEL SUMMARY")
    print("=" * 80)
    
    print(f"\nArchitecture: {model.__class__.__name__}")
    print(f"Total Parameters: {format_number(count_parameters(model))}")
    
    if hasattr(model, 'config'):
        config = model.config
        print(f"\nConfiguration:")
        print(f"  Vocabulary Size: {config.vocab_size:,}")
        print(f"  Max Sequence Length: {config.max_seq_len:,}")
        print(f"  Model Dimension: {config.d_model}")
        print(f"  Number of Layers: {config.n_layers}")
        print(f"  Number of Heads: {config.n_heads}")
        print(f"  Feed-forward Dimension: {config.d_ff}")
        print(f"  Dropout: {config.dropout}")
    
    print("\nLayer-wise Parameters:")
    total_params = 0
    for name, param in model.named_parameters():
        param_count = param.numel()
        total_params += param_count
        if param.requires_grad:
            print(f"  {name:50s} {format_number(param_count):>10s}  {list(param.shape)}")
    
    print(f"\nTotal: {format_number(total_params)}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Example usage
    from model import LanguageModel
    from config import TINY_CONFIG
    
    set_seed(42)
    model = LanguageModel(TINY_CONFIG)
    
    print_model_summary(model)
    
    mem_usage = estimate_memory_usage(model, batch_size=4, seq_len=256)
    print("\nEstimated Memory Usage:")
    for key, value in mem_usage.items():
        print(f"  {key}: {value:.2f}")
