"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, controls, eval, ingest, query
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.runtime_controls import ingest_allowed
from app.db.connection import get_connection
from app.models.query_models import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.app_base_url, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(query.router, prefix="/query", tags=["query"])
    app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
    app.include_router(eval.router, prefix="/eval", tags=["eval"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(controls.router, prefix="/controls", tags=["controls"])

    @app.get("/healthz", response_model=HealthResponse, tags=["health"])
    async def healthz() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app_env=settings.app_env,
            app_name=settings.app_name,
            read_only=settings.read_only,
            ingest_enabled=ingest_allowed(settings),
        )

    @app.get("/healthz/ready", tags=["health"])
    async def healthz_ready() -> dict:
        if settings.app_env in ("production", "staging", "preview"):
            try:
                with get_connection(settings) as conn:
                    conn.execute("SELECT 1")
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database not ready",
                ) from exc
        return {"status": "ready", "app_env": settings.app_env}

    return app


app = create_app()
