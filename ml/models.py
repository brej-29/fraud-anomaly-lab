from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type

import joblib
import numpy as np
from pyod.models.copod import COPOD
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from shared.utils import log_info


class BaseAnomalyModel:
    """
    Base interface for anomaly detection models.

    Implementations must ensure that `score_samples` returns higher scores for
    more anomalous observations.
    """

    def fit(self, X: np.ndarray) -> "BaseAnomalyModel":
        raise NotImplementedError

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def save(self, path: Path | str) -> None:
        raise NotImplementedError

    @classmethod
    def load(cls, path: Path | str) -> "BaseAnomalyModel":
        raise NotImplementedError

    def get_params(self) -> Dict[str, Any]:
        """Return model hyperparameters, if available."""
        return {}


class IsolationForestWrapper(BaseAnomalyModel):
    """
    Wrapper around sklearn's IsolationForest.

    sklearn's IsolationForest.score_samples returns the opposite of the anomaly score
    (larger values correspond to less abnormal observations). We invert it so that
    higher scores mean more suspicious.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.model = IsolationForest(**kwargs)

    def fit(self, X: np.ndarray) -> "IsolationForestWrapper":
        self.model.fit(X)
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        scores = self.model.score_samples(X)
        return -np.asarray(scores)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        try:
            joblib.dump(self.model, path)
            log_info("Saved IsolationForest model to %s", path)
        except Exception as exc:  # noqa: BLE001
            log_info(f"Failed to save IsolationForest model to {path}: {exc}")

    @classmethod
    def load(cls, path: Path | str) -> "IsolationForestWrapper":
        path = Path(path)
        model = joblib.load(path)
        wrapper = cls()
        wrapper.model = model
        return wrapper

    def get_params(self) -> Dict[str, Any]:
        return self.model.get_params(deep=False)


class LOFWrapper(BaseAnomalyModel):
    """
    Wrapper around sklearn's LocalOutlierFactor with novelty detection.

    score_samples returns the opposite of the local outlier factor; we invert it so that
    higher scores indicate more anomalous observations.
    """

    def __init__(self, **kwargs: Any) -> None:
        # Ensure novelty detection is enabled by default so score_samples is available.
        kwargs.setdefault("novelty", True)
        self.model = LocalOutlierFactor(**kwargs)

    def fit(self, X: np.ndarray) -> "LOFWrapper":
        self.model.fit(X)
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        scores = self.model.score_samples(X)
        return -np.asarray(scores)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        try:
            joblib.dump(self.model, path)
            log_info("Saved LOF model to %s", path)
        except Exception as exc:  # noqa: BLE001
            log_info(f"Failed to save LOF model to {path}: {exc}")

    @classmethod
    def load(cls, path: Path | str) -> "LOFWrapper":
        path = Path(path)
        model = joblib.load(path)
        wrapper = cls()
        wrapper.model = model
        return wrapper

    def get_params(self) -> Dict[str, Any]:
        return self.model.get_params(deep=False)


class OneClassSVMWrapper(BaseAnomalyModel):
    """
    Wrapper around sklearn's OneClassSVM.

    decision_function returns positive values for inliers and negative for outliers.
    We invert it so that higher scores correspond to more anomalous observations.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.model = OneClassSVM(**kwargs)

    def fit(self, X: np.ndarray) -> "OneClassSVMWrapper":
        self.model.fit(X)
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        scores = self.model.decision_function(X)
        return -np.asarray(scores)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        try:
            joblib.dump(self.model, path)
            log_info("Saved OneClassSVM model to %s", path)
        except Exception as exc:  # noqa: BLE001
            log_info(f"Failed to save OneClassSVM model to {path}: {exc}")

    @classmethod
    def load(cls, path: Path | str) -> "OneClassSVMWrapper":
        path = Path(path)
        model = joblib.load(path)
        wrapper = cls()
        wrapper.model = model
        return wrapper

    def get_params(self) -> Dict[str, Any]:
        return self.model.get_params(deep=False)


class COPODWrapper(BaseAnomalyModel):
    """
    Wrapper around PyOD's COPOD model.

    COPOD's decision_function returns outlier scores where larger values indicate
    more abnormal observations, which aligns with our convention.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.model = COPOD(**kwargs)

    def fit(self, X: np.ndarray) -> "COPODWrapper":
        self.model.fit(X)
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        scores = self.model.decision_function(X)
        return np.asarray(scores)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        try:
            joblib.dump(self.model, path)
            log_info("Saved COPOD model to %s", path)
        except Exception as exc:  # noqa: BLE001
            log_info(f"Failed to save COPOD model to {path}: {exc}")

    @classmethod
    def load(cls, path: Path | str) -> "COPODWrapper":
        path = Path(path)
        model = joblib.load(path)
        wrapper = cls()
        wrapper.model = model
        return wrapper

    def get_params(self) -> Dict[str, Any]:
        return self.model.get_params(deep=False)


MODEL_REGISTRY: Dict[str, Type[BaseAnomalyModel]] = {
    "isolation_forest": IsolationForestWrapper,
    "lof": LOFWrapper,
    "one_class_svm": OneClassSVMWrapper,
    "copod": COPODWrapper,
}