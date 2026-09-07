"""Centralized Configuration Module for Referral Management Copilot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Centralized Settings class for LLM, database, and system configurations."""

    def __init__(self):
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "gemini").lower()

        # Gemini settings
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Groq settings
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        self.groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        # Model hyperparameters
        self.temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
        self.timeout: int = int(os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

        # Paths
        self.checkpoint_db_path: Path = BASE_DIR / os.getenv("CHECKPOINT_DB_PATH", "data/checkpoints.db")
        self.memory_db_path: Path = BASE_DIR / os.getenv("MEMORY_DB_PATH", "data/memory.db")
        self.vector_store_dir: Path = BASE_DIR / os.getenv("VECTOR_STORE_DIR", "data/vector_store")
        self.data_dir: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
        self.evidence_dir: Path = BASE_DIR / os.getenv("EVIDENCE_DIR", "evidence")

        # Ensure directories exist
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "synthetic").mkdir(parents=True, exist_ok=True)


settings = Settings()
