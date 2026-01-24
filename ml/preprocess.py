from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from shared.utils import log_info


@dataclass
class SplitData:
    """Container for train/validation/test splits."""

    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series


def load_raw_data(path: Path | str) -> pd.DataFrame:
    """
    Load the raw credit card dataset from CSV.

    Parameters
    ----------
    path:
        Path to the CSV file.

    Returns
    -------
    DataFrame containing the raw dataset.
    """
    log_info(f"Loading raw data from {path}")
    return pd.read_csv(path)


def time_based_split(
    df: pd.DataFrame, test_size: float = 0.2, val_size: float = 0.1, random_state: int = 42
) -> SplitData:
    """
    Perform a leakage-safe time-based split of the dataset.

    This is a placeholder implementation that currently falls back to random splitting.
    The time-based splitting logic will be implemented once EDA confirms details.

    Parameters
    ----------
    df:
        Full dataset as a DataFrame.
    test_size:
        Fraction of the data to allocate to the test set.
    val_size:
        Fraction of the remaining training data to allocate to validation.
    random_state:
        Random seed for reproducibility.

    Returns
    -------
    SplitData with train/validation/test partitions.
    """
    log_info("Performing placeholder random train/val/test split (time-based TBD).")

    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    val_rel_size = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=val_rel_size,
        random_state=random_state,
        stratify=y_train_val,
    )

    return SplitData(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
    )


def preprocess(path: Path | str) -> Tuple[SplitData, dict]:
    """
    Orchestrate data loading and preprocessing.

    Currently:
    - Loads the raw CSV.
    - Performs a placeholder random split (time-based to be implemented).
    - Does not yet perform scaling or feature engineering.

    Returns
    -------
    A tuple of:
    - SplitData with train/val/test data.
    - Dictionary of metadata (e.g., columns) for downstream use.
    """
    df = load_raw_data(path)
    split_data = time_based_split(df)
    metadata = {
        "columns": list(split_data.X_train.columns),
        "n_rows": int(df.shape[0]),
        "n_fraud": int(df["Class"].sum()),
    }
    log_info(
        f"Preprocessing complete (placeholder). Rows={metadata['n_rows']}, fraud={metadata['n_fraud']}."
    )
    return split_data, metadata