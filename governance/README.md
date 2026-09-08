# Production governance records

Each production-profile project must have one reviewed JSON record in this directory.
Start from `templates/github-governance.example.json`, replace every placeholder with
real identities and evidence, and reference the result from that project's registry
entry. The static gate checks the record; GitHub branch protection and permissions
must be configured separately as described in `docs/GITHUB_GOVERNANCE.md`.
