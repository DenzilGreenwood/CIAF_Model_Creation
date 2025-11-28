"""
Byte Pair Encoding (BPE) Tokenizer implementation from scratch.
Supports training, encoding, and decoding of text.
"""
import json
import regex as re
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional


class BPETokenizer:
    """Byte Pair Encoding tokenizer for language models."""
    
    def __init__(self, vocab_size: int = 50257):
        """
        Initialize the BPE tokenizer.
        
        Args:
            vocab_size: Target vocabulary size (default: 50257 like GPT-2)
        """
        self.vocab_size = vocab_size
        self.encoder: Dict[bytes, int] = {}
        self.decoder: Dict[int, bytes] = {}
        self.bpe_ranks: Dict[Tuple[bytes, bytes], int] = {}
        self.cache: Dict[str, str] = {}
        
        # Pattern for splitting text (handles contractions, punctuation, etc.)
        self.pat = re.compile(
            r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
        )
        
    def train(self, text: str, verbose: bool = True) -> None:
        """
        Train the BPE tokenizer on the given text.
        
        Args:
            text: Training text corpus
            verbose: Whether to print training progress
        """
        # Start with byte-level vocabulary (256 tokens)
        self.encoder = {bytes([i]): i for i in range(256)}
        self.decoder = {i: bytes([i]) for i in range(256)}
        
        # Tokenize text into words
        words = re.findall(self.pat, text)
        word_freqs = Counter(words)
        
        # Convert words to byte sequences
        word_bytes = {}
        for word in word_freqs.keys():
            word_bytes[word] = tuple(word.encode('utf-8'))
        
        # Calculate initial pairs
        def get_pairs(word: Tuple[bytes, ...]) -> set:
            """Get all adjacent pairs in a word."""
            pairs = set()
            prev_byte = word[0]
            for byte in word[1:]:
                pairs.add((prev_byte, byte))
                prev_byte = byte
            return pairs
        
        # Merge pairs until we reach target vocab size
        num_merges = self.vocab_size - 256
        
        for i in range(num_merges):
            # Count pair frequencies
            pair_freqs = defaultdict(int)
            for word, freq in word_freqs.items():
                pairs = get_pairs(word_bytes[word])
                for pair in pairs:
                    pair_freqs[pair] += freq
            
            if not pair_freqs:
                break
            
            # Find most frequent pair
            best_pair = max(pair_freqs, key=pair_freqs.get)
            
            # Add to vocabulary
            new_token = best_pair[0] + best_pair[1]
            new_token_id = len(self.encoder)
            self.encoder[new_token] = new_token_id
            self.decoder[new_token_id] = new_token
            self.bpe_ranks[best_pair] = i
            
            # Merge the pair in all words
            new_word_bytes = {}
            for word, byte_seq in word_bytes.items():
                new_seq = []
                i_byte = 0
                while i_byte < len(byte_seq):
                    if (i_byte < len(byte_seq) - 1 and 
                        (byte_seq[i_byte], byte_seq[i_byte + 1]) == best_pair):
                        new_seq.append(new_token)
                        i_byte += 2
                    else:
                        new_seq.append(byte_seq[i_byte])
                        i_byte += 1
                new_word_bytes[word] = tuple(new_seq)
            word_bytes = new_word_bytes
            
            if verbose and (i + 1) % 100 == 0:
                print(f"Merge {i + 1}/{num_merges}: {best_pair[0]!r} + {best_pair[1]!r} -> {new_token!r}")
        
        if verbose:
            print(f"Training complete! Vocabulary size: {len(self.encoder)}")
    
    def _bpe(self, token: str) -> str:
        """
        Apply BPE merges to a token.
        
        Args:
            token: String token to encode
            
        Returns:
            Space-separated BPE tokens
        """
        if token in self.cache:
            return self.cache[token]
        
        word = tuple(token.encode('utf-8'))
        pairs = self._get_pairs(word)
        
        if not pairs:
            self.cache[token] = token
            return token
        
        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float('inf')))
            if bigram not in self.bpe_ranks:
                break
            
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(first, i)
                    new_word.extend(word[i:j])
                    i = j
                except ValueError:
                    new_word.extend(word[i:])
                    break
                
                if i < len(word) - 1 and word[i] == first and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            
            word = tuple(new_word)
            if len(word) == 1:
                break
            pairs = self._get_pairs(word)
        
        word_str = ' '.join(b.decode('utf-8', errors='replace') for b in word)
        self.cache[token] = word_str
        return word_str
    
    def _get_pairs(self, word: Tuple) -> set:
        """Get all adjacent pairs in a word."""
        pairs = set()
        prev = word[0]
        for item in word[1:]:
            pairs.add((prev, item))
            prev = item
        return pairs
    
    def encode(self, text: str) -> List[int]:
        """
        Encode text into token IDs.
        
        Args:
            text: Text to encode
            
        Returns:
            List of token IDs
        """
        tokens = []
        for token in re.findall(self.pat, text):
            token_bytes = token.encode('utf-8')
            # Apply BPE merges
            bpe_tokens = self._bpe(token)
            for bpe_token in bpe_tokens.split(' '):
                token_id = self.encoder.get(bpe_token.encode('utf-8'))
                if token_id is not None:
                    tokens.append(token_id)
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            Decoded text
        """
        byte_array = bytearray()
        for token_id in token_ids:
            if token_id in self.decoder:
                byte_array.extend(self.decoder[token_id])
        return byte_array.decode('utf-8', errors='replace')
    
    def save(self, filepath: str) -> None:
        """
        Save tokenizer to file.
        
        Args:
            filepath: Path to save the tokenizer
        """
        data = {
            'vocab_size': self.vocab_size,
            'encoder': {k.decode('latin-1'): v for k, v in self.encoder.items()},
            'bpe_ranks': {f"{k[0].decode('latin-1')}|{k[1].decode('latin-1')}": v 
                         for k, v in self.bpe_ranks.items()}
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str) -> None:
        """
        Load tokenizer from file.
        
        Args:
            filepath: Path to load the tokenizer from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.vocab_size = data['vocab_size']
        self.encoder = {k.encode('latin-1'): v for k, v in data['encoder'].items()}
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.bpe_ranks = {
            (k.split('|')[0].encode('latin-1'), k.split('|')[1].encode('latin-1')): v
            for k, v in data['bpe_ranks'].items()
        }
        self.cache = {}


if __name__ == "__main__":
    # Example usage
    sample_text = """
    Hello, world! This is a sample text for training a tokenizer.
    The quick brown fox jumps over the lazy dog.
    Machine learning is fascinating, isn't it?
    """
    
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(sample_text, verbose=True)
    
    # Test encoding/decoding
    test_text = "Hello, world!"
    tokens = tokenizer.encode(test_text)
    decoded = tokenizer.decode(tokens)
    
    print(f"\nOriginal: {test_text}")
    print(f"Tokens: {tokens}")
    print(f"Decoded: {decoded}")
