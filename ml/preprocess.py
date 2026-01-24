from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from shared.utils import log_info

TARGET_COLUMN = "Class"
REQUIRED_COLUMNS = ["Time", "Amount", TARGET_COLUMN] + [f"V{i}" for i in range(1, 29)]


@dataclass
class SplitData:
    """Container for preprocessed train/validation/test splits."""

    X_train: np.ndarray
    X_val: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_val: np.ndarray
    y_test: np.ndarray
    X_train_normal: np.ndarray
    feature_columns: list[str]


def load_raw_data(path: Path | str) -> pd.DataFrame:
    """
    Load the raw credit card dataset from CSV and perform basic validation.

    Parameters
    ----------
    path:
        Path to the CSV file.

    Returns
    -------
    DataFrame containing the raw dataset.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is empty or cannot be parsed.
    """
    path = Path(path)
    log_info(f"Loading raw data from {path}")
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found at {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Raw data file at {path} is empty or invalid.") from exc

    validate_schema(df)
    return df


def validate_schema(df: pd.DataFrame) -> None:
    """
    Validate that the dataframe matches the expected schema.

    Checks:
    - All required columns are present.
    - TARGET_COLUMN is binary (0/1).
    - No missing values in critical columns (Time, Amount, Class).
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    target_values = df[TARGET_COLUMN].dropna().unique()
    # Accept numeric 0/1 values (int or float).
    normalized = set(int(v) for v in target_values)
    if not normalized.issubset({0, 1}):
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' must be binary 0/1; "
            f"found values: {sorted(target_values)}"
        )

    critical_na = df[["Time", "Amount", TARGET_COLUMN]].isna().any()
    if critical_na.any():
        cols_with_na = list(critical_na[critical_na].index)
        raise ValueError(f"Critical columns contain missing values: {cols_with_na}")

    log_info("Schema validation passed: required columns present and target is binary.")


def time_based_split(
    df: pd.DataFrame,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    sort_by: str = "Time",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Perform a leakage-safe time-based split of the dataset.

    Data is sorted by the `sort_by` column (default: Time), then split into
    train/validation/test using the provided ratios.

    Parameters
    ----------
    df:
        Full dataset as a DataFrame.
    train_ratio:
        Fraction of data to allocate to the training set.
    val_ratio:
        Fraction of data to allocate to the validation set.
    test_ratio:
        Fraction of data to allocate to the test set.
    sort_by:
        Column name to use for sorting (typically "Time").

    Returns
    -------
    (train_df, val_df, test_df)
    """
    if sort_by not in df.columns:
        raise ValueError(f"Column '{sort_by}' not found in dataframe.")

    ratio_sum = train_ratio + val_ratio + test_ratio
    if not np.isclose(ratio_sum, 1.0):
        raise ValueError(
            f"train_ratio + val_ratio + test_ratio must sum to 1.0; got {ratio_sum}"
        )

    df_sorted = df.sort_values(by=sort_by).reset_index(drop=True)
    n_rows = len(df_sorted)
    train_end = int(n_rows * train_ratio)
    val_end = train_end + int(n_rows * val_ratio)

    train_df = df_sorted.iloc[:train_end]
    val_df = df_sorted.iloc[train_end:val_end]
    test_df = df_sorted.iloc[val_end:]

    log_info(
        "Time-based split complete: "
        f"train={len(train_df)}, val={len(val_df)}, test={len(test_df)}."
    )
    if not train_df.empty:
        log_info(
            "Train Time range: [%s, %s]",
            train_df["Time"].min(),
            train_df["Time"].max(),
        )
    if not val_df.empty:
        log_info(
            "Val Time range: [%s, %s]",
            val_df["Time"].min(),
            val_df["Time"].max(),
        )
    if not test_df.empty:
        log_info(
            "Test Time range: [%s, %s]",
            test_df["Time"].min(),
            test_df["Time"].max(),
        )

    return train_df, val_df, test_df


def build_preprocessor(scale_time: bool = True) -> Pipeline:
    """
    Build a preprocessing pipeline that scales Amount (and optionally Time)
    using RobustScaler and passes through PCA components.

    Returns
    -------
    sklearn Pipeline instance.
    """
    feature_columns = ["Time", "Amount"] + [f"V{i}" for i in range(1, 29)]

    columns_to_scale = ["Amount"]
    if scale_time and "Time" in feature_columns:
        columns_to_scale.append("Time")

    transformer = ColumnTransformer(
        transformers=[
            ("robust_scaler", RobustScaler(), columns_to_scale),
        ],
        remainder="passthrough",
    )
    pipeline = Pipeline([("features", transformer)])
    log_info(
        "Preprocessor created with RobustScaler on columns: %s", ", ".join(columns_to_scale)
    )
    return pipeline


def transform_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    preprocessor: Pipeline,
) -> SplitData:
    """
    Fit the preprocessor on the training data and transform all splits.

    Returns
    -------
    SplitData containing numpy arrays for X/y and normal-only training data.
    """
    feature_columns = [c for c in train_df.columns if c != TARGET_COLUMN]

    X_train_raw = train_df[feature_columns]
    y_train = train_df[TARGET_COLUMN].astype(int).to_numpy()

    preprocessor.fit(X_train_raw)
    X_train = preprocessor.transform(X_train_raw)
    X_val = preprocessor.transform(val_df[feature_columns])
    X_test = preprocessor.transform(test_df[feature_columns])

    y_val = val_df[TARGET_COLUMN].astype(int).to_numpy()
    y_test = test_df[TARGET_COLUMN].astype(int).to_numpy()

    X_train_normal = X_train[y_train == 0]

    log_info(
        "Transformed splits: X_train=%s, X_val=%s, X_test=%s; normal-only train=%s.",
        X_train.shape,
        X_val.shape,
        X_test.shape,
        X_train_normal.shape,
    )

    return SplitData(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
        X_train_normal=X_train_normal,
        feature_columns=feature_columns,
    )


def save_processed_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    out_dir: Path,
) -> None:
    """Save processed splits to CSV files for caching."""
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = out_dir / "train.csv"
    val_path = out_dir / "val.csv"
    test_path = out_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    log_info("Saved processed splits to %s", out_dir)


def load_processed_splits(out_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load processed splits from CSV files."""
    train_path = out_dir / "train.csv"
    val_path = out_dir / "val.csv"
    test_path = out_dir / "test.csv"

    if not (train_path.exists() and val_path.exists() and test_path.exists()):
        raise FileNotFoundError(
            f"Processed split files not found in {out_dir}. "
            "Expected train.csv, val.csv, test.csv."
        )

    log_info("Loading processed splits from %s", out_dir)
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)
    return train_df, val_df, test_df


def prepare_data(
    raw_path: Path | str,
    processed_dir: Path | str | None = None,
    force: bool = False,
) -> Tuple[SplitData, Pipeline, Dict[str, Any]]:
    """
    Orchestrate data loading, splitting, preprocessing, and optional caching.

    Parameters
    ----------
    raw_path:
        Path to the raw CSV file.
    processed_dir:
        Directory where processed splits (train/val/test CSV) will be cached.
    force:
        If True, ignore any existing cached splits and recompute from raw data.

    Returns
    -------
    split_data:
        SplitData with transformed arrays and normal-only training data.
    preprocessor:
        Fitted preprocessing pipeline.
    metadata:
        Dictionary with dataset and split metadata.
    """
    raw_path = Path(raw_path)
    processed_dir_path = Path(processed_dir) if processed_dir is not None else None

    if processed_dir_path and not force:
        try:
            train_df, val_df, test_df = load_processed_splits(processed_dir_path)
            df_all = pd.concat([train_df, val_df, test_df], ignore_index=True)
            validate_schema(df_all)
            log_info("Reusing cached processed splits from %s", processed_dir_path)
        except FileNotFoundError:
            df_all = load_raw_data(raw_path)
            train_df, val_df, test_df = time_based_split(df_all)
            if processed_dir_path is not None:
                save_processed_splits(train_df, val_df, test_df, processed_dir_path)
    else:
        df_all = load_raw_data(raw_path)
        train_df, val_df, test_df = time_based_split(df_all)
        if processed_dir_path is not None:
            save_processed_splits(train_df, val_df, test_df, processed_dir_path)

    preprocessor = build_preprocessor()
    split_data = transform_splits(train_df, val_df, test_df, preprocessor)

    metadata: Dict[str, Any] = {
        "raw_path": str(raw_path),
        "n_rows": int(df_all.shape[0]),
        "n_fraud": int(df_all[TARGET_COLUMN].sum()),
        "feature_columns": split_data.feature_columns,
        "splits": {
            "train": int(train_df.shape[0]),
            "val": int(val_df.shape[0]),
            "test": int(test_df.shape[0]),
        },
    }

    log_info(
        "Preprocessing complete. Rows=%s, fraud=%s.",
        metadata["n_rows"],
        metadata["n_fraud"],
    )
    return split_data, preprocessor, metadata


def preprocess(path: Path | str) -> Tuple[SplitData, Dict[str, Any]]:
    """
    Backwards-compatible wrapper for preprocessing.

    Returns
    -------
    (SplitData, metadata)
    """
    split_data, _, metadata = prepare_data(path)
    return split_data, metadata


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess credit card fraud data.")
    parser.add_argument(
        "--raw",
        type=str,
        required=True,
        help="Path to raw creditcard.csv file (e.g., data/raw/creditcard.csv).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="data/processed",
        help="Output directory for processed CSV splits (default: data/processed).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recomputation of splits even if cached files exist.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for preprocessing."""
    args = _parse_args(argv)
    raw_path = Path(args.raw)
    out_dir = Path(args.out) if args.out else None

    try:
        split_data, _, metadata = prepare_data(raw_path, processed_dir=out_dir, force=args.force)
    except Exception as exc:  # noqa: BLE001 - top-level CLI handler
        log_info(f"Preprocessing failed: {exc}")
        raise

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        meta_path = out_dir / "metadata.json"
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        log_info("Wrote preprocessing metadata to %s", meta_path)

    log_info(
        "Preprocessing CLI complete. Train/val/test sizes: %s/%s/%s.",
        metadata["splits"]["train"],
        metadata["splits"]["val"],
        metadata["splits"]["test"],
    )
    log_info("Next steps: run `make train` and then `make report` to train models and generate the comparison report.")


if __name__ == "__main__":
    main()