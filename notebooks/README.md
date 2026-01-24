# Notebooks

This folder contains Jupyter notebooks used for exploratory data analysis (EDA), decision tracking, and experiments.

## Conventions

- Keep notebooks **lightweight** and focused on:
  - Understanding data characteristics and class imbalance.
  - Visualizing model behavior and trade-offs.
  - Documenting decisions that are later reflected in code and context docs.
- For production logic, prefer moving code into modules under `ml/` or `shared/` and import them into notebooks.

## 01_eda_decisions.ipynb

The `01_eda_decisions.ipynb` notebook is a **template** designed to:

- Frame the fraud detection problem and dataset specifics.
- Explore class imbalance and temporal structure.
- Plan leakage-safe splitting, preprocessing, model selection, metrics, and explainability.
- Capture reproducibility choices (seeds, versions, environment details).

Fill in this template as one of the first steps once data is available locally in `data/raw/`.