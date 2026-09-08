# Project kinds: PCB, schematic, system wiring, and harness interface

Every native KiCad project in this template has one explicit `kind`. Select it
before creating source files; a project does not become a PCB merely because it
uses KiCad.

| Kind | Controlled source root | Primary authority | Native KiCad gate | Explicitly not implied |
| --- | --- | --- | --- | --- |
| `pcb` | `projects/pcb/<id>/` | Schematic, board geometry, and typed board netlist contract | ERC, DRC with schematic parity, netlist identity, schematic/PCB SVG exports | Procurement, fabrication, fit, or release approval |
| `schematic` | `projects/schematic/<id>/` | Electrical intent and interface-review sheet | ERC and schematic SVG export | PCB layout, DRC, fabrication outputs, or a board BOM |
| `system_wiring` | `projects/system-wiring/<id>/` | Typed product terminals, connection kinds, harnesses, and mechanical handoffs; the KiCad sheet is the review view | Complete typed traceability, ERC, and schematic SVG export | That a drawn line is copper/net continuity, a cable construction, or a fit analysis |
| `harness_interface` | `projects/harness-interface/<id>/` | Typed electrical conductors, endpoint terminals, and harness attributes; the KiCad sheet is the interface-review view | Exact harness/conductor/endpoint coverage, ERC, and schematic SVG export | Cable construction instructions, a procurement approval, or system-level functional/mechanical claims |

The source folder policy is enforced. A `pcb` project must contain and inventory
both `.kicad_sch` and `.kicad_pcb`; `schematic`, `system_wiring`, and
`harness_interface` projects must
contain and inventory a `.kicad_sch` but must not carry an accidental `.kicad_pcb`.
Every project still has a `.kicad_pro` and is run in a digest-pinned KiCad lane.

## Semantic authority for wiring and harness projects

System wiring needs more than a picture. Its configuration names one typed product
and must cover exactly every connection, endpoint terminal, harness, and mechanical
handoff in that product. The check rejects omissions, extra IDs, duplicate IDs, an
unknown product, or a product-index mismatch. Connection types remain distinct:
electrical, functional, protocol, and mechanical relationships are never silently
recast as one electrical wire.

Use `examples/projects/system-wiring/status-indicator-wiring/` as the reference example. It is deliberately
non-production. The relationship identifiers in the sheet map to
`examples/products/status-indicator-system.json`; that record, not a line on the sheet, owns
the connection semantics.

A harness-interface view is deliberately narrower. It names one or more harnesses
and must cover exactly the electrical connections that use them, plus each conductor
endpoint. It cannot claim a functional status relationship or mechanical fit merely
because those items appear in the broader product. The generated harness schedule
is a typed planning/review artifact: it records revision, instance, length, conductor
area, endpoints, assurance, and evidence. Use
`examples/projects/harness-interface/status-indicator-harness-interface/` as the synthetic example.

## Adding a deliverable

1. Start from the matching project-config template and create the KiCad project
   under its kind's canonical `projects/<domain>/` source root.
2. Inventory every source input. Shared libraries, firmware, drawings, or models
   belong in `source_roots` only when the deliverable actually depends on them.
3. Add a registry entry with the same `kind`, toolchain, tags, interfaces, and
   assurance profile. A system-wiring or harness-interface project also belongs in
   the associated product's index entry.
4. For system wiring or harness interfaces, add/validate typed product IDs first;
   then draw the readable KiCad review view. For schematic-only work, do not invent
   footprints or PCB constraints just to satisfy a board-specific check.
5. Run the focused lane, then the full lane:

```sh
python -B -m tools.ci --project <project-id>
python -B -m tools.ci
```

The system-wiring and schematic-only examples prove static policy, typed contract,
and source-layout behavior. Run the pinned KiCad lane in CI or on a matching local
installation before relying on native ERC/SVG evidence.
