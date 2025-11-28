"""
Dataset utilities for loading and preprocessing text data.
"""
import os
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from typing import List, Optional, Iterator
from tokenizer import BPETokenizer


class TextDataset(Dataset):
    """Dataset for text data with tokenization."""
    
    def __init__(
        self,
        data: List[int],
        seq_len: int,
        stride: Optional[int] = None,
    ):
        """
        Initialize text dataset.
        
        Args:
            data: List of token IDs
            seq_len: Length of each sequence
            stride: Stride for creating sequences (default: seq_len)
        """
        self.data = data
        self.seq_len = seq_len
        self.stride = stride if stride is not None else seq_len
        
        # Calculate number of sequences
        self.n_sequences = max(1, (len(data) - seq_len) // self.stride + 1)
    
    def __len__(self) -> int:
        return self.n_sequences
    
    def __getitem__(self, idx: int) -> dict:
        """
        Get a sequence and its target.
        
        Returns:
            Dictionary with 'input_ids' and 'labels'
        """
        start_idx = idx * self.stride
        end_idx = start_idx + self.seq_len + 1
        
        # Handle edge case at the end
        if end_idx > len(self.data):
            end_idx = len(self.data)
            start_idx = max(0, end_idx - self.seq_len - 1)
        
        # Get sequence
        sequence = self.data[start_idx:end_idx]
        
        # Ensure we have at least seq_len + 1 tokens
        if len(sequence) < self.seq_len + 1:
            # Pad with zeros if needed
            sequence = sequence + [0] * (self.seq_len + 1 - len(sequence))
        
        # Input is all tokens except the last one
        input_ids = torch.tensor(sequence[:-1], dtype=torch.long)
        # Target is all tokens except the first one
        labels = torch.tensor(sequence[1:], dtype=torch.long)
        
        return {
            'input_ids': input_ids,
            'labels': labels,
        }


class TextDataLoader:
    """Utility class for loading text data."""
    
    def __init__(
        self,
        tokenizer: BPETokenizer,
        batch_size: int = 8,
        seq_len: int = 1024,
        num_workers: int = 0,
    ):
        """
        Initialize data loader.
        
        Args:
            tokenizer: Tokenizer for encoding text
            batch_size: Batch size for training
            seq_len: Sequence length
            num_workers: Number of workers for data loading
        """
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.num_workers = num_workers
    
    def load_text_file(self, filepath: str) -> List[int]:
        """
        Load and tokenize a text file.
        
        Args:
            filepath: Path to text file
            
        Returns:
            List of token IDs
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        tokens = self.tokenizer.encode(text)
        return tokens
    
    def load_text_files(self, filepaths: List[str]) -> List[int]:
        """
        Load and tokenize multiple text files.
        
        Args:
            filepaths: List of paths to text files
            
        Returns:
            List of token IDs
        """
        all_tokens = []
        for filepath in filepaths:
            tokens = self.load_text_file(filepath)
            all_tokens.extend(tokens)
        return all_tokens
    
    def create_dataloader(
        self,
        tokens: List[int],
        shuffle: bool = True,
        stride: Optional[int] = None,
    ) -> DataLoader:
        """
        Create a PyTorch DataLoader from tokens.
        
        Args:
            tokens: List of token IDs
            shuffle: Whether to shuffle the data
            stride: Stride for creating sequences
            
        Returns:
            PyTorch DataLoader
        """
        dataset = TextDataset(tokens, self.seq_len, stride)
        
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            pin_memory=torch.cuda.is_available(),
        )
        
        return dataloader
    
    def split_data(
        self,
        tokens: List[int],
        train_ratio: float = 0.9,
    ) -> tuple:
        """
        Split tokens into train and validation sets.
        
        Args:
            tokens: List of token IDs
            train_ratio: Ratio of data to use for training
            
        Returns:
            Tuple of (train_tokens, val_tokens)
        """
        n_train = int(len(tokens) * train_ratio)
        train_tokens = tokens[:n_train]
        val_tokens = tokens[n_train:]
        return train_tokens, val_tokens


class MemoryMappedDataset(Dataset):
    """Memory-mapped dataset for large text files."""
    
    def __init__(
        self,
        data_file: str,
        seq_len: int,
        stride: Optional[int] = None,
    ):
        """
        Initialize memory-mapped dataset.
        
        Args:
            data_file: Path to .npy file containing token IDs
            seq_len: Length of each sequence
            stride: Stride for creating sequences
        """
        self.data = np.load(data_file, mmap_mode='r')
        self.seq_len = seq_len
        self.stride = stride if stride is not None else seq_len
        self.n_sequences = max(1, (len(self.data) - seq_len) // self.stride + 1)
    
    def __len__(self) -> int:
        return self.n_sequences
    
    def __getitem__(self, idx: int) -> dict:
        """Get a sequence and its target."""
        start_idx = idx * self.stride
        end_idx = start_idx + self.seq_len + 1
        
        if end_idx > len(self.data):
            end_idx = len(self.data)
            start_idx = max(0, end_idx - self.seq_len - 1)
        
        sequence = self.data[start_idx:end_idx]
        
        if len(sequence) < self.seq_len + 1:
            sequence = np.pad(sequence, (0, self.seq_len + 1 - len(sequence)))
        
        input_ids = torch.from_numpy(sequence[:-1].astype(np.int64))
        labels = torch.from_numpy(sequence[1:].astype(np.int64))
        
        return {
            'input_ids': input_ids,
            'labels': labels,
        }


def save_tokens_to_file(tokens: List[int], filepath: str) -> None:
    """
    Save tokens to a numpy file for memory-mapped access.
    
    Args:
        tokens: List of token IDs
        filepath: Path to save file (.npy)
    """
    tokens_array = np.array(tokens, dtype=np.int32)
    np.save(filepath, tokens_array)
    print(f"Saved {len(tokens):,} tokens to {filepath}")


def load_tokens_from_file(filepath: str) -> List[int]:
    """
    Load tokens from a numpy file.
    
    Args:
        filepath: Path to .npy file
        
    Returns:
        List of token IDs
    """
    tokens_array = np.load(filepath)
    return tokens_array.tolist()


class InfiniteDataLoader:
    """Infinite data loader that cycles through the dataset."""
    
    def __init__(self, dataloader: DataLoader):
        """
        Initialize infinite data loader.
        
        Args:
            dataloader: PyTorch DataLoader to cycle through
        """
        self.dataloader = dataloader
        self.iterator = None
    
    def __iter__(self) -> Iterator:
        return self
    
    def __next__(self) -> dict:
        """Get next batch, cycling through dataset infinitely."""
        if self.iterator is None:
            self.iterator = iter(self.dataloader)
        
        try:
            batch = next(self.iterator)
        except StopIteration:
            # Reset iterator when epoch ends
            self.iterator = iter(self.dataloader)
            batch = next(self.iterator)
        
        return batch


if __name__ == "__main__":
    # Example usage
    from tokenizer import BPETokenizer
    
    # Create sample text
    sample_text = "Hello world! " * 100
    
    # Initialize tokenizer
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(sample_text, verbose=False)
    
    # Tokenize
    tokens = tokenizer.encode(sample_text)
    print(f"Total tokens: {len(tokens)}")
    
    # Create dataset
    dataset = TextDataset(tokens, seq_len=32)
    print(f"Number of sequences: {len(dataset)}")
    
    # Get a sample
    sample = dataset[0]
    print(f"Input shape: {sample['input_ids'].shape}")
    print(f"Label shape: {sample['labels'].shape}")
    
    # Create dataloader
    data_loader = TextDataLoader(tokenizer, batch_size=4, seq_len=32)
    loader = data_loader.create_dataloader(tokens)
    
    # Get a batch
    batch = next(iter(loader))
    print(f"\nBatch input shape: {batch['input_ids'].shape}")
    print(f"Batch label shape: {batch['labels'].shape}")
