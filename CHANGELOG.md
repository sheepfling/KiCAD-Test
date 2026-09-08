# Scaffold changelog

These versions describe the reusable workflow, independently of board and product
revisions. See [versioning](docs/VERSIONING.md) and [adoption](docs/TEMPLATE_ADOPTION.md).

## 1.0.0 — candidate

The implementation is prepared for baseline review. Publication of the `v1.0.0`
annotated tag remains pending; this heading is not evidence of a published release.

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

The [baseline review](docs/BASELINE_REVIEW.md) maps the requested workflow to source,
tests and hosted evidence, and lists the remaining publication requirements.
