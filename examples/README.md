# Reference examples

**Discardable reference material:** this entire directory may be removed or
replaced after the workflow has been understood. It is not active product source.

This directory is the worked example system that ships with the template. It is
here to make the process concrete: every example is registered, typed, checked,
and connected to the same product and library records used by the tests.

The reusable process does not live here. Use `docs/` for guidance, `templates/`
for starting records, `tools/` for checks, and `tests/` for executable examples
of the policy. During adoption, review these examples, replace or remove the
ones that do not fit, and create real deliverables under `projects/<domain>/`.

## Example project map

| Domain | Reference project | What it demonstrates |
| --- | --- | --- |
| PCB | `examples/projects/pcb/arduino-uno-status-led/` | Schematic, board layout, local project tables, shared library use, and BOM identity |
| PCB | `examples/projects/pcb/raspberry-pi-status-led/` | A second host interface using the same reusable library pattern |
| PCB | `examples/projects/pcb/controller/` | The smallest native KiCad checker fixture |
| Schematic | `examples/projects/schematic/passive-signal-reference/` | Schematic-only deliverable without a PCB claim |
| System wiring | `examples/projects/system-wiring/status-indicator-wiring/` | Product-level blockout and typed relationship traceability |
| Harness interface | `examples/projects/harness-interface/status-indicator-harness-interface/` | Conductor, endpoint, and harness-interface coverage |

Supporting example records live beside this map:

- `examples/configs/` contains the per-project typed check contracts.
- `examples/products/` contains the cross-project product record used by the system and harness views.
- `examples/libraries/` contains the small shared training library.
- `examples/firmware/` contains the companion Arduino and Raspberry Pi examples.

These are reference inputs, not a product specification. Their organization,
traceability, and checks are authoritative examples of the workflow; their
component choices and electrical/mechanical claims are not requirements for an
adopted project.
