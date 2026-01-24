"""Shared utility helpers."""

import logging
import os
import random
from typing import Any

import numpy as np


logger = logging.getLogger("fraud_anomaly_lab")


def configure_basic_logging(level: int = logging.INFO) -> None:
    """Configure a simple root logger for non-backend modules."""
    if logger.handlers:
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def log_info(message: str, *args: Any) -> None:
    """Log an info-level message via the shared logger."""
    if not logger.handlers:
        configure_basic_logging()
    logger.info(message, *args)


def set_global_seed(seed: int) -> None:
    """Set random seed for reproducibility across numpy and random."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)