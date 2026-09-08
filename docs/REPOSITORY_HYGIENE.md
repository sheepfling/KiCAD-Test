# Repository hygiene and accidental-file safety

This repository is a reviewable source record, not a shared Downloads folder. Its
ignore rules are designed for contributors who may work primarily through KiCad,
Windows Explorer or an Office application rather than Git commands.

## Two layers of protection

`.gitignore` prevents ordinary `git add` from selecting personal/editor state,
temporary files, Office files, media, archives and installers. The repository policy
also rejects those files if someone uses a force-add command or a graphical client
overrides the ignore list. A policy failure is reported as either
`TRACKED_LOCAL_STATE` or `TRACKED_UNMANAGED_ARTIFACT`.

Ignored files remain on the contributor's computer; the rule does not delete them.
Do not use a force-add option to bypass it. If an ignored file appears to be needed,
stop and propose a reviewed policy change rather than making a local exception.

## External reference bundles

Downloaded handoff bundles and planning packets are temporary reference material.
Keep their archives outside the repository, unpack or inspect them in a separate
working location, and do not commit the archive or an extracted vendor-style copy.
When a reference materially informs a decision, record only its source, received
date and SHA-256 in a reviewed Markdown or structured record. This preserves the
audit trail without turning a binary bundle into repository history.

## What is intentionally ignored

- Operating-system metadata, recycle/trash folders, thumbnails and file-manager
  leftovers from Windows, macOS and Linux.
- KiCad locks, local preferences, autosaves, caches and backup directories.
- Editor/workspace settings, temporary/recovery files and local test/build output.
- Word, Excel, PowerPoint, LibreOffice, Apple iWork, OneNote and mail-client files.
- Images, audio, video, archives, downloaded installers and disk images.

## What remains eligible for review

KiCad source, project-local libraries, Python, Markdown, JSON/YAML and generated
CSV views remain normal tracked source. PDF, STEP/STP and DXF are not globally
ignored because a real mechanical handoff may need a reviewed drawing or model.
When they are used, give them a stable repository path, declare or link them from
the relevant project/handoff record, and review their source, revision and hash.

Before requesting review, close KiCad and inspect `git status --short`. Stage only
the intended source and evidence records. Unexpected files are a stop condition:
leave them untracked/ignored or move them outside the repository; do not discard
them merely to make status look clean.
