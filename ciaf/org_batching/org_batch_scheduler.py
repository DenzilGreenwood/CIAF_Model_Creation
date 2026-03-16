"""
Organization-Level Batching with Time-Window Scheduling

Batches all task batches from an organization at regular intervals (6 hours).
Creates organization-level merkle tree for audit checkpoints.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
import uuid
import asyncio
import hashlib
import json

from ciaf.sessions import TaskBatch
from ciaf.core.merkle import MerkleTree


@dataclass
class OrgBatchWindow:
    """
    Organization-level batch window.

    Contains all task batches completed during a 6-hour window.
    Creates merkle tree proving all outputs in that period.
    """

    window_id: str  # e.g., "org_001_2025_03_13_00h"
    organization_id: str
    window_start: datetime
    window_end: datetime

    # Contents
    task_batch_ids: List[str] = field(default_factory=list)
    completed_task_batches: List[TaskBatch] = field(default_factory=list)

    # Cryptographic proof
    merkle_root: Optional[str] = None
    merkle_tree_leaves: List[str] = field(default_factory=list)

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # "pending", "completed", "closed"

    def add_task_batch(self, batch: TaskBatch) -> None:
        """Add task batch to window."""
        if batch.task_batch_id not in self.task_batch_ids:
            self.task_batch_ids.append(batch.task_batch_id)
            self.completed_task_batches.append(batch)

    def compute_content_hash(self) -> str:
        """Compute hash of all task batches in window."""
        # Sort batch IDs for determinism
        sorted_ids = sorted(self.task_batch_ids)
        content = json.dumps({
            "organization_id": self.organization_id,
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "batch_ids": sorted_ids,
        }, sort_keys=True)

        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def finalize_window(self) -> Optional[str]:
        """
        Finalize window and create merkle tree.

        Returns:
            Merkle root if successful, None otherwise
        """
        if not self.completed_task_batches:
            self.status = "completed"
            return None

        # Collect content hashes from all task batches
        merkle_leaves = []
        for batch in self.completed_task_batches:
            if batch.content_hash:
                merkle_leaves.append(batch.content_hash)

        if not merkle_leaves:
            self.status = "completed"
            return None

        # Create merkle tree
        merkle_tree = MerkleTree(merkle_leaves)
        self.merkle_root = merkle_tree.get_root()
        self.merkle_tree_leaves = merkle_leaves
        self.status = "completed"

        return self.merkle_root

    def to_dict(self) -> Dict:
        """Serialize window to dictionary."""
        return {
            "window_id": self.window_id,
            "organization_id": self.organization_id,
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "task_batch_count": len(self.task_batch_ids),
            "merkle_root": self.merkle_root,
            "status": self.status,
            "created_at": self.created_at,
        }


class OrgBatchScheduler:
    """
    Schedules and manages organization-level batching.

    Creates 6-hour batching windows per organization.
    Background task runs timer for each organization.
    """

    def __init__(self, batch_interval: timedelta = timedelta(hours=6)):
        self.batch_interval = batch_interval

        # organization_id -> list of pending task batches
        self.pending_batches: Dict[str, List[TaskBatch]] = {}

        # organization_id -> list of completed windows
        self.completed_windows: Dict[str, List[OrgBatchWindow]] = {}

        # organization_id -> current window
        self.current_windows: Dict[str, OrgBatchWindow] = {}

        # organization_id -> asyncio task (scheduler)
        self.scheduler_tasks: Dict[str, asyncio.Task] = {}

    def queue_task_batch(
        self,
        organization_id: str,
        task_batch: TaskBatch,
    ) -> None:
        """
        Queue a completed task batch for org batching.

        Called when a task batch is completed and ready for org-level batching.

        Args:
            organization_id: Which organization owns this batch
            task_batch: Completed TaskBatch object
        """
        if organization_id not in self.pending_batches:
            self.pending_batches[organization_id] = []

        self.pending_batches[organization_id].append(task_batch)

    async def start_org_batching(self, organization_id: str) -> None:
        """
        Start periodic batching for an organization.

        Creates a background task that batches every 6 hours.

        Args:
            organization_id: Which organization to batch
        """
        if organization_id in self.scheduler_tasks:
            return  # Already running

        # Create background task
        task = asyncio.create_task(self._batch_timer(organization_id))
        self.scheduler_tasks[organization_id] = task

    async def stop_org_batching(self, organization_id: str) -> None:
        """
        Stop batching for an organization.

        Args:
            organization_id: Which organization to stop
        """
        if organization_id in self.scheduler_tasks:
            self.scheduler_tasks[organization_id].cancel()
            del self.scheduler_tasks[organization_id]

    async def _batch_timer(self, organization_id: str) -> None:
        """
        Background timer loop for organization batching.

        Batches every 6 hours.

        Args:
            organization_id: Which organization
        """
        try:
            while True:
                await asyncio.sleep(self.batch_interval.total_seconds())
                await self.create_batch_window(organization_id)
        except asyncio.CancelledError:
            pass

    async def create_batch_window(self, organization_id: str) -> Optional[str]:
        """
        Create a new batch window and finalize previous one.

        Called on timer or explicitly.

        Args:
            organization_id: Which organization

        Returns:
            Window ID if successful
        """
        # Finalize previous window
        if organization_id in self.current_windows:
            old_window = self.current_windows[organization_id]
            old_window.finalize_window()

            if organization_id not in self.completed_windows:
                self.completed_windows[organization_id] = []
            self.completed_windows[organization_id].append(old_window)

        # Create new window
        now = datetime.now()
        window_id = f"org_{organization_id}_{now.strftime('%Y%m%d_%H')}h"

        window = OrgBatchWindow(
            window_id=window_id,
            organization_id=organization_id,
            window_start=now,
            window_end=now + self.batch_interval,
        )

        # Add pending batches to window
        if organization_id in self.pending_batches:
            for batch in self.pending_batches[organization_id]:
                window.add_task_batch(batch)

            # Clear pending queue
            self.pending_batches[organization_id] = []

        self.current_windows[organization_id] = window

        return window_id

    def get_current_window(self, organization_id: str) -> Optional[OrgBatchWindow]:
        """Get current batch window for organization."""
        return self.current_windows.get(organization_id)

    def get_completed_windows(
        self, organization_id: str
    ) -> List[OrgBatchWindow]:
        """Get all completed batch windows."""
        return self.completed_windows.get(organization_id, [])

    def get_org_stats(self, organization_id: str) -> Dict:
        """Get batching statistics for organization."""
        current = self.get_current_window(organization_id)
        completed = self.get_completed_windows(organization_id)

        return {
            "organization_id": organization_id,
            "current_window": current.to_dict() if current else None,
            "completed_windows": len(completed),
            "total_task_batches": sum(len(w.task_batch_ids) for w in completed)
            + (len(current.task_batch_ids) if current else 0),
            "windows": [w.to_dict() for w in completed[-10:]],  # Last 10 windows
        }
