# Template acceptance and remaining work

## Reference and implementation decision

The user-supplied generic planning packet v0.1 (2026-09-07) informed this extension.
Its ZIP SHA-256 is
`d6868017ee21dab8f067841ab25eae63adfe4db690467fae189cea34c0bd307f`.
It was reference material, not executable policy or an imported agent instruction.
No employer branding or proprietary design was incorporated.

Keep `boards/`, `catalog/`, `libraries/` and the existing real KiCad lane. Add a
small Python product layer under `tools/hwrepo/`, not a replacement CAD tool. See
the [plan completion matrix](PLAN_COMPLETION_MATRIX.md) for each packet requirement,
the implemented evidence and the human/hosted boundaries that remain external.

## What is exercised automatically

| Concern | Enforcement / negative test |
| --- | --- |
| Typed serialization boundary | Pydantic 2.13.4 strict/frozen/closed models; duplicate JSON keys, non-finite values, unknown fields and scalar coercion fail before policy code |
| Python implementation quality | Ruff 0.16.1 checks formatting/import hygiene; strict Pyright 1.1.411 verifies `tools/`; architecture tests reject `Any`, opaque core maps and raw JSON parsing outside declared adapters |
| Markdown documentation | A typed offline policy checks 32 repository documents for tabs/trailing whitespace, H1/heading/fence structure, local links/anchors, exact portable paths, reachability and expiring exceptions |
| Strict record shape, schema version, IDs | Unknown fields/types, duplicate keys/IDs/case collisions fail |
| Parts, assemblies, instances | Unknown references, duplicate refs, cycles including unreachable definitions, invalid purchased expansion fail |
| Terminal identity and allocation | Missing instance/pin, duplicated terminal, exclusive allocation conflict fail |
| Typed relations | Incompatible endpoint types and non-electrical harness use fail; functional rows excluded from continuity export |
| Evidence | Wrong type/scope, missing evidence and changed file hashes fail |
| Variants | Unknown exclusions/variants and active excluded endpoints/harnesses fail |
| Mechanical/harness records | Units, positive dimensions, existence of instances and drawing references checked; physical correctness NOT checked |
| BOM | Built/purchased/phantom expansion, quantity multiplication, exclusions, CSV formula escaping and deterministic order tested |
| Generated views/schema | Missing, stale, extra product outputs or schema drift fail |
| CAD/identity | Native netlist adapter checks all mapped symbol PART_ID fields; existing native lane checks ERC/DRC/parity/netlist/exports |
| Repository portability | Cross-OS path/traversal/case checks, versioned library variables, undeclared projects/designs, tracked local state, and force-added Office/media/archive/installer artifacts |
| Entry-point parity | Direct KiCad validation cannot bypass product policy; defect probes carry their dependency catalogs |
| Review evidence | Write-once snapshots, truthful dirty state, tampered output detection; release authorization explicitly denied |
| Release readiness | Typed manifest checks bind source commit, clean tree, toolchain, selected product/variant, checks, artifact hashes, deviations, maturity, approval and annotated-tag prerequisites; it never tags, publishes or authorizes a release |
| System context | Renderer-neutral system projections retain electrical, functional and mechanical relation kinds without becoming an electrical authority |
| Template adoption | Typed preflight, clean-source atomic local bootstrap and forward-only migration planning; it cannot overwrite a target, mutate Git history or edit KiCad source |
| Sourcing observations | A typed, repository-bound supplier snapshot validates controlled part IDs and explicit price/availability observations without fetching, selecting, purchasing or authorizing parts |
| Current metrics | A typed read-only report counts current failed policy checks, stale evidence and release-deviation status/expiry without impersonating historical CI or as-built operations |
| CAD-library SBOM | A deterministic generated inventory retains each controlled shared-library version, path, owner/status and provenance/licensing hashes; drift is a shared CI failure |

The local/CI entry point is `python -B -m tools.ci`, which invokes Ruff, strict
Pyright and behavior tests before the policy gate. The hosted workflow adds a
Python 3.12 Windows/Linux/macOS matrix and retains digest-pinned KiCad container
jobs. Configuring these jobs is not evidence that they have run remotely. The
Python setup action is pinned to the verified v6.0.0 commit; its behavior is
documented in the [official action repository](https://github.com/actions/setup-python/tree/e797f83bcb11b83ae66e0230d6156d7c80228e7c).

## Open acceptance work — do not mark complete from a green unit suite

Local verification on 2026-09-07: the shared static gate passed on Windows with
Python 3.10.11. The suite ran 115 tests: 114 passed; one symlink-creation test was
skipped because this host session lacks that permission. Generated-view/schema
drift and the 32-document Markdown layout/link/anchor/reachability policy passed.
A write-once review snapshot's eight artifact hashes verified; the manifest correctly
recorded the dirty working tree.

Native KiCad 10.0.6 diagnostic exports from disposable copies passed both LED
boards' ERC/DRC/parity, golden netlist contracts and all three component PART_ID
mirrors per board. Repository CAD/library/firmware source hashes stayed unchanged.
The real pinned validator correctly rejected 10.0.6 because 10.0.5 is approved.
These diagnostic results are not a pinned 10.0.5 acceptance run or hosted CI run.

- Run the changed hosted workflow; exercise clean clones on supported workstations
  and the exact approved native KiCad version. A different desktop patch build is
  diagnostic evidence only until the toolchain baseline is deliberately migrated.
- Demonstrate three real actors, independent review, protected-branch enforcement,
  concurrent editing, stale-branch update, conflict resolution, handoff and access
  revocation. Local JSON strings cannot prove server-side permissions.
- Replace synthetic identities/pinouts with representative permitted engineering
  data, including source/licensing evidence. Obtain electrical and mechanical
  independent review. No public example is buildable by implication.
- Add a real enclosure/model/harness vertical proof, mating and fit tolerances,
  native geometric cross-checks, and a fresh-workstation library/3D-model rehearsal.
- Design scoped, expiring waiver/deviation records and maturity-specific evidence
  rules. Current KiCad disabled-check baselines are explicit training policy, not
  approved production waivers. Do not silently waive failing checks.
- Add source packaging, clean-tree/tag requirements, exact exporter provenance,
  immutable release artifacts, release authority and independent tag/restore tests.
  No release, tag or GitHub permission mutation is automated by this extension.
- Add fractional units, approved alternatives, richer DNP/variant selection,
  harness contacts/splices/shields and optional renderer/PLM/supplier adapters as
  separate versioned extensions with deliberate-defect fixtures.
- Extend Markdown parsing only when a concrete repository need exceeds the current
  deterministic local policy. It intentionally does not crawl external sources,
  validate remote pages, or make formatting edits automatically.

## Extension rule

For every new build-critical rule, add one valid fixture and one deliberately bad
fixture, specify its authority and diagnostics, add it to the shared entry point,
and update this coverage record. Do not substitute a checklist for an executable
gate, or an executable gate for a human engineering judgment it cannot make.
