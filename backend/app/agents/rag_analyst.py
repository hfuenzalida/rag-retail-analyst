"""RAG Analyst agent entry point."""

from pathlib import Path

import yaml

from app.agents.routing_agent import evaluate_routing
from app.core.rollout import is_feature_available_for_role
from app.core.runtime_controls import is_feature_enabled, is_kill_switch_active
from app.core.tenant import validate_tenant_access
from app.models.query_models import QueryRequest, QueryResponse
from app.services.query_pipeline import execute_query

PROMPT_PATH = Path(__file__).parent / "prompts" / "rag_analyst.yaml"
STABLE_PROMPT = "You are a grounded retail data analyst. Answer only from tool outputs."


def load_system_prompt(request: QueryRequest | None = None) -> str:
    use_new = is_feature_enabled("new_prompts", default=False)
    if request and not is_feature_available_for_role("new_prompts", request.role):
        use_new = False
    if is_kill_switch_active("new_prompts"):
        use_new = False

    if not use_new or not PROMPT_PATH.exists():
        return STABLE_PROMPT
    data = yaml.safe_load(PROMPT_PATH.read_text(encoding="utf-8"))
    return data.get("system_prompt", STABLE_PROMPT)


async def run_analyst_query(request: QueryRequest) -> QueryResponse:
    """
    Main analyst flow:
    1. Tenant validation (production)
    2. Routing / sensitivity evaluation
    3. Grounded tool execution via query pipeline
    4. Tiered LLM summary polish with fallbacks
    """
    validate_tenant_access(request.client_id, request.role)
    load_system_prompt(request)
    evaluate_routing(request)
    return execute_query(request, use_llm_polish=True)
