from __future__ import annotations

import subprocess
from pathlib import Path

from shared.utils import log_info


DATA_DIR = Path("data") / "raw"
DATASET_SLUG = "mlg-ulb/creditcardfraud"


def data_exists() -> bool:
    """Check whether the expected raw dataset file(s) are present."""
    csv_files = list(DATA_DIR.glob("*.csv"))
    return len(csv_files) > 0


def download_with_kaggle() -> None:
    """
    Trigger dataset download via the Kaggle CLI.

    Requires:
    - `kaggle` package installed and CLI on PATH.
    - Valid `kaggle.json` credentials configured (see scripts/kaggle_setup.md).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    log_info(f"Downloading dataset {DATASET_SLUG} into {DATA_DIR}...")

    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET_SLUG,
        "-p",
        str(DATA_DIR),
        "--force",
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        log_info(
            "Kaggle CLI not found. Install with `pip install kaggle` and ensure it is on your PATH."
        )
        return
    except subprocess.CalledProcessError as exc:
        log_info(f"Kaggle download failed: {exc}")
        return

    # Unzip any downloaded archives
    for archive in DATA_DIR.glob("*.zip"):
        log_info(f"Unzipping {archive}...")
        subprocess.run(["unzip", "-o", str(archive), "-d", str(DATA_DIR)], check=False)

    log_info("Download step completed. Verify that the CSV file is present in data/raw/.")


def main() -> None:
    """Entry point for downloading data, with basic existence checks."""
    if data_exists():
        log_info("Raw data already present in data/raw/. No action taken.")
        return

    log_info("Raw data not found in data/raw/. Attempting Kaggle download...")
    download_with_kaggle()
    if not data_exists():
        log_info(
            "Dataset still not found after attempted download.\n"
            "Please verify Kaggle configuration and consider using scripts/download_kaggle.sh."
        )
    else:
        log_info("Dataset successfully downloaded to data/raw/.")


if __name__ == "__main__":
    main()