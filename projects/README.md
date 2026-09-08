# Adopted project sources

This is the canonical source root for a repository created from the template.
Create each real KiCad deliverable under the domain that describes its primary
engineering role:

- `projects/pcb/<project-id>/`
- `projects/schematic/<project-id>/`
- `projects/system-wiring/<project-id>/`
- `projects/harness-interface/<project-id>/`

The matching configuration belongs in `configs/`, and the project must be added
to `catalog/projects.json`. The complete worked reference system is separate,
under `examples/projects/`, so example files are not mistaken for active product
source.

Every project directory contains its `.kicad_pro` and `.kicad_sch`; only a PCB
project also contains a `.kicad_pcb`. Keep project-local libraries beside that
project. Put reusable shared libraries in `libraries/<library-id>/` and declare
their provenance and exact inputs in the project configuration.
