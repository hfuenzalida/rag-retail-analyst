"""Embedding helper tests."""

import math

from app.rag.embeddings import EMBEDDING_DIMENSIONS, deterministic_embed, embed_text


def test_deterministic_embed_dimensions():
    vec = deterministic_embed("total revenue metric")
    assert len(vec) == EMBEDDING_DIMENSIONS


def test_deterministic_embed_normalized():
    vec = deterministic_embed("inventory schema")
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 1e-5


def test_embed_text_stable():
    assert embed_text("sales table") == embed_text("sales table")
