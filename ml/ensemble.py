from __future__ import annotations

from typing import Any, Dict, List

from shared.utils import log_info


class EnsembleModel:
    """
    Placeholder ensemble model.

    This class will combine outputs from multiple base models (e.g., via averaging
    scores, stacking, or rules) to produce a final fraud score and decision.
    """

    def __init__(self, model_names: List[str] | None = None) -> None:
        self.model_names = model_names or []
        log_info(f"Initialized EnsembleModel with models: {self.model_names}")

    def predict_score(self, features: Dict[str, Any]) -> float:
        """
        Compute a fraud score for a single transaction.

        Currently returns a constant placeholder value.
        """
        # TODO: Implement real ensemble scoring logic.
        return 0.0

    def predict_is_fraud(self, features: Dict[str, Any], threshold: float = 0.5) -> bool:
        """
        Convert a score into a binary fraud decision using a threshold.

        Parameters
        ----------
        features:
            Transaction features.
        threshold:
            Score threshold above which a transaction is flagged as fraud.
        """
        score = self.predict_score(features)
        return score >= threshold