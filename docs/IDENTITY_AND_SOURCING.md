# Identity, pinouts, BOMs, and sourcing

KiCad holds electrical design facts; controlled catalogs hold business and supply-chain facts. Link them with stable identifiers rather than copying volatile information into drawing text.

## Stable identities

Every production-bound component needs an internal part ID, manufacturer, MPN, datasheet URL, lifecycle state, approved status, and linked library asset. Store it in `catalog/parts.json`; put the internal ID and MPN in KiCad fields. A changed MPN, footprint, lifecycle state, or approved alternate is an engineering-review change.

Every external connector needs an interface ID and revision in `catalog/interfaces.json`. Its pin list records pin number, signal, direction, voltage/domain, mating connector, orientation, and mechanical clearance. A future netlist-to-interface check can fail a PR when a connector pinout drifts from that contract.

Every reusable library needs an ID, version, owner, status, and repository path in `catalog/libraries.json`. A board lists the library IDs it consumes; its release manifest records the exact revision. Project-local assets remain with their board and are protected by that board's source inventory.

## BOM and price policy

Generate a BOM from the tagged KiCad source and enrich it from the approved part catalog. Store a sourcing snapshot beside the release—not as a permanent `Price` field in a schematic. Each snapshot must state supplier, supplier SKU, quantity break, currency, region, lead time/stock observation, timestamp, and source link or export reference.

Price and availability are observations, not immutable design facts. The release identity is the Git tag plus the manifest, BOM, toolchain version, library revisions, and evidence hashes.

## Fixture boundary

The controller project is a synthetic fixture, so its catalog entries are intentionally empty and its registry marks component identity as not required. A real engineering project must set `component_identity.required` to `true`, declare approved part IDs, and link each shared library/interface before it can pass governance lint.
