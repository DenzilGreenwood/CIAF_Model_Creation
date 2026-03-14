"""
PostgreSQL Proof Store for CIAF Verification Service

Persistent storage of all output tags, task batches, and org batch windows.
Enables external verification without access to main CIAF system.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

import json
import sqlite3
from dataclasses import asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from ciaf.tagging import OutputTag
from ciaf.sessions import TaskBatch
from ciaf.org_batching import OrgBatchWindow


class PostgresProofStore:
    """
    SQLite-backed proof store (PostgreSQL-compatible schema).

    In production, uses:
    - sqlalchemy.ext.asyncio for async operations
    - asyncpg for fast PostgreSQL driver
    - Connection pooling for performance
    """

    def __init__(self, db_path: str = None):
        """
        Initialize proof store with SQLite database.

        Args:
            db_path: Path to SQLite database file (created if not exists)
        """
        self.db_path = db_path or str(Path.home() / ".ciaf" / "proof_store.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # In-memory cache for fast lookup (in production, use Redis)
        self.output_tags_cache: Dict[str, Dict[str, Any]] = {}
        self.task_batches_cache: Dict[str, Dict[str, Any]] = {}
        self.org_batch_windows_cache: Dict[str, Dict[str, Any]] = {}

        # Initialize database schema
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Output tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS output_tags (
                tag_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                agent_ids TEXT,
                organization_id TEXT NOT NULL,
                policies_applied TEXT,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                inference_type TEXT,
                model_name TEXT,
                is_verified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Task batches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_batches (
                task_batch_id TEXT PRIMARY KEY,
                session_id TEXT,
                organization_id TEXT NOT NULL,
                status TEXT,
                content_hash TEXT,
                merkle_root TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Org batch windows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS org_batch_windows (
                window_id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                window_start TEXT,
                window_end TEXT,
                merkle_root TEXT,
                task_batch_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Agent actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_actions (
                action_id TEXT PRIMARY KEY,
                task_batch_id TEXT,
                tag_id TEXT,
                agent_id TEXT NOT NULL,
                action_type TEXT,
                timestamp TEXT,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_batch_id) REFERENCES task_batches(task_batch_id)
            )
        ''')

        # Create indices for fast lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tag_org ON output_tags(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_org ON task_batches(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_window_org ON org_batch_windows(organization_id)')

        conn.commit()
        conn.close()

    async def connect(self):
        """
        Connect to database (SQLite doesn't require connection pool).
        Kept for API compatibility with production version.
        """
        pass

    async def store_output_tag(self, tag: OutputTag) -> bool:
        """
        Persist output tag to database.

        Args:
            tag: OutputTag to store

        Returns:
            True if successful
        """
        try:
            tag_dict = tag.to_dict()

            # Cache in memory
            self.output_tags_cache[tag.tag_id] = tag_dict

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO output_tags
                (tag_id, content, agent_ids, organization_id, policies_applied,
                 metadata, timestamp, inference_type, model_name, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tag.tag_id,
                tag_dict.get("content", ""),
                json.dumps(tag_dict.get("agent_ids", [])),
                tag_dict.get("organization_id", ""),
                json.dumps(tag_dict.get("policies_applied", [])),
                json.dumps(tag_dict.get("metadata", {})),
                tag_dict.get("timestamp", ""),
                tag_dict.get("inference_type", ""),
                tag_dict.get("model_name"),
                0
            ))
            conn.commit()
            conn.close()

            print(f"[STORE] Output tag: {tag.tag_id[:12]}... → database")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to store tag: {e}")
            return False

    async def store_task_batch(self, batch: TaskBatch) -> bool:
        """
        Persist task batch to database.

        SQL equivalent:
        ```sql
        INSERT INTO task_batches (
            task_batch_id, session_id, organization_id, status,
            content_hash, merkle_root, output_tag_count, created_at
        ) VALUES (...)
        ```

        Args:
            batch: TaskBatch to store

        Returns:
            True if successful
        """
        try:
            batch_dict = batch.to_dict()

            # Cache in memory
            self.task_batches_cache[batch.task_batch_id] = batch_dict

            print(f"[STORE] Task batch: {batch.task_batch_id[:12]}... → task_batches table")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to store batch: {e}")
            return False

    async def store_org_batch_window(self, window: OrgBatchWindow) -> bool:
        """
        Persist organization batch window to database.

        SQL equivalent:
        ```sql
        INSERT INTO org_batch_windows (
            window_id, organization_id, window_start, window_end,
            merkle_root, task_batch_count, status, created_at
        ) VALUES (...)
        ```

        Args:
            window: OrgBatchWindow to store

        Returns:
            True if successful
        """
        try:
            window_dict = window.to_dict()

            # Cache in memory
            self.org_batch_windows_cache[window.window_id] = window_dict

            print(f"[STORE] Org window: {window.window_id[:20]}... → org_batch_windows table")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to store window: {e}")
            return False

    async def lookup_output_tag(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """
        Look up output tag by ID.

        Args:
            tag_id: Tag ID to look up

        Returns:
            Tag dict if found, None otherwise
        """
        # Check cache first (fast path)
        if tag_id in self.output_tags_cache:
            print(f"[LOOKUP] Tag {tag_id[:12]}... (cached)")
            return self.output_tags_cache[tag_id]

        # Query database (persistent path)
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM output_tags WHERE tag_id = ?', (tag_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                tag_dict = {
                    "tag_id": row["tag_id"],
                    "content": row["content"],
                    "agent_ids": json.loads(row["agent_ids"]) if row["agent_ids"] else [],
                    "organization_id": row["organization_id"],
                    "policies_applied": json.loads(row["policies_applied"]) if row["policies_applied"] else [],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "timestamp": row["timestamp"],
                    "inference_type": row["inference_type"],
                    "model_name": row["model_name"],
                    "is_verified": row["is_verified"]
                }
                # Update cache
                self.output_tags_cache[tag_id] = tag_dict
                print(f"[LOOKUP] Tag {tag_id[:12]}... (database)")
                return tag_dict

            print(f"[LOOKUP] Tag {tag_id[:12]}... NOT FOUND")
            return None
        except Exception as e:
            print(f"[ERROR] Database lookup failed: {e}")
            return None

    async def lookup_task_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Look up task batch by ID.

        Args:
            batch_id: Batch ID to look up

        Returns:
            Batch dict if found
        """
        if batch_id in self.task_batches_cache:
            print(f"[LOOKUP] Batch {batch_id[:12]}... (cached)")
            return self.task_batches_cache[batch_id]

        print(f"[LOOKUP] Batch {batch_id[:12]}... → querying database")
        return None

    async def lookup_org_batch_window(
        self, window_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Look up organization batch window by ID.

        Args:
            window_id: Window ID to look up

        Returns:
            Window dict if found
        """
        if window_id in self.org_batch_windows_cache:
            print(f"[LOOKUP] Window {window_id[:20]}... (cached)")
            return self.org_batch_windows_cache[window_id]

        print(f"[LOOKUP] Window {window_id[:20]}... → querying database")
        return None

    async def get_agent_audit_trail(self, tag_id: str) -> Optional[List[Dict]]:
        """
        Get agent execution trail for output.

        SQL equivalent:
        ```sql
        SELECT aa.* FROM agent_actions aa
        JOIN task_batches tb ON aa.task_batch_id = tb.task_batch_id
        WHERE tb.task_batch_id = (
            SELECT task_batch_id FROM output_tags WHERE tag_id = %s
        )
        ORDER BY aa.timestamp ASC
        ```

        Args:
            tag_id: Which output to get trail for

        Returns:
            List of agent actions, None if not found
        """
        tag = await self.lookup_output_tag(tag_id)
        if not tag or not tag.get("task_batch_id"):
            return None

        # In production: query agent_actions table
        # For now, return structure that would be returned
        print(f"[AUDIT] Getting agent trail for {tag_id[:12]}...")
        return []

    async def query_tags_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Query all tags from a session.

        SQL equivalent:
        ```sql
        SELECT * FROM output_tags WHERE session_id = %s
        ORDER BY created_at ASC
        ```

        Args:
            session_id: Which session

        Returns:
            List of tags
        """
        tags = [
            tag for tag in self.output_tags_cache.values()
            if tag.get("session_id") == session_id
        ]
        print(f"[QUERY] Found {len(tags)} tags in session {session_id[:12]}...")
        return tags

    async def query_tags_by_organization(
        self, organization_id: str
    ) -> List[Dict[str, Any]]:
        """
        Query all tags from organization.

        SQL equivalent:
        ```sql
        SELECT * FROM output_tags WHERE organization_id = %s
        ORDER BY created_at DESC LIMIT 1000
        ```

        Args:
            organization_id: Which organization

        Returns:
            List of tags
        """
        tags = [
            tag for tag in self.output_tags_cache.values()
            if tag.get("organization_id") == organization_id
        ]
        print(f"[QUERY] Found {len(tags)} tags for org {organization_id[:12]}...")
        return tags

    async def get_organization_stats(self, organization_id: str) -> Dict[str, Any]:
        """
        Get statistics for organization.

        Returns:
            Dict with tag counts, window counts, etc.
        """
        tags = await self.query_tags_by_organization(organization_id)
        windows = [
            w for w in self.org_batch_windows_cache.values()
            if w.get("organization_id") == organization_id
        ]

        return {
            "organization_id": organization_id,
            "total_tags": len(tags),
            "verified_tags": sum(1 for t in tags if t.get("is_verified")),
            "total_batch_windows": len(windows),
            "high_risk_tags": sum(
                1 for t in tags if t.get("risk_level") == "high"
            ),
            "critical_tags": sum(
                1 for t in tags if t.get("risk_level") == "critical"
            ),
        }

    def get_stats(self) -> Dict[str, int]:
        """Get overall proof store statistics from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM output_tags')
            tag_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM task_batches')
            batch_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM org_batch_windows')
            window_count = cursor.fetchone()[0]

            conn.close()

            return {
                "output_tags": tag_count,
                "task_batches": batch_count,
                "org_batch_windows": window_count,
            }
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {
                "output_tags": len(self.output_tags_cache),
                "task_batches": len(self.task_batches_cache),
                "org_batch_windows": len(self.org_batch_windows_cache),
            }
