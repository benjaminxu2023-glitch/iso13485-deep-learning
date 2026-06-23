"""Pluggable embedding engine for semantic similarity.

Two backends share one interface:

* ``tfidf`` (default) - scikit-learn TF-IDF vectors. Fully offline, deterministic,
  no model downloads. Suitable for a reproducible, auditable compliance tool.
* ``transformer`` - sentence-transformers embeddings (optional ``[nlp]`` extra).
"""

from __future__ import annotations

import numpy as np


class NLPEngine:
    """Encodes text to L2-normalised vectors and computes cosine similarity."""

    def __init__(self, backend: str = "tfidf", model_name: str | None = None):
        self.backend = backend
        self.model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        self._model = None  # transformer model, lazily loaded
        self._vectorizer = None  # tfidf vectorizer, fitted per corpus

    # -- transformer backend -------------------------------------------------
    @property
    def model(self):  # pragma: no cover - exercised only with the [nlp] extra
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ImportError(
                    "The 'transformer' NLP backend requires the optional 'nlp' extra: "
                    "pip install 'iso13485-audit[nlp]'"
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _encode_transformer(self, texts: list[str]) -> np.ndarray:  # pragma: no cover
        emb = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(emb, dtype=np.float32)

    # -- tfidf backend -------------------------------------------------------
    def fit(self, corpus: list[str]) -> None:
        """Fit the TF-IDF vocabulary on a corpus (no-op for the transformer backend)."""
        if self.backend != "tfidf":
            return
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=1, sublinear_tf=True
        )
        self._vectorizer.fit(corpus or [""])

    def _encode_tfidf(self, texts: list[str]) -> np.ndarray:
        if self._vectorizer is None:
            # Fit lazily on the texts themselves if no corpus was provided.
            self.fit(texts)
        matrix = self._vectorizer.transform(texts)
        dense = matrix.toarray().astype(np.float32)
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return dense / norms

    # -- public API ----------------------------------------------------------
    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 1), dtype=np.float32)
        if self.backend == "transformer":
            return self._encode_transformer(texts)
        return self._encode_tfidf(texts)

    def similarity_matrix(self, queries: np.ndarray, keys: np.ndarray) -> np.ndarray:
        """Cosine similarity between two sets of (already normalised) vectors."""
        if queries.size == 0 or keys.size == 0:
            return np.zeros((queries.shape[0], keys.shape[0]), dtype=np.float32)
        return queries @ keys.T

    def similarity(self, text_a: str, text_b: str) -> float:
        emb = self.encode([text_a, text_b])
        return float(np.dot(emb[0], emb[1]))


_default_engine: NLPEngine | None = None


def get_default_engine() -> NLPEngine:
    """Return a process-wide engine configured from settings."""
    global _default_engine
    if _default_engine is None:
        from ..config import get_settings

        settings = get_settings()
        _default_engine = NLPEngine(
            backend=settings.nlp_backend, model_name=settings.nlp_model_name
        )
    return _default_engine
