from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)

from shared.utils import log_info


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    scores: np.ndarray,
) -> Dict[str, Any]:
    """
    Compute standard binary classification and ranking metrics.

    Returns
    -------
    Dictionary containing roc_auc, pr_auc, precision, recall, f1, and confusion matrix entries.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    scores = np.asarray(scores)

    metrics: Dict[str, Any] = {}

    try:
        metrics["roc_auc"] = float(roc_auc_score(y_true, scores))
    except ValueError:
        metrics["roc_auc"] = None

    try:
        metrics["pr_auc"] = float(average_precision_score(y_true, scores))
    except ValueError:
        metrics["pr_auc"] = None

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    metrics["precision"] = float(precision)
    metrics["recall"] = float(recall)
    metrics["f1"] = float(f1)

    # Ensure a 2x2 confusion matrix even if a class is missing
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    metrics.update(
        {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        }
    )
    return metrics


def choose_threshold(
    scores_val: np.ndarray,
    y_val: np.ndarray,
    precision_target: float = 0.90,
    recall_target: float = 0.75,
    n_thresholds: int = 100,
) -> Dict[str, Any]:
    """
    Select a decision threshold based on validation scores and labels.

    Strategy:
    - Sweep thresholds across a grid between min and max validation scores.
    - Find thresholds that meet BOTH precision and recall targets.
    - Among those, select the one with the best F1.
    - If none meet constraints, select the threshold with the best F1 overall
      and mark constraints as not met.
    """
    scores = np.asarray(scores_val)
    y = np.asarray(y_val)

    if scores.size == 0:
        raise ValueError("Cannot choose threshold: scores array is empty.")

    score_min = float(scores.min())
    score_max = float(scores.max())

    if np.isclose(score_min, score_max):
        thresholds = np.array([score_min])
    else:
        thresholds = np.linspace(score_min, score_max, num=n_thresholds)

    best_threshold = thresholds[0]
    best_f1 = -1.0
    best_metrics: Dict[str, Any] | None = None
    best_constraints_met = False

    for thr in thresholds:
        y_pred = (scores >= thr).astype(int)
        metrics = compute_metrics(y, y_pred, scores)

        f1 = metrics["f1"]
        precision = metrics["precision"]
        recall = metrics["recall"]

        constraints_met = precision >= precision_target and recall >= recall_target

        if constraints_met:
            if not best_constraints_met or f1 > best_f1:
                best_threshold = float(thr)
                best_f1 = float(f1)
                best_metrics = metrics
                best_constraints_met = True
        else:
            if not best_constraints_met and f1 > best_f1:
                best_threshold = float(thr)
                best_f1 = float(f1)
                best_metrics = metrics

    if best_metrics is None:
        raise RuntimeError("Failed to compute metrics during threshold search.")

    return {
        "threshold": best_threshold,
        "constraints_met": best_constraints_met,
        "metrics": best_metrics,
        "precision_target": precision_target,
        "recall_target": recall_target,
    }


def evaluate_models(artifacts_dir: Path | str | None = None) -> Dict[str, Any]:
    """
    Load evaluation metadata for trained models.

    Parameters
    ----------
    artifacts_dir:
        Directory where model artifacts and metadata.json are stored.

    Returns
    -------
    Dictionary with per-model metadata and metrics, or empty dict if not available.
    """
    artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else Path("ml") / "artifacts"
    metadata_path = artifacts_dir / "metadata.json"
    if not metadata_path.exists():
        log_info("No metadata.json found at %s. Run training first.", metadata_path)
        return {}

    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    return metadata.get("models", {})


def generate_model_comparison_report(
    artifacts_dir: Path,
    report_path: Path,
) -> None:
    """
    Generate a markdown report comparing model performance.

    Reads metadata.json from artifacts_dir and writes a markdown table with
    validation and test metrics for each model.
    """
    metadata_path = artifacts_dir / "metadata.json"
    if not metadata_path.exists():
        log_info("Cannot generate report: %s does not exist.", metadata_path)
        return

    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    models = metadata.get("models", {})
    if not models:
        log_info("No model metrics found in metadata.json.")
        return

    lines: list[str] = []
    lines.append("# Model Comparison Report")
    lines.append("")
    lines.append("This report was generated from `ml/artifacts/metadata.json`.")
    lines.append("")
    lines.append("## 1. Overview")
    lines.append("")
    lines.append(f"- Dataset: Kaggle `mlg-ulb/creditcardfraud`")
    lines.append("- Objective: Detect fraudulent credit card transactions via anomaly detection.")
    lines.append(
        "- Metrics: PR-AUC (primary), ROC-AUC, and threshold-based precision, recall, and F1."
    )
    lines.append("")
    lines.append("## 2. Per-Model Metrics")
    lines.append("")
    header = (
        "| Model | Split | ROC-AUC | PR-AUC | Precision | Recall | F1 | "
        "Threshold | Constraints Met |"
    )
    separator = (
        "|---|---|---|---|---|---|---|---|---|"
    )
    lines.append(header)
    lines.append(separator)

    for model_name, info in models.items():
        threshold = info.get("threshold")
        constraints_met = info.get("constraints_met", False)
        for split_name in ("val", "test"):
            m = info.get("metrics", {}).get(split_name, {})
            lines.append(
                "| {model} | {split} | {roc_auc} | {pr_auc} | {precision} | {recall} | {f1} | "
                "{threshold} | {constraints_met} |".format(
                    model=model_name,
                    split=split_name,
                    roc_auc=_fmt_metric(m.get("roc_auc")),
                    pr_auc=_fmt_metric(m.get("pr_auc")),
                    precision=_fmt_metric(m.get("precision")),
                    recall=_fmt_metric(m.get("recall")),
                    f1=_fmt_metric(m.get("f1")),
                    threshold=_fmt_metric(threshold),
                    constraints_met="yes" if constraints_met else "no",
                )
            )

    lines.append("")
    lines.append("## 3. Notes")
    lines.append("")
    lines.append(
        "- Models are trained on **normal-only** transactions from the training split."
    )
    lines.append(
        "- Splits are **time-based** (train: early, val/test: later) to reduce leakage."
    )
    lines.append(
        "- Thresholds are calibrated on the validation set using precision and recall constraints."
    )
    lines.append("")
    lines.append("## 4. Best Model (Summary)")
    lines.append("")
    lines.append(
        "Refer to the table above to identify the model with the best balance of PR-AUC, recall, "
        "and precision on the validation and test sets."
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log_info("Model comparison report written to %s", report_path)


def _fmt_metric(value: Any) -> str:
    """Format numeric metrics for markdown output."""
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate trained models and generate reports.")
    parser.add_argument(
        "--artifacts",
        type=str,
        default="ml/artifacts",
        help="Directory containing model artifacts and metadata.json.",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="Path to write the markdown comparison report. "
        "If omitted, no report is generated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint to evaluate models and optionally generate a report."""
    args = _parse_args(argv)
    artifacts_dir = Path(args.artifacts)

    models = evaluate_models(artifacts_dir)
    if not models:
        return

    if args.report:
        report_path = Path(args.report)
        generate_model_comparison_report(artifacts_dir, report_path)


if __name__ == "__main__":
    main()