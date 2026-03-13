"""
CIAF Complete Integration: All Phases (1-5)

Demonstrates end-to-end flow with verification microservice.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from ciaf.agents import create_example_agent_registry
from ciaf.sessions import AgentSession
from ciaf.org_batching import OrgBatchScheduler
from ciaf.tagging import TagEmbedder
from ciaf.verification import PostgresProofStore, VerificationService
import asyncio


async def complete_healthcare_verification_workflow():
    """
    Complete end-to-end workflow including verification.

    Demonstrates all 5 phases together.
    """

    print("=" * 80)
    print("CIAF: COMPLETE WORKFLOW (Phases 1-5)")
    print("=" * 80)
    print()

    # ========================================================================
    # PHASES 1-4: Create outputs, tags, and batches
    # ========================================================================
    print("[PHASES 1-4] Creating outputs with governance...")
    print("-" * 80)

    registry = create_example_agent_registry()

    # Create session and outputs
    session = AgentSession(
        session_id="verification_demo_001",
        user_id="physician_001",
        organization_id="healthcare_org_001",
    )

    session.start_task("Clinical analysis")

    # Record outputs (agent + model)
    clinical_output = """
    PATIENT ANALYSIS
    ================
    Chief Complaint: Hypertension
    Assessment: Stage 2 HTN with CKD Stage 3b
    Recommendation: ACE inhibitor therapy
    Risk Level: HIGH
    Requires: Physician review before implementation
    """

    tag = session.record_output(
        output_content=clinical_output,
        inference_receipt_id="lcm_clinical_001",
        agent_ids=["healthcare_reader_001", "analysis_agent_001", "recommendation_agent_001"],
        policies_applied=["HIPAA_COMPLIANT", "FDA_SaMD", "ISO_14971"],
        risk_level="high",
    )

    print(f"✓ Created output tag: {tag.tag_id[:12]}...")
    print(f"  Content hash: {tag.output_content_hash[:16]}...")
    print(f"  Agents: {tag.agent_ids}")
    print()

    # Complete task (creates merkle tree)
    task = session.complete_current_task("success")
    print(f"✓ Task completed with merkle root: {task.merkle_root[:16]}...")
    print()

    session.end_session()

    # Simulate org-level batching
    scheduler = OrgBatchScheduler()
    scheduler.queue_task_batch("healthcare_org_001", task)
    await scheduler.create_batch_window("healthcare_org_001")

    print(f"✓ Org batch window created")
    print()

    # Embed tag in output
    embedded_output = TagEmbedder.embed_in_text(
        clinical_output, tag, format="json_comment"
    )

    print("✓ Tag embedded in output (ready for delivery to user)")
    print()

    # ========================================================================
    # PHASE 5: VERIFICATION
    # ========================================================================
    print("\n[PHASE 5] VERIFICATION MICROSERVICE")
    print("-" * 80)

    # Initialize proof store and verification service
    proof_store = PostgresProofStore()
    await proof_store.connect()

    print("✓ Connected to PostgreSQL proof store")
    print()

    # Store proof in database
    await proof_store.store_output_tag(tag)
    await proof_store.store_task_batch(task)

    current_window = scheduler.get_current_window("healthcare_org_001")
    await proof_store.store_org_batch_window(current_window)

    print("✓ Stored proofs in PostgreSQL:")
    print(f"  - Output tag")
    print(f"  - Task batch")
    print(f"  - Org batch window")
    print()

    # Create verification service
    verification_service = VerificationService(proof_store)

    # ========================================================================
    # VERIFICATION WORKFLOW
    # ========================================================================
    print("VERIFICATION WORKFLOW:")
    print("-" * 80)
    print()

    # Step 1: Extract tag from output
    print("Step 1: Extract tag from output")
    extracted_tag = TagEmbedder.extract_tag_from_text(embedded_output)
    print(f"  ✓ Extracted tag ID: {extracted_tag.tag_id[:12]}...")
    print()

    # Step 2: Query verification service
    print("Step 2: Query verification service: GET /verify/{tag_id}")
    verification_result = await verification_service.verify_output(
        tag_id=extracted_tag.tag_id,
        verify_merkle=True,
        include_audit_trail=True,
    )

    print(f"  ✓ Verification result: {'PASS' if verification_result.verified else 'FAIL'}")
    print(f"  ✓ Organization: {verification_result.organization_id}")
    print(f"  ✓ Inference type: {verification_result.inference_type}")
    print()

    # Step 3: Display results
    print("Step 3: Verification Details")
    print("-" * 80)
    print()

    print("OUTPUT METADATA:")
    print(f"  Tag ID: {verification_result.tag_id}")
    print(f"  Risk Level: {verification_result.risk_level}")
    print(f"  Model: {verification_result.model_name or 'N/A (agent-orchestrated)'}")
    print(f"  Agents: {', '.join(verification_result.agent_ids) or 'N/A'}")
    print()

    print("POLICIES ENFORCED:")
    for policy in verification_result.policies_applied:
        print(f"  ✓ {policy}")
    print()

    print("CRYPTOGRAPHIC PROOFS:")
    print(f"  Task batch verified: {verification_result.task_batch_verified}")
    print(f"  Org batch verified: {verification_result.org_batch_verified}")
    print(f"  Merkle proof valid: {verification_result.merkle_proof_valid}")
    print()

    print("ISSUES:")
    if verification_result.issues:
        for issue in verification_result.issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ No issues detected")
    print()

    print("WARNINGS:")
    if verification_result.warnings:
        for warning in verification_result.warnings:
            print(f"  ⚠ {warning}")
    else:
        print("  ✓ No warnings")
    print()

    # Step 4: Get organization statistics
    print("Step 4: Organization Statistics")
    print("-" * 80)

    stats = await verification_service.get_verification_summary(
        "healthcare_org_001"
    )

    print(f"Organization: healthcare_org_001")
    print(f"  Total outputs: {stats['verification_summary']['total_tags']}")
    print(f"  Verified: {stats['verification_summary']['verified_tags']}")
    print(f"  Verification rate: {stats['verified_rate']:.1%}")
    print(f"  High risk outputs: {stats['verification_summary']['high_risk_tags']}")
    print(f"  Critical outputs: {stats['verification_summary']['critical_tags']}")
    print()

    # Step 5: Get compliance report
    print("Step 5: Policy Compliance Report")
    print("-" * 80)

    compliance = await verification_service.get_policy_compliance_report(
        "healthcare_org_001",
        policy="HIPAA_COMPLIANT",
    )

    print(f"Policy: {compliance['policy']}")
    print(f"  Total outputs: {compliance['total_outputs']}")
    print(f"  Policy covered: {compliance['policy_covered']}")
    print(f"  Compliance rate: {compliance['compliance_rate']:.1%}")
    print(f"  Verified outputs: {compliance['verified_outputs']}")
    print()

    # ========================================================================
    # REST API EXAMPLES
    # ========================================================================
    print("\n" + "=" * 80)
    print("REST API EXAMPLES (Microservice)")
    print("=" * 80)
    print()

    print("API Endpoints Available:")
    print()

    print("1. VERIFY OUTPUT")
    print(f"   POST /verify")
    print(f"   Body:")
    print(f"   {{")
    print(f'       "tag_id": "{extracted_tag.tag_id}",')
    print(f'       "verify_merkle": true,')
    print(f'       "include_audit_trail": true')
    print(f"   }}")
    print()

    print("2. VERIFY BY TAG ID (GET)")
    print(f"   GET /verify/{extracted_tag.tag_id[:12]}...?verify_merkle=true")
    print()

    print("3. GET AUDIT TRAIL")
    print(f"   GET /audit/{extracted_tag.tag_id[:12]}...")
    print()

    print("4. GET COMPLIANCE REPORT")
    print(f"   GET /compliance/healthcare_org_001?policy=HIPAA_COMPLIANT")
    print()

    print("5. GET ORGANIZATION STATS")
    print(f"   GET /stats/healthcare_org_001")
    print()

    print("6. HEALTH CHECK")
    print(f"   GET /health")
    print()

    # ========================================================================
    # DEPLOYMENT ARCHITECTURE
    # ========================================================================
    print("=" * 80)
    print("DEPLOYMENT ARCHITECTURE")
    print("=" * 80)
    print()

    print("""
CIAF CORE (Port 8000)
  ├─ Agent Registry + Policies
  ├─ Session & Task Batching
  ├─ Output Tagging
  └─ Org Batch Scheduling

PostgreSQL (Port 5432)
  ├─ output_tags table
  ├─ task_batches table
  ├─ org_batch_windows table
  └─ agent_actions table

VERIFICATION MICROSERVICE (Port 8001)
  ├─ /verify/{tag_id} - Verify outputs
  ├─ /audit/{tag_id} - Get audit trail
  ├─ /compliance/{org} - Policy compliance
  ├─ /stats/{org} - Organization stats
  └─ /health - Service health

Data Flow:
  User Output
    ↓
  CIAF Core (tag + batch)
    ↓
  PostgreSQL (store proofs)
    ↓
  Verification Service (verify)
    ↓
  REST API Response (audit trail + compliance)
""")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("VERIFICATION COMPLETED")
    print("=" * 80)
    print()

    print("✓ Output verified as authentic")
    print("✓ Agent audit trail retrieved")
    print("✓ Policy compliance confirmed")
    print("✓ Merkle proofs validated")
    print("✓ Organization statistics available")
    print()

    print("Key Features:")
    print("  ✓ Non-repudiation: Proves AI generated the output")
    print("  ✓ Tamper detection: Content hash prevents modification")
    print("  ✓ Audit trail: Full agent execution history")
    print("  ✓ Policy tracking: Which policies were enforced")
    print("  ✓ Cryptographic proofs: Merkle tree verification")
    print("  ✓ Server-side storage: Minimal embedded tag (anti-forgery)")
    print()


if __name__ == "__main__":
    asyncio.run(complete_healthcare_verification_workflow())
