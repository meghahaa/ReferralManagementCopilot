"""Tiered Memory System for Referral Copilot.

Satisfies AC-06: Tiered memory (Short-term working context + Long-term persistent store).
Satisfies AC-07: Persistent cross-session recall backed by local SQLite storage.
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from referral_copilot.config import settings
from referral_copilot.memory.eviction import MemoryEvictionPolicy


class TieredMemoryStore:
    """Manages short-term working state and durable cross-session long-term memory."""

    def __init__(self, db_path: Optional[Path] = None, max_capacity: int = 100):
        self.db_path = db_path or settings.memory_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.eviction_policy = MemoryEvictionPolicy(self.db_path, max_capacity=max_capacity)
        self._init_db()

    def _init_db(self) -> None:
        """Initializes SQLite schema for long-term durable memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_facts (
                fact_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                referral_id TEXT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                importance_score REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                last_accessed_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 1,
                ttl_seconds INTEGER
            )
            """
        )
        cursor.execute(
            "DELETE FROM memory_facts WHERE rowid NOT IN "
            "(SELECT MAX(rowid) FROM memory_facts GROUP BY category, key)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_facts_logical_key "
            "ON memory_facts(category, key)"
        )
        conn.commit()
        conn.close()

    def write_fact(
        self,
        session_id: str,
        category: str,
        key: str,
        value: str,
        referral_id: Optional[str] = None,
        importance_score: float = 0.5,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """Writes a durable fact into long-term cross-session memory store."""
        fact_id = f"FACT-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO memory_facts (
                fact_id, session_id, referral_id, category, key, value,
                importance_score, created_at, last_accessed_at, access_count, ttl_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                session_id = excluded.session_id,
                referral_id = excluded.referral_id,
                value = excluded.value,
                importance_score = excluded.importance_score,
                last_accessed_at = excluded.last_accessed_at,
                access_count = memory_facts.access_count + 1,
                ttl_seconds = excluded.ttl_seconds
            """,
            (fact_id, session_id, referral_id, category, key, value, importance_score, now, now, ttl_seconds)
        )
        conn.commit()
        conn.close()

        # Enforce eviction check post-write
        self.eviction_policy.enforce_eviction()
        return fact_id

    def get_fact_by_key(self, key: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves a persistent fact by key across sessions, updating last_accessed metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if session_id:
            cursor.execute(
                "SELECT fact_id, session_id, category, key, value, importance_score, created_at FROM memory_facts WHERE key = ? AND session_id = ? ORDER BY last_accessed_at DESC LIMIT 1",
                (key, session_id)
            )
        else:
            cursor.execute(
                "SELECT fact_id, session_id, category, key, value, importance_score, created_at FROM memory_facts WHERE key = ? ORDER BY last_accessed_at DESC LIMIT 1",
                (key,)
            )

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        fact_id, sess_id, cat, k, val, imp, created = row
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            "UPDATE memory_facts SET last_accessed_at = ?, access_count = access_count + 1 WHERE fact_id = ?",
            (now, fact_id)
        )
        conn.commit()
        conn.close()

        return {
            "fact_id": fact_id,
            "session_id": sess_id,
            "category": cat,
            "key": k,
            "value": val,
            "importance_score": imp,
            "created_at": created
        }

    def search_facts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists durable facts matching a category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category:
            cursor.execute("SELECT fact_id, session_id, category, key, value, importance_score FROM memory_facts WHERE category = ? ORDER BY last_accessed_at DESC", (category,))
        else:
            cursor.execute("SELECT fact_id, session_id, category, key, value, importance_score FROM memory_facts ORDER BY last_accessed_at DESC")

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "fact_id": r[0],
                "session_id": r[1],
                "category": r[2],
                "key": r[3],
                "value": r[4],
                "importance_score": r[5]
            }
            for r in rows
        ]
