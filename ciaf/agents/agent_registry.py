"""
Agent Registry for CIAF Agentic Workflows

Central registry of all agents with their policies.
Provides lookup and policy validation at scale.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from .agent_policies import IAMPolicy, PAMPolicy, PolicyViolation


@dataclass
class Agent:
    """Agent registration record with policies."""

    agent_id: str
    organization_id: str
    agent_name: str
    description: str
    iam_policy: IAMPolicy
    pam_policy: PAMPolicy

    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "organization_id": self.organization_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "iam_policy": self.iam_policy.to_dict(),
            "pam_policy": self.pam_policy.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "tags": self.tags,
        }


class AgentRegistry:
    """
    Central registry of all agents with their policies.

    Provides:
    - Agent registration and lookup
    - Policy validation
    - Inter-agent permission checking
    - Audit trail of agent operations
    """

    def __init__(self):
        # agent_id -> Agent
        self.agents: Dict[str, Agent] = {}

        # organization_id -> [agent_ids]
        self.org_agents: Dict[str, List[str]] = {}

        # Audit trail of policy violations
        self.policy_violations: List[PolicyViolation] = []

    def register_agent(
        self,
        agent_id: str,
        organization_id: str,
        agent_name: str,
        description: str,
        iam_policy: IAMPolicy,
        pam_policy: PAMPolicy,
        tags: List[str] = None,
    ) -> Agent:
        """
        Register a new agent with policies.

        Args:
            agent_id: Unique identifier for the agent
            organization_id: Organization that owns this agent
            agent_name: Human-readable name
            description: What does this agent do?
            iam_policy: Identity & Access Management policy
            pam_policy: Privileged Access Management policy
            tags: Optional tags for categorization

        Returns:
            Agent: The registered agent
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} already registered")

        agent = Agent(
            agent_id=agent_id,
            organization_id=organization_id,
            agent_name=agent_name,
            description=description,
            iam_policy=iam_policy,
            pam_policy=pam_policy,
            created_at=datetime.now(),
            tags=tags or [],
        )

        self.agents[agent_id] = agent

        # Track agents by organization
        if organization_id not in self.org_agents:
            self.org_agents[organization_id] = []
        self.org_agents[organization_id].append(agent_id)

        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Retrieve agent by ID.

        Returns:
            Agent if exists, else None
        """
        return self.agents.get(agent_id)

    def get_org_agents(self, organization_id: str) -> List[Agent]:
        """
        List all agents in an organization.

        Returns:
            List of Agent objects
        """
        agent_ids = self.org_agents.get(organization_id, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def deactivate_agent(self, agent_id: str) -> bool:
        """
        Deactivate an agent (soft delete).

        Returns:
            True if successful, False if agent not found
        """
        agent = self.agents.get(agent_id)
        if agent:
            agent.is_active = False
            agent.updated_at = datetime.now()
            return True
        return False

    def update_iam_policy(self, agent_id: str, new_policy: IAMPolicy) -> bool:
        """
        Update an agent's IAM policy.

        Returns:
            True if successful
        """
        agent = self.agents.get(agent_id)
        if agent:
            agent.iam_policy = new_policy
            agent.updated_at = datetime.now()
            return True
        return False

    def update_pam_policy(self, agent_id: str, new_policy: PAMPolicy) -> bool:
        """
        Update an agent's PAM policy.

        Returns:
            True if successful
        """
        agent = self.agents.get(agent_id)
        if agent:
            agent.pam_policy = new_policy
            agent.updated_at = datetime.now()
            return True
        return False

    def validate_agent_call(
        self,
        caller_id: str,
        target_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if agent A can call agent B.

        Args:
            caller_id: Agent making the call
            target_id: Agent being called

        Returns:
            (allowed, error_message_if_denied)
        """
        # Check both agents exist
        caller = self.get_agent(caller_id)
        target = self.get_agent(target_id)

        if not caller:
            return False, f"Caller agent {caller_id} not found"

        if not target:
            return False, f"Target agent {target_id} not found"

        # Check if caller is active
        if not caller.is_active:
            return False, f"Caller agent {caller_id} is deactivated"

        # Check if target is active
        if not target.is_active:
            return False, f"Target agent {target_id} is deactivated"

        # Check IAM policy
        if not caller.iam_policy.can_call_agent(target_id):
            return False, f"{caller_id} not authorized to call {target_id}"

        return True, None

    def validate_resource_access(
        self,
        agent_id: str,
        resource_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if agent can access a resource.

        Args:
            agent_id: Agent requesting access
            resource_id: Resource being requested

        Returns:
            (allowed, error_message_if_denied)
        """
        agent = self.get_agent(agent_id)

        if not agent:
            return False, f"Agent {agent_id} not found"

        if not agent.is_active:
            return False, f"Agent {agent_id} is deactivated"

        if not agent.iam_policy.can_access_resource(resource_id):
            return False, f"{agent_id} not authorized to access {resource_id}"

        return True, None

    def get_agent_by_tags(self, organization_id: str, tag: str) -> List[Agent]:
        """
        Find agents by tag in organization.

        Returns:
            List of agents with the specified tag
        """
        agents = self.get_org_agents(organization_id)
        return [a for a in agents if tag in a.tags]

    def record_policy_violation(self, violation: PolicyViolation) -> None:
        """Record a policy violation for audit purposes."""
        self.policy_violations.append(violation)

    def get_violations_for_agent(self, agent_id: str) -> List[PolicyViolation]:
        """Get all recorded violations for an agent."""
        return [v for v in self.policy_violations if v.agent_id == agent_id]

    def get_org_stats(self, organization_id: str) -> Dict:
        """
        Get statistics for an organization.

        Returns:
            Dict with agent counts and policy info
        """
        agents = self.get_org_agents(organization_id)
        active_count = sum(1 for a in agents if a.is_active)

        return {
            "organization_id": organization_id,
            "total_agents": len(agents),
            "active_agents": active_count,
            "inactive_agents": len(agents) - active_count,
            "agents": [a.agent_id for a in agents],
        }

    def to_dict(self) -> Dict:
        """Serialize entire registry to dictionary."""
        return {
            "agents": {aid: agent.to_dict() for aid, agent in self.agents.items()},
            "org_agents": self.org_agents,
            "violation_count": len(self.policy_violations),
        }
