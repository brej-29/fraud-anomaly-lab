# Product
<!-- impeccable:product-schema 1 -->
## Platform
web
## Stack
Delegated by the mission. Static Vite application, browser-local computation, offline Python evaluation. Existing Python research retained as historical evidence.
## Users
Inferred focus: fraud analysts and ML practitioners deciding how to allocate a limited manual-review capacity to scored transactions.
## Product Purpose
Turn a scored batch into an explicit capacity decision with observed fraud capture, legitimate reviews, and an exportable ranked queue.
## Positioning
A private, portable policy workbench: compare ranking strategies at the same capacity, inspect the trade-off, and export without a service integration.
## Operating Context
Historical backtesting on matured labels; users bring scores from an existing fraud model. This product does not approve, decline, or score live payments.
## Capabilities and Constraints
No money, credit card, new account, or hosted model required. Uploads stay in browser memory. Labeled CSV enables retrospective metrics; unlabeled files cannot establish precision or recall. All demonstration data identified by origin. Free public static hosting on the existing GitHub account is preferred.
## Evidence on Hand
Original anomaly report reports every model missing constraints (reports/model_comparison.md). Local ULB dataset contains 284807 rows and 492 fraud labels. Raw rows and credentials remain ignored.
## Product Principles
Equal review budgets for comparisons. Counts before persuasive claims. Preserve useful negative results. Label retrospective performance and uncertainty. Fail closed on malformed input.
## Accessibility & Inclusion
Responsive phone to wide desktop, keyboard access, screen-reader labels, WCAG AA contrast, reduced motion. Inferred audience and naming may be revised by future user evidence; the mission explicitly delegates current decisions.
