"""Cloud LLM client and sanitization tests."""

from unittest.mock import MagicMock, patch

from app.llm.cloud_client import CloudLLMClient, cloud_polish_summary, sanitize_text
from app.tools.routing_tools import route_to_cloud_llm, sanitize_for_cloud


def test_sanitize_text_redacts_email_and_phone():
    text = "Contact john@example.com or 555-123-4567 for salary info"
    cleaned = sanitize_text(text)
    assert "john@example.com" not in cleaned
    assert "555-123-4567" not in cleaned
    assert "[email-redacted]" in cleaned


def test_sanitize_for_cloud_wrapper():
    assert "[redacted]" in sanitize_for_cloud("customer salary export").lower()


def test_cloud_polish_falls_back_when_unconfigured():
    summary = cloud_polish_summary("Revenue?", "Draft summary.")
    assert summary == "Draft summary."


@patch("app.llm.cloud_client.httpx.Client")
def test_cloud_client_chat(mock_client_cls):
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "Polished summary"}}]}
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client.post.return_value = mock_response
    mock_client_cls.return_value = mock_client

    from app.core.config import Settings

    settings = Settings(enable_openai=True, openai_api_key="test-key")
    client = CloudLLMClient(settings)
    assert client.is_configured
    result = client.chat("Rewrite this summary")
    assert result == "Polished summary"


@patch("app.llm.cloud_client.CloudLLMClient")
def test_route_to_cloud_llm(mock_client_cls):
    instance = MagicMock()
    instance.chat.return_value = "cloud response"
    mock_client_cls.return_value = instance

    from app.core.config import Settings

    result = route_to_cloud_llm("Summarize", {"q": "revenue"}, Settings(enable_openai=True, openai_api_key="k"))
    assert result == "cloud response"
