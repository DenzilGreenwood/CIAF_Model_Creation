"""
Model deployment utilities for saving, loading, and serving the language model.
"""
import os
import json
import torch
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timezone

from model import LanguageModel
from config import ModelConfig
from tokenizer import BPETokenizer


class ModelDeployment:
    """Utilities for deploying and serving the language model."""
    
    def __init__(self, model_dir: str = "deployed_model"):
        """
        Initialize model deployment.
        
        Args:
            model_dir: Directory to save/load the deployed model
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def save_model(
        self,
        model: LanguageModel,
        tokenizer: BPETokenizer,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save model, tokenizer, and metadata for deployment.
        
        Args:
            model: Trained language model
            tokenizer: Tokenizer
            metadata: Optional metadata about the model
            
        Returns:
            Path to saved model directory
        """
        print(f"Saving model to {self.model_dir}")
        
        # Save model weights
        model_path = self.model_dir / "model.pt"
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': model.config,
        }, model_path)
        print(f"Model saved to {model_path}")
        
        # Save tokenizer
        tokenizer_path = self.model_dir / "tokenizer.json"
        tokenizer.save(str(tokenizer_path))
        print(f"Tokenizer saved to {tokenizer_path}")
        
        # Save metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'saved_at': datetime.now().isoformat(),
            'model_params': model.get_num_params(),
            'vocab_size': model.config.vocab_size,
            'max_seq_len': model.config.max_seq_len,
            'd_model': model.config.d_model,
            'n_layers': model.config.n_layers,
            'n_heads': model.config.n_heads,
        })
        
        metadata_path = self.model_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {metadata_path}")
        
        # Save config as JSON for easy inspection
        config_path = self.model_dir / "config.json"
        config_dict = {
            k: v for k, v in model.config.__dict__.items()
            if not k.startswith('_')
        }
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        print(f"Config saved to {config_path}")
        
        return str(self.model_dir)
    
    def load_model(
        self,
        device: str = "cuda",
    ) -> tuple:
        """
        Load deployed model and tokenizer.
        
        Args:
            device: Device to load model on
            
        Returns:
            Tuple of (model, tokenizer, metadata)
        """
        print(f"Loading model from {self.model_dir}")
        
        # Load model
        model_path = self.model_dir / "model.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        checkpoint = torch.load(model_path, map_location=device)
        config = checkpoint['config']
        
        model = LanguageModel(config)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        model.eval()
        print(f"Model loaded with {model.get_num_params():,} parameters")
        
        # Load tokenizer
        tokenizer_path = self.model_dir / "tokenizer.json"
        if not tokenizer_path.exists():
            raise FileNotFoundError(f"Tokenizer not found at {tokenizer_path}")
        
        tokenizer = BPETokenizer(vocab_size=config.vocab_size)
        tokenizer.load(str(tokenizer_path))
        print(f"Tokenizer loaded with vocab size {len(tokenizer.encoder)}")
        
        # Load metadata
        metadata_path = self.model_dir / "metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        return model, tokenizer, metadata
    
    def export_to_onnx(
        self,
        model: LanguageModel,
        sample_seq_len: int = 128,
        opset_version: int = 14,
    ) -> str:
        """
        Export model to ONNX format for deployment.
        
        Args:
            model: Language model to export
            sample_seq_len: Sample sequence length for tracing
            opset_version: ONNX opset version
            
        Returns:
            Path to exported ONNX model
        """
        try:
            import torch.onnx
        except ImportError:
            raise ImportError("PyTorch ONNX support not available")
        
        onnx_path = self.model_dir / "model.onnx"
        
        # Create dummy input
        dummy_input = torch.randint(
            0, model.config.vocab_size,
            (1, sample_seq_len),
            dtype=torch.long
        )
        
        # Export to ONNX
        model.eval()
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_path),
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=['input_ids'],
            output_names=['logits'],
            dynamic_axes={
                'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                'logits': {0: 'batch_size', 1: 'sequence_length'},
            }
        )
        
        print(f"Model exported to ONNX: {onnx_path}")
        return str(onnx_path)
    
    def quantize_model(
        self,
        model: LanguageModel,
        quantization_type: str = "dynamic",
    ) -> LanguageModel:
        """
        Quantize model for faster inference and smaller size.
        
        Args:
            model: Language model to quantize
            quantization_type: Type of quantization ('dynamic' or 'static')
            
        Returns:
            Quantized model
        """
        try:
            import torch.quantization as quantization
        except ImportError:
            raise ImportError("PyTorch quantization not available")
        
        if quantization_type == "dynamic":
            # Dynamic quantization (post-training, no calibration needed)
            quantized_model = torch.quantization.quantize_dynamic(
                model,
                {torch.nn.Linear},
                dtype=torch.qint8
            )
            print("Model quantized using dynamic quantization")
            
        elif quantization_type == "static":
            # Static quantization (requires calibration data)
            model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
            quantized_model = torch.quantization.prepare(model, inplace=False)
            # Note: User needs to run calibration data through the model here
            quantized_model = torch.quantization.convert(quantized_model, inplace=False)
            print("Model prepared for static quantization (calibration required)")
            
        else:
            raise ValueError(f"Unknown quantization type: {quantization_type}")
        
        # Save quantized model
        quantized_path = self.model_dir / "model_quantized.pt"
        torch.save({
            'model_state_dict': quantized_model.state_dict(),
            'config': model.config,
        }, quantized_path)
        print(f"Quantized model saved to {quantized_path}")
        
        return quantized_model
    
    def create_model_info(self, model: LanguageModel) -> Dict[str, Any]:
        """
        Create comprehensive model information dictionary.
        
        Args:
            model: Language model
            
        Returns:
            Dictionary with model information
        """
        return {
            'architecture': 'Transformer Decoder',
            'total_parameters': model.get_num_params(),
            'trainable_parameters': sum(
                p.numel() for p in model.parameters() if p.requires_grad
            ),
            'non_embedding_parameters': model.get_num_params(non_embedding=True),
            'config': {
                'vocab_size': model.config.vocab_size,
                'max_seq_len': model.config.max_seq_len,
                'd_model': model.config.d_model,
                'n_layers': model.config.n_layers,
                'n_heads': model.config.n_heads,
                'd_ff': model.config.d_ff,
                'dropout': model.config.dropout,
            },
            'memory_footprint_mb': sum(
                p.numel() * p.element_size() for p in model.parameters()
            ) / (1024 ** 2),
        }


class ModelServer:
    """Simple HTTP server for model inference (requires Flask)."""
    
    def __init__(
        self,
        model: LanguageModel,
        tokenizer: BPETokenizer,
        device: str = "cuda",
    ):
        """
        Initialize model server.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            device: Device to run inference on
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Model server initialized on {self.device}")
    
    def predict(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_k: Top-k sampling
            top_p: Top-p sampling
            
        Returns:
            Dictionary with generated text and metadata
        """
        from inference import TextGenerator
        
        generator = TextGenerator(self.model, self.tokenizer, str(self.device))
        
        generated_text = generator.generate(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )
        
        return {
            'prompt': prompt,
            'generated_text': generated_text,
            'num_tokens': len(self.tokenizer.encode(generated_text)),
            'parameters': {
                'max_new_tokens': max_new_tokens,
                'temperature': temperature,
                'top_k': top_k,
                'top_p': top_p,
            }
        }


if __name__ == "__main__":
    # Example usage
    from config import TINY_CONFIG
    
    # Create sample model and tokenizer
    sample_text = "Hello world! " * 100
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(sample_text, verbose=False)
    
    model = LanguageModel(TINY_CONFIG)
    
    # Deploy model
    deployment = ModelDeployment("example_deployment")
    
    # Save model
    deployment.save_model(
        model,
        tokenizer,
        metadata={'description': 'Example tiny model', 'version': '1.0'}
    )
    
    # Load model
    loaded_model, loaded_tokenizer, metadata = deployment.load_model(device="cpu")
    
    print("\nModel Metadata:")
    print(json.dumps(metadata, indent=2))
    
    # Create model info
    info = deployment.create_model_info(loaded_model)
    print("\nModel Info:")
    print(json.dumps(info, indent=2))
