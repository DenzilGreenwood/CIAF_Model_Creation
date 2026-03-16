"""
Quick test to verify Agent Infrastructure (Phase 1)

Run with: python -m pytest ciaf/agents/tests/test_agent_infrastructure.py -v
"""

import pytest
from ciaf.agents import (
    IAMPolicy,
    PAMPolicy,
    AgentRegistry,
    AgentExecutionContext,
    AgentAction,
    create_healthcare_policies,
    create_banking_policies,
    create_example_agent_registry,
)
from datetime import datetime, timezone


class TestIAMPolicy:
    """Test IAM policy functionality."""

    def test_iam_creation(self):
        """Test creating an IAM policy."""
        policy = IAMPolicy(
            agent_id="test_agent_001",
            organization_id="test_org",
            agent_name="Test Agent",
            allowed_resources=["model_1", "db_1"],
            allowed_agents=["agent_2"],
        )

        assert policy.agent_id == "test_agent_001"
        assert "model_1" in policy.allowed_resources
        assert policy.can_access_resource("model_1")
        assert not policy.can_access_resource("model_2")

    def test_agent_call_permission(self):
        """Test inter-agent call permissions."""
        policy = IAMPolicy(
            agent_id="agent_1",
            organization_id="test_org",
            agent_name="Agent 1",
            allowed_agents=["agent_2", "agent_3"],
        )

        assert policy.can_call_agent("agent_2")
        assert not policy.can_call_agent("agent_4")

    def test_approval_requirement(self):
        """Test approval requirement flagging."""
        policy = IAMPolicy(
            agent_id="agent_1",
            organization_id="test_org",
            agent_name="Agent 1",
            approval_required_for=["high_risk_action"],
        )

        assert policy.requires_approval("high_risk_action")
        assert not policy.requires_approval("normal_action")


class TestPAMPolicy:
    """Test PAM policy functionality."""

    def test_pam_creation(self):
        """Test creating a PAM policy."""
        policy = PAMPolicy(
            agent_id="admin_agent",
            can_finalize_batches=True,
            can_approve_high_risk=True,
            max_batch_size=1000,
        )

        assert policy.can_finalize_batches
        assert policy.can_approve_high_risk
        assert policy.max_batch_size == 1000


class TestAgentRegistry:
    """Test agent registry operations."""

    def test_agent_registration(self):
        """Test registering agents."""
        registry = AgentRegistry()

        iam = IAMPolicy(
            agent_id="agent_1",
            organization_id="org_1",
            agent_name="Agent 1",
            allowed_resources=["resource_1"],
        )

        pam = PAMPolicy(agent_id="agent_1")

        agent = registry.register_agent(
            agent_id="agent_1",
            organization_id="org_1",
            agent_name="Agent 1",
            description="Test agent",
            iam_policy=iam,
            pam_policy=pam,
        )

        assert agent.agent_id == "agent_1"
        assert registry.get_agent("agent_1") is not None

    def test_agent_call_validation(self):
        """Test validating inter-agent calls."""
        registry = AgentRegistry()

        # Create agent 1 that can call agent 2
        iam1 = IAMPolicy(
            agent_id="agent_1",
            organization_id="org_1",
            agent_name="Agent 1",
            allowed_agents=["agent_2"],
        )
        pam1 = PAMPolicy(agent_id="agent_1")

        registry.register_agent(
            agent_id="agent_1",
            organization_id="org_1",
            agent_name="Agent 1",
            description="Test agent 1",
            iam_policy=iam1,
            pam_policy=pam1,
        )

        # Create agent 2
        iam2 = IAMPolicy(
            agent_id="agent_2",
            organization_id="org_1",
            agent_name="Agent 2",
        )
        pam2 = PAMPolicy(agent_id="agent_2")

        registry.register_agent(
            agent_id="agent_2",
            organization_id="org_1",
            agent_name="Agent 2",
            description="Test agent 2",
            iam_policy=iam2,
            pam_policy=pam2,
        )

        # Validate call
        allowed, error = registry.validate_agent_call("agent_1", "agent_2")
        assert allowed
        assert error is None

        # Validate invalid call
        allowed, error = registry.validate_agent_call("agent_2", "agent_1")
        assert not allowed
        assert error is not None

    def test_org_agents_listing(self):
        """Test listing agents by organization."""
        registry = AgentRegistry()

        for i in range(3):
            iam = IAMPolicy(
                agent_id=f"agent_{i}",
                organization_id="org_1",
                agent_name=f"Agent {i}",
            )
            pam = PAMPolicy(agent_id=f"agent_{i}")

            registry.register_agent(
                agent_id=f"agent_{i}",
                organization_id="org_1",
                agent_name=f"Agent {i}",
                description=f"Test agent {i}",
                iam_policy=iam,
                pam_policy=pam,
            )

        agents = registry.get_org_agents("org_1")
        assert len(agents) == 3


class TestExecutionContext:
    """Test agent execution context tracking."""

    def test_context_creation(self):
        """Test creating execution context."""
        context = AgentExecutionContext(
            session_id="session_1",
            task_batch_id="batch_1",
            organization_id="org_1",
        )

        assert context.session_id == "session_1"
        assert context.status == "running"

    def test_recording_actions(self):
        """Test recording agent actions."""
        context = AgentExecutionContext(
            session_id="session_1",
            task_batch_id="batch_1",
            organization_id="org_1",
        )

        action = AgentAction(
            agent_id="agent_1",
            action_type="inference",
            timestamp=datetime.now().isoformat(),
            input_hash="abc123",
            output_hash="def456",
            status="success",
        )

        context.add_agent_action(action)
        assert len(context.actions) == 1
        assert context.success_count == 1

    def test_agent_sequence(self):
        """Test tracking agent execution sequence."""
        context = AgentExecutionContext(
            session_id="session_1",
            task_batch_id="batch_1",
            organization_id="org_1",
        )

        agents = ["agent_1", "agent_2", "agent_1", "agent_3"]
        for i, agent_id in enumerate(agents):
            action = AgentAction(
                agent_id=agent_id,
                action_type="inference",
                timestamp=datetime.now().isoformat(),
                input_hash=f"in_{i}",
                output_hash=f"out_{i}",
            )
            context.add_agent_action(action)

        sequence = context.get_agent_sequence()
        # Should be unique ordered sequence: [agent_1, agent_2, agent_3]
        assert sequence == ["agent_1", "agent_2", "agent_3"]


class TestExamplePolicies:
    """Test example policy creation."""

    def test_healthcare_policies(self):
        """Test healthcare policy creation."""
        iam_dict, pam_dict = create_healthcare_policies()

        assert "healthcare_reader" in iam_dict
        assert "analysis_agent" in iam_dict
        assert "recommendation_agent" in iam_dict

        # Verify reader can only call analysis agent
        reader = iam_dict["healthcare_reader"]
        assert reader.can_call_agent("analysis_agent_001")
        assert not reader.can_call_agent("recommendation_agent_001")

    def test_banking_policies(self):
        """Test banking policy creation."""
        iam_dict, pam_dict = create_banking_policies()

        assert "banking_analyst" in iam_dict
        assert "credit_decision" in iam_dict
        assert "risk_override" in iam_dict

        # Verify privilege escalation
        risk_agent_pam = pam_dict["risk_override"]
        assert risk_agent_pam.can_finalize_batches
        assert risk_agent_pam.can_approve_high_risk

    def test_example_registry(self):
        """Test creating example registry."""
        registry = create_example_agent_registry()

        # Verify healthcare agents
        hc_agents = registry.get_org_agents("healthcare_org_001")
        assert len(hc_agents) == 3

        # Verify banking agents
        bank_agents = registry.get_org_agents("banking_org_001")
        assert len(bank_agents) == 3

        # Verify healthcare hierarchy
        reader = registry.get_agent("healthcare_reader_001")
        analysis = registry.get_agent("analysis_agent_001")

        allowed, _ = registry.validate_agent_call(
            "healthcare_reader_001", "analysis_agent_001"
        )
        assert allowed

        # Verify banking hierarchy
        allowed, _ = registry.validate_agent_call(
            "banking_analyst_001", "credit_decision_agent_001"
        )
        assert allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
