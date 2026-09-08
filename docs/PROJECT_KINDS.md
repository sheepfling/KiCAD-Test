# Project kinds

Every deliverable uses `projects/<id>/` with local docs/tests. The manifest's `kind`
selects the required native inventory and checks; kinds are not folder categories.

| Kind | Native source | Extra contract/check |
| --- | --- | --- |
| `pcb` | `.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | ERC, DRC/parity, independent expected nets/components, SVGs |
| `schematic` | `.kicad_pro`, `.kicad_sch` | ERC and schematic SVG |
| `system_wiring` | `.kicad_pro`, `.kicad_sch` | Whole-product relation/terminal/harness/mechanical traceability, ERC and SVG |
| `harness_interface` | `.kicad_pro`, `.kicad_sch` | Exact electrical conductor/endpoint/harness coverage, ERC and SVG |

PCB and schematic projects can stand alone. Wiring/harness views reference the
optional product whose relationships they describe. A schematic line by itself does
not establish cable construction, mechanical fit or an approved electrical interface.
Use [project-local test contracts](../tests/README.md) and the [product workflow](PRODUCT_WORKFLOW.md).
