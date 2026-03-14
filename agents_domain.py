"""Banking and Healthcare agent implementations."""

from typing import Optional, List, Dict, Any
from agents_base import Agent
from llm_providers import LLMProvider


class BankingAgent(Agent):
    """Banking domain agent for credit analysis."""

    BANKING_POLICIES = [
        "fair_lending",
        "risk_assessment",
        "compliance_monitoring",
        "bias_detection"
    ]

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str = "credit_analyst",
        llm_provider: Optional[LLMProvider] = None
    ):
        """Initialize banking agent.

        Args:
            agent_id: Agent identifier
            organization_id: Organization ID
            role: Agent role
            llm_provider: LLM provider to use
        """
        super().__init__(
            agent_id=agent_id,
            organization_id=organization_id,
            role=role,
            policies=self.BANKING_POLICIES,
            llm_provider=llm_provider
        )

    def get_system_prompt(self) -> str:
        """Get banking system prompt."""
        return """You are a professional credit analyst for a financial institution. Your role is to:
1. Analyze customer creditworthiness based on financial metrics
2. Provide risk assessments with clear justification
3. Make recommendations on credit decisions
4. Ensure all recommendations comply with fair lending practices
5. Flag any potential biases in your analysis

Always provide:
- Clear risk rating (Low/Medium/High)
- Specific justification for your assessment
- Any concerns or red flags
- Recommended action (approve/deny/further review)

Format your response in a structured way that can be easily audited."""

    def analyze_credit_application(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a credit application.

        Args:
            customer_profile: Dictionary with customer financial data

        Returns:
            Tagged analysis with CIAF verification
        """
        prompt = f"""Analyze the following credit application:

Customer Profile:
- Annual Income: ${customer_profile.get('annual_income', 0):,.0f}
- Credit Score: {customer_profile.get('credit_score', 0)}
- Years Employment: {customer_profile.get('years_employed', 0)}
- Current Debt: ${customer_profile.get('current_debt', 0):,.0f}
- Payment History: {customer_profile.get('payment_history', 'Unknown')}
- Requested Loan Amount: ${customer_profile.get('loan_amount', 0):,.0f}

Please provide a risk assessment and recommendation."""

        return self.create_tagged_output(prompt, temperature=0.3, max_tokens=400)

    def generate_credit_recommendation(self, scenario: str) -> Dict[str, Any]:
        """Generate a credit recommendation.

        Args:
            scenario: Credit scenario description

        Returns:
            Tagged recommendation with CIAF verification
        """
        prompt = f"""Based on this scenario, provide a credit recommendation:

{scenario}

Include:
1. Risk assessment with rationale
2. Recommended credit decision
3. Any compliance considerations
4. Potential bias concerns"""

        return self.create_tagged_output(prompt, temperature=0.4, max_tokens=500)


class HealthcareAgent(Agent):
    """Healthcare domain agent for clinical decision support."""

    HEALTHCARE_POLICIES = [
        "hipaa_compliance",
        "clinical_accuracy",
        "bias_mitigation",
        "informed_consent"
    ]

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str = "clinical_assistant",
        llm_provider: Optional[LLMProvider] = None
    ):
        """Initialize healthcare agent.

        Args:
            agent_id: Agent identifier
            organization_id: Organization ID
            role: Agent role
            llm_provider: LLM provider to use
        """
        super().__init__(
            agent_id=agent_id,
            organization_id=organization_id,
            role=role,
            policies=self.HEALTHCARE_POLICIES,
            llm_provider=llm_provider
        )

    def get_system_prompt(self) -> str:
        """Get healthcare system prompt."""
        return """You are a clinical decision support assistant. Your role is to:
1. Analyze patient data and symptoms
2. Provide evidence-based clinical insights
3. Identify potential diagnoses and risk factors
4. Recommend appropriate clinical actions
5. Flag any concerning patterns or outliers

IMPORTANT DISCLAIMERS:
- This is decision SUPPORT, not a diagnosis
- Always recommend physician review
- Consider patient demographics and social factors
- Flag any potential health equity concerns
- Respect all HIPAA and privacy requirements

Format suggestions in a clear, structured way suitable for physician review."""

    def analyze_patient_case(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a patient case.

        Args:
            patient_data: Dictionary with patient clinical data

        Returns:
            Tagged analysis with CIAF verification
        """
        prompt = f"""Analyze the following patient case:

Patient Demographics:
- Age: {patient_data.get('age', 0)}
- Gender: {patient_data.get('gender', 'N/A')}
- Medical History: {patient_data.get('medical_history', 'None')}

Current Presentation:
- Chief Complaint: {patient_data.get('chief_complaint', 'N/A')}
- Symptoms: {patient_data.get('symptoms', 'N/A')}
- Vital Signs: {patient_data.get('vital_signs', 'N/A')}
- Lab Results: {patient_data.get('lab_results', 'N/A')}

Please provide a clinical assessment including:
1. Differential diagnoses
2. Risk assessment
3. Recommended workup
4. Follow-up plan"""

        return self.create_tagged_output(prompt, temperature=0.3, max_tokens=400)

    def generate_treatment_recommendation(self, clinical_scenario: str) -> Dict[str, Any]:
        """Generate a treatment recommendation.

        Args:
            clinical_scenario: Clinical scenario description

        Returns:
            Tagged recommendation with CIAF verification
        """
        prompt = f"""Based on this clinical scenario, provide treatment recommendations:

{clinical_scenario}

Include:
1. Clinical evidence basis
2. Risk-benefit analysis
3. Patient equity considerations
4. Follow-up plan
5. Any red flags or concerns"""

        return self.create_tagged_output(prompt, temperature=0.4, max_tokens=500)


class AgentOrchestrator:
    """Orchestrates multiple agents working together."""

    def __init__(self, organization_id: str, llm_provider: Optional[LLMProvider] = None):
        """Initialize orchestrator.

        Args:
            organization_id: Organization ID
            llm_provider: Shared LLM provider
        """
        self.organization_id = organization_id
        self.llm_provider = llm_provider
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent) -> None:
        """Register an agent.

        Args:
            agent: Agent to register
        """
        self.agents[agent.agent_id] = agent

    def create_banking_agent(self, agent_id: str, role: str = "credit_analyst") -> BankingAgent:
        """Create and register a banking agent."""
        agent = BankingAgent(agent_id, self.organization_id, role, self.llm_provider)
        self.register_agent(agent)
        return agent

    def create_healthcare_agent(self, agent_id: str, role: str = "clinical_assistant") -> HealthcareAgent:
        """Create and register a healthcare agent."""
        agent = HealthcareAgent(agent_id, self.organization_id, role, self.llm_provider)
        self.register_agent(agent)
        return agent

    def get_system_summary(self) -> Dict[str, Any]:
        """Get summary of all agents and their activities."""
        return {
            "organization_id": self.organization_id,
            "total_agents": len(self.agents),
            "agents": {
                agent_id: agent.get_execution_summary()
                for agent_id, agent in self.agents.items()
            }
        }

    def get_compliance_overview(self) -> Dict[str, Any]:
        """Get compliance overview across all agents."""
        total_outputs = 0
        verified_outputs = 0

        for agent in self.agents.values():
            for execution in agent.execution_history:
                total_outputs += 1
                if execution.get("verification", {}).get("status") == "verified":
                    verified_outputs += 1

        return {
            "organization_id": self.organization_id,
            "total_outputs": total_outputs,
            "verified_outputs": verified_outputs,
            "verification_rate": (verified_outputs / total_outputs * 100) if total_outputs > 0 else 0,
            "agents_count": len(self.agents),
            "agents_list": list(self.agents.keys())
        }
