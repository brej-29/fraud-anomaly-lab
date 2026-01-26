from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

import numpy as np

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


class ScoreEnsemble:
    """
    Score-based ensemble for anomaly detection models.

    The ensemble combines per-model anomaly scores into a single score by:

    - Normalizing each model's scores using min–max parameters estimated on the
      training data (if available).
    - Averaging the normalized scores across all base models.

    If normalization parameters are missing (e.g. older artifacts), the ensemble
    falls back to averaging raw scores.
    """

    def __init__(
        self,
        base_models: Sequence[str],
        normalization_params: Mapping[str, Dict[str, float]] | None = None,
        method: str = "min_max",
    ) -> None:
        self.base_models = list(base_models)
        self.normalization_params = dict(normalization_params or {})
        self.method = method
        # If we have no normalization parameters or an unsupported method, fall back to raw scores.
        self._use_raw_scores = not self.normalization_params or self.method != "min_max"

        log_info(
            "Initialized ScoreEnsemble with base_models=%s, method=%s, use_raw_scores=%s",
            ", ".join(self.base_models),
            self.method,
            self._use_raw_scores,
        )

    def _normalize_min_max(self, name: str, scores: np.ndarray) -> np.ndarray:
        """
        Normalize scores for a single model using min–max statistics from training.

        If statistics are missing or degenerate, raw scores are returned.
        """
        params = self.normalization_params.get(name)
        if not params:
            return scores.astype("float32")

        score_min = params.get("score_min_train")
        score_max = params.get("score_max_train")
        if score_min is None or score_max is None:
            return scores.astype("float32")

        score_min_f = float(score_min)
        score_max_f = float(score_max)

        if np.isclose(score_min_f, score_max_f):
            # Degenerate case: model produced nearly constant scores during training.
            # Return zeros so this model does not dominate the ensemble.
            return np.zeros_like(scores, dtype="float32")

        normalized = (scores - score_min_f) / (score_max_f - score_min_f)
        return normalized.astype("float32")

    def combine(self, per_model_scores: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Combine per-model score vectors into a single ensemble score vector.

        Parameters
        ----------
        per_model_scores:
            Mapping from model name to 1D array of anomaly scores.

        Returns
        -------
        1D numpy array of ensemble scores.
        """
        aggregated: List[np.ndarray] = []

        for name in self.base_models:
            if name not in per_model_scores:
                log_info("ScoreEnsemble: missing scores for model '%s'; skipping.", name)
                continue

            scores = np.asarray(per_model_scores[name], dtype="float32").reshape(-1)
            if self._use_raw_scores:
                normalized = scores
            elif self.method == "min_max":
                normalized = self._normalize_min_max(name, scores)
            else:
                # Unknown method: fall back to raw scores for safety.
                normalized = scores

            aggregated.append(normalized)

        if not aggregated:
            raise ValueError("ScoreEnsemble.combine called with no matching model scores.")

        stacked = np.vstack(aggregated)
        # Average across models (axis 0 = models, axis 1 = samples).
        return stacked.mean(axis=0)