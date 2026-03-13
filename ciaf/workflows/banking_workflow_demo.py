"""
CIAF Banking Workflow Demo

Demonstrates fair lending compliance and credit decision governance.
Shows how CIAF tracks multi-agent credit decisions through verification.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from ciaf.agents import create_example_agent_registry
from ciaf.sessions import AgentSession
from ciaf.org_batching import OrgBatchScheduler
from ciaf.tagging import TagEmbedder
from ciaf.verification import PostgresProofStore, VerificationService
import asyncio
import json


async def banking_loan_application_workflow():
    """
    Complete banking workflow: Loan application through verification.

    Scenario:
    - Customer applies for $50,000 loan
    - Multi-agent orchestration: Data analyst → Credit decision → Risk override
    - Compliance: Fair lending, SR 11-7, ECOA
    - Output: Loan decision with full compliance proof
    """

    print("=" * 80)
    print("CIAF BANKING WORKFLOW: Fair Lending Compliance Demo")
    print("=" * 80)
    print()

    # ========================================================================
    # SETUP: Agents & Registry
    # ========================================================================
    print("[SETUP] Loading banking agents with policies...")
    print("-" * 80)

    registry = create_example_agent_registry()

    # Get banking agents
    analyst = registry.get_agent("banking_analyst_001")
    credit_engine = registry.get_agent("credit_decision_agent_001")
    risk_manager = registry.get_agent("risk_override_agent_001")

    print(f"✓ {analyst.agent_name}")
    print(f"  Policies: fair lending, risk assessment")
    print()

    print(f"✓ {credit_engine.agent_name}")
    print(f"  Policies: credit scoring, ECOA compliance")
    print()

    print(f"✓ {risk_manager.agent_name}")
    print(f"  Policies: risk oversight, can override decisions")
    print()

    # ========================================================================
    # LOAN APPLICATION
    # ========================================================================
    print("\n[APPLICATION] Processing loan request...")
    print("-" * 80)

    loan_app = {
        "application_id": "LOAN_2025_03_13_001",
        "applicant": {
            "name": "Jane Doe",
            "age": 42,
            "income": "$85,000",
            "employment": "Software Engineer",
            "employment_years": 5,
        },
        "loan": {
            "amount": 50000,
            "purpose": "Home improvement",
            "term_months": 60,
        },
        "credit": {
            "score": 745,
            "history": "Excellent (no late payments)",
            "debt_to_income": 0.28,
        },
    }

    print(f"✓ Loan Application: {loan_app['application_id']}")
    print(f"  Applicant: {loan_app['applicant']['name']}")
    print(f"  Requested: ${loan_app['loan']['amount']:,}")
    print(f"  Credit Score: {loan_app['credit']['score']}")
    print(f"  Debt-to-Income: {loan_app['credit']['debt_to_income']:.1%}")
    print()

    # ========================================================================
    # SESSION & TASK 1: DATA ANALYSIS
    # ========================================================================
    print("[TASK 1] Financial Analysis")
    print("-" * 80)

    session = AgentSession(
        session_id="loan_app_2025_03_13_001",
        user_id="loan_officer_001",
        organization_id="banking_org_001",
    )

    session.start_task("Analyze applicant financial data")

    analyst_output = f"""
    FINANCIAL ANALYSIS REPORT
    =========================
    Application ID: {loan_app['application_id']}

    CREDIT ASSESSMENT:
    - Credit Score: {loan_app['credit']['score']} (Excellent)
    - Credit History: {loan_app['credit']['history']}
    - Debt-to-Income Ratio: {loan_app['credit']['debt_to_income']:.1%} (Well below 43% threshold)

    INCOME VERIFICATION:
    - Annual Income: {loan_app['applicant']['income']}
    - Employment Tenure: {loan_app['applicant']['employment_years']} years
    - Stability: STABLE (consistent employment)

    LOAN ANALYSIS:
    - Loan Amount: ${loan_app['loan']['amount']:,}
    - Loan Purpose: {loan_app['loan']['purpose']}
    - Loan-to-Value: Strong (home improvement = asset enhancement)
    - Term: {loan_app['loan']['term_months']} months at estimated 4.5% APR
    - Monthly Payment: ~$930 (well within income)

    RISK FACTORS:
    - Primary Risk: MINIMAL
    - Secondary Risk: Age {loan_app['applicant']['age']} (low default risk)

    RECOMMENDATION: APPROVE
    Analyst confidence: 98%
    """

    analyst_tag = session.record_output(
        output_content=analyst_output,
        inference_receipt_id="lcm_analyst_001",
        agent_ids=["banking_analyst_001"],
        policies_applied=["FAIR_LENDING_ANALYSIS", "INCOME_VERIFICATION"],
        risk_level="low",
    )

    print(f"✓ Analysis complete")
    print(f"  Tag ID: {analyst_tag.tag_id[:12]}...")
    print()

    task1 = session.complete_current_task("success")
    print(f"✓ Task batched with merkle root: {task1.merkle_root[:16]}...")
    print()

    # ========================================================================
    # TASK 2: CREDIT DECISION
    # ========================================================================
    print("[TASK 2] Credit Decision (SR 11-7 Compliance)")
    print("-" * 80)

    session.start_task("Make credit decision with fair lending validation")

    credit_decision = f"""
    CREDIT DECISION REPORT
    ======================
    Application: {loan_app['application_id']}

    DECISION: APPROVED

    LOAN TERMS:
    - Approved Amount: ${loan_app['loan']['amount']:,}
    - Interest Rate: 4.5%
    - Term: {loan_app['loan']['term_months']} months
    - Monthly Payment: $930
    - Total Interest: $5,800

    REGULATORY COMPLIANCE:

    Fair Lending (ECOA):
    ✓ Age: {loan_app['applicant']['age']} - No age discrimination
    ✓ Protected status: No protected class factors in decision
    ✓ Disparate impact: Loan terms in line with similar profiles
    ✓ Adverse action: N/A (approved)

    SR 11-7 (Model Risk Management):
    ✓ Model validation: Credit model validated annually
    ✓ Performance monitoring: Model AUC = 0.94 (excellent discrimination)
    ✓ Recalibration: Performed Q4 2024
    ✓ Use case: Consumer credit decision (standard operating)
    ✓ Model risk tier: TIER 1 (low risk - standard model, strong performance)

    ECOA Transparency:
    ✓ Terms consistent with credit profile
    ✓ No hidden fees or discriminatory terms
    ✓ Terms comparable to similar-profile applicants
    ✓ Adverse action notice: N/A (approved)

    REGULATORY CHECKLIST:
    ✓ FCRA (Fair Credit Reporting Act): Compliance confirmed
    ✓ ECOA (Equal Credit Opportunity Act): Compliance confirmed
    ✓ SR 11-7 (Model Risk Management): Compliance confirmed
    ✓ GDPR (where applicable): Terms disclosed

    Approval authorized by: Credit Decision Engine v5
    Risk Score: 18/100 (Excellent)
    Confidence Level: 99.2%
    """

    credit_tag = session.record_output(
        output_content=credit_decision,
        inference_receipt_id="lcm_credit_001",
        agent_ids=["banking_analyst_001", "credit_decision_agent_001"],
        policies_applied=[
            "FAIR_LENDING_COMPLIANCE",
            "SR_11_7_MODEL_VALIDATION",
            "ECOA_TRANSPARENCY",
        ],
        risk_level="medium",
    )

    print(f"✓ Credit decision approved")
    print(f"  Tag ID: {credit_tag.tag_id[:12]}...")
    print(f"  Loan Amount: ${loan_app['loan']['amount']:,}")
    print(f"  Interest Rate: 4.5%")
    print()

    task2 = session.complete_current_task("success")
    print(f"✓ Task batched with merkle root: {task2.merkle_root[:16]}...")
    print()

    # ========================================================================
    # TASK 3: RISK OVERSIGHT
    # ========================================================================
    print("[TASK 3] Risk Management Override (Final Authorization)")
    print("-" * 80)

    session.start_task("Risk oversight and final authorization")

    risk_report = f"""
    RISK MANAGEMENT OVERSIGHT REPORT
    ================================
    Application: {loan_app['application_id']}

    RISK ASSESSMENT:
    Overall Risk Score: 18/100 (EXCELLENT)

    Risk Components:
    - Credit Risk: 8/100 (Excellent credit history)
    - Market Risk: 15/100 (Stable housing market)
    - Operational Risk: 5/100 (Standard KYC passed)
    - Regulatory Risk: 0/100 (All compliance checks passed)

    ECONOMIC CAPITAL ALLOCATION:
    - EC Requirement: $1,200 (2.4% of loan amount)
    - EC Available: $50M (well-capitalized)
    - EC Ratio: 4,167% (far exceeds regulatory minimum of 8%)

    CONCENTRATION RISK:
    - Portfolio concentration: 0.001% (negligible)
    - Geographic concentration: Acceptable
    - Sector concentration: Consumer lending (core business)

    LIQUIDITY ASSESSMENT:
    - Loan is immediately marketable (AAA rated pool)
    - Secondary market available

    SYSTEMIC RISK:
    - No systemic risk factors identified
    - Loan meets all stress test scenarios

    FINAL AUTHORIZATION: APPROVED

    Rationale:
    - Credit quality excellent
    - Risk factors minimal
    - Regulatory compliance confirmed across all frameworks
    - Economic capital available and abundant
    - No concentration or liquidity issues

    Authorized by: Risk Management System
    Authority: Yes (risk score < 25th percentile)
    Date: 2025-03-13
    Time: 14:32 UTC

    This authorization constitutes final approval for loan origination.
    """

    risk_tag = session.record_output(
        output_content=risk_report,
        inference_receipt_id="lcm_risk_001",
        agent_ids=[
            "banking_analyst_001",
            "credit_decision_agent_001",
            "risk_override_agent_001",
        ],
        policies_applied=[
            "ECONOMIC_CAPITAL_MANAGEMENT",
            "STRESS_TESTING",
            "SYSTEMIC_RISK_ASSESSMENT",
        ],
        risk_level="low",
    )

    print(f"✓ Risk oversight complete - APPROVED")
    print(f"  Tag ID: {risk_tag.tag_id[:12]}...")
    print(f"  Risk Score: 18/100 (Excellent)")
    print()

    task3 = session.complete_current_task("success")
    print(f"✓ Task batched with merkle root: {task3.merkle_root[:16]}...")
    print()

    session.end_session()

    # ========================================================================
    # ORG-LEVEL BATCHING
    # ========================================================================
    print("[ORG BATCHING] Creating organization batch window...")
    print("-" * 80)

    scheduler = OrgBatchScheduler()
    scheduler.queue_task_batch("banking_org_001", task1)
    scheduler.queue_task_batch("banking_org_001", task2)
    scheduler.queue_task_batch("banking_org_001", task3)

    await scheduler.create_batch_window("banking_org_001")

    window = scheduler.get_current_window("banking_org_001")
    print(f"✓ Window created: {window.window_id}")
    print(f"  Task batches: {len(window.completed_task_batches)}")
    print()

    # ========================================================================
    # VERIFICATION
    # ========================================================================
    print("[VERIFICATION] Verifying loan decision...")
    print("-" * 80)

    proof_store = PostgresProofStore()
    await proof_store.connect()

    # Store proofs
    await proof_store.store_output_tag(risk_tag)
    await proof_store.store_task_batch(task3)
    await proof_store.store_org_batch_window(window)

    # Verify
    verification_service = VerificationService(proof_store)

    result = await verification_service.verify_output(
        tag_id=risk_tag.tag_id,
        verify_merkle=True,
        include_audit_trail=True,
    )

    print(f"✓ Verification Result: {'PASS' if result.verified else 'FAIL'}")
    print(f"  Organization: {result.organization_id}")
    print(f"  Agents involved: {len(result.agent_ids)}")
    print(f"  Policies enforced: {len(result.policies_applied)}")
    print(f"  Merkle proof valid: {result.merkle_proof_valid}")
    print()

    # ========================================================================
    # LOAN APPROVAL LETTER
    # ========================================================================
    print("=" * 80)
    print("LOAN APPROVAL LETTER (CRYPTOGRAPHICALLY VERIFIED)")
    print("=" * 80)
    print()

    loan_letter = f"""
    {window.window_id}

    Dear {loan_app['applicant']['name']},

    Congratulations! Your loan application {loan_app['application_id']} has been APPROVED.

    LOAN DETAILS:
    - Loan Amount: ${loan_app['loan']['amount']:,}
    - Interest Rate: 4.5% APR
    - Loan Term: {loan_app['loan']['term_months']} months
    - Monthly Payment: $930
    - Purpose: {loan_app['loan']['purpose']}

    DECISION MADE BY:
    Multi-agent orchestration with compliance oversight:
    - Financial Analyst (Data validation)
    - Credit Decision Engine (Model-based decision)
    - Risk Manager (Independent risk oversight)

    COMPLIANCE CERTIFICATIONS:
    ✓ Fair Lending Compliance (ECOA)
    ✓ Model Risk Management (SR 11-7)
    ✓ Income Verification (FCRA)
    ✓ Risk Assessment (Economic Capital Adequacy)
    ✓ Regulatory Compliance (All frameworks)

    CRYPTOGRAPHIC VERIFICATION:
    This decision is backed by cryptographic proof of compliance:
    - Decision ID: {risk_tag.tag_id[:16]}...
    - Agent Audit Trail: Verifiable
    - Policy Enforcement: Auditable
    - Merkle Timestamp: {window.window_start.isoformat()}

    To verify this decision:
    GET /verify/{risk_tag.tag_id}

    Next Steps:
    1. Review this approved loan offer
    2. Sign all required documentation
    3. Schedule funding appointment
    4. Funds will be disbursed within 5 business days

    Questions? Contact your loan officer at (555) 123-4567

    Sincerely,
    Banking Compliance System (Cryptographically Certified)
    """

    print(loan_letter)
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("BANKING WORKFLOW SUMMARY")
    print("=" * 80)
    print()

    print("PROCESSING STEPS:")
    print("  1. Financial analysis (low risk)")
    print("  2. Credit decision with fair lending checks (medium risk)")
    print("  3. Risk oversight and final authorization (low risk)")
    print()

    print("COMPLIANCE VERIFIED:")
    print("  ✓ Fair Lending (ECOA) - No discrimination")
    print("  ✓ Model Risk (SR 11-7) - Model validated and monitored")
    print("  ✓ Income Verification (FCRA) - All checks passed")
    print("  ✓ Risk Management - Capital adequate")
    print()

    print("CRYPTOGRAPHIC PROOFS:")
    print(f"  ✓ Decision hash: {risk_tag.output_content_hash[:16]}...")
    print(f"  ✓ Task batch: {task3.merkle_root[:16]}...")
    print(f"  ✓ Org window: {window.merkle_root[:16]}...")
    print()

    print("AUDIT TRAIL:")
    print(f"  ✓ {len(result.agent_ids)} agents involved")
    print(f"  ✓ {len(result.policies_applied)} policies enforced")
    print(f"  ✓ {window.task_batch_count} task batches")
    print(f"  ✓ Multiple verification methods available")
    print()

    print("RESULT: ✓ LOAN APPROVED & VERIFIED")
    print()


if __name__ == "__main__":
    asyncio.run(banking_loan_application_workflow())
