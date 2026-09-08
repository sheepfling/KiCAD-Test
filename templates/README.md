# Instantiating the team template

Use this repository as a GitHub template after the adoption record in
`docs/START_HERE.md` is complete. The reusable process is in `docs/`,
`templates/`, `tools/`, and `tests/`; the complete worked system is grouped in
`examples/` so it is easy to review, replace, or remove.

Choose the deliverable kind before creating source in an adopted repository: PCB
projects live in `projects/pcb/`, schematic-only projects in
`projects/schematic/`, system-wiring views in `projects/system-wiring/`, and
harness-interface views in `projects/harness-interface/`. Every kind commits
`.kicad_pro` and `.kicad_sch`; only PCB projects commit `.kicad_pcb`. Use the
matching configuration template, source-root inventory, and typed validation
contract before relying on CI.

Copy the release-manifest example and [mechanical-handoff template](mechanical-handoff.production.md); replace every placeholder with reviewed project facts. Example labels describe the bundled reference data; record the actual assurance and release disposition for an adopted project.

The typed [release-manifest template](release-manifest.example.json) is the candidate
record validated by `python -m tools.ci --release`; the YAML example in `docs/` remains a
human-readable field guide, not the executable contract.

The adjacent JSON examples show the machine-readable shapes used by the repository-wide lint. Copy them into `catalog/` only after replacing every `EXAMPLE` value with a reviewed identity, source, owner, and revision.

`interfaces-catalog.example.json` records connector side/view, voltage or electrical
domain, mating-part source and mechanical-clearance authority per pin. It is the
controlled endpoint contract that harness terminals bind to; it is not a visual
diagram or an inferred pinout.

`sourcing-snapshot.example.json` is not a part catalog and does not approve an
alternate. It is a timestamped, typed observation of a supplier offer, intended to
be retained with a review or release record after the real source data is captured.

For a real PCB, begin with `production-project-config.example.json`; for a
schematic, system-wiring, or harness-interface deliverable, start with the matching
adjacent configuration example. Pair it with
`production-project-registry.example.json`, then add a reviewed mechanical handoff
and GitHub governance record from the adjacent templates. Production lint rejects
generic parts, unapproved libraries, disabled applicable checks, absent mechanical
records, and incomplete role separation.
