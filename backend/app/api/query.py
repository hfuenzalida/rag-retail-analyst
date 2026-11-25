"""Query API — primary analytical entry point."""

from fastapi import APIRouter, HTTPException, status

from app.agents.rag_analyst import run_analyst_query
from app.core.tenant import TenantAccessError
from app.models.query_models import QueryRequest, QueryResponse

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def ask(request: QueryRequest) -> QueryResponse:
    try:
        return await run_analyst_query(request)
    except TenantAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
