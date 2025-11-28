"""
Command-line interface for training, evaluating, and generating text with the LLM.
"""
import argparse
import sys
import torch
from pathlib import Path

from config import ModelConfig, GPT2_SMALL_CONFIG, TINY_CONFIG
from model import LanguageModel
from tokenizer import BPETokenizer
from dataset import TextDataLoader, save_tokens_to_file, load_tokens_from_file
from trainer import Trainer
from inference import TextGenerator
from evaluation import Evaluator
from deployment import ModelDeployment


def train_tokenizer(args):
    """Train a new tokenizer."""
    print(f"Training tokenizer on {args.data_file}")
    
    # Load training data
    with open(args.data_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Loaded {len(text):,} characters")
    
    # Train tokenizer
    tokenizer = BPETokenizer(vocab_size=args.vocab_size)
    tokenizer.train(text, verbose=True)
    
    # Save tokenizer
    tokenizer.save(args.output)
    print(f"Tokenizer saved to {args.output}")


def train_model(args):
    """Train a language model."""
    print("Starting model training...")
    
    # Load tokenizer
    tokenizer = BPETokenizer(vocab_size=args.vocab_size)
    if Path(args.tokenizer).exists():
        tokenizer.load(args.tokenizer)
        print(f"Loaded tokenizer from {args.tokenizer}")
    else:
        print("Training new tokenizer...")
        with open(args.data_file, 'r', encoding='utf-8') as f:
            text = f.read()
        tokenizer.train(text, verbose=True)
        tokenizer.save(args.tokenizer)
    
    # Load and tokenize data
    print("Loading training data...")
    if args.data_file.endswith('.npy'):
        tokens = load_tokens_from_file(args.data_file)
    else:
        with open(args.data_file, 'r', encoding='utf-8') as f:
            text = f.read()
        tokens = tokenizer.encode(text)
    
    print(f"Total tokens: {len(tokens):,}")
    
    # Split data
    data_loader = TextDataLoader(
        tokenizer,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
    )
    train_tokens, val_tokens = data_loader.split_data(tokens, train_ratio=0.9)
    
    print(f"Training tokens: {len(train_tokens):,}")
    print(f"Validation tokens: {len(val_tokens):,}")
    
    # Create dataloaders
    train_loader = data_loader.create_dataloader(train_tokens, shuffle=True)
    val_loader = data_loader.create_dataloader(val_tokens, shuffle=False)
    
    # Create model config
    if args.config == 'tiny':
        config = TINY_CONFIG
    elif args.config == 'small':
        config = GPT2_SMALL_CONFIG
    else:
        config = ModelConfig()
    
    # Override config with command-line arguments
    config.vocab_size = args.vocab_size
    config.max_seq_len = args.seq_len
    config.batch_size = args.batch_size
    config.max_steps = args.max_steps
    config.learning_rate = args.learning_rate
    config.device = args.device
    
    # Create model
    model = LanguageModel(config)
    
    # Load checkpoint if provided
    if args.checkpoint:
        checkpoint = torch.load(args.checkpoint, map_location=config.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded checkpoint from {args.checkpoint}")
    
    # Create trainer
    trainer = Trainer(
        model,
        config,
        train_loader,
        val_loader,
        checkpoint_dir=args.output_dir,
    )
    
    # Train
    trainer.train(max_steps=args.max_steps)
    
    print(f"Training complete! Model saved to {args.output_dir}")


def generate_text(args):
    """Generate text using a trained model."""
    print("Loading model for generation...")
    
    # Load model
    deployment = ModelDeployment(args.model_dir)
    model, tokenizer, metadata = deployment.load_model(device=args.device)
    
    print(f"Model loaded: {metadata.get('description', 'No description')}")
    
    # Create generator
    generator = TextGenerator(model, tokenizer, device=args.device)
    
    # Get prompt
    if args.prompt:
        prompt = args.prompt
    elif args.prompt_file:
        with open(args.prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
    else:
        prompt = input("Enter prompt: ")
    
    print(f"\nPrompt: {prompt}")
    print("\nGenerating...\n")
    
    # Generate
    generated = generator.generate(
        prompt=prompt,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_k=args.top_k if args.top_k > 0 else None,
        top_p=args.top_p if args.top_p > 0 else None,
    )
    
    print(generated)
    
    # Save if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(generated)
        print(f"\nGenerated text saved to {args.output}")


def evaluate_model(args):
    """Evaluate a trained model."""
    print("Loading model for evaluation...")
    
    # Load model
    deployment = ModelDeployment(args.model_dir)
    model, tokenizer, metadata = deployment.load_model(device=args.device)
    
    # Load evaluation data
    print("Loading evaluation data...")
    if args.data_file.endswith('.npy'):
        tokens = load_tokens_from_file(args.data_file)
    else:
        with open(args.data_file, 'r', encoding='utf-8') as f:
            text = f.read()
        tokens = tokenizer.encode(text)
    
    print(f"Evaluation tokens: {len(tokens):,}")
    
    # Create dataloader
    data_loader = TextDataLoader(tokenizer, batch_size=args.batch_size, seq_len=args.seq_len)
    eval_loader = data_loader.create_dataloader(tokens, shuffle=False)
    
    # Create evaluator
    evaluator = Evaluator(model, tokenizer, device=args.device)
    
    # Generate report
    report = evaluator.generate_evaluation_report(
        eval_loader,
        save_path=args.output if args.output else None
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Language Model Training and Inference")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Train tokenizer command
    tokenizer_parser = subparsers.add_parser('train-tokenizer', help='Train a tokenizer')
    tokenizer_parser.add_argument('--data-file', type=str, required=True, help='Training data file')
    tokenizer_parser.add_argument('--vocab-size', type=int, default=50257, help='Vocabulary size')
    tokenizer_parser.add_argument('--output', type=str, default='tokenizer.json', help='Output file')
    
    # Train model command
    train_parser = subparsers.add_parser('train', help='Train a language model')
    train_parser.add_argument('--data-file', type=str, required=True, help='Training data file')
    train_parser.add_argument('--tokenizer', type=str, default='tokenizer.json', help='Tokenizer file')
    train_parser.add_argument('--config', type=str, default='small', choices=['tiny', 'small'], help='Model config')
    train_parser.add_argument('--vocab-size', type=int, default=50257, help='Vocabulary size')
    train_parser.add_argument('--seq-len', type=int, default=1024, help='Sequence length')
    train_parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    train_parser.add_argument('--max-steps', type=int, default=100000, help='Maximum training steps')
    train_parser.add_argument('--learning-rate', type=float, default=3e-4, help='Learning rate')
    train_parser.add_argument('--device', type=str, default='cuda', help='Device (cuda/cpu)')
    train_parser.add_argument('--checkpoint', type=str, help='Checkpoint to resume from')
    train_parser.add_argument('--output-dir', type=str, default='checkpoints', help='Output directory')
    
    # Generate text command
    generate_parser = subparsers.add_parser('generate', help='Generate text')
    generate_parser.add_argument('--model-dir', type=str, required=True, help='Model directory')
    generate_parser.add_argument('--prompt', type=str, help='Text prompt')
    generate_parser.add_argument('--prompt-file', type=str, help='File containing prompt')
    generate_parser.add_argument('--max-tokens', type=int, default=100, help='Max tokens to generate')
    generate_parser.add_argument('--temperature', type=float, default=1.0, help='Sampling temperature')
    generate_parser.add_argument('--top-k', type=int, default=0, help='Top-k sampling (0 = disabled)')
    generate_parser.add_argument('--top-p', type=float, default=0, help='Top-p sampling (0 = disabled)')
    generate_parser.add_argument('--device', type=str, default='cuda', help='Device (cuda/cpu)')
    generate_parser.add_argument('--output', type=str, help='Output file')
    
    # Evaluate model command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a model')
    eval_parser.add_argument('--model-dir', type=str, required=True, help='Model directory')
    eval_parser.add_argument('--data-file', type=str, required=True, help='Evaluation data file')
    eval_parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    eval_parser.add_argument('--seq-len', type=int, default=1024, help='Sequence length')
    eval_parser.add_argument('--device', type=str, default='cuda', help='Device (cuda/cpu)')
    eval_parser.add_argument('--output', type=str, help='Output file for report')
    
    args = parser.parse_args()
    
    if args.command == 'train-tokenizer':
        train_tokenizer(args)
    elif args.command == 'train':
        train_model(args)
    elif args.command == 'generate':
        generate_text(args)
    elif args.command == 'evaluate':
        evaluate_model(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
