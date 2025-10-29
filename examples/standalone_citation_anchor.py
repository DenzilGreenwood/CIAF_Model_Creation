"""
Standalone Citation Anchor System for CIAF Compliance

This is a standalone implementation that demonstrates the citation anchor
functionality without complex CIAF dependencies.

Created: 2025-10-27
Author: Denzil James Greenwood
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
import json


class CitationType(Enum):
    """Types of citations tracked by the system."""
    DATASET = "dataset"
    RESEARCH_PAPER = "research_paper"
    CODE_REPOSITORY = "code_repository"
    MODEL_WEIGHTS = "model_weights"
    TRAINING_DATA = "training_data"
    VALIDATION_DATA = "validation_data"
    TEST_DATA = "test_data"
    BENCHMARKS = "benchmarks"
    METHODOLOGY = "methodology"
    ALGORITHM = "algorithm"
    SOFTWARE_LIBRARY = "software_library"
    OPEN_SOURCE_CODE = "open_source_code"
    PROPRIETARY_CODE = "proprietary_code"
    COMMERCIAL_API = "commercial_api"
    HUMAN_ANNOTATION = "human_annotation"


class LicenseType(Enum):
    """Standard license types for data and code usage."""
    MIT = "mit"
    APACHE_2_0 = "apache_2_0"
    GPL_V3 = "gpl_v3"
    BSD_3_CLAUSE = "bsd_3_clause"
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    CC_BY_NC = "cc_by_nc"
    CC_BY_NC_SA = "cc_by_nc_sa"
    CC0 = "cc0"
    PROPRIETARY = "proprietary"
    COMMERCIAL = "commercial"
    CUSTOM = "custom"
    UNKNOWN = "unknown"
    PUBLIC_DOMAIN = "public_domain"


class UsageType(Enum):
    """Types of usage for cited resources."""
    TRAINING = "training"
    VALIDATION = "validation"
    TESTING = "testing"
    INFERENCE = "inference"
    BENCHMARKING = "benchmarking"
    RESEARCH = "research"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    REDISTRIBUTION = "redistribution"
    MODIFICATION = "modification"
    COMMERCIAL_USE = "commercial_use"


@dataclass
class CitationMetadata:
    """Metadata for a single citation."""
    citation_id: str
    title: str
    authors: List[str]
    organization: Optional[str] = None
    publication_date: Optional[str] = None
    version: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    license_type: LicenseType = LicenseType.UNKNOWN
    license_text: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class UsageRecord:
    """Record of how a cited resource is being used."""
    usage_id: str
    citation_id: str
    usage_type: UsageType
    purpose: str
    scope: str  # "full", "partial", "derived"
    percentage_used: Optional[float] = None
    modifications_made: List[str] = field(default_factory=list)
    attribution_provided: bool = False
    attribution_text: Optional[str] = None
    compliance_verified: bool = False
    used_by_model_id: Optional[str] = None
    used_by_dataset_id: Optional[str] = None
    usage_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expiry_date: Optional[str] = None


@dataclass
class ComplianceCheck:
    """Result of compliance verification for a citation."""
    check_id: str
    citation_id: str
    framework: str
    requirement: str
    status: str  # "compliant", "non_compliant", "needs_review", "not_applicable"
    severity: str  # "critical", "high", "medium", "low", "info"
    details: str
    recommendations: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None


class CitationAnchor:
    """
    Standalone Citation anchor system for tracking and validating data usage compliance.
    """
    
    def __init__(self):
        """Initialize citation anchor system."""
        self.citations: Dict[str, CitationMetadata] = {}
        self.usage_records: Dict[str, UsageRecord] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        
        # License compatibility matrix
        self.license_compatibility = self._build_license_compatibility_matrix()
        
    def _build_license_compatibility_matrix(self) -> Dict[LicenseType, Dict[UsageType, bool]]:
        """Build matrix of license type vs usage type compatibility."""
        return {
            LicenseType.MIT: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: True,
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: True,
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: True,
            },
            LicenseType.APACHE_2_0: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: True,
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: True,
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: True,
            },
            LicenseType.GPL_V3: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: False,  # Copyleft restrictions
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: False,  # Copyleft restrictions
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: False,  # Requires GPL compliance
            },
            LicenseType.CC_BY: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: True,
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: True,
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: True,
            },
            LicenseType.CC_BY_NC: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: False,  # Non-commercial restriction
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: False,  # Non-commercial restriction
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: False,
            },
            LicenseType.CC_BY_SA: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: True,
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: True,
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: True,
            },
            LicenseType.PUBLIC_DOMAIN: {
                UsageType.TRAINING: True,
                UsageType.VALIDATION: True,
                UsageType.TESTING: True,
                UsageType.INFERENCE: True,
                UsageType.BENCHMARKING: True,
                UsageType.RESEARCH: True,
                UsageType.DEVELOPMENT: True,
                UsageType.PRODUCTION: True,
                UsageType.REDISTRIBUTION: True,
                UsageType.MODIFICATION: True,
                UsageType.COMMERCIAL_USE: True,
            },
            LicenseType.PROPRIETARY: {
                UsageType.TRAINING: False,  # Requires explicit permission
                UsageType.VALIDATION: False,
                UsageType.TESTING: False,
                UsageType.INFERENCE: False,
                UsageType.BENCHMARKING: False,
                UsageType.RESEARCH: False,
                UsageType.DEVELOPMENT: False,
                UsageType.PRODUCTION: False,
                UsageType.REDISTRIBUTION: False,
                UsageType.MODIFICATION: False,
                UsageType.COMMERCIAL_USE: False,
            },
        }
    
    def add_citation(self, citation: CitationMetadata) -> str:
        """Add a new citation to the anchor system."""
        citation_hash = self._generate_citation_hash(citation)
        citation.citation_id = citation_hash
        
        self.citations[citation_hash] = citation
        
        print(f"🔗 Added citation: {citation.title} (ID: {citation_hash[:8]}...)")
        
        return citation_hash
    
    def record_usage(self, usage: UsageRecord) -> str:
        """Record usage of a cited resource."""
        if usage.citation_id not in self.citations:
            raise ValueError(f"Citation {usage.citation_id} not found")
        
        usage_hash = self._generate_usage_hash(usage)
        usage.usage_id = usage_hash
        
        self.usage_records[usage_hash] = usage
        
        # Automatically verify compliance for this usage
        compliance_result = self.verify_usage_compliance(usage.citation_id, usage.usage_type)
        
        print(f"📝 Recorded usage: {usage.purpose[:50]}... (ID: {usage_hash[:8]}...)")
        
        return usage_hash
    
    def verify_usage_compliance(self, citation_id: str, usage_type: UsageType) -> Dict[str, Any]:
        """Verify if usage complies with citation license."""
        if citation_id not in self.citations:
            raise ValueError(f"Citation {citation_id} not found")
        
        citation = self.citations[citation_id]
        license_type = citation.license_type
        
        # Check license compatibility
        is_compatible = self.license_compatibility.get(license_type, {}).get(usage_type, False)
        
        # Generate compliance check
        check_id = f"compliance_{citation_id[:8]}_{usage_type.value}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        if is_compatible:
            status = "compliant"
            severity = "info"
            details = f"Usage type '{usage_type.value}' is compatible with license '{license_type.value}'"
            recommendations = []
        else:
            status = "non_compliant"
            severity = "high"
            details = f"Usage type '{usage_type.value}' is NOT compatible with license '{license_type.value}'"
            recommendations = [
                "Obtain explicit permission from rights holder",
                "Consider alternative data sources with compatible licenses",
                "Review license terms for specific exemptions",
                "Consult legal team for guidance"
            ]
        
        # Special handling for unknown licenses
        if license_type == LicenseType.UNKNOWN:
            status = "needs_review"
            severity = "medium"
            details = "License type is unknown - manual review required"
            recommendations = [
                "Identify and document the correct license",
                "Contact data source for license clarification",
                "Assume restrictive usage until confirmed"
            ]
        
        compliance_check = ComplianceCheck(
            check_id=check_id,
            citation_id=citation_id,
            framework="general",
            requirement="License Compliance",
            status=status,
            severity=severity,
            details=details,
            recommendations=recommendations,
            evidence={
                "license_type": license_type.value,
                "usage_type": usage_type.value,
                "compatibility_matrix_result": is_compatible
            }
        )
        
        self.compliance_checks[check_id] = compliance_check
        
        return {
            "check_id": check_id,
            "status": status,
            "is_compliant": status == "compliant",
            "severity": severity,
            "details": details,
            "recommendations": recommendations
        }
    
    def generate_attribution_text(self, citation_id: str) -> str:
        """Generate proper attribution text for a citation."""
        if citation_id not in self.citations:
            raise ValueError(f"Citation {citation_id} not found")
        
        citation = self.citations[citation_id]
        
        # Build attribution based on available information
        attribution_parts = []
        
        # Authors
        if citation.authors:
            if len(citation.authors) == 1:
                attribution_parts.append(citation.authors[0])
            elif len(citation.authors) <= 3:
                attribution_parts.append(", ".join(citation.authors[:-1]) + " and " + citation.authors[-1])
            else:
                attribution_parts.append(citation.authors[0] + " et al.")
        
        # Title
        if citation.title:
            attribution_parts.append(f'"{citation.title}"')
        
        # Organization/Publisher
        if citation.organization:
            attribution_parts.append(citation.organization)
        
        # Publication date
        if citation.publication_date:
            attribution_parts.append(f"({citation.publication_date})")
        
        # DOI or URL
        if citation.doi:
            attribution_parts.append(f"DOI: {citation.doi}")
        elif citation.url:
            attribution_parts.append(f"Available at: {citation.url}")
        
        # License information
        if citation.license_type != LicenseType.UNKNOWN:
            attribution_parts.append(f"Licensed under {citation.license_type.value.upper().replace('_', ' ')}")
        
        return ". ".join(attribution_parts) + "."
    
    def validate_citations_for_model(self, model_id: str) -> Dict[str, Any]:
        """Validate all citations used by a specific model."""
        model_usages = [
            usage for usage in self.usage_records.values()
            if usage.used_by_model_id == model_id
        ]
        
        validation_results = []
        overall_compliant = True
        critical_issues = []
        warnings = []
        
        for usage in model_usages:
            citation = self.citations[usage.citation_id]
            compliance_result = self.verify_usage_compliance(usage.citation_id, usage.usage_type)
            
            validation_results.append({
                "usage_id": usage.usage_id,
                "citation_id": usage.citation_id,
                "citation_title": citation.title,
                "usage_type": usage.usage_type.value,
                "compliance_status": compliance_result["status"],
                "severity": compliance_result["severity"],
                "recommendations": compliance_result["recommendations"]
            })
            
            if compliance_result["status"] == "non_compliant":
                overall_compliant = False
                critical_issues.append({
                    "citation": citation.title,
                    "issue": compliance_result["details"],
                    "recommendations": compliance_result["recommendations"]
                })
            elif compliance_result["status"] == "needs_review":
                warnings.append({
                    "citation": citation.title,
                    "issue": compliance_result["details"]
                })
        
        return {
            "model_id": model_id,
            "total_citations": len(model_usages),
            "overall_compliant": overall_compliant,
            "validation_results": validation_results,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "validation_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report for all citations."""
        total_citations = len(self.citations)
        total_usages = len(self.usage_records)
        
        # Count compliance statuses
        compliance_counts = {}
        for check in self.compliance_checks.values():
            status = check.status
            compliance_counts[status] = compliance_counts.get(status, 0) + 1
        
        # License distribution
        license_distribution = {}
        for citation in self.citations.values():
            license_type = citation.license_type.value
            license_distribution[license_type] = license_distribution.get(license_type, 0) + 1
        
        # Usage type distribution
        usage_distribution = {}
        for usage in self.usage_records.values():
            usage_type = usage.usage_type.value
            usage_distribution[usage_type] = usage_distribution.get(usage_type, 0) + 1
        
        # Recent compliance issues
        recent_issues = [
            {
                "check_id": check.check_id,
                "citation_id": check.citation_id,
                "status": check.status,
                "severity": check.severity,
                "details": check.details,
                "checked_at": check.checked_at
            }
            for check in sorted(
                [c for c in self.compliance_checks.values() if c.status != "compliant"],
                key=lambda x: x.checked_at,
                reverse=True
            )[:10]
        ]
        
        return {
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_citations": total_citations,
                "total_usages": total_usages,
                "total_compliance_checks": len(self.compliance_checks),
                "compliance_rate": compliance_counts.get("compliant", 0) / max(len(self.compliance_checks), 1)
            },
            "compliance_distribution": compliance_counts,
            "license_distribution": license_distribution,
            "usage_distribution": usage_distribution,
            "recent_issues": recent_issues
        }
    
    def export_citations_bibliography(self, format: str = "bibtex") -> str:
        """Export citations in bibliography format."""
        if format.lower() == "bibtex":
            return self._export_bibtex()
        elif format.lower() == "apa":
            return self._export_apa()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_bibtex(self) -> str:
        """Export citations in BibTeX format."""
        bibtex_entries = []
        
        for citation in self.citations.values():
            entry_type = "misc"  # Default
            fields = []
            
            # Clean citation ID for BibTeX
            clean_id = citation.citation_id.replace("-", "_")[:16]
            
            fields.append(f'title = "{{{citation.title}}}"')
            
            if citation.authors:
                authors = " and ".join(citation.authors)
                fields.append(f'author = "{{{authors}}}"')
            
            if citation.organization:
                fields.append(f'organization = "{{{citation.organization}}}"')
            
            if citation.publication_date:
                fields.append(f'year = "{{{citation.publication_date}}}"')
            
            if citation.url:
                fields.append(f'url = "{{{citation.url}}}"')
            
            if citation.doi:
                fields.append(f'doi = "{{{citation.doi}}}"')
            
            fields.append(f'note = "Licensed under {citation.license_type.value.upper().replace("_", " ")}"')
            
            entry = f"@{entry_type}{{{clean_id},\n  " + ",\n  ".join(fields) + "\n}"
            bibtex_entries.append(entry)
        
        return "\n\n".join(bibtex_entries)
    
    def _export_apa(self) -> str:
        """Export citations in APA format."""
        apa_entries = []
        
        for citation in self.citations.values():
            apa_entries.append(self.generate_attribution_text(citation.citation_id))
        
        return "\n\n".join(apa_entries)
    
    def _generate_citation_hash(self, citation: CitationMetadata) -> str:
        """Generate hash for citation ID."""
        content = f"{citation.title}_{citation.authors}_{citation.organization}_{citation.publication_date}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_usage_hash(self, usage: UsageRecord) -> str:
        """Generate hash for usage ID."""
        content = f"{usage.citation_id}_{usage.usage_type.value}_{usage.purpose}_{usage.usage_timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]