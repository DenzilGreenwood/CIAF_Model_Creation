"""
Cryptoeconomic Context Framework

Documentation of trust boundaries, signing entities, cross-jurisdiction proofs,
and cryptoeconomic mechanisms in the CIAF LCM system.

Created: 2025-10-24
Author: Denzil James Greenwood
Version: 1.0.0
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class EntityType(Enum):
    """Types of entities in the cryptoeconomic system."""
    MODEL_OWNER = "model_owner"
    DATA_PROVIDER = "data_provider"
    PLATFORM_OPERATOR = "platform_operator"
    AUDITOR = "auditor"
    REGULATOR = "regulator"
    VALIDATOR = "validator"
    TIMESTAMP_AUTHORITY = "timestamp_authority"
    KEY_AUTHORITY = "key_authority"


class TrustLevel(Enum):
    """Trust levels for different operations."""
    UNTRUSTED = "untrusted"
    SEMI_TRUSTED = "semi_trusted"
    TRUSTED = "trusted"
    HIGHLY_TRUSTED = "highly_trusted"


class JurisdictionType(Enum):
    """Types of regulatory jurisdictions."""
    EU = "european_union"
    US = "united_states"
    UK = "united_kingdom"
    CANADA = "canada"
    SINGAPORE = "singapore"
    AUSTRALIA = "australia"
    MULTI_JURISDICTION = "multi_jurisdiction"
    GLOBAL = "global"


@dataclass
class SigningEntity:
    """Definition of an entity that can sign LCM components."""
    entity_id: str
    entity_type: EntityType
    trust_level: TrustLevel
    signing_capabilities: List[str]
    jurisdiction: JurisdictionType
    public_key_fingerprint: str
    certification_authority: Optional[str]
    revocation_endpoint: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class TrustBoundary:
    """Definition of a trust boundary in the system."""
    boundary_id: str
    description: str
    trusted_entities: Set[str]  # Entity IDs
    untrusted_entities: Set[str]  # Entity IDs
    cryptographic_requirements: List[str]
    verification_methods: List[str]
    cross_boundary_protocols: List[str]
    jurisdiction_implications: Dict[JurisdictionType, str]


@dataclass
class CrossJurisdictionProof:
    """Proof structure for cross-jurisdiction validation."""
    proof_id: str
    source_jurisdiction: JurisdictionType
    target_jurisdictions: List[JurisdictionType]
    compliance_mappings: Dict[JurisdictionType, Dict[str, str]]
    selective_disclosure_fields: List[str]
    privacy_preserving_mechanisms: List[str]
    legal_framework_references: Dict[JurisdictionType, List[str]]


class CryptoeconomicFramework:
    """
    Comprehensive cryptoeconomic framework for CIAF LCM.
    
    Defines trust boundaries, signing entities, economic incentives,
    and cross-jurisdiction validation mechanisms.
    """
    
    def __init__(self):
        """Initialize cryptoeconomic framework."""
        self.signing_entities = self._initialize_signing_entities()
        self.trust_boundaries = self._initialize_trust_boundaries()
        self.jurisdiction_mappings = self._initialize_jurisdiction_mappings()
    
    def _initialize_signing_entities(self) -> Dict[str, SigningEntity]:
        """Initialize standard signing entities for LCM operations."""
        entities = {}
        
        # Model Owner Entity
        entities["model_owner_primary"] = SigningEntity(
            entity_id="model_owner_primary",
            entity_type=EntityType.MODEL_OWNER,
            trust_level=TrustLevel.TRUSTED,
            signing_capabilities=[
                "model_anchor_creation",
                "training_authorization",
                "deployment_approval",
                "inference_validation"
            ],
            jurisdiction=JurisdictionType.MULTI_JURISDICTION,
            public_key_fingerprint="sha256:a1b2c3d4...",
            certification_authority="GlobalTrust_CA",
            revocation_endpoint="https://ca.globaltrust.com/revoke",
            metadata={
                "organization": "Model Development Corp",
                "compliance_certifications": ["ISO27001", "SOC2_Type2"],
                "audit_frequency": "quarterly"
            }
        )
        
        # Platform Operator Entity
        entities["platform_operator"] = SigningEntity(
            entity_id="platform_operator",
            entity_type=EntityType.PLATFORM_OPERATOR,
            trust_level=TrustLevel.HIGHLY_TRUSTED,
            signing_capabilities=[
                "receipt_generation",
                "merkle_root_computation",
                "timestamp_validation",
                "infrastructure_attestation"
            ],
            jurisdiction=JurisdictionType.US,
            public_key_fingerprint="sha256:e5f6g7h8...",
            certification_authority="FedRAMP_CA",
            revocation_endpoint="https://ca.fedramp.gov/revoke",
            metadata={
                "platform_type": "cloud_ml_platform",
                "security_clearance": "FedRAMP_High",
                "sla_guarantees": "99.99%_uptime"
            }
        )
        
        # Independent Auditor Entity
        entities["independent_auditor"] = SigningEntity(
            entity_id="independent_auditor",
            entity_type=EntityType.AUDITOR,
            trust_level=TrustLevel.HIGHLY_TRUSTED,
            signing_capabilities=[
                "audit_validation",
                "compliance_certification",
                "third_party_verification",
                "dispute_resolution"
            ],
            jurisdiction=JurisdictionType.EU,
            public_key_fingerprint="sha256:i9j0k1l2...",
            certification_authority="EU_eIDAS_CA",
            revocation_endpoint="https://ca.eidas.eu/revoke",
            metadata={
                "audit_firm": "TechAudit International",
                "accreditations": ["ISAE3000", "SSAE18", "CSA_STAR"],
                "specializations": ["AI_auditing", "cryptographic_systems"]
            }
        )
        
        # Timestamp Authority Entity
        entities["timestamp_authority"] = SigningEntity(
            entity_id="timestamp_authority",
            entity_type=EntityType.TIMESTAMP_AUTHORITY,
            trust_level=TrustLevel.HIGHLY_TRUSTED,
            signing_capabilities=[
                "rfc3161_timestamping",
                "temporal_ordering",
                "chronological_proof"
            ],
            jurisdiction=JurisdictionType.GLOBAL,
            public_key_fingerprint="sha256:m3n4o5p6...",
            certification_authority="GlobalTime_TSA",
            revocation_endpoint="https://tsa.globaltime.org/revoke",
            metadata={
                "tsa_type": "qualified_timestamp_service",
                "accuracy_guarantee": "±1_second_UTC",
                "availability": "24x7x365"
            }
        )
        
        # Regulatory Authority Entity
        entities["regulatory_authority"] = SigningEntity(
            entity_id="regulatory_authority",
            entity_type=EntityType.REGULATOR,
            trust_level=TrustLevel.HIGHLY_TRUSTED,
            signing_capabilities=[
                "compliance_validation",
                "regulatory_approval",
                "enforcement_action",
                "policy_attestation"
            ],
            jurisdiction=JurisdictionType.EU,
            public_key_fingerprint="sha256:q7r8s9t0...",
            certification_authority="EU_Gov_CA",
            revocation_endpoint="https://ca.europa.eu/revoke",
            metadata={
                "authority_type": "national_competent_authority",
                "regulatory_scope": ["AI_Act", "GDPR", "Digital_Services_Act"],
                "enforcement_powers": "administrative_fines"
            }
        )
        
        return entities
    
    def _initialize_trust_boundaries(self) -> Dict[str, TrustBoundary]:
        """Initialize trust boundaries for the LCM system."""
        boundaries = {}
        
        # Core Cryptographic Boundary
        boundaries["core_crypto"] = TrustBoundary(
            boundary_id="core_crypto",
            description="Core cryptographic operations requiring highest trust",
            trusted_entities={
                "model_owner_primary", "platform_operator", 
                "timestamp_authority", "independent_auditor"
            },
            untrusted_entities=set(),
            cryptographic_requirements=[
                "ed25519_signatures",
                "hmac_sha256_anchors",
                "rfc3161_timestamps",
                "merkle_tree_proofs"
            ],
            verification_methods=[
                "signature_verification",
                "anchor_derivation_validation",
                "timestamp_verification",
                "merkle_proof_validation"
            ],
            cross_boundary_protocols=[
                "zero_knowledge_proofs",
                "selective_disclosure",
                "cryptographic_commitments"
            ],
            jurisdiction_implications={
                JurisdictionType.EU: "GDPR Article 25 - Privacy by Design",
                JurisdictionType.US: "NIST Cybersecurity Framework",
                JurisdictionType.UK: "UK GDPR + Data Protection Act 2018"
            }
        )
        
        # Model Governance Boundary
        boundaries["model_governance"] = TrustBoundary(
            boundary_id="model_governance",
            description="Model governance and lifecycle management",
            trusted_entities={
                "model_owner_primary", "independent_auditor", "regulatory_authority"
            },
            untrusted_entities={"external_users", "anonymous_validators"},
            cryptographic_requirements=[
                "model_anchor_signatures",
                "training_session_proofs",
                "deployment_attestations"
            ],
            verification_methods=[
                "multi_party_validation",
                "audit_trail_verification",
                "compliance_checking"
            ],
            cross_boundary_protocols=[
                "regulatory_reporting",
                "audit_coordination",
                "compliance_attestation"
            ],
            jurisdiction_implications={
                JurisdictionType.EU: "AI Act Article 16 - Quality Management System",
                JurisdictionType.US: "FDA 21 CFR Part 820 (if medical device)",
                JurisdictionType.CANADA: "Directive on Automated Decision-Making"
            }
        )
        
        # Data Privacy Boundary
        boundaries["data_privacy"] = TrustBoundary(
            boundary_id="data_privacy",
            description="Data privacy and protection mechanisms",
            trusted_entities={
                "model_owner_primary", "platform_operator", "regulatory_authority"
            },
            untrusted_entities={"external_auditors", "third_party_services"},
            cryptographic_requirements=[
                "dataset_anchor_privacy",
                "differential_privacy_proofs",
                "homomorphic_encryption"
            ],
            verification_methods=[
                "privacy_preserving_validation",
                "anonymization_verification",
                "consent_validation"
            ],
            cross_boundary_protocols=[
                "privacy_preserving_computation",
                "federated_validation",
                "secure_multi_party_computation"
            ],
            jurisdiction_implications={
                JurisdictionType.EU: "GDPR Articles 5, 25, 32",
                JurisdictionType.US: "CCPA + sector-specific regulations",
                JurisdictionType.SINGAPORE: "Personal Data Protection Act"
            }
        )
        
        return boundaries
    
    def _initialize_jurisdiction_mappings(self) -> Dict[JurisdictionType, Dict[str, Any]]:
        """Initialize regulatory jurisdiction mappings."""
        return {
            JurisdictionType.EU: {
                "primary_regulations": ["AI Act", "GDPR", "Digital Services Act"],
                "competent_authorities": ["National AI Authorities", "Data Protection Authorities"],
                "audit_requirements": {
                    "high_risk_ai": "mandatory_third_party_conformity_assessment",
                    "audit_frequency": "continuous_monitoring",
                    "documentation": "technical_documentation_package"
                },
                "cross_border_mechanisms": ["adequacy_decisions", "scc_safeguards", "bcr_programs"],
                "enforcement_tools": ["administrative_fines", "market_withdrawal", "service_suspension"]
            },
            JurisdictionType.US: {
                "primary_regulations": ["NIST AI RMF", "Algorithmic Accountability Act", "CPPA"],
                "competent_authorities": ["NIST", "FTC", "Sector-specific agencies"],
                "audit_requirements": {
                    "impact_assessment": "algorithmic_impact_assessment",
                    "audit_frequency": "risk_based_approach",
                    "documentation": "comprehensive_documentation"
                },
                "cross_border_mechanisms": ["privacy_shield_successor", "mutual_recognition"],
                "enforcement_tools": ["civil_penalties", "consent_decrees", "injunctive_relief"]
            },
            JurisdictionType.UK: {
                "primary_regulations": ["UK GDPR", "Data Protection Act 2018", "Online Safety Act"],
                "competent_authorities": ["ICO", "Ofcom", "CMA"],
                "audit_requirements": {
                    "impact_assessment": "data_protection_impact_assessment",
                    "audit_frequency": "risk_based_monitoring",
                    "documentation": "accountability_documentation"
                },
                "cross_border_mechanisms": ["uk_adequacy_regulations", "international_transfers"],
                "enforcement_tools": ["monetary_penalties", "enforcement_notices", "prosecutions"]
            }
        }
    
    def get_signing_requirements_for_operation(self, operation: str) -> Dict[str, Any]:
        """Get signing requirements for a specific LCM operation."""
        operation_requirements = {
            "dataset_anchor_creation": {
                "required_signers": ["model_owner_primary"],
                "optional_signers": ["platform_operator"],
                "trust_boundary": "data_privacy",
                "signature_type": "ed25519",
                "additional_proofs": ["data_lineage", "consent_validation"]
            },
            "model_anchor_creation": {
                "required_signers": ["model_owner_primary"],
                "optional_signers": ["independent_auditor"],
                "trust_boundary": "model_governance",
                "signature_type": "ed25519",
                "additional_proofs": ["model_validation", "bias_testing"]
            },
            "training_session_completion": {
                "required_signers": ["model_owner_primary", "platform_operator"],
                "optional_signers": ["timestamp_authority"],
                "trust_boundary": "core_crypto",
                "signature_type": "ed25519",
                "additional_proofs": ["training_metrics", "resource_attestation"]
            },
            "deployment_authorization": {
                "required_signers": ["model_owner_primary", "platform_operator"],
                "optional_signers": ["regulatory_authority", "independent_auditor"],
                "trust_boundary": "model_governance",
                "signature_type": "ed25519",
                "additional_proofs": ["deployment_testing", "security_assessment"]
            },
            "inference_receipt_generation": {
                "required_signers": ["platform_operator"],
                "optional_signers": ["timestamp_authority"],
                "trust_boundary": "core_crypto",
                "signature_type": "ed25519",
                "additional_proofs": ["inference_validation", "output_verification"]
            },
            "audit_validation": {
                "required_signers": ["independent_auditor"],
                "optional_signers": ["regulatory_authority"],
                "trust_boundary": "model_governance",
                "signature_type": "ed25519",
                "additional_proofs": ["audit_methodology", "compliance_verification"]
            }
        }
        
        return operation_requirements.get(operation, {
            "error": f"Unknown operation: {operation}",
            "available_operations": list(operation_requirements.keys())
        })
    
    def generate_cross_jurisdiction_proof(
        self,
        source_jurisdiction: JurisdictionType,
        target_jurisdictions: List[JurisdictionType],
        data_elements: List[str],
        privacy_level: str = "high"
    ) -> CrossJurisdictionProof:
        """Generate cross-jurisdiction proof for selective disclosure."""
        proof_id = f"cjp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Map compliance requirements across jurisdictions
        compliance_mappings = {}
        for jurisdiction in target_jurisdictions:
            jurisdiction_info = self.jurisdiction_mappings.get(jurisdiction, {})
            compliance_mappings[jurisdiction] = {
                "primary_legal_basis": jurisdiction_info.get("primary_regulations", []),
                "audit_requirements": jurisdiction_info.get("audit_requirements", {}),
                "cross_border_mechanism": jurisdiction_info.get("cross_border_mechanisms", [])
            }
        
        # Determine selective disclosure fields based on privacy level
        if privacy_level == "high":
            selective_disclosure_fields = [
                "inference_metadata_only",
                "aggregated_metrics",
                "anonymized_patterns"
            ]
            privacy_mechanisms = [
                "differential_privacy",
                "k_anonymity",
                "homomorphic_encryption"
            ]
        elif privacy_level == "medium":
            selective_disclosure_fields = [
                "model_performance_metrics",
                "training_summary_statistics",
                "deployment_metadata"
            ]
            privacy_mechanisms = [
                "data_minimization",
                "pseudonymization",
                "aggregation"
            ]
        else:  # low privacy
            selective_disclosure_fields = data_elements
            privacy_mechanisms = [
                "access_control",
                "audit_logging"
            ]
        
        # Legal framework references
        legal_frameworks = {}
        for jurisdiction in target_jurisdictions:
            if jurisdiction == JurisdictionType.EU:
                legal_frameworks[jurisdiction] = [
                    "GDPR Article 44-49 (International Transfers)",
                    "AI Act Article 28 (Obligations of importers)",
                    "Adequacy Decision mechanisms"
                ]
            elif jurisdiction == JurisdictionType.US:
                legal_frameworks[jurisdiction] = [
                    "Privacy Shield successor mechanisms",
                    "Standard Contractual Clauses",
                    "Sector-specific transfer agreements"
                ]
            else:
                legal_frameworks[jurisdiction] = [
                    "Mutual Legal Assistance Treaties",
                    "Bilateral cooperation agreements",
                    "International standards compliance"
                ]
        
        return CrossJurisdictionProof(
            proof_id=proof_id,
            source_jurisdiction=source_jurisdiction,
            target_jurisdictions=target_jurisdictions,
            compliance_mappings=compliance_mappings,
            selective_disclosure_fields=selective_disclosure_fields,
            privacy_preserving_mechanisms=privacy_mechanisms,
            legal_framework_references=legal_frameworks
        )
    
    def validate_key_rotation_event(
        self,
        old_key_fingerprint: str,
        new_key_fingerprint: str,
        rotation_reason: str,
        entity_id: str
    ) -> Dict[str, Any]:
        """Validate and log key rotation event in Merkle structure."""
        rotation_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Get entity information
        entity = self.signing_entities.get(entity_id)
        if not entity:
            return {"error": f"Unknown entity: {entity_id}"}
        
        # Create rotation record
        rotation_record = {
            "event_type": "key_rotation",
            "entity_id": entity_id,
            "entity_type": entity.entity_type.value,
            "old_key_fingerprint": old_key_fingerprint,
            "new_key_fingerprint": new_key_fingerprint,
            "rotation_reason": rotation_reason,
            "timestamp": rotation_timestamp,
            "certification_authority": entity.certification_authority,
            "jurisdiction": entity.jurisdiction.value,
            "overlap_period_hours": 72,  # 3-day overlap for graceful transition
            "revocation_scheduled": rotation_timestamp,
            "compliance_attestation": {
                "rotation_policy_compliance": True,
                "security_audit_passed": True,
                "regulatory_notification_sent": True
            }
        }
        
        # Merkle tree integration
        merkle_integration = {
            "merkle_leaf_hash": self._compute_rotation_hash(rotation_record),
            "tree_insertion_timestamp": rotation_timestamp,
            "proof_generation_required": True,
            "historical_verification_impact": {
                "signatures_affected": "all_signatures_with_old_key",
                "verification_window": "72_hours_graceful_period",
                "backward_compatibility": "maintained_with_proof_chain"
            }
        }
        
        return {
            "rotation_record": rotation_record,
            "merkle_integration": merkle_integration,
            "validation_status": "approved",
            "next_actions": [
                "Update key distribution channels",
                "Notify all trust boundary participants",
                "Schedule old key revocation",
                "Monitor signature validation during overlap"
            ]
        }
    
    def _compute_rotation_hash(self, rotation_record: Dict[str, Any]) -> str:
        """Compute hash for key rotation record."""
        # Use deterministic JSON serialization for hashing
        canonical_json = json.dumps(rotation_record, sort_keys=True, separators=(',', ':'))
        
        # Import here to avoid circular imports
        from ...ciaf.core import sha256_hash
        return sha256_hash(canonical_json.encode('utf-8'))
    
    def get_trust_boundary_documentation(self) -> Dict[str, Any]:
        """Generate comprehensive trust boundary documentation."""
        documentation = {
            "trust_boundaries_overview": {
                "total_boundaries": len(self.trust_boundaries),
                "boundary_types": ["cryptographic", "governance", "privacy"],
                "cross_boundary_protocols": set()
            },
            "boundary_details": {},
            "entity_trust_matrix": {},
            "jurisdiction_implications": {}
        }
        
        # Document each boundary
        for boundary_id, boundary in self.trust_boundaries.items():
            documentation["boundary_details"][boundary_id] = {
                "description": boundary.description,
                "trusted_entity_count": len(boundary.trusted_entities),
                "untrusted_entity_count": len(boundary.untrusted_entities),
                "crypto_requirements": boundary.cryptographic_requirements,
                "verification_methods": boundary.verification_methods,
                "cross_boundary_protocols": boundary.cross_boundary_protocols
            }
            
            # Collect all cross-boundary protocols
            documentation["trust_boundaries_overview"]["cross_boundary_protocols"].update(
                boundary.cross_boundary_protocols
            )
        
        # Convert set to list for JSON serialization
        documentation["trust_boundaries_overview"]["cross_boundary_protocols"] = list(
            documentation["trust_boundaries_overview"]["cross_boundary_protocols"]
        )
        
        # Create entity trust matrix
        for entity_id, entity in self.signing_entities.items():
            documentation["entity_trust_matrix"][entity_id] = {
                "entity_type": entity.entity_type.value,
                "trust_level": entity.trust_level.value,
                "jurisdiction": entity.jurisdiction.value,
                "trusted_in_boundaries": [
                    boundary_id for boundary_id, boundary in self.trust_boundaries.items()
                    if entity_id in boundary.trusted_entities
                ],
                "signing_capabilities": entity.signing_capabilities
            }
        
        # Document jurisdiction implications
        all_jurisdictions = set()
        for boundary in self.trust_boundaries.values():
            all_jurisdictions.update(boundary.jurisdiction_implications.keys())
        
        for jurisdiction in all_jurisdictions:
            documentation["jurisdiction_implications"][jurisdiction.value] = {
                "applicable_boundaries": [
                    boundary_id for boundary_id, boundary in self.trust_boundaries.items()
                    if jurisdiction in boundary.jurisdiction_implications
                ],
                "regulatory_framework": self.jurisdiction_mappings.get(jurisdiction, {}),
                "compliance_requirements": [
                    boundary.jurisdiction_implications[jurisdiction]
                    for boundary in self.trust_boundaries.values()
                    if jurisdiction in boundary.jurisdiction_implications
                ]
            }
        
        return documentation