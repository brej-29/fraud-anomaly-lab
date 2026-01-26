from __future__ import annotations

import os

from fastapi import FastAPI

from .api.routes import router as api_router
from .core.logging import configure_logging
from .core.middleware import MetricsMiddleware, RequestIdMiddleware
from .core.metrics import METRICS
from .services.model_registry import ModelRegistry
from .services.scorer import Scorer
from .services.storage import init_db


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()

    root_path = os.getenv("ROOT_PATH", "")
    app = FastAPI(title="Fraud Anomaly Lab API", version="0.1.0", root_path=root_path)

    # Middleware for request id propagation and basic metrics.
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(MetricsMiddleware)

    @app.on_event("startup")
    async def _startup() -> None:
        """
        Application startup hook.

        - Load model artifacts via the model registry.
        - Initialize the SQLite database for prediction storage.
        """
        registry = ModelRegistry()
        registry.load_all()
        app.state.model_registry = registry
        app.state.scorer = Scorer(registry=registry)
        init_db()

    @app.get("/", tags=["root"])
    async def root() -> dict:
        """
        Simple welcome route with a pointer to API docs.

        When deployed on Hugging Face Spaces, the API should be accessed via the
        Space's `*.hf.space` URL rather than the `huggingface.co/spaces/...` path
        to avoid proxy-related 404s.
        """
        docs_url = app.docs_url or "/docs"
        return {
            "message": "Fraud Anomaly Lab API. See the interactive docs at the URL below.",
            "docs_url": docs_url,
            "version": app.version,
        }

    @app.get("/metrics", tags=["metrics"])
    async def metrics() -> dict:
        """Expose lightweight in-memory metrics for observability."""
        return METRICS.snapshot()

    # Include the main API router both at the root and under /api for backward compatibility.
    app.include_router(api_router)
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()