# Notebooks

This folder contains Jupyter notebooks used for exploratory data analysis (EDA), decision tracking, and experiments.

## Conventions

- Keep notebooks **lightweight** and focused on:
  - Understanding data characteristics and class imbalance.
  - Visualizing model behavior and trade-offs.
  - Documenting decisions that are later reflected in code and context docs.
- For production logic, prefer moving code into modules under `ml/` or `shared/` and import them into notebooks.

## 01_eda_decisions.ipynb

The `01_eda_decisions.ipynb` notebook provides a **full EDA and decisions walkthrough** for this project. It:

- Frames the fraud detection problem and dataset specifics.
- Explores class imbalance and temporal structure.
- Implements and justifies a leakage-safe time-based split.
- Examines feature distributions (Time, Amount, PCA components).
- Trains a simple supervised proxy model for feature importance via permutation importance.
- Captures reproducibility choices (seeds, versions, environment details).
- Documents metric and thresholding choices, and what we plan to monitor in production.

### How to run the notebook

1. Ensure dependencies are installed:

   ```bash
   make setup
   ```

2. Download the Kaggle dataset (requires Kaggle API configuration as per `scripts/kaggle_setup.md`):

   ```bash
   make download-data
   ```

3. (Optional but recommended) Run preprocessing once to confirm the pipeline works:

   ```bash
   make preprocess
   ```

4. Launch your notebook environment from the project root (for example):

   ```bash
   jupyter notebook
   ```

5. Open `notebooks/01_eda_decisions.ipynb` and run all cells.  
   The notebook assumes the raw dataset is available at `data/raw/creditcard.csv` and uses functions from `ml.preprocess` for consistency.