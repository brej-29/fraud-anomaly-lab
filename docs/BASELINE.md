# Starting-state audit

Starting default-branch commit: `b87dd5b`. Fetched and pulled `main` before edits; tagged `backup/starting-state-2026-11-05`. The project is a single public monorepo; unrelated sibling repositories were not changed.

## What existed

- Python pipelines with time-based splitting, normal-only anomaly models and saved metadata.
- FastAPI scoring, SQLite prediction storage, feedback and monitoring endpoints.
- Streamlit UI: single-prediction workflow required manually pasting Time, Amount and V1–V28 in JSON.
- Two merged historical pull requests. Ignored local dataset and model binaries were already present.

## Reproduced failures

Installed the original unpinned requirements in a local Python 3.11 environment, then ran `python -m pytest backend ml -q --disable-warnings --cache-clear`: **9 passed, 1 failed**. `test_predict_returns_503_when_artifacts_missing` failed because local artifacts existed, so its implicit assumption about the filesystem was false. Exercising that path revealed the scorer sent an unnamed array to a preprocessor that selects columns by name, raising `ValueError: Specifying the columns using strings is only supported for dataframes.`

Repair: preserve feature names in a DataFrame; isolate missing-artifact tests with an empty temporary registry. A new regression test fits a real named-column transformer and exercises single and batch scoring. The legacy service remains optional research infrastructure; it is not needed by Clearcut.

The historical `reports/model_comparison.md` records every anomaly model missing its constraints. Its saved Isolation Forest test precision is 0.0493 at its chosen threshold despite ROC-AUC 0.9433. These are historical saved results, not freshly reproduced scores. The new benchmark makes a separate equal-capacity comparison and reports its exact configuration.

## Kept and changed

Kept the dataset provenance, chronological-evaluation principle, anomaly baseline and original research code. Replaced the product workflow with an API-free scored-batch review workbench. No unsupervised detector is represented as a generally superior fraud model; the supervised candidate explicitly depends on matured fraud labels.

Existing default history includes automated coauthor trailers in 14 commits. History is preserved. New terminal-created commits and pull request text are checked by `scripts/check-attribution.mjs`; `.githooks/commit-msg` rejects disallowed attribution text.
