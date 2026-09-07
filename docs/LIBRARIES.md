# Library policy

Use two kinds of libraries deliberately.

| Type | Location | Use when | Versioning rule |
| --- | --- | --- | --- |
| Project-local | `boards/<project-id>/` beside the `.kicad_pro` | The symbol, footprint, or model belongs only to one board | Commit it with the project change that depends on it. |
| Shared | `libraries/<library-id>/` | More than one project needs the same approved asset | Declare the library directory in `source_roots`, include it in `required_inputs`, and record its revision in the release manifest. |

`controller` demonstrates a project-local library: `Pilot.kicad_sym` and `Pilot.pretty` sit beside its project file, and its `sym-lib-table` / `fp-lib-table` use `${KIPRJMOD}`. Keep those paths relative. Do not rely on a user's global KiCad tables, Downloads folder, or an absolute home-directory path.

For shared assets, use one named library directory per approved library and keep its symbols, footprints, 3D models, licensing/provenance notes, and changelog together. A library revision that changes an existing footprint is an engineering change: it needs a PR, review of affected boards, and an explicit release-manifest entry.

The checker intentionally hashes only `boards/` for the synthetic fixture. Before introducing a shared library, update `pilot.json` so `source_roots` includes its path and `required_inputs` lists every tracked input. The checker will then fail closed if an unreviewed library file appears or disappears.
