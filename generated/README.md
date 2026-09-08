# Generated review views

Run `python -B -m tools.hardware generate` at the repository root, then review the
diff and run `python -B -m tools.ci`. Do not hand-edit these BOM/connection files.
These small deterministic review views are intentionally tracked and drift-checked.
Large native exports and per-run logs belong in ignored `build/` evidence folders.
Published input and release schemas live under `schemas/`; their authoritative
definitions are the Pydantic models in `tools/hwrepo/models.py`. Internal report
models are validated by Python and are not duplicated as committed schemas.

Every BOM here is NOT FOR MANUFACTURE. Electrical connection JSON is a projection
for adapter/review testing, not a wire harness drawing or KiCad source file.
