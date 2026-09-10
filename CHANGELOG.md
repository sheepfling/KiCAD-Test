# Scaffold changelog

These versions describe the reusable workflow, independently of board and product
revisions. See [versioning](docs/workflow/VERSIONING.md) and [adoption](docs/workflow/TEMPLATE_ADOPTION.md).

## 1.2.0 — 2026-09-10

- Replace hand-built project, import and release-review Markdown with shared typed
  SnakeMD document builders.
- Pin SnakeMD 2.4.1 at runtime and snakemd-stubs 2.4.1.0 for strict static analysis.
- Add deterministic generator contracts for links, native paths, lists, inline code
  and final-newline behavior.
- Separate scaffold guidance under `docs/workflow/` from adopter-owned material under
  `docs/team/`, with a single documentation map at `docs/README.md`.
- Remove dated audit, rehearsal and acceptance reports from the distributable source;
  their evidence belongs to pull requests, CI artifacts and releases.
- Enforce the documentation namespaces in the typed Markdown policy and move its
  configuration to `catalog/`.

Existing 1.1.0 adopters can preserve all project and catalog records. Apply the
updated Python tools and dependency pins, move reusable scaffold guides to
`docs/workflow/`, place organization-wide docs under `docs/team/`, update local
links, and follow the 1.1.0-to-1.2.0 migration.

## 1.1.0 — 2026-09-09

- Require the same Python 3.12 minimum locally, in package metadata and in CI.
- Add a read-only environment doctor and a one-command fresh-fork adoption path.
- Print the complete release archive SHA-256 after package and restore verification.
- Add a concrete first-board path and durable release-storage checklist.
- Schedule bounded monthly Python and GitHub Actions dependency-update pull requests.
- Move checkout and artifact upload to their Node 24 action releases while retaining
  immutable commit-SHA pins.
- Correct the 1.0 publication record and surface the repository's remaining hosted
  governance responsibilities.

Existing 1.0.0 adopters can preserve their project layout and live catalogs. Follow
the short 1.0.0-to-1.1.0 migration to update the policy environment and tools.

## 1.0.0 — 2026-09-08

The reviewed baseline is published as the annotated `v1.0.0` tag at
`37632266cb8b45631297e3ff7f6d1adb04cd41f2`. The post-merge
[hosted acceptance run](https://github.com/sheepfling/KiCAD-Test/actions/runs/34266735257)
passed all portable, pinned KiCad, failure-probe and release/restore jobs.

- Repeatable project islands keep each deliverable's source, docs, tests and optional
  firmware together. Discovery adds projects and native CI lanes automatically.
- Fresh initialization creates empty live catalogs while retaining independent
  regression examples. Bootstrap and import use staged copies and preserve source.
- Working BOMs, schemas, native exports and reports are generated into ignored
  output locations. Authored BOM inputs and frozen release records have explicit owners.
- Shared, project and product suites run through one portable entry point. CI covers
  Windows, macOS and Linux, pinned KiCad checks, deliberate faults and release restore.
- Standalone releases bind source commits, component identities, native outputs and
  retained evidence. Packages carry source history and verify an independent restore.
- Team controls are configurable. Actual reviewers, hosting enforcement and
  manufacturing approvals remain the adopting team's responsibility.
- The original scaffold is available under 0BSD. Bootstrap removes only the known
  root notice before a company's first commit; custom and nested licenses survive.

Existing 0.3.0 adopters follow the forward migration without replacing live projects
or company licensing. Earlier versions follow the intervening plans. Keep the old
adoption version until review and verification finish.
