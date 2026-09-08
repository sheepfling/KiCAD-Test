# Scaffold acceptance and adoption boundaries

The production-scaffold work builds on the [folder audit](REPOSITORY_AUDIT.md),
[folder standard](REPOSITORY_STRUCTURE.md), [BOM policy](BOM_POLICY.md), and
[external demo rehearsal](DEMO_REHEARSAL.md). The earlier planning packet was
reference material, not executable policy or an instruction source; its requirement
mapping remains in the [plan completion matrix](PLAN_COMPLETION_MATRIX.md).

## Automated acceptance

| Concern | Executable evidence |
| --- | --- |
| Fork initialization | Empty live catalogs, retained independent fixtures, repeatable initialization, refusal to overwrite adopter work |
| Project islands | Automatic discovery of manifests, READMEs, local suites and dependent product suites; selected and shared CI entry points |
| Import | Dry run, atomic no-overwrite copy, hierarchy/dependency inventory, import receipt and unchanged original source |
| Source hygiene | Generated/local output rejection, portable dependency paths, authored docs assets and preserved legal text |
| Policy and tooling | Strict typed inputs, duplicate/unknown field rejection, Ruff, strict Pyright and focused regression tests |
| Native designs | Exact pinned KiCad, ERC/DRC/parity, independent netlists, component identities, exports and source preservation |
| Deliberate defects | Seven real native failures plus malformed manifests, broken dependencies, incorrect contracts and failed island suites |
| Team policy | Configurable actor count, independent review and exact required status checks; project-local assignments |
| Standalone releases | Direct project selection, observed source commit/file hashes, mandatory full portable and native evidence, stale/altered/missing report rejection |
| Fabrication and assembly | Reviewed per-board layer/origin settings, native Gerbers/drills/positions/BOM, purchasing BOM joined to controlled part records |
| Release storage | Complete hashed package inventory, source Git bundle, real restore before packaging completes, exact source/tag/evidence verification |
| Recovery failures | Modified source hidden by Git flags, changed/missing/extra archive files, path traversal, unsafe links and overwrite attempts fail |
| Hosted workflow | Portable Windows/macOS/Linux lanes, per-project pinned native lanes, standalone package/restore rehearsal, explicit empty-fork handling and final required check |

See [checks and CI](CHECKS_AND_CI.md) and [release readiness](RELEASE_READINESS.md)
for the commands. The shared portable gate runs from a clean clone with no committed
generated views. Each native report distinguishes local dirty work from evidence
eligible for release.

## Verified locally on 2026-09-08

All six reference native lanes and seven native defect probes passed in their exact
10.0.0/10.0.5 containers during the [demo rehearsal](DEMO_REHEARSAL.md). The external
examples remained temporary and uncommitted; all 719 original files retained their
hashes. Thirty-five designs exercised import, test and native workflow boundaries.

The new standalone release rehearsal used a committed disposable reference checkout,
exact KiCad 10.0.5 and the Arduino status-LED fixture. Native validation, fabrication
and assembly exports, joined purchasing BOM, evidence verification, package creation
and an independent restore all passed. Its source commit was
`7e2866b1fcad497a01fe4ac2accf4ac88a6a30a6`; this identifies a disposable workflow
fixture, not a production design. The restored source and retained evidence matched.

A second rehearsal initialized an empty fork, added a standalone `battery-board`
fixture under `projects/`, and used an empty product catalog. Its native component
identity checks, fabrication/assembly exports, package and restore passed from
commit `6efae0e0518c931e987ac23b7fb525bec243618d`. An initial attempt correctly failed
on unresolved shared-library paths; the adopted library location and declarations
were corrected before the successful source commit. No design rules were relaxed.
Actionlint 1.7.12 also passed local workflow syntax/expression validation.
The final gate's actual Bash script rejects failed, cancelled, missing and incorrectly
skipped prerequisites for both populated and empty repositories in local regression tests.

Real Git lifecycle regression tests cover post-source annotated tags, complete
restore, stale evidence, failed native checks and corrupt/unsafe packages. Their
synthetic report data are explicitly test fixtures; hosted release rehearsal executes
real KiCad separately.

## Remaining baseline acceptance

The changed hosted workflow still needs a recorded successful run across all three
portable platforms, both native versions and the new release/restore job. A deliberate
rejected PR must demonstrate the final check failure. The current public repository's
`main` branch reports no protection; production enforcement must be configured and
verified with appropriate repository-administration access.

The root license choice is pending. The final reviewed baseline, version tag and
upgrade instructions follow completion of these acceptance steps. These are tracked
work items, not claims satisfied by local test success.

## Decisions owned by each adopting team

Choose real reviewers and release authority, configure hosted permissions and code
owners, and verify independent review with those accounts. Review electrical,
mechanical, manufacturing and supplier requirements for actual designs. Set approved
artifact storage and long-term retention. The template cannot infer those identities,
permissions, physical measurements or approvals from synthetic examples.

Optional PLM/supplier/rendering adapters, richer harness models or new waiver policies
are extensions, not prerequisites for a standalone board workflow. Add them only with
a concrete need, a typed input boundary, a valid case and a deliberately failing case.
