"""Local LLM client tests."""

from unittest.mock import MagicMock, patch

from app.llm.client import LocalLLMClient, LLMMessage, polish_summary


def test_local_llm_not_configured():
    client = LocalLLMClient(settings=MagicMock(local_llm_chat_url=None))
    assert not client.is_configured


@patch("app.llm.client.httpx.Client")
def test_local_llm_chat(mock_client_cls):
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "Polished answer"}}]}
    mock_response.raise_for_status.return_value = None
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client.post.return_value = mock_response
    mock_client_cls.return_value = mock_client

    settings = MagicMock(local_llm_chat_url="http://localhost:11434/v1")
    client = LocalLLMClient(settings=settings)
    result = client.chat([LLMMessage(role="user", content="Hello")])
    assert result == "Polished answer"


def test_polish_summary_fallback_without_llm():
    settings = MagicMock(local_llm_chat_url=None)
    draft = "total revenue: 1640 currency."
    assert polish_summary("revenue?", draft, settings) == draft
