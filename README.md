# KiCad + GitHub workflow pilot v0.3

**NOT FOR MANUFACTURE. Public synthetic training repository.**

Open `boards/controller/controller.kicad_pro` in KiCad **10.0.5**. The example contains two passive resistor symbols, two locally defined footprints, two nets and two routed tracks. It is a workflow fixture, not a functional product or approved electrical design. All symbol/footprint dependencies are committed beside the project.

## Start here

Read [the employee route](docs/EMPLOYEE_GUIDE_v0.2_candidate.md) and [the desk card](docs/QUICK_REFERENCE_v0.2_candidate.md). These are **unapproved candidates** adapted from the supplied handoff; desktop observations and independent human signoff remain outstanding.

On each pull request, Actions runs the checker unit tests, actual KiCad ERC, DRC with schematic parity and zone refill, an independent exported-netlist contract, SVG review exports, source-integrity checks, and deliberate defect probes. The final job rejects unsuccessful prerequisite jobs. See the exact image/version in `pilot.json` and download the run's `kicad-review-*` artifact for raw reports, command logs, hashes, BOM and drawings. Artifacts expire after 30 days; they are not immutable manufacturing releases.

## What this repository does NOT prove

There is no native exclusive checkout, no board-path publication restriction configured here, no independently approved merge, and no manufacturing release. A green Actions result does not itself protect `main`: a maintainer must separately configure required checks and independent review. The workflow and check definitions also need trusted ownership/protection.

The original v0.2 pilot requires a private organization repository, a representative approved board, three distinct authenticated participants and observed desktop use. This personally owned public repository is an explicitly narrower smoke pilot, not a replacement or an all-pass result for that matrix.

No MCP or local desktop connection is needed for this repository/CI route. Editing in a running local KiCad GUI remains a separate access and usability test.

## Local checks

From the repository root, with Python 3.12+ and KiCad 10.0.5 on PATH:

```sh
python -m unittest discover -s tests -v
python tools/validate.py --output build/review-001
python tools/fault_probe.py --output build/faults-001
```

Use a new output directory per attempt; retained evidence is never overwritten. The CI container is pinned by digest, not a floating `latest` tag. A changed fixture/netlist contract, new source scope or checker change needs explicit review.

No proprietary designs, customer information, private handoff documents, credentials or hardware orders belong here.
