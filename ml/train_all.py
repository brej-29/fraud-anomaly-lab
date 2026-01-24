from __future__ import annotations

from pathlib import Path

from shared.utils import log_info

from .preprocess import preprocess


ARTIFACTS_DIR = Path("ml") / "artifacts"
RAW_DATA_PATH = Path("data") / "raw" / "creditcard.csv"


def train_all_models() -> None:
    """
    Placeholder training orchestrator for all models.

    This function will eventually:
    - Load and preprocess data.
    - Train six anomaly detection / classification models.
    - Persist model artifacts and metadata under ml/artifacts/.
    """
    if not RAW_DATA_PATH.exists():
        log_info(
            f"Raw data not found at {RAW_DATA_PATH}. "
            "Run `make download-data` or see scripts/kaggle_setup.md."
        )
        return

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    log_info("Starting placeholder training for all models.")

    split_data, metadata = preprocess(RAW_DATA_PATH)
    log_info(
        "Training is not yet implemented. "
        f"Loaded {metadata['n_rows']} rows with {metadata['n_fraud']} fraud cases."
    )

    # TODO: Implement actual training and artifact persistence.
    log_info("train_all_models completed (no-op placeholder).")


def main() -> None:
    """CLI entrypoint to trigger training for all models."""
    train_all_models()


if __name__ == "__main__":
    main()