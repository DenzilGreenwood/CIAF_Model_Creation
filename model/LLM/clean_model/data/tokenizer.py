"""
Tokenizer Module
Handles tokenization using GPT2 tokenizer from HuggingFace
"""

from typing import List, Union, Optional
import torch
from transformers import GPT2Tokenizer


class SimpleTokenizer:
    """
    Tokenizer wrapper using GPT2 tokenizer.
    """
    
    def __init__(
        self,
        tokenizer_name: str = "gpt2",
        cache_dir: Optional[str] = None
    ):
        """
        Initialize tokenizer.
        
        Args:
            tokenizer_name: HuggingFace tokenizer name (default: gpt2)
            cache_dir: Cache directory for tokenizer files
        """
        print(f"Loading tokenizer: {tokenizer_name}")
        
        # Load GPT2 tokenizer from HuggingFace
        self.tokenizer = GPT2Tokenizer.from_pretrained(
            tokenizer_name,
            cache_dir=cache_dir
        )
        
        # Set padding token (GPT2 doesn't have one by default)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.tokenizer_name = tokenizer_name
        self.vocab_size = len(self.tokenizer)
        
        print(f"✓ Tokenizer loaded")
        print(f"  Vocab size: {self.vocab_size:,}")
        print(f"  PAD token: {self.tokenizer.pad_token} (ID: {self.tokenizer.pad_token_id})")
        print(f"  EOS token: {self.tokenizer.eos_token} (ID: {self.tokenizer.eos_token_id})")
        print(f"  BOS token: {self.tokenizer.bos_token} (ID: {self.tokenizer.bos_token_id})")
    
    def encode(
        self,
        text: Union[str, List[str]],
        max_length: Optional[int] = None,
        padding: bool = False,
        truncation: bool = False,
        return_tensors: Optional[str] = None
    ) -> Union[List[int], torch.Tensor]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text or list of texts
            max_length: Maximum sequence length
            padding: Whether to pad sequences
            truncation: Whether to truncate sequences
            return_tensors: Return type ('pt' for PyTorch tensors)
            
        Returns:
            Token IDs as list or tensor
        """
        encoded = self.tokenizer(
            text,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors=return_tensors
        )
        
        if return_tensors == 'pt':
            return encoded['input_ids']
        elif isinstance(text, str):
            return encoded['input_ids']
        else:
            return encoded['input_ids']
    
    def decode(
        self,
        token_ids: Union[List[int], torch.Tensor],
        skip_special_tokens: bool = True
    ) -> str:
        """
        Decode token IDs to text.
        
        Args:
            token_ids: Token IDs as list or tensor
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            Decoded text
        """
        if isinstance(token_ids, torch.Tensor):
            token_ids = token_ids.tolist()
        
        return self.tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
    
    def batch_encode(
        self,
        texts: List[str],
        max_length: int = 1024,
        padding: bool = True,
        truncation: bool = True
    ) -> torch.Tensor:
        """
        Batch encode texts to token IDs.
        
        Args:
            texts: List of input texts
            max_length: Maximum sequence length
            padding: Whether to pad sequences
            truncation: Whether to truncate sequences
            
        Returns:
            Token IDs tensor (batch_size, seq_len)
        """
        encoded = self.tokenizer(
            texts,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors='pt'
        )
        
        return encoded['input_ids']
    
    def batch_decode(
        self,
        token_ids_batch: torch.Tensor,
        skip_special_tokens: bool = True
    ) -> List[str]:
        """
        Batch decode token IDs to texts.
        
        Args:
            token_ids_batch: Token IDs tensor (batch_size, seq_len)
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            List of decoded texts
        """
        return self.tokenizer.batch_decode(
            token_ids_batch,
            skip_special_tokens=skip_special_tokens
        )
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size."""
        return self.vocab_size
    
    def save_pretrained(self, output_dir: str):
        """Save tokenizer to directory."""
        self.tokenizer.save_pretrained(output_dir)
        print(f"✓ Tokenizer saved to {output_dir}")


def create_tokenizer(tokenizer_name: str = "gpt2") -> SimpleTokenizer:
    """
    Create a tokenizer instance.
    
    Args:
        tokenizer_name: HuggingFace tokenizer name
        
    Returns:
        SimpleTokenizer instance
    """
    return SimpleTokenizer(tokenizer_name=tokenizer_name)


if __name__ == "__main__":
    # Test tokenizer
    print("="*80)
    print("Tokenizer Test")
    print("="*80)
    
    # Create tokenizer
    tokenizer = create_tokenizer(tokenizer_name="gpt2")
    
    # Test encoding
    text = "Hello, world! This is a test of the tokenizer."
    print(f"\nOriginal text: '{text}'")
    
    token_ids = tokenizer.encode(text)
    print(f"Token IDs: {token_ids}")
    print(f"Number of tokens: {len(token_ids)}")
    
    # Test decoding
    decoded = tokenizer.decode(token_ids)
    print(f"Decoded text: '{decoded}'")
    
    # Test batch encoding
    texts = [
        "First example sentence.",
        "Second example with more words.",
        "Third test."
    ]
    print(f"\nBatch encoding {len(texts)} texts...")
    batch_ids = tokenizer.batch_encode(texts, max_length=20, padding=True)
    print(f"Batch shape: {batch_ids.shape}")
    print(f"Batch IDs:\n{batch_ids}")
    
    # Test batch decoding
    decoded_texts = tokenizer.batch_decode(batch_ids)
    print(f"\nDecoded texts:")
    for i, text in enumerate(decoded_texts):
        print(f"  {i+1}. '{text}'")
