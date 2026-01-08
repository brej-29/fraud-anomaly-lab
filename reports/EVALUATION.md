# Temporal review-budget benchmark

Source: [ULB / Worldline](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). Run: python evaluation/run.py. Full evidence: [benchmark.json](benchmark.json).

Holdout: 56962 rows, 75 frauds. Review budget: 284 rows (floor of 0.5%). Candidate selected by validation average precision, before viewing test performance.

| Strategy | AP | ROC-AUC | Caught | Recall | Precision | Legitimate reviews |
|---|---:|---:|---:|---:|---:|---:|
| Logistic regression | 0.7461 | 0.9818 | 64 | 85.3% | 22.5% | 220 |
| Logistic · no amount | 0.7451 | 0.9817 | 64 | 85.3% | 22.5% | 220 |
| Isolation Forest | 0.0793 | 0.9520 | 35 | 46.7% | 12.3% | 249 |
| Largest amount first | 0.0014 | 0.3820 | 1 | 1.3% | 0.4% | 283 |

Predeclared target met. Label-informed logistic regression captures 64 frauds versus 35 for normal-only Isolation Forest. This is a comparison of two information regimes, not proof of supervised learning superiority without labels. The logistic no-amount ablation has the same operating-point counts; amount adds little.

Three seeds: logistic AP 0.74608 and recall 85.3% in each (deterministic lbfgs); Isolation Forest recall 46.7%, 42.7%, 41.3%. Paired fixed-score bootstrap recall-lift interval: 26.7–48.7 percentage points. Wilson recall interval for the selected ranker: 75.6–91.6%. Neither accounts for institutional or temporal distribution shift.

Feature overlap: 648 test rows match training features, 1469 match validation features; union 1722. Excluding all earlier-seen test feature rows leaves 55240 rows, 75 frauds and 85.3% recall at 276 reviews. PCA fitting provenance is unavailable; original supplied components may encode upstream whole-dataset transformations.

Error analysis: six misses among amounts ≤25, one among 25–100, four above 100. Earlier holdout half recall 88.7%; later half 77.3%. Only two historical days are observed; there is no production performance, review-time measurement, financial recovery claim, or user validation.

Dataset SHA-256: 76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89
