# Security and Provenance

## Old repository warning

The former repository contains credentials in files and Git history, including a Kaggle token and a GitHub personal access token embedded in a remote URL. They must be revoked/rotated. They are not copied into this repository and must never be pasted into issues, commits, notebooks, or chat.

The new repository uses environment variables or a local untracked `.env` file. A future `.env.example` may document variable names, never values.

## Provenance rules

- Record URLs, commit SHAs, dataset versions, and download dates.
- Preserve licenses and attribution for upstream code/data.
- Do not commit downloaded scroll volumes or model weights unless explicitly permitted and small enough for the repository.
- Keep generated reports deterministic where possible.
- Treat external data and third-party scripts as untrusted until checksummed and tested.

