"""
Organization-Level Batching System

Manages periodic batching of task batches at organization level.
Creates 6-hour batch windows with merkle proofs.

Created: 2025-03-13
Author: Denzil James Greenwood
Version: 0.1.0
"""

from .org_batch_scheduler import (
    OrgBatchWindow,
    OrgBatchScheduler,
)

__all__ = [
    "OrgBatchWindow",
    "OrgBatchScheduler",
]

__version__ = "0.1.0"
