"""Cloud LLM client with payload sanitization."""

import re

import httpx

from app.core.config import Settings, get_settings

EMAIL_PATTERN = re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b")
PHONE_PATTERN = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")


def sanitize_text(text: str) -> str:
    """Remove obvious PII patterns before any cloud transmission."""
    cleaned = EMAIL_PATTERN.sub("[email-redacted]", text)
    cleaned = PHONE_PATTERN.sub("[phone-redacted]", cleaned)
    for token in ("customer", "salary", "patient", "ssn"):
        cleaned = re.sub(rf"\b{token}\b", "[redacted]", cleaned, flags=re.IGNORECASE)
    return cleaned


def sanitize_summary_payload(question: str, summary: str) -> dict:
    return {
        "question": sanitize_text(question),
        "summary": sanitize_text(summary),
    }


class CloudLLMClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _provider_config(self) -> tuple[str, str] | None:
        cfg = self.settings
        if cfg.enable_openai and cfg.openai_api_key:
            return ("https://api.openai.com/v1", cfg.openai_api_key.get_secret_value())
        if cfg.enable_anthropic and cfg.anthropic_api_key:
            return ("https://api.anthropic.com/v1", cfg.anthropic_api_key.get_secret_value())
        return None

    @property
    def is_configured(self) -> bool:
        return self._provider_config() is not None

    def chat(self, prompt: str) -> str:
        provider = self._provider_config()
        if not provider:
            raise RuntimeError("No cloud LLM provider configured.")

        base_url, api_key = provider
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()


def cloud_polish_summary(question: str, draft_summary: str, settings: Settings | None = None) -> str:
    client = CloudLLMClient(settings)
    if not client.is_configured:
        return draft_summary
    payload = sanitize_summary_payload(question, draft_summary)
    prompt = (
        "Rewrite this grounded retail analytics summary clearly. "
        "Do not add numbers or facts.\n\n"
        f"Question: {payload['question']}\nSummary: {payload['summary']}"
    )
    try:
        return client.chat(prompt)
    except Exception:
        return draft_summary
