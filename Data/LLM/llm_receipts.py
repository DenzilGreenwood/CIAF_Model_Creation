"""
LLM Receipt Data Structures

Implements receipt data structures for LLM operations following the 
CIAF Inference and Training Structures specification.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


@dataclass 
class LLMInferenceReceipt:
    """
    Lightweight receipt for LLM inference operations.
    Implements the CIAF LCM Inference Receipt structure.
    """
    
    # Core identification
    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""                   # Request correlation ID
    
    # LLM-specific identifiers
    deployment_anchor_ref: str = ""        # Reference to deployment anchor
    model_version: Optional[str] = None    # Specific model version used
    
    # Cryptographic commitments for privacy
    query_hash: str = ""                   # SHA-256 of input query/prompt
    response_hash: str = ""                # SHA-256 of generated response
    query_commitment: Optional[str] = None  # Privacy-preserving input commitment
    response_commitment: Optional[str] = None  # Privacy-preserving output commitment
    
    # LLM inference metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Inference parameters used
    inference_config: Dict[str, Any] = field(default_factory=dict)
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    
    # Performance metrics
    latency_ms: Optional[float] = None     # Response latency in milliseconds
    token_count_input: Optional[int] = None  # Input token count
    token_count_output: Optional[int] = None  # Output token count
    compute_units: Optional[float] = None   # Compute units consumed
    
    # Quality and safety metrics
    confidence_score: Optional[float] = None  # Model confidence
    safety_score: Optional[float] = None   # Safety assessment score
    bias_indicators: Dict[str, float] = field(default_factory=dict)
    content_flags: List[str] = field(default_factory=list)
    
    # Explanation and interpretability
    explanation_data: Optional[Dict[str, Any]] = None
    attention_weights: Optional[str] = None  # Hash of attention patterns
    layer_activations: Optional[str] = None  # Hash of layer activations
    
    # Optional encrypted data for audit materialization
    raw_query: Optional[str] = None        # Encrypted input data
    raw_response: Optional[str] = None     # Encrypted output data
    
    # Operational metadata
    priority: str = "normal"               # Processing priority
    evidence_strength: str = "real"        # Evidence reliability classification
    
    # Verification and compliance
    committed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    signature: Optional[str] = None        # Digital signature
    policy: Optional[Any] = None           # LCM Policy reference


@dataclass
class LLMTrainingSession:
    """
    Comprehensive training session record for LLM training processes.
    Implements the CIAF Training Session Structure.
    """
    
    # Core identification
    session_id: str = ""                   # Training session identifier
    anchor_id: Optional[str] = None        # Derived anchor identifier
    
    # Training configuration
    model_anchor_ref: str = ""             # Reference to model anchor
    dataset_anchor_ref: Optional[str] = None  # Reference to training dataset
    base_model_ref: Optional[str] = None   # Reference to base model (for fine-tuning)
    
    # LLM-specific training configuration
    training_type: str = "full_training"   # 'full_training', 'fine_tuning', 'rlhf'
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    
    # Standard training hyperparameters for LLMs
    learning_rate: Optional[float] = None
    batch_size: Optional[int] = None
    sequence_length: Optional[int] = None
    gradient_accumulation_steps: Optional[int] = None
    warmup_steps: Optional[int] = None
    weight_decay: Optional[float] = None
    dropout_rate: Optional[float] = None
    
    # Training progress tracking
    total_epochs: Optional[int] = None
    epochs_completed: int = 0
    total_steps: Optional[int] = None
    steps_completed: int = 0
    
    # Training metrics by epoch/step
    training_metrics: Dict[str, List[float]] = field(default_factory=dict)
    validation_metrics: Dict[str, List[float]] = field(default_factory=dict)
    
    # LLM-specific metrics
    perplexity_history: List[float] = field(default_factory=list)
    loss_history: List[float] = field(default_factory=list)
    bleu_scores: List[float] = field(default_factory=list)
    rouge_scores: Dict[str, List[float]] = field(default_factory=dict)
    
    # Checkpoint management
    checkpoint_hashes: List[str] = field(default_factory=list)
    best_checkpoint_hash: Optional[str] = None
    checkpoint_frequency: Optional[int] = None
    
    # Resource utilization
    compute_resources: Dict[str, Any] = field(default_factory=dict)
    memory_usage: Dict[str, float] = field(default_factory=dict)
    gpu_utilization: List[float] = field(default_factory=list)
    training_time_hours: Optional[float] = None
    
    # Data and tokenization
    total_tokens_processed: Optional[int] = None
    effective_batch_size: Optional[int] = None
    data_loading_config: Dict[str, Any] = field(default_factory=dict)
    tokenization_config: Dict[str, Any] = field(default_factory=dict)
    
    # Distributed training configuration
    distributed_config: Dict[str, Any] = field(default_factory=dict)
    num_gpus: Optional[int] = None
    num_nodes: Optional[int] = None
    parallel_strategy: Optional[str] = None  # 'data_parallel', 'model_parallel', 'pipeline_parallel'
    
    # Environment and reproducibility
    random_seeds: Dict[str, int] = field(default_factory=dict)
    environment_info: Dict[str, str] = field(default_factory=dict)
    framework_versions: Dict[str, str] = field(default_factory=dict)
    hardware_info: Dict[str, Any] = field(default_factory=dict)
    
    # Safety and alignment training (for RLHF, constitutional AI, etc.)
    safety_training_config: Optional[Dict[str, Any]] = None
    alignment_objectives: List[str] = field(default_factory=list)
    reward_model_ref: Optional[str] = None
    human_feedback_data: Optional[Dict[str, Any]] = None
    
    # Early stopping and optimization
    early_stopping_config: Dict[str, Any] = field(default_factory=dict)
    optimizer_config: Dict[str, Any] = field(default_factory=dict)
    scheduler_config: Dict[str, Any] = field(default_factory=dict)
    
    # Final results and evaluation
    final_evaluation: Dict[str, float] = field(default_factory=dict)
    convergence_metrics: Dict[str, Any] = field(default_factory=dict)
    training_stability: Dict[str, float] = field(default_factory=dict)
    
    # Audit and verification
    training_start: Optional[str] = None   # Training start timestamp
    training_end: Optional[str] = None     # Training completion timestamp
    merkle_root: Optional[str] = None      # Training verification root
    signature: Optional[str] = None        # Digital signature
    
    # Policy and governance
    policy: Optional[Any] = None           # LCM Policy reference
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')


@dataclass
class LLMBatchInferenceReceipt:
    """
    Receipt for batch LLM inference operations.
    Used for high-throughput batch processing scenarios.
    """
    
    # Core identification
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    deployment_anchor_ref: str = ""
    
    # Batch configuration
    batch_size: int = 0
    total_requests: int = 0
    processed_requests: int = 0
    failed_requests: int = 0
    
    # Aggregate metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    average_latency_ms: Optional[float] = None
    total_compute_units: Optional[float] = None
    
    # Batch-level cryptographic commitments
    batch_input_hash: str = ""            # Hash of all inputs
    batch_output_hash: str = ""           # Hash of all outputs
    individual_hashes: List[str] = field(default_factory=list)
    
    # Quality metrics
    average_confidence: Optional[float] = None
    safety_violations: int = 0
    content_flag_summary: Dict[str, int] = field(default_factory=dict)
    
    # Processing metadata
    processing_start: Optional[str] = None
    processing_end: Optional[str] = None
    processing_duration_ms: Optional[float] = None
    
    # Individual receipt references
    individual_receipts: List[str] = field(default_factory=list)
    
    # Verification and compliance
    committed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    signature: Optional[str] = None
    policy: Optional[Any] = None