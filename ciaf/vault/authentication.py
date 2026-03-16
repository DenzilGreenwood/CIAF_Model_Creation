"""
API Key authentication and multi-tenant organization management.
"""

import sqlite3
import secrets
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class Tenant:
    """Organization/tenant."""
    org_id: str
    name: str
    created_at: str
    api_key_count: int = 0
    last_activity: Optional[str] = None


@dataclass
class APIKey:
    """API key for accessing vault."""
    key_id: str
    org_id: str
    key_hash: str
    key_prefix: str  # First 8 chars for display
    created_at: str
    last_used: Optional[str] = None
    expires_at: Optional[str] = None
    is_active: bool = True
    description: str = ""


class APIKeyManager:
    """Manage API keys and multi-tenant organizations."""

    def __init__(self, vault_path: str = None):
        """Initialize API key manager."""
        self.vault_path = Path(vault_path or Path.home() / ".ciaf" / "vault")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.db_path = str(self.vault_path / "auth.db")
        self._init_auth_database()

    def _init_auth_database(self):
        """Initialize authentication database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Organizations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                org_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP,
                metadata TEXT
            )
        ''')

        # API keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                description TEXT,
                FOREIGN KEY (org_id) REFERENCES organizations(org_id)
            )
        ''')

        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keys_org ON api_keys(org_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keys_hash ON api_keys(key_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keys_active ON api_keys(is_active)')

        conn.commit()
        conn.close()

    def create_organization(self, org_id: str, name: str) -> Tenant:
        """Create new organization/tenant."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO organizations (org_id, name)
                VALUES (?, ?)
            ''', (org_id, name))

            conn.commit()
            conn.close()

            return Tenant(
                org_id=org_id,
                name=name,
                created_at=datetime.now().isoformat(),
                api_key_count=0
            )
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Organization already exists: {org_id}")

    def create_api_key(
        self,
        org_id: str,
        description: str = "",
        expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """
        Create new API key for organization.

        Returns:
            Tuple of (raw_key, key_object)
            Raw key must be shown to user only once.
        """
        # Generate random key
        raw_key = secrets.token_urlsafe(32)
        key_id = secrets.token_hex(8)
        key_prefix = raw_key[:8]

        # Hash key for storage
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        # Calculate expiry
        created_at = datetime.now()
        expires_at = None
        if expires_in_days:
            expires_at = (created_at + timedelta(days=expires_in_days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO api_keys (
                    key_id, org_id, key_hash, key_prefix,
                    expires_at, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                key_id,
                org_id,
                key_hash,
                key_prefix,
                expires_at,
                description
            ))

            conn.commit()
            conn.close()

            key_obj = APIKey(
                key_id=key_id,
                org_id=org_id,
                key_hash=key_hash,
                key_prefix=key_prefix,
                created_at=created_at.isoformat(),
                expires_at=expires_at,
                description=description
            )

            return raw_key, key_obj
        except Exception as e:
            conn.close()
            raise

    def verify_api_key(self, raw_key: str) -> Optional[tuple[str, str]]:
        """
        Verify API key and return (org_id, key_id) if valid.

        Args:
            raw_key: The API key to verify

        Returns:
            Tuple of (org_id, key_id) if valid, None otherwise
        """
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT org_id, key_id, is_active, expires_at
            FROM api_keys
            WHERE key_hash = ?
        ''', (key_hash,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        org_id, key_id, is_active, expires_at = row

        # Check if key is active
        if not is_active:
            conn.close()
            return None

        # Check if key has expired
        if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
            conn.close()
            return None

        # Update last_used timestamp
        cursor.execute(
            'UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE key_id = ?',
            (key_id,)
        )

        # Update organization last_activity
        cursor.execute(
            'UPDATE organizations SET last_activity = CURRENT_TIMESTAMP WHERE org_id = ?',
            (org_id,)
        )

        conn.commit()
        conn.close()

        return org_id, key_id

    def list_api_keys(self, org_id: str) -> List[APIKey]:
        """List all API keys for organization."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM api_keys WHERE org_id = ? ORDER BY created_at DESC
        ''', (org_id,))

        rows = cursor.fetchall()
        conn.close()

        return [
            APIKey(
                key_id=row["key_id"],
                org_id=row["org_id"],
                key_hash=row["key_hash"],
                key_prefix=row["key_prefix"],
                created_at=row["created_at"],
                last_used=row["last_used"],
                expires_at=row["expires_at"],
                is_active=bool(row["is_active"]),
                description=row["description"]
            )
            for row in rows
        ]

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke API key."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'UPDATE api_keys SET is_active = 0 WHERE key_id = ?',
            (key_id,)
        )

        conn.commit()
        affect = cursor.rowcount
        conn.close()

        return affect > 0

    def get_organization(self, org_id: str) -> Optional[Tenant]:
        """Get organization details."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM organizations WHERE org_id = ?', (org_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # Count API keys
        cursor.execute('SELECT COUNT(*) FROM api_keys WHERE org_id = ? AND is_active = 1', (org_id,))
        api_key_count = cursor.fetchone()[0]

        conn.close()

        return Tenant(
            org_id=row["org_id"],
            name=row["name"],
            created_at=row["created_at"],
            api_key_count=api_key_count,
            last_activity=row["last_activity"]
        )
