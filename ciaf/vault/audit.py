"""
Comprehensive audit logging for vault access and operations.
Every access is logged and immutable.
"""

import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class AuditEntry:
    """Single audit log entry."""
    entry_id: str
    action: str  # 'submit_proof', 'verify_proof', 'generate_certificate', etc.
    organization_id: str
    proof_id: Optional[str]
    actor: str  # API key or system
    timestamp: str
    result: str  # 'success' or 'failure'
    details: Dict[str, Any]
    ip_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditLogger:
    """
    Immutable audit logging system for vault operations.
    """

    def __init__(self, vault_path: str = None):
        """Initialize audit logger."""
        self.vault_path = Path(vault_path or Path.home() / ".ciaf" / "vault")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.db_path = str(self.vault_path / "audit.db")
        self._init_audit_database()

    def _init_audit_database(self):
        """Initialize audit database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Immutable audit log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                entry_id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                proof_id TEXT,
                actor TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                result TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                _written_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indices for fast queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_log(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_proof ON audit_log(proof_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor)')

        conn.commit()
        conn.close()

    def log_action(
        self,
        entry_id: str,
        action: str,
        organization_id: str,
        actor: str,
        result: str,
        details: Dict[str, Any],
        proof_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditEntry:
        """
        Log an action to the immutable audit trail.

        Args:
            entry_id: Unique entry ID
            action: Action performed
            organization_id: Organization performing action
            actor: Who/what performed action (API key, system, etc.)
            result: 'success' or 'failure'
            details: Additional details JSON
            proof_id: Associated proof if applicable
            ip_address: Source IP address

        Returns:
            AuditEntry created
        """
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO audit_log (
                    entry_id, action, organization_id, proof_id,
                    actor, timestamp, result, details, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_id,
                action,
                organization_id,
                proof_id,
                actor,
                timestamp,
                result,
                json.dumps(details),
                ip_address
            ))

            conn.commit()
            conn.close()

            return AuditEntry(
                entry_id=entry_id,
                action=action,
                organization_id=organization_id,
                proof_id=proof_id,
                actor=actor,
                timestamp=timestamp,
                result=result,
                details=details,
                ip_address=ip_address
            )
        except Exception as e:
            conn.close()
            raise

    def get_audit_trail(
        self,
        organization_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        action_filter: Optional[str] = None,
        limit: int = 1000
    ) -> List[AuditEntry]:
        """
        Get audit trail for organization.
        Multi-tenant isolation enforced.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = 'SELECT * FROM audit_log WHERE organization_id = ?'
        params = [organization_id]

        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time)
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time)
        if action_filter:
            query += ' AND action = ?'
            params.append(action_filter)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        entries = [
            AuditEntry(
                entry_id=row["entry_id"],
                action=row["action"],
                organization_id=row["organization_id"],
                proof_id=row["proof_id"],
                actor=row["actor"],
                timestamp=row["timestamp"],
                result=row["result"],
                details=json.loads(row["details"]) if row["details"] else {},
                ip_address=row["ip_address"]
            )
            for row in rows
        ]

        conn.close()
        return entries

    def get_audit_summary(self, organization_id: str) -> Dict[str, Any]:
        """Get audit summary for organization."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT COUNT(*) FROM audit_log WHERE organization_id = ?',
            (organization_id,)
        )
        total_actions = cursor.fetchone()[0]

        cursor.execute(
            'SELECT action, COUNT(*) as count FROM audit_log WHERE organization_id = ? GROUP BY action',
            (organization_id,)
        )
        actions = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(
            'SELECT result, COUNT(*) as count FROM audit_log WHERE organization_id = ? GROUP BY result',
            (organization_id,)
        )
        results = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(
            'SELECT COUNT(DISTINCT actor) FROM audit_log WHERE organization_id = ?',
            (organization_id,)
        )
        unique_actors = cursor.fetchone()[0]

        conn.close()

        return {
            "total_actions": total_actions,
            "actions_by_type": actions,
            "results": results,
            "unique_actors": unique_actors,
        }
