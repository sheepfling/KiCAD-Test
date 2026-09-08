# KiCad + Git desk card v0.2 candidate

**Unapproved. Synthetic public pilot. NOT FOR MANUFACTURE.**

Get the board assignment. Close KiCad before changing branches. Preserve existing work. Fetch/pull current main, then create one issue-linked branch. During setup only, use the pilot branch named in the README; main does not contain the project until setup is accepted.

Open the `.kicad_pro`, not a detached schematic copy. Edit, synchronize schematic/PCB as needed, run checks, and save. Review the changed source. Commit locally, push, and open a PR. These are four separate actions.

Continue tomorrow on the same branch/PR. Pulling that branch does not automatically merge main. Do not reset, clean, or force-push to resolve uncertainty.

Inspect the Actions review artifact and checked commit. A green run is not independent approval, a board lock, protected-main enforcement, or permission to manufacture. Another qualified person reviews; the integrator accepts; then close KiCad, update local main and hand back the assignment.

On conflict, missing libraries, new tool versions or unexpected changes: stop, preserve work and ask the maintainer with branch, SHA, status and error. Never guess ours/theirs.

Checks: `python -m tools.validate --output build/review-001` (new output name each time). Toolchain: KiCad 10.0.5; Python 3.12+. Libraries travel with the project.
