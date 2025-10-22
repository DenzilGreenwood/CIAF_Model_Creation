"""
Consent Management Module for CIAF

This module provides standardized consent management capabilities aligned with
GDPR, CCPA, and other privacy regulations. It includes consent tracking,
validation, and migration utilities for backward compatibility.

Created: 2025-10-21
Author: Denzil James Greenwood
Version: 1.0.0
"""

import hashlib
import json
import time
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from ..core.enums import ConsentStatus, ConsentType, ConsentScope


# Type aliases for backward compatibility
ConsentStatusValue = Union[ConsentStatus, str, bool]
LegacyConsentValue = Union[str, bool, Dict[str, Any]]


@dataclass
class ConsentRecord:
    """Standardized consent record structure."""
    
    consent_id: str
    data_subject_id: str
    consent_type: ConsentType
    consent_scope: ConsentScope
    status: ConsentStatus
    granted_timestamp: Optional[str] = None
    withdrawn_timestamp: Optional[str] = None
    expiry_timestamp: Optional[str] = None
    legal_basis: str = "consent"  # GDPR Article 6
    purpose: str = ""
    version: str = "1.0"
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Auto-set granted timestamp if not provided and status is granted
        if (not self.granted_timestamp and 
            self.status in [ConsentStatus.GRANTED, ConsentStatus.ACTIVE, ConsentStatus.VALID]):
            self.granted_timestamp = datetime.now(timezone.utc).isoformat()
    
    def is_valid(self) -> bool:
        """Check if consent is currently valid."""
        if self.status not in [ConsentStatus.GRANTED, ConsentStatus.ACTIVE, ConsentStatus.VALID]:
            return False
            
        if self.expiry_timestamp:
            try:
                expiry = datetime.fromisoformat(self.expiry_timestamp.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) > expiry:
                    return False
            except ValueError:
                # Invalid timestamp format
                return False
                
        return True
    
    def can_process_for_purpose(self, purpose: str) -> bool:
        """Check if consent allows processing for specific purpose."""
        return self.is_valid() and purpose.lower() in self.purpose.lower()
    
    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time until consent expires."""
        if not self.expiry_timestamp:
            return None
        
        try:
            expiry = datetime.fromisoformat(self.expiry_timestamp.replace('Z', '+00:00'))
            delta = expiry - datetime.now(timezone.utc)
            return delta if delta.total_seconds() > 0 else timedelta(0)
        except ValueError:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert consent record to dictionary."""
        return asdict(self)
    
    def get_consent_hash(self) -> str:
        """Generate hash for consent record integrity."""
        consent_data = {
            "consent_id": self.consent_id,
            "data_subject_id": self.data_subject_id,
            "consent_type": self.consent_type.value,
            "consent_scope": self.consent_scope.value,
            "status": self.status.value,
            "granted_timestamp": self.granted_timestamp,
            "purpose": self.purpose
        }
        return hashlib.sha256(json.dumps(consent_data, sort_keys=True).encode()).hexdigest()


class ConsentMigrator:
    """Utilities for migrating legacy consent values to standardized format."""
    
    @staticmethod
    def migrate_string_value(value: str) -> ConsentStatus:
        """Migrate legacy string consent values to ConsentStatus enum."""
        value_lower = value.lower().strip()
        
        # Direct mappings
        direct_mappings = {
            "granted": ConsentStatus.GRANTED,
            "active": ConsentStatus.ACTIVE,
            "valid": ConsentStatus.VALID,
            "approved": ConsentStatus.GRANTED,
            "accepted": ConsentStatus.GRANTED,
            "yes": ConsentStatus.GRANTED,
            
            "denied": ConsentStatus.DENIED,
            "refused": ConsentStatus.REFUSED,
            "rejected": ConsentStatus.DENIED,
            "no": ConsentStatus.DENIED,
            
            "withdrawn": ConsentStatus.WITHDRAWN,
            "revoked": ConsentStatus.REVOKED,
            "cancelled": ConsentStatus.WITHDRAWN,
            
            "pending": ConsentStatus.PENDING,
            "requested": ConsentStatus.REQUESTED,
            "under_review": ConsentStatus.UNDER_REVIEW,
            "review": ConsentStatus.UNDER_REVIEW,
            
            "expired": ConsentStatus.EXPIRED,
            "invalid": ConsentStatus.INVALID,
            "not_provided": ConsentStatus.NOT_PROVIDED,
            "none": ConsentStatus.NOT_PROVIDED,
            
            "unknown": ConsentStatus.UNKNOWN,
            "error": ConsentStatus.ERROR,
        }
        
        if value_lower in direct_mappings:
            return direct_mappings[value_lower]
        
        # Fuzzy matching for common variations
        if "grant" in value_lower or "allow" in value_lower:
            return ConsentStatus.GRANTED
        elif "deny" in value_lower or "refuse" in value_lower:
            return ConsentStatus.DENIED
        elif "withdraw" in value_lower or "revoke" in value_lower:
            return ConsentStatus.WITHDRAWN
        elif "pend" in value_lower or "wait" in value_lower:
            return ConsentStatus.PENDING
        elif "expir" in value_lower:
            return ConsentStatus.EXPIRED
        
        # Default to unknown
        warnings.warn(f"Unknown consent value '{value}' migrated to UNKNOWN")
        return ConsentStatus.UNKNOWN
    
    @staticmethod
    def migrate_boolean_value(value: bool) -> ConsentStatus:
        """Migrate legacy boolean consent values to ConsentStatus enum."""
        return ConsentStatus.GRANTED if value else ConsentStatus.DENIED
    
    @staticmethod
    def migrate_legacy_value(value: LegacyConsentValue) -> ConsentStatus:
        """Migrate any legacy consent value format to ConsentStatus enum."""
        if isinstance(value, ConsentStatus):
            return value
        elif isinstance(value, bool):
            return ConsentMigrator.migrate_boolean_value(value)
        elif isinstance(value, str):
            return ConsentMigrator.migrate_string_value(value)
        elif isinstance(value, dict) and "status" in value:
            return ConsentMigrator.migrate_legacy_value(value["status"])
        else:
            warnings.warn(f"Unable to migrate consent value '{value}' of type {type(value)}")
            return ConsentStatus.UNKNOWN
    
    @staticmethod
    def migrate_consent_dict(consent_dict: Dict[str, Any]) -> Dict[str, ConsentStatus]:
        """Migrate a dictionary of consent values."""
        migrated = {}
        for key, value in consent_dict.items():
            migrated[key] = ConsentMigrator.migrate_legacy_value(value)
        return migrated
    
    @staticmethod
    def migrate_boolean_consent(
        consent_dict: Dict[str, bool], 
        data_subject_id: str, 
        consent_type: ConsentType
    ) -> Dict[str, ConsentRecord]:
        """Migrate boolean consent dictionary to ConsentRecord format."""
        migrated_records = {}
        
        for purpose, granted in consent_dict.items():
            consent_status = ConsentStatus.GRANTED if granted else ConsentStatus.DENIED
            
            # Infer scope from purpose key
            scope = ConsentScope.DATA_PROCESSING  # Default
            purpose_lower = purpose.lower()
            
            if "marketing" in purpose_lower:
                scope = ConsentScope.MARKETING_COMMUNICATIONS
            elif "analytics" in purpose_lower:
                scope = ConsentScope.ANALYTICS_TRACKING
            elif "biometric" in purpose_lower:
                scope = ConsentScope.BIOMETRIC_COLLECTION
            elif "research" in purpose_lower:
                scope = ConsentScope.RESEARCH_PARTICIPATION
            elif "sharing" in purpose_lower or "third_party" in purpose_lower:
                scope = ConsentScope.THIRD_PARTY_SHARING
            elif "personalization" in purpose_lower:
                scope = ConsentScope.PERSONALIZATION
            elif "automated" in purpose_lower or "decision" in purpose_lower:
                scope = ConsentScope.AUTOMATED_DECISION_MAKING
            
            # Create consent record
            consent_id = f"migrated_{data_subject_id}_{purpose}_{int(time.time())}"
            
            record = ConsentRecord(
                consent_id=consent_id,
                data_subject_id=data_subject_id,
                consent_type=consent_type,
                consent_scope=scope,
                status=consent_status,
                purpose=f"Migrated consent for: {purpose}",
                metadata={
                    "migrated": True,
                    "original_purpose": purpose,
                    "original_value": granted,
                    "migration_timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            migrated_records[purpose] = record
        
        return migrated_records


class ConsentManager:
    """Centralized consent management for CIAF."""
    
    def __init__(self):
        self.consent_records: Dict[str, ConsentRecord] = {}
        self._audit_trail: List[Dict[str, Any]] = []
    
    def record_consent(
        self, 
        data_subject_id: str,
        consent_type: ConsentType,
        consent_scope: ConsentScope,
        purpose: str,
        legal_basis: str = "consent",
        expiry_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """Record new consent with standardized values."""
        
        consent_id = f"{data_subject_id}_{consent_scope.value}_{int(time.time())}"
        
        expiry_timestamp = None
        if expiry_days:
            expiry_date = datetime.now(timezone.utc) + timedelta(days=expiry_days)
            expiry_timestamp = expiry_date.isoformat()
        
        record = ConsentRecord(
            consent_id=consent_id,
            data_subject_id=data_subject_id,
            consent_type=consent_type,
            consent_scope=consent_scope,
            status=ConsentStatus.GRANTED,
            granted_timestamp=datetime.now(timezone.utc).isoformat(),
            expiry_timestamp=expiry_timestamp,
            legal_basis=legal_basis,
            purpose=purpose,
            metadata=metadata or {}
        )
        
        self.consent_records[consent_id] = record
        
        # Audit trail
        self._add_audit_entry("consent_granted", {
            "consent_id": consent_id,
            "data_subject_id": data_subject_id,
            "consent_scope": consent_scope.value,
            "consent_type": consent_type.value,
            "purpose": purpose
        })
        
        return record
    
    def withdraw_consent(
        self, 
        consent_id: Optional[str] = None,
        data_subject_id: Optional[str] = None,
        consent_scope: Optional[ConsentScope] = None
    ) -> List[str]:
        """Withdraw consent with standardized status update."""
        withdrawn_ids = []
        
        if consent_id:
            # Withdraw specific consent
            if consent_id in self.consent_records:
                record = self.consent_records[consent_id]
                record.status = ConsentStatus.WITHDRAWN
                record.withdrawn_timestamp = datetime.now(timezone.utc).isoformat()
                withdrawn_ids.append(consent_id)
                
                self._add_audit_entry("consent_withdrawn", {
                    "consent_id": consent_id,
                    "data_subject_id": record.data_subject_id,
                    "withdrawal_method": "specific_consent_id"
                })
        
        elif data_subject_id and consent_scope:
            # Withdraw by subject and scope
            for record in self.consent_records.values():
                if (record.data_subject_id == data_subject_id and 
                    record.consent_scope == consent_scope and
                    record.status in [ConsentStatus.GRANTED, ConsentStatus.ACTIVE, ConsentStatus.VALID]):
                    
                    record.status = ConsentStatus.WITHDRAWN
                    record.withdrawn_timestamp = datetime.now(timezone.utc).isoformat()
                    withdrawn_ids.append(record.consent_id)
                    
                    self._add_audit_entry("consent_withdrawn", {
                        "consent_id": record.consent_id,
                        "data_subject_id": data_subject_id,
                        "consent_scope": consent_scope.value,
                        "withdrawal_method": "subject_and_scope"
                    })
        
        elif data_subject_id:
            # Withdraw all consents for subject
            for record in self.consent_records.values():
                if (record.data_subject_id == data_subject_id and
                    record.status in [ConsentStatus.GRANTED, ConsentStatus.ACTIVE, ConsentStatus.VALID]):
                    
                    record.status = ConsentStatus.WITHDRAWN
                    record.withdrawn_timestamp = datetime.now(timezone.utc).isoformat()
                    withdrawn_ids.append(record.consent_id)
                    
                    self._add_audit_entry("consent_withdrawn", {
                        "consent_id": record.consent_id,
                        "data_subject_id": data_subject_id,
                        "withdrawal_method": "all_consents_for_subject"
                    })
        
        return withdrawn_ids
    
    def get_consent_status(
        self, 
        data_subject_id: str, 
        scope: ConsentScope
    ) -> ConsentStatus:
        """Get current consent status for specific scope."""
        for record in self.consent_records.values():
            if (record.data_subject_id == data_subject_id and 
                record.consent_scope == scope):
                return record.status
        
        return ConsentStatus.NOT_PROVIDED
    
    def validate_processing_consent(
        self, 
        data_subject_id: str, 
        scope: ConsentScope, 
        purpose: str
    ) -> Dict[str, Any]:
        """Validate consent for specific processing activity."""
        
        for record in self.consent_records.values():
            if (record.data_subject_id == data_subject_id and 
                record.consent_scope == scope):
                
                validation_result = {
                    "consent_valid": record.is_valid(),
                    "purpose_allowed": record.can_process_for_purpose(purpose),
                    "consent_status": record.status.value,
                    "consent_type": record.consent_type.value,
                    "granted_timestamp": record.granted_timestamp,
                    "legal_basis": record.legal_basis,
                    "consent_id": record.consent_id,
                    "time_until_expiry": None
                }
                
                if record.expiry_timestamp:
                    time_left = record.time_until_expiry()
                    if time_left:
                        validation_result["time_until_expiry"] = time_left.total_seconds()
                
                return validation_result
        
        return {
            "consent_valid": False,
            "purpose_allowed": False,
            "consent_status": ConsentStatus.NOT_PROVIDED.value,
            "error": "No consent record found",
            "data_subject_id": data_subject_id,
            "scope": scope.value
        }
    
    def get_consent_records_for_subject(self, data_subject_id: str) -> List[ConsentRecord]:
        """Get all consent records for a data subject."""
        return [
            record for record in self.consent_records.values()
            if record.data_subject_id == data_subject_id
        ]
    
    def cleanup_expired_consents(self) -> List[str]:
        """Mark expired consents and return list of expired consent IDs."""
        expired_ids = []
        current_time = datetime.now(timezone.utc)
        
        for record in self.consent_records.values():
            if (record.expiry_timestamp and 
                record.status in [ConsentStatus.GRANTED, ConsentStatus.ACTIVE, ConsentStatus.VALID]):
                
                try:
                    expiry = datetime.fromisoformat(record.expiry_timestamp.replace('Z', '+00:00'))
                    if current_time > expiry:
                        record.status = ConsentStatus.EXPIRED
                        expired_ids.append(record.consent_id)
                        
                        self._add_audit_entry("consent_expired", {
                            "consent_id": record.consent_id,
                            "data_subject_id": record.data_subject_id,
                            "expiry_timestamp": record.expiry_timestamp
                        })
                        
                except ValueError:
                    # Invalid timestamp, mark as error
                    record.status = ConsentStatus.ERROR
                    expired_ids.append(record.consent_id)
        
        return expired_ids
    
    def migrate_legacy_consent_data(
        self,
        legacy_data: Dict[str, LegacyConsentValue],
        data_subject_id: str,
        default_scope: ConsentScope = ConsentScope.DATA_PROCESSING,
        default_type: ConsentType = ConsentType.EXPLICIT
    ) -> List[ConsentRecord]:
        """Migrate legacy consent data to standardized format."""
        migrated_records = []
        
        for key, value in legacy_data.items():
            # Try to determine scope from key name
            scope = self._infer_scope_from_key(key, default_scope)
            consent_type = self._infer_type_from_key(key, default_type)
            
            # Migrate the value
            migrated_status = ConsentMigrator.migrate_legacy_value(value)
            
            # Create consent record
            consent_id = f"migrated_{data_subject_id}_{key}_{int(time.time())}"
            
            record = ConsentRecord(
                consent_id=consent_id,
                data_subject_id=data_subject_id,
                consent_type=consent_type,
                consent_scope=scope,
                status=migrated_status,
                purpose=f"Migrated from legacy field: {key}",
                metadata={"migrated": True, "original_key": key, "original_value": str(value)}
            )
            
            self.consent_records[consent_id] = record
            migrated_records.append(record)
            
            self._add_audit_entry("consent_migrated", {
                "consent_id": consent_id,
                "data_subject_id": data_subject_id,
                "original_key": key,
                "original_value": str(value),
                "migrated_status": migrated_status.value
            })
        
        return migrated_records
    
    def _infer_scope_from_key(self, key: str, default: ConsentScope) -> ConsentScope:
        """Infer consent scope from legacy key name."""
        key_lower = key.lower()
        
        scope_mappings = {
            "marketing": ConsentScope.MARKETING_COMMUNICATIONS,
            "analytics": ConsentScope.ANALYTICS_TRACKING,
            "biometric": ConsentScope.BIOMETRIC_COLLECTION,
            "research": ConsentScope.RESEARCH_PARTICIPATION,
            "sharing": ConsentScope.DATA_SHARING,
            "third_party": ConsentScope.THIRD_PARTY_SHARING,
            "personalization": ConsentScope.PERSONALIZATION,
            "automated": ConsentScope.AUTOMATED_DECISION_MAKING,
            "cross_border": ConsentScope.CROSS_BORDER_TRANSFER
        }
        
        for pattern, scope in scope_mappings.items():
            if pattern in key_lower:
                return scope
        
        return default
    
    def _infer_type_from_key(self, key: str, default: ConsentType) -> ConsentType:
        """Infer consent type from legacy key name."""
        key_lower = key.lower()
        
        type_mappings = {
            "parental": ConsentType.PARENTAL,
            "student": ConsentType.STUDENT,
            "guardian": ConsentType.GUARDIAN,
            "marketing": ConsentType.MARKETING,
            "analytics": ConsentType.ANALYTICS,
            "biometric": ConsentType.BIOMETRIC,
            "medical": ConsentType.MEDICAL,
            "research": ConsentType.RESEARCH,
            "opt_in": ConsentType.OPT_IN,
            "opt_out": ConsentType.OPT_OUT
        }
        
        for pattern, consent_type in type_mappings.items():
            if pattern in key_lower:
                return consent_type
        
        return default
    
    def _add_audit_entry(self, action: str, details: Dict[str, Any]):
        """Add entry to consent audit trail."""
        self._audit_trail.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "details": details
        })
    
    def export_consent_audit_trail(self) -> List[Dict[str, Any]]:
        """Export consent audit trail for compliance reporting."""
        return self._audit_trail.copy()
    
    def get_consent_summary(self, data_subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of consent status across all records."""
        records = self.consent_records.values()
        if data_subject_id:
            records = [r for r in records if r.data_subject_id == data_subject_id]
        
        summary = {
            "total_records": len(list(records)),
            "status_breakdown": {},
            "scope_breakdown": {},
            "type_breakdown": {},
            "valid_consents": 0,
            "expired_consents": 0,
            "withdrawn_consents": 0
        }
        
        for record in records:
            # Status breakdown
            status = record.status.value
            summary["status_breakdown"][status] = summary["status_breakdown"].get(status, 0) + 1
            
            # Scope breakdown
            scope = record.consent_scope.value
            summary["scope_breakdown"][scope] = summary["scope_breakdown"].get(scope, 0) + 1
            
            # Type breakdown
            consent_type = record.consent_type.value
            summary["type_breakdown"][consent_type] = summary["type_breakdown"].get(consent_type, 0) + 1
            
            # Validity checks
            if record.is_valid():
                summary["valid_consents"] += 1
            
            if record.status == ConsentStatus.EXPIRED:
                summary["expired_consents"] += 1
            
            if record.status in [ConsentStatus.WITHDRAWN, ConsentStatus.REVOKED]:
                summary["withdrawn_consents"] += 1
        
        return summary


# Utility functions for backward compatibility
def validate_consent_status(status: ConsentStatusValue) -> ConsentStatus:
    """Validate and convert consent status to enum."""
    if isinstance(status, ConsentStatus):
        return status
    
    return ConsentMigrator.migrate_legacy_value(status)


def migrate_consent_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate consent-related fields in metadata dictionaries."""
    migrated = metadata.copy()
    
    consent_fields = [
        "consent_status", "consent_compliance", "customer_consent",
        "parental_consent_status", "student_consent_status",
        "user_consent_status", "biometric_consent", "informed_consent_status"
    ]
    
    for field in consent_fields:
        if field in migrated:
            original_value = migrated[field]
            if isinstance(original_value, dict):
                # Handle dictionary of consent values
                migrated[field] = {
                    key: validate_consent_status(value).value
                    for key, value in original_value.items()
                }
            else:
                # Handle single consent value
                migrated[field] = validate_consent_status(original_value).value
            
            # Add migration metadata
            migrated[f"{field}_migrated"] = True
            migrated[f"{field}_original"] = str(original_value)
    
    return migrated


# Global consent manager instance
_global_consent_manager: Optional[ConsentManager] = None


def get_consent_manager() -> ConsentManager:
    """Get global consent manager instance."""
    global _global_consent_manager
    if _global_consent_manager is None:
        _global_consent_manager = ConsentManager()
    return _global_consent_manager


def reset_consent_manager():
    """Reset global consent manager (for testing)."""
    global _global_consent_manager
    _global_consent_manager = ConsentManager()


__all__ = [
    "ConsentRecord",
    "ConsentMigrator", 
    "ConsentManager",
    "ConsentStatusValue",
    "LegacyConsentValue",
    "validate_consent_status",
    "migrate_consent_metadata",
    "get_consent_manager",
    "reset_consent_manager"
]