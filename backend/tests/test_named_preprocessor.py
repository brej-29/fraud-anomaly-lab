import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from backend.app.services.model_registry import ModelRegistry
from backend.app.services.scorer import Scorer

class SumScore:
    def score_samples(self, matrix):
        return np.asarray(matrix).sum(axis=1)

def test_single_and_batch_preserve_named_transformer_contract(tmp_path, monkeypatch):
    registry = ModelRegistry(tmp_path)
    registry.metadata = {"feature_columns": ["Amount", "Time"], "models": {}}
    registry.preprocessor = ColumnTransformer([("scale", StandardScaler(), ["Amount", "Time"])]).fit(pd.DataFrame({"Amount": [1., 2., 3.], "Time": [10., 20., 30.]}))
    registry._models = {"sum": SumScore()}
    monkeypatch.setattr("backend.app.services.scorer.insert_prediction", lambda **kwargs: 1)
    scorer = Scorer(registry)
    first, second = {"Time": 20., "Amount": 2.}, {"Amount": 3., "Time": 30.}
    assert scorer.score_transaction(first)["ensemble"]["score"] == 0
    batch = scorer.score_batch([first, second])
    assert len(batch) == 2
    assert batch[0]["ensemble"]["score"] == 0
    assert batch[1]["ensemble"]["score"] > 0
