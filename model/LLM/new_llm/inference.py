"""
Text generation and inference utilities.
Implements various sampling strategies including greedy, top-k, top-p, and temperature sampling.
"""
import torch
import torch.nn.functional as F
from typing import List, Optional, Callable
from model import LanguageModel
from tokenizer import BPETokenizer


class TextGenerator:
    """Text generation with various sampling strategies."""
    
    def __init__(
        self,
        model: LanguageModel,
        tokenizer: BPETokenizer,
        device: str = "cuda",
    ):
        """
        Initialize text generator.
        
        Args:
            model: Trained language model
            tokenizer: Tokenizer for encoding/decoding
            device: Device to run inference on
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
    
    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        repetition_penalty: float = 1.0,
        stop_tokens: Optional[List[int]] = None,
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_k: Top-k sampling (keep only top k tokens)
            top_p: Nucleus sampling (keep tokens with cumulative probability >= p)
            repetition_penalty: Penalty for repeating tokens (>1 discourages repetition)
            stop_tokens: List of token IDs that end generation
            
        Returns:
            Generated text
        """
        # Encode prompt
        input_ids = self.tokenizer.encode(prompt)
        input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(self.device)
        
        # Track generated tokens for repetition penalty
        generated_tokens = set(input_ids[0].tolist())
        
        # Generate tokens
        for _ in range(max_new_tokens):
            # Check sequence length
            if input_ids.size(1) >= self.model.config.max_seq_len:
                # Truncate from the beginning if too long
                input_ids = input_ids[:, -self.model.config.max_seq_len:]
            
            # Forward pass
            logits, _ = self.model(input_ids)
            
            # Get logits for last token
            logits = logits[:, -1, :]  # (batch_size, vocab_size)
            
            # Apply repetition penalty
            if repetition_penalty != 1.0:
                for token_id in generated_tokens:
                    if token_id < logits.size(-1):
                        logits[0, token_id] /= repetition_penalty
            
            # Apply temperature
            if temperature != 1.0:
                logits = logits / temperature
            
            # Apply top-k sampling
            if top_k is not None:
                logits = self._top_k_filtering(logits, top_k)
            
            # Apply top-p (nucleus) sampling
            if top_p is not None:
                logits = self._top_p_filtering(logits, top_p)
            
            # Sample from distribution
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Check for stop tokens
            if stop_tokens and next_token.item() in stop_tokens:
                break
            
            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)
            generated_tokens.add(next_token.item())
        
        # Decode generated tokens
        generated_ids = input_ids[0].tolist()
        generated_text = self.tokenizer.decode(generated_ids)
        
        return generated_text
    
    @staticmethod
    def _top_k_filtering(logits: torch.Tensor, top_k: int) -> torch.Tensor:
        """
        Filter logits to keep only top-k tokens.
        
        Args:
            logits: Logits tensor of shape (batch_size, vocab_size)
            top_k: Number of top tokens to keep
            
        Returns:
            Filtered logits
        """
        top_k = min(top_k, logits.size(-1))
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = float('-inf')
        return logits
    
    @staticmethod
    def _top_p_filtering(logits: torch.Tensor, top_p: float) -> torch.Tensor:
        """
        Filter logits using nucleus (top-p) sampling.
        
        Args:
            logits: Logits tensor of shape (batch_size, vocab_size)
            top_p: Cumulative probability threshold
            
        Returns:
            Filtered logits
        """
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        
        # Remove tokens with cumulative probability above threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Keep at least one token
        sorted_indices_to_remove[..., 0] = False
        
        # Scatter sorted tensors back to original indexing
        indices_to_remove = sorted_indices_to_remove.scatter(
            -1, sorted_indices, sorted_indices_to_remove
        )
        logits[indices_to_remove] = float('-inf')
        return logits
    
    @torch.no_grad()
    def generate_greedy(self, prompt: str, max_new_tokens: int = 100) -> str:
        """
        Generate text using greedy decoding (always pick most likely token).
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text
        """
        input_ids = self.tokenizer.encode(prompt)
        input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(self.device)
        
        for _ in range(max_new_tokens):
            if input_ids.size(1) >= self.model.config.max_seq_len:
                input_ids = input_ids[:, -self.model.config.max_seq_len:]
            
            logits, _ = self.model(input_ids)
            logits = logits[:, -1, :]
            
            # Pick most likely token
            next_token = torch.argmax(logits, dim=-1, keepdim=True)
            input_ids = torch.cat([input_ids, next_token], dim=1)
        
        generated_ids = input_ids[0].tolist()
        return self.tokenizer.decode(generated_ids)
    
    @torch.no_grad()
    def generate_beam_search(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        beam_size: int = 4,
        length_penalty: float = 1.0,
    ) -> List[str]:
        """
        Generate text using beam search.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            beam_size: Number of beams to maintain
            length_penalty: Penalty for sequence length (>1 favors longer sequences)
            
        Returns:
            List of generated texts (one per beam)
        """
        input_ids = self.tokenizer.encode(prompt)
        input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(self.device)
        
        # Initialize beams: (sequence, score)
        beams = [(input_ids, 0.0)]
        
        for _ in range(max_new_tokens):
            all_candidates = []
            
            for seq, score in beams:
                if seq.size(1) >= self.model.config.max_seq_len:
                    seq = seq[:, -self.model.config.max_seq_len:]
                
                logits, _ = self.model(seq)
                logits = logits[:, -1, :]
                log_probs = F.log_softmax(logits, dim=-1)
                
                # Get top-k tokens
                top_log_probs, top_indices = torch.topk(log_probs, beam_size)
                
                for i in range(beam_size):
                    token = top_indices[0, i].unsqueeze(0).unsqueeze(0)
                    token_score = top_log_probs[0, i].item()
                    new_seq = torch.cat([seq, token], dim=1)
                    
                    # Compute normalized score
                    new_score = score + token_score
                    normalized_score = new_score / (new_seq.size(1) ** length_penalty)
                    
                    all_candidates.append((new_seq, new_score, normalized_score))
            
            # Select top beam_size candidates
            beams = sorted(all_candidates, key=lambda x: x[2], reverse=True)[:beam_size]
            beams = [(seq, score) for seq, score, _ in beams]
        
        # Decode all beams
        results = []
        for seq, _ in beams:
            generated_ids = seq[0].tolist()
            text = self.tokenizer.decode(generated_ids)
            results.append(text)
        
        return results
    
    @torch.no_grad()
    def compute_perplexity(self, text: str) -> float:
        """
        Compute perplexity of the model on given text.
        
        Args:
            text: Text to compute perplexity on
            
        Returns:
            Perplexity value
        """
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) < 2:
            return float('inf')
        
        input_ids = torch.tensor(tokens[:-1], dtype=torch.long).unsqueeze(0).to(self.device)
        targets = torch.tensor(tokens[1:], dtype=torch.long).unsqueeze(0).to(self.device)
        
        # Handle long sequences
        max_len = self.model.config.max_seq_len
        if input_ids.size(1) > max_len:
            input_ids = input_ids[:, :max_len]
            targets = targets[:, :max_len]
        
        _, loss = self.model(input_ids, targets=targets)
        perplexity = torch.exp(loss).item()
        
        return perplexity


if __name__ == "__main__":
    # Example usage
    from config import TINY_CONFIG
    from tokenizer import BPETokenizer
    
    # Create tokenizer and model
    sample_text = "Hello world! " * 100
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(sample_text, verbose=False)
    
    model = LanguageModel(TINY_CONFIG)
    
    # Create generator
    generator = TextGenerator(model, tokenizer, device="cpu")
    
    # Generate text
    prompt = "Hello"
    print(f"Prompt: {prompt}")
    print("\nGreedy generation:")
    print(generator.generate_greedy(prompt, max_new_tokens=20))
    
    print("\nSampling with temperature:")
    print(generator.generate(prompt, max_new_tokens=20, temperature=0.8))
    
    print("\nTop-k sampling:")
    print(generator.generate(prompt, max_new_tokens=20, top_k=10))
    
    print("\nTop-p sampling:")
    print(generator.generate(prompt, max_new_tokens=20, top_p=0.9))
