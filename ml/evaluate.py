from __future__ import annotations

from pathlib import Path
from typing import Dict

from shared.utils import log_info


def evaluate_models(artifacts_dir: Path | str | None = None) -> Dict[str, float]:
    """
    Placeholder evaluation routine for trained models.

    Parameters
    ----------
    artifacts_dir:
        Directory where model artifacts are stored.

    Returns
    -------
    Dictionary of placeholder metrics, to be replaced with real evaluation logic.
    """
    artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else Path("ml") / "artifacts"
    log_info(f"Evaluating models using artifacts from: {artifacts_dir}")

    # TODO: Load models, compute PR-AUC/ROC-AUC and thresholded metrics.
    metrics: Dict[str, float] = {}
    log_info("evaluate_models completed (no-op placeholder).")
    return metrics


def main() -> None:
    """CLI entrypoint to evaluate models."""
    evaluate_models()


if __name__ == "__main__":
    main()