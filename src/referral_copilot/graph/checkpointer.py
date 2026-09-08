"""Graph Checkpointer Module.

Satisfies AC-05: Configured SQLite graph state checkpointer supporting pause,
checkpointing, and session resumption.
"""

from pathlib import Path
from referral_copilot.config import settings


def get_sqlite_checkpointer(db_path: Path = None):
    """Initializes and returns a SqliteSaver checkpointer instance.

    Args:
        db_path: Optional SQLite database file path.

    Returns:
        SqliteSaver instance or MemorySaver fallback.
    """
    target_path = db_path or settings.checkpoint_db_path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    from langgraph.checkpoint.sqlite import SqliteSaver
    import sqlite3

    conn = sqlite3.connect(str(target_path), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()
    return checkpointer
