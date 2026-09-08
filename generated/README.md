# Generated review views

Run `python -B tools/hardware.py generate` at the repository root, then review the
diff and run `python -B tools/ci.py`. Do not hand-edit these BOM/connection files.
These small deterministic review views are intentionally tracked and drift-checked.
Large native exports and per-run logs belong in ignored `build/` evidence folders.
Generated schemas live under `schemas/`; their authoritative definitions are in
`tools/hwrepo/contracts.py`.

Every BOM here is NOT FOR MANUFACTURE. Electrical connection JSON is a projection
for adapter/review testing, not a wire harness drawing or KiCad source file.
