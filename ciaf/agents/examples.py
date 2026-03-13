"""
Example Agent Policies and Registry Setup

Provides ready-to-use policy examples for different industries.
These are templates that organizations can customize.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from .agent_policies import IAMPolicy, PAMPolicy
from .agent_registry import AgentRegistry, Agent
from datetime import datetime


def create_healthcare_policies() -> tuple[dict, dict]:
    """
    Create example IAM/PAM policies for a healthcare organization.

    Healthcare example shows multi-tiered access:
    - Reader agents: Read-only access to patient data
    - Analysis agents: Can analyze but need approval for recommendations
    - Decision agents: Can make clinical recommendations

    Returns:
        (iam_policies_dict, pam_policies_dict)
    """

    # ==================== HEALTHCARE READER AGENT ====================
    # Reads patient data, anonymizes it, cannot make recommendations
    healthcare_reader_iam = IAMPolicy(
        agent_id="healthcare_reader_001",
        organization_id="healthcare_org_001",
        agent_name="Patient Data Reader",
        description="Safely reads and anonymizes patient data for analysis",
        allowed_resources=[
            "llama2-7b",  # Small model for reading
            "patient_database_read",
            "medical_nlp_model",
        ],
        allowed_agents=["analysis_agent_001"],  # Can only call analysis agent
        rate_limits={
            "inferences_per_hour": 500,
            "api_calls_per_minute": 50,
            "concurrent_sessions": 5,
        },
        data_scopes=["pii_safe", "anonymized_patient_data"],
        approval_required_for=[],  # No approval needed for reading
        allowed_hours="24/7",
    )

    healthcare_reader_pam = PAMPolicy(
        agent_id="healthcare_reader_001",
        can_create_agents=False,
        can_finalize_batches=False,
        can_access_audit_history=False,
        max_batch_size=50,
        can_approve_high_risk=False,
        can_escalate_to_human=False,
    )

    # ==================== HEALTHCARE ANALYSIS AGENT ====================
    # Analyzes data, detects patterns, needs approval for clinical recommendations
    analysis_agent_iam = IAMPolicy(
        agent_id="analysis_agent_001",
        organization_id="healthcare_org_001",
        agent_name="Medical Analysis Agent",
        description="Analyzes clinical data and detects patterns for physician review",
        allowed_resources=[
            "llama2-13b",  # Larger model for analysis
            "medical_nlp_model",
            "clinical_decision_tree_engine",
        ],
        allowed_agents=["recommendation_agent_001"],  # Can escalate to decision agent
        rate_limits={
            "inferences_per_hour": 1000,
            "api_calls_per_minute": 100,
        },
        data_scopes=["pii_safe", "anonymized_patient_data", "clinical_metadata"],
        approval_required_for=["clinical_recommendation"],  # Needs approval before recommending
        allowed_hours="24/7",
    )

    analysis_agent_pam = PAMPolicy(
        agent_id="analysis_agent_001",
        can_create_agents=False,
        can_finalize_batches=False,
        can_access_audit_history=True,  # Can see history for training
        max_batch_size=100,
        can_approve_high_risk=False,
        can_escalate_to_human=True,  # Can escalate complex cases
    )

    # ==================== HEALTHCARE DECISION AGENT ====================
    # Makes clinical recommendations (requires human approval first)
    recommendation_agent_iam = IAMPolicy(
        agent_id="recommendation_agent_001",
        organization_id="healthcare_org_001",
        agent_name="Clinical Decision Agent",
        description="Makes and documents clinical recommendations after human approval",
        allowed_resources=[
            "gpt4_turbo",  # State-of-the-art for clinical decisions
            "medical_knowledge_base",
            "clinical_guidelines_database",
            "fda_adverse_event_db",
        ],
        allowed_agents=[],  # Cannot call other agents
        rate_limits={
            "inferences_per_hour": 200,  # Lower rate for high-stakes decisions
            "api_calls_per_minute": 10,
        },
        data_scopes=["all_clinical_data"],  # Has access to all data
        approval_required_for=[],  # Already approved by analysis agent
        allowed_hours="09:00-17:00",  # Daytime only (human oversight)
    )

    recommendation_agent_pam = PAMPolicy(
        agent_id="recommendation_agent_001",
        can_create_agents=False,
        can_finalize_batches=False,
        can_access_audit_history=True,
        max_batch_size=50,
        can_approve_high_risk=True,  # Can approve high-risk clinical decisions
        can_escalate_to_human=True,  # Always escalate if uncertain
        can_delegate_to_agents=[],
    )

    return (
        {
            "healthcare_reader": healthcare_reader_iam,
            "analysis_agent": analysis_agent_iam,
            "recommendation_agent": recommendation_agent_iam,
        },
        {
            "healthcare_reader": healthcare_reader_pam,
            "analysis_agent": analysis_agent_pam,
            "recommendation_agent": recommendation_agent_pam,
        },
    )


def create_banking_policies() -> tuple[dict, dict]:
    """
    Create example IAM/PAM policies for a banking organization.

    Banking example shows risk-tiered access:
    - Data analyst agents: Can analyze customer data safely
    - Credit agents: Can make credit decisions with risk assessment
    - Risk agents: Can override decisions if risk is too high

    Returns:
        (iam_policies_dict, pam_policies_dict)
    """

    # ==================== BANKING DATA ANALYST AGENT ====================
    banking_analyst_iam = IAMPolicy(
        agent_id="banking_analyst_001",
        organization_id="banking_org_001",
        agent_name="Financial Data Analyst",
        description="Analyzes customer financial data for credit assessment",
        allowed_resources=[
            "llama2-7b",
            "credit_scoring_model",
            "customer_database",
            "transaction_history_db",
        ],
        allowed_agents=["credit_decision_agent_001"],
        rate_limits={
            "inferences_per_hour": 1000,
            "api_calls_per_minute": 100,
        },
        data_scopes=["pii_safe_financial", "customer_metadata"],
        approval_required_for=[],
        allowed_hours="24/7",
    )

    banking_analyst_pam = PAMPolicy(
        agent_id="banking_analyst_001",
        can_create_agents=False,
        can_finalize_batches=False,
        can_access_audit_history=False,
        max_batch_size=500,
        can_approve_high_risk=False,
        can_escalate_to_human=False,
    )

    # ==================== BANKING CREDIT DECISION AGENT ====================
    credit_decision_iam = IAMPolicy(
        agent_id="credit_decision_agent_001",
        organization_id="banking_org_001",
        agent_name="Credit Decision Engine",
        description="Makes credit decisions with fair lending compliance (SR 11-7)",
        allowed_resources=[
            "gpt4_turbo",
            "credit_model_v5",
            "fair_lending_validator",
            "basel_iii_calculator",
        ],
        allowed_agents=["risk_override_agent_001"],  # Can escalate to risk agent
        rate_limits={
            "inferences_per_hour": 2000,
            "api_calls_per_minute": 200,
        },
        data_scopes=["all_customer_data", "regulatory_compliance_data"],
        approval_required_for=["credit_denial_for_protected_class"],  # Flag for manual review
        allowed_hours="24/7",
    )

    credit_decision_pam = PAMPolicy(
        agent_id="credit_decision_agent_001",
        can_create_agents=False,
        can_finalize_batches=False,
        can_access_audit_history=True,
        max_batch_size=1000,
        can_approve_high_risk=False,
        can_escalate_to_human=True,  # Escalate flagged decisions
    )

    # ==================== BANKING RISK OVERRIDE AGENT ====================
    risk_override_iam = IAMPolicy(
        agent_id="risk_override_agent_001",
        organization_id="banking_org_001",
        agent_name="Risk Management Agent",
        description="Risk assessment and potential decision override (high privilege)",
        allowed_resources=[
            "gpt4_turbo",
            "risk_model_v3",
            "regulatory_oracle",
            "market_risk_db",
            "operational_risk_db",
        ],
        allowed_agents=[],  # No outbound calls
        rate_limits={
            "inferences_per_hour": 500,  # Lower rate for high-stakes decisions
            "api_calls_per_minute": 50,
        },
        data_scopes=["all_data"],  # Full access
        approval_required_for=[],  # Already reviewed
        allowed_hours="09:00-17:00",  # Business hours only
    )

    risk_override_pam = PAMPolicy(
        agent_id="risk_override_agent_001",
        can_create_agents=True,  # Can create risk assessment agents
        can_finalize_batches=True,  # Can finalize batches
        can_access_audit_history=True,
        max_batch_size=2000,
        can_approve_high_risk=True,  # Can approve high-risk decisions
        can_escalate_to_human=True,  # Always escalate systemic risk
    )

    return (
        {
            "banking_analyst": banking_analyst_iam,
            "credit_decision": credit_decision_iam,
            "risk_override": risk_override_iam,
        },
        {
            "banking_analyst": banking_analyst_pam,
            "credit_decision": credit_decision_pam,
            "risk_override": risk_override_pam,
        },
    )


def create_example_agent_registry() -> AgentRegistry:
    """
    Create an example registry with healthcare and banking agents.

    Returns:
        Configured AgentRegistry with example organizations and agents
    """
    registry = AgentRegistry()

    # ==================== HEALTHCARE ORGANIZATION ====================
    hc_iam, hc_pam = create_healthcare_policies()

    registry.register_agent(
        agent_id="healthcare_reader_001",
        organization_id="healthcare_org_001",
        agent_name="Patient Data Reader",
        description="Safely reads and anonymizes patient data",
        iam_policy=hc_iam["healthcare_reader"],
        pam_policy=hc_pam["healthcare_reader"],
        tags=["reader", "pii_handling", "hipaa_trained"],
    )

    registry.register_agent(
        agent_id="analysis_agent_001",
        organization_id="healthcare_org_001",
        agent_name="Medical Analysis Agent",
        description="Analyzes clinical data and detects patterns",
        iam_policy=hc_iam["analysis_agent"],
        pam_policy=hc_pam["analysis_agent"],
        tags=["analysis", "clinical", "fda_validated"],
    )

    registry.register_agent(
        agent_id="recommendation_agent_001",
        organization_id="healthcare_org_001",
        agent_name="Clinical Decision Agent",
        description="Makes clinical recommendations after human approval",
        iam_policy=hc_iam["recommendation_agent"],
        pam_policy=hc_pam["recommendation_agent"],
        tags=["decision", "clinical", "high_privilege"],
    )

    # ==================== BANKING ORGANIZATION ====================
    bank_iam, bank_pam = create_banking_policies()

    registry.register_agent(
        agent_id="banking_analyst_001",
        organization_id="banking_org_001",
        agent_name="Financial Data Analyst",
        description="Analyzes customer financial data",
        iam_policy=bank_iam["banking_analyst"],
        pam_policy=bank_pam["banking_analyst"],
        tags=["analyst", "fair_lending", "sr11-7"],
    )

    registry.register_agent(
        agent_id="credit_decision_agent_001",
        organization_id="banking_org_001",
        agent_name="Credit Decision Engine",
        description="Makes credit decisions with regulatory compliance",
        iam_policy=bank_iam["credit_decision"],
        pam_policy=bank_pam["credit_decision"],
        tags=["decision", "credit", "regulatory_compliance"],
    )

    registry.register_agent(
        agent_id="risk_override_agent_001",
        organization_id="banking_org_001",
        agent_name="Risk Management Agent",
        description="Risk assessment and decision override",
        iam_policy=bank_iam["risk_override"],
        pam_policy=bank_pam["risk_override"],
        tags=["risk", "override", "high_privilege"],
    )

    return registry
