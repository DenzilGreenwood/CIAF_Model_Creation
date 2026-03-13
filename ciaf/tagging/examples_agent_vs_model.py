"""
Output Tagging Guide: Agent vs Direct Model Inference

This guide shows how the tagging system works for both:
1. Agent-orchestrated workflows (multi-agent)
2. Direct model inference (single model or traditional API)

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from ciaf.tagging import OutputTag, OutputTagManager, TagEmbedder


def example_agent_inference_tagging():
    """
    Example: Tagging output from agent-orchestrated workflow

    Healthcare scenario:
    - Session: User consultation
    - Agents: Reader (data) → Analyzer (analysis) → Decision (recommendation)
    - Output: Final clinical recommendation
    """
    manager = OutputTagManager()

    # Simulate multi-agent workflow output
    clinical_recommendation = """
    Based on patient review and clinical analysis:
    - Primary condition: Moderate hypertension
    - Recommended treatment: ACE inhibitor + lifestyle modification
    - Risk level: Medium
    - Requires physician review: Yes
    """

    # Create tag for agent-orchestrated output
    tag = manager.create_agent_tag(
        output_content=clinical_recommendation,
        session_id="patient_consultation_2025_03_13_001",
        inference_receipt_id="lcm_receipt_healthcare_001",
        agent_ids=[
            "healthcare_reader_001",
            "analysis_agent_001",
            "recommendation_agent_001",
        ],
        organization_id="healthcare_org_001",
        policies_applied=["HIPAA_COMPLIANT", "FDA_SaMD", "ISO_14971_RISK_MGMT"],
        risk_level="high",  # Clinical decision is high-risk
    )

    print("=== AGENT-ORCHESTRATED INFERENCE TAG ===")
    print(f"Tag ID: {tag.tag_id}")
    print(f"Inference Type: {tag.inference_type}")
    print(f"Agents Involved: {tag.agent_ids}")
    print(f"Organization: {tag.organization_id}")
    print(f"Risk Level: {tag.risk_level}")
    print(f"Content Hash: {tag.output_content_hash}")
    print()

    # Embed tag in output for delivery to user
    embedded_output = TagEmbedder.embed_in_text(
        clinical_recommendation, tag, format="json_comment"
    )

    print("Embedded output (first 500 chars):")
    print(embedded_output[:500])
    print()

    return tag, manager


def example_model_inference_tagging():
    """
    Example: Tagging output from direct model inference

    Financial scenario:
    - Session: Customer loan application
    - Model: Credit risk classifier
    - Output: Loan decision
    """
    manager = OutputTagManager()

    # Direct model inference output
    loan_decision = """
    {
        "application_id": "loan_app_2025_03_13_001",
        "decision": "approved",
        "credit_score": 750,
        "approved_amount": 50000,
        "interest_rate": 4.5,
        "explanation": "Strong credit history and stable income. Approved with standard terms."
    }
    """

    # Create tag for direct model output
    tag = manager.create_model_tag(
        output_content=loan_decision,
        session_id="loan_application_2025_03_13_001",
        inference_receipt_id="lcm_receipt_banking_001",
        model_name="credit_risk_model_v5",  # Specific model
        organization_id="banking_org_001",
        policies_applied=["FAIR_LENDING_COMPLIANCE", "SR_11_7", "ECOA"],
        risk_level="medium",
    )

    print("=== DIRECT MODEL INFERENCE TAG ===")
    print(f"Tag ID: {tag.tag_id}")
    print(f"Inference Type: {tag.inference_type}")
    print(f"Model Used: {tag.model_name}")
    print(f"Organization: {tag.organization_id}")
    print(f"Risk Level: {tag.risk_level}")
    print(f"Content Hash: {tag.output_content_hash}")
    print()

    # Embed tag in structured output
    import json

    loan_decision_dict = json.loads(loan_decision)
    embedded_output = TagEmbedder.embed_in_structured(loan_decision_dict, tag)

    print("Embedded structured output:")
    print(json.dumps(embedded_output, indent=2)[:500])
    print()

    return tag, manager


def example_verification_workflow():
    """
    Example: Using tags for cryptographic verification

    Shows how tags enable verification without access to original system.
    """
    print("=== VERIFICATION WORKFLOW ===")
    print()

    manager = OutputTagManager()

    # Create a model output
    model_output = "Predicted class: Positive sentiment (confidence: 0.92)"
    tag = manager.create_model_tag(
        output_content=model_output,
        session_id="sentiment_analysis_001",
        inference_receipt_id="lcm_receipt_sentiment_001",
        model_name="sentiment_classifier_bert",
        organization_id="analytics_org_001",
    )

    # Simulate task batch creation (Phase 3 will handle this)
    task_batch_id = "task_batch_2025_03_13_001"
    merkle_root = "a1b2c3d4e5f6..."
    merkle_proof = [("sib_hash_1", "left"), ("sib_hash_2", "right")]

    # Add proof to tag
    manager.add_task_batch_proof(task_batch_id, merkle_root, merkle_proof)

    print(f"Original Output: {model_output}")
    print()
    print(f"Tag Details:")
    print(f"  Tag ID: {tag.tag_id}")
    print(f"  Content Hash: {tag.output_content_hash}")
    print(f"  Task Batch ID: {tag.task_batch_id}")
    print(f"  Merkle Root: {tag.task_batch_merkle_root}")
    print()

    # Verification: Extract tag and verify content
    extracted_tag = TagEmbedder.extract_tag_from_text(
        f"Output: {model_output}\nTag: {tag.to_json()}"
    )

    if extracted_tag:
        is_valid = manager.verify_content(extracted_tag.tag_id, model_output)
        print(f"Content Verification: {'PASS' if is_valid else 'FAIL'}")
        print(f"Merkle Proof Available: {extracted_tag.task_batch_proof is not None}")
    print()


def example_mixed_session_tagging():
    """
    Example: Single session with both agent and model inferences

    Real-world scenario where a session uses both approaches.
    """
    print("=== MIXED SESSION (Agent + Model) ===")
    print()

    manager = OutputTagManager()

    session_id = "mixed_session_2025_03_13_001"
    org_id = "analytics_org_001"

    # Agent workflow output
    agent_analysis = "Detailed trend analysis: Sales increased 15% YoY"
    agent_tag = manager.create_agent_tag(
        output_content=agent_analysis,
        session_id=session_id,
        inference_receipt_id="lcm_agent_001",
        agent_ids=["data_processor_001", "trend_analyzer_001"],
        organization_id=org_id,
    )

    # Direct model output (model inference on agent's analysis)
    model_prediction = "Predicted next quarter: Growth continues, expect 12% increase"
    model_tag = manager.create_model_tag(
        output_content=model_prediction,
        session_id=session_id,
        inference_receipt_id="lcm_model_001",
        model_name="forecasting_lstm_v2",
        organization_id=org_id,
    )

    # Simple model (no agent)
    simple_output = "Data quality score: 0.95"
    simple_tag = manager.create_model_tag(
        output_content=simple_output,
        session_id=session_id,
        inference_receipt_id="lcm_simple_001",
        model_name="data_quality_checker",
        organization_id=org_id,
    )

    # Get session stats
    session_tags = manager.get_session_tags(session_id)
    print(f"Session: {session_id}")
    print(f"Total outputs: {len(session_tags)}")
    print()

    for i, tag in enumerate(session_tags, 1):
        print(f"{i}. Inference Type: {tag.inference_type}")
        if tag.inference_type == "agent_orchestrated":
            print(f"   Agents: {tag.agent_ids}")
        else:
            print(f"   Model: {tag.model_name}")
        print(f"   Tag ID: {tag.tag_id}")
        print()

    # Organization stats
    stats = manager.get_stats(org_id)
    print("Organization Stats:")
    print(f"  Total outputs: {stats['total_tags']}")
    print(f"  Agent-orchestrated: {stats['inference_types']['agent_orchestrated']}")
    print(f"  Direct model: {stats['inference_types']['direct_model']}")
    print(f"  Models involved: {stats['models_involved']}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("OUTPUT TAGGING SYSTEM: Agent vs Model Inference")
    print("=" * 60)
    print()

    # Run examples
    example_agent_inference_tagging()
    print()

    example_model_inference_tagging()
    print()

    example_verification_workflow()
    print()

    example_mixed_session_tagging()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("=" * 60)
    print("""
1. Agent Inference:
   - Use create_agent_tag() with list of agent_ids
   - Tracks multi-agent orchestration
   - Perfect for complex workflows

2. Direct Model Inference:
   - Use create_model_tag() with model_name
   - Tracks which model was used
   - Can be called directly by any system

3. Mixed Sessions:
   - Single session can contain both types
   - Both get merkle proofs after batching
   - Full audit trail maintained

4. Verification:
   - Tags embed minimal proof (hard to forge)
   - Full proof stored server-side (PostgreSQL)
   - Content hash prevents tampering
""")
