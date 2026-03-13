"""
Session & Task Batching System for CIAF

Manages user sessions with task batching and merkle proof generation.

Created: 2025-03-13
Author: Denzil James Greenwood
Version: 0.1.0
"""

from .agent_session import (
    TaskBatch,
    SessionBatcher,
    AgentSession,
)

__all__ = [
    "TaskBatch",
    "SessionBatcher",
    "AgentSession",
]

__version__ = "0.1.0"
