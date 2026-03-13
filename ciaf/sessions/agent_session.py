"""
Session & Task Batching for CIAF

Manages per-user sessions and creates merkle-proof batches at task completion.
Connects agents/models → outputs → task batches → merkle trees.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid
import hashlib
import json

from ciaf.tagging import OutputTag, OutputTagManager
from ciaf.core.merkle import MerkleTree


@dataclass
class TaskBatch:
    """
    Atomic unit of work: 1+ inferences from a task (agent or model).

    Represents a single "task" that may involve:
    - Multiple agent calls (orchestrated)
    - Multiple model inferences (sequential)
    - Mix of both

    At completion, creates merkle proof linking all outputs.
    """

    task_batch_id: str
    session_id: str
    organization_id: str

    # Contents
    output_tag_ids: List[str] = field(default_factory=list)  # Tags in this batch
    status: str = "success"  # "success", "failure", "partial"
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None

    # Cryptographic proof
    content_hash: str = ""  # SHA-256 of batch contents
    merkle_root: Optional[str] = None  # Root of merkle tree over outputs
    merkle_tree_leaves: List[str] = field(default_factory=list)  # Content hashes

    # Org batch integration (filled after org batching)
    org_batch_id: Optional[str] = None
    org_batch_merkle_root: Optional[str] = None
    org_batch_proof: Optional[List[Tuple[str, str]]] = None

    # Metadata
    task_description: str = ""
    error_message: Optional[str] = None

    def add_output_tag(self, tag_id: str) -> None:
        """Add an output tag to this batch."""
        if tag_id not in self.output_tag_ids:
            self.output_tag_ids.append(tag_id)

    def compute_content_hash(self) -> str:
        """
        Compute deterministic hash of batch contents.

        Returns:
            Hex-encoded SHA-256 hash
        """
        # Sort tag IDs for determinism
        sorted_ids = sorted(self.output_tag_ids)
        content = json.dumps({
            "session_id": self.session_id,
            "organization_id": self.organization_id,
            "tag_ids": sorted_ids,
            "status": self.status,
        }, sort_keys=True)

        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def finalize(self, status: str = "success") -> None:
        """
        Finalize batch and compute hash.

        Args:
            status: Final status ("success", "failure", "partial")
        """
        self.end_time = datetime.now().isoformat()
        self.status = status

        # Compute duration
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        self.duration_ms = (end - start).total_seconds() * 1000

        # Compute content hash
        self.content_hash = self.compute_content_hash()

    def to_dict(self) -> Dict:
        """Serialize batch to dictionary."""
        return {
            "task_batch_id": self.task_batch_id,
            "session_id": self.session_id,
            "organization_id": self.organization_id,
            "output_tag_ids": self.output_tag_ids,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "content_hash": self.content_hash,
            "merkle_root": self.merkle_root,
            "org_batch_id": self.org_batch_id,
            "task_description": self.task_description,
        }


class SessionBatcher:
    """
    Creates merkle-proof batches at task completion.

    Workflow:
    1. new_task() - Start a new task
    2. add_output_to_task() - Add output tags
    3. complete_task() - Finalize & create merkle tree
    """

    def __init__(self, tag_manager: OutputTagManager):
        self.tag_manager = tag_manager

        # task_batch_id -> TaskBatch
        self.batches: Dict[str, TaskBatch] = {}

    def new_task(
        self,
        session_id: str,
        organization_id: str,
        task_description: str = "",
    ) -> TaskBatch:
        """
        Create a new task batch.

        Args:
            session_id: Which session owns this task
            organization_id: Organization context
            task_description: Human-readable description

        Returns:
            New TaskBatch
        """
        task_batch_id = str(uuid.uuid4())
        batch = TaskBatch(
            task_batch_id=task_batch_id,
            session_id=session_id,
            organization_id=organization_id,
            task_description=task_description,
        )

        self.batches[task_batch_id] = batch
        return batch

    def add_output_to_task(
        self,
        task_batch_id: str,
        output_tag_id: str,
    ) -> bool:
        """
        Add an output tag to task batch.

        Args:
            task_batch_id: Which task
            output_tag_id: Which output

        Returns:
            True if successful
        """
        batch = self.batches.get(task_batch_id)
        if not batch:
            return False

        batch.add_output_tag(output_tag_id)
        return True

    def complete_task(
        self,
        task_batch_id: str,
        status: str = "success",
    ) -> Tuple[bool, Optional[str]]:
        """
        Finalize task and create merkle tree.

        Creates merkle tree from output content hashes and attaches
        merkle proofs to each output tag.

        Args:
            task_batch_id: Which task to complete
            status: Final status ("success", "failure", "partial")

        Returns:
            (success, merkle_root_if_successful)
        """
        batch = self.batches.get(task_batch_id)
        if not batch:
            return False, None

        # Finalize batch
        batch.finalize(status)

        # If no outputs, nothing to merkle-tree
        if not batch.output_tag_ids:
            return True, None

        # Get content hashes from tags (this is what gets merkle-proved)
        content_hashes = []
        for tag_id in batch.output_tag_ids:
            tag = self.tag_manager.get_tag(tag_id)
            if tag:
                content_hashes.append(tag.output_content_hash)

        if not content_hashes:
            return True, None

        # Create merkle tree from content hashes
        merkle_tree = MerkleTree(content_hashes)
        merkle_root = merkle_tree.get_root()

        # Store merkle tree
        batch.merkle_root = merkle_root
        batch.merkle_tree_leaves = content_hashes

        # Attach merkle proofs to each tag
        for tag_id in batch.output_tag_ids:
            tag = self.tag_manager.get_tag(tag_id)
            if tag:
                # Get proof for this tag's content hash
                proof = merkle_tree.get_proof(tag.output_content_hash)
                # Add proof to tag
                self.tag_manager.add_task_batch_proof(
                    tag_id,
                    task_batch_id,
                    merkle_root,
                    proof,
                )

        return True, merkle_root

    def get_batch(self, task_batch_id: str) -> Optional[TaskBatch]:
        """Retrieve batch by ID."""
        return self.batches.get(task_batch_id)

    def get_stats_for_session(self, session_id: str) -> Dict:
        """Get statistics for all batches in session."""
        session_batches = [
            b for b in self.batches.values() if b.session_id == session_id
        ]

        status_counts = {"success": 0, "failure": 0, "partial": 0}
        for batch in session_batches:
            status_counts[batch.status] = status_counts.get(batch.status, 0) + 1

        total_outputs = sum(len(b.output_tag_ids) for b in session_batches)
        total_duration = sum(b.duration_ms or 0 for b in session_batches)

        return {
            "session_id": session_id,
            "batch_count": len(session_batches),
            "status_distribution": status_counts,
            "total_outputs": total_outputs,
            "total_duration_ms": total_duration,
            "avg_batch_size": total_outputs / len(session_batches)
            if session_batches
            else 0,
        }


class AgentSession:
    """
    User session containing multiple task batches.

    Manages the lifecycle of a user's interaction, tracking all
    inferences (agent or model) and organizing them into batches.
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        organization_id: str,
        tag_manager: Optional[OutputTagManager] = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.organization_id = organization_id
        self.created_at = datetime.now()
        self.ended_at: Optional[datetime] = None

        # Tagging and batching
        self.tag_manager = tag_manager or OutputTagManager()
        self.batcher = SessionBatcher(self.tag_manager)

        # Current task
        self.current_task: Optional[TaskBatch] = None
        self.completed_tasks: List[TaskBatch] = []

    def start_task(self, task_description: str = "") -> TaskBatch:
        """
        Start a new task in this session.

        Args:
            task_description: Human-readable description

        Returns:
            New TaskBatch
        """
        # Finalize current task if exists
        if self.current_task:
            self.complete_current_task("success")

        # Create new task
        self.current_task = self.batcher.new_task(
            session_id=self.session_id,
            organization_id=self.organization_id,
            task_description=task_description,
        )

        return self.current_task

    def record_output(
        self,
        output_content: str,
        inference_receipt_id: str,
        agent_ids: List[str] = None,
        model_name: str = None,
        policies_applied: List[str] = None,
        risk_level: str = "medium",
    ) -> OutputTag:
        """
        Record an output (agent or model) to current task.

        Args:
            output_content: The AI output
            inference_receipt_id: LCM receipt ID
            agent_ids: For agent inference (optional)
            model_name: For model inference (optional)
            policies_applied: Policies enforced
            risk_level: Risk classification

        Returns:
            OutputTag
        """
        if not self.current_task:
            raise RuntimeError("No active task. Call start_task() first.")

        # Create tag
        if agent_ids:
            tag = self.tag_manager.create_agent_tag(
                output_content=output_content,
                session_id=self.session_id,
                inference_receipt_id=inference_receipt_id,
                agent_ids=agent_ids,
                organization_id=self.organization_id,
                policies_applied=policies_applied,
                risk_level=risk_level,
            )
        elif model_name:
            tag = self.tag_manager.create_model_tag(
                output_content=output_content,
                session_id=self.session_id,
                inference_receipt_id=inference_receipt_id,
                model_name=model_name,
                organization_id=self.organization_id,
                policies_applied=policies_applied,
                risk_level=risk_level,
            )
        else:
            raise ValueError("Must provide either agent_ids or model_name")

        # Add to current task
        self.batcher.add_output_to_task(self.current_task.task_batch_id, tag.tag_id)

        return tag

    def complete_current_task(self, status: str = "success") -> Optional[TaskBatch]:
        """
        Complete the current task.

        Creates merkle tree and attaches proofs to all outputs.

        Args:
            status: Final status ("success", "failure", "partial")

        Returns:
            Completed TaskBatch or None
        """
        if not self.current_task:
            return None

        # Finalize task and create merkle tree
        success, merkle_root = self.batcher.complete_task(
            self.current_task.task_batch_id, status
        )

        if success:
            self.completed_tasks.append(self.current_task)
            task = self.current_task
            self.current_task = None
            return task

        return None

    def end_session(self):
        """
        End this session.

        Finalizes current task if exists.
        """
        if self.current_task:
            self.complete_current_task("success")

        self.ended_at = datetime.now()

    def get_session_summary(self) -> Dict:
        """Get summary of all tasks in session."""
        total_duration = (
            (self.ended_at or datetime.now()) - self.created_at
        ).total_seconds()

        total_outputs = sum(len(t.output_tag_ids) for t in self.completed_tasks)
        total_batch_duration = sum(t.duration_ms or 0 for t in self.completed_tasks)

        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": total_duration,
            "completed_tasks": len(self.completed_tasks),
            "total_outputs": total_outputs,
            "batch_processing_ms": total_batch_duration,
        }

    def to_dict(self) -> Dict:
        """Serialize session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "tasks": [t.to_dict() for t in self.completed_tasks],
            "current_task": self.current_task.to_dict() if self.current_task else None,
        }
