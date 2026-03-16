"""Base agent class and agent orchestration."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod
from llm_providers import LLMProvider, LLMProviderFactory, LLMProviderType
from ciaf_client import CIAFClient


class Agent(ABC):
    """Base class for CIAF agents."""

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str,
        policies: List[str],
        llm_provider: Optional[LLMProvider] = None
    ):
        """Initialize agent.

        Args:
            agent_id: Unique agent identifier
            organization_id: Organization this agent belongs to
            role: Agent role (e.g., "credit_analyst", "physician")
            policies: List of applicable policies
            llm_provider: LLM provider to use
        """
        self.agent_id = agent_id
        self.organization_id = organization_id
        self.role = role
        self.policies = policies
        self.llm_provider = llm_provider or LLMProviderFactory.create_auto()
        self.ciaf_client = CIAFClient()
        self.execution_history: List[Dict[str, Any]] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        pass

    def generate_output(
        self,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate output using LLM.

        Args:
            user_prompt: User input prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens

        Returns:
            Generated output
        """
        output = self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=self.get_system_prompt(),
            temperature=temperature,
            max_tokens=max_tokens
        )
        return output

    def create_tagged_output(
        self,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """Generate output and create CIAF tag.

        Args:
            user_prompt: User input prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens

        Returns:
            Dictionary with output, tag_id, and verification result
        """
        # Generate output
        output = self.generate_output(user_prompt, temperature, max_tokens)

        # Create tag
        tag_id = str(uuid.uuid4())

        # Submit to CIAF
        verification = self.ciaf_client.submit_verification(
            content=output,
            tag_id=tag_id,
            agents=[self.agent_id],
            organization_id=self.organization_id,
            policies=self.policies,
            metadata={
                "role": self.role,
                "user_prompt": user_prompt,
                "temperature": temperature
            }
        )

        # Record execution
        execution_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tag_id": tag_id,
            "output": output,
            "verification": verification
        }
        self.execution_history.append(execution_record)

        return {
            "output": output,
            "tag_id": tag_id,
            "verification": verification,
            "policies_applied": self.policies
        }

    def verify_past_output(self, tag_id: str) -> Dict[str, Any]:
        """Verify a previously generated output.

        Args:
            tag_id: Tag ID to verify

        Returns:
            Verification result
        """
        result = self.ciaf_client.verify_output(tag_id, include_audit=True)
        return {
            "tag_id": tag_id,
            "status": result.status.value,
            "risk_level": result.risk_level.value,
            "policies": result.policies,
            "merkle_proof_valid": result.merkle_proof_valid,
            "issues": result.issues,
            "warnings": result.warnings
        }

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of agent executions."""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "total_outputs": len(self.execution_history),
            "executions": self.execution_history
        }
