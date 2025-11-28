"""
Package initialization for the new_llm language model.
"""

__version__ = "1.0.0"
__author__ = "LLM from Scratch"
__description__ = "Complete transformer-based language model implementation"

from .config import ModelConfig, GPT2_SMALL_CONFIG, TINY_CONFIG
from .model import LanguageModel
from .tokenizer import BPETokenizer
from .trainer import Trainer
from .inference import TextGenerator
from .evaluation import Evaluator
from .deployment import ModelDeployment

__all__ = [
    'ModelConfig',
    'GPT2_SMALL_CONFIG',
    'TINY_CONFIG',
    'LanguageModel',
    'BPETokenizer',
    'Trainer',
    'TextGenerator',
    'Evaluator',
    'ModelDeployment',
]
