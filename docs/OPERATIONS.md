# Release and operating notes

The default branch is `main`. `Publish` builds and browser-tests the static app, publishes GitHub Pages, then exercises the public URL with `npm run smoke` and three fresh-profile mobile Lighthouse audits. Every category in every audit must reach 90; the bounded result is retained as an artifact for seven days. `Workbench` and `Evidence` check pull requests. No cloud resources beyond the existing public repository and its Pages site are required.

Runners are pinned to Ubuntu 24.04. Their published [browser-equipped image](https://github.com/actions/runner-images/blob/ubuntu24/20261101.360/images/ubuntu/Ubuntu2404-Readme.md) already provides Chrome's system libraries; workflows download the pinned Playwright browser without a redundant operating-system package update. Browser installation is bounded to three minutes and jobs to ten minutes. This replaced a stalled package-update step during release verification. The image manifest also announces a November 2026 default-Ubuntu transition, so the OS version is explicit.

## Local quality commands

```bash
npm ci
npm test
npm run build
npx playwright install chromium
npm run test:e2e
node scripts/check-attribution.mjs
node scripts/check-secrets.mjs
```

Install the repository commit guard with `git config core.hooksPath .githooks`. All release commits are made through the terminal and pull requests through the authenticated repository CLI; automatic commit/PR composition surfaces are not used. The local hook rejects disallowed attribution text, and the release scan checks new commit messages, changed files and the exact PR body before push. The official tool configuration reference did not establish a supported built-in attribution-disable key during this build; no unverified setting was invented.

Existing default-branch coauthor trailers were reported and retained. No history was rewritten. The task requested a simulated January 2026 commit timeline: new commits explicitly set both author and committer timestamps, advancing 1–4 randomized days after the first. Those dates are historical simulation metadata, not experimental preregistration or the actual deployment date.

## Publishing

Pages uses the existing account, public repository and workflow source. The live URL is `https://brej-29.github.io/fraud-anomaly-lab/`. Use the same source and `npm run build` with another ordinary static host if terms change. The output is `dist/`; serving requires no Python service, secrets, application database or paid model.

Before merging a release, obtain green PR checks. Integration can fast-forward `main` to the reviewed head; this preserves explicitly assigned commit timestamps and GitHub marks the PR merged. Never force-push the default branch. For rollback, use a new reviewed revert commit and redeploy; the starting tag is `backup/starting-state-2026-11-05`.

## Incidents and limits

A failed benchmark fetch gives a retry screen. A malformed or oversized CSV is rejected locally; close/reload the tab to clear imported rows. A local worker failure asks for reload. No paid fallback or automatic upload exists. When the static host rate-limits or is unavailable, retry later or run the static build locally; cached state is not promised across reloads.

Raw ULB data and model binaries remain ignored. Keep credentials in platform or local environment settings, never in the committed tree. The signature scan reports file and key type only and cannot discover every secret format. No matching committed secret signatures were found during this build.
