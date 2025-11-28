"""
Model Configuration for GPT-style Transformer
Optimized for 16GB VRAM (NVIDIA 4060 Ti)
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional
import hashlib


@dataclass
class GPTModelConfig:
    """
    Configuration for GPT-style transformer model.
    
    This configuration is optimized for training on 16GB VRAM.
    Target parameters: 300-500M
    """
    # Architecture
    model_type: str = "gpt_ciaf_v1"
    d_model: int = 1024              # Hidden dimension
    n_layer: int = 20                # Number of transformer layers
    n_head: int = 16                 # Number of attention heads
    dim_ff: int = 4096               # Feed-forward dimension (4x d_model)
    
    # Tokenization
    vocab_size: int = 32768          # Vocabulary size
    max_seq_len: int = 1024          # Maximum sequence length
    
    # Architecture details
    activation: str = "gelu"         # Activation function
    use_rotary: bool = True          # Use rotary positional embeddings
    use_bias: bool = True            # Use bias in linear layers
    dropout: float = 0.1             # Dropout rate
    attention_dropout: float = 0.1   # Attention dropout
    
    # Normalization
    norm_type: str = "layernorm"     # Type of normalization
    norm_eps: float = 1e-5           # Epsilon for normalization
    
    # Initialization
    init_std: float = 0.02           # Standard deviation for weight initialization
    
    # Additional metadata
    version: str = "1.0.0"
    description: str = "GPT-style transformer for SlimPajama-6B pretraining"
    
    def estimate_parameters(self) -> int:
        """
        Estimate the total number of parameters.
        
        Returns:
            Approximate parameter count
        """
        # Embedding parameters
        embed_params = self.vocab_size * self.d_model
        pos_embed_params = self.max_seq_len * self.d_model if not self.use_rotary else 0
        
        # Transformer block parameters (per layer)
        # Attention: Q, K, V projections + output projection
        attn_params = 4 * (self.d_model * self.d_model)
        
        # Feed-forward
        ff_params = 2 * (self.d_model * self.dim_ff)
        
        # Layer norms (2 per layer)
        ln_params = 2 * (2 * self.d_model)
        
        # Per layer total
        per_layer = attn_params + ff_params + ln_params
        
        # All layers
        transformer_params = self.n_layer * per_layer
        
        # Final layer norm + output projection
        output_params = 2 * self.d_model + (self.d_model * self.vocab_size)
        
        total = embed_params + pos_embed_params + transformer_params + output_params
        
        return total
    
    def estimate_memory_gb(self, dtype: str = "float32") -> float:
        """
        Estimate memory requirements in GB.
        
        Args:
            dtype: Data type (float32, float16, bfloat16)
            
        Returns:
            Estimated memory in GB
        """
        params = self.estimate_parameters()
        
        # Bytes per parameter
        bytes_per_param = {
            'float32': 4,
            'float16': 2,
            'bfloat16': 2
        }.get(dtype, 4)
        
        # Model weights
        model_memory = (params * bytes_per_param) / (1024 ** 3)
        
        # Gradients (same size as weights)
        gradient_memory = model_memory
        
        # Optimizer states (Adam: 2x parameters for momentum and variance)
        optimizer_memory = 2 * model_memory
        
        # Activations (rough estimate: depends on batch size and sequence length)
        # Assuming batch_size=4, seq_len=1024
        activation_memory = 0.5  # GB (rough estimate)
        
        total_memory = model_memory + gradient_memory + optimizer_memory + activation_memory
        
        return total_memory
    
    def to_dict(self):
        """Convert config to dictionary."""
        return asdict(self)
    
    def compute_config_hash(self) -> str:
        """
        Compute SHA-256 hash of the configuration.
        
        Returns:
            Hexadecimal hash string
        """
        config_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def save(self, output_path: str):
        """
        Save configuration to JSON file.
        
        Args:
            output_path: Path to output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, input_path: str) -> 'GPTModelConfig':
        """
        Load configuration from JSON file.
        
        Args:
            input_path: Path to input file
            
        Returns:
            GPTModelConfig object
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(**data)


def create_small_config(vocab_size: int = 50257) -> GPTModelConfig:
    """
    Create a small model config (~125M params) for testing.
    Uses GPT2 tokenizer vocab size by default.
    
    Args:
        vocab_size: Vocabulary size (default: 50257 for GPT2)
    
    Returns:
        GPTModelConfig
    """
    return GPTModelConfig(
        d_model=768,
        n_layer=12,
        n_head=12,
        dim_ff=3072,
        vocab_size=vocab_size,
        description="Small GPT for testing (~125M params)"
    )


def create_medium_config(vocab_size: int = 50257) -> GPTModelConfig:
    """
    Create a medium model config (~350M params) for 16GB VRAM.
    Uses GPT2 tokenizer vocab size by default.
    
    Args:
        vocab_size: Vocabulary size (default: 50257 for GPT2)
    
    Returns:
        GPTModelConfig
    """
    return GPTModelConfig(
        d_model=1024,
        n_layer=20,
        n_head=16,
        dim_ff=4096,
        vocab_size=vocab_size,
        description="Medium GPT optimized for 16GB VRAM (~350M params)"
    )


def create_large_config(vocab_size: int = 50257) -> GPTModelConfig:
    """
    Create a larger model config (~760M params) for 16GB VRAM with optimizations.
    Uses GPT2 tokenizer vocab size by default.
    
    Args:
        vocab_size: Vocabulary size (default: 50257 for GPT2)
    
    Returns:
        GPTModelConfig
    """
    return GPTModelConfig(
        d_model=1280,
        n_layer=24,
        n_head=20,
        dim_ff=5120,
        vocab_size=vocab_size,
        description="Large GPT for 16GB VRAM with gradient checkpointing (~760M params)"
    )


if __name__ == "__main__":
    # Create and display model configurations
    configs = {
        'small': create_small_config(),
        'medium': create_medium_config(),
        'large': create_large_config()
    }
    
    print("Model Configuration Analysis")
    print("=" * 80)
    
    for name, config in configs.items():
        params = config.estimate_parameters()
        memory_fp32 = config.estimate_memory_gb('float32')
        memory_fp16 = config.estimate_memory_gb('float16')
        
        print(f"\n{name.upper()} Model:")
        print(f"  d_model: {config.d_model}, n_layer: {config.n_layer}, n_head: {config.n_head}")
        print(f"  Parameters: {params:,} ({params / 1e6:.1f}M)")
        print(f"  Memory (FP32): {memory_fp32:.2f} GB")
        print(f"  Memory (FP16): {memory_fp16:.2f} GB")
        print(f"  Config Hash: {config.compute_config_hash()}")
        
        # Save config
        output_path = f"../config/model_config_{name}.json"
        config.save(output_path)
        print(f"  Saved to: {output_path}")
    
    print("\n" + "=" * 80)
    print("Recommendation: Start with 'medium' config for 16GB VRAM")
    print("Use mixed precision (FP16/BF16) + gradient accumulation for training")
