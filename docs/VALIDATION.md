# Validation record

## Functional evidence

- Original install/test baseline: 9 passed, 1 failed; see [BASELINE.md](BASELINE.md).
- Repaired research path and evaluation: **13 Python tests pass** (`python -m pytest backend ml evaluation -q --tb=short`). This includes actual named-column preprocessing for both single and batch scoring.
- Browser core: **7 Node tests pass** (`npm test`), including known confusion counts, stable ties, unknown outcomes, strict CSV rejection, quoting, spreadsheet protection and curve/direct-count agreement at every budget point.
- Product flow: **12 browser tests pass** (`npm run test:e2e`) across 390×844, 834×1112 and 1440×1000 viewports. Coverage includes historical benchmark, budget changes, private CSVs, synthetic tutorial, amount comparison, keyboard pagination, export, errors and offline calculations in a loaded tab.
- Four routes at three sizes are scanned for automated WCAG A/AA violations with axe; reduced-motion mode is enabled. This does not replace assistive-technology testing with users.
- Full offline evaluation rerun reproduced `public/benchmark.json` byte for byte: artifact SHA-256 `fd89d820f123c10f9006d16cff4f9880398a873f61f0ff1a6e4ccd504eb4f816`. Input dataset checksum is recorded inside that file.
- Dependency audit after updating the initially vulnerable build tools: **zero known npm advisories** at the recorded install. This is time-dependent, not a permanent security certification.
- Repository lint passes its explicit rules. Attribution and secret-signature scans pass; existing historical coauthor trailers are retained.

## Visual verification

`node scripts/capture.mjs` captures Workbench, Evidence, Guide, Import and the synthetic queue at all three viewport sizes. Local review evidence is kept in ignored `.local/screenshots/`; representative screenshots are in [screenshots/](screenshots/). They contain aggregate historical metrics or explicitly synthetic rows, not uploaded private records.

The initial visual/browser pass found insufficient secondary-text contrast, unlabeled icon-only navigation and non-focusable horizontal tables. These were corrected with darker muted ink, accessible link names and keyboard-focusable table regions. Phone chart geometry was adjusted to keep its labels readable instead of shrinking a desktop canvas.

An independent finish review then required visible phone destination labels, sideways-scroll cues, strategy-specific queue ordering copy and focus continuity after pagination. The second review scored all four fixes resolved, with **disposition: ship for those scored fixes**. The mechanical design detector returned no findings. Design tokens and durable component rules are recorded in [DESIGN.md](../DESIGN.md).

## Critique against three relevant products

| Reference and inspected evidence | Useful craft standard | Resulting Clearcut decision | Deliberate limitation |
|---|---|---|---|
| [Stripe Radar](https://stripe.com/radar) and [review documentation](https://docs.stripe.com/radar/transaction-reviews) | Clear hierarchy between risk observations, the queue and concrete actions | Put the capacity inspector beside a single primary curve; expose legitimate review counts before export | No imitation approval/refund buttons or implied transaction integration |
| [Adyen case management](https://docs.adyen.com/risk-management/case-management), including its queue overview | Explicit statuses and a scannable table with predictable workflow navigation | Labeled benchmark/synthetic/private states, semantic comparison tables, visible mobile destination labels | No assignees, shared case state or payment modifications |
| [Sift's product primer](https://sift.com/wp-content/uploads/2025/06/Primer_Sift-for-Streaming-Services-Fraud.pdf), page 3 console image | Dense evidence grouped by meaning, stable navigation and numbers with context | Separate source, capacity outcomes, equal-budget comparison and row inspection; retain original identifiers locally | No fabricated device, identity-network or investigation panels without supporting data |

The warm-paper/forest palette, self-hosted humanist typography and acid-green active region establish a distinct identity. Motion is limited to chart/selection transitions and status feedback, with reduced motion respected. No 3D, shader or stock illustration was added because it would not explain the budget decision.

## Performance

[Local Lighthouse record](../reports/lighthouse-local.json): mobile Lighthouse 13.6.0, production preview, **100 performance / 100 accessibility / 100 best practices / 100 SEO**, CLS 0 in that run. An earlier run was 90/100/100/92 with CLS 0.15; a stable initial skeleton removed the measured layout shift and a valid robots.txt fixed the SEO failure. These are synthetic lab measurements, not field percentiles or guarantees on every device and connection.

Run `node scripts/lighthouse.mjs` with the production preview on port 4173. Set `LIVE_URL` to measure production and write `reports/lighthouse-live.json`. The release workflow also executes a deployed browser smoke test that opens the real site, loads the synthetic CSV tutorial and completes a real queue download.

## Remaining practical limits

The app is tested in Chromium; Safari/Firefox and manual screen-reader testing have not been performed. All file rows are rejected on an invalid value; label maturity and correctness cannot be verified from the CSV alone. A loaded tab can calculate offline, while first load and refresh need hosting access; the site has no service-worker offline reload guarantee. No analyst usability study, prospective fraud trial or recovered-money measurement has been run.

Production verification initially passed all 12 browser tests and the real CSV-download smoke test. Windows-host mobile Lighthouse performance varied across four fresh profiles: 87, 100, 82, 89; the other categories stayed at 100. The full negative record is retained in reports/lighthouse-live-runs.json. Targeted rendering isolation did not establish a reliable app-level improvement, so a separate Linux-runner three-profile audit now gates production quality; each category of each run must reach 90.
