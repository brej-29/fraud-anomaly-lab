#!/usr/bin/env bash
set -euo pipefail

# Download the Kaggle Credit Card Fraud Detection dataset into data/raw/
# Requires:
# - Kaggle account and API token (see scripts/kaggle_setup.md)
# - `kaggle` CLI installed: pip install kaggle

DATA_DIR="data/raw"
DATASET_SLUG="mlg-ulb/creditcardfraud"

mkdir -p "${DATA_DIR}"

echo "Downloading dataset ${DATASET_SLUG} to ${DATA_DIR}..."
kaggle datasets download -d "${DATASET_SLUG}" -p "${DATA_DIR}" --force

echo "Unzipping any downloaded archives..."
for f in "${DATA_DIR}"/*.zip; do
  [ -e "$f" ] || continue
  unzip -o "$f" -d "${DATA_DIR}"
done

echo "Done. Verify that the CSV file is present in ${DATA_DIR}."