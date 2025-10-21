#!/usr/bin/env python3
"""
Framework Validation Script
===========================

Validates that all CIAF framework implementations are complete,
error-free, and properly integrated.

This script:
- Validates all 20 industry framework implementations
- Checks PolicyEnforcement integration
- Verifies interface compliance
- Validates method implementations
- Generates framework health report
"""

import sys
import os
import importlib
import inspect
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Add CIAF to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def get_industry_frameworks() -> List[str]:
    """Get list of all industry framework modules."""
    
    frameworks = [
        'healthcare', 'banking', 'government', 'insurance', 'manufacturing',
        'retail', 'energy', 'telecommunications', 'transportation', 'education',
        'aerospace', 'pharmaceutical', 'automotive', 'realestate', 'agriculture',
        'entertainment', 'nonprofit', 'consulting', 'hospitality', 'foodservice'
    ]
    
    return frameworks

def validate_framework_import(framework_name: str) -> Tuple[bool, str, Any]:
    """Validate that a framework can be imported successfully."""
    
    try:
        module_path = f"ciaf.industries.{framework_name}"
        module = importlib.import_module(module_path)
        return True, "Import successful", module
    except ImportError as e:
        return False, f"Import failed: {e}", None
    except Exception as e:
        return False, f"Unexpected error: {e}", None

def validate_framework_class(module: Any, framework_name: str) -> Tuple[bool, str, Any]:
    """Validate that the framework class exists and is properly defined."""
    
    # Expected class name pattern
    class_name = f"{framework_name.title()}AIGovernanceFramework"
    
    try:
        framework_class = getattr(module, class_name)
        
        # Verify it's a class
        if not inspect.isclass(framework_class):
            return False, f"{class_name} is not a class", None
        
        return True, f"Class {class_name} found", framework_class
        
    except AttributeError:
        return False, f"Class {class_name} not found in module", None
    except Exception as e:
        return False, f"Unexpected error accessing class: {e}", None

def validate_framework_methods(framework_class: Any) -> Tuple[bool, str, List[str]]:
    """Validate that required framework methods are implemented."""
    
    required_methods = [
        '__init__',
        'assess_compliance',
        'generate_audit_report',
        'get_regulatory_requirements',
        'validate_model_governance'
    ]
    
    missing_methods = []
    implemented_methods = []
    
    for method_name in required_methods:
        if hasattr(framework_class, method_name):
            method = getattr(framework_class, method_name)
            if callable(method):
                implemented_methods.append(method_name)
            else:
                missing_methods.append(f"{method_name} (not callable)")
        else:
            missing_methods.append(method_name)
    
    if missing_methods:
        return False, f"Missing methods: {', '.join(missing_methods)}", implemented_methods
    else:
        return True, "All required methods implemented", implemented_methods

def validate_framework_instantiation(framework_class: Any, framework_name: str) -> Tuple[bool, str]:
    """Validate that the framework can be instantiated."""
    
    try:
        # Try to instantiate with minimal parameters
        instance = framework_class(
            organization_id=f"test_{framework_name}",
            regulatory_jurisdiction="test_jurisdiction"
        )
        
        # Verify basic attributes
        if hasattr(instance, 'regulatory_standards'):
            return True, "Framework instantiated successfully"
        else:
            return False, "Framework missing regulatory_standards attribute"
            
    except TypeError as e:
        # Try with different parameter names that might be expected
        try:
            if framework_name == 'healthcare':
                instance = framework_class(
                    healthcare_organization_id=f"test_{framework_name}",
                    medical_device_class="Class_I"
                )
            elif framework_name == 'banking':
                instance = framework_class(
                    bank_id=f"test_{framework_name}",
                    regulatory_jurisdiction="US_Federal_Reserve"
                )
            elif framework_name == 'government':
                instance = framework_class(
                    agency_id=f"test_{framework_name}",
                    chief_ai_officer="test_cao"
                )
            else:
                # Generic fallback
                instance = framework_class()
            
            return True, "Framework instantiated with alternative parameters"
            
        except Exception as e2:
            return False, f"Instantiation failed: {e}, Alternative: {e2}"
            
    except Exception as e:
        return False, f"Instantiation failed: {e}"

def validate_policy_enforcement_integration(framework_class: Any) -> Tuple[bool, str]:
    """Validate PolicyEnforcement integration."""
    
    try:
        # Check if framework has policy enforcement capabilities
        instance = framework_class()
        
        # Look for policy-related methods
        policy_methods = [method for method in dir(instance) if 'policy' in method.lower()]
        
        if policy_methods:
            return True, f"Policy integration found: {len(policy_methods)} methods"
        else:
            return False, "No policy enforcement integration detected"
            
    except Exception as e:
        return False, f"Policy enforcement validation failed: {e}"

def validate_all_frameworks() -> Dict[str, Dict]:
    """Validate all industry frameworks."""
    
    frameworks = get_industry_frameworks()
    results = {}
    
    for framework_name in frameworks:
        print(f"Validating {framework_name}...")
        
        framework_result = {
            'import_status': None,
            'class_status': None,
            'methods_status': None,
            'instantiation_status': None,
            'policy_integration_status': None,
            'overall_status': 'UNKNOWN'
        }
        
        # Test import
        import_success, import_msg, module = validate_framework_import(framework_name)
        framework_result['import_status'] = {'success': import_success, 'message': import_msg}
        
        if not import_success:
            framework_result['overall_status'] = 'FAILED'
            results[framework_name] = framework_result
            continue
        
        # Test class
        class_success, class_msg, framework_class = validate_framework_class(module, framework_name)
        framework_result['class_status'] = {'success': class_success, 'message': class_msg}
        
        if not class_success:
            framework_result['overall_status'] = 'FAILED'
            results[framework_name] = framework_result
            continue
        
        # Test methods
        methods_success, methods_msg, implemented_methods = validate_framework_methods(framework_class)
        framework_result['methods_status'] = {
            'success': methods_success, 
            'message': methods_msg,
            'implemented_methods': implemented_methods
        }
        
        # Test instantiation
        inst_success, inst_msg = validate_framework_instantiation(framework_class, framework_name)
        framework_result['instantiation_status'] = {'success': inst_success, 'message': inst_msg}
        
        # Test policy integration
        policy_success, policy_msg = validate_policy_enforcement_integration(framework_class)
        framework_result['policy_integration_status'] = {'success': policy_success, 'message': policy_msg}
        
        # Determine overall status
        all_passed = all([
            import_success,
            class_success,
            methods_success,
            inst_success,
            policy_success
        ])
        
        framework_result['overall_status'] = 'PASSED' if all_passed else 'FAILED'
        results[framework_name] = framework_result
    
    return results

def generate_validation_report(results: Dict[str, Dict]) -> Dict:
    """Generate comprehensive validation report."""
    
    total_frameworks = len(results)
    passed_frameworks = sum(1 for r in results.values() if r['overall_status'] == 'PASSED')
    failed_frameworks = total_frameworks - passed_frameworks
    
    # Collect failure details
    failures = {}
    for framework, result in results.items():
        if result['overall_status'] == 'FAILED':
            failure_reasons = []
            for check, status in result.items():
                if isinstance(status, dict) and not status.get('success', True):
                    failure_reasons.append(f"{check}: {status.get('message', 'Unknown error')}")
            failures[framework] = failure_reasons
    
    # Generate summary
    report = {
        "validation_timestamp": "2024-02-15T10:30:00Z",
        "total_frameworks": total_frameworks,
        "passed_frameworks": passed_frameworks,
        "failed_frameworks": failed_frameworks,
        "success_rate": passed_frameworks / total_frameworks if total_frameworks > 0 else 0,
        "framework_results": results,
        "failures": failures,
        "validation_status": "PASS" if failed_frameworks == 0 else "FAIL"
    }
    
    return report

def main():
    """Main validation function."""
    
    print("🔍 CIAF Framework Validation")
    print("=" * 40)
    
    try:
        # Validate all frameworks
        print("\n1. Validating all industry frameworks...")
        results = validate_all_frameworks()
        
        # Generate report
        print("\n2. Generating validation report...")
        report = generate_validation_report(results)
        
        # Display summary
        print(f"\n📊 Validation Summary:")
        print(f"   • Total Frameworks: {report['total_frameworks']}")
        print(f"   • Passed: {report['passed_frameworks']}")
        print(f"   • Failed: {report['failed_frameworks']}")
        print(f"   • Success Rate: {report['success_rate']:.3f}")
        print(f"   • Overall Status: {report['validation_status']}")
        
        # Show passed frameworks
        passed_frameworks = [name for name, result in results.items() 
                           if result['overall_status'] == 'PASSED']
        if passed_frameworks:
            print(f"\n✅ Passed Frameworks ({len(passed_frameworks)}):")
            for framework in sorted(passed_frameworks):
                print(f"   • {framework}")
        
        # Show failed frameworks
        if report['failures']:
            print(f"\n❌ Failed Frameworks ({len(report['failures'])}):")
            for framework, reasons in report['failures'].items():
                print(f"   • {framework}:")
                for reason in reasons[:3]:  # Show first 3 reasons
                    print(f"     - {reason}")
        
        # Save detailed report
        import json
        report_path = Path(__file__).parent.parent / "framework_validation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Exit with appropriate code for CI/CD
        if report['validation_status'] == 'PASS':
            print(f"\n✅ Framework Validation PASSED - All frameworks are valid")
            return 0
        else:
            print(f"\n❌ Framework Validation FAILED - Issues found in frameworks")
            return 1
            
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)