# Library policy

Use two kinds of libraries deliberately.

| Type | Location | Use when | Versioning rule |
| --- | --- | --- | --- |
| Project-local | `boards/<project-id>/` beside the `.kicad_pro` | The symbol, footprint, or model belongs only to one board | Commit it with the project change that depends on it. |
| Shared | `libraries/<library-id>/` | More than one project needs the same approved asset | Declare the library directory in `source_roots`, include it in `required_inputs`, and record its revision in the release manifest. |

`controller` demonstrates a project-local library: `Pilot.kicad_sym` and `Pilot.pretty` sit beside its project file, and its `sym-lib-table` / `fp-lib-table` use `${KIPRJMOD}`. Keep those paths relative. Do not rely on a user's global KiCad tables, Downloads folder, or an absolute home-directory path.

For shared assets, use one named library directory per approved library and keep its symbols, footprints, 3D models, licensing/provenance notes, and changelog together. The library catalog must name repository-relative provenance and licensing records and pin the SHA-256 of each. The static gate fails if either record is missing or changes without its catalog hash changing. A library revision that changes an existing footprint is an engineering change: it needs a PR, review of affected boards, and an explicit release-manifest entry.

`PROVENANCE.md` records whether the asset was authored here, generated, copied from a
vendor source, or derived from a third party; it names the source, revision/date,
scope and review limits. `LICENSE.md` (or an equivalently named licensing record)
states the applicable distribution/use terms and any notice obligations. A hash only
binds the reviewed record bytes. It does not establish that a source is truthful,
complete or legally sufficient; obtain the relevant engineering and licensing review
before marking a shared library approved.

The controller configuration intentionally hashes only `boards/controller` because it is
a project-local synthetic fixture. The Arduino and Raspberry Pi examples demonstrate the
shared-library rule: each project configuration includes `libraries/status-led` in
its `source_roots` and `required_inputs`. The checker fails closed if any declared
library input appears, disappears, or changes outside review.

`generated/library-sbom-v1.json` is the deterministic inventory of controlled shared
CAD libraries, including each ID, version, path, owner/status and provenance/licensing
record hashes. It is regenerated with `python -B -m tools.hardware generate` and
drift-checked by the shared CI gate. It does not assert that a library's legal review
or physical footprint qualification is complete.
