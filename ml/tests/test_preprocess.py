import numpy as np
import pandas as pd

from ml.preprocess import TARGET_COLUMN, time_based_split


def _make_dummy_dataframe(n_rows: int = 100) -> pd.DataFrame:
    time = np.arange(n_rows)
    amount = np.linspace(1.0, 100.0, n_rows)
    # Simple deterministic pattern for the target
    target = np.where(time % 10 == 0, 1, 0)
    data = {
        "Time": time,
        "Amount": amount,
        TARGET_COLUMN: target,
    }
    for i in range(1, 29):
        data[f"V{i}"] = np.random.randn(n_rows)
    return pd.DataFrame(data)


def test_time_based_split_shapes_and_order():
    df = _make_dummy_dataframe(200)
    train_df, val_df, test_df = time_based_split(
        df, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, sort_by="Time"
    )

    # All rows should be assigned to exactly one split
    total_len = len(train_df) + len(val_df) + len(test_df)
    assert total_len == len(df)

    # Time should be non-decreasing across splits
    assert train_df["Time"].max() <= val_df["Time"].min()
    assert val_df["Time"].max() <= test_df["Time"].min()