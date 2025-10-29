"""
LLM Anchor Data Structures

Implements anchor data structures specifically for Large Language Models
following the CIAF Data Structures Technical Specification.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class LLMDatasetAnchor:
    """
    Dataset anchor for LLM training data with cryptographic binding.
    Follows CIAF Dataset Anchor Framework from technical specification.
    """
    
    # Core identification
    anchor_id: str                         # Derived anchor identifier
    dataset_id: str                        # Original dataset identifier
    dataset_hash: str                      # SHA-256 of dataset content
    
    # LLM-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Dataset characteristics for LLMs
    token_count: Optional[int] = None      # Total token count
    sequence_length: Optional[int] = None  # Maximum sequence length
    vocabulary_size: Optional[int] = None  # Vocabulary size
    language: Optional[str] = None         # Primary language
    domain: Optional[str] = None           # Domain (e.g., 'general', 'medical', 'legal')
    
    # Provenance and quality
    source_info: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    preprocessing_steps: List[str] = field(default_factory=list)
    
    # Privacy and compliance
    privacy_classification: str = "unclassified"
    contains_pii: bool = False
    data_retention_policy: Optional[str] = None
    
    # Cryptographic verification
    merkle_root: Optional[str] = None      # Merkle root for batch verification
    signature: Optional[str] = None        # Digital signature for authenticity
    
    # Policy and governance
    policy: Optional[Any] = None           # LCM Policy reference
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')


@dataclass
class LLMModelAnchor:
    """
    Model anchor for LLM architecture and trained weights.
    Follows CIAF Model Anchor Framework from technical specification.
    """
    
    # Core identification
    anchor_id: str                         # Derived anchor identifier
    model_id: str                          # Model identifier
    model_hash: str                        # Hash of model parameters
    
    # LLM architecture details
    architecture: Dict[str, Any] = field(default_factory=dict)
    model_type: str = "transformer"        # Model architecture type
    parameter_count: Optional[int] = None  # Total parameter count
    layer_count: Optional[int] = None      # Number of layers
    attention_heads: Optional[int] = None  # Number of attention heads
    embedding_dimension: Optional[int] = None  # Embedding dimension
    
    # Training configuration
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    framework_info: Dict[str, str] = field(default_factory=dict)
    
    # Training provenance
    dataset_anchor_ref: Optional[str] = None  # Reference to training dataset anchor
    training_session_ref: Optional[str] = None  # Reference to training session
    base_model_ref: Optional[str] = None   # Reference to base model (for fine-tuning)
    
    # Performance and capabilities
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    benchmark_results: Dict[str, Any] = field(default_factory=dict)
    capability_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Safety and alignment
    safety_evaluation: Dict[str, Any] = field(default_factory=dict)
    bias_assessment: Dict[str, Any] = field(default_factory=dict)
    alignment_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Cryptographic verification
    merkle_root: Optional[str] = None      # Merkle root for verification
    signature: Optional[str] = None        # Digital signature
    
    # Policy and governance
    policy: Optional[Any] = None           # LCM Policy reference
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')


@dataclass
class LLMDeploymentAnchor:
    """
    Deployment anchor for LLM production deployment configuration.
    Follows CIAF Deployment Anchor Framework from technical specification.
    """
    
    # Core identification
    anchor_id: str                         # Deployment anchor identifier
    deployment_id: str                     # Deployment instance identifier
    
    # Model binding
    model_anchor_ref: str                  # Reference to deployed model
    predeployment_anchor_ref: Optional[str] = None  # Reference to pre-deployment validation
    
    # LLM-specific deployment configuration
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    serving_configuration: Dict[str, Any] = field(default_factory=dict)
    inference_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Infrastructure and scaling
    environment_info: Dict[str, Any] = field(default_factory=dict)
    scaling_config: Dict[str, Any] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    
    # LLM-specific operational parameters
    max_tokens: Optional[int] = None       # Maximum tokens per request
    temperature: Optional[float] = None    # Sampling temperature
    top_p: Optional[float] = None          # Top-p sampling parameter
    top_k: Optional[int] = None           # Top-k sampling parameter
    repetition_penalty: Optional[float] = None  # Repetition penalty
    
    # Monitoring and observability
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    logging_level: str = "INFO"
    metrics_collection: bool = True
    
    # Performance and SLA
    performance_targets: Dict[str, float] = field(default_factory=dict)
    latency_requirements: Dict[str, float] = field(default_factory=dict)
    throughput_targets: Dict[str, float] = field(default_factory=dict)
    
    # Security and access control
    access_controls: List[str] = field(default_factory=list)
    api_security: Dict[str, Any] = field(default_factory=dict)
    content_filtering: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance and governance
    compliance_requirements: List[str] = field(default_factory=list)
    audit_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Verification and validation
    deployment_tests: List[Dict[str, Any]] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    # Cryptographic verification
    deployment_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    merkle_root: Optional[str] = None      # Verification Merkle root
    signature: Optional[str] = None        # Deployment signature
    
    # Policy and governance
    policy: Optional[Any] = None           # LCM Policy reference
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')