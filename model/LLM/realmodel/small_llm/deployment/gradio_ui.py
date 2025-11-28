"""
Gradio UI for GPT Model Inference
Simple web interface with CIAF/LCM tracking
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import gradio as gr
except ImportError:
    print("Gradio not installed. Run: pip install gradio")
    sys.exit(1)

import torch
from model.gpt_model import GPTModel
from model.model_config import GPTModelConfig
from ciaf_integration.inference_manager import InferenceManager, create_deployment_anchor


class GradioInferenceApp:
    """Gradio UI for model inference with CIAF tracking."""
    
    def __init__(self):
        self.model: Optional[GPTModel] = None
        self.config: Optional[GPTModelConfig] = None
        self.inference_manager: Optional[InferenceManager] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
    
    def load_model(
        self,
        checkpoint_path: str,
        model_version_anchor_id: str
    ) -> str:
        """Load model from checkpoint."""
        try:
            print(f"Loading model from: {checkpoint_path}")
            
            # Load checkpoint
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Load config
            self.config = GPTModelConfig(**checkpoint['config'])
            
            # Create model
            self.model = GPTModel(self.config)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Create deployment anchor
            deployment = create_deployment_anchor(
                model_version_anchor_id=model_version_anchor_id,
                deployment_config={
                    'device': self.device,
                    'checkpoint_path': checkpoint_path
                },
                output_path="./deployment_anchor.json"
            )
            
            # Create inference manager
            self.inference_manager = InferenceManager(
                deployment_anchor_id=deployment.deployment_id,
                receipts_dir="./inference_receipts"
            )
            
            self.model_loaded = True
            
            return f"✅ Model loaded successfully!\nParameters: {self.model.count_parameters():,}\nDevice: {self.device}"
        
        except Exception as e:
            return f"❌ Error loading model: {str(e)}"
    
    def generate(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.8,
        top_k: int = 50
    ) -> Tuple[str, str]:
        """Generate text from prompt."""
        if not self.model_loaded:
            return "❌ Model not loaded", ""
        
        if not prompt.strip():
            return "❌ Please enter a prompt", ""
        
        try:
            # Placeholder for actual generation
            # In real implementation:
            # 1. Tokenize prompt
            # 2. Generate with model
            # 3. Decode output
            
            generated_text = prompt + "\n\n[Generated text would appear here with actual model inference...]"
            
            # Create inference receipt
            receipt = self.inference_manager.create_inference_receipt(
                input_text=prompt,
                output_text=generated_text,
                generation_params={
                    'max_length': max_length,
                    'temperature': temperature,
                    'top_k': top_k
                }
            )
            
            # Format provenance info
            provenance_info = f"""
📝 Inference Receipt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Receipt ID: {receipt.receipt_id}
Commitment Hash: {receipt.commitment_hash}

Input Hash: {receipt.input_hash}
Output Hash: {receipt.output_hash}

Prompt Length: {receipt.prompt_length} chars
Generation Length: {receipt.generation_length} chars

Compliance Assertions:
{chr(10).join('  ✓ ' + assertion for assertion in receipt.compliance_assertions)}

Timestamp: {receipt.timestamp}
            """.strip()
            
            return generated_text, provenance_info
        
        except Exception as e:
            return f"❌ Error during generation: {str(e)}", ""
    
    def get_statistics(self) -> str:
        """Get inference statistics."""
        if not self.model_loaded or not self.inference_manager:
            return "Model not loaded"
        
        stats = self.inference_manager.get_statistics()
        
        return f"""
📊 Inference Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Inferences: {stats['total_inferences']}
Avg Prompt Length: {stats['avg_prompt_length']:.1f} chars
Avg Generation Length: {stats['avg_generation_length']:.1f} chars
        """.strip()
    
    def create_interface(self) -> gr.Blocks:
        """Create Gradio interface."""
        with gr.Blocks(title="CIAF-LLM Inference") as demo:
            gr.Markdown("# 🤖 CIAF-LLM Inference Interface")
            gr.Markdown("GPT model inference with full CIAF/LCM provenance tracking")
            
            with gr.Tab("🚀 Generate"):
                with gr.Row():
                    with gr.Column(scale=2):
                        prompt_input = gr.Textbox(
                            label="Prompt",
                            placeholder="Enter your prompt here...",
                            lines=5
                        )
                        
                        with gr.Row():
                            max_length_slider = gr.Slider(
                                minimum=10,
                                maximum=500,
                                value=100,
                                step=10,
                                label="Max Length"
                            )
                            temperature_slider = gr.Slider(
                                minimum=0.1,
                                maximum=2.0,
                                value=0.8,
                                step=0.1,
                                label="Temperature"
                            )
                            top_k_slider = gr.Slider(
                                minimum=1,
                                maximum=100,
                                value=50,
                                step=1,
                                label="Top-K"
                            )
                        
                        generate_btn = gr.Button("Generate", variant="primary")
                    
                    with gr.Column(scale=2):
                        output_text = gr.Textbox(
                            label="Generated Text",
                            lines=10
                        )
                        provenance_text = gr.Textbox(
                            label="Provenance Receipt",
                            lines=10
                        )
                
                generate_btn.click(
                    fn=self.generate,
                    inputs=[prompt_input, max_length_slider, temperature_slider, top_k_slider],
                    outputs=[output_text, provenance_text]
                )
            
            with gr.Tab("📊 Statistics"):
                stats_output = gr.Textbox(label="Statistics", lines=10)
                refresh_btn = gr.Button("Refresh Statistics")
                
                refresh_btn.click(
                    fn=self.get_statistics,
                    outputs=stats_output
                )
            
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## About CIAF-LLM
                
                This inference interface demonstrates:
                
                - **Full Provenance Tracking**: Every inference is tracked with cryptographic receipts
                - **CIAF Integration**: Anchors link model versions, data, and training runs
                - **LCM Receipts**: Lightweight consensus mechanism for governance
                - **Compliance**: Built-in compliance assertions and validation
                
                ### Provenance Chain
                
                1. **Data Curation**: SlimPajama-6B filtered with quality heuristics
                2. **Training**: GPT model trained with epoch-level tracking
                3. **Evaluation**: Performance metrics with test anchors
                4. **Deployment**: Model deployed with compliance policies
                5. **Inference**: Each request tracked with commitment hashes
                
                ### Tech Stack
                
                - PyTorch + Custom GPT Implementation
                - CIAF/LCM Framework
                - FastAPI / Gradio UI
                - Cryptographic Anchors & Merkle Trees
                """)
        
        return demo


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Gradio inference UI")
    parser.add_argument("--checkpoint", type=str, help="Path to model checkpoint")
    parser.add_argument("--model-anchor", type=str, help="Model version anchor ID")
    parser.add_argument("--share", action="store_true", help="Create public link")
    
    args = parser.parse_args()
    
    # Create app
    app = GradioInferenceApp()
    
    # Load model if checkpoint provided
    if args.checkpoint and args.model_anchor:
        result = app.load_model(args.checkpoint, args.model_anchor)
        print(result)
    
    # Create and launch interface
    demo = app.create_interface()
    demo.launch(share=args.share)


if __name__ == "__main__":
    main()
