"""
Core vault functionality with WORM (Write-Once-Read-Many) enforcement
and multi-tenant isolation.
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import uuid
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend


@dataclass
class ProofReceipt:
    """Cryptographic receipt for submitted proof."""
    receipt_id: str
    proof_id: str
    organization_id: str
    timestamp: str
    signature: str
    verification_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationCertificate:
    """Certificate proving proof validity."""
    certificate_id: str
    proof_id: str
    generated_at: str
    valid_until: str
    issuer: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImmutableProof:
    """Proof stored in WORM (Write-Once-Read-Many) vault."""
    proof_id: str
    organization_id: str
    content_hash: str
    raw_content: str
    agent_ids: List[str]
    policies_applied: List[str]
    timestamp: str
    created_at: str
    verified: bool = False
    merkle_root: Optional[str] = None
    read_count: int = 0
    last_read: Optional[str] = None
    # WORM enforcement - once set, never changes
    _locked: bool = field(default=True, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "organization_id": self.organization_id,
            "content_hash": self.content_hash,
            "agent_ids": self.agent_ids,
            "policies_applied": self.policies_applied,
            "timestamp": self.timestamp,
            "created_at": self.created_at,
            "verified": self.verified,
            "merkle_root": self.merkle_root,
            "read_count": self.read_count,
            "last_read": self.last_read,
        }


class VaultManager:
    """
    Enterprise vault for storing cryptographic proofs.
    Enforces WORM and multi-tenant isolation.
    """

    def __init__(self, vault_path: str = None):
        """Initialize vault with WORM enforcement."""
        self.vault_path = Path(vault_path or Path.home() / ".ciaf" / "vault")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.db_path = str(self.vault_path / "vault.db")

        # Generate vault signing key (for receipts/certificates)
        self.signing_key_path = self.vault_path / "vault_key.pem"
        self._init_signing_key()

        # Initialize database with WORM enforcement
        self._init_vault_database()

    def _init_signing_key(self):
        """Initialize or load vault's cryptographic signing key."""
        if self.signing_key_path.exists():
            with open(self.signing_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
        else:
            # Generate new key for this vault
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(self.signing_key_path, "wb") as f:
                f.write(pem)

    def _init_vault_database(self):
        """Initialize vault database with WORM enforcement."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Immutable proofs table (WORM)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vault_proofs (
                proof_id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                content_hash TEXT NOT NULL UNIQUE,
                raw_content TEXT NOT NULL,
                agent_ids TEXT,
                policies_applied TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified INTEGER DEFAULT 0,
                merkle_root TEXT,
                read_count INTEGER DEFAULT 0,
                last_read TIMESTAMP,
                key_version TEXT DEFAULT '1.0',
                _write_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Receipts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vault_receipts (
                receipt_id TEXT PRIMARY KEY,
                proof_id TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                signature TEXT NOT NULL,
                verification_url TEXT,
                key_version TEXT DEFAULT '1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (proof_id) REFERENCES vault_proofs(proof_id)
            )
        ''')

        # Verification certificates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vault_certificates (
                certificate_id TEXT PRIMARY KEY,
                proof_id TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valid_until TIMESTAMP NOT NULL,
                issuer TEXT,
                signature TEXT NOT NULL,
                key_version TEXT DEFAULT '1.0',
                FOREIGN KEY (proof_id) REFERENCES vault_proofs(proof_id)
            )
        ''')

        # Multi-tenant organization isolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vault_organizations (
                org_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                api_key_salt TEXT,
                data_encryption_key TEXT
            )
        ''')

        # Key rotation table for managing signing key versions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vault_key_versions (
                key_version TEXT PRIMARY KEY,
                private_key_path TEXT NOT NULL,
                public_key_pem TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rotated_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                reason TEXT
            )
        ''')

        # Create indices for fast queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vault_org ON vault_proofs(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vault_timestamp ON vault_proofs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vault_hash ON vault_proofs(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_receipt_proof ON vault_receipts(proof_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vault_org_timestamp ON vault_proofs(organization_id, timestamp DESC)')

        # Add DB-level WORM enforcement triggers
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS vault_proofs_no_proof_update
            BEFORE UPDATE ON vault_proofs
            FOR EACH ROW
            WHEN NEW.proof_id != OLD.proof_id
              OR NEW.organization_id != OLD.organization_id
              OR NEW.content_hash != OLD.content_hash
              OR NEW.raw_content != OLD.raw_content
              OR NEW.agent_ids != OLD.agent_ids
              OR NEW.policies_applied != OLD.policies_applied
              OR NEW.timestamp != OLD.timestamp
              OR NEW.merkle_root != COALESCE(OLD.merkle_root, 'null')
            BEGIN
              SELECT RAISE(ABORT, 'WORM_VIOLATION: Cannot modify immutable proof fields');
            END
        ''')

        conn.commit()
        conn.close()

    def submit_proof(
        self,
        organization_id: str,
        content: str,
        agent_ids: List[str],
        policies_applied: List[str],
        timestamp: str
    ) -> ProofReceipt:
        """
        Submit proof to vault (WORM: can't be modified after).

        Args:
            organization_id: Organization submitting proof
            content: Raw proof content
            agent_ids: Agents involved
            policies_applied: Policies enforced
            timestamp: When proof was created

        Returns:
            ProofReceipt with verification URL
        """
        proof_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Generate merkle root for this proof
        merkle_root = hashlib.sha256(f"{proof_id}:{content_hash}".encode()).hexdigest()

        # Get current key version
        current_key_version = self.get_key_version()

        # Check for duplicate content (content addressed)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT proof_id FROM vault_proofs WHERE content_hash = ?', (content_hash,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            raise ValueError(f"Proof already exists: {existing[0]} (duplicate content)")

        # WORM: INSERT only (no updates allowed)
        try:
            cursor.execute('''
                INSERT INTO vault_proofs (
                    proof_id, organization_id, content_hash, raw_content,
                    agent_ids, policies_applied, timestamp, merkle_root, key_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proof_id,
                organization_id,
                content_hash,
                content,
                json.dumps(agent_ids),
                json.dumps(policies_applied),
                timestamp,
                merkle_root,
                current_key_version
            ))

            conn.commit()

            # Generate receipt
            receipt_id = str(uuid.uuid4())
            signature = self._sign_receipt(proof_id, organization_id, timestamp)

            cursor.execute('''
                INSERT INTO vault_receipts (
                    receipt_id, proof_id, organization_id, timestamp, signature, verification_url, key_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                receipt_id,
                proof_id,
                organization_id,
                timestamp,
                signature,
                f"https://vault.ciaf.io/verify/{proof_id}",
                current_key_version
            ))

            conn.commit()
            conn.close()

            return ProofReceipt(
                receipt_id=receipt_id,
                proof_id=proof_id,
                organization_id=organization_id,
                timestamp=datetime.now().isoformat(),
                signature=signature,
                verification_url=f"https://vault.ciaf.io/verify/{proof_id}"
            )
        except Exception as e:
            conn.close()
            raise

    def verify_proof(self, proof_id: str, organization_id: str) -> Optional[ImmutableProof]:
        """
        Verify and retrieve proof (WORM: read-only, increments read counter).

        Args:
            proof_id: Proof to verify
            organization_id: Organization requesting verification

        Returns:
            ImmutableProof if valid
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verify organization isolation
        cursor.execute(
            'SELECT * FROM vault_proofs WHERE proof_id = ? AND organization_id = ?',
            (proof_id, organization_id)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # WORM: Increment read counter (only update allowed)
        cursor.execute(
            'UPDATE vault_proofs SET read_count = read_count + 1, last_read = CURRENT_TIMESTAMP WHERE proof_id = ?',
            (proof_id,)
        )
        conn.commit()

        # Fetch updated row to get new read_count
        cursor.execute(
            'SELECT * FROM vault_proofs WHERE proof_id = ?',
            (proof_id,)
        )
        updated_row = cursor.fetchone()

        proof = ImmutableProof(
            proof_id=updated_row["proof_id"],
            organization_id=updated_row["organization_id"],
            content_hash=updated_row["content_hash"],
            raw_content=updated_row["raw_content"],
            agent_ids=json.loads(updated_row["agent_ids"]) if updated_row["agent_ids"] else [],
            policies_applied=json.loads(updated_row["policies_applied"]) if updated_row["policies_applied"] else [],
            timestamp=updated_row["timestamp"],
            created_at=updated_row["created_at"],
            verified=bool(updated_row["verified"]),
            merkle_root=updated_row["merkle_root"],
            read_count=updated_row["read_count"],
            last_read=updated_row["last_read"]
        )

        conn.close()
        return proof

    def get_organization_proofs(
        self,
        organization_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[ImmutableProof]:
        """
        Get all proofs for organization with time filtering.
        Multi-tenant isolation enforced.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = 'SELECT * FROM vault_proofs WHERE organization_id = ?'
        params = [organization_id]

        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time)
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        proofs = [
            ImmutableProof(
                proof_id=row["proof_id"],
                organization_id=row["organization_id"],
                content_hash=row["content_hash"],
                raw_content=row["raw_content"],
                agent_ids=json.loads(row["agent_ids"]) if row["agent_ids"] else [],
                policies_applied=json.loads(row["policies_applied"]) if row["policies_applied"] else [],
                timestamp=row["timestamp"],
                created_at=row["created_at"],
                verified=bool(row["verified"]),
                merkle_root=row["merkle_root"],
                read_count=row["read_count"],
                last_read=row["last_read"]
            )
            for row in rows
        ]

        conn.close()
        return proofs

    def generate_certificate(self, proof_id: str, organization_id: str) -> VerificationCertificate:
        """Generate verification certificate for proof."""
        certificate_id = str(uuid.uuid4())
        valid_until = (datetime.now() + timedelta(days=365)).isoformat()  # 1 year
        signature = self._sign_certificate(proof_id, certificate_id)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO vault_certificates (
                certificate_id, proof_id, valid_until, issuer, signature
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            certificate_id,
            proof_id,
            valid_until,
            "CIAF Vault",
            signature
        ))

        conn.commit()
        conn.close()

        return VerificationCertificate(
            certificate_id=certificate_id,
            proof_id=proof_id,
            generated_at=datetime.now().isoformat(),
            valid_until=valid_until,
            issuer="CIAF Vault",
            signature=signature
        )

    def _sign_receipt(self, proof_id: str, org_id: str, timestamp: str) -> str:
        """Sign receipt with vault key."""
        message = f"{proof_id}:{org_id}:{timestamp}".encode()
        signature = self.private_key.sign(message)
        return signature.hex()

    def _sign_certificate(self, proof_id: str, cert_id: str) -> str:
        """Sign certificate with vault key."""
        message = f"{proof_id}:{cert_id}".encode()
        signature = self.private_key.sign(message)
        return signature.hex()

    def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM vault_proofs')
        total_proofs = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM vault_organizations')
        total_orgs = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(read_count) FROM vault_proofs')
        total_reads = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(DISTINCT organization_id) FROM vault_proofs')
        active_orgs = cursor.fetchone()[0]

        conn.close()

        return {
            "total_proofs": total_proofs,
            "total_organizations": total_orgs,
            "active_organizations": active_orgs,
            "total_reads": total_reads,
            "avg_reads_per_proof": total_reads / max(total_proofs, 1),
        }

    def get_public_key_pem(self) -> str:
        """Get vault's public key for independent signature verification."""
        public_key = self.private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def get_key_version(self) -> str:
        """Get current key version."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT key_version FROM vault_key_versions WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "1.0"

    def rotate_key(self, reason: str = "Scheduled rotation") -> Dict[str, Any]:
        """
        Rotate the vault's signing key to a new version.

        Args:
            reason: Reason for key rotation (e.g., "Compromised", "Scheduled rotation")

        Returns:
            New key version metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Deactivate old key
        old_version = self.get_key_version()
        cursor.execute(
            'UPDATE vault_key_versions SET is_active = 0, rotated_at = CURRENT_TIMESTAMP WHERE is_active = 1'
        )

        # Generate new key
        new_private_key = ed25519.Ed25519PrivateKey.generate()
        new_version = f"{int(old_version.split('.')[0]) + 1}.0"

        # Store new key
        new_key_path = str(self.vault_path / f"vault_key_v{new_version}.pem")
        pem = new_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(new_key_path, "wb") as f:
            f.write(pem)

        # Record in database
        public_pem = new_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        cursor.execute('''
            INSERT INTO vault_key_versions (key_version, private_key_path, public_key_pem, is_active, reason)
            VALUES (?, ?, ?, 1, ?)
        ''', (new_version, new_key_path, public_pem, reason))

        conn.commit()
        conn.close()

        # Update active key in memory
        self.private_key = new_private_key
        self.signing_key_path = Path(new_key_path)

        return {
            "new_version": new_version,
            "old_version": old_version,
            "rotated_at": datetime.now().isoformat(),
            "reason": reason,
            "public_key_pem": public_pem
        }

    def get_key_versions(self) -> List[Dict[str, Any]]:
        """Get all key versions and their status."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT key_version, created_at, rotated_at, is_active, reason
            FROM vault_key_versions
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
