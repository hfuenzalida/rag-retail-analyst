"""OpenAI-compatible local LLM client (Ollama / vLLM)."""

from dataclasses import dataclass

import httpx

from app.core.config import Settings, get_settings


@dataclass
class LLMMessage:
    role: str
    content: str


class LocalLLMClient:
    """Calls a local OpenAI-compatible chat completions endpoint."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.base_url = (self.settings.local_llm_chat_url or "").rstrip("/")
        self.model = "llama3.2"

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url)

    def chat(self, messages: list[LLMMessage], temperature: float = 0.2) -> str:
        if not self.is_configured:
            raise RuntimeError("Local LLM endpoint is not configured (APP_LOCAL_LLM_CHAT_URL).")

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()


def polish_summary(question: str, draft_summary: str, settings: Settings | None = None) -> str:
    """Optionally refine a grounded summary via local LLM."""
    llm = LocalLLMClient(settings)
    if not llm.is_configured:
        return draft_summary

    prompt = (
        "Rewrite the following business analytics answer for clarity. "
        "Do NOT add new numbers or facts — only rephrase the draft.\n\n"
        f"Question: {question}\nDraft: {draft_summary}"
    )
    try:
        return llm.chat([LLMMessage(role="user", content=prompt)])
    except Exception:
        return draft_summary
