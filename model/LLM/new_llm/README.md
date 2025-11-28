# Language Model from Scratch

A complete implementation of a transformer-based language model built from scratch using PyTorch. This project includes everything needed to train, evaluate, and deploy a GPT-style autoregressive language model.

## Features

- **Custom BPE Tokenizer**: Byte Pair Encoding tokenizer with training capabilities
- **Transformer Architecture**: Multi-head attention, feed-forward networks, and layer normalization
- **Training Pipeline**: Complete training loop with learning rate scheduling, gradient clipping, and checkpointing
- **Text Generation**: Multiple sampling strategies (greedy, top-k, top-p, temperature, beam search)
- **Evaluation Metrics**: Perplexity, accuracy, BLEU score, calibration error
- **Model Deployment**: Save/load utilities, ONNX export, quantization support
- **CLI Interface**: Easy-to-use command-line tools

## Project Structure

```
new_llm/
├── config.py           # Model configuration and hyperparameters
├── model.py            # Transformer model architecture
├── tokenizer.py        # BPE tokenizer implementation
├── dataset.py          # Data loading and preprocessing
├── trainer.py          # Training loop and optimization
├── inference.py        # Text generation with various sampling strategies
├── evaluation.py       # Evaluation metrics (perplexity, BLEU, etc.)
├── deployment.py       # Model saving/loading and deployment utilities
├── utils.py            # Helper functions
├── main.py             # Command-line interface
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- torch >= 2.0.0
- numpy >= 1.20.0
- regex >= 2021.0.0

## Quick Start

### 1. Train a Tokenizer

```bash
python main.py train-tokenizer --data-file data.txt --vocab-size 10000 --output tokenizer.json
```

### 2. Train a Model

```bash
python main.py train \
    --data-file data.txt \
    --tokenizer tokenizer.json \
    --config small \
    --batch-size 8 \
    --max-steps 10000 \
    --output-dir checkpoints
```

### 3. Generate Text

```bash
python main.py generate \
    --model-dir checkpoints \
    --prompt "Once upon a time" \
    --max-tokens 100 \
    --temperature 0.8 \
    --top-k 50
```

### 4. Evaluate a Model

```bash
python main.py evaluate \
    --model-dir checkpoints \
    --data-file test_data.txt \
    --output evaluation_report.json
```

## Usage Examples

### Training from Python

```python
from config import GPT2_SMALL_CONFIG
from model import LanguageModel
from tokenizer import BPETokenizer
from dataset import TextDataLoader
from trainer import Trainer

# Load data
with open('data.txt', 'r') as f:
    text = f.read()

# Train tokenizer
tokenizer = BPETokenizer(vocab_size=10000)
tokenizer.train(text)

# Prepare data
tokens = tokenizer.encode(text)
data_loader = TextDataLoader(tokenizer, batch_size=8, seq_len=512)
train_loader = data_loader.create_dataloader(tokens)

# Create and train model
config = GPT2_SMALL_CONFIG
model = LanguageModel(config)
trainer = Trainer(model, config, train_loader)
trainer.train(max_steps=10000)
```

### Text Generation from Python

```python
from inference import TextGenerator
from deployment import ModelDeployment

# Load model
deployment = ModelDeployment('checkpoints')
model, tokenizer, metadata = deployment.load_model()

# Generate text
generator = TextGenerator(model, tokenizer)
text = generator.generate(
    prompt="Hello world",
    max_new_tokens=100,
    temperature=0.8,
    top_k=50,
    top_p=0.9
)
print(text)
```

### Model Evaluation

```python
from evaluation import Evaluator

# Create evaluator
evaluator = Evaluator(model, tokenizer)

# Compute metrics
perplexity = evaluator.compute_perplexity(eval_loader)
accuracy = evaluator.compute_accuracy(eval_loader)

# Generate full report
report = evaluator.generate_evaluation_report(eval_loader)
```

## Model Configurations

Several pre-configured model sizes are available:

- **TINY_CONFIG**: 4 layers, 128 hidden size (for testing)
- **GPT2_SMALL_CONFIG**: 12 layers, 768 hidden size (~117M parameters)
- **GPT2_MEDIUM_CONFIG**: 24 layers, 1024 hidden size (~345M parameters)
- **GPT2_LARGE_CONFIG**: 36 layers, 1280 hidden size (~774M parameters)
- **GPT2_XL_CONFIG**: 48 layers, 1600 hidden size (~1.5B parameters)

## Architecture Details

### Transformer Model
- **Multi-head Self-Attention**: Causal masking for autoregressive generation
- **Position-wise Feed-Forward**: GELU activation
- **Layer Normalization**: Pre-norm architecture (like GPT-2)
- **Residual Connections**: Around attention and feed-forward layers
- **Weight Tying**: Shared embeddings between input and output layers

### Training Features
- **AdamW Optimizer**: With weight decay and separate decay/no-decay groups
- **Learning Rate Schedule**: Linear warmup + cosine decay
- **Gradient Clipping**: Prevents gradient explosion
- **Mixed Precision**: Support for automatic mixed precision (AMP)
- **Checkpointing**: Regular model checkpoints with best model tracking

### Generation Strategies
- **Greedy Decoding**: Always pick most likely token
- **Temperature Sampling**: Control randomness in generation
- **Top-k Sampling**: Sample from top k most likely tokens
- **Top-p (Nucleus) Sampling**: Sample from smallest set with cumulative probability ≥ p
- **Beam Search**: Maintain multiple hypotheses during generation
- **Repetition Penalty**: Discourage repetitive text

## Performance Optimization

### Memory Efficiency
- Gradient accumulation for large effective batch sizes
- Memory-mapped datasets for large corpora
- Efficient attention implementation

### Speed Optimization
- PyTorch 2.0 `torch.compile()` support
- Multi-worker data loading
- CUDA kernel optimizations

### Model Compression
- Dynamic quantization (INT8)
- ONNX export for deployment
- Model pruning support

## Evaluation Metrics

- **Perplexity**: Primary metric for language modeling
- **Accuracy**: Top-1 and top-k prediction accuracy
- **BLEU Score**: For comparing generated text to references
- **Calibration Error**: Model confidence calibration
- **Token Statistics**: Vocabulary coverage and frequency analysis

## Deployment

### Save Model for Production

```python
from deployment import ModelDeployment

deployment = ModelDeployment('production_model')
deployment.save_model(model, tokenizer, metadata={
    'version': '1.0',
    'description': 'Production language model'
})
```

### Export to ONNX

```python
deployment.export_to_onnx(model, sample_seq_len=128)
```

### Quantize Model

```python
quantized_model = deployment.quantize_model(model, quantization_type='dynamic')
```

## Contributing

This is a complete, self-contained implementation designed for learning and experimentation. Feel free to modify and extend for your needs.

## License

This implementation is provided as-is for educational purposes.

## References

- Vaswani et al. (2017): "Attention Is All You Need"
- Radford et al. (2019): "Language Models are Unsupervised Multitask Learners" (GPT-2)
- Sennrich et al. (2016): "Neural Machine Translation of Rare Words with Subword Units" (BPE)

## Acknowledgments

Built from scratch to demonstrate core concepts in modern language model training and deployment.
