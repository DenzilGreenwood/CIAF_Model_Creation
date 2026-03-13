"""
Agent Registry & Policy Management for CIAF Agentic Workflows

Provides declarative IAM/PAM (Identity & Access Management / Privileged Access Management)
policies for controlling agent behavior, inter-agent communication, and resource access.

Created: 2025-03-13
Author: Denzil James Greenwood
Version: 0.1.0
"""

from .agent_policies import (
    IAMPolicy,
    PAMPolicy,
    AgentPolicyValidator,
    PolicyViolation,
)
from .agent_registry import (
    Agent,
    AgentRegistry,
)
from .agent_context import (
    AgentAction,
    AgentExecutionContext,
)
from .examples import (
    create_healthcare_policies,
    create_banking_policies,
    create_example_agent_registry,
)

__all__ = [
    # Policies
    "IAMPolicy",
    "PAMPolicy",
    "AgentPolicyValidator",
    "PolicyViolation",
    # Registry
    "Agent",
    "AgentRegistry",
    # Execution
    "AgentAction",
    "AgentExecutionContext",
    # Examples
    "create_healthcare_policies",
    "create_banking_policies",
    "create_example_agent_registry",
]

__version__ = "0.1.0"
