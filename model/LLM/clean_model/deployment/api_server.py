"""
FastAPI Inference Server
Serves GPT model for text generation
"""

import sys
import torch
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

from model import GPTModel, GPTModelConfig
from data import SimpleTokenizer


# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 100
    temperature: float = 0.8
    top_k: int = 50


class GenerateResponse(BaseModel):
    generated_text: str
    prompt_length: int
    generation_length: int
    generation_time: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str


class StatsResponse(BaseModel):
    total_requests: int
    total_tokens_generated: int
    avg_generation_time: float


# Initialize FastAPI app
app = FastAPI(
    title="LLM Inference API",
    description="GPT model inference API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
model: Optional[GPTModel] = None
config: Optional[GPTModelConfig] = None
tokenizer: Optional[SimpleTokenizer] = None
device: str = "cuda" if torch.cuda.is_available() else "cpu"

# Statistics
total_requests = 0
total_tokens_generated = 0
total_generation_time = 0.0


def load_model(checkpoint_path: str):
    """
    Load model from checkpoint.
    
    Args:
        checkpoint_path: Path to checkpoint file
    """
    global model, config, tokenizer
    
    print(f"Loading model from: {checkpoint_path}")
    print(f"Device: {device}")
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Load config
    config = GPTModelConfig(**checkpoint['config'])
    
    # Create model
    model = GPTModel(config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    # Load tokenizer
    tokenizer = SimpleTokenizer(tokenizer_name="gpt2")
    
    print(f"Model loaded: {model.count_parameters():,} parameters")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "not_ready",
        model_loaded=model is not None,
        device=device
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text from prompt.
    """
    global total_requests, total_tokens_generated, total_generation_time
    
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Tokenize prompt
        input_ids = tokenizer.encode(
            request.prompt,
            return_tensors='pt'
        ).to(device)
        
        prompt_length = input_ids.size(1)
        
        # Generate
        with torch.no_grad():
            for _ in range(request.max_length):
                # Forward pass
                logits = model(input_ids)
                
                # Get next token logits
                next_token_logits = logits[:, -1, :] / request.temperature
                
                # Top-k sampling
                if request.top_k > 0:
                    top_k_values, top_k_indices = torch.topk(next_token_logits, request.top_k)
                    next_token_logits = torch.full_like(next_token_logits, float('-inf'))
                    next_token_logits.scatter_(1, top_k_indices, top_k_values)
                
                # Sample next token
                probs = torch.nn.functional.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append to input
                input_ids = torch.cat([input_ids, next_token], dim=1)
                
                # Check for EOS
                if next_token.item() == tokenizer.tokenizer.eos_token_id:
                    break
        
        # Decode
        generated_text = tokenizer.decode(input_ids[0])
        generation_length = input_ids.size(1) - prompt_length
        
        # Record stats
        generation_time = time.time() - start_time
        total_requests += 1
        total_tokens_generated += generation_length
        total_generation_time += generation_time
        
        return GenerateResponse(
            generated_text=generated_text,
            prompt_length=prompt_length,
            generation_length=generation_length,
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/statistics", response_model=StatsResponse)
async def get_statistics():
    """Get inference statistics."""
    avg_time = total_generation_time / total_requests if total_requests > 0 else 0.0
    
    return StatsResponse(
        total_requests=total_requests,
        total_tokens_generated=total_tokens_generated,
        avg_generation_time=avg_time
    )


def start_server(
    checkpoint_path: str,
    host: str = "0.0.0.0",
    port: int = 8000
):
    """
    Start the API server.
    
    Args:
        checkpoint_path: Path to model checkpoint
        host: Server host
        port: Server port
    """
    # Load model
    load_model(checkpoint_path)
    
    # Start server
    print(f"\nStarting server on {host}:{port}")
    print(f"API docs available at http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start LLM inference API server")
    parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Path to model checkpoint"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    start_server(
        checkpoint_path=args.checkpoint,
        host=args.host,
        port=args.port
    )
