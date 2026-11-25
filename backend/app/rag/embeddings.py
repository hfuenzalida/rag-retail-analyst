"""Embedding generation with optional Ollama/OpenAI-compatible endpoint."""

import hashlib
import math
from functools import lru_cache

import httpx

from app.core.config import Settings, get_settings

EMBEDDING_DIMENSIONS = 384


def deterministic_embed(text: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """Deterministic local fallback embedding for dev/test without an LLM runtime."""
    values: list[float] = []
    counter = 0
    while len(values) < dimensions:
        digest = hashlib.sha256(f"{text}:{counter}".encode()).digest()
        for byte in digest:
            values.append((byte / 127.5) - 1.0)
            if len(values) >= dimensions:
                break
        counter += 1
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def _embed_via_http(text: str, url: str) -> list[float]:
    endpoint = url.rstrip("/") + "/embeddings"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(endpoint, json={"input": text, "model": "nomic-embed-text"})
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


def embed_text(text: str, settings: Settings | None = None) -> list[float]:
    cfg = settings or get_settings()
    if cfg.local_llm_embeddings_url:
        try:
            return _embed_via_http(text, cfg.local_llm_embeddings_url)
        except Exception:
            pass
    return deterministic_embed(text)


@lru_cache(maxsize=256)
def embed_text_cached(text: str) -> list[float]:
    return embed_text(text)
