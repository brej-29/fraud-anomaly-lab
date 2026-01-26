from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from fastapi import APIRouter, HTTPException, Request, status

from shared.drift import compute_psi
from ..schemas.transactions import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    FeedbackRequest,
    PredictionResponse,
    Transaction,
)
from ..services.model_registry import ModelRegistry
from ..services.scorer import Scorer
from ..services.storage import get_recent_ensemble_scores, get_recent_predictions

router = APIRouter()


def _get_registry(request: Request) -> ModelRegistry:
    registry = getattr(request.app.state, "model_registry", None)
    if registry is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model registry is not initialized.",
        )
    return registry


def _get_scorer(request: Request) -> Scorer:
    scorer = getattr(request.app.state, "scorer", None)
    if scorer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scoring service is not initialized.",
        )
    return scorer


@router.get("/health", tags=["health"])
def health(request: Request) -> dict:
    """Health endpoint exposed under /health and /api/health for internal checks."""
    registry = getattr(request.app.state, "model_registry", None)
    loaded_models = registry.loaded_models_count if registry is not None else 0
    return {"status": "ok", "component": "api", "loaded_models": loaded_models}


@router.get("/models", tags=["models"])
def list_models(request: Request) -> dict:
    """
    List available models and thresholds.

    Useful for debugging and for the dashboard to introspect the current
    scoring configuration.
    """
    registry = _get_registry(request)
    models_meta = registry.metadata.get("models", {})
    return {
        "artifacts_dir": str(registry.artifacts_dir),
        "models": models_meta,
        "thresholds": registry.thresholds,
    }


@router.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(transaction: Transaction, request: Request) -> PredictionResponse:
    """
    Score a single transaction using the anomaly ensemble.
    """
    scorer = _get_scorer(request)
    try:
        result = scorer.score_transaction(transaction.dict())
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return PredictionResponse(**result)


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    tags=["prediction"],
)
def predict_batch(payload: BatchPredictionRequest, request: Request) -> BatchPredictionResponse:
    """
    Score a batch of transactions.

    Clients can send either a list of Transaction objects or raw rows
    `[Time, Amount, V1, ..., V28]` in the correct order.
    """
    registry = _get_registry(request)
    scorer = _get_scorer(request)

    rows: List[Dict[str, Any]] = []
    if payload.transactions is not None:
        rows = [tx.dict() for tx in payload.transactions]
    elif payload.rows is not None:
        feature_columns = registry.feature_columns
        if not feature_columns:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Feature columns not available in metadata.",
            )
        expected_len = len(feature_columns)
        for idx, row in enumerate(payload.rows):
            if len(row) != expected_len:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Row {idx} has {len(row)} values but {expected_len} are required.",
                )
            rows.append({col: val for col, val in zip(feature_columns, row)})

    if not rows:
        return BatchPredictionResponse(
            results=[],
            summary={
                "total_predictions": 0,
                "ensemble_fraud_count": 0,
            },
        )

    try:
        batch_results = scorer.score_batch(rows)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    ensemble_fraud_count = sum(
        1 for r in batch_results if r["ensemble"]["is_fraud"]
    )

    return BatchPredictionResponse(
        results=[
            {
                "prediction_id": r["prediction_id"],
                "created_at": r["created_at"],
                "model_scores": r["model_scores"],
                "ensemble": r["ensemble"],
            }
            for r in batch_results
        ],
        summary={
            "total_predictions": len(batch_results),
            "ensemble_fraud_count": ensemble_fraud_count,
        },
    )


@router.get("/monitor/recent", tags=["monitoring"])
def recent_predictions(limit: int = 100) -> dict:
    """
    Return recent prediction records for monitoring and debugging.
    """
    records = get_recent_predictions(limit=limit)
    return {
        "limit": limit,
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "created_at": r.created_at,
                "ensemble_score": r.ensemble_score,
                "final_flag": r.final_flag,
            }
            for r in records
        ],
    }


@router.post("/feedback", tags=["feedback"])
def submit_feedback(payload: FeedbackRequest) -> dict:
    """
    Record user feedback for a given prediction id.

    This endpoint accepts labels such as "fraud" / "not_fraud" and optional notes.
    """
    from ..services.storage import insert_feedback  # Local import to avoid cycles.

    feedback_id = insert_feedback(
        prediction_id=payload.prediction_id,
        label=payload.label,
        notes=payload.notes,
    )
    return {"feedback_id": feedback_id}


@router.get("/drift", tags=["monitoring"])
def drift(request: Request, window_size: int = 500) -> dict:
    """
    Compute a simple drift metric (PSI) for ensemble scores.

    Compares the score distribution of the most recent predictions against
    the validation-based baseline stored in `metadata.json`.
    """
    registry = _get_registry(request)
    ensemble_meta = registry.ensemble_config or {}
    baseline = ensemble_meta.get("baseline")
    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ensemble baseline histogram not available; rerun training.",
        )

    hist_meta = baseline.get("histogram", {})
    bin_edges = hist_meta.get("bin_edges")
    baseline_counts = hist_meta.get("counts")
    if not bin_edges or not baseline_counts:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Baseline histogram is incomplete in metadata.",
        )

    recent_scores = get_recent_ensemble_scores(window_size=window_size)
    if not recent_scores:
        return {
            "window_size": window_size,
            "psi": 0.0,
            "drift_level": "none",
            "baseline_n_samples": baseline.get("n_samples"),
            "recent_n_samples": 0,
            "has_data": False,
            "message": "No recent predictions available; drift cannot be computed yet.",
        }

    hist_recent, _ = np.histogram(
        recent_scores,
        bins=np.asarray(bin_edges, dtype="float32"),
    )
    psi = compute_psi(baseline_counts, hist_recent)

    if psi < 0.1:
        drift_level = "low"
    elif psi < 0.25:
        drift_level = "medium"
    else:
        drift_level = "high"

    return {
        "window_size": window_size,
        "psi": psi,
        "drift_level": drift_level,
        "baseline_n_samples": baseline.get("n_samples"),
        "recent_n_samples": len(recent_scores),
        "has_data": True,
    }