from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator


class Transaction(BaseModel):
    """
    Schema for a single credit card transaction.

    The fields mirror the Kaggle credit card fraud dataset: `Time`, `Amount`,
    and PCA components `V1`–`V28`.
    """

    Time: float = Field(..., description="Seconds since the first transaction in the dataset.")
    Amount: float = Field(..., description="Transaction amount.")

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    class Config:
        extra = "forbid"


class ModelScore(BaseModel):
    score: float = Field(..., description="Anomaly score (higher = more anomalous).")
    threshold: Optional[float] = Field(
        None,
        description="Decision threshold used for this model, if available.",
    )
    is_fraud: Optional[bool] = Field(
        None,
        description="Binary decision for this model based on the threshold, if available.",
    )


class EnsembleSummary(BaseModel):
    score: float = Field(..., description="Ensemble anomaly score (higher = more anomalous).")
    threshold: Optional[float] = Field(
        None,
        description="Threshold used by the ensemble decision rule.",
    )
    is_fraud: bool = Field(..., description="Final ensemble decision (True = flagged as fraud).")


class PredictionResponse(BaseModel):
    """
    Response schema for a single prediction.

    Includes per-model scores and flags plus an ensemble-level summary.
    """

    prediction_id: int = Field(
        ...,
        description="Identifier of the prediction record in the persistence layer.",
    )
    created_at: datetime = Field(..., description="Timestamp (UTC) when the prediction was created.")
    model_scores: Dict[str, ModelScore] = Field(
        ...,
        description="Per-model anomaly scores and decisions.",
    )
    ensemble: EnsembleSummary = Field(
        ...,
        description="Ensemble-level score and decision.",
    )


class BatchPredictionResult(BaseModel):
    prediction_id: int
    created_at: datetime
    model_scores: Dict[str, ModelScore]
    ensemble: EnsembleSummary


class BatchPredictionSummary(BaseModel):
    total_predictions: int = Field(..., description="Number of transactions scored in this batch.")
    ensemble_fraud_count: int = Field(
        ...,
        description="How many transactions the ensemble flagged as fraud.",
    )


class BatchPredictionResponse(BaseModel):
    results: List[BatchPredictionResult]
    summary: BatchPredictionSummary


class BatchPredictionRequest(BaseModel):
    """
    Request schema for batch prediction.

    Clients can either provide:
    - `transactions`: a list of fully-typed Transaction objects, or
    - `rows`: a list of rows `[Time, Amount, V1, ..., V28]` in the correct order.

    Only one of `transactions` or `rows` may be provided.
    """

    transactions: Optional[List[Transaction]] = Field(
        None,
        description="List of transactions to score.",
    )
    rows: Optional[List[List[float]]] = Field(
        None,
        description="List of feature rows [Time, Amount, V1, ..., V28].",
    )

    @root_validator(skip_on_failure=True)
    def _check_input(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        tx, rows = values.get("transactions"), values.get("rows")
        if tx is None and rows is None:
            raise ValueError("Either 'transactions' or 'rows' must be provided.")
        if tx is not None and rows is not None:
            raise ValueError("Provide only one of 'transactions' or 'rows', not both.")
        return values


class FeedbackRequest(BaseModel):
    prediction_id: int = Field(..., description="Prediction id to attach feedback to.")
    label: str = Field(
        ...,
        description="Label for the prediction, e.g. 'fraud' or 'not_fraud'.",
    )
    notes: Optional[str] = Field(
        None,
        description="Optional free-text notes about the feedback.",
    )