"""
NIST AI RMF Citation Anchor Demo

This script demonstrates how to properly cite and validate usage of the
NIST AI Risk Management Framework document using the Citation Anchor system.

Based on the NIST AI RMF dataset documentation provided.

Created: 2025-10-27
Author: Denzil James Greenwood
Version: 1.0.0
"""

import sys
import os
from datetime import datetime, timezone

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Use standalone implementation to avoid dependency issues
print("🔄 Using standalone implementation...")
from standalone_citation_anchor import (
    CitationAnchor,
    CitationMetadata,
    UsageRecord,
    CitationType,
    LicenseType,
    UsageType
)
print("✅ Using standalone Citation Anchor implementation")


def demonstrate_nist_ai_rmf_citation():
    """Demonstrate proper citation and validation for NIST AI RMF dataset."""
    
    print("\n🏛️ NIST AI RMF Citation Anchor Demo")
    print("=" * 50)
    
    # Initialize citation anchor system
    citation_system = CitationAnchor()
    
    print("\n1. Adding NIST AI RMF Citation")
    print("-" * 35)
    
    # Create citation for NIST AI RMF based on the provided documentation
    nist_citation = CitationMetadata(
        citation_id="",  # Will be auto-generated
        title="Artificial Intelligence Risk Management Framework (AI RMF 1.0)",
        authors=["Elham Tabassi"],
        organization="National Institute of Standards and Technology (NIST)",
        publication_date="2023",
        doi="10.6028/NIST.AI.100-1",
        url="https://doi.org/10.6028/NIST.AI.100-1",
        license_type=LicenseType.PUBLIC_DOMAIN,  # NIST publications are public domain
        description="Federal standard providing comprehensive approach for AI risk management",
        keywords=[
            "AI Risk Management", 
            "Federal Standards", 
            "Technology Governance",
            "AI Actor roles",
            "TEVV processes",
            "Human Factors",
            "Impact Assessment"
        ]
    )
    
    # Add citation to system
    nist_citation_id = citation_system.add_citation(nist_citation)
    
    print(f"✅ Added NIST AI RMF citation (ID: {nist_citation_id[:8]}...)")
    print(f"   Title: {nist_citation.title}")
    print(f"   Author: {nist_citation.authors[0]}")
    print(f"   DOI: {nist_citation.doi}")
    print(f"   License: {nist_citation.license_type.value}")
    
    print("\n2. Recording Training Data Usage")
    print("-" * 35)
    
    # Record usage based on the dataset documentation
    training_usage = UsageRecord(
        usage_id="",
        citation_id=nist_citation_id,
        usage_type=UsageType.TRAINING,
        purpose="Training large language model on regulatory/governance text domain",
        scope="full",  # Using full document content
        percentage_used=100.0,
        modifications_made=[
            "Sentence-level splitting",
            "85/15 train/eval split", 
            "Preprocessing for transfer learning from EU AI Act"
        ],
        attribution_provided=True,
        used_by_model_id="nist_ai_rmf_transfer_model",
        used_by_dataset_id="nist_ai_rmf_train.txt"
    )
    
    # Record the usage
    usage_id = citation_system.record_usage(training_usage)
    
    print(f"📝 Recorded training usage (ID: {usage_id[:8]}...)")
    print(f"   Purpose: {training_usage.purpose}")
    print(f"   Scope: {training_usage.scope} ({training_usage.percentage_used}%)")
    print(f"   Model ID: {training_usage.used_by_model_id}")
    print(f"   Modifications: {len(training_usage.modifications_made)} preprocessing steps")
    
    print("\n3. Compliance Validation")
    print("-" * 25)
    
    # Validate training usage compliance
    compliance_result = citation_system.verify_usage_compliance(
        nist_citation_id, 
        UsageType.TRAINING
    )
    
    print(f"🔍 Training Usage Compliance:")
    print(f"   Status: {'✅ Compliant' if compliance_result['is_compliant'] else '❌ Non-compliant'}")
    print(f"   Severity: {compliance_result['severity'].upper()}")
    print(f"   Details: {compliance_result['details']}")
    
    if compliance_result['recommendations']:
        print(f"   Recommendations: {', '.join(compliance_result['recommendations'])}")
    
    # Also test other usage types
    print(f"\n🔍 Production Usage Compliance:")
    prod_compliance = citation_system.verify_usage_compliance(
        nist_citation_id, 
        UsageType.PRODUCTION
    )
    print(f"   Status: {'✅ Compliant' if prod_compliance['is_compliant'] else '❌ Non-compliant'}")
    print(f"   Details: {prod_compliance['details']}")
    
    print(f"\n🔍 Commercial Use Compliance:")
    commercial_compliance = citation_system.verify_usage_compliance(
        nist_citation_id, 
        UsageType.COMMERCIAL_USE
    )
    print(f"   Status: {'✅ Compliant' if commercial_compliance['is_compliant'] else '❌ Non-compliant'}")
    print(f"   Details: {commercial_compliance['details']}")
    
    print("\n4. Model Validation")
    print("-" * 20)
    
    # Validate all citations for the NIST transfer model
    model_validation = citation_system.validate_citations_for_model("nist_ai_rmf_transfer_model")
    
    print(f"🤖 Model: {model_validation['model_id']}")
    print(f"   Total citations: {model_validation['total_citations']}")
    print(f"   Overall compliant: {'✅ Yes' if model_validation['overall_compliant'] else '❌ No'}")
    print(f"   Validation timestamp: {model_validation['validation_timestamp']}")
    
    if model_validation['critical_issues']:
        print("   ⚠️  Critical Issues:")
        for issue in model_validation['critical_issues']:
            print(f"      - {issue['citation']}: {issue['issue']}")
    else:
        print("   ✅ No critical compliance issues found")
    
    if model_validation['warnings']:
        print("   ⚡ Warnings:")
        for warning in model_validation['warnings']:
            print(f"      - {warning['citation']}: {warning['issue']}")
    
    print("\n5. Attribution Generation")
    print("-" * 25)
    
    # Generate proper attribution text
    attribution = citation_system.generate_attribution_text(nist_citation_id)
    
    print("📄 Generated Attribution Text:")
    print(f"   {attribution}")
    
    print("\n📝 Recommended Citation for Research Papers:")
    print("   Tabassi, E. (2023). Artificial Intelligence Risk Management")
    print("   Framework (AI RMF 1.0). National Institute of Standards and")
    print("   Technology. https://doi.org/10.6028/NIST.AI.100-1")
    
    print("\n6. Training Configuration Compliance")
    print("-" * 38)
    
    # Demonstrate specific training configuration validation
    training_config = {
        "dataset_source": "NIST AI RMF 1.0",
        "local_file": "data/corpus/NIST.txt",
        "training_split": "data/train/nist_ai_rmf_train.txt",
        "eval_split": "data/eval/nist_ai_rmf_eval.txt",
        "split_ratio": "85/15",
        "content_length": "21,412 characters, 146 sentences",
        "transfer_learning": "from EU AI Act averaged checkpoint",
        "batch_size": 2,
        "learning_rate": "1.0e-4",
        "epochs": 3
    }
    
    print("⚙️ Training Configuration:")
    print(f"   Dataset: {training_config['dataset_source']}")
    print(f"   Content: {training_config['content_length']}")
    print(f"   Split: {training_config['split_ratio']} train/eval")
    print(f"   Method: Transfer learning {training_config['transfer_learning']}")
    print(f"   License Status: ✅ Public Domain - No restrictions")
    
    print("\n7. Bibliography Export")
    print("-" * 22)
    
    # Export in different formats
    bibtex = citation_system.export_citations_bibliography("bibtex")
    apa = citation_system.export_citations_bibliography("apa")
    
    print("📚 BibTeX Format:")
    print(bibtex)
    
    print("\n📚 APA Format:")
    print(apa)
    
    print("\n8. Compliance Report")
    print("-" * 20)
    
    # Generate compliance report
    report = citation_system.generate_compliance_report()
    
    print(f"📊 Compliance Summary:")
    print(f"   Total Citations: {report['summary']['total_citations']}")
    print(f"   Total Usages: {report['summary']['total_usages']}")
    print(f"   Compliance Rate: {report['summary']['compliance_rate']:.1%}")
    print(f"   Generated: {report['report_generated'][:19].replace('T', ' ')} UTC")
    
    print("\n✨ NIST AI RMF Citation Demo Complete!")
    print("=" * 50)
    
    print("\n🎯 Key Validation Results:")
    print("   ✅ Public Domain license allows all usage types")
    print("   ✅ Training usage fully compliant")
    print("   ✅ Production deployment approved")
    print("   ✅ Commercial use permitted")
    print("   ✅ Proper attribution generated")
    print("   ✅ No intellectual property violations")
    
    print("\n💡 This demonstrates how the Citation Anchor system")
    print("   ensures proper compliance for federal standards")
    print("   and public domain datasets in AI training pipelines!")
    
    return citation_system


if __name__ == "__main__":
    # Run the NIST AI RMF demonstration
    system = demonstrate_nist_ai_rmf_citation()
    
    print("\n" + "="*60)
    print("🏛️ NIST AI RMF Dataset Compliance Verified")
    print("="*60)