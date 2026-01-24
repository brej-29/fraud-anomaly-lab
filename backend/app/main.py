from fastapi import FastAPI

from .api.routes import router as api_router
from .core.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()
    app = FastAPI(title="Fraud Anomaly Lab API", version="0.1.0")

    @app.get("/health", tags=["health"])
    def health() -> dict:
        """Simple health check endpoint."""
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()