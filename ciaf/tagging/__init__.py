"""
Output Tagging System for CIAF Agentic Workflows

Provides cryptographic watermarking for AI-generated outputs.
Supports embedding tags in text, images, and structured data.

Created: 2025-03-13
Author: Denzil James Greenwood
Version: 0.1.0
"""

from .output_tag import (
    OutputTag,
    OutputTagManager,
)
from .tag_embedder import (
    TagEmbedder,
)

__all__ = [
    "OutputTag",
    "OutputTagManager",
    "TagEmbedder",
]

__version__ = "0.1.0"
