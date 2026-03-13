"""
CIAF Agentic AI Governance: Complete Workflow (Phases 1-4)

Demonstrates end-to-end flow from agent execution to org-level batching.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

# ============================================================================
# WORKFLOW: Healthcare Clinical Decision with Full CIAF Governance
# ============================================================================

from ciaf.agents import (
    AgentRegistry,
    IAMPolicy,
    PAMPolicy,
    AgentExecutionContext,
    AgentAction,
    create_healthcare_policies,
)
from ciaf.sessions import AgentSession
from ciaf.org_batching import OrgBatchScheduler
from ciaf.tagging import TagEmbedder
from datetime import datetime


def complete_healthcare_workflow():
    """
    Complete healthcare workflow showing all CIAF components.

    Scenario:
    - Patient consultation session
    - Multiple agents: Reader → Analyzer → Decision
    - Outputs tagged, batched, and org-batched
    - Full merkle-proof audit trail
    """

    print("=" * 80)
    print("CIAF AGENTIC GOVERNANCE: Healthcare Clinical Decision Workflow")
    print("=" * 80)
    print()

    # ========================================================================
    # PHASE 1: AGENT INFRASTRUCTURE & POLICY
    # ========================================================================
    print("\n[PHASE 1] POLICY ENFORCEMENT")
    print("-" * 80)

    # Create organization agents with IAM/PAM policies
    iam_dict, pam_dict = create_healthcare_policies()
    registry = AgentRegistry()

    # Register agents
    reader_agent = registry.register_agent(
        agent_id="healthcare_reader_001",
        organization_id="healthcare_org_001",
        agent_name="Patient Data Reader",
        description="Safely reads and anonymizes patient data",
        iam_policy=iam_dict["healthcare_reader"],
        pam_policy=pam_dict["healthcare_reader"],
        tags=["reader", "pii_handling"],
    )

    analysis_agent = registry.register_agent(
        agent_id="analysis_agent_001",
        organization_id="healthcare_org_001",
        agent_name="Medical Analysis Agent",
        description="Analyzes clinical data and detects patterns",
        iam_policy=iam_dict["analysis_agent"],
        pam_policy=pam_dict["analysis_agent"],
        tags=["analysis", "clinical"],
    )

    recommendation_agent = registry.register_agent(
        agent_id="recommendation_agent_001",
        organization_id="healthcare_org_001",
        agent_name="Clinical Decision Agent",
        description="Makes clinical recommendations",
        iam_policy=iam_dict["recommendation_agent"],
        pam_policy=pam_dict["recommendation_agent"],
        tags=["decision", "clinical"],
    )

    print("✓ Registered 3 agents with policies:")
    print(f"  - {reader_agent.agent_name} (IAM: read-only)")
    print(f"  - {analysis_agent.agent_name} (IAM: can call recommendation agent)")
    print(f"  - {recommendation_agent.agent_name} (IAM: can approve decisions)")

    # Validate inter-agent communication
    allowed, _ = registry.validate_agent_call(
        "healthcare_reader_001", "analysis_agent_001"
    )
    print(f"\n✓ Reader → Analyzer: {'Allowed' if allowed else 'Denied'}")

    allowed, _ = registry.validate_agent_call(
        "analysis_agent_001", "recommendation_agent_001"
    )
    print(f"✓ Analyzer → Decision: {'Allowed' if allowed else 'Denied'}")

    # ========================================================================
    # PHASE 3: SESSION & TASK BATCHING
    # ========================================================================
    print("\n\n[PHASE 3] SESSION & TASK BATCHING")
    print("-" * 80)

    # Create patient consultation session
    session = AgentSession(
        session_id="patient_consult_2025_03_13_001",
        user_id="physician_001",
        organization_id="healthcare_org_001",
    )

    print("✓ Created session: {session.session_id}")
    print(f"  User: {session.user_id}")
    print()

    # ---- TASK 1: Data Reading Phase ----
    print("Task 1: Patient Data Review")
    session.start_task("Read and anonymize patient data")

    # Reader agent output
    patient_data_summary = """
    Patient ID: P12345 (anonymized)
    Age: 52, Gender: M
    Chief Complaint: Elevated blood pressure
    Recent Labs: Creatinine elevated, eGFR 45
    Current Medications: Metoprolol
    """

    reader_tag = session.record_output(
        output_content=patient_data_summary,
        inference_receipt_id="lcm_reader_001",
        agent_ids=["healthcare_reader_001"],
        policies_applied=["HIPAA_COMPLIANT", "PII_ANONYMIZATION"],
        risk_level="medium",
    )

    print(f"✓ Reader output tagged: {reader_tag.tag_id[:12]}...")
    task1 = session.complete_current_task("success")
    print(f"✓ Task 1 completed with merkle root: {task1.merkle_root[:16]}...")
    print()

    # ---- TASK 2: Analysis Phase ----
    print("Task 2: Clinical Analysis")
    session.start_task("Analyze clinical findings")

    # Analyzer agent output
    clinical_analysis = """
    Analysis Results:
    - Hypertension with chronic kidney disease (Stage 3b)
    - Likely secondary hypertension due to CKD
    - Cardiovascular risk: Moderate
    - Recommendation needed for therapy adjustment
    - Flag: Requires specialist review (eGFR < 45)
    """

    analysis_tag = session.record_output(
        output_content=clinical_analysis,
        inference_receipt_id="lcm_analysis_001",
        agent_ids=["healthcare_reader_001", "analysis_agent_001"],
        policies_applied=["FDA_SaMD", "ISO_14971_RISK_MGMT"],
        risk_level="high",
    )

    print(f"✓ Analysis output tagged: {analysis_tag.tag_id[:12]}...")
    task2 = session.complete_current_task("success")
    print(f"✓ Task 2 completed with merkle root: {task2.merkle_root[:16]}...")
    print()

    # ---- TASK 3: Decision Phase ----
    print("Task 3: Clinical Decision")
    session.start_task("Make treatment recommendation")

    # Decision agent output
    clinical_recommendation = """
    CLINICAL RECOMMENDATION
    ----------------------
    Primary Treatment: ACE inhibitor initiation
    Rationale: CKD + Hypertension, renal protective
    Dose: Lisinopril 10mg daily
    Monitoring: Renal function in 2 weeks
    Escalation: Requires physician review before implementation
    Risk Level: HIGH
    """

    decision_tag = session.record_output(
        output_content=clinical_recommendation,
        inference_receipt_id="lcm_decision_001",
        agent_ids=[
            "healthcare_reader_001",
            "analysis_agent_001",
            "recommendation_agent_001",
        ],
        policies_applied=["CLINICAL_VALIDATION", "PHYSICIAN_OVERSIGHT"],
        risk_level="critical",
    )

    print(f"✓ Decision output tagged: {decision_tag.tag_id[:12]}...")
    task3 = session.complete_current_task("success")
    print(f"✓ Task 3 completed with merkle root: {task3.merkle_root[:16]}...")

    session.end_session()
    print("\n✓ Session ended")

    session_summary = session.get_session_summary()
    print(f"\nSession Summary:")
    print(f"  - Duration: {session_summary['duration_seconds']:.1f} seconds")
    print(f"  - Tasks completed: {session_summary['completed_tasks']}")
    print(f"  - Total outputs: {session_summary['total_outputs']}")

    # ========================================================================
    # PHASE 2: OUTPUT TAGGING (embedded in session above, show extraction)
    # ========================================================================
    print("\n\n[PHASE 2] OUTPUT TAGGING & EMBEDDING")
    print("-" * 80)

    # Show tag embedding
    embedded = TagEmbedder.embed_in_text(
        clinical_recommendation, decision_tag, format="json_comment"
    )
    print("✓ Embedded decision tag in output:")
    print(f"  Format: JSON comment")
    print(f"  Tag ID: {decision_tag.tag_id}")
    print(f"  Content Hash: {decision_tag.output_content_hash[:16]}...")
    print(f"  First 200 chars of embedded output:")
    print(f"  {embedded[:200]}...")

    # Show tag extraction
    extracted = TagEmbedder.extract_tag_from_text(embedded)
    print(f"\n✓ Extracted tag from output:")
    print(f"  Extracted Tag ID: {extracted.tag_id if extracted else 'None'}")
    print(f"  Match: {'PASS' if extracted and extracted.tag_id == decision_tag.tag_id else 'FAIL'}")

    # ========================================================================
    # PHASE 4: ORG-LEVEL BATCHING
    # ========================================================================
    print("\n\n[PHASE 4] ORGANIZATION-LEVEL BATCHING (6-hour windows)")
    print("-" * 80)

    scheduler = OrgBatchScheduler()

    # Queue task batches for org batching
    scheduler.queue_task_batch("healthcare_org_001", task1)
    scheduler.queue_task_batch("healthcare_org_001", task2)
    scheduler.queue_task_batch("healthcare_org_001", task3)

    print(f"✓ Queued {3} task batches for organization batch")

    # Create first batch window
    import asyncio

    async def create_windows():
        await scheduler.create_batch_window("healthcare_org_001")

    asyncio.run(create_windows())

    current_window = scheduler.get_current_window("healthcare_org_001")
    print(f"✓ Created batch window: {current_window.window_id}")
    print(f"  Start: {current_window.window_start.isoformat()}")
    print(f"  End: {current_window.window_end.isoformat()}")
    print(f"  Task batches: {len(current_window.completed_task_batches)}")

    # Finalize window and create merkle tree
    merkle_root = current_window.finalize_window()
    print(f"\n✓ Window finalized with merkle root:")
    print(f"  Root: {merkle_root[:32]}...")

    # ========================================================================
    # FINAL AUDIT TRAIL
    # ========================================================================
    print("\n\n[AUDIT TRAIL] Cryptographic Proof Chain")
    print("-" * 80)

    print("Chain of Merkle Proofs:")
    print(f"  Output 1 (Reader)")
    print(f"    └─ Task Batch Merkle Root: {task1.merkle_root[:32]}...")
    print()

    print(f"  Output 2 (Analyzer)")
    print(f"    └─ Task Batch Merkle Root: {task2.merkle_root[:32]}...")
    print()

    print(f"  Output 3 (Decision) [CRITICAL]")
    print(f"    └─ Task Batch Merkle Root: {task3.merkle_root[:32]}...")
    print(f"       └─ Org Batch Window Merkle Root: {merkle_root[:32]}...")
    print()

    print("Verification Flow:")
    print("  1. User receives clinical recommendation + embedded tag")
    print("  2. Extract tag_id from output")
    print("  3. Query verification service: GET /verify/{tag_id}")
    print("  4. Service returns:")
    print("     - Agent audit trail (which agents, in what order)")
    print("     - Task batch merkle proof (proves in batch)")
    print("     - Org batch merkle proof (proves in org window)")
    print("     - Policy enforcement details (HIPAA, FDA, etc)")
    print("     - Risk assessment (HIGH → requires physician review)")
    print()

    print("Anti-Forgery Protection:")
    print("  ✓ Output hash in tag (detects content tampering)")
    print("  ✓ Merkle proof (proves inclusion in task batch)")
    print("  ✓ Org batch proof (proves in time-window)")
    print("  ✓ Server-side proof storage (minimal embedded tag)")
    print("  ✓ Cryptographic signatures (ed25519)")

    print("\n" + "=" * 80)
    print("Complete CIAF governance flow demonstrated!")
    print("=" * 80)


if __name__ == "__main__":
    complete_healthcare_workflow()
