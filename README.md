# KiCad + Git team repository template

This repository is the reference implementation of a reusable, platform-agnostic
KiCad/Git workflow. It is organized so a new team can understand the process,
copy the templates, and run the same checks on PCB, schematic, system-wiring, and
harness-interface work.

Read the [authority model](docs/AUTHORITY_MODEL.md) before copying anything. It
labels what is normative process, what becomes adopted project source, what is a
copyable template, and what is safe to delete after rehearsal.

The authoritative process is deliberately separate from the worked examples:

| Area | Purpose |
| --- | --- |
| `docs/` | Authoritative workflow, review, sourcing, release, and collaboration guidance |
| `templates/` | Copyable project, catalog, handoff, and governance records |
| `tools/` | The executable policy, generation, and validation services |
| `tests/` | Unit and policy tests that define expected behavior |
| `catalog/`, [`configs/`](configs/README.md), [`products/`](products/README.md), `schemas/` | Controlled registries, adopted-project check contracts, cross-project product records, and published input/release contracts |
| `generated/` | Deterministic review views produced by the tooling |
| [`projects/`](projects/README.md) | Canonical source root for projects created from this template |
| [`examples/`](examples/README.md) | A complete reference system showing how the process fits together |

Start with [Start here](docs/START_HERE.md). The examples are intentionally
small so the workflow is easy to inspect; their organization and checks are the
lesson, not their component choices or product claims.

## Use this template deliberately

1. Read [Start here](docs/START_HERE.md), then set the adoption fields before editing a real board.
2. Use the [reference examples](examples/README.md) to rehearse the workflow. For adopted work, choose the deliverable kind first: projects live under `projects/pcb/`, `projects/schematic/`, `projects/system-wiring/`, or `projects/harness-interface/`. Each has a different required source inventory and native-check profile.
3. Put reusable assets under `libraries/` only after declaring them in the source scope and release metadata. See [Library policy](docs/LIBRARIES.md).
4. Record the exact KiCad version, project/library revisions, and evidence before tagging a release. See [Versioning and releases](docs/VERSIONING.md).
5. Promote a real board only through the production assurance profile and complete [GitHub governance](docs/GITHUB_GOVERNANCE.md).
6. Bootstrap a clean template copy or plan a template update with the typed [template adoption guide](docs/TEMPLATE_ADOPTION.md).

The approved KiCad build is recorded in `catalog/toolchains.json`; check the exact
project-selected pin before opening a project. The template currently supports
catalogued KiCad 10.0.0 and 10.0.5 pins. Toolchain migration is a deliberate
workflow change documented in [Project workflow](docs/PROJECT_WORKFLOW.md).

## Included guidance

- [Project workflow](docs/PROJECT_WORKFLOW.md): branches, edits, review, and safe recovery.
- [Libraries](docs/LIBRARIES.md): project-local versus shared assets and path rules.
- [Mechanical handoff](docs/MECHANICAL_HANDOFF.md): interface details a board project must publish for mechanical work.
- [Versioning and releases](docs/VERSIONING.md): toolchain pins, tags, release records, and migrations.
- [Release readiness](docs/RELEASE_READINESS.md): typed candidate, deviation, artifact, toolchain and tag checks without auto-release authority.
- [Checks and CI](docs/CHECKS_AND_CI.md): individual-project and repository-wide gates.
- [Assurance profiles](docs/ASSURANCE_PROFILES.md): the enforced boundary between training and production projects.
- [GitHub governance](docs/GITHUB_GOVERNANCE.md): required branch protection, roles, and evidence for a production project.
- [Identity and sourcing](docs/IDENTITY_AND_SOURCING.md): controlled part, pinout, supplier, and price records.
- [Product workflow](docs/PRODUCT_WORKFLOW.md): authority boundaries, assembly/variant BOMs, harness semantics, evidence and mechanical collaboration.
- [Project kinds](docs/PROJECT_KINDS.md): when a deliverable is a PCB, schematic-only sheet, or system-wiring review view—and the checks each type receives.
- [Acceptance coverage](docs/TEMPLATE_ACCEPTANCE.md): executable checks, limits and remaining adoption work.
- [Plan completion matrix](docs/PLAN_COMPLETION_MATRIX.md): requirement-by-requirement implementation and external-acceptance boundary for the generic packet.
- [Scripting standard](docs/SCRIPTING_STANDARD.md): typed Pydantic contracts, adapter boundaries and test rules for Python tooling.
- [Template adoption](docs/TEMPLATE_ADOPTION.md): safe local bootstrap and review-only migration planning.
- [Template metrics](docs/METRICS.md): read-only current-policy, stale-evidence and deviation counts.
- [Markdown documentation policy](docs/MARKDOWN_POLICY.md): deterministic layout, local-link, anchor, portability and documentation-graph rules.
- [Repository hygiene](docs/REPOSITORY_HYGIENE.md): two-layer protection against temporary, Office, media and downloaded files.
- [Contributor guide](docs/CONTRIBUTOR_GUIDE.md): the normal assignment, edit, review, and handoff workflow.
- [Quick reference](docs/QUICK_REFERENCE.md): the short version for day-to-day work.
- [Arduino Uno R3 example](docs/examples/arduino-uno-status-led.md): a D13/LED_BUILTIN interface contract, KiCad project, and sketch.
- [Raspberry Pi example](docs/examples/raspberry-pi-status-led.md): a GPIO17 interface contract, KiCad project, and GPIO Zero script.

The contributor guide and quick reference are workflow guidance, not approval records.

## Checks

On each pull request, Actions runs checker unit tests, real KiCad ERC/DRC with parity and zone refill, a netlist contract, SVG review exports, source-integrity checks, and deliberate defect probes. The final job rejects unsuccessful prerequisite jobs. The selected reference configuration is under `examples/configs/`; download the `kicad-review-*` artifact for review evidence.

From the repository root, with Python 3.12+ and the exact KiCad version selected by
the project on PATH:

```sh
python -B -m tools.ci
# Fast local policy check for one project and the products that declare it
python -B -m tools.ci --project arduino-uno-status-led
# Select a group by metadata, or omit legacy fixtures
python -B -m tools.ci --tag status-led
python -B -m tools.ci --exclude-tag legacy
python -B -m tools.ci --kicad --output build/complete-review-001
python -m unittest discover -s tests -v
python -m tools.check_toolchain --toolchain kicad-10.0.0  # controller baseline
python -m tools.check_toolchain --toolchain kicad-10.0.5  # LED/reference fixtures
python -m tools.lint_registry --all
python -m tools.lint_registry --project controller
python -m tools.lint_registry --project arduino-uno-status-led
python -m tools.validate --output build/review-001
python -m tools.check_all --all --output build/all-review-001
python -m tools.fault_probe --output build/faults-001
```

Close KiCad before checking. Use a new output directory per attempt; retained evidence is never overwritten. No proprietary designs, private handoffs, credentials, customer data, or hardware orders belong here.
