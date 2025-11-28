"""
Example: Quick start demo for training and using the language model.
"""
import torch
from config import TINY_CONFIG
from model import LanguageModel
from tokenizer import BPETokenizer
from dataset import TextDataLoader
from trainer import Trainer
from inference import TextGenerator
from deployment import ModelDeployment
from utils import set_seed, print_model_summary


def main():
    # Set seed for reproducibility
    set_seed(42)
    
    print("=" * 80)
    print("Language Model Quick Start Demo")
    print("=" * 80)
    
    # Step 1: Create sample training data
    print("\n1. Creating sample training data...")
    sample_text = """
    The quick brown fox jumps over the lazy dog.
    Machine learning is a fascinating field of artificial intelligence.
    Natural language processing enables computers to understand human language.
    Deep learning models have revolutionized many areas of AI.
    Transformers are the foundation of modern language models.
    """ * 50  # Repeat to get more data
    
    print(f"   Total characters: {len(sample_text):,}")
    
    # Step 2: Train tokenizer
    print("\n2. Training BPE tokenizer...")
    tokenizer = BPETokenizer(vocab_size=1000)
    tokenizer.train(sample_text, verbose=False)
    print(f"   Vocabulary size: {len(tokenizer.encoder)}")
    
    # Step 3: Tokenize data
    print("\n3. Tokenizing text...")
    tokens = tokenizer.encode(sample_text)
    print(f"   Total tokens: {len(tokens):,}")
    
    # Step 4: Create dataloaders
    print("\n4. Creating dataloaders...")
    data_loader = TextDataLoader(tokenizer, batch_size=4, seq_len=64)
    train_tokens, val_tokens = data_loader.split_data(tokens, train_ratio=0.9)
    train_loader = data_loader.create_dataloader(train_tokens, shuffle=True)
    val_loader = data_loader.create_dataloader(val_tokens, shuffle=False)
    print(f"   Training batches: {len(train_loader)}")
    print(f"   Validation batches: {len(val_loader)}")
    
    # Step 5: Create model
    print("\n5. Creating model...")
    config = TINY_CONFIG
    config.vocab_size = len(tokenizer.encoder)
    config.max_seq_len = 64
    config.max_steps = 200
    config.eval_every = 100
    config.save_every = 100
    
    model = LanguageModel(config)
    print_model_summary(model)
    
    # Step 6: Train model
    print("\n6. Training model...")
    trainer = Trainer(
        model,
        config,
        train_loader,
        val_loader,
        checkpoint_dir="demo_checkpoints"
    )
    trainer.train(max_steps=200)
    
    # Step 7: Save model
    print("\n7. Saving model...")
    deployment = ModelDeployment("demo_model")
    deployment.save_model(
        model,
        tokenizer,
        metadata={
            'description': 'Demo language model',
            'training_steps': 200,
            'training_tokens': len(train_tokens),
        }
    )
    
    # Step 8: Load model and generate text
    print("\n8. Loading model and generating text...")
    loaded_model, loaded_tokenizer, metadata = deployment.load_model(device='cpu')
    
    generator = TextGenerator(loaded_model, loaded_tokenizer, device='cpu')
    
    # Test different generation strategies
    prompts = [
        "The quick brown",
        "Machine learning",
        "Natural language",
    ]
    
    print("\n" + "=" * 80)
    print("TEXT GENERATION EXAMPLES")
    print("=" * 80)
    
    for prompt in prompts:
        print(f"\n{'Prompt:':<20} {prompt}")
        
        # Greedy generation
        greedy = generator.generate_greedy(prompt, max_new_tokens=20)
        print(f"{'Greedy:':<20} {greedy}")
        
        # Temperature sampling
        sampled = generator.generate(prompt, max_new_tokens=20, temperature=0.8)
        print(f"{'Temperature (0.8):':<20} {sampled}")
        
        # Top-k sampling
        top_k = generator.generate(prompt, max_new_tokens=20, top_k=10)
        print(f"{'Top-k (10):':<20} {top_k}")
    
    # Step 9: Evaluate model
    print("\n\n9. Evaluating model...")
    from evaluation import Evaluator
    
    evaluator = Evaluator(loaded_model, loaded_tokenizer, device='cpu')
    perplexity = evaluator.compute_perplexity(val_loader, max_batches=10)
    accuracy = evaluator.compute_accuracy(val_loader, top_k=1, max_batches=10)
    
    print(f"   Perplexity: {perplexity:.2f}")
    print(f"   Accuracy: {accuracy:.2f}%")
    
    print("\n" + "=" * 80)
    print("Demo complete! Model saved to 'demo_model' directory.")
    print("=" * 80)


if __name__ == "__main__":
    main()
