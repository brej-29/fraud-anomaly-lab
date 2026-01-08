# Evaluation plan — specified before implementation

Primary question: can a labeled, supervised ranker allocate scarce reviews more effectively than the original normal-only anomaly approach?

Primary operating point: floor(0.005 × holdout size) reviews. Success requires recall ≥ 60%, precision ≥ 15%, and recall ≥ 10 percentage points above normal-only Isolation Forest at exactly the same review count. A failure is published, not retuned away.

Data: original local `data/raw/creditcard.csv`, ULB/Worldline September 2013 European card payments. Stable chronological sort by Time; first 60% training, next 20% validation, final 20% test. Ties at boundaries moved into the later partition. Check duplicate feature rows crossing partitions and report them. Fit scaling on training only. Do not resample test data. No test-driven model selection.

Candidates: class-balanced logistic regression with all V1–V28 features and log1p(Amount); same regression without Amount (ablation). Select between these using validation average precision at seed 17. Baselines: normal-only Isolation Forest, amount descending, analytical expected random selection. All model and service IDs live in configuration. Repeat stochastic models with seeds 17, 29, 43. Preserve every run.

Metrics: average precision (AP, step-integral, not trapezoidal PR-AUC), ROC-AUC, precision/recall at fixed capacity, false-positive review counts, missed fraud counts. Wilson 95% intervals describe observed proportions, not future guarantees. Paired row bootstrap (1,000 samples) estimates recall-difference uncertainty for fixed trained scores and fixed review count; it does not capture model retraining, temporal dependence or institution shift. Include errors by amount bucket and chronological half of holdout. Include the legacy saved report as unverified historical evidence, separate from fresh reruns.

Only aggregate curves and statistics are published. No raw transaction rows, model binaries, financial identifiers or credentials. Users obtain the dataset under its own terms; reproduction must check SHA-256 and row counts. The interface consumes existing scores; benchmark rankers are offline experiments, not a production fraud service.
