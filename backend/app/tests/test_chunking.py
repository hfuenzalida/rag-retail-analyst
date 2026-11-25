"""Text chunking tests."""

from app.rag.chunking import chunk_text


def test_chunk_text_single_short():
    chunks = chunk_text("Hello world")
    assert len(chunks) == 1
    assert chunks[0].content == "Hello world"


def test_chunk_text_overlap():
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=400, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c.content) <= 400 for c in chunks)
