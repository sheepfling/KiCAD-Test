# Production-scaffold baseline review

This is a technical completion review of the reusable workflow on 2026-09-08.
It records code and test evidence; it is not an independent human PR approval or
approval to manufacture any of the synthetic reference designs.

## Requirement coverage

| Requirement | Reviewed implementation and evidence |
| --- | --- |
| Folder purpose and standalone boards | [Folder standard](REPOSITORY_STRUCTURE.md), `discovery.py`, `scaffold.py` and `test_islands.py`; no product is required for board checks or releases |
| BOM and generated-output ownership | [BOM policy](BOM_POLICY.md), repository classification and generation checks; forced exports fail and fresh generation does not change tracked source |
| Parallel docs, project and product tests | `project_tests.py` isolates each suite in a process; island tests cover duplicate module names, failing local suites and dependent products |
| Extensible shared automation | Typed manifest/test contracts, shared toolchains, automatic CI matrix and documented [test extension](../tests/README.md) |
| Temporary real-project imports | [Demo rehearsal](DEMO_REHEARSAL.md): 35 imported designs, independent preservation suites, real native execution and deliberate failures; external designs remain uncommitted |
| Safe adoption and company licensing | `initialization.py`, `template.py`, `licensing.py`; lifecycle tests cover empty catalogs, rollback, repeatability, custom notices and the company's first commit |
| Standalone release and recovery | `evidence.py`, `releasing.py`, `release.py`, `packaging.py`; actual source hashes, retained report verification, package inventory and isolated restore |
| Meaningful failure handling | Missing, altered and stale evidence, wrong component identity, corrupt archives, unsafe paths, failed local suites and seven actual native defects are rejected |
| Team policy | `catalog/team-policy.json` and governance tests require the configured actors and independent review; production records cannot be supplied by training metadata |
| Versioning and deliberate upgrades | Package/module/contract metadata identify 1.0.0; migration tests exercise earlier adopter versions even after the current contract changes |

## Observed hosted acceptance

The [complete candidate run](https://github.com/sheepfling/KiCAD-Test/actions/runs/34260265342)
validated code at `923f93fc0aa884d43ca5a40e2445911bc8c9aac8` through the PR integration
checkout. All three operating-system jobs passed 182 shared tests (one Unix-only
test skipped on Windows). All six pinned KiCad lanes, seven native defect probes,
standalone release/package/restore and `Template acceptance` passed. Ten artifacts
were retained. Version-metadata and release-note changes require their own final run.

The [missing-source run](https://github.com/sheepfling/KiCAD-Test/actions/runs/34256642991)
failed the final required gate and retained failure reports on all three platforms.
The [empty-fork run](https://github.com/sheepfling/KiCAD-Test/actions/runs/34256840465)
passed scaffold checks with an empty matrix and explicitly skipped hardware validation.
Both probe PRs are closed and unmerged. External demo designs were used locally and
were not uploaded to either probe.

The original demo collection was rechecked during this review: all 719 files still
match the hashes recorded before rehearsal. Detailed receipts and reports remain in
ignored local storage; the baseline contains the authored workflow and synthetic
regression inputs.

## Publication result

[PR #3](https://github.com/sheepfling/KiCAD-Test/pull/3) was merged at
`37632266cb8b45631297e3ff7f6d1adb04cd41f2`. The
[post-merge acceptance run](https://github.com/sheepfling/KiCAD-Test/actions/runs/34266735257)
passed at that exact commit, and the annotated `v1.0.0` tag resolves to it. The run
retained ten review artifacts. This completes the versioned technical baseline.

## Remaining operational acceptance

GitHub reported `main` as unprotected after publication and PR #3 had no submitted
independent review. Configure branch enforcement and rehearse it with actual team
accounts before treating an adopted repository as production controlled. These
controls cannot be inferred from a passing workflow or a JSON governance record.
See [GitHub governance](GITHUB_GOVERNANCE.md).

Each adopting team must separately supply its actual engineering requirements,
reviewers, hosted permissions, release authority and durable artifact retention.
None of the workflow fixtures supplies those operational approvals.
