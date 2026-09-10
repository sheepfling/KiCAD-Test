# Copyable project and workflow records

The easiest start is `python -B -m tools.template new-project --project-id battery-board --kind pcb --toolchain kicad-10.0.5`.
The scaffold contains no circuit. Create the real KiCad design and complete its contract.

For manual creation, copy the appropriate `*-project-config.example.json` to
`projects/<id>/project.json` and the matching `project-tests/<kind>.json` to
`projects/<id>/tests/contract.json`. Replace placeholders, set local native paths,
and declare actual required inputs. The PCB/schematic/wiring/harness templates all
use the same island layout. The production template adds explicit release controls.

Manifest source paths are project-relative. Only `shared_source_roots` and
`shared_inputs` are repository-relative. Toolchain version and image are resolved
from `toolchain_id`, so they are not duplicated in project files.

Catalog examples describe shared identities. [Mechanical handoff](mechanical-handoff.production.md)
and governance examples become board-local reviewed records. The typed release-manifest
example illustrates the checker schema. Use `tools.release prepare` to populate
real source, dependency and evidence hashes automatically; placeholders cannot pass.
`OPTIONAL_NO_AUTO_MERGE.gitattributes` is an opt-in policy fragment for teams that
want every KiCad file conflict to require deliberate file-level resolution. Review
and append it to the root `.gitattributes` only when that matches the team's process.

The template contract and upgrade catalog describe supported adoption steps. See
[template adoption](../docs/workflow/TEMPLATE_ADOPTION.md), [BOM policy](../docs/workflow/BOM_POLICY.md),
[sourcing](../docs/workflow/IDENTITY_AND_SOURCING.md) and [library policy](../docs/workflow/LIBRARIES.md).
