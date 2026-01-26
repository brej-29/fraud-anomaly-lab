from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from ml.ensemble import ScoreEnsemble  # type: ignore[import]
from ..core.logging import get_logger
from ..core.metrics import METRICS
from .model_registry import ModelRegistry
from .storage import insert_prediction

logger = get_logger(__name__)


class Scorer:
    """
    Scoring service that applies preprocessing, per-model anomaly scoring,
    and ensemble aggregation.

    It is intentionally thin: all heavy lifting (model loading, preprocessing,
    and persistence) is delegated to other components.
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()
        if not self.registry.metadata:
            # In case the scorer is used outside the FastAPI startup lifecycle.
            self.registry.load_all()
        self._ensemble = self._build_ensemble()
        logger.info("Scorer initialized with artifacts directory: %s", self.registry.artifacts_dir)

    def _build_ensemble(self) -> ScoreEnsemble | None:
        """
        Construct a ScoreEnsemble from registry metadata, if available.
        """
        ensemble_meta = self.registry.ensemble_config or {}
        models_meta = self.registry.metadata.get("models", {})

        if not ensemble_meta and not models_meta:
            logger.warning("No ensemble configuration found in metadata; ensemble is disabled.")
            return None

        base_models = ensemble_meta.get("base_models")
        if not base_models:
            # Fall back to all models we have thresholds for, excluding the ensemble itself.
            base_models = [name for name in self.registry.thresholds.keys() if name != "ensemble"]

        normalization = ensemble_meta.get("normalization", {})
        per_model_norm = normalization.get("per_model") or {}

        # If per-model normalization is missing (e.g. older artifacts), we degrade gracefully
        # by constructing an empty ScoreEnsemble that will use raw scores.
        ensemble = ScoreEnsemble(
            base_models=base_models,
            normalization_params=per_model_norm,
            method="min_max",
        )
        logger.info("ScoreEnsemble configured with base_models=%s", ", ".join(base_models))
        return ensemble

    def _ensure_ready(self) -> None:
        if self.registry.preprocessor is None or not self.registry.loaded_models_count:
            raise RuntimeError(
                "Model artifacts not available. "
                "Run the training pipeline (`make train-all`) and restart the API."
            )

    def _get_feature_columns(self) -> List[str]:
        cols = self.registry.feature_columns
        if not cols:
            raise RuntimeError("Feature columns not found in metadata; cannot build feature vector.")
        return cols

    def _build_feature_matrix(self, rows: List[Dict[str, Any]]) -> np.ndarray:
        feature_columns = self._get_feature_columns()
        matrix: List[List[float]] = []
        for row in rows:
            try:
                values = [float(row[col]) for col in feature_columns]
            except KeyError as exc:  # noqa: BLE001
                missing = str(exc)
                raise ValueError(f"Missing required feature {missing!r} in payload.") from exc
            matrix.append(values)
        return np.asarray(matrix, dtype="float32")

    def _compute_input_hash(self, features: Dict[str, Any]) -> str:
        feature_columns = self._get_feature_columns()
        ordered_payload = {col: features.get(col) for col in feature_columns}
        payload_json = json.dumps(ordered_payload, sort_keys=True)
        return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    def score_transaction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single transaction.

        Parameters
        ----------
        features:
            Dictionary of feature values for a single transaction.

        Returns
        -------
        A dictionary matching `PredictionResponse` (see schemas.transactions).
        """
        self._ensure_ready()

        X_raw = self._build_feature_matrix([features])
        assert X_raw.shape[0] == 1
        X = self.registry.preprocessor.transform(X_raw)

        per_model_scores: Dict[str, np.ndarray] = {}
        model_scores_for_response: Dict[str, Dict[str, Any]] = {}

        # Per-model scores and decisions.
        for name, model in self.registry._models.items():  # type: ignore[attr-defined]
            scores = np.asarray(model.score_samples(X), dtype="float32")
            if scores.shape[0] != 1:
                raise RuntimeError(f"Model '{name}' returned scores of unexpected shape {scores.shape}.")

            raw_score = float(scores[0])
            threshold = self.registry.thresholds.get(name)
            is_fraud = bool(raw_score >= float(threshold)) if threshold is not None else None

            per_model_scores[name] = scores
            model_scores_for_response[name] = {
                "score": raw_score,
                "threshold": float(threshold) if threshold is not None else None,
                "is_fraud": is_fraud,
            }

        # Ensemble aggregation.
        if self._ensemble is not None:
            ensemble_scores = self._ensemble.combine(per_model_scores)
            ensemble_score = float(ensemble_scores[0])
        else:
            ensemble_score = float(
                np.mean([m["score"] for m in model_scores_for_response.values()])
            )

        ensemble_threshold = self.registry.thresholds.get("ensemble")
        ensemble_is_fraud = (
            bool(ensemble_score >= float(ensemble_threshold))
            if ensemble_threshold is not None
            else False
        )

        created_at_dt = datetime.utcnow()
        created_at_iso = created_at_dt.isoformat() + "Z"
        input_hash = self._compute_input_hash(features)

        # Persist prediction.
        prediction_payload_for_db = {
            name: {
                "score": data["score"],
                "threshold": data["threshold"],
                "is_fraud": data["is_fraud"],
            }
            for name, data in model_scores_for_response.items()
        }
        prediction_id = insert_prediction(
            input_hash=input_hash,
            model_scores=prediction_payload_for_db,
            ensemble_score=ensemble_score,
            final_flag=ensemble_is_fraud,
            created_at=created_at_iso,
        )

        # Update in-memory metrics.
        METRICS.record_prediction(n_transactions=1, n_flagged_ensemble=int(ensemble_is_fraud))

        return {
            "prediction_id": prediction_id,
            "created_at": created_at_dt,
            "model_scores": model_scores_for_response,
            "ensemble": {
                "score": ensemble_score,
                "threshold": float(ensemble_threshold) if ensemble_threshold is not None else None,
                "is_fraud": ensemble_is_fraud,
            },
        }

    def score_batch(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score a batch of transactions.

        Parameters
        ----------
        rows:
            List of transactions, each as a mapping from feature name to value.

        Returns
        -------
        List of dictionaries, each matching the single-transaction response payload.
        """
        if not rows:
            return []

        self._ensure_ready()

        X_raw = self._build_feature_matrix(rows)
        X = self.registry.preprocessor.transform(X_raw)

        n = X.shape[0]
        per_model_scores: Dict[str, np.ndarray] = {}
        for name, model in self.registry._models.items():  # type: ignore[attr-defined]
            scores = np.asarray(model.score_samples(X), dtype="float32")
            if scores.shape[0] != n:
                raise RuntimeError(
                    f"Model '{name}' returned scores of unexpected shape {scores.shape}; expected {n}."
                )
            per_model_scores[name] = scores

        if self._ensemble is not None:
            ensemble_scores = self._ensemble.combine(per_model_scores)
        else:
            stacked = np.vstack(list(per_model_scores.values()))
            ensemble_scores = stacked.mean(axis=0)

        ensemble_threshold = self.registry.thresholds.get("ensemble")
        created_at_dt = datetime.utcnow()
        created_at_iso = created_at_dt.isoformat() + "Z"

        results: List[Dict[str, Any]] = []
        ensemble_fraud_count = 0

        # Iterate over rows and persist each prediction.
        for idx, features in enumerate(rows):
            per_model_for_row: Dict[str, Dict[str, Any]] = {}
            for name, scores in per_model_scores.items():
                raw_score = float(scores[idx])
                threshold = self.registry.thresholds.get(name)
                is_fraud = bool(raw_score >= float(threshold)) if threshold is not None else None
                per_model_for_row[name] = {
                    "score": raw_score,
                    "threshold": float(threshold) if threshold is not None else None,
                    "is_fraud": is_fraud,
                }

            ensemble_score = float(ensemble_scores[idx])
            ensemble_is_fraud = (
                bool(ensemble_score >= float(ensemble_threshold))
                if ensemble_threshold is not None
                else False
            )
            if ensemble_is_fraud:
                ensemble_fraud_count += 1

            input_hash = self._compute_input_hash(features)
            prediction_id = insert_prediction(
                input_hash=input_hash,
                model_scores=per_model_for_row,
                ensemble_score=ensemble_score,
                final_flag=ensemble_is_fraud,
                created_at=created_at_iso,
            )

            results.append(
                {
                    "prediction_id": prediction_id,
                    "created_at": created_at_dt,
                    "model_scores": per_model_for_row,
                    "ensemble": {
                        "score": ensemble_score,
                        "threshold": float(ensemble_threshold)
                        if ensemble_threshold is not None
                        else None,
                        "is_fraud": ensemble_is_fraud,
                    },
                }
            )

        # Single metrics record for the whole batch request.
        METRICS.record_prediction(
            n_transactions=len(rows),
            n_flagged_ensemble=ensemble_fraud_count,
        )

        return results