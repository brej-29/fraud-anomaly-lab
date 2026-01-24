from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from shared.utils import log_info, set_global_seed

from .evaluate import choose_threshold, compute_metrics
from .models import (
    BaseAnomalyModel,
    COPODWrapper,
    IsolationForestWrapper,
    LOFWrapper,
    OneClassSVMWrapper,
)
from .preprocess import prepare_data

ARTIFACTS_DIR = Path("ml") / "artifacts"
RAW_DATA_PATH = Path("data") / "raw" / "creditcard.csv"
PROCESSED_DIR = Path("data") / "processed"


def _build_models() -> Dict[str, BaseAnomalyModel]:
    """Instantiate the anomaly detection models used in this step."""
    models: Dict[str, BaseAnomalyModel] = {
        "isolation_forest": IsolationForestWrapper(
            n_estimators=200,
            max_samples="auto",
            contamination="auto",
            random_state=42,
        ),
        "lof": LOFWrapper(
            n_neighbors=20,
            novelty=True,
        ),
        "one_class_svm": OneClassSVMWrapper(
            kernel="rbf",
            gamma="scale",
            nu=0.01,
        ),
        "copod": COPODWrapper(),
    }
    return models


def _save_preprocessor(preprocessor: Any, path: Path) -> None:
    """Persist the fitted preprocessor to disk with basic error handling."""
    try:
        joblib.dump(preprocessor, path)
        log_info("Saved preprocessor to %s", path)
    except Exception as exc:  # noqa: BLE001 - log and continue
        log_info(f"Failed to save preprocessor to {path}: {exc}")


def _save_metadata(metadata: Dict[str, Any], path: Path) -> None:
    """Persist training metadata to JSON."""
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        log_info("Saved metadata to %s", path)
    except Exception as exc:  # noqa: BLE001 - log and continue
        log_info(f"Failed to save metadata to {path}: {exc}")


def _save_thresholds(thresholds: Dict[str, float], path: Path) -> None:
    """Persist per-model thresholds to JSON."""
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(thresholds, f, indent=2)
        log_info("Saved thresholds to %s", path)
    except Exception as exc:  # noqa: BLE001 - log and continue
        log_info(f"Failed to save thresholds to {path}: {exc}")


def train_all_models() -> None:
    """
    Train and evaluate anomaly detection models.

    Pipeline:
    - Load and preprocess data (time-based split, scaling).
    - Fit models on normal-only training data.
    - Calibrate thresholds on validation scores using precision/recall constraints.
    - Evaluate on test set.
    - Persist models, preprocessor, thresholds, and metadata under ml/artifacts/.
    """
    if not RAW_DATA_PATH.exists():
        log_info(
            f"Raw data not found at {RAW_DATA_PATH}. "
            "Run `make download-data` or see scripts/kaggle_setup.md."
        )
        return

    set_global_seed(42)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    log_info("Starting training for anomaly detection models.")

    split_data, preprocessor, metadata = prepare_data(
        RAW_DATA_PATH, processed_dir=PROCESSED_DIR, force=False
    )

    if split_data.X_train_normal.shape[0] == 0:
        log_info("No normal samples found in training data; cannot train anomaly models.")
        return

    models = _build_models()
    thresholds: Dict[str, float] = {}
    models_summary: Dict[str, Any] = {}

    for name, model in models.items():
        log_info("Training model: %s", name)
        model.fit(split_data.X_train_normal)

        scores_val = model.score_samples(split_data.X_val)
        scores_test = model.score_samples(split_data.X_test)

        calibration = choose_threshold(scores_val, split_data.y_val)
        threshold = float(calibration["threshold"])
        thresholds[name] = threshold

        y_val_pred = (scores_val >= threshold).astype(int)
        y_test_pred = (scores_test >= threshold).astype(int)

        metrics_val = calibration["metrics"]
        metrics_test = compute_metrics(split_data.y_test, y_test_pred, scores_test)

        # Attempt to extract hyperparameters from underlying estimator if available.
        try:
            params = model.get_params()
        except Exception:  # noqa: BLE001
            params = {}

        models_summary[name] = {
            "type": model.__class__.__name__,
            "hyperparameters": params,
            "threshold": threshold,
            "constraints_met": calibration["constraints_met"],
            "metrics": {
                "val": metrics_val,
                "test": metrics_test,
            },
        }

        model_path = ARTIFACTS_DIR / f"{name}.joblib"
        model.save(model_path)

    metadata_out: Dict[str, Any] = {
        "dataset": "mlg-ulb/creditcardfraud",
        "raw_path": str(RAW_DATA_PATH),
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "feature_columns": split_data.feature_columns,
        "splits": metadata.get("splits", {}),
        "n_rows": metadata.get("n_rows"),
        "n_fraud": metadata.get("n_fraud"),
        "models": models_summary,
    }

    _save_preprocessor(preprocessor, ARTIFACTS_DIR / "preprocessor.joblib")
    _save_thresholds(thresholds, ARTIFACTS_DIR / "thresholds.json")
    _save_metadata(metadata_out, ARTIFACTS_DIR / "metadata.json")

    log_info("Training complete for models: %s", ", ".join(models.keys()))
    log_info("Next step: run `make report` to generate the model comparison report.")
    log_info("Artifacts directory: %s", ARTIFACTS_DIR)


def main() -> None:
    """CLI entrypoint to trigger training for all models."""
    train_all_models()


if __name__ == "__main__":
    main()