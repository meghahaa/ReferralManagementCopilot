"""Memory Eviction & Importance Policy Module.

Satisfies AC-08: Implements an explicit importance-weighted LRU eviction policy.

Design Rationale:
-----------------
Healthcare referral memory stores both transient session details and persistent patient/provider facts.
1. High-importance facts (importance_score >= 0.8, e.g. severe clinical allergies or insurance overrides)
   are protected from LRU eviction.
2. Low-importance facts (importance_score < 0.5) are subject to LRU eviction when memory store exceeds max capacity.
3. Expired facts (TTL exceeded) are purged automatically regardless of importance.
"""

from datetime import datetime, timedelta, timezone
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path


class MemoryEvictionPolicy:
    """Manages TTL and Importance-Weighted LRU Eviction for persistent memory."""

    def __init__(self, db_path: Path, max_capacity: int = 100, default_ttl_days: int = 30):
        self.db_path = db_path
        self.max_capacity = max_capacity
        self.default_ttl_days = default_ttl_days

    def enforce_eviction(self) -> List[str]:
        """Executes eviction algorithm and returns IDs of evicted memory facts."""
        evicted_ids: List[str] = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Purge TTL Expired Records
        cursor.execute(
            """
            SELECT fact_id FROM memory_facts
            WHERE ttl_seconds IS NOT NULL
            AND datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime(?)
            """,
            (now_iso,)
        )
        expired_rows = cursor.fetchall()
        for row in expired_rows:
            evicted_ids.append(row[0])

        if expired_rows:
            cursor.execute(
                f"DELETE FROM memory_facts WHERE fact_id IN ({','.join(['?']*len(expired_rows))})",
                [r[0] for r in expired_rows]
            )

        # 2. Capacity Check & Importance-Weighted LRU Eviction
        cursor.execute("SELECT COUNT(*) FROM memory_facts")
        current_count = cursor.fetchone()[0]

        if current_count > self.max_capacity:
            excess = current_count - self.max_capacity
            # Select lowest importance, oldest last_accessed_at rows
            cursor.execute(
                """
                SELECT fact_id FROM memory_facts
                WHERE importance_score < 0.8
                ORDER BY importance_score ASC, last_accessed_at ASC
                LIMIT ?
                """,
                (excess,)
            )
            lru_rows = cursor.fetchall()
            for row in lru_rows:
                evicted_ids.append(row[0])

            if lru_rows:
                cursor.execute(
                    f"DELETE FROM memory_facts WHERE fact_id IN ({','.join(['?']*len(lru_rows))})",
                    [r[0] for r in lru_rows]
                )

        conn.commit()
        conn.close()
        return evicted_ids
