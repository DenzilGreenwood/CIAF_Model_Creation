"""
Consent Migration Utilities for CIAF

This module provides utilities for migrating existing consent data structures
to the new standardized consent management system with backward compatibility.

Created: 2025-10-21
Author: Denzil James Greenwood
Version: 1.0.0
"""

import warnings
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from .consent import (
    ConsentManager, ConsentRecord, ConsentMigrator, 
    validate_consent_status, migrate_consent_metadata,
    get_consent_manager
)
from ..core.enums import ConsentStatus, ConsentType, ConsentScope


class ConsentMigrationEngine:
    """Engine for batch migration of consent data across CIAF components."""
    
    def __init__(self, consent_manager: Optional[ConsentManager] = None):
        self.consent_manager = consent_manager or get_consent_manager()
        self.migration_log: List[Dict[str, Any]] = []
    
    def migrate_gdpr_wrapper_data(
        self, 
        wrapper_data: Dict[str, Any],
        data_subject_id: str
    ) -> Dict[str, Any]:
        """Migrate GDPR wrapper consent data to standardized format."""
        migrated_data = wrapper_data.copy()
        migration_count = 0
        
        # Check for metadata consent_status
        if "metadata" in migrated_data and isinstance(migrated_data["metadata"], dict):
            metadata = migrated_data["metadata"]
            
            if "consent_status" in metadata:
                original_value = metadata["consent_status"]
                migrated_status = validate_consent_status(original_value)
                
                # Update to standardized value
                metadata["consent_status"] = migrated_status.value
                metadata["consent_status_migrated"] = True
                metadata["consent_status_original"] = str(original_value)
                
                # Create consent record in manager
                self.consent_manager.record_consent(
                    data_subject_id=data_subject_id,
                    consent_type=ConsentType.EXPLICIT,
                    consent_scope=ConsentScope.DATA_PROCESSING,
                    purpose="GDPR-compliant AI model processing",
                    metadata={"source": "gdpr_wrapper_migration"}
                )
                
                migration_count += 1
                self._log_migration("gdpr_wrapper", "consent_status", original_value, migrated_status.value)
        
        # Handle provenance capsule consent data
        if "provenance_capsules" in migrated_data:
            capsules = migrated_data["provenance_capsules"]
            if isinstance(capsules, list):
                for capsule in capsules:
                    if isinstance(capsule, dict) and "metadata" in capsule:
                        capsule_metadata = capsule["metadata"]
                        if "consent_status" in capsule_metadata:
                            original_value = capsule_metadata["consent_status"]
                            migrated_status = validate_consent_status(original_value)
                            capsule_metadata["consent_status"] = migrated_status.value
                            migration_count += 1
        
        if migration_count > 0:
            print(f"✅ Migrated {migration_count} consent fields in GDPR wrapper data")
        
        return migrated_data
    
    def migrate_education_consent_data(
        self,
        education_data: Dict[str, Any],
        system_id: str
    ) -> Dict[str, Any]:
        """Migrate education module consent data (boolean to enum)."""
        migrated_data = education_data.copy()
        migration_count = 0
        
        # Migrate parental consent status
        if "parental_consent_status" in migrated_data:
            original_dict = migrated_data["parental_consent_status"]
            if isinstance(original_dict, dict):
                migrated_dict = {}
                for student_id, consent_bool in original_dict.items():
                    migrated_status = ConsentMigrator.migrate_boolean_value(consent_bool)
                    migrated_dict[student_id] = migrated_status.value
                    
                    # Create individual consent records
                    self.consent_manager.record_consent(
                        data_subject_id=student_id,
                        consent_type=ConsentType.PARENTAL,
                        consent_scope=ConsentScope.DATA_PROCESSING,
                        purpose="Educational AI system data processing",
                        metadata={"system_id": system_id, "source": "education_migration"}
                    )
                    
                    migration_count += 1
                
                migrated_data["parental_consent_status"] = migrated_dict
                migrated_data["parental_consent_migrated"] = True
                self._log_migration("education", "parental_consent_status", str(original_dict), str(migrated_dict))
        
        # Migrate student consent status
        if "student_consent_status" in migrated_data:
            original_dict = migrated_data["student_consent_status"]
            if isinstance(original_dict, dict):
                migrated_dict = {}
                for student_id, consent_bool in original_dict.items():
                    migrated_status = ConsentMigrator.migrate_boolean_value(consent_bool)
                    migrated_dict[student_id] = migrated_status.value
                    
                    # Create individual consent records
                    self.consent_manager.record_consent(
                        data_subject_id=student_id,
                        consent_type=ConsentType.STUDENT,
                        consent_scope=ConsentScope.DATA_PROCESSING,
                        purpose="Educational AI system data processing",
                        metadata={"system_id": system_id, "source": "education_migration"}
                    )
                    
                    migration_count += 1
                
                migrated_data["student_consent_status"] = migrated_dict
                migrated_data["student_consent_migrated"] = True
                self._log_migration("education", "student_consent_status", str(original_dict), str(migrated_dict))
        
        if migration_count > 0:
            print(f"✅ Migrated {migration_count} consent records in education data")
        
        return migrated_data
    
    def migrate_telecommunications_consent_data(
        self,
        telecom_data: Dict[str, Any],
        customer_id: str
    ) -> Dict[str, Any]:
        """Migrate telecommunications consent data (dynamic keys to records)."""
        migrated_data = telecom_data.copy()
        migration_count = 0
        
        # Look for consent_status patterns in telecom data
        consent_fields = [
            "customer_consent_status", "user_consent_status", 
            "consent_compliance", "consent_status"
        ]
        
        for field in consent_fields:
            if field in migrated_data:
                original_value = migrated_data[field]
                
                if isinstance(original_value, dict):
                    # Handle dynamic consent structures
                    migrated_dict = {}
                    for key, value in original_value.items():
                        migrated_status = validate_consent_status(value)
                        migrated_dict[key] = migrated_status.value
                        
                        # Determine scope from key
                        scope = self._infer_telecom_scope(key)
                        
                        # Create consent record
                        self.consent_manager.record_consent(
                            data_subject_id=customer_id,
                            consent_type=ConsentType.OPT_IN,
                            consent_scope=scope,
                            purpose=f"Telecommunications service: {key}",
                            metadata={"field": field, "original_key": key, "source": "telecom_migration"}
                        )
                        
                        migration_count += 1
                    
                    migrated_data[field] = migrated_dict
                else:
                    # Handle single consent value
                    migrated_status = validate_consent_status(original_value)
                    migrated_data[field] = migrated_status.value
                    migration_count += 1
                
                migrated_data[f"{field}_migrated"] = True
                self._log_migration("telecommunications", field, str(original_value), str(migrated_data[field]))
        
        if migration_count > 0:
            print(f"✅ Migrated {migration_count} consent fields in telecommunications data")
        
        return migrated_data
    
    def migrate_industry_implementation(
        self,
        industry_data: Dict[str, Any],
        industry_name: str,
        entity_id: str
    ) -> Dict[str, Any]:
        """Generic migration for industry implementation consent data."""
        migrated_data = industry_data.copy()
        
        # Common consent field patterns
        consent_field_patterns = [
            "consent_status", "consent_compliance", "customer_consent",
            "participant_consent", "employee_consent", "user_consent_status",
            "informed_consent_status", "biometric_consent"
        ]
        
        migration_count = 0
        
        for field_pattern in consent_field_patterns:
            # Look for exact matches and variations
            matching_fields = [
                key for key in migrated_data.keys()
                if field_pattern in key.lower()
            ]
            
            for field in matching_fields:
                original_value = migrated_data[field]
                
                if original_value is not None:
                    migrated_status = validate_consent_status(original_value)
                    migrated_data[field] = migrated_status.value
                    migrated_data[f"{field}_migrated"] = True
                    
                    # Create consent record
                    scope = self._infer_industry_scope(field, industry_name)
                    consent_type = self._infer_industry_type(field, industry_name)
                    
                    self.consent_manager.record_consent(
                        data_subject_id=entity_id,
                        consent_type=consent_type,
                        consent_scope=scope,
                        purpose=f"{industry_name} AI system processing",
                        metadata={"field": field, "industry": industry_name, "source": "industry_migration"}
                    )
                    
                    migration_count += 1
                    self._log_migration(industry_name, field, str(original_value), migrated_status.value)
        
        if migration_count > 0:
            print(f"✅ Migrated {migration_count} consent fields in {industry_name} implementation")
        
        return migrated_data
    
    def batch_migrate_metadata_collection(
        self,
        metadata_collection: List[Dict[str, Any]],
        collection_name: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """Batch migrate a collection of metadata dictionaries."""
        migrated_collection = []
        total_migrations = 0
        
        for i, metadata in enumerate(metadata_collection):
            migrated_metadata = migrate_consent_metadata(metadata)
            migrated_collection.append(migrated_metadata)
            
            # Count migrations
            migration_fields = [key for key in migrated_metadata.keys() if key.endswith("_migrated")]
            if migration_fields:
                total_migrations += len(migration_fields)
                self._log_migration(collection_name, f"item_{i}", "batch_metadata", f"{len(migration_fields)}_fields")
        
        if total_migrations > 0:
            print(f"✅ Batch migrated {total_migrations} consent fields across {len(metadata_collection)} items in {collection_name}")
        
        return migrated_collection
    
    def validate_migration_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all consent fields have been migrated properly."""
        validation_results = {
            "total_consent_fields": 0,
            "migrated_fields": 0,
            "unmigrated_fields": [],
            "invalid_values": [],
            "migration_complete": False
        }
        
        def _scan_dict(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if this is a consent field
                    if "consent" in key.lower():
                        validation_results["total_consent_fields"] += 1
                        
                        # Check if migrated
                        if f"{key}_migrated" in obj:
                            validation_results["migrated_fields"] += 1
                        else:
                            validation_results["unmigrated_fields"].append(current_path)
                        
                        # Validate value
                        try:
                            validate_consent_status(value)
                        except Exception as e:
                            validation_results["invalid_values"].append({
                                "field": current_path,
                                "value": str(value),
                                "error": str(e)
                            })
                    
                    # Recurse into nested structures
                    _scan_dict(value, current_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    _scan_dict(item, f"{path}[{i}]")
        
        _scan_dict(data)
        
        validation_results["migration_complete"] = (
            validation_results["total_consent_fields"] > 0 and
            len(validation_results["unmigrated_fields"]) == 0 and
            len(validation_results["invalid_values"]) == 0
        )
        
        return validation_results
    
    def _infer_telecom_scope(self, key: str) -> ConsentScope:
        """Infer consent scope for telecommunications keys."""
        key_lower = key.lower()
        
        if "marketing" in key_lower:
            return ConsentScope.MARKETING_COMMUNICATIONS
        elif "analytics" in key_lower or "tracking" in key_lower:
            return ConsentScope.ANALYTICS_TRACKING
        elif "sharing" in key_lower or "third_party" in key_lower:
            return ConsentScope.THIRD_PARTY_SHARING
        elif "personalization" in key_lower:
            return ConsentScope.PERSONALIZATION
        else:
            return ConsentScope.DATA_PROCESSING
    
    def _infer_industry_scope(self, field: str, industry: str) -> ConsentScope:
        """Infer consent scope based on field name and industry."""
        field_lower = field.lower()
        industry_lower = industry.lower()
        
        if "biometric" in field_lower:
            return ConsentScope.BIOMETRIC_COLLECTION
        elif "research" in field_lower or "research" in industry_lower:
            return ConsentScope.RESEARCH_PARTICIPATION
        elif "marketing" in field_lower:
            return ConsentScope.MARKETING_COMMUNICATIONS
        elif "analytics" in field_lower:
            return ConsentScope.ANALYTICS_TRACKING
        elif "sharing" in field_lower:
            return ConsentScope.DATA_SHARING
        else:
            return ConsentScope.DATA_PROCESSING
    
    def _infer_industry_type(self, field: str, industry: str) -> ConsentType:
        """Infer consent type based on field name and industry."""
        field_lower = field.lower()
        industry_lower = industry.lower()
        
        if "parental" in field_lower:
            return ConsentType.PARENTAL
        elif "student" in field_lower and "education" in industry_lower:
            return ConsentType.STUDENT
        elif "biometric" in field_lower:
            return ConsentType.BIOMETRIC
        elif "medical" in field_lower or "healthcare" in industry_lower:
            return ConsentType.MEDICAL
        elif "research" in field_lower:
            return ConsentType.RESEARCH
        else:
            return ConsentType.EXPLICIT
    
    def _log_migration(self, source: str, field: str, original: str, migrated: str):
        """Log migration details for audit trail."""
        self.migration_log.append({
            "timestamp": self.consent_manager._audit_trail[-1]["timestamp"] if self.consent_manager._audit_trail else None,
            "source": source,
            "field": field,
            "original_value": original,
            "migrated_value": migrated,
            "migration_engine": "ConsentMigrationEngine"
        })
    
    def export_migration_report(self) -> Dict[str, Any]:
        """Export detailed migration report."""
        return {
            "total_migrations": len(self.migration_log),
            "migration_log": self.migration_log,
            "consent_manager_summary": self.consent_manager.get_consent_summary(),
            "migration_engine_version": "1.0.0"
        }


def create_migration_deprecation_wrapper(original_func):
    """Decorator to add deprecation warnings for legacy consent functions."""
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"Function {original_func.__name__} uses legacy consent handling. "
            f"Please migrate to the new consent management system using ConsentManager.",
            DeprecationWarning,
            stacklevel=2
        )
        return original_func(*args, **kwargs)
    return wrapper


def migrate_wrapper_instance(wrapper_instance: Any) -> bool:
    """Migrate an existing wrapper instance to use new consent management."""
    migration_engine = ConsentMigrationEngine()
    migrated = False
    
    # Check if this is a GDPR wrapper
    if hasattr(wrapper_instance, '_gdpr_manifest'):
        manifest = wrapper_instance._gdpr_manifest
        if hasattr(manifest, 'to_dict'):
            manifest_data = manifest.to_dict()
            migrated_data = migration_engine.migrate_gdpr_wrapper_data(
                manifest_data, 
                getattr(wrapper_instance, 'model_name', 'unknown')
            )
            
            # Update the manifest with migrated data
            for key, value in migrated_data.items():
                if hasattr(manifest, key):
                    setattr(manifest, key, value)
            
            migrated = True
    
    # Check for training data with consent information
    if hasattr(wrapper_instance, 'training_snapshot'):
        snapshot = wrapper_instance.training_snapshot
        if hasattr(snapshot, 'metadata') and isinstance(snapshot.metadata, dict):
            migrated_metadata = migrate_consent_metadata(snapshot.metadata)
            snapshot.metadata = migrated_metadata
            migrated = True
    
    # Check for last receipt with consent information
    if hasattr(wrapper_instance, 'last_receipt'):
        receipt = wrapper_instance.last_receipt
        if hasattr(receipt, 'metadata') and isinstance(receipt.metadata, dict):
            migrated_metadata = migrate_consent_metadata(receipt.metadata)
            receipt.metadata = migrated_metadata
            migrated = True
    
    if migrated:
        # Add migration flag to wrapper
        wrapper_instance._consent_migrated = True
        wrapper_instance._consent_migration_timestamp = datetime.now(timezone.utc).isoformat()
        print(f"✅ Successfully migrated wrapper instance '{getattr(wrapper_instance, 'model_name', 'unknown')}' to new consent system")
    
    return migrated


__all__ = [
    "ConsentMigrationEngine",
    "create_migration_deprecation_wrapper",
    "migrate_wrapper_instance"
]