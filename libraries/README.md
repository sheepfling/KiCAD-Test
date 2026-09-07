# Shared KiCad libraries

This directory is intentionally empty in the synthetic pilot. It exists to make the project/library boundary explicit.

Create one named directory for each approved reusable library, such as `libraries/power-connectors/`. Keep symbols, footprints, models, provenance, and a changelog together. Before any library becomes a dependency, add its directory to `source_roots` and its files to `required_inputs` in the project configuration so CI hashes and reviews it.

Do not move a project-local asset here merely because it looks reusable. First establish ownership, compatibility, versioning, and the impact on each consuming board.
