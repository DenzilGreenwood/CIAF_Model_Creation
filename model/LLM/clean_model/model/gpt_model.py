"""
GPT-style Transformer Architecture
Implementation of decoder-only transformer with rotary embeddings
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class RotaryPositionalEmbedding(nn.Module):
    """
    Rotary Positional Embeddings (RoPE) from "RoFormer: Enhanced Transformer with Rotary Position Embedding"
    """
    
    def __init__(self, dim: int, max_seq_len: int = 2048, base: int = 10000):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len
        self.base = base
        
        # Precompute frequencies
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer('inv_freq', inv_freq)
        
        # Cache for efficiency
        self._seq_len_cached = None
        self._cos_cached = None
        self._sin_cached = None
    
    def _update_cache(self, seq_len: int, device: torch.device):
        """Update cached cos and sin values."""
        if seq_len != self._seq_len_cached:
            self._seq_len_cached = seq_len
            t = torch.arange(seq_len, device=device).type_as(self.inv_freq)
            freqs = torch.einsum('i,j->ij', t, self.inv_freq)
            # Don't concatenate - freqs is already (seq_len, dim/2)
            # We'll duplicate for each half during rotation
            emb = torch.cat((freqs, freqs), dim=-1)  # (seq_len, dim)
            self._cos_cached = emb.cos()
            self._sin_cached = emb.sin()
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: Input tensor of shape (batch, seq_len, dim)
            
        Returns:
            Tuple of (cos, sin) tensors
        """
        seq_len = x.shape[1]
        self._update_cache(seq_len, x.device)
        return self._cos_cached[:seq_len], self._sin_cached[:seq_len]


def apply_rotary_emb(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """
    Apply rotary embeddings to input tensor.
    
    Args:
        x: Input tensor (batch, seq_len, n_head, head_dim)
        cos: Cosine values (seq_len, head_dim)
        sin: Sine values (seq_len, head_dim)
        
    Returns:
        Tensor with rotary embeddings applied
    """
    # Reshape cos/sin to match x dimensions: (1, seq_len, 1, head_dim)
    # Need to slice to match head_dim if cos/sin are larger
    head_dim = x.shape[-1]
    cos = cos[..., :head_dim].unsqueeze(0).unsqueeze(2)  # (1, seq_len, 1, head_dim)
    sin = sin[..., :head_dim].unsqueeze(0).unsqueeze(2)  # (1, seq_len, 1, head_dim)
    
    # Split into two halves
    x1, x2 = x.chunk(2, dim=-1)
    
    # Apply rotation
    return torch.cat([
        x1 * cos[..., :head_dim//2] - x2 * sin[..., :head_dim//2],
        x2 * cos[..., head_dim//2:] + x1 * sin[..., head_dim//2:]
    ], dim=-1)


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention with optional rotary embeddings."""
    
    def __init__(
        self,
        d_model: int,
        n_head: int,
        dropout: float = 0.1,
        use_bias: bool = True,
        use_rotary: bool = True,
        max_seq_len: int = 2048
    ):
        super().__init__()
        assert d_model % n_head == 0, "d_model must be divisible by n_head"
        
        self.d_model = d_model
        self.n_head = n_head
        self.head_dim = d_model // n_head
        self.use_rotary = use_rotary
        
        # Q, K, V projections
        self.q_proj = nn.Linear(d_model, d_model, bias=use_bias)
        self.k_proj = nn.Linear(d_model, d_model, bias=use_bias)
        self.v_proj = nn.Linear(d_model, d_model, bias=use_bias)
        
        # Output projection
        self.out_proj = nn.Linear(d_model, d_model, bias=use_bias)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Rotary embeddings
        if use_rotary:
            self.rotary_emb = RotaryPositionalEmbedding(self.head_dim, max_seq_len)
        else:
            self.rotary_emb = None
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            x: Input tensor (batch, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Output tensor (batch, seq_len, d_model)
        """
        batch_size, seq_len, _ = x.shape
        
        # Project Q, K, V
        q = self.q_proj(x).view(batch_size, seq_len, self.n_head, self.head_dim)
        k = self.k_proj(x).view(batch_size, seq_len, self.n_head, self.head_dim)
        v = self.v_proj(x).view(batch_size, seq_len, self.n_head, self.head_dim)
        
        # Apply rotary embeddings if enabled
        if self.use_rotary:
            cos, sin = self.rotary_emb(x)
            q = apply_rotary_emb(q, cos, sin)
            k = apply_rotary_emb(k, cos, sin)
        
        # Transpose for attention computation: (batch, n_head, seq_len, head_dim)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        
        # Scaled dot-product attention
        scale = 1.0 / math.sqrt(self.head_dim)
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) * scale
        
        # Apply mask if provided
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))
        
        attn_probs = F.softmax(attn_scores, dim=-1)
        attn_probs = self.dropout(attn_probs)
        
        # Apply attention to values
        out = torch.matmul(attn_probs, v)
        
        # Reshape and project output
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        out = self.out_proj(out)
        
        return out


class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(
        self,
        d_model: int,
        dim_ff: int,
        dropout: float = 0.1,
        activation: str = "gelu",
        use_bias: bool = True
    ):
        super().__init__()
        self.fc1 = nn.Linear(d_model, dim_ff, bias=use_bias)
        self.fc2 = nn.Linear(dim_ff, d_model, bias=use_bias)
        self.dropout = nn.Dropout(dropout)
        
        # Activation function
        if activation == "gelu":
            self.activation = nn.GELU()
        elif activation == "relu":
            self.activation = nn.ReLU()
        elif activation == "swish":
            self.activation = nn.SiLU()
        else:
            raise ValueError(f"Unknown activation: {activation}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (batch, seq_len, d_model)
            
        Returns:
            Output tensor (batch, seq_len, d_model)
        """
        x = self.fc1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class TransformerBlock(nn.Module):
    """Single transformer decoder block."""
    
    def __init__(
        self,
        d_model: int,
        n_head: int,
        dim_ff: int,
        dropout: float = 0.1,
        attention_dropout: float = 0.1,
        activation: str = "gelu",
        use_bias: bool = True,
        use_rotary: bool = True,
        max_seq_len: int = 2048,
        norm_eps: float = 1e-5
    ):
        super().__init__()
        
        # Attention
        self.attention = MultiHeadAttention(
            d_model, n_head, attention_dropout, use_bias, use_rotary, max_seq_len
        )
        
        # Feed-forward
        self.feed_forward = FeedForward(
            d_model, dim_ff, dropout, activation, use_bias
        )
        
        # Layer norms
        self.ln1 = nn.LayerNorm(d_model, eps=norm_eps)
        self.ln2 = nn.LayerNorm(d_model, eps=norm_eps)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            x: Input tensor (batch, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Output tensor (batch, seq_len, d_model)
        """
        # Pre-norm architecture
        # Attention block with residual
        residual = x
        x = self.ln1(x)
        x = self.attention(x, mask)
        x = self.dropout(x)
        x = residual + x
        
        # Feed-forward block with residual
        residual = x
        x = self.ln2(x)
        x = self.feed_forward(x)
        x = self.dropout(x)
        x = residual + x
        
        return x


class GPTModel(nn.Module):
    """GPT-style transformer language model."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Token embeddings
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        
        # Positional embeddings (if not using rotary)
        if not config.use_rotary:
            self.position_embedding = nn.Embedding(config.max_seq_len, config.d_model)
        else:
            self.position_embedding = None
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(
                d_model=config.d_model,
                n_head=config.n_head,
                dim_ff=config.dim_ff,
                dropout=config.dropout,
                attention_dropout=config.attention_dropout,
                activation=config.activation,
                use_bias=config.use_bias,
                use_rotary=config.use_rotary,
                max_seq_len=config.max_seq_len,
                norm_eps=config.norm_eps
            )
            for _ in range(config.n_layer)
        ])
        
        # Final layer norm
        self.ln_f = nn.LayerNorm(config.d_model, eps=config.norm_eps)
        
        # Output projection (language modeling head)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        # Tie weights (share embeddings with output)
        self.lm_head.weight = self.token_embedding.weight
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize weights."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=self.config.init_std)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=self.config.init_std)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.ones_(module.weight)
            torch.nn.init.zeros_(module.bias)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Args:
            input_ids: Input token IDs (batch, seq_len)
            labels: Optional labels for language modeling loss
            
        Returns:
            Tuple of (logits, loss)
        """
        batch_size, seq_len = input_ids.shape
        
        # Token embeddings
        x = self.token_embedding(input_ids)
        
        # Add positional embeddings if not using rotary
        if self.position_embedding is not None:
            positions = torch.arange(0, seq_len, device=input_ids.device).unsqueeze(0)
            x = x + self.position_embedding(positions)
        
        # Create causal mask
        mask = torch.tril(torch.ones(seq_len, seq_len, device=input_ids.device)).view(
            1, 1, seq_len, seq_len
        )
        
        # Apply transformer blocks
        for block in self.blocks:
            x = block(x, mask)
        
        # Final layer norm
        x = self.ln_f(x)
        
        # Language modeling head
        logits = self.lm_head(x)
        
        # Compute loss if labels provided
        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            
            # Compute cross-entropy loss
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100
            )
        
        return logits, loss
    
    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


if __name__ == "__main__":
    from model_config import create_medium_config
    
    # Create model
    config = create_medium_config()
    model = GPTModel(config)
    
    print("GPT Model Architecture")
    print("=" * 60)
    print(f"Configuration: {config.description}")
    print(f"Parameters: {model.count_parameters():,}")
    print(f"Expected: ~{config.estimate_parameters():,}")
    
    # Test forward pass
    batch_size = 2
    seq_len = 128
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    
    print(f"\nTest forward pass:")
    print(f"  Input shape: {input_ids.shape}")
    
    with torch.no_grad():
        logits, loss = model(input_ids, labels=input_ids)
    
    print(f"  Output logits shape: {logits.shape}")
    print(f"  Memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB" if torch.cuda.is_available() else "  CPU mode")
