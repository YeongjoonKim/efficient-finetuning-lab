# Security policy

This is an offline reconstructed example, not a production service. Only the default
standard-library sample is tested locally. Do not add real records, credentials,
private model artifacts or production configuration. Do not expose it to the internet.

## Reporting

After publication, use GitHub's **Report a vulnerability** if private reporting has been
enabled. Never post secrets or sensitive reproduction data in public issues. If that
channel is unavailable, request a private reporting channel without sensitive details.
No response-time guarantee or active security support release is claimed.

## Checks and limits

Run `python3 scripts/check_repository.py`: syntax, local Markdown targets, JSON and
heuristic credential patterns, including reachable Git history. This is not a specialist
secret scanner, semantic source audit, external-link check or proof of absence.

Before publication: owner/IP review, clean staged tree, author-email review, all local
checks, then review public files and logs. After publication: verify secret scanning,
push protection, private vulnerability reporting and dependency alerts in Settings.
Review CodeQL default setup for Python; activation is pending, not claimed here.
CI uses read-only contents permission, pinned actions and no repository secrets.
Optional model training is outside CI and must use an isolated approved environment.
