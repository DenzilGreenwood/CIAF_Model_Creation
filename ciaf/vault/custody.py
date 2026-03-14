"""
Custody management (alias for core module for backwards compatibility).
"""

from .core import ImmutableProof, VaultManager

__all__ = ["ImmutableProof", "VaultManager", "CustodyManager"]


class CustodyManager(VaultManager):
    """Alias for VaultManager - provides custody management."""
    pass
