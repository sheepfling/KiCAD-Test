# Adopted project configurations

This is the canonical root for typed check contracts belonging to adopted
projects. Create one configuration per entry in `catalog/projects.json`, using
the matching file in `templates/` as the starting point.

The complete worked reference system keeps its configurations under
`examples/configs/` so those fixtures remain visibly separate from active
project source. A configuration names the project kind, exact toolchain,
source roots, required inputs, and the kind-specific validation contract.
