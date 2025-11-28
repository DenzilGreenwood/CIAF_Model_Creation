"""
Data Loading Module for SlimPajama-6B Dataset
Handles streaming and loading of the SlimPajama-6B dataset with CIAF/LCM integration
"""

from datasets import load_dataset
from typing import Iterator, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlimPajamaLoader:
    """
    Loader for SlimPajama-6B dataset with streaming support.
    
    Dataset info:
    - ~5.5M train rows
    - ~24GB decompressed
    - Sources: CommonCrawl, C4, GitHub, books, arXiv, Wikipedia, StackExchange
    
    Reference: https://huggingface.co/datasets/DKYoon/SlimPajama-6B
    """
    
    def __init__(
        self,
        dataset_name: str = "DKYoon/SlimPajama-6B",
        split: str = "train",
        streaming: bool = True
    ):
        """
        Initialize the SlimPajama loader.
        
        Args:
            dataset_name: HuggingFace dataset identifier
            split: Dataset split to load (default: "train")
            streaming: Whether to stream the dataset (recommended for large datasets)
        """
        self.dataset_name = dataset_name
        self.split = split
        self.streaming = streaming
        self.dataset = None
        
    def load(self) -> Any:
        """
        Load the dataset from HuggingFace.
        
        Returns:
            Dataset or IterableDataset
        """
        logger.info(f"Loading {self.dataset_name} ({self.split}) with streaming={self.streaming}")
        
        self.dataset = load_dataset(
            self.dataset_name,
            split=self.split,
            streaming=self.streaming
        )
        
        logger.info("Dataset loaded successfully")
        return self.dataset
    
    def stream_samples(self, max_samples: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """
        Stream samples from the dataset.
        
        Args:
            max_samples: Maximum number of samples to stream (None = all)
            
        Yields:
            Dictionary containing sample data with keys like 'text', 'meta', etc.
        """
        if self.dataset is None:
            self.load()
        
        count = 0
        for sample in self.dataset:
            yield sample
            count += 1
            
            if max_samples and count >= max_samples:
                break
            
            if count % 10000 == 0:
                logger.info(f"Streamed {count} samples")
    
    def get_sample_info(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from a sample.
        
        Args:
            sample: Dataset sample
            
        Returns:
            Dictionary with sample information
        """
        info = {
            'text_length': len(sample.get('text', '')),
            'has_meta': 'meta' in sample,
        }
        
        if 'meta' in sample and sample['meta']:
            meta = sample['meta']
            if isinstance(meta, dict):
                info['source'] = meta.get('redpajama_set_name', 'unknown')
            else:
                info['source'] = 'unknown'
        else:
            info['source'] = 'unknown'
            
        return info


if __name__ == "__main__":
    # Example usage
    loader = SlimPajamaLoader(streaming=True)
    
    print("Loading SlimPajama-6B dataset...")
    loader.load()
    
    print("\nStreaming first 5 samples:")
    for idx, sample in enumerate(loader.stream_samples(max_samples=5)):
        info = loader.get_sample_info(sample)
        print(f"\nSample {idx + 1}:")
        print(f"  Text length: {info['text_length']} chars")
        print(f"  Source: {info['source']}")
        print(f"  Preview: {sample['text'][:100]}...")
