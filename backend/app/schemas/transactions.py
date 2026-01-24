from typing import Dict, Any

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    """
    Request schema for scoring a single credit card transaction.

    This is intentionally generic; individual features (V1–V28, Amount, Time, etc.)
    will be validated more strictly once preprocessing is finalized.
    """

    features: Dict[str, Any] = Field(
        ...,
        description="Dictionary of feature_name -> value for a single transaction.",
    )


class PredictionResponse(BaseModel):
    """Response schema for transaction fraud prediction."""

    score: float = Field(..., description="Model or ensemble fraud score (higher = more likely fraud).")
    is_fraud: bool = Field(..., description="Binary decision based on the current threshold.")
    details: str | None = Field(
        None,
        description="Optional human-readable explanation or status message.",
    )