# First board

This is the shortest path from a fresh fork to a checked project island. Use
[Start here](START_HERE.md) when adopting company licensing or production controls.

1. Install Python 3.12+, create a virtual environment and install `.[dev]` as shown
   in the [root setup](../README.md#first-run-setup).
2. Check the workstation and initialize the fresh repository:

   ```sh
   python -B -m tools.template doctor
   python -B -m tools.template adopt --project-id my-hardware
   ```

3. Create the first standalone board and check native-runner availability:

   ```sh
   python -B -m tools.template new-project --project-id battery-board --kind pcb --toolchain kicad-10.0.5
   python -B -m tools.template doctor --native --toolchain kicad-10.0.5
   ```

4. Create and save the design under `projects/battery-board/kicad/`. Complete its
   `project.json`, `tests/contract.json` and design notes; the generated skeleton is
   intentionally incomplete and fails until it describes the real board.
5. Run the fast island check, then the pinned native check:

   ```sh
   python -B -m tools.ci --project battery-board
   python -B -m tools.ci --kicad --project battery-board --output projects/battery-board/build/review-001
   ```

6. Commit only authored source, push a short-lived branch and open a pull request.
   Review the exact Actions commit and retained evidence before merging.

The first passing check establishes a development baseline. Promotion to a prototype,
pilot or production release requires [release readiness](RELEASE_READINESS.md), real
reviewers and durable [release storage](RELEASE_STORAGE.md).
