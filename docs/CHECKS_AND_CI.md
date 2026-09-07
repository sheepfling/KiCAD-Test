# Checks and CI

The template has two complementary gates. Neither replaces engineering review.

| Gate | Scope | Purpose |
| --- | --- | --- |
| Static governance lint | One declared project or all projects | Checks project registration, source inventory, controlled part/interface/library references, and safe repository-relative paths. |
| KiCad validation | One declared project or all projects | Runs the pinned KiCad CLI, ERC, DRC, schematic/PCB parity, netlist contract, SVG exports, and source-unchanged guard. |

## Commands

```sh
# Fast static checks
python tools/lint_registry.py --project controller
python tools/lint_registry.py --all

# One project with its declared configuration
python tools/validate.py --config pilot.json --output build/controller-review-001

# Every project declared in catalog/projects.json
python tools/check_all.py --all --output build/all-review-001
```

Every output directory is write-once. Choose a new name for every run. Close KiCad before running a check; a lock file or unexpected source rewrite is a stop condition.

## Adding a project

1. Create the complete project under `boards/<project-id>/`.
2. Give it a project-specific JSON configuration with exact KiCad version, project path, source roots, required inputs, and expected netlist/check policy.
3. Add it to `catalog/projects.json` with its status, configuration path, identity requirement, interfaces, and approved libraries.
4. Run `lint_registry.py --project <project-id>` before enabling full KiCad checks.
5. CI automatically adds one matrix lane per registered project using the project's digest-pinned KiCad image. Review the generated lane before adding a new image/version.

## CI behavior

CI first resolves a project-specific KiCad matrix, runs the all-project static lint and unit tests, then runs `check_all.py --project <id>` in each project's digest-pinned container. This means a new board, shared library, interface, or catalog entry cannot quietly bypass repository-wide governance or run under a different KiCad build. The existing fault probes remain specific to the synthetic controller fixture.
