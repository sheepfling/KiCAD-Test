# KiCad + Git team-template candidate

**NOT FOR MANUFACTURE. Public synthetic training repository.**

The template is project-, vendor-, and employer-agnostic. Adopt it under your own
repository, maintainers, and component sourcing policy. Arduino and Raspberry Pi
appear only as concrete interface examples; the workflow and shared library do not
require either platform or a particular parts supplier.

This repository is a reusable starting point for a KiCad/Git workflow. Its `controller` project is a deliberately small golden fixture: two resistors, two local footprints, two nets and two routed tracks. It proves workflow mechanics only; it is not an electrical design, a mechanical interface definition, or an approved product.

Two additional, equally non-production training examples show the full project/catalog pattern:

- [Arduino Uno R3 D13 status LED](docs/examples/arduino-uno-status-led.md)
- [Raspberry Pi 40-pin GPIO17 status LED](docs/examples/raspberry-pi-status-led.md)

The [product workflow](docs/PRODUCT_WORKFLOW.md) combines these independent boards
into a synthetic assembly/variant/harness example with strict Python policy,
deterministic BOMs and scoped evidence checks. Start with the checks in the
[scripting standard](docs/SCRIPTING_STANDARD.md).

KiCad deliverables are explicitly classified as a PCB, schematic-only,
system-wiring, or harness-interface project. The last three are first-class source types with their own
native-check profiles and typed semantic boundaries; see [project kinds](docs/PROJECT_KINDS.md).
See [acceptance coverage](docs/TEMPLATE_ACCEPTANCE.md) for exactly what is enforced
and what still needs engineering or hosted acceptance. None of these checks
authorizes procurement, fabrication or release.

## Use this template deliberately

1. Read [Start here](docs/START_HERE.md), then set the adoption fields before editing a real board.
2. Use the golden fixture and the status-LED examples to rehearse the workflow. Choose the deliverable kind first: PCBs live under `boards/`, schematic-only work under `schematics/`, system-wiring views under `systems/`, and harness interfaces under `harnesses/`. Each has a different required source inventory and native-check profile.
3. Put reusable assets under `libraries/` only after declaring them in the source scope and release metadata. See [Library policy](docs/LIBRARIES.md).
4. Record the exact KiCad version, project/library revisions, and evidence before tagging a release. See [Versioning and releases](docs/VERSIONING.md).
5. Promote a real board only through the production assurance profile and complete [GitHub governance](docs/GITHUB_GOVERNANCE.md).
6. Bootstrap a clean template copy or plan a template update with the typed [template adoption guide](docs/TEMPLATE_ADOPTION.md).

The native desktop rehearsal found that KiCad 10.0.6 expanded this fixture's minimal `controller.kicad_pro` immediately on open and created a local `.kicad_prl`. The checked fixture and CI remain pinned to **KiCad 10.0.5** until a dedicated, reviewed migration changes that baseline. Opening a project with a different build is therefore not a read-only action; follow [Project workflow](docs/PROJECT_WORKFLOW.md).

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
- [Arduino Uno R3 example](docs/examples/arduino-uno-status-led.md): a D13/LED_BUILTIN interface contract, KiCad project, and sketch.
- [Raspberry Pi example](docs/examples/raspberry-pi-status-led.md): a GPIO17 interface contract, KiCad project, and GPIO Zero script.

The earlier [contributor guide](docs/CONTRIBUTOR_GUIDE_v0.2_candidate.md) and [desk card](docs/QUICK_REFERENCE_v0.2_candidate.md) remain historical public-pilot candidates. They are not approval records.

## Checks

On each pull request, Actions runs checker unit tests, real KiCad ERC/DRC with parity and zone refill, a netlist contract, SVG review exports, source-integrity checks, and deliberate defect probes. The final job rejects unsuccessful prerequisite jobs. See `pilot.json` for the exact pinned image/version and download the `kicad-review-*` artifact for review evidence.

From the repository root, with Python 3.12+ and KiCad 10.0.5 on PATH:

```sh
python -B -m tools.ci
# Fast local policy check for one board and the products that declare it
python -B -m tools.ci --project arduino-uno-status-led
# Select a group by metadata, or omit legacy fixtures
python -B -m tools.ci --tag status-led
python -B -m tools.ci --exclude-tag legacy
python -B -m tools.ci --kicad --output build/complete-review-001
python -m unittest discover -s tests -v
python -m tools.check_toolchain --toolchain kicad-10.0.5
python -m tools.lint_registry --all
python -m tools.lint_registry --project controller
python -m tools.lint_registry --project arduino-uno-status-led
python -m tools.validate --output build/review-001
python -m tools.check_all --all --output build/all-review-001
python -m tools.fault_probe --output build/faults-001
```

Close KiCad before checking. Use a new output directory per attempt; retained evidence is never overwritten. No proprietary designs, private handoffs, credentials, customer data, or hardware orders belong here.
