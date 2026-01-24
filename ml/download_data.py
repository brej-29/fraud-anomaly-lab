from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from shared.utils import log_info

DATA_DIR = Path("data") / "raw"
RAW_FILE = DATA_DIR / "creditcard.csv"
DATASET_SLUG = "mlg-ulb/creditcardfraud"
SCRIPT_PATH = Path("scripts") / "download_kaggle.sh"


def data_exists() -> bool:
    """Check whether the expected raw dataset file is present."""
    return RAW_FILE.exists()


def kaggle_cli_available() -> bool:
    """Return True if the Kaggle CLI is available on PATH."""
    return shutil.which("kaggle") is not None


def kaggle_credentials_available() -> bool:
    """Check for presence of kaggle.json credentials."""
    candidates = []
    config_dir = os.getenv("KAGGLE_CONFIG_DIR")
    if config_dir:
        candidates.append(Path(config_dir) / "kaggle.json")
    candidates.append(Path.home() / ".kaggle" / "kaggle.json")
    return any(p.is_file() for p in candidates)


def download_with_script() -> None:
    """
    Trigger dataset download via the helper shell script.

    This wraps `scripts/download_kaggle.sh` to keep logic in one place.
    """
    if not SCRIPT_PATH.exists():
        log_info(
            f"Download script not found at {SCRIPT_PATH}. "
            "Please run the Kaggle CLI manually as documented in scripts/kaggle_setup.md."
        )
        return

    log_info(f"Running download script: {SCRIPT_PATH}")
    try:
        subprocess.run(["bash", str(SCRIPT_PATH)], check=True)
    except FileNotFoundError:
        log_info(
            "Shell or script could not be executed. Ensure bash is installed and the script is executable."
        )
    except subprocess.CalledProcessError as exc:
        log_info(f"Download script failed with exit code {exc.returncode}.")


def main() -> None:
    """Entry point for downloading data, with robust checks and guidance."""
    if data_exists():
        log_info(f"Raw data already present at {RAW_FILE}. No download needed.")
        log_info(
            "Next steps: run `make preprocess` to prepare splits, then `make train` and `make report`."
        )
        return

    log_info(f"Raw data not found at {RAW_FILE}. Preparing to download {DATASET_SLUG}.")

    if not kaggle_cli_available():
        log_info(
            "Kaggle CLI not found on PATH. Install with `pip install kaggle` and ensure `kaggle` is available."
        )

    if not kaggle_credentials_available():
        log_info(
            "Kaggle credentials (kaggle.json) not detected. "
            "Follow scripts/kaggle_setup.md to configure your Kaggle API token."
        )

    download_with_script()

    if data_exists():
        log_info(f"Dataset successfully downloaded to {RAW_FILE}.")
        log_info(
            "Next steps: run `make preprocess` to create processed splits, then `make train` and `make report`."
        )
    else:
        log_info(
            f"Dataset still not found at {RAW_FILE} after running the script.\n"
            "Please verify Kaggle configuration and consider running the commands in scripts/kaggle_setup.md manually."
        )


if __name__ == "__main__":
    main()