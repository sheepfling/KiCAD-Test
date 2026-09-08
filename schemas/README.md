# Generated JSON Schemas

The authoritative contracts are Pydantic models in `tools/hwrepo/models.py`.
Run `python -B -m tools.hardware generate` to export the published input and release
schemas here for editors or non-Python consumers. These JSON files are ignored and
are also available as portable CI artifacts. Only this README is tracked.

Change the model and its [contract tests](../tests/README.md), not an exported schema.
The portable gate regenerates independently in a temporary directory, so a fresh
clone does not need these files. Internal reports remain typed Python models without
separate published schema artifacts.
