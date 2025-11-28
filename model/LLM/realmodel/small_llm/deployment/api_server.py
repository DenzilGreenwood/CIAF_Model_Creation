"""
FastAPI Inference Server with CIAF/LCM Integration
Serves GPT model with full provenance tracking
"""

import sys
import torch
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

from model.gpt_model import GPTModel
from model.model_config import GPTModelConfig
from ciaf_integration.inference_manager import InferenceManager, create_deployment_anchor


# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 100
    temperature: float = 0.8
    top_k: int = 50


class GenerateResponse(BaseModel):
    generated_text: str
    receipt_id: str
    commitment_hash: str
    prompt_length: int
    generation_length: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    deployment_anchor_id: str


# Initialize FastAPI app
app = FastAPI(
    title="CIAF-LLM Inference API",
    description="GPT model inference with full CIAF/LCM provenance tracking",
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
inference_manager: Optional[InferenceManager] = None
deployment_anchor_id: Optional[str] = None
device: str = "cuda" if torch.cuda.is_available() else "cpu"


def load_model(
    checkpoint_path: str,
    model_version_anchor_id: str
):
    """
    Load model from checkpoint.
    
    Args:
        checkpoint_path: Path to checkpoint file
        model_version_anchor_id: Model version anchor ID
    """
    global model, config, inference_manager, deployment_anchor_id
    
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
    
    print(f"Model loaded: {model.count_parameters():,} parameters")
    
    # Create deployment anchor
    deployment = create_deployment_anchor(
        model_version_anchor_id=model_version_anchor_id,
        deployment_config={
            'device': device,
            'checkpoint_path': checkpoint_path,
            'checkpoint_step': checkpoint.get('global_step', 0)
        },
        output_path="./deployment_anchor.json"
    )
    
    deployment_anchor_id = deployment.deployment_id
    
    # Create inference manager
    inference_manager = InferenceManager(
        deployment_anchor_id=deployment_anchor_id,
        receipts_dir="./inference_receipts"
    )
    
    print(f"Deployment anchor: {deployment_anchor_id}")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "not_ready",
        model_loaded=model is not None,
        deployment_anchor_id=deployment_anchor_id or "not_initialized"
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text from prompt with CIAF/LCM tracking.
    """
    if model is None or inference_manager is None:
        raise HTTPException(status_code=503, error="Model not loaded")
    
    # In a real implementation, you would:
    # 1. Tokenize the prompt
    # 2. Generate with the model
    # 3. Decode the output
    
    # Placeholder implementation
    prompt = request.prompt
    
    # Simulate generation (replace with actual model inference)
    generated_text = prompt + " [Generated text would appear here...]"
    
    # Create inference receipt
    receipt = inference_manager.create_inference_receipt(
        input_text=prompt,
        output_text=generated_text,
        generation_params={
            'max_length': request.max_length,
            'temperature': request.temperature,
            'top_k': request.top_k
        },
        confidence_score=0.85  # Placeholder
    )
    
    return GenerateResponse(
        generated_text=generated_text,
        receipt_id=receipt.receipt_id,
        commitment_hash=receipt.commitment_hash,
        prompt_length=len(prompt),
        generation_length=len(generated_text)
    )


@app.get("/statistics")
async def get_statistics():
    """Get inference statistics."""
    if inference_manager is None:
        raise HTTPException(status_code=503, detail="Inference manager not initialized")
    
    return inference_manager.get_statistics()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CIAF-LLM inference server")
    parser.add_argument("--checkpoint", type=str, required=False, help="Path to model checkpoint")
    parser.add_argument("--model-anchor", type=str, required=False, help="Model version anchor ID")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Load model if checkpoint provided
    if args.checkpoint and args.model_anchor:
        load_model(args.checkpoint, args.model_anchor)
    else:
        print("Warning: Starting server without loading model")
        print("Use --checkpoint and --model-anchor to load a model")
    
    # Run server
    print(f"\nStarting inference server on {args.host}:{args.port}")
    print(f"API documentation: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port)
