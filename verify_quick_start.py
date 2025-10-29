#!/usr/bin/env python3
"""
CIAF Quick Start - Final Verification

Tests the exact commands mentioned in the Quick Start guide:
1. ciaf generate --model model.pkl --data input.json
2. ciaf batch --receipts ./receipts/ --output proof.merkle
3. ciaf verify --proof proof.merkle --receipt receipt_id
4. ciaf materialize --receipt receipt_id --evidence evidence.json

Usage: python verify_quick_start.py
"""

import subprocess
import json
import sys
from pathlib import Path


def test_command(cmd, description, expected_success=True):
    """Test a command and report results."""
    print(f"\n{'='*60}")
    print(f"TESTING: {description}")
    print(f"COMMAND: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("STATUS: SUCCESS ✓")
        print("\nOUTPUT:")
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if expected_success:
            print("STATUS: FAILED ✗")
            print(f"\nERROR: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
        else:
            print("STATUS: EXPECTED FAILURE ✓")
        return False, e.stdout


def main():
    """Test all Quick Start commands."""
    
    print("CIAF Quick Start Commands - Final Verification")
    print("Testing the exact commands from the documentation...")
    
    # Cleanup
    Path("receipts").mkdir(exist_ok=True)
    for f in ["proof.merkle", "evidence.json"]:
        Path(f).unlink(missing_ok=True)
    for receipt in Path("receipts").glob("*.json"):
        receipt.unlink()
    
    all_passed = True
    
    # Test 1: Generate command
    success, output = test_command([
        "python", "-m", "ciaf.cli", "generate",
        "--model", "model.pkl",
        "--data", "input.json"
    ], "Generate lightweight receipt")
    
    all_passed &= success
    
    if success:
        # Move receipt to receipts folder and get ID
        receipt_files = list(Path(".").glob("receipt_*.json"))
        if receipt_files:
            receipt_file = receipt_files[0]
            new_path = Path("receipts") / receipt_file.name
            receipt_file.rename(new_path)
            
            with open(new_path, 'r') as f:
                receipt_data = json.load(f)
            receipt_id = receipt_data["receipt_id"]
            
            print(f"\n[INFO] Receipt ID: {receipt_id}")
            print(f"[INFO] Receipt file: {new_path}")
    
    # Create additional receipts for batch
    for i in range(2, 4):
        test_command([
            "python", "-m", "ciaf.cli", "generate",
            "--model", "model.pkl",
            "--data", "input.json", 
            "--output", f"receipts/receipt_{i:03d}.json"
        ], f"Generate additional receipt {i}")
    
    # Test 2: Batch command
    success, output = test_command([
        "python", "-m", "ciaf.cli", "batch",
        "--receipts", "./receipts/",
        "--output", "proof.merkle"
    ], "Create Merkle batch proof")
    
    all_passed &= success
    
    # Test 3: Verify command (with receipt ID)
    if 'receipt_id' in locals():
        success, output = test_command([
            "python", "-m", "ciaf.cli", "verify",
            "--proof", "proof.merkle",
            "--receipt", receipt_id
        ], f"Verify proof with specific receipt ID")
        
        all_passed &= success
    
    # Test 3b: Verify command (general)
    success, output = test_command([
        "python", "-m", "ciaf.cli", "verify",
        "--proof", "proof.merkle",
        "--verbose"
    ], "Verify proof (general verification)")
    
    all_passed &= success
    
    # Test 4: Materialize command
    if 'receipt_id' in locals():
        # Extract numeric part of receipt ID
        receipt_num = receipt_id.split('_')[-1] if '_' in receipt_id else receipt_id
        
        success, output = test_command([
            "python", "-m", "ciaf.cli", "materialize",
            "--receipt", receipt_num,
            "--evidence", "evidence.json"
        ], f"Materialize evidence from receipt")
        
        all_passed &= success
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL VERIFICATION RESULTS")
    print('='*60)
    
    if all_passed:
        print("STATUS: ALL TESTS PASSED ✓")
        print("\nAll Quick Start commands are working correctly!")
        
        # Show generated files
        print(f"\nGenerated Files:")
        for file_path in ["proof.merkle", "evidence.json"]:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                print(f"  ✓ {file_path} ({size:,} bytes)")
        
        receipt_count = len(list(Path("receipts").glob("*.json")))
        print(f"  ✓ receipts/ directory ({receipt_count} receipt files)")
        
        # Show file contents summary
        if Path("proof.merkle").exists():
            with open("proof.merkle", 'r') as f:
                proof = json.load(f)
            print(f"\nMerkle Proof Summary:")
            print(f"  • Batch ID: {proof['batch_id']}")
            print(f"  • Root Hash: {proof['root_hash'][:32]}...")
            print(f"  • Receipt Count: {proof['receipt_count']}")
        
        if Path("evidence.json").exists():
            with open("evidence.json", 'r') as f:
                evidence = json.load(f)
            print(f"\nEvidence Summary:")
            print(f"  • Evidence ID: {evidence['evidence_id']}")
            print(f"  • Compliance Frameworks: {len(evidence['compliance_evidence']['frameworks'])}")
            print(f"  • Applied Policies: {len(evidence['compliance_evidence']['policies'])}")
        
        print(f"\nQuick Start Commands (Ready to Use):")
        print("  ciaf generate --model model.pkl --data input.json")
        print("  ciaf batch --receipts ./receipts/ --output proof.merkle")
        print("  ciaf verify --proof proof.merkle --receipt <receipt_id>")
        print("  ciaf materialize --receipt <receipt_id> --evidence evidence.json")
        
    else:
        print("STATUS: SOME TESTS FAILED ✗")
        print("\nPlease review the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)