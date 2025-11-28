# CIAF Governed LLM Stack - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GOVERNANCE & POLICY LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  EU AI Act   │  │  NIST AI RMF │  │  ISO 42001   │  │   Custom    │ │
│  │   Policies   │  │   Policies   │  │   Policies   │  │  Policies   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                            GATE ENGINE                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   Data   │  │  Model   │  │   Eval   │  │  Deploy  │  │ Runtime  │ │
│  │  Gates   │  │  Gates   │  │  Gates   │  │  Gates   │  │  Gates   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        CIAF ANCHOR REGISTRY                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Dataset   │  │    Model    │  │  Training   │  │ Deployment  │   │
│  │   Anchors   │  │   Anchors   │  │   Anchors   │  │   Anchors   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    LCM STORAGE & RECEIPTS                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Compressed Capsules: Logs, Metrics, Configs, Evaluations       │   │
│  │  Merkle Receipts: Cryptographic proofs for all artifacts        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      HUGGINGFACE INTEGRATION                             │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐    │
│  │   Datasets API           │  │   Transformers/Models API        │    │
│  │   • load_dataset()       │  │   • AutoModel.from_pretrained()  │    │
│  │   • Dataset cards        │  │   • Model cards                  │    │
│  │   • Version tracking     │  │   • Safetensors                  │    │
│  └──────────────────────────┘  └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: HuggingFace → Governed Production LLM

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: GOVERNANCE BOOTSTRAP                                            │
│                                                                           │
│  Define Risk Profile → Create Policy Bundle → Generate System Anchor    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATASET INTAKE (HuggingFace → CIAF)                            │
│                                                                           │
│  HF Dataset  →  Create DatasetAnchor  →  License Gate                   │
│                        ↓                        ↓                        │
│                 Generate Receipt          Safety Gate                    │
│                                                 ↓                        │
│                                           PII Gate                       │
│                                                 ↓                        │
│                              [APPROVED] → Transform & Curate             │
│                                                 ↓                        │
│                              Create CuratedDatasetAnchor                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: BASE MODEL SELECTION                                           │
│                                                                           │
│  HF Model  →  Create ModelAnchor  →  License Gate                       │
│                      ↓                      ↓                            │
│              Generate Receipt         Capability Risk Gate               │
│                                            ↓                             │
│                            [APPROVED] → Ready for Training               │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: TRAINING PIPELINE (Gated)                                      │
│                                                                           │
│  TrainingConfig  →  TrainingPlanGate  →  [APPROVED]                     │
│                                                 ↓                        │
│                              Create TrainingRunAnchor                    │
│                                                 ↓                        │
│                       Execute Training (LCM logging)                     │
│                                                 ↓                        │
│                              ReproducibilityGate                         │
│                                                 ↓                        │
│                      [PASSED] → CandidateModelAnchor                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: EVALUATION & SAFETY                                            │
│                                                                           │
│  Evaluation Suites  →  Run Benchmarks  →  Store in LCM                  │
│                              ↓                                           │
│                     Safety Red-Teaming                                   │
│                              ↓                                           │
│                   ReleaseReadinessGate                                   │
│                              ↓                                           │
│     [APPROVED] → Create DeploymentCandidateAnchor                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: DEPLOYMENT                                                     │
│                                                                           │
│  DeploymentConfig  →  DeploymentGate  →  [APPROVED]                     │
│                                                ↓                         │
│                       Create DeploymentConfigAnchor                      │
│                                                ↓                         │
│                            Deploy to Environment                         │
│                                                ↓                         │
│                     Configure Runtime Safety Stack                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: RUNTIME INFERENCE (Gated)                                      │
│                                                                           │
│  Request  →  AuthGate  →  PromptGate  →  [Model Inference]              │
│                                                    ↓                     │
│                                            OutputSafetyGate              │
│                                                    ↓                     │
│                                             LoggingGate                  │
│                                                    ↓                     │
│                                [Response + LCM Receipt]                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 7: MONITORING & GOVERNANCE                                        │
│                                                                           │
│  Continuous Monitoring  →  DriftGate  →  [Drift Detection]              │
│                                                  ↓                       │
│                                    [Threshold Exceeded]                  │
│                                                  ↓                       │
│                           Require Re-evaluation/Retraining               │
│                                                  ↓                       │
│                              Change Management Process                   │
│                                                  ↓                       │
│                     New Version → Back to Phase 1/2/3                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Anchor Registry

#### DatasetAnchor
```python
{
    "anchor_id": "dataset_anchor_xyz123",
    "hf_repo_id": "squad",
    "hf_revision": "3c9c8c0",
    "license_spdx": "CC-BY-4.0",
    "hash_tree_root": "merkle_root_abc...",
    "schema": {
        "columns": ["id", "title", "context", "question", "answers"],
        "types": ["str", "str", "str", "str", "dict"]
    },
    "lineage": {
        "source_url": "https://huggingface.co/datasets/squad",
        "ingestion_timestamp": "2025-11-24T10:30:00Z"
    },
    "gate_approvals": [
        {"gate": "DatasetLicenseGate", "status": "APPROVED", "receipt": "..."},
        {"gate": "DatasetSafetyScanGate", "status": "APPROVED", "receipt": "..."}
    ]
}
```

#### ModelAnchor
```python
{
    "anchor_id": "model_anchor_abc456",
    "hf_repo_id": "meta-llama/Meta-Llama-3-8B",
    "hf_revision": "7e1d3f2",
    "license": "Llama-3-Community",
    "model_family": "llama-3",
    "parameter_count": "8B",
    "weight_files_hash": "merkle_root_def...",
    "intended_use": ["research", "commercial"],
    "known_limitations": ["may generate biased content", "not medical device"],
    "gate_approvals": [
        {"gate": "BaseModelLicenseGate", "status": "APPROVED", "receipt": "..."},
        {"gate": "CapabilityRiskGate", "status": "APPROVED_WITH_CONSTRAINTS", "receipt": "..."}
    ]
}
```

#### TrainingRunAnchor
```python
{
    "anchor_id": "training_run_xyz789",
    "dataset_anchor_id": "dataset_anchor_xyz123",
    "base_model_anchor_id": "model_anchor_abc456",
    "hyperparameters": {
        "learning_rate": 2e-5,
        "batch_size": 16,
        "epochs": 3,
        "optimizer": "AdamW"
    },
    "hardware": "8x NVIDIA A100",
    "training_duration_seconds": 86400,
    "final_checkpoint_hash": "checkpoint_hash_ghi...",
    "lcm_capsule_refs": ["capsule_001", "capsule_002", "..."],
    "gate_approvals": [
        {"gate": "TrainingPlanGate", "status": "APPROVED", "receipt": "..."},
        {"gate": "ReproducibilityGate", "status": "PASSED", "receipt": "..."}
    ]
}
```

---

### 2. Gate Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         GATE EXECUTION                           │
│                                                                   │
│  Input:                                                           │
│    • Proposed Action (e.g., "train model with dataset X")       │
│    • Current Anchors (dataset, model, config)                   │
│    • Policy Bundle                                               │
│                                                                   │
│  Process:                                                         │
│    1. Load applicable policies                                   │
│    2. Evaluate constraints                                       │
│    3. Check evidence requirements                                │
│    4. Apply risk scoring                                         │
│    5. Generate decision                                          │
│                                                                   │
│  Output:                                                          │
│    • Decision: ALLOW | DENY | REQUIRE_HUMAN_REVIEW              │
│    • Reasoning: Policy references + constraint violations        │
│    • Receipt: Cryptographic proof of gate decision               │
│    • Next Actions: What must happen before progression           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. LCM Capsule Structure

```python
{
    "capsule_id": "lcm_capsule_001",
    "capsule_type": "training_logs",
    "anchor_ref": "training_run_xyz789",
    "compression": "zstd",
    "time_range": {
        "start": "2025-11-24T00:00:00Z",
        "end": "2025-11-25T00:00:00Z"
    },
    "events": [
        {
            "timestamp": "2025-11-24T00:15:33Z",
            "event_type": "checkpoint_saved",
            "data": {
                "step": 1000,
                "loss": 0.342,
                "checkpoint_hash": "hash_jkl..."
            }
        },
        # ... thousands more events compressed
    ],
    "merkle_root": "capsule_merkle_root_mno...",
    "materialization_policy": "lazy",
    "retention_period_days": 2555  # 7 years for compliance
}
```

---

### 4. Runtime Safety Stack

```
┌─────────────────────────────────────────────────────────────┐
│               INFERENCE REQUEST PROCESSING                   │
│                                                               │
│  User Request                                                 │
│       ↓                                                       │
│  ┌─────────────┐                                             │
│  │  AuthGate   │ → Verify API key, tenant, permissions      │
│  └─────────────┘                                             │
│       ↓                                                       │
│  ┌─────────────┐                                             │
│  │ PromptGate  │ → Check for:                                │
│  └─────────────┘   • Injection attacks                       │
│       ↓            • Disallowed topics                       │
│                    • Prompt jailbreaks                       │
│  ┌─────────────────────────┐                                 │
│  │  Model Inference        │                                 │
│  │  (with logging)         │                                 │
│  └─────────────────────────┘                                 │
│       ↓                                                       │
│  ┌─────────────────┐                                         │
│  │ OutputSafetyGate│ → Check for:                            │
│  └─────────────────┘   • Harmful content                     │
│       ↓                • PII leakage                         │
│                        • Policy violations                   │
│  ┌─────────────┐                                             │
│  │ LoggingGate │ → Store to LCM:                             │
│  └─────────────┘   • Full request/response                   │
│       ↓            • Gate decisions                          │
│                    • Performance metrics                     │
│  Response to User                                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### HuggingFace APIs

```python
# Dataset loading with CIAF anchoring
from datasets import load_dataset
from ciaf.llm import DatasetAnchor, DatasetGateEngine

# Load HF dataset
hf_dataset = load_dataset("squad", revision="3c9c8c0")

# Create CIAF anchor
dataset_anchor = DatasetAnchor.from_hf_dataset(
    dataset=hf_dataset,
    license_spdx="CC-BY-4.0",
    policy_bundle=policy_bundle
)

# Run gates
gate_results = DatasetGateEngine.evaluate(
    anchor=dataset_anchor,
    gates=["license", "safety", "pii"]
)

# If approved, proceed
if gate_results.all_approved():
    curated_dataset = transform_and_clean(hf_dataset)
    curated_anchor = dataset_anchor.create_curated_version(curated_dataset)
```

---

## Security & Compliance

### Cryptographic Guarantees

1. **Immutable Anchors**: Each anchor is content-addressed (hash-based ID)
2. **Merkle Receipts**: All artifacts have verifiable proofs
3. **Gate Decisions**: Signed and timestamped
4. **LCM Capsules**: Tamper-evident compressed storage

### Audit Trail

Every action generates:
- **Who**: User/system identity
- **What**: Action and artifacts
- **When**: Timestamp (with timezone)
- **Why**: Policy references
- **How**: Gate decisions and reasoning
- **Proof**: Cryptographic receipts

### Compliance Mappings

| Framework | CIAF Components | Evidence |
|-----------|----------------|----------|
| EU AI Act Article 10 (Data Governance) | DatasetAnchor, PIIGate, DatasetLicenseGate | Dataset receipts, gate decisions |
| EU AI Act Article 11 (Documentation) | All Anchors, LCM Capsules | Complete provenance chain |
| EU AI Act Article 12 (Record-keeping) | LCM Storage, Receipts | 7-year retention, tamper-proof |
| NIST AI RMF (MAP) | RiskProfile, PolicyBundle | Risk assessments, policy mappings |
| NIST AI RMF (MEASURE) | EvaluationSuiteAnchor, DriftGate | Benchmark results, monitoring |
| NIST AI RMF (MANAGE) | All Gates, Change Management | Gate approvals, version control |
| ISO 42001 (Clause 7.4) | TrainingRunAnchor, ModelAnchor | Training documentation, lineage |

---

## Performance Considerations

### Lazy Materialization

- **Training logs**: Compressed into LCM capsules, materialized only for debugging
- **Checkpoints**: Hash-referenced, downloaded on-demand
- **Evaluation data**: Summarized in anchors, full data in capsules

### Scalability

- **Distributed gates**: Gates can run in parallel
- **Async processing**: Non-blocking gate evaluation
- **Caching**: Anchor registry with efficient lookups
- **Batch operations**: Multiple artifacts processed together

### Storage Efficiency

- **LCM compression**: 10-100x reduction in log storage
- **Merkle trees**: Compact proofs (KB vs GB)
- **Deduplication**: Same datasets/models referenced, not copied

---

## Next Steps

See implementation guides:
- `implementation_guide.md` - Step-by-step code examples
- `gate_catalog.md` - Complete gate specifications
- `api_reference.md` - Python API documentation
- `deployment_playbook.md` - Production deployment guide
