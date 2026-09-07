# KiCad + Git team-template candidate

**NOT FOR MANUFACTURE. Public synthetic training repository.**

This repository is a reusable starting point for a KiCad/Git workflow. Its `controller` project is a deliberately small golden fixture: two resistors, two local footprints, two nets and two routed tracks. It proves workflow mechanics only; it is not an electrical design, a mechanical interface definition, or an approved product.

## Use this template deliberately

1. Read [Start here](docs/START_HERE.md), then set the adoption fields before editing a real board.
2. Use the golden fixture to rehearse the workflow. For a real project, create `boards/<project-id>/` with its complete schematic, PCB, project file, tables, and project-local dependencies.
3. Put reusable assets under `libraries/` only after declaring them in the source scope and release metadata. See [Library policy](docs/LIBRARIES.md).
4. Record the exact KiCad version, project/library revisions, and evidence before tagging a release. See [Versioning and releases](docs/VERSIONING.md).

The native desktop rehearsal found that KiCad 10.0.6 expanded this fixture's minimal `controller.kicad_pro` immediately on open and created a local `.kicad_prl`. The checked fixture and CI remain pinned to **KiCad 10.0.5** until a dedicated, reviewed migration changes that baseline. Opening a project with a different build is therefore not a read-only action; follow [Project workflow](docs/PROJECT_WORKFLOW.md).

## Included guidance

- [Project workflow](docs/PROJECT_WORKFLOW.md): branches, edits, review, and safe recovery.
- [Libraries](docs/LIBRARIES.md): project-local versus shared assets and path rules.
- [Mechanical handoff](docs/MECHANICAL_HANDOFF.md): interface details a board project must publish for mechanical work.
- [Versioning and releases](docs/VERSIONING.md): toolchain pins, tags, release records, and migrations.
- [Release-manifest example](docs/release-manifest.example.yaml): fields required before a release can be considered.

The earlier [employee guide](docs/EMPLOYEE_GUIDE_v0.2_candidate.md) and [desk card](docs/QUICK_REFERENCE_v0.2_candidate.md) remain historical public-pilot candidates. They are not approval records.

## Checks

On each pull request, Actions runs checker unit tests, real KiCad ERC/DRC with parity and zone refill, a netlist contract, SVG review exports, source-integrity checks, and deliberate defect probes. The final job rejects unsuccessful prerequisite jobs. See `pilot.json` for the exact pinned image/version and download the `kicad-review-*` artifact for review evidence.

From the repository root, with Python 3.12+ and KiCad 10.0.5 on PATH:

```sh
python -m unittest discover -s tests -v
python tools/validate.py --output build/review-001
python tools/fault_probe.py --output build/faults-001
```

Close KiCad before checking. Use a new output directory per attempt; retained evidence is never overwritten. No proprietary designs, private handoffs, credentials, customer data, or hardware orders belong here.
