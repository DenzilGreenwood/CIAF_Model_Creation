"""End-to-end demo workflows showcasing CIAF functionality."""

import sys
import io

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from agents_domain import AgentOrchestrator
from ciaf_client import CIAFClient
from llm_providers import LLMProviderFactory
import json
from datetime import datetime


def demo_banking_workflow():
    """Demo: Complete banking credit analysis workflow with CIAF verification."""
    print("\n" + "="*80)
    print("🏦 BANKING WORKFLOW DEMO - Credit Analysis with CIAF Verification")
    print("="*80)

    # Initialize
    org_id = "banking_org_001"
    llm = LLMProviderFactory.create_auto()
    orchestrator = AgentOrchestrator(org_id, llm)
    ciaf_client = CIAFClient()

    print(f"\n✅ Initialized LLM Provider: {llm.__class__.__name__}")
    print(f"✅ Organization: {org_id}")

    # Create banking agent
    analyst = orchestrator.create_banking_agent("agent_credit_analyst_001", "credit_analyst")
    print(f"✅ Created agent: {analyst.agent_id} ({analyst.role})")

    # Demo 1: Analyze credit applications
    print("\n" + "-"*80)
    print("DEMO 1: Credit Application Analysis")
    print("-"*80)

    customer_profiles = [
        {
            "annual_income": 85000,
            "credit_score": 750,
            "years_employed": 8,
            "current_debt": 15000,
            "payment_history": "Excellent (>2 years history)",
            "loan_amount": 50000
        },
        {
            "annual_income": 45000,
            "credit_score": 620,
            "years_employed": 2,
            "current_debt": 25000,
            "payment_history": "Fair (late payments 1 year ago)",
            "loan_amount": 30000
        }
    ]

    for i, profile in enumerate(customer_profiles, 1):
        print(f"\n📋 Customer {i}:")
        result = analyst.analyze_credit_application(profile)

        print(f"   Output excerpt: {result['output'][:200]}...")
        print(f"   Tag ID: {result['tag_id']}")
        print(f"   Policies Applied: {', '.join(result['policies_applied'])}")
        print(f"   Verification Status: {result['verification'].get('status', 'N/A')}")

    # Demo 2: Generate recommendations with compliance tracking
    print("\n" + "-"*80)
    print("DEMO 2: Credit Recommendations with Compliance Tracking")
    print("-"*80)

    scenarios = [
        "High-income customer with excellent credit history requesting substantial loan increase",
        "Recently-employed customer (3 months) applying for mortgage with limited credit history"
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}:")
        result = analyst.generate_credit_recommendation(scenario)

        print(f"   Recommendation: {result['output'][:200]}...")
        print(f"   Tag ID: {result['tag_id']}")
        print(f"   Compliance Policies: {', '.join(result['policies_applied'])}")

    # Demo 3: Verify past outputs
    print("\n" + "-"*80)
    print("DEMO 3: Verify Previously Generated Outputs")
    print("-"*80)

    if analyst.execution_history:
        latest_execution = analyst.execution_history[0]
        tag_id = latest_execution["tag_id"]

        print(f"\n🔍 Verifying tag: {tag_id}")
        verification = analyst.verify_past_output(tag_id)

        print(f"   Status: {verification['status']}")
        print(f"   Risk Level: {verification['risk_level']}")
        print(f"   Merkle Proof Valid: {verification['merkle_proof_valid']}")
        if verification['issues']:
            print(f"   Issues: {', '.join(verification['issues'])}")
        if verification['warnings']:
            print(f"   Warnings: {', '.join(verification['warnings'])}")

    #Demo 4: Get compliance overview
    print("\n" + "-"*80)
    print("DEMO 4: Compliance Dashboard")
    print("-"*80)

    compliance = orchestrator.get_compliance_overview()
    print(f"\n📊 System Compliance:")
    print(f"   Total Outputs: {compliance['total_outputs']}")
    print(f"   Verified Outputs: {compliance['verified_outputs']}")
    print(f"   Verification Rate: {compliance['verification_rate']:.1f}%")
    print(f"   Active Agents: {compliance['agents_count']}")

    return orchestrator


def demo_healthcare_workflow():
    """Demo: Complete healthcare clinical decision support workflow with CIAF verification."""
    print("\n" + "="*80)
    print("🏥 HEALTHCARE WORKFLOW DEMO - Clinical Decision Support with CIAF Verification")
    print("="*80)

    # Initialize
    org_id = "healthcare_org_001"
    llm = LLMProviderFactory.create_auto()
    orchestrator = AgentOrchestrator(org_id, llm)

    print(f"\n✅ Initialized LLM Provider: {llm.__class__.__name__}")
    print(f"✅ Organization: {org_id}")

    # Create healthcare agent
    clinician = orchestrator.create_healthcare_agent("agent_clinician_001", "clinical_assistant")
    print(f"✅ Created agent: {clinician.agent_id} ({clinician.role})")

    # Demo 1: Analyze patient cases
    print("\n" + "-"*80)
    print("DEMO 1: Patient Case Analysis")
    print("-"*80)

    patient_cases = [
        {
            "age": 55,
            "gender": "M",
            "medical_history": "Hypertension, Type 2 Diabetes",
            "chief_complaint": "Shortness of breath",
            "symptoms": "Dyspnea on exertion, chest tightness, fatigue",
            "vital_signs": "BP 155/95, HR 92, RR 18, O2 sat 94%",
            "lab_results": "Elevated troponin, BNP 350"
        },
        {
            "age": 28,
            "gender": "F",
            "medical_history": "No significant history",
            "chief_complaint": "Acute headache",
            "symptoms": "Sudden severe headache, neck stiffness, photophobia",
            "vital_signs": "BP 128/82, HR 88, RR 16, Temp 38.5°C",
            "lab_results": "Pending"
        }
    ]

    for i, case in enumerate(patient_cases, 1):
        print(f"\n👤 Patient Case {i}:")
        result = clinician.analyze_patient_case(case)

        print(f"   Assessment: {result['output'][:200]}...")
        print(f"   Tag ID: {result['tag_id']}")
        print(f"   Policies Applied: {', '.join(result['policies_applied'])}")
        print(f"   Verification Status: {result['verification'].get('status', 'N/A')}")

    # Demo 2: Treatment recommendations
    print("\n" + "-"*80)
    print("DEMO 2: Treatment Recommendations with Compliance Tracking")
    print("-"*80)

    clinical_scenarios = [
        "65-year-old hypertensive patient presenting with AF and rapid ventricular response",
        "28-year-old diabetic patient with HbA1c 9.5% despite metformin monotherapy"
    ]

    for i, scenario in enumerate(clinical_scenarios, 1):
        print(f"\n💊 Scenario {i}:")
        result = clinician.generate_treatment_recommendation(scenario)

        print(f"   Recommendation: {result['output'][:200]}...")
        print(f"   Tag ID: {result['tag_id']}")
        print(f"   Policies Applied: {', '.join(result['policies_applied'])}")

    # Demo 3: Verify outputs
    print("\n" + "-"*80)
    print("DEMO 3: Verify Clinical Recommendations")
    print("-"*80)

    if clinician.execution_history:
        latest_execution = clinician.execution_history[0]
        tag_id = latest_execution["tag_id"]

        print(f"\n🔍 Verifying tag: {tag_id}")
        verification = clinician.verify_past_output(tag_id)

        print(f"   Status: {verification['status']}")
        print(f"   Risk Level: {verification['risk_level']}")
        print(f"   Merkle Proof Valid: {verification['merkle_proof_valid']}")
        if verification['issues']:
            print(f"   Issues: {', '.join(verification['issues'])}")

    # Demo 4: Compliance overview
    print("\n" + "-"*80)
    print("DEMO 4: Compliance Dashboard")
    print("-"*80)

    compliance = orchestrator.get_compliance_overview()
    print(f"\n📊 System Compliance:")
    print(f"   Total Clinical Outputs: {compliance['total_outputs']}")
    print(f"   Verified Outputs: {compliance['verified_outputs']}")
    print(f"   Verification Rate: {compliance['verification_rate']:.1f}%")
    print(f"   Active Clinical Agents: {compliance['agents_count']}")

    return orchestrator


def demo_multi_agent_collaboration():
    """Demo: Multi-agent system with cross-domain collaboration."""
    print("\n" + "="*80)
    print("🤝 MULTI-AGENT COLLABORATION DEMO - Banking & Healthcare Together")
    print("="*80)

    org_id = "multi_org_001"
    llm = LLMProviderFactory.create_auto()
    orchestrator = AgentOrchestrator(org_id, llm)

    print(f"\n✅ Organization: {org_id}")

    # Create agents from both domains
    banker = orchestrator.create_banking_agent("agent_banker_001", "loan_officer")
    clinician = orchestrator.create_healthcare_agent("agent_doctor_001", "physician")

    print(f"✅ Banking Agent: {banker.agent_id}")
    print(f"✅ Healthcare Agent: {clinician.agent_id}")

    # Scenario: Medical debt analysis
    print("\n" + "-"*80)
    print("💰 Scenario: Medical Debt Analysis for Loan Decision")
    print("-"*80)

    print("\n1️⃣  Clinician generates medical assessment:")
    medical_result = clinician.analyze_patient_case({
        "age": 45,
        "gender": "F",
        "medical_history": "Chronic condition requiring ongoing treatment",
        "chief_complaint": "High healthcare costs",
        "symptoms": "Financial hardship from medical expenses",
        "vital_signs": "N/A",
        "lab_results": "N/A"
    })
    print(f"   Medical Assessment Tag: {medical_result['tag_id']}")

    print("\n2️⃣  Banker uses medical assessment for credit decision:")
    credit_result = banker.generate_credit_recommendation(
        "Patient requires medical financing. Assessment shows chronic condition requiring ongoing treatment."
    )
    print(f"   Credit Decision Tag: {credit_result['tag_id']}")

    # System summary
    print("\n" + "-"*80)
    print("📈 Multi-Agent System Summary")
    print("-"*80)

    summary = orchestrator.get_system_summary()
    print(f"\n👥 Agents: {summary['total_agents']}")
    for agent_id, agent_summary in summary['agents'].items():
        print(f"   - {agent_id}: {agent_summary['total_outputs']} outputs generated")

    compliance = orchestrator.get_compliance_overview()
    print(f"\n✅ Verification Rate: {compliance['verification_rate']:.1f}%")
    print(f"📊 Total Outputs Tracked: {compliance['total_outputs']}")


if __name__ == "__main__":
    print("\n🚀 CIAF MVP - End-to-End Demonstrations")
    print("="*80)

    try:
        # Run demos
        banking_orchestrator = demo_banking_workflow()
        healthcare_orchestrator = demo_healthcare_workflow()
        demo_multi_agent_collaboration()

        print("\n" + "="*80)
        print("✅ All demos completed successfully!")
        print("="*80)
        print("\n📊 Generated tagged outputs are now:")
        print("   - Verified by CIAF Verification Service")
        print("   - Stored with Merkle proofs")
        print("   - Auditable through dashboard")
        print("   - Compliant with policies")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
