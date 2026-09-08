# Versioning, tags, and releases

## Working versions

- Use one issue-linked branch and PR per logical change.
- Commit the board source and the exact local-library revision it needs together.
- Record the approved KiCad version in `catalog/toolchains.json` and the PR. Run `python -m tools.check_toolchain --toolchain <id>` before editing. A new KiCad version or project-format rewrite is a dedicated migration branch/PR.
- Do not use a tag to mark unfinished work, a personal checkpoint, or a CI artifact.

## Release versions

Use annotated tags on an accepted release commit, for example `controller-v0.3.0`. Tag names must identify the project and released revision without implying approval before approval exists. Complete a typed release manifest from `templates/release-manifest.example.json` at the tagged commit and validate it with `python -B -m tools.ci --release --manifest release/<release-id>.json`.

The manifest binds the release to the Git commit, selected product/variant revisions,
exact KiCad build, library revisions plus provenance/licensing hashes, interface
revisions, typed generated artifacts, evidence, limitations, and approval record.
Store immutable manufacturing artifacts in the approved release location; short-lived
CI artifacts are review evidence only.

## Restoring or handing off

Restore by cloning or checking out the recorded tag and verifying artifact hashes—not by copying a desktop folder over another engineer's worktree. On handoff, record the branch, last commit, status, open PR, outstanding findings, local unpushed work, and responsible next person.
