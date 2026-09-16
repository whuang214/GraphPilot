# 12 Security and Privacy

## Backend-Only Secrets

Azure OpenAI secrets belong only in backend configuration.

Rules:

- frontend must never receive Azure OpenAI keys
- frontend must never store backend secrets
- backend `.env` and backend runtime config own the model credentials

## No Frontend Secrets

Frontend configuration should contain only public or local UI configuration such as API base URL and app display values.

## Local File Safety

GraphPilot is local-file-based, so file access must stay controlled.

Rules:

- do not expose arbitrary local file reads through query parameters
- do not expose arbitrary local file writes from the UI
- keep preview cache and blueprint directories under backend-owned control

## PreviewId Instead of Raw Paths

Preview loading must use `previewId`, not raw file paths.

This helps prevent accidental exposure of arbitrary local files.

## Prompt and Data Sensitivity

Prompts and diagrams may contain internal system design information.

Operational expectations:

- treat prompts and generated diagrams as internal engineering artifacts
- avoid placing secrets directly in prompts when not needed
- keep output handling local-first for MVP

## Optional Usage Logs

Usage logging may exist as an optional local capability.

If enabled:

- keep logs local
- avoid storing secrets in logs
- keep usage logging clearly separated from active diagram content

## No Auth in MVP

The MVP does not introduce users or auth.

That means security relies on local runtime boundaries, careful file access rules, and backend-only secret handling rather than identity or permission systems.
