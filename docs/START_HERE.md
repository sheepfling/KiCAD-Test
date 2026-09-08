# Start here — adopting the KiCad/Git template

This repository is the reference implementation of the team template. Read the
[authority model](AUTHORITY_MODEL.md) first: the reusable process is in `docs/`,
`templates/`, `tools/`, `tests/`, and the repository controls, while the complete
sample system under `examples/` is discardable reference material.

Complete this record before copying the structure to a real repository. A blank
field is a decision to make with the designated maintainer, not a value to guess.

Run `python -B -m tools.template preflight` before bootstrap or adoption; see
[template bootstrap and upgrades](TEMPLATE_ADOPTION.md) for the safe copy and
migration-plan commands.

| Required decision | Record before adoption |
| --- | --- |
| Repository and default branch | URL and protected branch name |
| Project identity | Project ID and `projects/<domain>/<project-id>/<project-id>.kicad_pro` |
| Approved KiCad build | Exact version, installer source, and rollout owner |
| Library model | Project-local, shared, or both; approved versions and owners |
| Mechanical owner | Interface reviewer and backup |
| Electrical owner | Schematic/PCB reviewer and backup |
| Integrator | Person authorized to merge and tag releases |
| Required checks | Exact check names, evidence retention, and failure policy |
| Assurance profile | `training` for rehearsal or `production` for a real board; record the decision in both registry and config |
| GitHub governance | Protected branch, exact required checks, three role assignments, and evidence record |
| Release authority | Who signs the release manifest and where immutable artifacts live |
| Recovery path | Backup, restore, and handoff procedure |

## First rehearsal

1. Clone the repository and read `README.md`.
2. Record `git status` and the current branch before opening KiCad.
3. Open the `.kicad_pro` in the approved KiCad build. Close KiCad and record `git status` again.
4. Make one non-electrical text change on a short-lived branch, run ERC/DRC and the repository checks, then complete a reviewed PR rehearsal.
5. Run a separate toolchain-migration rehearsal before deploying a newer KiCad build to the team.

The examples demonstrate repository mechanics; a real design still needs its own
identity, review, sourcing, mechanical handoff, and release record.

Before editing, run `python -m tools.check_toolchain --toolchain <toolchain-id>`;
the smallest bundled controller reference uses `kicad-10.0.0` and the LED
references use `kicad-10.0.5`.
A failure means the installed KiCad is read-only for this repository: do not save or
convert; use the approved build or open a dedicated migration branch.

## Reference examples

Use these to learn the project, library, firmware, catalog, and review workflow:

- [Arduino Uno R3 D13 status LED](examples/arduino-uno-status-led.md)
- [Raspberry Pi 40-pin GPIO17 status LED](examples/raspberry-pi-status-led.md)

They are deliberately small and synthetic. They are examples of organization and
review flow, not product requirements.
