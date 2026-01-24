# Metrics and Thresholding Strategy

This project targets **credit card fraud detection** under **severe class imbalance** (~0.172% fraud). Traditional accuracy is misleading; we prioritize metrics tailored to rare positive events. See `context/GOAL.md` for high-level performance targets.

---

## Core Metrics

### 1. Precision (Positive Predictive Value)

\[
\text{Precision} = \frac{TP}{TP + FP}
\]

- Among all transactions flagged as fraud, how many are truly fraud?
- High precision reduces **false alarms**.

### 2. Recall (Sensitivity / True Positive Rate)

\[
\text{Recall} = \frac{TP}{TP + FN}
\]

- Among all actual fraud transactions, how many did we detect?
- High recall reduces **missed frauds**.

### 3. F1 Score

\[
\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
\]

- Harmonic mean of precision and recall.
- Useful summary when we care about both false positives and false negatives, but it assumes a somewhat symmetric trade-off.

### 4. ROC-AUC (Area Under ROC Curve)

- Plots **True Positive Rate** vs **False Positive Rate** across thresholds.
- Measures the model’s ability to rank positives above negatives.
- Can remain high even when precision is low in extremely imbalanced settings, so it is **secondary**.

### 5. PR-AUC (Area Under Precision–Recall Curve)

- Plots **Precision** vs **Recall** across thresholds.
- Directly reflects performance on the **positive (fraud) class**.
- Much more informative than ROC-AUC when fraud is rare.

**We adopt PR-AUC as our primary model selection metric.**

---

## Why PR-AUC Matters for Class Imbalance

In highly imbalanced problems:

- A naive model that always predicts “non-fraud” can achieve very high accuracy.
- Even models with excellent ROC-AUC may still yield poor precision at practically useful recall levels.
- The **PR curve** and **PR-AUC** highlight how well the model concentrates probability mass on the rare positives:
  - High PR-AUC → the model can achieve **good recall with acceptable precision** at some threshold.

Therefore, we will:

- Compare models primarily using **validation PR-AUC**.
- Use ROC-AUC as a supplementary sanity check.

---

## Threshold Selection Strategy

Our models (or ensemble) will output **continuous scores** (e.g., anomaly scores or fraud probabilities). We must choose a threshold to convert scores to binary decisions.

### Candidate Approaches

1. **Maximize F1** on a validation set.
2. **Target recall**:
   - Choose the lowest threshold that achieves a specified recall (e.g., ≥ 0.80) and report the associated precision.
3. **Target precision**:
   - Choose a threshold that ensures a minimum precision (e.g., ≥ 0.10) and report the associated recall.
4. **Cost-aware thresholding (future)**:
   - Incorporate business costs of false positives vs false negatives when available.

### Initial Plan

- Use the validation set to:
  - Plot **precision–recall curves**.
  - Identify thresholds at:
    - Maximum F1.
    - Minimum precision level (e.g., 0.10) with maximum recall.
- Report and document:
  - Selected threshold(s).
  - Corresponding precision, recall, F1, and PR-AUC.

Implementation details will be captured in:

- `ml/evaluate.py` – threshold search and metric computation.
- `reports/model_comparison.md` – comparison and narrative.
- `notebooks/01_eda_decisions.ipynb` – initial analysis and reasoning.

---

## Reporting Conventions

For each model and the ensemble on the **validation and test sets**, we will log:

- PR-AUC
- ROC-AUC
- Precision, recall, and F1 at selected thresholds
- Confusion matrix entries: TP, FP, TN, FN
- Optionally:
  - Precision at fixed recall levels (e.g., recall 0.6, 0.8, 0.9)
  - Recall at fixed precision levels (e.g., precision 0.1, 0.2)

All metric computations should be **reproducible** (fixed random seeds, documented versions) and, where possible, stored in structured formats (e.g., JSON or CSV) for later analysis.