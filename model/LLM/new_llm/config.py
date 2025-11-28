"""
Configuration settings for the LLM.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for the transformer model."""
    
    # Model architecture
    vocab_size: int = 50257  # Size of vocabulary
    max_seq_len: int = 1024  # Maximum sequence length
    d_model: int = 768  # Model dimension (embedding size)
    n_layers: int = 12  # Number of transformer layers
    n_heads: int = 12  # Number of attention heads
    d_ff: int = 3072  # Feed-forward dimension (usually 4 * d_model)
    dropout: float = 0.1  # Dropout probability
    
    # Regularization
    attention_dropout: float = 0.1  # Dropout in attention
    residual_dropout: float = 0.1  # Dropout in residual connections
    embedding_dropout: float = 0.1  # Dropout after embeddings
    
    # Architecture choices
    use_bias: bool = True  # Whether to use bias in linear layers
    layer_norm_eps: float = 1e-5  # Layer normalization epsilon
    
    # Training settings
    learning_rate: float = 3e-4  # Initial learning rate
    weight_decay: float = 0.1  # Weight decay for AdamW
    beta1: float = 0.9  # Adam beta1
    beta2: float = 0.95  # Adam beta2
    grad_clip: float = 1.0  # Gradient clipping threshold
    
    # Learning rate schedule
    warmup_steps: int = 2000  # Number of warmup steps
    max_steps: int = 100000  # Maximum training steps
    lr_decay_steps: int = 100000  # Steps for learning rate decay
    min_lr: float = 3e-5  # Minimum learning rate
    
    # Training logistics
    batch_size: int = 8  # Training batch size
    gradient_accumulation_steps: int = 4  # Steps to accumulate gradients
    
    # Checkpointing
    save_every: int = 1000  # Save checkpoint every N steps
    eval_every: int = 500  # Evaluate every N steps
    
    # Generation settings
    temperature: float = 1.0  # Sampling temperature
    top_k: int = 50  # Top-k sampling
    top_p: float = 0.9  # Nucleus (top-p) sampling
    
    # Device settings
    device: str = "cuda"  # Device to use (cuda/cpu)
    compile_model: bool = False  # Whether to use torch.compile (PyTorch 2.0+)
    
    def __post_init__(self):
        """Validate configuration."""
        assert self.d_model % self.n_heads == 0, \
            f"d_model ({self.d_model}) must be divisible by n_heads ({self.n_heads})"
        assert self.d_ff > self.d_model, \
            f"d_ff ({self.d_ff}) should be larger than d_model ({self.d_model})"
        assert 0 <= self.dropout <= 1, "dropout must be between 0 and 1"
        assert self.learning_rate > 0, "learning_rate must be positive"
        assert self.batch_size > 0, "batch_size must be positive"


# Predefined configurations
GPT2_SMALL_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=1024,
    d_model=768,
    n_layers=12,
    n_heads=12,
    d_ff=3072,
    dropout=0.1,
)

GPT2_MEDIUM_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=1024,
    d_model=1024,
    n_layers=24,
    n_heads=16,
    d_ff=4096,
    dropout=0.1,
)

GPT2_LARGE_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=1024,
    d_model=1280,
    n_layers=36,
    n_heads=20,
    d_ff=5120,
    dropout=0.1,
)

GPT2_XL_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=1024,
    d_model=1600,
    n_layers=48,
    n_heads=25,
    d_ff=6400,
    dropout=0.1,
)

# Smaller config for testing
TINY_CONFIG = ModelConfig(
    vocab_size=1000,
    max_seq_len=256,
    d_model=128,
    n_layers=4,
    n_heads=4,
    d_ff=512,
    dropout=0.1,
    batch_size=4,
)
