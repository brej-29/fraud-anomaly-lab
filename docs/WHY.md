# Why Clearcut exists

Clearcut helps someone with an existing fraud score answer a concrete question: **with this many reviews, how much known fraud enters my queue, and how many legitimate payments come with it?** It is a private retrospective workbench, with an exportable ranked batch. It does not score or act on live payments.

## Why this problem, and who has it

The intended user is a fraud analyst or ML practitioner evaluating a scored transaction batch under a finite manual-review budget. This audience is an inference from the original project and published operational guidance; there have been no customer interviews or production deployments with fraud teams. [Stripe's review guidance](https://docs.stripe.com/radar/transaction-reviews) describes both the value of human review and the risk of delaying legitimate customers.

The repository supplied a reproducible local symptom: a dashboard that asks for 30 numerical features in JSON, a broken named-column inference path, and a saved report where every anomaly detector missed its constraints. The historical Isolation Forest report pairs ROC-AUC 0.9433 with precision 0.0493 at its saved threshold. Those saved numbers are contextual evidence; the new experiment is independently rerun at an equal review budget. See [starting-state audit](BASELINE.md).

## Why now

Fraud review is not new, and this project does not claim a new fraud threat or regulatory mandate. The practical opening is that a browser can parse, sort and evaluate bounded scored batches without sending financial records to a service, while a public static project can be hosted on an existing free account. [GitHub documents free public Pages availability](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages); [standard hosted CI is free for public repositories](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

This is an architecture and access advantage for a narrow workflow, not proof of market timing. Modern commercial systems already offer sophisticated review and rule testing; the opportunity hypothesis is that some users need a portable, integration-free comparison before adopting or changing those systems.

## Why not the alternatives

The criteria below apply consistently: whether a user supplies existing scores, where batch processing happens, how equal-capacity evidence is obtained, and what downstream actions exist. “Not established” means the cited public material did not establish that capability, not that the product cannot provide it.

| Alternative | Existing scores | Processing boundary | Equal-capacity evidence | Payment/investigation actions |
|---|---|---|---|---|
| Clearcut | CSV, any finite higher-is-riskier score | Browser memory, 12 MiB / 100k rows | Built-in score and amount curves, counts, intervals | Local queue export only |
| [Stripe Radar reviews and rule testing](https://docs.stripe.com/radar/transaction-reviews) | Uses integrated risk context; [rule testing](https://docs.stripe.com/radar/testing) available | Integrated Stripe system | Test rules and inspect outcomes; identical portable CSV top-k workflow not established | Review, approve, refund and report fraud |
| [Adyen Protect](https://docs.adyen.com/risk-management) | Integrated risk profiles and rules | Adyen account/integration | Rule backtests, analytics and experiments; portable local CSV workflow not established | Allow, block, review; premium case management |
| [Sift](https://developers.sift.com/docs/v204) | Score APIs, event and outcome integration | Connected service and console | Sophisticated console and workflows; identical local top-k tool not established | Decisions and review workflows |
| Excel or LibreOffice sort/filter | Yes | Local desktop (or cloud, depending on app) | Easy top-k sorting; consistent counts, label checks, intervals and multiple policies need formulas | Manual export |
| Python + pandas / scikit-learn | Yes | User-controlled environment | Most flexible; user writes and verifies evaluation code | Whatever the user implements |
| Off-the-shelf Isolation Forest | Requires features, not just scores | User-controlled training/inference | A ranker alone does not define workload; new benchmark catches 35/75 at 284 reviews | No review system by itself |

A spreadsheet is a strong alternative for occasional expert use. Clearcut earns its place only if explicit validation, a visible capacity curve and instant comparisons make the recurring task clearer. Commercial platforms should remain the choice when investigations, organization-wide permissions, live decisions or payment integrations are required; Clearcut has no evidence of replacing them.

## Why this approach and stack

The useful input is a score from a system the user already has. A local web worker validates the full file, then computes stable top-k profiles; native controls, semantic tables and an SVG capture curve expose the decision. The next-best architecture is the original FastAPI/Streamlit split, but that adds server uploads and deployment dependencies while the current main operation is sorting and counting. [Architecture notes](ARCHITECTURE.md) explain the boundary.

Vite builds static assets, Papa Parse handles real CSV quoting, and self-hosted DM Sans avoids runtime font services. We examined shadcn/Recharts and Motion; native controls and a small SVG were enough, so extra framework and animation dependencies did not earn their runtime cost. Python/scikit-learn remains the offline measurement environment. No hosted model IDs, GPU quotas, inference keys or paid fallbacks are required; ranker IDs and parameters live in [configuration](../evaluation/config.json).

## What the numbers show

The [evaluation plan](EVALUATION_PLAN.md) specified the operating point and targets before implementation: at 0.5% capacity, ≥60% recall, ≥15% precision and ≥10 percentage points of recall above normal-only Isolation Forest. This is an author-controlled plan, not an independently registered study. The requested historical commit-date simulation is not evidence of when experiments were run.

The stable chronological split has 170,882 training, 56,963 validation and 56,962 test transactions; timestamp ties move into the later partition. There are 75 confirmed frauds in test, so 0.5% capacity means floor(56,962 × 0.005) = **284 reviews**. Choose logistic versus its no-amount ablation using validation AP only. Full results and versions are in [benchmark.json](../reports/benchmark.json) and the [evaluation report](../reports/EVALUATION.md).

| Strategy | AP | Recall @ 284 | Precision @ 284 | Fraud caught | Legitimate reviews |
|---|---:|---:|---:|---:|---:|
| Logistic regression | 0.7461 | 85.3% | 22.5% | 64 | 220 |
| Logistic without amount | 0.7451 | 85.3% | 22.5% | 64 | 220 |
| Isolation Forest, seed 17 | 0.0793 | 46.7% | 12.3% | 35 | 249 |
| Largest amount first | 0.0014 | 1.3% | 0.4% | 1 | 283 |
| Random selection, analytical expectation | prevalence | 0.499% | 0.132% | 0.374 expected | 283.626 expected |

The target is met on this holdout. Logistic recall is identical across three seeds because this solver is deterministic; those are reproducibility checks, not three independent generalization studies. Isolation Forest recall is 46.7%, 42.7% and 41.3%. The paired fixed-score row-bootstrap 95% interval on recall lift is 26.7–48.7 percentage points; logistic's Wilson recall interval is 75.6–91.6%.

The amount ablation is a useful negative result: amount contributes little at this operating point. Feature hashes also reveal overlap across chronological splits. Removing all 1,722 test rows seen in either earlier partition leaves 55,240 rows and 75 frauds; recall remains 85.3% at 276 reviews. This sensitivity check reduces one leakage concern, but does not establish the provenance of the supplied PCA transformation.

## What the numbers do not show

- **Label advantage:** logistic receives training fraud labels, while Isolation Forest trains on normal-only examples. The comparison concerns operating regimes; it does not isolate algorithm quality under equal supervision.
- **Age and scope:** two days of 2013 European payments do not represent a modern merchant. No card identities, merchant categories, original PCA features or fitted-PCA provenance are available.
- **Small positive count:** 75 test frauds and row-level intervals do not capture correlated campaigns, model retraining uncertainty, delayed labels or future drift.
- **Review is not recovery:** 220 of the 284 selected payments are legitimate, and 11 frauds are outside the queue. Nothing here measures analyst accuracy, review time, customer abandonment or recovered money.
- **Uneven errors:** recall is 88.7% in the earlier test half and 77.3% in the later half; above amount 100 it is 73.3%. These tiny segment counts are diagnostic, not reliable subgroup guarantees.
- **No adoption evidence:** the workflow is browser-tested, not validated in fraud-team user research. An attractive interface cannot establish that it improves a real analyst's decisions.

## What would prove the idea wrong

For the ranker claim, failing any predeclared target on the held-out data would reject this experiment's success condition; it did not fail here. For the product hypothesis, test with five intended users on their own matured, anonymized scored batches: each must import without help, correctly identify false-positive review cost and export a chosen budget. If fewer than four complete all three tasks without coaching, the current workflow fails the proposed usability criterion; that study has not been run.

Next, collect recent longitudinal scored batches with explicit label-maturity windows and compare the chosen budget prospectively against an analyst's existing policy. Add block-bootstrap or rolling-window uncertainty and a comparison-score column before adding a more complex ranker. If users consistently prefer their spreadsheet or integrated provider and gain no decision clarity, keep the evaluation library and retire the hosted UI rather than inventing a market.

## Fifteen hard questions

### 1. Is this just sorting a CSV?

Sorting is the mechanism, and it is deliberately simple. The added workflow is strict file validation, equal-capacity policy comparison, unknown-label handling, uncertainty and safe export, covered by the core and browser tests. Whether that saves an analyst meaningful effort remains a user-study question.

### 2. Why does a high ROC-AUC not solve the problem?

ROC-AUC averages ranking across all thresholds, including review volumes nobody can staff. The fresh Isolation Forest run reaches ROC-AUC 0.9520 but catches only 35 frauds in 284 reviews. The comparison table keeps the review denominator fixed so that failure is visible.

### 3. Did you improve the model by giving it answers the baseline lacked?

The supervised candidate receives historical training labels; the anomaly baseline does not. That is disclosed as a comparison of two information regimes, not a controlled algorithm superiority claim. Users without matured labels must not expect the supervised result.

### 4. Did you tune against test data?

Configuration and success criteria are written in the evaluation plan, and the candidate is selected solely by validation average precision. Both candidates and all seeds are retained in the report, including the almost unchanged no-amount ablation. No model-search claim or independently timestamped preregistration is made.

### 5. Could duplicates explain the improvement?

The feature-hash audit finds 1,722 test rows that also occur in training or validation. Excluding them leaves all 75 frauds and the same 85.3% recall at the adjusted 0.5% budget. Duplicate positives therefore do not explain this result, while unknown upstream PCA fitting remains a separate limitation.

### 6. Why use a dataset from 2013?

It was the original project's local, labeled dataset and supports a reproducible diagnosis of the queue-budget failure. It cannot validate contemporary fraud protection, merchant-specific performance or deployment safety. The import workflow exists so users can test recent scored batches without accepting its baseline as their own.

### 7. Are the intervals overstating certainty?

The interface labels Wilson intervals as historical sampling uncertainty. The paired bootstrap resamples rows from fixed test scores, so it excludes correlated fraud campaigns, refitting and distribution shift. The interval is useful for interpreting a 75-positive holdout, not a service-level guarantee.

### 8. What happened to the eleven missed frauds?

They remain outside the 284-row queue and are reported explicitly. Six are in the amount ≤25 bucket, one in 25–100 and four above 100; the later temporal half has lower recall. Expanding the budget captures more cases but sends many more legitimate payments to review, which the live curve makes visible.

### 9. What if my labels are absent, delayed or biased?

Without labels, the app exposes only queue volume and selected rows; it does not invent recall or precision. A present label column must contain complete binary values on every row. Users must supply matured, consistently defined outcomes; selection-biased or delayed labels can invalidate the interpretation even when the CSV is syntactically valid.

### 10. Can I use the exported score cutoff on tomorrow's traffic?

The product exports a ranked batch or aggregate report, not a recommended prospective cutoff. A top-k batch can include only part of a tied score group, and future score distributions can drift. A streaming policy needs separate time-window validation and capacity controls.

### 11. Does the private-data claim survive inspection?

The runtime has no upload endpoint, analytics or external font requests. The web worker processes in memory, the export occurs locally, and browser tests check that the import flow issues no non-GET network requests. The static host still receives ordinary page requests and may log visitor IP addresses under [its documented practices](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

### 12. What happens with malicious or enormous files?

Size and row limits reject unbounded batches, numeric and label validation reject malformed rows, and all imported identifiers are HTML-escaped. Export neutralizes spreadsheet formula-like identifiers, while tests cover quoting, duplicate IDs, invalid labels, inert HTML and formula injection. A browser tab can still run out of memory on a constrained device; the 12 MiB/100k bound is a guardrail, not an unlimited-processing promise.

### 13. Why not buy Radar, Protect or Sift?

Those products provide integrated signals, case workflows and real operational actions that Clearcut does not attempt. Clearcut's specific advantage is an integration-free local batch comparison from existing scores. There is no evidence here that it reduces a provider's fraud losses or replaces its investigations.

### 14. What keeps this running when free quotas change?

There is no online model or server process to sleep, and no service key to exhaust. The static build can be served by any ordinary file host; the current loaded tab continues calculating offline. Hosting availability and first-load network access remain dependencies, and published limits are documented in the README rather than hidden behind an unavailable fallback.

### 15. What is the strongest reason not to build more yet?

The benchmark proves an equal-capacity ranking result, not product demand or analyst efficiency. Before adding accounts, payments integration or more models, run the proposed unassisted task study and recent-batch validation. A failed study should simplify or retire the interface rather than be explained away in the case study.
