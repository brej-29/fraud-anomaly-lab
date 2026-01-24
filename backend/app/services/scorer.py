from typing import Any, Dict

from ..core.logging import get_logger
from .model_registry import ModelRegistry

logger = get_logger(__name__)


class Scorer:
    """
    Placeholder scorer that will apply preprocessing and ensemble logic.

    Currently, this class only logs the received payload and returns a dummy result.
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()
        logger.info("Scorer initialized with artifacts directory: %s", self.registry.artifacts_dir)

    def score_transaction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single transaction.

        Parameters
        ----------
        features:
            Dictionary of feature values for a single transaction.

        Returns
        -------
        A dictionary with placeholder score and decision.
        """
        logger.info("Received transaction for scoring (placeholder).")
        # TODO: Replace with real scoring using models from the registry.
        return {
            "score": 0.0,
            "is_fraud": False,
            "details": "Scoring not implemented yet.",
        }