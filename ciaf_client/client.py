"""Main CIAF Client for communicating with the verification service."""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from .types import VerificationResult, AuditAction, ComplianceReport, VerificationStatus, RiskLevel


class CIAFClient:
    """Client for communicating with CIAF Verification Service."""

    def __init__(self, base_url: str = "http://localhost:8001", timeout: int = 30):
        """Initialize CIAF Client.

        Args:
            base_url: Base URL of the verification service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify connection to the verification service."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            if response.status_code != 200:
                raise ConnectionError(f"Service health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to CIAF service at {self.base_url}: {e}")

    def verify_output(self, tag_id: str, include_audit: bool = False) -> VerificationResult:
        """Verify an output tag.

        Args:
            tag_id: The tag ID to verify
            include_audit: Whether to include full audit trail

        Returns:
            VerificationResult object
        """
        params = {"include_audit": include_audit}
        response = self.session.get(
            f"{self.base_url}/verify/{tag_id}",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        return self._parse_verification_result(data)

    def submit_verification(
        self,
        content: str,
        tag_id: str,
        agents: List[str],
        organization_id: str,
        policies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Submit content for verification (stores tag in proof store).

        Args:
            content: The AI-generated content
            tag_id: Unique tag identifier
            agents: List of agent IDs that generated the content
            organization_id: Organization ID
            policies: Applied policies
            metadata: Additional metadata

        Returns:
            Submission confirmation with tag_id
        """
        payload = {
            "tag_id": tag_id,
            "content": content,
            "agents": agents,
            "organization_id": organization_id,
            "policies": policies or [],
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        response = self.session.post(
            f"{self.base_url}/tags",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_audit_trail(
        self,
        tag_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditAction]:
        """Get audit trail for a tag.

        Args:
            tag_id: The tag ID
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of AuditAction objects
        """
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = self.session.get(
            f"{self.base_url}/audit/{tag_id}",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        return [self._parse_audit_action(action) for action in data.get("actions", [])]

    def get_compliance_report(
        self,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ComplianceReport:
        """Get compliance report for organization.

        Args:
            organization_id: Organization ID
            start_date: Report start date
            end_date: Report end date

        Returns:
            ComplianceReport object
        """
        params = {"org_id": organization_id}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = self.session.get(
            f"{self.base_url}/compliance/{organization_id}",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        return self._parse_compliance_report(data)

    def get_organization_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get organization statistics.

        Args:
            organization_id: Organization ID

        Returns:
            Organization statistics
        """
        response = self.session.get(
            f"{self.base_url}/stats/{organization_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def refresh_verification_cache(self) -> Dict[str, Any]:
        """Refresh the verification cache.

        Returns:
            Cache refresh response
        """
        response = self.session.post(
            f"{self.base_url}/admin/refresh-cache",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _parse_verification_result(data: Dict[str, Any]) -> VerificationResult:
        """Parse verification result from API response."""
        return VerificationResult(
            tag_id=data.get("tag_id", ""),
            status=VerificationStatus(data.get("status", "unverified")),
            risk_level=RiskLevel(data.get("risk_level", "low")),
            verified_at=datetime.fromisoformat(data.get("verified_at", datetime.now(timezone.utc).isoformat())),
            agents=data.get("agents", []),
            policies=data.get("policies", []),
            merkle_proof_valid=data.get("merkle_proof_valid", False),
            content_hash=data.get("content_hash", ""),
            issues=data.get("issues", []),
            warnings=data.get("warnings", [])
        )

    @staticmethod
    def _parse_audit_action(data: Dict[str, Any]) -> AuditAction:
        """Parse audit action from API response."""
        return AuditAction(
            action_id=data.get("action_id", ""),
            agent_id=data.get("agent_id", ""),
            action_type=data.get("action_type", ""),
            resource=data.get("resource", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(timezone.utc).isoformat())),
            status=data.get("status", ""),
            details=data.get("details", {})
        )

    @staticmethod
    def _parse_compliance_report(data: Dict[str, Any]) -> ComplianceReport:
        """Parse compliance report from API response."""
        return ComplianceReport(
            organization_id=data.get("organization_id", ""),
            period_start=datetime.fromisoformat(data.get("period_start", datetime.now(timezone.utc).isoformat())),
            period_end=datetime.fromisoformat(data.get("period_end", datetime.now(timezone.utc).isoformat())),
            total_outputs=data.get("total_outputs", 0),
            verified_outputs=data.get("verified_outputs", 0),
            compliance_rate=data.get("compliance_rate", 0.0),
            high_risk_count=data.get("high_risk_count", 0),
            critical_count=data.get("critical_count", 0),
            policies_covered=data.get("policies_covered", []),
            gaps=data.get("gaps", [])
        )
