# Template bootstrap and upgrades

The template contract in `templates/template-contract.json` names the portable
files required for a reusable starting point. Verify it before copying the template:

```sh
python -B -m tools.template preflight
```

## Bootstrap

To create a new local copy from a **clean, committed** template source, choose a
new, nonexistent directory outside the source template:

```sh
python -B -m tools.template bootstrap --destination ../my-hardware-repo --project-id my-board
```

The command copies the controlled template into a staging directory and atomically
places it only after writing `template-adoption.json`. It excludes `.git`, build
outputs and known local state. It never overwrites a destination, initializes a
remote, creates a commit, changes repository permissions, opens KiCad or modifies a
design. Bootstrap copies the template's synthetic examples intentionally; remove or
replace them in a reviewed adoption change, never by treating them as production
source.

The adopting maintainer must then initialize/attach the correct Git remote, complete
[Start here](START_HERE.md), select the approved KiCad version, configure hosted
governance and commit the adoption record. A generated `template-adoption.json` only
records the chosen project identity and the source template version; it is not a
release or approval record.

## Upgrade plan

Every template change that needs adopter action adds one forward migration record to
`templates/template-upgrades.json`. Ask the helper for the unique reviewed path:

```sh
python -B -m tools.template upgrade-plan --target-version 0.2.0
```

The helper only returns ordered typed steps. It refuses downgrades, missing paths and
ambiguous migration routes; it does not rewrite KiCad, JSON, documentation or Git
history. Review the proposed steps on a branch, run the full local and native gates,
then apply the adopting repository's normal review and release process.
