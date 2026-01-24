from fastapi import APIRouter, HTTPException, status

from ..schemas.transactions import TransactionRequest, PredictionResponse

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict:
    """Health endpoint exposed under /api/health for internal checks."""
    return {"status": "ok", "component": "api"}


@router.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(request: TransactionRequest) -> PredictionResponse:
    """
    Placeholder prediction endpoint.

    This will be wired to the real model ensemble in future steps.
    """
    # For now, we raise a simple 501 with structured response.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Prediction endpoint is not implemented yet.",
    )