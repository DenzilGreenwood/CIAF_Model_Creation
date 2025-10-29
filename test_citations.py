#!/usr/bin/env python3
"""
Test Citation System Imports and Functionality
"""
import sys

sys.path.insert(0, ".")


def test_direct_import():
    try:
        from ciaf.compliance.citation_anchor import CitationAnchor

        print("✅ Direct import works: CitationAnchor")
        return True
    except Exception as e:
        print(f"❌ Direct import failed: {e}")
        return False


def test_compliance_module_import():
    try:
        from ciaf.compliance import CitationAnchor

        print("✅ Compliance module import works: CitationAnchor")
        return True
    except Exception as e:
        print(f"❌ Compliance module import failed: {e}")
        return False


def test_citation_functionality():
    try:
        from ciaf.compliance.citation_anchor import CitationAnchor, CitationMetadata, LicenseType

        # Create citation metadata
        metadata = CitationMetadata(
            citation_id="test_citation_001",
            title="Test Dataset",
            authors=["Test Author"],
            publication_date="2025",
            license_type=LicenseType.MIT,
            description="Test dataset for validation",
        )

        # Create citation anchor
        citation = CitationAnchor()
        citation_id = citation.add_citation(metadata)

        print(f"✅ Citation functionality works. Citation ID: {citation_id[:12]}...")
        return True
    except Exception as e:
        print(f"❌ Citation functionality failed: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Testing CIAF Citation System...")
    print("=" * 50)

    tests = [
        ("Direct Import", test_direct_import),
        ("Compliance Module Import", test_compliance_module_import),
        ("Citation Functionality", test_citation_functionality),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")

    all_passed = all(result for _, result in results)
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
