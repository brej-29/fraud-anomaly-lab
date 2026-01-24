import numpy as np

from ml.models import (
    COPODWrapper,
    IsolationForestWrapper,
    LOFWrapper,
    OneClassSVMWrapper,
)
from shared.utils import set_global_seed


def _make_synthetic_data():
    """Create a tiny synthetic dataset with clear anomalies."""
    set_global_seed(42)
    normal = np.random.normal(loc=0.0, scale=1.0, size=(100, 2))
    anomalies = np.random.normal(loc=5.0, scale=0.5, size=(5, 2))
    X = np.vstack([normal, anomalies])
    y = np.array([0] * len(normal) + [1] * len(anomalies))
    return X, y


def _assert_scores_direction(model_cls):
    X, y = _make_synthetic_data()
    model = model_cls()
    model.fit(X[y == 0])
    scores = model.score_samples(X)
    assert scores.shape[0] == X.shape[0]

    mean_normal = scores[y == 0].mean()
    mean_anomaly = scores[y == 1].mean()

    # By convention, higher scores must indicate more anomalous observations.
    assert mean_anomaly > mean_normal


def test_score_direction_isolation_forest():
    _assert_scores_direction(IsolationForestWrapper)


def test_score_direction_lof():
    _assert_scores_direction(LOFWrapper)


def test_score_direction_one_class_svm():
    _assert_scores_direction(OneClassSVMWrapper)


def test_score_direction_copod():
    _assert_scores_direction(COPODWrapper)