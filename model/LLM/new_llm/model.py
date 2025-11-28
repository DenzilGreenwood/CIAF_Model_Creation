"""
Transformer-based Language Model architecture built from scratch.
Implements multi-head attention, feed-forward networks, and decoder blocks.
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
from config import ModelConfig


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        assert config.d_model % config.n_heads == 0
        
        self.d_model = config.d_model
        self.n_heads = config.n_heads
        self.d_head = config.d_model // config.n_heads
        self.dropout = config.attention_dropout
        
        # Q, K, V projections for all heads (batched)
        self.qkv_proj = nn.Linear(config.d_model, 3 * config.d_model, bias=config.use_bias)
        # Output projection
        self.out_proj = nn.Linear(config.d_model, config.d_model, bias=config.use_bias)
        
        self.attn_dropout = nn.Dropout(config.attention_dropout)
        self.resid_dropout = nn.Dropout(config.residual_dropout)
        
        # Causal mask for autoregressive generation
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(config.max_seq_len, config.max_seq_len))
            .view(1, 1, config.max_seq_len, config.max_seq_len)
        )
    
    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape (batch_size, seq_len, d_model)
            attention_mask: Optional mask of shape (batch_size, seq_len)
        
        Returns:
            Output tensor of shape (batch_size, seq_len, d_model)
        """
        batch_size, seq_len, d_model = x.shape
        
        # Compute Q, K, V for all heads in batch
        qkv = self.qkv_proj(x)  # (B, T, 3 * d_model)
        q, k, v = qkv.chunk(3, dim=-1)  # Each: (B, T, d_model)
        
        # Reshape for multi-head attention
        # (B, T, d_model) -> (B, n_heads, T, d_head)
        q = q.view(batch_size, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        
        # Compute attention scores
        # (B, n_heads, T, d_head) @ (B, n_heads, d_head, T) -> (B, n_heads, T, T)
        attn_scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        
        # Apply causal mask
        attn_scores = attn_scores.masked_fill(
            self.causal_mask[:, :, :seq_len, :seq_len] == 0,
            float('-inf')
        )
        
        # Apply attention mask if provided
        if attention_mask is not None:
            # attention_mask: (B, T) -> (B, 1, 1, T)
            attention_mask = attention_mask.view(batch_size, 1, 1, seq_len)
            attn_scores = attn_scores.masked_fill(attention_mask == 0, float('-inf'))
        
        # Softmax and dropout
        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = self.attn_dropout(attn_weights)
        
        # Apply attention to values
        # (B, n_heads, T, T) @ (B, n_heads, T, d_head) -> (B, n_heads, T, d_head)
        out = attn_weights @ v
        
        # Reshape back to (B, T, d_model)
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)
        
        # Output projection
        out = self.out_proj(out)
        out = self.resid_dropout(out)
        
        return out


class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.fc1 = nn.Linear(config.d_model, config.d_ff, bias=config.use_bias)
        self.fc2 = nn.Linear(config.d_ff, config.d_model, bias=config.use_bias)
        self.dropout = nn.Dropout(config.residual_dropout)
        self.activation = nn.GELU()  # Using GELU activation like GPT-2
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape (batch_size, seq_len, d_model)
        
        Returns:
            Output tensor of shape (batch_size, seq_len, d_model)
        """
        x = self.fc1(x)
        x = self.activation(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class TransformerBlock(nn.Module):
    """Single transformer decoder block."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.attn = MultiHeadAttention(config)
        self.ln2 = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.ffn = FeedForward(config)
    
    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape (batch_size, seq_len, d_model)
            attention_mask: Optional mask of shape (batch_size, seq_len)
        
        Returns:
            Output tensor of shape (batch_size, seq_len, d_model)
        """
        # Pre-norm architecture (like GPT-2)
        # Self-attention with residual connection
        x = x + self.attn(self.ln1(x), attention_mask)
        # Feed-forward with residual connection
        x = x + self.ffn(self.ln2(x))
        return x


class LanguageModel(nn.Module):
    """Transformer-based autoregressive language model."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Token embeddings
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        # Positional embeddings
        self.position_embedding = nn.Embedding(config.max_seq_len, config.d_model)
        self.emb_dropout = nn.Dropout(config.embedding_dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(config) for _ in range(config.n_layers)
        ])
        
        # Final layer norm
        self.ln_f = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        
        # Language modeling head
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        # Weight tying (share embeddings with output layer)
        self.token_embedding.weight = self.lm_head.weight
        
        # Initialize weights
        self.apply(self._init_weights)
        
        # Calculate number of parameters
        n_params = sum(p.numel() for p in self.parameters())
        print(f"Model initialized with {n_params:,} parameters")
    
    def _init_weights(self, module):
        """Initialize weights using scaled initialization."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        targets: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Args:
            input_ids: Token IDs of shape (batch_size, seq_len)
            attention_mask: Optional mask of shape (batch_size, seq_len)
            targets: Optional target token IDs for computing loss
        
        Returns:
            Tuple of (logits, loss)
            - logits: shape (batch_size, seq_len, vocab_size)
            - loss: scalar tensor if targets provided, else None
        """
        batch_size, seq_len = input_ids.shape
        
        # Check sequence length
        assert seq_len <= self.config.max_seq_len, \
            f"Sequence length {seq_len} exceeds maximum {self.config.max_seq_len}"
        
        # Get embeddings
        # Token embeddings
        token_emb = self.token_embedding(input_ids)  # (B, T, d_model)
        
        # Positional embeddings
        positions = torch.arange(0, seq_len, dtype=torch.long, device=input_ids.device)
        position_emb = self.position_embedding(positions)  # (T, d_model)
        
        # Combine embeddings
        x = self.emb_dropout(token_emb + position_emb)
        
        # Pass through transformer blocks
        for block in self.blocks:
            x = block(x, attention_mask)
        
        # Final layer norm
        x = self.ln_f(x)
        
        # Language modeling head
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        # Compute loss if targets provided
        loss = None
        if targets is not None:
            # Flatten for cross entropy
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-100  # Ignore padding tokens
            )
        
        return logits, loss
    
    def get_num_params(self, non_embedding: bool = True) -> int:
        """
        Return the number of parameters in the model.
        
        Args:
            non_embedding: If True, subtract embedding parameters
        """
        n_params = sum(p.numel() for p in self.parameters())
        if non_embedding:
            n_params -= self.position_embedding.weight.numel()
            n_params -= self.token_embedding.weight.numel()
        return n_params


if __name__ == "__main__":
    # Test the model
    from config import TINY_CONFIG
    
    config = TINY_CONFIG
    model = LanguageModel(config)
    
    # Create dummy input
    batch_size = 2
    seq_len = 64
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    targets = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    
    # Forward pass
    logits, loss = model(input_ids, targets=targets)
    
    print(f"Input shape: {input_ids.shape}")
    print(f"Output shape: {logits.shape}")
    print(f"Loss: {loss.item():.4f}")
    print(f"Total parameters: {model.get_num_params():,}")
    print(f"Non-embedding parameters: {model.get_num_params(non_embedding=True):,}")
