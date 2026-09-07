# Mechanical handoff checklist

Every real board project needs a reviewed mechanical-interface record. Keep it with the repository's documentation and link it from the PR or release manifest.

| Item | Record |
| --- | --- |
| Coordinate system | PCB origin, units, drawing datum, and orientation |
| Envelope | Board outline, thickness, stackup assumption, maximum component heights, and restricted volumes |
| Mounting | Hole locations, hardware, tolerances, keepouts, and chassis contact rules |
| Connectors | Manufacturer part, mating part, location, orientation, insertion envelope, and service clearance |
| Interfaces | Edge clearances, heat paths, shielding/grounding features, and cable routing constraints |
| Model package | STEP/DXF/PDF source, revision, units, and SHA-256 where applicable |
| Ownership | Mechanical reviewer, electrical reviewer, approval status, and exact commit |

The PCB's `Edge.Cuts`, mechanical layers, footprints, and 3D models must agree with this record. Do not create a separate “mechanical copy” of a board as a handoff; publish the reviewed source revision and derived artifacts together.

The synthetic controller fixture has no approved dimensions, stackup, or enclosure interface. It is for training only.
