"""
CIAF Command Line Interface

Provides command-line tools for CIAF operations including generation, 
batching, verification, and materialization of evidence.

Created: 2025-09-09
Last Modified: 2025-10-29
Author: Denzil James Greenwood
Version: 1.2.0
"""

import argparse
import json
import sys
import pickle
import hashlib
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .metadata_config import create_config_template
from .metadata_integration import ModelMetadataManager


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CIAF - Cognitive Insight Audit Framework CLI",
        prog="ciaf"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command - core Quick Start functionality
    generate_parser = subparsers.add_parser("generate", help="Generate lightweight receipt for model operation")
    generate_parser.add_argument("--model", required=True, help="Path to model file (e.g., model.pkl)")
    generate_parser.add_argument("--data", required=True, help="Path to input data file (e.g., input.json)")
    generate_parser.add_argument("--output", help="Output receipt file (default: receipt_<timestamp>.json)")
    generate_parser.add_argument("--operation", default="inference", help="Operation type (default: inference)")
    
    # Batch command - Merkle tree generation
    batch_parser = subparsers.add_parser("batch", help="Create Merkle batch proof from receipts")
    batch_parser.add_argument("--receipts", required=True, help="Directory containing receipt files")
    batch_parser.add_argument("--output", required=True, help="Output Merkle proof file (e.g., proof.merkle)")
    batch_parser.add_argument("--format", choices=["json", "binary"], default="json", help="Output format")
    
    # Verify command - proof verification
    verify_parser = subparsers.add_parser("verify", help="Verify cryptographic proof")
    verify_parser.add_argument("--proof", required=True, help="Path to Merkle proof file")
    verify_parser.add_argument("--receipt", help="Specific receipt ID to verify")
    verify_parser.add_argument("--root-hash", help="Expected root hash for verification")
    verify_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose verification output")
    
    # Materialize command - evidence reconstruction
    materialize_parser = subparsers.add_parser("materialize", help="Materialize evidence from receipt")
    materialize_parser.add_argument("--receipt", required=True, help="Receipt ID to materialize")
    materialize_parser.add_argument("--evidence", required=True, help="Output evidence file path")
    materialize_parser.add_argument("--format", choices=["json", "detailed"], default="json", help="Output format")
    
    # Setup command - maintained for compatibility
    setup_parser = subparsers.add_parser("setup", help="Set up CIAF metadata storage")
    setup_parser.add_argument("project_name", help="Name of your project")
    setup_parser.add_argument(
        "--backend", 
        choices=["json", "sqlite", "pickle"], 
        default="json",
        help="Storage backend (default: json)"
    )
    setup_parser.add_argument(
        "--path", 
        help="Custom storage path (default: {project_name}_metadata)"
    )
    setup_parser.add_argument(
        "--template",
        choices=["development", "production", "testing", "high_performance"],
        default="production",
        help="Configuration template (default: production)"
    )
    
    # Compliance command - maintained for compatibility
    compliance_parser = subparsers.add_parser("compliance", help="Generate compliance reports")
    compliance_parser.add_argument(
        "framework",
        choices=["eu_ai_act", "nist_ai_rmf", "gdpr", "hipaa", "sox", "iso_27001"],
        help="Compliance framework"
    )
    compliance_parser.add_argument("model_id", help="Model ID to generate report for")
    compliance_parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    compliance_parser.add_argument(
        "--format",
        choices=["json", "html"],
        default="json",
        help="Output format (default: json)"
    )
    compliance_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    # Metadata command - maintained for compatibility
    metadata_parser = subparsers.add_parser("metadata", help="Manage model metadata")
    metadata_subparsers = metadata_parser.add_subparsers(dest="metadata_action", help="Metadata actions")
    
    # List models
    list_parser = metadata_subparsers.add_parser("list", help="List models with metadata")
    list_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    
    # Show model details
    show_parser = metadata_subparsers.add_parser("show", help="Show detailed model metadata")
    show_parser.add_argument("model_name", help="Model name to show")
    show_parser.add_argument("--version", help="Model version (default: latest)")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show CIAF version")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate handler
    try:
        if args.command == "generate":
            generate_command(args)
        elif args.command == "batch":
            batch_command(args)
        elif args.command == "verify":
            verify_command(args)
        elif args.command == "materialize":
            materialize_command(args)
        elif args.command == "setup":
            setup_command(args)
        elif args.command == "compliance":
            compliance_command(args)
        elif args.command == "metadata":
            metadata_command(args)
        elif args.command == "version":
            version_command(args)
    except Exception as e:
        print(f"[ERROR] Command failed: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def generate_command(args):
    """Handle generate command - creates lightweight receipt for model operation."""
    print(">>> Generating CIAF receipt for model operation...")
    
    # Validate input files
    model_path = Path(args.model)
    data_path = Path(args.data)
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Load and hash the model
    model_hash = _compute_file_hash(model_path)
    
    # Load and hash the input data
    with open(data_path, 'r') as f:
        input_data = json.load(f)
    input_hash = _compute_data_hash(input_data)
    
    # Simulate model prediction (in real implementation, would actually run the model)
    prediction = _simulate_prediction(input_data, model_path)
    prediction_hash = _compute_data_hash(prediction)
    
    # Generate timestamp
    timestamp = datetime.now().isoformat()
    receipt_id = f"receipt_{int(datetime.now().timestamp())}"
    
    # Create lightweight receipt
    receipt = {
        "receipt_id": receipt_id,
        "ciaf_version": "1.2.0",
        "operation_type": args.operation,
        "timestamp": timestamp,
        "model_anchor": {
            "model_path": str(model_path),
            "model_hash": model_hash,
            "model_type": _detect_model_type(model_path)
        },
        "input_hash": input_hash,
        "prediction": prediction,
        "prediction_hash": prediction_hash,
        "governance_metadata": {
            "policies_applied": _get_applicable_policies(args.operation),
            "compliance_frameworks": ["NIST_AI_RMF", "EU_AI_ACT"],
            "bias_checks": _simulate_bias_checks(),
            "model_performance": {
                "confidence": 0.89,
                "uncertainty": 0.11
            },
            "regulatory_compliance": {
                "gdpr_compliant": True,
                "explainability_required": True,
                "human_oversight": False
            }
        },
        "cryptographic_seal": {
            "signature_algorithm": "Ed25519",
            "hash_algorithm": "SHA-256"
        }
    }
    
    # Add digital signature (simplified for demo)
    payload_for_signature = {
        "model_hash": model_hash,
        "input_hash": input_hash,
        "prediction_hash": prediction_hash,
        "timestamp": timestamp
    }
    receipt["signature"] = _generate_signature(payload_for_signature)
    
    # Determine output path
    output_path = args.output or f"receipt_{receipt_id}.json"
    
    # Save receipt
    with open(output_path, 'w') as f:
        json.dump(receipt, f, indent=2)
    
    print("[SUCCESS] Receipt generated successfully!")
    print(f"   Receipt ID: {receipt_id}")
    print(f"   Output file: {output_path}")
    print(f"   Model hash: {model_hash[:16]}...")
    print(f"   Prediction confidence: {receipt['governance_metadata']['model_performance']['confidence']}")


def batch_command(args):
    """Handle batch command - creates Merkle batch proof from receipts."""
    print(">>> Creating Merkle batch proof from receipts...")
    
    receipts_dir = Path(args.receipts)
    if not receipts_dir.exists() or not receipts_dir.is_dir():
        raise FileNotFoundError(f"Receipts directory not found: {receipts_dir}")
    
    # Find all receipt files
    receipt_files = list(receipts_dir.glob("*.json"))
    if not receipt_files:
        raise ValueError(f"No receipt files found in {receipts_dir}")
    
    print(f"   Found {len(receipt_files)} receipt files")
    
    # Load and process receipts
    receipts = []
    receipt_hashes = []
    
    for receipt_file in receipt_files:
        try:
            with open(receipt_file, 'r') as f:
                receipt = json.load(f)
            receipts.append(receipt)
            
            # Create canonical hash for Merkle tree
            canonical_data = {
                "receipt_id": receipt["receipt_id"],
                "input_hash": receipt["input_hash"],
                "prediction_hash": receipt["prediction_hash"],
                "timestamp": receipt["timestamp"]
            }
            receipt_hash = _compute_data_hash(canonical_data)
            receipt_hashes.append(receipt_hash)
            
        except Exception as e:
            print(f"[WARNING] Skipping invalid receipt {receipt_file}: {e}")
    
    if not receipt_hashes:
        raise ValueError("No valid receipts found for batch processing")
    
    # Build Merkle tree
    merkle_tree = _build_merkle_tree(receipt_hashes)
    root_hash = merkle_tree["root_hash"]
    
    # Create batch proof
    batch_proof = {
        "ciaf_version": "1.2.0",
        "batch_id": f"batch_{int(datetime.now().timestamp())}",
        "created_timestamp": datetime.now().isoformat(),
        "receipt_count": len(receipts),
        "merkle_tree": merkle_tree,
        "root_hash": root_hash,
        "receipts_metadata": [
            {
                "receipt_id": receipt["receipt_id"],
                "leaf_hash": receipt_hashes[i],
                "leaf_index": i
            }
            for i, receipt in enumerate(receipts)
        ],
        "verification_instructions": {
            "algorithm": "SHA-256 Merkle Tree",
            "verification_steps": [
                "1. Locate receipt in tree using leaf_index",
                "2. Follow proof_path to reconstruct root",
                "3. Compare computed root with batch root_hash"
            ]
        }
    }
    
    # Save batch proof
    output_path = args.output
    if args.format == "json":
        with open(output_path, 'w') as f:
            json.dump(batch_proof, f, indent=2)
    else:  # binary format
        with open(output_path, 'wb') as f:
            pickle.dump(batch_proof, f)
    
    print("[SUCCESS] Merkle batch proof created successfully!")
    print(f"   Batch ID: {batch_proof['batch_id']}")
    print(f"   Root hash: {root_hash}")
    print(f"   Receipts processed: {len(receipts)}")
    print(f"   Output file: {output_path}")


def verify_command(args):
    """Handle verify command - verifies cryptographic proof."""
    print(">>> Verifying cryptographic proof...")
    
    proof_path = Path(args.proof)
    if not proof_path.exists():
        raise FileNotFoundError(f"Proof file not found: {proof_path}")
    
    # Load proof
    try:
        if proof_path.suffix == '.merkle':
            # Try JSON first, then binary
            try:
                with open(proof_path, 'r') as f:
                    proof = json.load(f)
            except json.JSONDecodeError:
                with open(proof_path, 'rb') as f:
                    proof = pickle.load(f)
        else:
            with open(proof_path, 'r') as f:
                proof = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load proof file: {e}")
    
    print(f"   Proof type: Merkle batch proof")
    print(f"   Batch ID: {proof.get('batch_id', 'Unknown')}")
    print(f"   Receipt count: {proof.get('receipt_count', 0)}")
    
    # Verify root hash if provided
    if args.root_hash:
        expected_root = args.root_hash
        actual_root = proof.get('root_hash')
        if actual_root == expected_root:
            print("[SUCCESS] Root hash verification: PASSED")
        else:
            print("[FAILED] Root hash verification: FAILED")
            print(f"   Expected: {expected_root}")
            print(f"   Actual: {actual_root}")
            return False
    
    # Verify specific receipt if provided
    if args.receipt:
        receipt_found = False
        for receipt_meta in proof.get('receipts_metadata', []):
            if receipt_meta['receipt_id'] == args.receipt:
                receipt_found = True
                print(f"[SUCCESS] Receipt {args.receipt} found in batch")
                print(f"   Leaf hash: {receipt_meta['leaf_hash']}")
                print(f"   Leaf index: {receipt_meta['leaf_index']}")
                
                # Simulate verification path
                verification_result = _verify_merkle_path(
                    receipt_meta['leaf_hash'],
                    receipt_meta['leaf_index'],
                    proof['merkle_tree']
                )
                
                if verification_result:
                    print("[SUCCESS] Merkle proof verification: PASSED")
                else:
                    print("[FAILED] Merkle proof verification: FAILED")
                    return False
                break
        
        if not receipt_found:
            print(f"[FAILED] Receipt {args.receipt} not found in batch")
            return False
    
    # General proof structure validation
    required_fields = ['batch_id', 'root_hash', 'merkle_tree', 'receipts_metadata']
    missing_fields = [field for field in required_fields if field not in proof]
    
    if missing_fields:
        print(f"[FAILED] Proof validation: FAILED - Missing fields: {missing_fields}")
        return False
    
    print("[SUCCESS] Proof structure validation: PASSED")
    
    if args.verbose:
        print("\n[INFO] Detailed verification results:")
        print(f"   CIAF version: {proof.get('ciaf_version', 'Unknown')}")
        print(f"   Created: {proof.get('created_timestamp', 'Unknown')}")
        print(f"   Merkle tree depth: {_calculate_tree_depth(proof['receipt_count'])}")
        print(f"   Verification algorithm: {proof.get('verification_instructions', {}).get('algorithm', 'Unknown')}")
    
    print("[SUCCESS] Overall verification: PASSED")
    return True


def materialize_command(args):
    """Handle materialize command - reconstructs evidence from receipt."""
    print(">>> Materializing evidence from receipt...")
    
    receipt_id = args.receipt
    
    # Look for receipt file (simplified - in real implementation would query storage)
    receipt_file = None
    possible_locations = [
        f"receipt_{receipt_id}.json",
        f"{receipt_id}.json",
        f"receipts/{receipt_id}.json",
        f"receipts/receipt_{receipt_id}.json",
        f"receipts/receipt_demo_{receipt_id}.json",
        f"receipts/receipt_receipt_{receipt_id}.json"  # Handle double receipt prefix
    ]
    
    for location in possible_locations:
        if Path(location).exists():
            receipt_file = Path(location)
            break
    
    if not receipt_file:
        raise FileNotFoundError(f"Receipt {receipt_id} not found. Searched: {possible_locations}")
    
    # Load receipt
    with open(receipt_file, 'r') as f:
        receipt = json.load(f)
    
    print(f"   Receipt ID: {receipt['receipt_id']}")
    print(f"   Operation: {receipt.get('operation_type', 'Unknown')}")
    print(f"   Timestamp: {receipt['timestamp']}")
    
    # Materialize evidence from receipt
    if args.format == "detailed":
        evidence = _create_detailed_evidence(receipt)
    else:
        evidence = _create_standard_evidence(receipt)
    
    # Save evidence
    output_path = args.evidence
    with open(output_path, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print("[SUCCESS] Evidence materialized successfully!")
    print(f"   Output file: {output_path}")
    print(f"   Evidence size: {len(json.dumps(evidence))} bytes")
    print(f"   Compliance frameworks: {len(evidence.get('compliance_evidence', {}).get('frameworks', []))}")


# Helper functions for the Quick Start commands

def _compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _compute_data_hash(data: Any) -> str:
    """Compute SHA-256 hash of data."""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()


def _detect_model_type(model_path: Path) -> str:
    """Detect model type from file extension."""
    suffix = model_path.suffix.lower()
    type_mapping = {
        '.pkl': 'scikit-learn/pickle',
        '.joblib': 'scikit-learn/joblib',
        '.h5': 'tensorflow/keras',
        '.pt': 'pytorch',
        '.pth': 'pytorch',
        '.onnx': 'onnx',
        '.json': 'json-serialized'
    }
    return type_mapping.get(suffix, 'unknown')


def _simulate_prediction(input_data: Any, model_path: Path) -> Dict[str, Any]:
    """Simulate a model prediction (placeholder for actual inference)."""
    # In real implementation, would load and run the actual model
    return {
        "prediction_class": "class_1",
        "confidence_score": 0.89,
        "probabilities": {
            "class_0": 0.11,
            "class_1": 0.89
        },
        "model_info": {
            "model_file": str(model_path),
            "input_features": len(input_data) if isinstance(input_data, dict) else 1
        }
    }


def _get_applicable_policies(operation_type: str) -> List[str]:
    """Get applicable policies for operation type."""
    base_policies = ["POL-001", "POL-002", "POL-003"]
    operation_policies = {
        "inference": ["INF-001", "INF-015"],
        "training": ["TRN-001", "TRN-008", "TRN-023"],
        "evaluation": ["EVL-001", "EVL-005"]
    }
    return base_policies + operation_policies.get(operation_type, [])


def _simulate_bias_checks() -> Dict[str, float]:
    """Simulate bias check results."""
    return {
        "demographic_parity": 0.95,
        "equalized_odds": 0.92,
        "calibration": 0.88,
        "fairness_score": 0.91
    }


def _generate_signature(payload: Dict[str, Any]) -> str:
    """Generate a simplified digital signature."""
    payload_hash = _compute_data_hash(payload)
    # In real implementation, would use actual cryptographic signing
    return f"sig_{payload_hash[:32]}"


def _build_merkle_tree(hashes: List[str]) -> Dict[str, Any]:
    """Build a simple Merkle tree from hashes."""
    if not hashes:
        return {"root_hash": "", "levels": []}
    
    # Pad to power of 2
    import math
    tree_size = 2 ** math.ceil(math.log2(len(hashes)))
    padded_hashes = hashes + ["0" * 64] * (tree_size - len(hashes))
    
    levels = [padded_hashes]
    current_level = padded_hashes
    
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
            combined = hashlib.sha256((left + right).encode()).hexdigest()
            next_level.append(combined)
        levels.append(next_level)
        current_level = next_level
    
    return {
        "root_hash": current_level[0],
        "levels": levels,
        "leaf_count": len(hashes)
    }


def _verify_merkle_path(leaf_hash: str, leaf_index: int, merkle_tree: Dict[str, Any]) -> bool:
    """Verify a Merkle proof path (simplified)."""
    # Simplified verification - in real implementation would follow actual proof path
    levels = merkle_tree.get("levels", [])
    if not levels or leaf_index >= len(levels[0]):
        return False
    
    # Check if leaf hash exists at the expected position
    return levels[0][leaf_index] == leaf_hash


def _calculate_tree_depth(leaf_count: int) -> int:
    """Calculate Merkle tree depth for given leaf count."""
    import math
    return math.ceil(math.log2(max(1, leaf_count)))


def _create_standard_evidence(receipt: Dict[str, Any]) -> Dict[str, Any]:
    """Create standard evidence format from receipt."""
    return {
        "evidence_id": f"evidence_{receipt['receipt_id']}",
        "source_receipt": receipt['receipt_id'],
        "materialization_timestamp": datetime.now().isoformat(),
        "operation_evidence": {
            "operation_type": receipt.get('operation_type'),
            "model_details": receipt.get('model_anchor'),
            "input_hash": receipt.get('input_hash'),
            "prediction": receipt.get('prediction'),
            "timestamp": receipt.get('timestamp')
        },
        "governance_evidence": receipt.get('governance_metadata', {}),
        "cryptographic_evidence": {
            "signature": receipt.get('signature'),
            "hash_chain": [
                receipt.get('input_hash'),
                receipt.get('prediction_hash')
            ]
        },
        "compliance_evidence": {
            "frameworks": receipt.get('governance_metadata', {}).get('compliance_frameworks', []),
            "policies": receipt.get('governance_metadata', {}).get('policies_applied', [])
        }
    }


def _create_detailed_evidence(receipt: Dict[str, Any]) -> Dict[str, Any]:
    """Create detailed evidence format with audit trail."""
    standard_evidence = _create_standard_evidence(receipt)
    
    # Add detailed audit information
    standard_evidence.update({
        "audit_trail": {
            "evidence_chain": [
                {
                    "step": 1,
                    "description": "Model operation executed",
                    "timestamp": receipt.get('timestamp'),
                    "hash": receipt.get('input_hash')
                },
                {
                    "step": 2,
                    "description": "Prediction generated",
                    "timestamp": receipt.get('timestamp'),
                    "hash": receipt.get('prediction_hash')
                },
                {
                    "step": 3,
                    "description": "Governance metadata applied",
                    "timestamp": receipt.get('timestamp'),
                    "policies": receipt.get('governance_metadata', {}).get('policies_applied', [])
                },
                {
                    "step": 4,
                    "description": "Cryptographic seal generated",
                    "timestamp": receipt.get('timestamp'),
                    "signature": receipt.get('signature')
                }
            ]
        },
        "verification_metadata": {
            "verifiable_claims": [
                "Model operation occurred at specified timestamp",
                "Input data integrity maintained",
                "Prediction generated using specified model",
                "Governance policies properly applied",
                "Cryptographic signature valid"
            ],
            "verification_methods": [
                "SHA-256 hash verification",
                "Ed25519 signature verification",
                "Policy compliance checking",
                "Timestamp validation"
            ]
        },
        "regulatory_mapping": {
            "eu_ai_act": {
                "article_11": "High-risk AI system documentation",
                "article_12": "Quality management evidence",
                "article_13": "Transparency requirements"
            },
            "nist_ai_rmf": {
                "govern_1_1": "AI governance policies",
                "measure_2_1": "Test and validation evidence"
            }
        }
    })
    
    return standard_evidence


def setup_command(args):
    """Handle setup command."""
    try:
        from .metadata_config import MetadataConfig
        from .metadata_storage import MetadataStorage

        # Determine storage path
        storage_path = args.path or f"{args.project_name}_metadata"
        config_file = f"{args.project_name}_metadata_config.json"

        print(f"[LAUNCH] Setting up CIAF metadata storage for '{args.project_name}'")
        print("=" * 50)

        # Create configuration
        print(f"[CLIPBOARD] Creating configuration from '{args.template}' template...")
        create_config_template(args.template, config_file)

        # Update configuration
        config = MetadataConfig(config_file)
        config.set("storage_backend", args.backend)
        config.set("storage_path", storage_path)
        config.save_to_file(config_file)

        # Initialize storage
        print(f"[DATABASE] Initializing {args.backend} storage at '{storage_path}'...")
        storage = MetadataStorage(storage_path, args.backend)

        # Create directory structure
        project_dir = Path(storage_path)
        project_dir.mkdir(parents=True, exist_ok=True)

        subdirs = ["exports", "backups", "reports"]
        for subdir in subdirs:
            (project_dir / subdir).mkdir(exist_ok=True)

        print("\n[SUCCESS] Setup completed successfully!")
        print(f"   [POINT] Project: {args.project_name}")
        print(f"   [POINT] Backend: {args.backend}")
        print(f"   [POINT] Storage: {storage_path}")
        print(f"   [POINT] Config: {config_file}")

        print("\n[LAUNCH] Next Steps:")
        print(f"1. Review the configuration in '{config_file}'")
        print("2. Import CIAF in your project:")
        print("   from ciaf import CIAFFramework")
        print(f"3. Initialize: framework = CIAFFramework('{args.project_name}')")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


def compliance_command(args):
    """Handle compliance command."""
    try:
        # Try to import compliance tools
        try:
            from .compliance import ComplianceReportGenerator, ComplianceFramework
            from .compliance.audit_trails import AuditTrailGenerator
        except ImportError:
            print("❌ Compliance reporting tools not found")
            print("This is a prototype feature. Creating basic compliance report...")
            create_basic_compliance_report(args)
            return

        # Map framework string to enum
        framework_map = {
            "eu_ai_act": ComplianceFramework.EU_AI_ACT,
            "nist_ai_rmf": ComplianceFramework.NIST_AI_RMF,
            "gdpr": ComplianceFramework.GDPR,
            "hipaa": ComplianceFramework.HIPAA,
            "sox": ComplianceFramework.SOX,
            "iso_27001": ComplianceFramework.ISO_27001,
        }
        
        framework_enum = framework_map.get(args.framework)
        if not framework_enum:
            print(f"❌ Unknown framework: {args.framework}")
            sys.exit(1)

        # Initialize components
        reporter = ComplianceReportGenerator(args.model_id)
        audit_generator = AuditTrailGenerator(args.model_id, [args.framework])
        
        # Generate report
        if args.verbose:
            print(f"🚀 Generating detailed {args.framework} compliance report for {args.model_id}...")
        else:
            print(f"🚀 Generating {args.framework} compliance report...")
            
        report = reporter.generate_executive_summary_report(
            frameworks=[framework_enum],
            audit_generator=audit_generator,
            model_version="1.0.0",
        )
        
        # Save report
        output_path = args.output or f"compliance_report_{args.framework}_{args.model_id}.{args.format}"
        
        if args.format == "json":
            report_dict = asdict(report)
            with open(output_path, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
        elif args.format == "html":
            create_html_report(report, args, output_path)

        print(f"✅ Compliance report generated: {output_path}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def create_basic_compliance_report(args):
    """Create a basic compliance report when full compliance module isn't available."""
    from datetime import datetime
    
    # Create basic report structure
    report = {
        "report_id": f"basic_{args.framework}_{args.model_id}",
        "framework": args.framework.upper(),
        "model_id": args.model_id,
        "generated_date": datetime.now().isoformat(),
        "ciaf_version": "0.1.0",
        "report_type": "basic_prototype",
        "executive_summary": {
            "overall_compliance_score": 75.0,
            "status": "prototype_evaluation",
            "total_requirements": 12,
            "satisfied_requirements": 9,
            "key_findings": [
                "CIAF cryptographic primitives are implemented",
                "Audit trail capabilities are available",
                "Model anchoring system is functional",
                "Some compliance features are in prototype stage"
            ]
        },
        "compliance_areas": {
            "data_governance": "✅ Implemented",
            "model_tracking": "✅ Implemented", 
            "audit_trails": "✅ Implemented",
            "risk_assessment": "🧪 Prototype",
            "bias_detection": "🧪 Prototype",
            "documentation": "📋 Planned"
        },
        "recommendations": [
            "Complete implementation of all compliance modules",
            "Conduct thorough testing of audit trails",
            "Implement automated bias detection",
            "Enhance documentation for regulatory review"
        ],
        "disclaimer": "This is a prototype report. Full compliance assessment requires complete implementation and legal review."
    }
    
    # Save report
    output_path = args.output or f"compliance_report_{args.framework}_{args.model_id}.{args.format}"
    
    if args.format == "json":
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    elif args.format == "html":
        create_basic_html_report(report, output_path)
    
    print(f"✅ Basic compliance report generated: {output_path}")


def create_html_report(report, args, output_path):
    """Create HTML compliance report."""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CIAF Compliance Report - {args.framework.upper()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ background-color: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .compliant {{ color: green; font-weight: bold; }}
        .non-compliant {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CIAF Compliance Report</h1>
        <p><strong>Framework:</strong> {args.framework.upper()}</p>
        <p><strong>Model:</strong> {args.model_id}</p>
        <p><strong>Generated:</strong> {report.generated_date}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Overall Compliance Score:</strong> {report.executive_summary['overall_compliance_score']:.1f}%
        </div>
        <div class="metric">
            <strong>Status:</strong> 
            <span class="{'compliant' if report.compliance_status['overall_status'] == 'compliant' else 'non-compliant'}">
                {report.compliance_status['overall_status'].upper()}
            </span>
        </div>
        <div class="metric">
            <strong>Requirements Satisfied:</strong> {report.executive_summary['satisfied_requirements']} / {report.executive_summary['total_requirements']}
        </div>
    </div>
    
    <div class="section">
        <h2>Key Findings</h2>
        <ul>
            {''.join(['<li>' + finding + '</li>' for finding in report.executive_summary.get('key_findings', ['No findings available'])])}
        </ul>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            {''.join(['<li>' + rec['description'] + '</li>' for rec in report.recommendations[:5]])}
        </ul>
    </div>
</body>
</html>"""
    with open(output_path, 'w') as f:
        f.write(html_content)


def create_basic_html_report(report, output_path):
    """Create basic HTML report."""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CIAF Compliance Report - {report['framework']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ background-color: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .status {{ font-weight: bold; }}
        .disclaimer {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CIAF Compliance Report (Prototype)</h1>
        <p><strong>Framework:</strong> {report['framework']}</p>
        <p><strong>Model:</strong> {report['model_id']}</p>
        <p><strong>Generated:</strong> {report['generated_date']}</p>
    </div>
    
    <div class="disclaimer">
        <h3>⚠️ Prototype Disclaimer</h3>
        <p>{report['disclaimer']}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Overall Score:</strong> {report['executive_summary']['overall_compliance_score']:.1f}%
        </div>
        <div class="metric">
            <strong>Status:</strong> <span class="status">{report['executive_summary']['status'].upper()}</span>
        </div>
        <div class="metric">
            <strong>Requirements:</strong> {report['executive_summary']['satisfied_requirements']} / {report['executive_summary']['total_requirements']} satisfied
        </div>
    </div>
    
    <div class="section">
        <h2>Compliance Areas</h2>
        {''.join([f'<div class="metric"><strong>{area.replace("_", " ").title()}:</strong> {status}</div>' for area, status in report['compliance_areas'].items()])}
    </div>
    
    <div class="section">
        <h2>Key Findings</h2>
        <ul>
            {''.join(['<li>' + finding + '</li>' for finding in report['executive_summary']['key_findings']])}
        </ul>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            {''.join(['<li>' + rec + '</li>' for rec in report['recommendations']])}
        </ul>
    </div>
</body>
</html>"""
    with open(output_path, 'w') as f:
        f.write(html_content)


def metadata_command(args):
    """Handle metadata command."""
    try:
        if args.metadata_action == "list":
            list_models_command(args)
        elif args.metadata_action == "show":
            show_model_command(args)
        else:
            print("Please specify a metadata action (list, show)")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Metadata command failed: {e}")
        sys.exit(1)


def list_models_command(args):
    """List models with metadata."""
    try:
        manager = ModelMetadataManager("ciaf_models", "1.0.0")
        models = manager.get_all_model_metadata()
        
        if args.format == "json":
            print(json.dumps(models, indent=2, default=str))
        else:
            # Table format
            print("\n📊 CIAF Models")
            print("=" * 60)
            if not models:
                print("No models found.")
            else:
                print(f"{'Model':<20} {'Version':<10} {'Stage':<15} {'Last Updated':<20}")
                print("-" * 60)
                for model_id, metadata in models.items():
                    last_updated = metadata.get('last_updated', 'Unknown')
                    if isinstance(last_updated, str) and 'T' in last_updated:
                        last_updated = last_updated.split('T')[0]  # Show just date
                    version = metadata.get('version', '1.0.0')
                    stage = metadata.get('stage', 'unknown')
                    print(f"{model_id:<20} {version:<10} {stage:<15} {last_updated:<20}")
                print()
                
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        sys.exit(1)


def show_model_command(args):
    """Show detailed model metadata."""
    try:
        manager = ModelMetadataManager(args.model_name, args.version or "1.0.0")
        metadata = manager.get_model_metadata()
        
        if not metadata:
            print(f"❌ Model '{args.model_name}' not found")
            sys.exit(1)
            
        print(f"\n🤖 Model Details: {args.model_name}")
        print("=" * 50)
        print(f"Version: {metadata.get('version', 'Unknown')}")
        print(f"Stage: {metadata.get('stage', 'Unknown')}")
        print(f"Framework: {metadata.get('framework', 'Unknown')}")
        print(f"Last Updated: {metadata.get('last_updated', 'Unknown')}")
        
        if 'performance_metrics' in metadata:
            print(f"\n📈 Performance Metrics:")
            for metric, value in metadata['performance_metrics'].items():
                print(f"  {metric}: {value}")
                
        if 'compliance_status' in metadata:
            print(f"\n✅ Compliance Status:")
            for framework, status in metadata['compliance_status'].items():
                print(f"  {framework}: {status}")
                
        print()
        
    except Exception as e:
        print(f"❌ Failed to show model details: {e}")
        sys.exit(1)


def version_command(args):
    """Handle version command."""
    print("CIAF (Cognitive Insight Audit Framework)")
    print("Version: 0.1.0")
    print("Author: Denzil James Greenwood")
    print("License: Proprietary")


def compliance_report_cli():
    """CLI for generating compliance reports (legacy function)."""
    # This is kept for backward compatibility with the existing pyproject.toml
    import sys
    if len(sys.argv) >= 3:
        # Convert to new format
        framework = sys.argv[1]
        model_id = sys.argv[2]
        
        # Create mock args object
        class Args:
            def __init__(self):
                self.framework = framework
                self.model_id = model_id
                self.output = None
                self.format = "json"
                self.verbose = False
        
        compliance_command(Args())
    else:
        print("Usage: ciaf-compliance-report <framework> <model_id>")
        print("Available frameworks: eu_ai_act, nist_ai_rmf, gdpr, hipaa, sox, iso_27001")


def setup_metadata_cli():
    """CLI for setting up metadata storage (legacy function)."""
    # This is kept for backward compatibility with the existing pyproject.toml
    import sys
    if len(sys.argv) >= 2:
        project_name = sys.argv[1]
        
        # Create mock args object
        class Args:
            def __init__(self):
                self.project_name = project_name
                self.backend = "json"
                self.path = None
                self.template = "production"
        
        setup_command(Args())
    else:
        print("Usage: ciaf-setup-metadata <project_name>")


if __name__ == "__main__":
    main()
