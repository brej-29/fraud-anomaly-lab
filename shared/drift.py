from __future__ import annotations

from typing import Sequence

import numpy as np


def compute_psi(expected_counts: Sequence[float], actual_counts: Sequence[float]) -> float:
    """
    Compute Population Stability Index (PSI) between two histograms.

    Parameters
    ----------
    expected_counts:
        Baseline counts per bin (e.g. from training/validation data).
    actual_counts:
        Recent counts per bin (e.g. from production window).

    Returns
    -------
    PSI value (float). Rough rule of thumb:
    - < 0.1: no significant shift
    - 0.1–0.25: moderate shift
    - > 0.25: significant shift
    """
    expected = np.asarray(expected_counts, dtype="float64")
    actual = np.asarray(actual_counts, dtype="float64")

    expected_sum = expected.sum()
    actual_sum = actual.sum()
    if expected_sum <= 0 or actual_sum <= 0:
        return 0.0

    expected_pct = expected / expected_sum
    actual_pct = actual / actual_sum

    psi = 0.0
    for e, a in zip(expected_pct, actual_pct):
        if e <= 0 or a <= 0:
            # Skip bins with no mass in either distribution.
            continue
        psi += (a - e) * np.log(a / e)
    return float(psi)