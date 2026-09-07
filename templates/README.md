# Instantiating the team template

Use this repository as a GitHub template only after the adoption record in `docs/START_HERE.md` is complete. The included `boards/controller` files are a synthetic golden fixture, not a production starting design.

For a new board, create `boards/<project-id>/` in KiCad using the approved build. Commit the `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, library tables, and project-local assets together. Update the checker configuration with the new project path, source roots, required inputs, netlist expectations, and approved toolchain identity before relying on CI.

Copy the release-manifest example and mechanical-handoff checklist; replace every placeholder with reviewed project facts. Do not carry the `NOT FOR MANUFACTURE` fixture label into a release record without an explicit disposition.

The adjacent JSON examples show the machine-readable shapes used by the repository-wide lint. Copy them into `catalog/` only after replacing every `EXAMPLE` value with a reviewed identity, source, owner, and revision.
