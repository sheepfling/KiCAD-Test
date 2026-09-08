# Generic hardware-repository plan completion matrix

This matrix turns the generic planning packet v0.1 into repository evidence. It
does not relabel a green local suite as hosted permission, human-review, physical-fit
or manufacturing proof. The packet archive remains external reference material; its
recorded SHA-256 is in [template acceptance](TEMPLATE_ACCEPTANCE.md).

## Status vocabulary

- **Implemented and tested** — typed source, deterministic command and negative test exist.
- **Template control; external acceptance** — this repository supplies the control, but a
  real organization, GitHub configuration or independent engineer must exercise it.
- **Deliberately external** — a generic Git repository must not impersonate the named
  operational system or human authority.

## Master-plan maturity-stage reconciliation

| Packet stage / exit expectation | Status | Current evidence or boundary |
| --- | --- | --- |
| Stage A — skeleton, source classification, PR/CODEOWNERS starters and shared local/hosted checks | Implemented and tested | hygiene policy, `.gitattributes`, PR/issue templates, `CODEOWNERS.example`, contributor guidance and central CI driver |
| Stage A — protected branch, multi-clone collaboration, conflict, stale-main and closeout rehearsal | Template control; external acceptance | workflow/assignment/governance procedures are present; real roles, hosting rules and independent working copies must exercise them |
| Stage B — exact KiCad policy, controlled libraries, product records, ERC/DRC and broken fixtures | Implemented and tested | P0 controls below plus typed library provenance and interface-pin/harness binding checks |
| Stage B — fresh workstation reproduces every native check | Template control; external acceptance | portable-path policy and preflight exist; a clean supported workstation with the approved KiCad build must provide the proof |
| Stage C — revisions, variants, controlled BOM, release manifest/hashes, maturity/deviation rules | Implemented and tested | typed product/release policies, deterministic BOMs, assurance floors, artifact hashes and negative tests |
| Stage C — immutable tag/release package, physical outputs and a second engineer's purchase/build trace | Template control; external acceptance | gate requires records and tag prerequisites; authorized hosting, actual production data, physical artifacts and independent review cannot be fabricated by this template |
| Stage D — onboarding, bootstrap, deliberate upgrades, adapter seams and current metrics | Implemented and tested | onboarding/adoption documentation, typed atomic bootstrap, forward-only upgrade plan, provider-neutral sourcing snapshot and current-policy metrics |
| Stage D — external PLM/PDM, supplier, document and as-built operations | Deliberately external | the template exposes stable IDs and local contracts; system selection, credentials, retention, serial-unit handling and operational authority are organization-owned |

The packet's stated non-goals remain deliberate: this repository does not implement
semantic auto-merging of KiCad conflicts, a custom schematic editor, a custom PLM,
automatic pinout inference, or a mandatory cloud service.

## P0 — engineering-integrity baseline

| Packet requirement | Status | Evidence |
| --- | --- | --- |
| Exact supported KiCad policy and CI execution | Implemented and tested | `catalog/toolchains.json`, `python -m tools.check_toolchain`, digest-pinned KiCad lanes |
| Source/generated/local-state tree policy | Implemented and tested | `README.md`, repository policy, hygiene gate and generated-view drift |
| Portable attributes and ignored local state | Implemented and tested | `.gitattributes`, `.gitignore`, forced-artifact regression tests |
| Typed parts, assemblies, interfaces/terminals, connections, variants and evidence | Implemented and tested | strict Pydantic records and product schemas |
| Identity/reference/path checks | Implemented and tested | product/repository policy and deliberate-defect tests |
| KiCad project discovery, version, ERC and DRC | Implemented and tested | registry, native validator, fault probes and hosted workflow |
| Deterministic outputs and hashes | Implemented and tested | BOM/system/electrical projections, schema drift and review snapshot |
| One local entry point and matching hosted checks | Implemented and tested | `python -B -m tools.ci` and the thin workflow driver |

## P1 — release-candidate controls

| Packet requirement | Status | Evidence |
| --- | --- | --- |
| Assembly/variant BOM and KiCad field consistency | Implemented and tested | typed generator, native `PART_ID` mirror check and mutation tests |
| Harness validation seam | Implemented and tested | typed harness/terminal records bind to exact declared interface pins and relation-kind checks; WireViz remains optional |
| Semantic system view | Implemented and tested | generated `*.system.json` preserves electrical, functional and mechanical kinds |
| Maturity profiles, deviations and release readiness | Implemented and tested | [release-readiness gate](RELEASE_READINESS.md), typed assurance-floor catalog, manifest/deviation models and tests |
| Generated-output drift and documentation graph policy | Implemented and tested | static pipeline, Markdown policy and negative tests |
| CODEOWNERS/ruleset live pilot | Template control; external acceptance | `CODEOWNERS.example`, governance record and live-pilot instructions |
| Fresh-clone/fresh-workstation rehearsal | Template control; external acceptance | onboarding/preflight procedure; must run on permitted clean workstations |
| Immutable tag, hosted release and restore | Template control; external acceptance | release gate requires annotated tag; creating/publishing/restoring one needs release authority |

## P2 — scale and usability

| Packet requirement | Status | Boundary |
| --- | --- | --- |
| Template adoption and upgrade path | Implemented and tested | typed preflight, clean-source atomic bootstrap and forward-only migration planner; a real organization still owns the Git remote, users and adoption review |
| PLM/PDM, supplier and document-system adapters | Template control; external acceptance | stable IDs and a typed, provider-neutral supplier-offer snapshot contract exist; selecting, securing and operating any external connector remains organization-owned |
| Human-friendly editor/form workflow | Deliberately external | choose only after real users demonstrate that typed records are burdensome |
| As-built/deviation operational database | Deliberately external | Git defines design intent; serial-numbered units need an operational system |
| System-view projection | Implemented and tested | semantic JSON is renderer-neutral and never becomes an electrical authority |
| SBOM/license/provenance expansion | Implemented and tested | deterministic shared-CAD-library SBOM plus SHA-256-bound provenance/licensing records; organization-specific licensing review remains external |
| Current policy and release-exception metrics | Implemented and tested | typed read-only metrics report covers failed policy checks, stale evidence and optional release-deviation status/expiry; historical/operational aggregation stays external |

## Remaining acceptance before a real release

The next executable code work is complete only when the static and native CI lanes
pass. The following cannot be completed by editing this template: three distinct
people exercising GitHub rules, exact supported KiCad on a clean workstation,
independent electrical/mechanical review, physical fit, an approved component source,
or release authority creating and restoring an immutable tag. Record those results in
the adopting repository; do not copy a synthetic result forward as evidence.
