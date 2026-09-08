# Checks and CI

The template has complementary policy and native-tool checks. None replaces engineering review.

| Gate | Scope | Purpose |
| --- | --- | --- |
| Python quality | Policy/generation/validation implementation and tests | Ruff checks import/style hygiene; strict Pyright verifies typed implementation contracts; unit tests exercise public script functions and architecture rules. |
| Markdown documentation policy | Repository Markdown sources | Checks layout, local links/fragments, exact path case, repository containment and reachability from declared documentation roots. |
| Full portable gate | Entire repository | Runs shared product/evidence/variant policy, path/discovery hygiene, generated-view drift, Ruff, Pyright and all unit tests through `python -m tools.ci`. |
| Fast local project gate | Selected project plus dependent products | Validates the selected project's registry/configuration/CAD dependencies, product records that explicitly declare that project, and only those product projections. It does not run repository-wide Python quality checks or unrelated historical projects. |
| Static governance lint | One declared project or all projects | Checks project registration, source inventory, controlled part/interface/library references, and safe repository-relative paths. |
| KiCad validation | One declared project or all projects | Runs the pinned KiCad CLI and a kind-specific gate: PCB gets ERC, DRC/parity, netlist identity and both SVGs; schematic-only gets ERC and schematic SVG; system wiring gets whole-product relation coverage; harness interface gets exact harness/conductor/endpoint coverage. Every kind gets source-unchanged protection. |
| Desktop toolchain check | Before opening for editing | Refuses editing when the local KiCad version differs from the catalogued approved build. |

## Commands

```sh
# Fast static checks
python -B -m tools.ci

# Fast local board check: use during board development
python -B -m tools.ci --project arduino-uno-status-led

# Tag selectors: repeated --tag values are an OR match; exclusions apply afterward
python -B -m tools.ci --tag status-led
python -B -m tools.ci --exclude-tag legacy
# Example after a team assigns this baseline tag to a project
python -B -m tools.ci --tag abc-v1.0.1 --exclude-tag legacy

# CI-driver modes
python -B -m tools.ci --matrix
python -B -m tools.ci --kicad --project controller --output build/controller-review-001
python -B -m tools.ci --kicad --tag reference --output build/reference-review-001
python -B -m tools.ci --fault-probes --output build/fault-probes-001
python -B -m tools.ci --release --manifest release/<release-id>.json
python -B -m tools.template preflight
python -B -m tools.template upgrade-plan --target-version <template-version>
python -B -m tools.ci --metrics --manifest release/<release-id>.json

# Focused checks when diagnosing a specific failure
python -B -m tools.docs_policy
python -m tools.check_toolchain --toolchain kicad-10.0.5
python -m tools.lint_registry --project controller
python -m tools.lint_registry --project arduino-uno-status-led
python -m tools.lint_registry --tag status-led
python -m tools.lint_registry --all

# One project with its declared configuration
python -m tools.validate --config pilot.json --output build/controller-review-001
python -m tools.validate --config configs/arduino-uno-status-led.json --output build/arduino-review-001

# Every project declared in catalog/projects.json
python -m tools.check_all --all --output build/all-review-001
python -m tools.check_all --exclude-tag legacy --output build/current-review-001
```

Every output directory is write-once. Choose a new name for every run. Close KiCad before running a check; a lock file or unexpected source rewrite is a stop condition.

## Adding a project

1. Select `pcb`, `schematic`, `system_wiring`, or `harness_interface`; create the project under `boards/`, `schematics/`, `systems/`, or `harnesses/` respectively. See [project kinds](PROJECT_KINDS.md).
2. Choose `training` or `production` before creating its configuration. A production project starts from `templates/production-project-config.example.json` and must keep ERC/DRC ignored-check lists empty.
3. Give it a project-specific JSON configuration with exact KiCad version, toolchain ID, kind, project path, source roots, required inputs, and the matching typed validation contract. System wiring names whole-product relation/terminal/harness/mechanical coverage; harness interface names its exact electrical conductor/terminal/harness coverage.
4. Add it to `catalog/projects.json` with its assurance profile, status, configuration path, identity requirement, tags, interfaces, approved libraries, and—when production—mechanical and governance records.
5. Run `python -m tools.lint_registry --project <project-id>` before enabling full KiCad checks.
6. CI automatically adds one matrix lane per registered project using the project's digest-pinned KiCad image. Review the generated lane before adding a new image/version.

## CI behavior

CI first resolves a project-specific KiCad matrix, then runs Ruff, strict Pyright and
the all-project static/unit/documentation suite on Windows, macOS and Linux. It then runs
`python -m tools.ci --kicad --project <id>` in each project's digest-pinned container. This means
a new board, shared library, interface, or catalog entry cannot quietly bypass
repository-wide governance or run under a different KiCad build. The existing fault
probes remain specific to the synthetic controller fixture.
## Portable product and collaboration checks

Use `python -B -m tools.ci` for the full local/CI static gate; it runs Markdown
documentation policy, Ruff, strict Pyright and all behavior tests in addition to
repository-wide policy checks. Use `python -B -m tools.ci --project <id>` for a
fast local board gate: it checks the selected board and products that explicitly
depend on it, without running unrelated boards or the whole Python quality suite.
Add `--kicad --project <id> --output build/review-001` to execute pinned native
checks for that board too.
The configured hosted Python matrix covers Windows, Linux and macOS; a local
Windows pass is not evidence that those hosted jobs have executed.

See [product workflow](PRODUCT_WORKFLOW.md) for assemblies, variants, evidence,
mechanical/harness records and generated BOMs, and [acceptance coverage](TEMPLATE_ACCEPTANCE.md)
for explicit limits. See [Markdown documentation policy](MARKDOWN_POLICY.md) for
the source scope, local-link rules and exception record. See [repository hygiene](REPOSITORY_HYGIENE.md)
for the two-layer ignored-file policy. The direct `validate.py` entry point now runs repository
governance/product preflight and verifies mapped KiCad `PART_ID` fields.

## Project metadata selectors

`catalog/projects.json` owns each project's `tags`. Tags are exact, portable
identifiers, so values such as `legacy`, `prototype`, `customer-a`, or
`abc-v1.0.1` are valid. They are categorization metadata—not Git tags, release
approval, or a replacement for a KiCad/toolchain version. Keep lifecycle tags
(`legacy`, `active`), product-family tags (`status-led`), and approved internal
baseline labels distinct so selection remains understandable.

`--project` and repeated `--tag` options are combined as an OR selection;
repeated `--exclude-tag` options are then subtracted. With no selector, the full
gate runs. A selector that matches no project is a failure. The same selectors
work with `tools.ci`, `tools.ci --kicad`, `tools.ci --matrix`,
`tools.lint_registry`, and `tools.check_all`.
