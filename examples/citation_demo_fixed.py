"""
Citation Anchor Usage Example - Fixed Version

This script demonstrates how to use the Citation Anchor system in CIAF
to validate data usage compliance and track intellectual property.

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

def demonstrate_citation_anchor():
    """Demonstrate citation anchor functionality."""
    
    print("\n🔗 CIAF Citation Anchor System Demo")
    print("=" * 50)
    
    # Initialize citation anchor system
    citation_system = CitationAnchor()
    
    print("\n1. Adding Citations")
    print("-" * 20)
    
    # Add some example citations
    citation1 = CitationMetadata(
        citation_id="",  # Will be auto-generated
        title="ImageNet: A Large-Scale Hierarchical Image Database",
        authors=["Jia Deng", "Wei Dong", "Richard Socher", "Li-Jia Li", "Kai Li", "Li Fei-Fei"],
        organization="Stanford University",
        publication_date="2009",
        doi="10.1109/CVPR.2009.5206848",
        license_type=LicenseType.CUSTOM,
        description="Large-scale image dataset for visual recognition research"
    )
    
    citation2 = CitationMetadata(
        citation_id="",
        title="Common Crawl Web Dataset",
        authors=["Common Crawl Foundation"],
        organization="Common Crawl",
        publication_date="2023",
        url="https://commoncrawl.org/",
        license_type=LicenseType.CC_BY_SA,
        description="Web crawl data for language model training"
    )
    
    citation3 = CitationMetadata(
        citation_id="",
        title="OpenAI GPT-3.5 Turbo API",
        authors=["OpenAI"],
        organization="OpenAI",
        publication_date="2023",
        url="https://openai.com/api/",
        license_type=LicenseType.PROPRIETARY,
        description="Commercial language model API service"
    )
    
    # Add citations to system
    citation1_id = citation_system.add_citation(citation1)
    citation2_id = citation_system.add_citation(citation2)
    citation3_id = citation_system.add_citation(citation3)
    
    print(f"✅ Added citation: {citation1.title} (ID: {citation1_id[:8]}...)")
    print(f"✅ Added citation: {citation2.title} (ID: {citation2_id[:8]}...)")
    print(f"✅ Added citation: {citation3.title} (ID: {citation3_id[:8]}...)")
    
    print("\n2. Recording Data Usage")
    print("-" * 25)
    
    # Record usage for training a model
    usage1 = UsageRecord(
        usage_id="",
        citation_id=citation1_id,
        usage_type=UsageType.TRAINING,
        purpose="Training computer vision model for object detection",
        scope="partial",
        percentage_used=15.0,
        modifications_made=["Resized images to 224x224", "Applied data augmentation"],
        attribution_provided=True,
        used_by_model_id="model_cv_001"
    )
    
    usage2 = UsageRecord(
        usage_id="",
        citation_id=citation2_id,
        usage_type=UsageType.TRAINING,
        purpose="Training large language model",
        scope="partial",
        percentage_used=5.0,
        modifications_made=["Filtered for English content", "Removed personal information"],
        attribution_provided=True,
        used_by_model_id="model_llm_001"
    )
    
    usage3 = UsageRecord(
        usage_id="",
        citation_id=citation3_id,
        usage_type=UsageType.COMMERCIAL_USE,
        purpose="Using API for production inference",
        scope="full",
        attribution_provided=False,
        used_by_model_id="model_llm_001"
    )
    
    # Record usages
    usage1_id = citation_system.record_usage(usage1)
    usage2_id = citation_system.record_usage(usage2)
    usage3_id = citation_system.record_usage(usage3)
    
    print(f"📝 Recorded usage: {usage1.purpose[:40]}... (ID: {usage1_id[:8]}...)")
    print(f"📝 Recorded usage: {usage2.purpose[:40]}... (ID: {usage2_id[:8]}...)")
    print(f"📝 Recorded usage: {usage3.purpose[:40]}... (ID: {usage3_id[:8]}...)")
    
    print("\n3. Compliance Validation")
    print("-" * 25)
    
    # Validate compliance for each usage
    compliance1 = citation_system.verify_usage_compliance(citation1_id, UsageType.TRAINING)
    compliance2 = citation_system.verify_usage_compliance(citation2_id, UsageType.TRAINING)
    compliance3 = citation_system.verify_usage_compliance(citation3_id, UsageType.COMMERCIAL_USE)
    
    print(f"🔍 ImageNet Training: {'✅ Compliant' if compliance1['is_compliant'] else '❌ Non-compliant'}")
    print(f"   Details: {compliance1['details']}")
    if compliance1['recommendations']:
        print(f"   Recommendations: {', '.join(compliance1['recommendations'])}")
    
    print(f"🔍 Common Crawl Training: {'✅ Compliant' if compliance2['is_compliant'] else '❌ Non-compliant'}")
    print(f"   Details: {compliance2['details']}")
    
    print(f"🔍 OpenAI API Commercial Use: {'✅ Compliant' if compliance3['is_compliant'] else '❌ Non-compliant'}")
    print(f"   Details: {compliance3['details']}")
    if compliance3['recommendations']:
        print(f"   Recommendations: {', '.join(compliance3['recommendations'][:2])}")
    
    print("\n4. Model Validation")
    print("-" * 20)
    
    # Validate all citations for a specific model
    model_validation = citation_system.validate_citations_for_model("model_llm_001")
    
    print(f"🤖 Model: model_llm_001")
    print(f"   Total citations: {model_validation['total_citations']}")
    print(f"   Overall compliant: {'✅ Yes' if model_validation['overall_compliant'] else '❌ No'}")
    
    if model_validation['critical_issues']:
        print("   ⚠️  Critical Issues:")
        for issue in model_validation['critical_issues']:
            print(f"      - {issue['citation']}: {issue['issue']}")
    
    if model_validation['warnings']:
        print("   ⚡ Warnings:")
        for warning in model_validation['warnings']:
            print(f"      - {warning['citation']}: {warning['issue']}")
    
    print("\n5. Attribution Generation")
    print("-" * 25)
    
    # Generate proper attribution text
    attribution1 = citation_system.generate_attribution_text(citation1_id)
    attribution2 = citation_system.generate_attribution_text(citation2_id)
    
    print("📄 Generated Attribution Text:")
    print(f"   {attribution1}")
    print(f"   {attribution2}")
    
    print("\n6. Compliance Report")
    print("-" * 20)
    
    # Generate comprehensive compliance report
    report = citation_system.generate_compliance_report()
    
    print(f"📊 Compliance Summary:")
    print(f"   Total Citations: {report['summary']['total_citations']}")
    print(f"   Total Usages: {report['summary']['total_usages']}")
    print(f"   Compliance Rate: {report['summary']['compliance_rate']:.1%}")
    
    print(f"\n   License Distribution:")
    for license_type, count in report['license_distribution'].items():
        print(f"      {license_type.upper()}: {count}")
    
    print(f"\n   Usage Distribution:")
    for usage_type, count in report['usage_distribution'].items():
        print(f"      {usage_type.upper()}: {count}")
    
    if report['recent_issues']:
        print(f"\n   Recent Issues:")
        for issue in report['recent_issues'][:3]:
            print(f"      - {issue['severity'].upper()}: {issue['details']}")
    
    print("\n7. Bibliography Export")
    print("-" * 22)
    
    # Export citations in different formats
    bibtex = citation_system.export_citations_bibliography("bibtex")
    apa = citation_system.export_citations_bibliography("apa")
    
    print("📚 BibTeX Export (first entry):")
    print(bibtex.split('\n\n')[0])
    
    print("\n📚 APA Format (first entry):")
    print(apa.split('\n\n')[0])
    
    print("\n✨ Citation Anchor System Demo Complete!")
    print("=" * 50)
    
    return citation_system


if __name__ == "__main__":
    # Run the demonstration
    system = demonstrate_citation_anchor()
    
    print("\n🎯 Key Features Demonstrated:")
    print("   • Citation metadata management")
    print("   • License compatibility checking")
    print("   • Usage compliance validation")
    print("   • Automated attribution generation")
    print("   • Comprehensive reporting")
    print("   • Bibliography export")
    print("   • Model-level compliance validation")
    print("\n💡 This system ensures proper data usage compliance")
    print("   and intellectual property protection in AI workflows!")