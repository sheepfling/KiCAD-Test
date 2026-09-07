# Start here — KiCad/Git template adoption

**Status: candidate template. The included controller fixture is synthetic and NOT FOR MANUFACTURE.**

Complete this record before copying the structure to a real board repository. A blank field is a reason to stop and ask the designated maintainer, not a prompt to guess.

| Required decision | Record before adoption |
| --- | --- |
| Repository and default branch | URL and protected branch name |
| Project identity | Board/project ID and `boards/<project-id>/<project-id>.kicad_pro` |
| Approved KiCad build | Exact version, installer source, and rollout owner |
| Library model | Project-local, shared, or both; approved versions and owners |
| Mechanical owner | Interface reviewer and backup |
| Electrical owner | Schematic/PCB reviewer and backup |
| Integrator | Person authorized to merge and tag releases |
| Required checks | Exact check names, evidence retention, and failure policy |
| Release authority | Who signs the release manifest and where immutable artifacts live |
| Recovery path | Backup, restore, and handoff procedure |

## First rehearsal

1. Clone the repository and read `README.md`.
2. Record `git status` and the current branch before opening KiCad.
3. Open the `.kicad_pro` in the approved KiCad build. Close KiCad and record `git status` again.
4. Make one non-electrical text change on a short-lived branch, run ERC/DRC and the repository checks, then complete a reviewed PR rehearsal.
5. Run a separate toolchain-migration rehearsal before deploying a newer KiCad build to the team.

Do not promote the controller fixture, a green CI run, or a copied directory to a hardware approval.
