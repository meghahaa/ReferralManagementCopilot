"""Agentic-RAG Policy Lookup Tool.

Satisfies AC-11: Provides an agentic-RAG tool for referral-policy and network-rule lookups.
Retrieved inside graph loops on demand.
"""

import json
import re
import faiss
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from referral_copilot.config import settings
from referral_copilot.models.schemas import RAGQueryResult


class ReferralPolicyRAGTool:
    """Agentic RAG Tool indexing local synthetic healthcare policies and network rules."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.data_dir
        self.uploads_dir = self.data_dir / "uploads"
        self.evidence_dir = settings.evidence_dir
        self.documents: List[Dict[str, str]] = []
        self.index = None
        self.encoder = None
        self._load_documents()
        self._build_index()

    def _load_documents(self) -> None:
        """Loads and chunks text policy files from data/uploads/."""
        if not self.uploads_dir.exists():
            return

        for filepath in self.uploads_dir.glob("*.txt"):
            text = filepath.read_text(encoding="utf-8")
            # Chunk by section / paragraphs
            sections = [s.strip() for s in re.split(r"\n(?=[0-9]+\.|\bSECTION\b)", text) if s.strip()]
            for idx, sec in enumerate(sections):
                self.documents.append({
                    "source": filepath.name,
                    "chunk_id": f"{filepath.stem}_chunk_{idx+1}",
                    "text": sec
                })

    def _build_index(self) -> None:
        """Build a cosine-similarity FAISS index over policy embeddings."""
        if not self.documents:
            return
        from sentence_transformers import SentenceTransformer

        self.encoder = SentenceTransformer(settings.embedding_model)
        embeddings = self.encoder.encode(
            [document["text"] for document in self.documents],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

    def query_policy(self, query_text: str, top_k: int = 2) -> RAGQueryResult:
        """Performs on-demand policy lookup and relevance ranking.

        Args:
            query_text: User or agent policy query string.
            top_k: Maximum number of relevant policy chunks to retrieve.

        Returns:
            RAGQueryResult: Structured output containing retrieved chunks and source metadata.
        """
        if self.index is None or self.encoder is None:
            top_chunks = []
        else:
            query_embedding = self.encoder.encode(
                [query_text],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            ).astype("float32")
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            top_chunks = []
            for score, document_index in zip(scores[0], indices[0]):
                if document_index < 0:
                    continue
                if float(score) < settings.rag_relevance_threshold:
                    continue
                document = self.documents[document_index]
                top_chunks.append({
                    "chunk_id": document["chunk_id"],
                    "source": document["source"],
                    "text": document["text"],
                    "relevance_score": round(float(score), 3),
                })

        max_score = top_chunks[0]["relevance_score"] if top_chunks else 0.0
        primary_source = top_chunks[0]["source"] if top_chunks else "NO_MATCH"

        result = RAGQueryResult(
            query=query_text,
            retrieved_chunks=top_chunks,
            relevance_score=max_score,
            policy_source=primary_source
        )

        self._record_evidence(result)
        return result

    def _record_evidence(self, result: RAGQueryResult) -> None:
        """Records structured evidence JSON artifact for AC-11."""
        evidence_file = self.evidence_dir / "AC-11_agentic_rag.json"
        log_entry = {
            "ac_id": "AC-11",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": result.query,
            "relevance_score": result.relevance_score,
            "policy_source": result.policy_source,
            "chunks_count": len(result.retrieved_chunks),
            "retrieved_chunks": result.retrieved_chunks
        }
        with open(evidence_file, "w") as f:
            json.dump(log_entry, f, indent=2)
