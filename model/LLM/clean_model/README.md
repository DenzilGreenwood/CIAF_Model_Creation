# Clean GPT Language Model

A streamlined GPT-style transformer implementation without CIAF/LCM integration.

## Overview

This is a clean, production-ready GPT language model implementation optimized for:
- Training on 16GB VRAM (NVIDIA 4060 Ti)
- SlimPajama-6B dataset pretraining
- Decoder-only transformer with rotary embeddings
- ~350M parameters (medium config)

## Project Structure

```
clean_model/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── model/                 # Model architecture
│   ├── gpt_model.py      # GPT transformer implementation
│   └── model_config.py   # Model configurations
├── data/                  # Data loading
│   ├── data_loader.py    # Dataset loader
│   ├── data_curator.py   # Data curation
│   └── tokenizer.py      # Tokenization
├── training/              # Training scripts
│   └── train.py          # Main training script
├── evaluation/            # Evaluation
│   └── evaluate.py       # Evaluation harness
└── deployment/            # Inference serving
    ├── api_server.py     # FastAPI server
    └── gradio_ui.py      # Gradio interface
```

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Training

```bash
python training/train.py \
    --model-config medium \
    --dataset DKYoon/SlimPajama-6B \
    --batch-size 4 \
    --learning-rate 1e-4 \
    --output-dir ./checkpoints
```

### Evaluation

```bash
python evaluation/evaluate.py \
    --checkpoint ./checkpoints/model.pt \
    --test-dataset validation_data
```

### Inference Server

```bash
python deployment/api_server.py \
    --checkpoint ./checkpoints/model.pt \
    --host 0.0.0.0 \
    --port 8000
```

## Model Configurations

### Small (~125M params)
- d_model: 768
- n_layer: 12
- n_head: 12
- Good for testing and experimentation

### Medium (~350M params) - Recommended
- d_model: 1024
- n_layer: 20
- n_head: 16
- Optimized for 16GB VRAM

### Large (~760M params)
- d_model: 1280
- n_layer: 24
- n_head: 20
- Requires gradient checkpointing on 16GB VRAM

## Features

- **Rotary Positional Embeddings (RoPE)**: Better length generalization
- **Pre-norm Architecture**: Improved training stability
- **Flexible Configurations**: Easy to customize model size
- **Streaming Dataset Support**: Handle large datasets efficiently
- **Mixed Precision Training**: FP16/BF16 support
- **Gradient Accumulation**: Train larger batches on limited VRAM

## Training Tips

1. **Memory Optimization**:
   - Use mixed precision (FP16/BF16)
   - Enable gradient accumulation
   - Consider gradient checkpointing for larger models

2. **Learning Rate**:
   - Start with 1e-4 for medium model
   - Use warmup (1000-2000 steps)
   - Cosine decay schedule

3. **Batch Size**:
   - Effective batch size: ~500K tokens
   - Micro batch: 4-8 samples
   - Gradient accumulation: 32-64 steps

## Performance Benchmarks

On NVIDIA RTX 4060 Ti (16GB):
- Training speed: ~50K tokens/sec (medium model, FP16)
- Memory usage: ~14GB (with grad accumulation)
- Checkpoint size: ~1.4GB (medium model)

## License

This code follows standard open-source practices. See LICENSE file for details.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

## Support

For issues or questions, refer to the documentation or open an issue.
