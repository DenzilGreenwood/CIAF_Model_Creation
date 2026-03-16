"""
Agent Execution Context Tracking

Tracks which agents ran, in what order, and what they did during a task.
Provides structured audit trail for task execution.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


@dataclass
class AgentAction:
    """Record of a single agent action during task execution."""

    agent_id: str
    action_type: str  # "inference", "decision", "analysis"
    timestamp: str  # ISO format
    input_hash: str  # SHA-256 of input
    output_hash: str  # SHA-256 of output
    status: str = "success"  # "success", "failure", "partial"
    policies_enforced: List[str] = field(default_factory=list)
    risk_level: str = "medium"  # "low", "medium", "high", "critical"
    duration_ms: Optional[float] = None  # Execution time
    error_message: Optional[str] = None  # If status is failure
    metadata: Dict[str, Any] = field(default_factory=dict)  # Custom metadata

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "timestamp": self.timestamp,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "status": self.status,
            "policies_enforced": self.policies_enforced,
            "risk_level": self.risk_level,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class AgentExecutionContext:
    """
    Tracks the execution of a single task involving multiple agents.

    Provides:
    - Recording of agent actions in order
    - Overall task status tracking
    - Audit trail for task execution
    """

    def __init__(
        self,
        session_id: str,
        task_batch_id: str,
        organization_id: str,
    ):
        self.session_id = session_id
        self.task_batch_id = task_batch_id
        self.organization_id = organization_id

        # Execution tracking
        self.actions: List[AgentAction] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "running"  # "running", "success", "failure", "partial"

        # Overall task metadata
        self.task_id = str(uuid.uuid4())
        self.total_duration_ms: Optional[float] = None
        self.error_count = 0
        self.success_count = 0

    def add_agent_action(self, action: AgentAction) -> None:
        """
        Record an agent action.

        Args:
            action: AgentAction to record
        """
        self.actions.append(action)

        # Update counters
        if action.status == "success":
            self.success_count += 1
        elif action.status == "failure":
            self.error_count += 1

    def get_actions_for_agent(self, agent_id: str) -> List[AgentAction]:
        """Get all actions performed by a specific agent."""
        return [a for a in self.actions if a.agent_id == agent_id]

    def get_agent_sequence(self) -> List[str]:
        """Get the sequence of agents that ran (in order)."""
        seen = set()
        sequence = []
        for action in self.actions:
            if action.agent_id not in seen:
                sequence.append(action.agent_id)
                seen.add(action.agent_id)
        return sequence

    def finalize(self, status: str = "success") -> None:
        """
        Finalize task execution.

        Args:
            status: Final status ("success", "failure", "partial")
        """
        self.end_time = datetime.now()
        self.status = status
        self.total_duration_ms = (
            (self.end_time - self.start_time).total_seconds() * 1000
        )

    def has_failures(self) -> bool:
        """Check if any actions failed."""
        return any(a.status == "failure" for a in self.actions)

    def has_errors(self) -> bool:
        """Check if error_count > 0."""
        return self.error_count > 0

    def get_risk_levels(self) -> Dict[str, int]:
        """Get count of actions by risk level."""
        risk_counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        }
        for action in self.actions:
            risk_counts[action.risk_level] = risk_counts.get(action.risk_level, 0) + 1
        return risk_counts

    def get_policies_applied(self) -> List[str]:
        """Get all unique policies applied in this task."""
        policies = set()
        for action in self.actions:
            policies.update(action.policies_enforced)
        return sorted(list(policies))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "task_batch_id": self.task_batch_id,
            "organization_id": self.organization_id,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_ms": self.total_duration_ms,
            "agent_sequence": self.get_agent_sequence(),
            "action_count": len(self.actions),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "risk_levels": self.get_risk_levels(),
            "policies_applied": self.get_policies_applied(),
            "actions": [a.to_dict() for a in self.actions],
        }


class ExecutionContextManager:
    """
    Manages multiple execution contexts for a session.

    Tracks all tasks within a user session.
    """

    def __init__(self, session_id: str, organization_id: str):
        self.session_id = session_id
        self.organization_id = organization_id
        self.created_at = datetime.now()

        # task_batch_id -> ExecutionContext
        self.contexts: Dict[str, AgentExecutionContext] = {}
        self.current_context: Optional[AgentExecutionContext] = None

    def create_task(self, task_batch_id: str) -> AgentExecutionContext:
        """
        Create a new execution context for a task.

        Returns:
            New AgentExecutionContext
        """
        context = AgentExecutionContext(
            session_id=self.session_id,
            task_batch_id=task_batch_id,
            organization_id=self.organization_id,
        )
        self.contexts[task_batch_id] = context
        self.current_context = context
        return context

    def get_context(self, task_batch_id: str) -> Optional[AgentExecutionContext]:
        """Get context by task batch ID."""
        return self.contexts.get(task_batch_id)

    def finalize_current_task(self, status: str) -> Optional[AgentExecutionContext]:
        """
        Finalize the current task.

        Returns:
            The finalized context, or None if no current context
        """
        if self.current_context:
            self.current_context.finalize(status)
            return self.current_context
        return None

    def get_all_completed_tasks(self) -> List[AgentExecutionContext]:
        """Get all completed tasks in this session."""
        return [c for c in self.contexts.values() if c.status != "running"]

    def get_agent_summary(self) -> Dict[str, Any]:
        """
        Get summary of agent activity in this session.

        Returns:
            Dict with agent statistics
        """
        agent_stats = {}

        for context in self.contexts.values():
            for action in context.actions:
                agent_id = action.agent_id
                if agent_id not in agent_stats:
                    agent_stats[agent_id] = {
                        "action_count": 0,
                        "success_count": 0,
                        "failure_count": 0,
                        "risk_levels": {"low": 0, "medium": 0, "high": 0, "critical": 0},
                    }

                agent_stats[agent_id]["action_count"] += 1
                if action.status == "success":
                    agent_stats[agent_id]["success_count"] += 1
                elif action.status == "failure":
                    agent_stats[agent_id]["failure_count"] += 1

                if action.risk_level in agent_stats[agent_id]["risk_levels"]:
                    agent_stats[agent_id]["risk_levels"][action.risk_level] += 1

        return agent_stats

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "organization_id": self.organization_id,
            "created_at": self.created_at.isoformat(),
            "task_count": len(self.contexts),
            "completed_tasks": len(self.get_all_completed_tasks()),
            "agent_summary": self.get_agent_summary(),
            "contexts": {
                task_batch_id: context.to_dict()
                for task_batch_id, context in self.contexts.items()
            },
        }
