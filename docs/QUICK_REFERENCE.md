# KiCad + Git quick reference

Get the project assignment. Close KiCad before changing branches. Preserve existing
work. Fetch/pull current main, then create one issue-linked work branch. Use the
branch and project path recorded by the adopted repository; do not guess when the
assignment or starting state is unclear.

Open the `.kicad_pro`, not a detached schematic copy. Edit, synchronize schematic/PCB as needed, run checks, and save. Review the changed source. Commit locally, push, and open a PR. These are four separate actions.

Continue tomorrow on the same branch/PR. Pulling that branch does not automatically merge main. Do not reset, clean, or force-push to resolve uncertainty.

Inspect the Actions review artifact and checked commit. A green run is not a
substitute for independent approval or configured branch protection. Another
qualified person reviews; the integrator accepts; then close KiCad, update local
main and hand back the assignment.

On conflict, missing libraries, new tool versions or unexpected changes: stop, preserve work and ask the maintainer with branch, SHA, status and error. Never guess ours/theirs.

Checks: `python -m tools.validate --output build/review-001` (new output name each time). Use the exact catalogued toolchain for the project; this template exercises KiCad 10.0.0 and 10.0.5. Python 3.12+. Libraries travel with the project.
