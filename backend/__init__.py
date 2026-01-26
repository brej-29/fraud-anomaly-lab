"""Backend package for the Fraud Anomaly Lab API.

When deploying to Hugging Face Spaces with the Docker SDK, a minimal
`README.md` at the repository root is often sufficient. For reference,
you can include the following front-matter snippet in a Space-specific
README if desired:

```yaml
---
title: Fraud Anomaly Lab API
sdk: docker
app_port: 7860
---
```

The `sdk: docker` setting tells Spaces to build from the provided
`backend/Dockerfile`, and `app_port` can be adjusted if needed. The
actual port used inside the container is driven by the `PORT`
environment variable (defaulting to 8000), and the Dockerfile already
respects this via:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
"""ackend package root for fraud-anomaly-lab."""