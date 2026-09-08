# Authority model: keep, copy, replace, regenerate

This document is the repository map for adoption. It answers the question:
which files define the workflow, and which files are only there to demonstrate
it?

## The short rule

`docs/`, `templates/`, `tools/`, `tests/`, the repository controls, and the
published contracts define the reusable process. The contents of `examples/`
are a complete, discardable reference system. Read them, rehearse with them,
then remove or replace them in a reviewed adoption change. Do not copy an
example project into an active product by changing only its name.

## Repository areas

| Area | Classification | Adoption rule |
| --- | --- | --- |
| `README.md` and this document | Normative navigation | Keep; customize only the repository identity and links that genuinely change. |
| `docs/` | Authoritative guidance | Keep and follow. `docs/examples/` is reference-only explanatory material and may be removed with the worked examples. |
| `templates/` | Copyable record shapes | Keep the templates; copy a matching one into the adopted record root, replace every placeholder, and review it. Templates are not active project records. |
| `tools/` | Executable policy | Keep. A behavior change is a process change and requires an intentional code review plus tests. |
| `tests/` | Executable expectations | Keep. Update tests only when the intended policy or contract changes. |
| `.github/` and `pyproject.toml` | Process infrastructure | Keep and configure for the adopted repository; the workflow delegates to the Python policy driver. |
| `catalog/` and `schemas/` | Controlled registries and contracts | Keep the structure and version rules. Replace reference entries with reviewed adopted data; do not silently fork a contract. |
| `projects/`, `configs/`, `products/`, `libraries/`, `governance/` | Adopted source and review records | These are the real repository homes after adoption. Add project-specific content here; the template's worked records are elsewhere. |
| `examples/` | Disposable reference system | Rehearse here, then delete or replace the directory in a reviewed adoption change. Nothing here is active product source. |
| `generated/` | Derived review views | Regenerate with the tooling; never hand-edit. It is not design authority, although small deterministic views may be tracked. |
| `build/` and `.evidence/` | Run output | Disposable and ignored. Retain evidence externally or in the approved release/evidence system. |

## What is authoritative for a real design

For an adopted project, authority flows through these layers:

1. `projects/<domain>/<project-id>/` owns the native KiCad source.
2. `configs/<project-id>.json` owns the typed project scope, exact toolchain,
   source inventory, and kind-specific validation contract.
3. `products/<product-id>.json` owns cross-project assemblies, interfaces,
   harnesses, relationships, and mechanical claims.
4. `catalog/` owns controlled identities and registry membership.
5. `tools/` validates those records; `generated/` only projects them for review.

A line in a schematic, a generated BOM, or an example record cannot override a
typed adopted record. Human review and hosted repository controls remain required
for approval and release.

## Safe adoption sequence

1. Read [Start here](START_HERE.md) and this authority model.
2. Choose the project kind and copy the matching record templates.
3. Create the real project under `projects/`, its configuration under `configs/`,
   and any cross-project record under `products/`.
4. Register the adopted records in `catalog/` and declare libraries and evidence.
5. Rehearse against `examples/`, then remove or replace those fixtures.
6. Run the focused project gate and the full repository gate before review.
