"""
Clean Model Package
Simple GPT model training and inference without CIAF/LCM integration
"""

from .model import GPTModel, GPTModelConfig, create_small_model, create_medium_model, create_large_model
from .data import SlimPajamaDataLoader, SimpleTokenizer, DataCurator, create_dataloaders, create_tokenizer
from .training import Trainer, create_trainer
from .evaluation import ModelEvaluator, create_evaluator
from .deployment import start_server

__version__ = "1.0.0"

__all__ = [
    # Model
    'GPTModel',
    'GPTModelConfig',
    'create_small_model',
    'create_medium_model',
    'create_large_model',
    
    # Data
    'SlimPajamaDataLoader',
    'SimpleTokenizer',
    'DataCurator',
    'create_dataloaders',
    'create_tokenizer',
    
    # Training
    'Trainer',
    'create_trainer',
    
    # Evaluation
    'ModelEvaluator',
    'create_evaluator',
    
    # Deployment
    'start_server'
]
