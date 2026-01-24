from pathlib import Path
from typing import Any, Dict

from ..core.logging import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """
    Placeholder registry for loading and accessing model artifacts.

    In future steps this will:
    - Load trained models from `ml/artifacts/`.
    - Expose a unified interface to retrieve models and preprocessing objects.
    """

    def __init__(self, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = artifacts_dir or Path("ml") / "artifacts"
        self._models: Dict[str, Any] = {}

    def load_all(self) -> None:
        """Load all configured models from the artifacts directory (placeholder)."""
        logger.info("ModelRegistry.load_all called (no-op placeholder).")
        # TODO: Implement model loading when artifacts are available.

    def get_model(self, name: str) -> Any:
        """Retrieve a model by name, raising KeyError if it does not exist."""
        try:
            return self._models[name]
        except KeyError as exc:
            logger.error("Requested model '%s' not found in registry.", name)
            raise exc