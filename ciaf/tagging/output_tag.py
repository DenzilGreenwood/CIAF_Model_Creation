"""
Output Tagging System for CIAF

Creates cryptographic watermarks for AI-generated outputs.
Tags are minimal (hard to forge) with server-side proof storage.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
import uuid
import hashlib
import json


@dataclass
class OutputTag:
    """
    Cryptographic watermark for AI-generated output.

    Works with:
    - Direct model inferences (LLM, classifier, etc)
    - Agent-orchestrated inferences (multi-agent workflows)
    - Any AI system output

    Core design:
    - tag_id: Unique identifier (can be embedded in output)
    - Content hash: Prevents tampering (output must match hash)
    - Merkle proof: Proof it's in LCM chain (added after batching)
    """

    # Unique identifier
    tag_id: str

    # Output tracking
    session_id: str
    output_content_hash: str  # SHA-256(output content)
    inference_receipt_id: str  # Link to LCM inference receipt

    # Model/Agent context
    model_name: Optional[str] = None  # For direct model inference
    agent_ids: List[str] = field(default_factory=list)  # For agent workflows (optional)
    organization_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Inference type classification
    inference_type: str = "direct_model"  # "direct_model" or "agent_orchestrated"

    # Metadata for verification
    policies_applied: List[str] = field(default_factory=list)
    risk_level: str = "medium"

    # Merkle proof (filled after task batching)
    task_batch_id: Optional[str] = None
    task_batch_merkle_root: Optional[str] = None
    task_batch_proof: Optional[List[Tuple[str, str]]] = None

    # Org batch proof (filled after org batching)
    org_batch_id: Optional[str] = None
    org_batch_merkle_root: Optional[str] = None
    org_batch_proof: Optional[List[Tuple[str, str]]] = None

    # Status
    is_verified: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "tag_id": self.tag_id,
            "session_id": self.session_id,
            "output_content_hash": self.output_content_hash,
            "inference_receipt_id": self.inference_receipt_id,
            "agent_ids": self.agent_ids,
            "organization_id": self.organization_id,
            "timestamp": self.timestamp,
            "policies_applied": self.policies_applied,
            "risk_level": self.risk_level,
            "task_batch_id": self.task_batch_id,
            "task_batch_merkle_root": self.task_batch_merkle_root,
            "task_batch_proof": self.task_batch_proof,
            "org_batch_id": self.org_batch_id,
            "org_batch_merkle_root": self.org_batch_merkle_root,
            "org_batch_proof": self.org_batch_proof,
            "is_verified": self.is_verified,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_minimal_dict(self) -> Dict[str, str]:
        """
        Get minimal tag for embedding in output.

        Only includes:
        - tag_id: For lookup
        - session_id: For scope
        - output_content_hash: For tampering detection
        """
        return {
            "tag_id": self.tag_id,
            "session_id": self.session_id,
            "output_content_hash": self.output_content_hash,
            "inference_receipt_id": self.inference_receipt_id,
        }

    def add_task_batch_proof(
        self,
        task_batch_id: str,
        merkle_root: str,
        proof: List[Tuple[str, str]],
    ) -> None:
        """Add merkle proof from task batch."""
        self.task_batch_id = task_batch_id
        self.task_batch_merkle_root = merkle_root
        self.task_batch_proof = proof

    def add_org_batch_proof(
        self,
        org_batch_id: str,
        merkle_root: str,
        proof: List[Tuple[str, str]],
    ) -> None:
        """Add merkle proof from org batch."""
        self.org_batch_id = org_batch_id
        self.org_batch_merkle_root = merkle_root
        self.org_batch_proof = proof

    def mark_verified(self) -> None:
        """Mark tag as verified."""
        self.is_verified = True

    @staticmethod
    def compute_hash(content: Union[str, bytes]) -> str:
        """
        Compute SHA-256 hash of content.

        Args:
            content: Output content (text or bytes)

        Returns:
            Hex-encoded SHA-256 hash
        """
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()


class OutputTagManager:
    """
    Creates and manages output tags for all inference types.

    Workflow for agent inferences:
    1. create_agent_tag() - Create tag for agent output
    2. add_task_batch_proof() - Add proof after task batch
    3. add_org_batch_proof() - Add proof after org batch

    Workflow for direct model inferences:
    1. create_model_tag() - Create tag for model output
    2. add_task_batch_proof() - Add proof after task batch
    3. add_org_batch_proof() - Add proof after org batch
    """

    def __init__(self):
        self.tags: Dict[str, OutputTag] = {}
        self.tags_by_session: Dict[str, List[str]] = {}
        self.tags_by_model: Dict[str, List[str]] = {}  # model_name -> tag_ids
        self.tags_by_agent: Dict[str, List[str]] = {}  # agent_id -> tag_ids

    def create_agent_tag(
        self,
        output_content: Union[str, bytes],
        session_id: str,
        inference_receipt_id: str,
        agent_ids: List[str],
        organization_id: str,
        policies_applied: List[str] = None,
        risk_level: str = "medium",
    ) -> OutputTag:
        """
        Create tag for agent-orchestrated inference.

        Args:
            output_content: The AI-generated output
            session_id: User session ID
            inference_receipt_id: LCM inference receipt ID
            agent_ids: Which agents produced this
            organization_id: Organization context
            policies_applied: Policies enforced on this output
            risk_level: Risk classification

        Returns:
            OutputTag (without merkle proofs yet)
        """
        # Compute content hash
        content_hash = OutputTag.compute_hash(output_content)

        # Create tag
        tag_id = str(uuid.uuid4())
        tag = OutputTag(
            tag_id=tag_id,
            session_id=session_id,
            output_content_hash=content_hash,
            inference_receipt_id=inference_receipt_id,
            agent_ids=agent_ids,
            organization_id=organization_id,
            timestamp=datetime.now().isoformat(),
            policies_applied=policies_applied or [],
            risk_level=risk_level,
            inference_type="agent_orchestrated",
        )

        # Store
        self.tags[tag_id] = tag

        if session_id not in self.tags_by_session:
            self.tags_by_session[session_id] = []
        self.tags_by_session[session_id].append(tag_id)

        # Track by agents
        for agent_id in agent_ids:
            if agent_id not in self.tags_by_agent:
                self.tags_by_agent[agent_id] = []
            self.tags_by_agent[agent_id].append(tag_id)

        return tag

    def create_model_tag(
        self,
        output_content: Union[str, bytes],
        session_id: str,
        inference_receipt_id: str,
        model_name: str,
        organization_id: str,
        policies_applied: List[str] = None,
        risk_level: str = "medium",
    ) -> OutputTag:
        """
        Create tag for direct model inference (non-agent).

        Args:
            output_content: The AI-generated output
            session_id: User session ID
            inference_receipt_id: LCM inference receipt ID
            model_name: Which model was used (e.g., "llama2-7b", "gpt4_turbo")
            organization_id: Organization context
            policies_applied: Policies enforced on this output
            risk_level: Risk classification

        Returns:
            OutputTag (without merkle proofs yet)
        """
        # Compute content hash
        content_hash = OutputTag.compute_hash(output_content)

        # Create tag
        tag_id = str(uuid.uuid4())
        tag = OutputTag(
            tag_id=tag_id,
            session_id=session_id,
            output_content_hash=content_hash,
            inference_receipt_id=inference_receipt_id,
            model_name=model_name,
            agent_ids=[],  # No agents for direct inference
            organization_id=organization_id,
            timestamp=datetime.now().isoformat(),
            policies_applied=policies_applied or [],
            risk_level=risk_level,
            inference_type="direct_model",
        )

        # Store
        self.tags[tag_id] = tag

        if session_id not in self.tags_by_session:
            self.tags_by_session[session_id] = []
        self.tags_by_session[session_id].append(tag_id)

        # Track by model
        if model_name not in self.tags_by_model:
            self.tags_by_model[model_name] = []
        self.tags_by_model[model_name].append(tag_id)

        return tag

    def create_tag(
        self,
        output_content: Union[str, bytes],
        session_id: str,
        inference_receipt_id: str,
        organization_id: str,
        agent_ids: List[str] = None,
        model_name: str = None,
        policies_applied: List[str] = None,
        risk_level: str = "medium",
    ) -> OutputTag:
        """
        Generic tag creation - auto-detects agent vs model.

        Use create_agent_tag() or create_model_tag() for explicit control.

        Args:
            output_content: The AI-generated output
            session_id: User session ID
            inference_receipt_id: LCM inference receipt ID
            organization_id: Organization context
            agent_ids: For agent-orchestrated (optional)
            model_name: For direct model (optional)
            policies_applied: Policies enforced on this output
            risk_level: Risk classification

        Returns:
            OutputTag
        """
        if agent_ids:
            # Agent-orchestrated inference
            return self.create_agent_tag(
                output_content=output_content,
                session_id=session_id,
                inference_receipt_id=inference_receipt_id,
                agent_ids=agent_ids,
                organization_id=organization_id,
                policies_applied=policies_applied,
                risk_level=risk_level,
            )
        elif model_name:
            # Direct model inference
            return self.create_model_tag(
                output_content=output_content,
                session_id=session_id,
                inference_receipt_id=inference_receipt_id,
                model_name=model_name,
                organization_id=organization_id,
                policies_applied=policies_applied,
                risk_level=risk_level,
            )
        else:
            raise ValueError("Must provide either agent_ids or model_name")

    def get_tag(self, tag_id: str) -> Optional[OutputTag]:
        """Retrieve tag by ID."""
        return self.tags.get(tag_id)

    def get_session_tags(self, session_id: str) -> List[OutputTag]:
        """Get all tags from a session."""
        tag_ids = self.tags_by_session.get(session_id, [])
        return [self.tags[tid] for tid in tag_ids if tid in self.tags]

    def get_agent_tags(self, agent_id: str) -> List[OutputTag]:
        """Get all tags produced by a specific agent."""
        tag_ids = self.tags_by_agent.get(agent_id, [])
        return [self.tags[tid] for tid in tag_ids if tid in self.tags]

    def get_model_tags(self, model_name: str) -> List[OutputTag]:
        """Get all tags produced by a specific model."""
        tag_ids = self.tags_by_model.get(model_name, [])
        return [self.tags[tid] for tid in tag_ids if tid in self.tags]

    def add_task_batch_proof(
        self,
        tag_id: str,
        task_batch_id: str,
        merkle_root: str,
        proof: List[Tuple[str, str]],
    ) -> bool:
        """
        Add task batch merkle proof to tag.

        Called after task batch is created.

        Returns:
            True if successful
        """
        tag = self.get_tag(tag_id)
        if not tag:
            return False

        tag.add_task_batch_proof(task_batch_id, merkle_root, proof)
        return True

    def add_org_batch_proof(
        self,
        tag_id: str,
        org_batch_id: str,
        merkle_root: str,
        proof: List[Tuple[str, str]],
    ) -> bool:
        """
        Add org batch merkle proof to tag.

        Called after org batch window is created.

        Returns:
            True if successful
        """
        tag = self.get_tag(tag_id)
        if not tag:
            return False

        tag.add_org_batch_proof(org_batch_id, merkle_root, proof)
        tag.mark_verified()
        return True

    def verify_content(self, tag_id: str, content: Union[str, bytes]) -> bool:
        """
        Verify that content matches tag's hash.

        Returns:
            True if content matches
        """
        tag = self.get_tag(tag_id)
        if not tag:
            return False

        content_hash = OutputTag.compute_hash(content)
        return content_hash == tag.output_content_hash

    def export_tags(self, session_id: str) -> List[Dict[str, Any]]:
        """Export all tags from session as dicts."""
        tags = self.get_session_tags(session_id)
        return [tag.to_dict() for tag in tags]

    def get_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get statistics for organization."""
        org_tags = [
            tag for tag in self.tags.values() if tag.organization_id == organization_id
        ]

        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for tag in org_tags:
            risk_counts[tag.risk_level] = risk_counts.get(tag.risk_level, 0) + 1

        # Count by inference type
        agent_tags = [t for t in org_tags if t.inference_type == "agent_orchestrated"]
        model_tags = [t for t in org_tags if t.inference_type == "direct_model"]

        # Collect agents and models
        agents = set()
        models = set()
        for tag in org_tags:
            agents.update(tag.agent_ids)
            if tag.model_name:
                models.add(tag.model_name)

        return {
            "organization_id": organization_id,
            "total_tags": len(org_tags),
            "verified_tags": sum(1 for t in org_tags if t.is_verified),
            "risk_distribution": risk_counts,
            "inference_types": {
                "agent_orchestrated": len(agent_tags),
                "direct_model": len(model_tags),
            },
            "agents_involved": len(agents),
            "models_involved": list(models),
        }
