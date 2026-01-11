# Clearcut

**Make every fraud review count.** A private browser workbench for turning existing risk scores into a review budget, an honest trade-off, and an exportable queue.

[Open the workbench](https://brej-29.github.io/fraud-anomaly-lab/) · [Why this exists and 15 hard questions](docs/WHY.md) · [Evaluation](reports/EVALUATION.md) · [Architecture](docs/ARCHITECTURE.md)

## The problem

A high ranking metric does not tell a team how many legitimate payments it must review. The original anomaly lab made that gap concrete: every saved detector missed its acceptance constraints, and the single-prediction UI required 30 numerical features pasted as JSON. [The baseline audit](docs/BASELINE.md) records the installation, failing test and repaired preprocessing contract.

Clearcut makes the actual decision visible: **if I can review 0.5% of this batch, what enters the queue and what stays outside?** Start with a real historical aggregate benchmark, move the capacity slider, compare strategies at the same review count, then open a scored CSV to do the same calculation on your device. With labels, see measured precision, recall and misses; without them, outcomes remain unknown.

## Evidence and result

The [plan](docs/EVALUATION_PLAN.md) specified ≥60% recall, ≥15% precision and ≥10 percentage points of recall improvement over normal-only Isolation Forest at 0.5% review capacity. Chronological train/validation/test splits use the original [ULB/Worldline dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud); candidate selection uses validation only. No test resampling or synthetic rows inflate the holdout.

On **56,962 test payments, 75 confirmed frauds, 284 reviews**:

| Strategy | Fraud caught | Recall | Precision | Legitimate reviews |
|---|---:|---:|---:|---:|
| Logistic regression | **64** | **85.3%** | **22.5%** | 220 |
| Logistic without amount | 64 | 85.3% | 22.5% | 220 |
| Isolation Forest, seed 17 | 35 | 46.7% | 12.3% | 249 |
| Largest amount first | 1 | 1.3% | 0.4% | 283 |
| Random selection, expected | 0.374 | 0.499% | 0.132% | 283.626 |

The target is met on this historical holdout. Recall lift is **38.7 percentage points**, with a paired fixed-score row-bootstrap 95% interval of **26.7–48.7 points**. The selected model still misses **11 frauds**. Logistic has historical labels the anomaly baseline lacks; this compares information regimes, not an equally supervised model contest.

Three seeded runs reproduce the deterministic logistic result; anomaly recall varies from 41.3–46.7%. Removing amount barely helps or hurts. Removing test feature rows seen in earlier partitions leaves recall unchanged at 85.3%. Error analysis finds lower recall later in the holdout and for amounts above 100. Full counts, checksums, versions and uncertainty live in [the report](reports/EVALUATION.md) and [machine-readable evidence](reports/benchmark.json).

**Limits:** two days of European payments from 2013, only 75 test frauds, unknown upstream PCA-fitting provenance, no merchant context or production validation. Capture is not money recovered. This product consumes existing scores and never approves, declines or refunds payments. No fraud-team adoption or time-saving claim has been validated.

## Use it

1. Open the live workbench and inspect the benchmark's capacity curve.
2. Choose **Import scored CSV**. Required columns: `score,amount`; optional: `id,label`. Larger scores mean more suspicious. Labels must be 0 or 1 on every row, or omitted entirely.
3. Set a review budget, compare score versus amount ranking, inspect the selected rows, and export the queue. The downloadable tutorial is explicitly synthetic and separate from the benchmark.

```csv
id,score,amount,label
reference-a,0.92,42.50,1
reference-b,0.13,18.00,0
```

This two-row snippet documents the schema. Use the 2,000-row tutorial to explore a meaningful sub-5% review budget. Limits: 12 MiB, 100,000 rows, nonnegative amounts, finite scores and unique IDs. Invalid files are rejected as a whole. Scores can have arbitrary scale; they are not assumed to be calibrated probabilities.

## Run and test

Node 24 is used in CI; Vite requires Node ≥22.12 on the 22.x line.

```bash
npm ci
npm run dev
```

```bash
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

On Windows use `npm.cmd` and `npx.cmd` if PowerShell blocks their script wrappers. The browser suite covers benchmark → capacity → import → queue → export at 390, 834 and 1440 pixels, malformed input, unknown outcomes, offline use in a loaded tab, fetch recovery and automated WCAG checks. [Validation evidence](docs/VALIDATION.md) records screenshots, performance measurements and review findings.

Reproduce the offline experiment with Python 3.11:

```bash
python -m venv .venv
# Activate the environment using your operating system's command.
python -m pip install -r evaluation/requirements.txt
# Obtain the original dataset under its terms; place creditcard.csv in data/raw/.
python evaluation/run.py
python -m pytest evaluation -q
```

No dataset credentials are read by this evaluator. It checks the original 284,807-row/492-fraud counts and records SHA-256; only aggregate output is written. Benchmark data licensing and original research citations are in [sources and terms](docs/SOURCES.md). Code is MIT; source data has its own license.

For optional legacy research, install `backend/requirements.txt` and `ml/requirements.txt`, then run `python -m pytest backend ml evaluation -q`. `backend/`, `dashboard/`, `ml/` and `notebooks/` preserve the original work; the live product does not call those services. Historical deployment guides describe those optional services, not the current production deployment.

## Deployment and privacy

Live URL: **https://brej-29.github.io/fraud-anomaly-lab/**. The `Publish` workflow builds and browser-tests `main`, deploys static assets through GitHub Pages, then runs a real browser smoke test including tutorial import and CSV export. No new account, card, inference subscription or paid resource is required.

[Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits): 1 GB published site, soft 100 GB/month bandwidth, 10-minute deployment timeout; the 10-build/hour soft limit does not apply to custom Actions publishing. Limits and eligibility can change. This is a public project workbench, not a transactional payment service. Standard hosted runners are free for this public repository under [current Actions terms](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

CSV parsing and profiling run in a local web worker; rows live only in this tab's memory. No analytics, account or upload endpoint exists. The static host receives page requests and [may log visitor IPs](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages); the app sends it no CSV contents. The loaded workspace can calculate offline, but a fresh load or offline reload is not guaranteed. A failed benchmark fetch shows an explicit retry screen; no paid fallback is configured.

## Project map

| Path | Purpose |
|---|---|
| `src/` | Browser UI, validation/ranking core and local worker |
| `evaluation/` | Offline models, fixed configuration and measurement tests |
| `public/benchmark.json` | Real aggregate evidence shipped with the app |
| `tests/` | Core-logic and browser-flow tests |
| `docs/WHY.md` | Problem, alternatives, falsification criteria and 15 defenses |
| `docs/ARCHITECTURE.md` | Boundaries, decisions and failure modes |
| `reports/` | Results and quality measurements |

Future work should test five analysts on their own recent matured batches before adding more models or integrations. The proposed task-study threshold and reasons to retire the idea are in [WHY.md](docs/WHY.md).
