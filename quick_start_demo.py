#!/usr/bin/env python3
"""
CIAF Quick Start Demo - Exact Commands

This script demonstrates the exact Quick Start commands mentioned in the documentation:

1. Generate: ciaf generate --model model.pkl --data input.json
2. Batch: ciaf batch --receipts ./receipts/ --output proof.merkle  
3. Verify: ciaf verify --proof proof.merkle --receipt receipt_id
4. Materialize: ciaf materialize --receipt receipt_id --evidence evidence.json

Usage: python quick_start_demo.py
"""

import subprocess
import json
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n>>> {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False, ""


def main():
    """Run the CIAF Quick Start demo with exact commands."""
    
    print("CIAF Quick Start Demo - Exact Commands")
    print("=" * 60)
    print("Demonstrating the exact commands from the Quick Start guide:")
    print()
    
    # Clean setup
    Path("receipts").mkdir(exist_ok=True)
    for f in ["proof.merkle", "evidence.json"]:
        Path(f).unlink(missing_ok=True)
    for receipt in Path("receipts").glob("*.json"):
        receipt.unlink()
    
    # Command 1: Generate receipt
    print("STEP 1: Generate lightweight receipt")
    success1, output1 = run_command([
        "python", "-m", "ciaf.cli", "generate",
        "--model", "model.pkl",
        "--data", "input.json"
    ], "ciaf generate --model model.pkl --data input.json")
    
    if not success1:
        return 1
    
    # Extract receipt ID from output and move to receipts folder
    receipt_files = list(Path(".").glob("receipt_*.json"))
    if receipt_files:
        receipt_file = receipt_files[0]
        new_path = Path("receipts") / receipt_file.name
        receipt_file.rename(new_path)
        
        # Get receipt ID from the file
        with open(new_path, 'r') as f:
            receipt_data = json.load(f)
        receipt_id = receipt_data["receipt_id"]
        print(f"\n[INFO] Receipt moved to {new_path}")
        print(f"[INFO] Receipt ID: {receipt_id}")
    else:
        print("[ERROR] No receipt file found")
        return 1
    
    # Create a second receipt for batch demo
    success1b, _ = run_command([
        "python", "-m", "ciaf.cli", "generate",
        "--model", "model.pkl", 
        "--data", "input.json",
        "--output", "receipts/receipt_batch_demo.json"
    ], "Generate second receipt for batch")
    
    # Command 2: Create batch proof  
    print("\nSTEP 2: Create Merkle batch proof")
    success2, output2 = run_command([
        "python", "-m", "ciaf.cli", "batch",
        "--receipts", "./receipts/",
        "--output", "proof.merkle"
    ], "ciaf batch --receipts ./receipts/ --output proof.merkle")
    
    if not success2:
        return 1
    
    # Command 3: Verify proof
    print("\nSTEP 3: Verify cryptographic proof")
    success3, output3 = run_command([
        "python", "-m", "ciaf.cli", "verify",
        "--proof", "proof.merkle",
        "--receipt", receipt_id
    ], f"ciaf verify --proof proof.merkle --receipt {receipt_id}")
    
    if not success3:
        return 1
    
    # Command 4: Materialize evidence
    print("\nSTEP 4: Materialize evidence from receipt")
    # Extract just the numeric part of receipt_id for materialize command
    receipt_num = receipt_id.split('_')[-1] if '_' in receipt_id else receipt_id
    
    success4, output4 = run_command([
        "python", "-m", "ciaf.cli", "materialize",
        "--receipt", receipt_num,
        "--evidence", "evidence.json"
    ], f"ciaf materialize --receipt {receipt_num} --evidence evidence.json")
    
    if not success4:
        return 1
    
    # Show final results
    print("\n" + "=" * 60)
    print("QUICK START DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\nGenerated Files:")
    for file_path in ["proof.merkle", "evidence.json"]:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"  • {file_path} ({size:,} bytes)")
    
    receipt_count = len(list(Path("receipts").glob("*.json")))
    print(f"  • receipts/ directory ({receipt_count} receipt files)")
    
    # Show key information
    if Path("proof.merkle").exists():
        with open("proof.merkle", 'r') as f:
            proof = json.load(f)
        print(f"\nMerkle Proof Details:")
        print(f"  • Batch ID: {proof['batch_id']}")
        print(f"  • Root Hash: {proof['root_hash']}")
        print(f"  • Receipt Count: {proof['receipt_count']}")
    
    if Path("evidence.json").exists():
        with open("evidence.json", 'r') as f:
            evidence = json.load(f)
        print(f"\nMaterialized Evidence:")
        print(f"  • Evidence ID: {evidence['evidence_id']}")
        print(f"  • Source Receipt: {evidence['source_receipt']}")
        print(f"  • Compliance Frameworks: {', '.join(evidence['compliance_evidence']['frameworks'])}")
    
    print(f"\nNext Steps:")
    print("  1. Examine the generated receipt files in receipts/")
    print("  2. Review the Merkle proof structure in proof.merkle")
    print("  3. Analyze the materialized evidence in evidence.json")
    print("  4. Integrate these commands into your ML pipeline")
    
    print(f"\nCIAF Quick Start Commands Summary:")
    print("  ciaf generate --model model.pkl --data input.json")
    print("  ciaf batch --receipts ./receipts/ --output proof.merkle")
    print(f"  ciaf verify --proof proof.merkle --receipt {receipt_id}")
    print(f"  ciaf materialize --receipt {receipt_num} --evidence evidence.json")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)