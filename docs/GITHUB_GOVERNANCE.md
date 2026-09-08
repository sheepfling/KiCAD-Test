# GitHub governance and role separation

Repository files can document and gate the expected policy, but only GitHub can
enforce branch protection and permissions. Before a project is promoted to the
`production` assurance profile, create `projects/<project-id>/releases/governance.json` from
`templates/github-governance.example.json` and replace every placeholder.

The production lint requires a protected branch, exact required check names, branch
protection evidence and release authority. `catalog/team-policy.json` defines the
minimum actor count, independent-review requirement and required status checks.
The default needs two people: an author and an independent reviewer; either may
integrate. Teams can adopt stricter separation or an explicitly reviewed solo policy
by changing that file and its rationale. Case differences cannot create extra actors.

## Configure in GitHub

For the default branch, configure and verify:

1. Pull requests are required; direct pushes and force-pushes are blocked.
2. At least one independent approval is required, stale approvals are dismissed when
   new commits arrive, and the branch is up to date before merge.
3. The exact KiCad CI checks named in the governance record are required.
4. Code-owner review is required after `.github/CODEOWNERS` is populated with real
   users or teams. This repository intentionally ships only `CODEOWNERS.example`
   because it must not invent the team's identities.
5. Only named maintainers may merge; release tags and release artifacts follow the
   separately recorded release authority.

Record the GitHub settings URL, API output reference, or approved screenshot in the
governance record's `branch_protection_evidence`. Test the actual configured roles
and independent-review rule. Also rehearse a rejected check,
conflict handoff, access revocation, and release restore before relying on it.

## Tool access

Use `gh auth status` before trying to read or alter repository settings. A valid token
with repository-administration scope and the actual reviewer/team identities are
required to apply this policy; they are intentionally outside this template.
