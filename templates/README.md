# Instantiating the team template

Use this repository as a GitHub template only after the adoption record in `docs/START_HERE.md` is complete. The included `boards/controller` files are a synthetic golden fixture, not a production starting design.

Choose the deliverable kind before creating source: PCB projects live in `boards/`,
schematic-only projects in `schematics/`, system-wiring views in `systems/`, and
harness-interface views in `harnesses/`. Every kind commits `.kicad_pro` and
`.kicad_sch`; only PCB projects commit `.kicad_pcb`. Use the matching configuration
template, source-root inventory, and typed validation contract before relying on CI.

Copy the release-manifest example and [mechanical-handoff template](mechanical-handoff.production.md); replace every placeholder with reviewed project facts. Do not carry the `NOT FOR MANUFACTURE` fixture label into a release record without an explicit disposition.

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
