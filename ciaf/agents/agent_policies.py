"""
Agent IAM/PAM Policy Definitions

Declarative policies for controlling agent access, privileges, and inter-agent communication.
Organizations define these policies upfront; agents must comply.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import time


class AccessLevel(str, Enum):
    """Agent access level classifications."""
    VIEWER = "viewer"  # Read-only
    OPERATOR = "operator"  # Read + execute
    ADMIN = "admin"  # Full access


class ActionType(str, Enum):
    """Types of actions agents can perform."""
    INFERENCE = "inference"
    ANALYSIS = "analysis"
    DECISION = "decision"
    DATA_ACCESS = "data_access"
    AGENT_CREATION = "agent_creation"
    AGENT_ESCALATION = "agent_escalation"
    BATCH_FINALIZATION = "batch_finalization"


class RiskLevel(str, Enum):
    """Risk level for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IAMPolicy:
    """
    Identity & Access Management Policy for an agent.

    Defines what resources an agent can access and what other agents it can invoke.
    """

    agent_id: str
    organization_id: str

    # Agent metadata
    agent_name: str = ""
    description: str = ""

    # Resource access control
    allowed_resources: List[str] = field(default_factory=list)
    """Which models, databases, or services can this agent use?
    Examples: ["llama2-7b", "patient_database_read", "gpt4_api"]
    """

    allowed_agents: List[str] = field(default_factory=list)
    """Which other agents can this agent invoke?
    Examples: ["healthcare_reader_001", "analysis_agent_001"]
    """

    # Rate limiting
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "inferences_per_hour": 1000,
        "api_calls_per_minute": 100,
    })
    """Rate limits per resource."""

    # Data scopes
    data_scopes: List[str] = field(default_factory=list)
    """Which data categories can this agent access?
    Examples: ["pii_safe", "customer_data", "internal_only"]
    """

    # Approval requirements
    approval_required_for: List[str] = field(default_factory=list)
    """High-risk actions requiring human approval before execution.
    Examples: ["clinical_recommendation", "credit_denial"]
    """

    # Time-based access
    allowed_hours: Optional[str] = None
    """Business hours when agent can operate. None = 24/7
    Format: "09:00-17:00" or "24/7"
    """

    def can_access_resource(self, resource_id: str) -> bool:
        """Check if agent can access a specific resource."""
        return resource_id in self.allowed_resources

    def can_call_agent(self, target_agent_id: str) -> bool:
        """Check if agent can invoke another agent."""
        return target_agent_id in self.allowed_agents

    def requires_approval(self, action_type: str) -> bool:
        """Check if action requires approval."""
        return action_type in self.approval_required_for

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "organization_id": self.organization_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "allowed_resources": self.allowed_resources,
            "allowed_agents": self.allowed_agents,
            "rate_limits": self.rate_limits,
            "data_scopes": self.data_scopes,
            "approval_required_for": self.approval_required_for,
            "allowed_hours": self.allowed_hours,
        }


@dataclass
class PAMPolicy:
    """
    Privileged Access Management Policy for an agent.

    Defines elevated privileges an agent has, such as batch finalization,
    audit history access, or human escalation.
    """

    agent_id: str

    # Privilege elevation
    can_create_agents: bool = False
    """Can this agent create new agents?"""

    can_finalize_batches: bool = False
    """Can this agent finalize task/org batches?"""

    can_access_audit_history: bool = False
    """Can this agent view full audit trails?"""

    max_batch_size: int = 100
    """Maximum number of tasks in a batch created by this agent."""

    # Approval & delegation
    can_approve_high_risk: bool = False
    """Can this agent approve high-risk actions?"""

    can_escalate_to_human: bool = False
    """Can this agent escalate decisions to human reviewers?"""

    # Time-based access
    access_hours: Optional[str] = None
    """Hours when privilged access is allowed. None = 24/7
    Format: "09:00-17:00" or "24/7"
    """

    # Delegation
    can_delegate_to_agents: List[str] = field(default_factory=list)
    """Which agents can this agent delegate tasks to?"""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "can_create_agents": self.can_create_agents,
            "can_finalize_batches": self.can_finalize_batches,
            "can_access_audit_history": self.can_access_audit_history,
            "max_batch_size": self.max_batch_size,
            "can_approve_high_risk": self.can_approve_high_risk,
            "can_escalate_to_human": self.can_escalate_to_human,
            "access_hours": self.access_hours,
            "can_delegate_to_agents": self.can_delegate_to_agents,
        }


@dataclass
class PolicyViolation:
    """Record of a policy violation."""

    agent_id: str
    policy_type: str  # "iam" or "pam"
    violation_type: str  # "resource_access", "agent_call", "approval_required", etc.
    description: str
    action_attempted: str
    resource_or_target: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "policy_type": self.policy_type,
            "violation_type": self.violation_type,
            "description": self.description,
            "action_attempted": self.action_attempted,
            "resource_or_target": self.resource_or_target,
            "timestamp": self.timestamp,
        }


class AgentPolicyValidator:
    """
    Validates agent actions against IAM/PAM policies.

    Central enforcement point for agent governance.
    """

    def __init__(self):
        self.violation_history: List[PolicyViolation] = []

    def validate_resource_access(
        self,
        iam_policy: IAMPolicy,
        resource_id: str,
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Validate if agent can access a resource.

        Returns: (allowed, violation_if_denied)
        """
        if iam_policy.can_access_resource(resource_id):
            return True, None

        violation = PolicyViolation(
            agent_id=iam_policy.agent_id,
            policy_type="iam",
            violation_type="resource_access",
            description=f"Agent not authorized to access resource: {resource_id}",
            action_attempted="resource_access",
            resource_or_target=resource_id,
        )
        return False, violation

    def validate_agent_call(
        self,
        caller_iam: IAMPolicy,
        target_agent_id: str,
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Validate if agent A can call agent B.

        Returns: (allowed, violation_if_denied)
        """
        if caller_iam.can_call_agent(target_agent_id):
            return True, None

        violation = PolicyViolation(
            agent_id=caller_iam.agent_id,
            policy_type="iam",
            violation_type="agent_call",
            description=f"Agent not authorized to call: {target_agent_id}",
            action_attempted="agent_call",
            resource_or_target=target_agent_id,
        )
        return False, violation

    def validate_approval_requirement(
        self,
        iam_policy: IAMPolicy,
        action_type: str,
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Check if action requires human approval.

        Returns: (approval_required, violation_if_critical)
        """
        approval_needed = iam_policy.requires_approval(action_type)

        if approval_needed:
            # Approval required - return true to indicate caller should seek approval
            violation = PolicyViolation(
                agent_id=iam_policy.agent_id,
                policy_type="iam",
                violation_type="approval_required",
                description=f"Action {action_type} requires human approval",
                action_attempted=action_type,
            )
            return approval_needed, violation

        return False, None

    def validate_batch_finalization(
        self,
        pam_policy: PAMPolicy,
        batch_size: int,
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Validate if agent can finalize a batch of given size.

        Returns: (allowed, violation_if_denied)
        """
        if not pam_policy.can_finalize_batches:
            violation = PolicyViolation(
                agent_id=pam_policy.agent_id,
                policy_type="pam",
                violation_type="batch_finalization",
                description="Agent not authorized to finalize batches",
                action_attempted="batch_finalization",
            )
            return False, violation

        if batch_size > pam_policy.max_batch_size:
            violation = PolicyViolation(
                agent_id=pam_policy.agent_id,
                policy_type="pam",
                violation_type="batch_size_exceeded",
                description=f"Batch size {batch_size} exceeds limit {pam_policy.max_batch_size}",
                action_attempted="batch_finalization",
            )
            return False, violation

        return True, None

    def validate_escalation(
        self,
        pam_policy: PAMPolicy,
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Validate if agent can escalate to human.

        Returns: (allowed, violation_if_denied)
        """
        if not pam_policy.can_escalate_to_human:
            violation = PolicyViolation(
                agent_id=pam_policy.agent_id,
                policy_type="pam",
                violation_type="escalation",
                description="Agent not authorized to escalate to human",
                action_attempted="escalation",
            )
            return False, violation

        return True, None

    def record_violation(self, violation: PolicyViolation) -> None:
        """Record a policy violation for audit purposes."""
        self.violation_history.append(violation)

    def get_violations_for_agent(self, agent_id: str) -> List[PolicyViolation]:
        """Get all violations for a specific agent."""
        return [v for v in self.violation_history if v.agent_id == agent_id]
