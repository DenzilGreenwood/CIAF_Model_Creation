#!/usr/bin/env python3
"""
CIAF Quick Start Demo Script

Demonstrates the complete CIAF CLI workflow:
1. Generate receipts for model operations
2. Create Merkle batch proof
3. Verify cryptographic proofs
4. Materialize evidence from receipts

Usage: python demo_quickstart.py
"""

import subprocess
import json
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n🔧 {description}")
    print(f"   Command: {' '.join(cmd)}")
    print("   " + "="*50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"   Warning: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Run the complete CIAF Quick Start demo."""
    
    print("🚀 CIAF Quick Start Demo")
    print("="*60)
    print("This demo shows the complete CIAF CLI workflow:")
    print("1. Generate lightweight receipts")
    print("2. Create Merkle batch proofs") 
    print("3. Verify cryptographic integrity")
    print("4. Materialize audit evidence")
    print()
    
    # Clean up any existing files
    for file in ["proof.merkle", "evidence.json"]:
        Path(file).unlink(missing_ok=True)
    
    # Ensure receipts directory exists
    Path("receipts").mkdir(exist_ok=True)
    
    # Remove existing receipts for clean demo
    for receipt in Path("receipts").glob("*.json"):
        receipt.unlink()
    
    # Step 1: Generate receipts
    success = True
    
    success &= run_command([
        "python", "-m", "ciaf.cli", "generate",
        "--model", "model.pkl",
        "--data", "input.json",
        "--output", "receipts/receipt_demo_001.json"
    ], "Step 1a: Generate first receipt")
    
    success &= run_command([
        "python", "-m", "ciaf.cli", "generate", 
        "--model", "model.pkl",
        "--data", "input.json",
        "--output", "receipts/receipt_demo_002.json"
    ], "Step 1b: Generate second receipt")
    
    success &= run_command([
        "python", "-m", "ciaf.cli", "generate",
        "--model", "model.pkl", 
        "--data", "input.json",
        "--output", "receipts/receipt_demo_003.json"
    ], "Step 1c: Generate third receipt")
    
    # Step 2: Create Merkle batch
    success &= run_command([
        "python", "-m", "ciaf.cli", "batch",
        "--receipts", "receipts/",
        "--output", "proof.merkle"
    ], "Step 2: Create Merkle batch proof")
    
    # Load proof to get receipt info
    if Path("proof.merkle").exists():
        with open("proof.merkle", 'r') as f:
            proof_data = json.load(f)
        
        receipt_id = proof_data["receipts_metadata"][0]["receipt_id"]
        root_hash = proof_data["root_hash"]
        
        # Step 3: Verify proof
        success &= run_command([
            "python", "-m", "ciaf.cli", "verify",
            "--proof", "proof.merkle",
            "--receipt", receipt_id,
            "--verbose"
        ], f"Step 3a: Verify specific receipt {receipt_id}")
        
        success &= run_command([
            "python", "-m", "ciaf.cli", "verify",
            "--proof", "proof.merkle",
            "--root-hash", root_hash
        ], "Step 3b: Verify root hash")
    
    # Step 4: Materialize evidence
    success &= run_command([
        "python", "-m", "ciaf.cli", "materialize",
        "--receipt", "demo_001",
        "--evidence", "evidence.json"
    ], "Step 4a: Materialize evidence (standard format)")
    
    success &= run_command([
        "python", "-m", "ciaf.cli", "materialize",
        "--receipt", "demo_002", 
        "--evidence", "evidence_detailed.json",
        "--format", "detailed"
    ], "Step 4b: Materialize evidence (detailed format)")
    
    # Show final results
    print(f"\n📊 Demo Results Summary")
    print("="*40)
    
    if success:
        print("✅ All commands executed successfully!")
        
        # Show generated files
        print(f"\n📁 Generated Files:")
        for file in ["proof.merkle", "evidence.json", "evidence_detailed.json"]:
            if Path(file).exists():
                size = Path(file).stat().st_size
                print(f"   • {file} ({size} bytes)")
        
        receipt_count = len(list(Path("receipts").glob("*.json")))
        print(f"   • receipts/ directory ({receipt_count} receipts)")
        
        # Show proof details
        if Path("proof.merkle").exists():
            with open("proof.merkle", 'r') as f:
                proof = json.load(f)
            print(f"\n🔐 Cryptographic Proof Details:")
            print(f"   • Batch ID: {proof['batch_id']}")
            print(f"   • Root Hash: {proof['root_hash'][:32]}...")
            print(f"   • Receipts: {proof['receipt_count']}")
        
        # Show evidence details
        if Path("evidence.json").exists():
            with open("evidence.json", 'r') as f:
                evidence = json.load(f)
            print(f"\n📋 Evidence Details:")
            print(f"   • Evidence ID: {evidence['evidence_id']}")
            print(f"   • Compliance Frameworks: {len(evidence['compliance_evidence']['frameworks'])}")
            print(f"   • Applied Policies: {len(evidence['compliance_evidence']['policies'])}")
        
        print(f"\n🎯 Next Steps:")
        print("   • Review generated receipts in receipts/ directory")
        print("   • Examine Merkle proof structure in proof.merkle")
        print("   • Analyze materialized evidence in evidence files")
        print("   • Integrate CIAF commands into your ML pipeline")
        
    else:
        print("❌ Some commands failed. Check the output above for details.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)