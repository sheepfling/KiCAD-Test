# Forkable workflow audit

This records the earlier 0.2.0 audit. The 0.3.0 [project-island standard](REPOSITORY_STRUCTURE.md)
and [BOM policy](BOM_POLICY.md) supersede its centralized-layout and blanket source-only
recommendations. Use the [folder standard](REPOSITORY_STRUCTURE.md) for the durable layout.

| Finding | Resolution | Verification |
| --- | --- | --- |
| Generated BOMs, projections and model-derived schemas were tracked and required by CI | Remove exports from source; ignore their directories except README files; regenerate in a temporary directory in policy checks and upload generated CI artifacts | Clean-checkout generation, tamper/missing/stale output tests and Git hygiene tests |
| Tests depended on the live example project lists | Preserve authored fixture catalogs under `examples/catalog/`; assemble an isolated test repository; allow adopted live catalogs to replace examples | Reference regression tests plus an additional-project/adoption test |
| A fork could accidentally copy ignored local downloads through bootstrap | Copy the Git source inventory and filter known output/state paths | Bootstrap tests include ignored files and generated outputs |
| Native Docker command consumed a project variable it did not receive | Pass `PROJECT_ID` into the container; install dependencies into a writable temporary target | Workflow regression test; hosted native execution remains a separate verification |
| Dependency pins were duplicated across workflow steps; first-run installation was missing from onboarding | Install from `pyproject.toml` everywhere and document a virtual environment setup | Pinned local policy gate |
| macOS temporary paths resolved to a different prefix during source hashing | Resolve the root before calculating relative source paths | Existing four source-hash regressions on macOS |
| Markdown policy rejected valid parent-relative links between folders | Normalize links within the repository while retaining escape, case and symlink checks | Valid cross-folder link and escaping-link regressions |
| Several folders had no entry guidance; test extension and ownership were unclear | Add the linked folder map and catalog, tools, tests and schema guides | Markdown layout, links and reachability checks |
| Pyright configuration claimed tests while the driver checked only tools | Make strict typing scope explicit for services; behavior tests remain Ruff-checked and executed | Full portable gate |

## Verification on 2026-09-08

The full portable gate passed on macOS with Python 3.12.14 and the pinned development
dependencies: 135 tests, Ruff, strict Pyright, live registry/product/repository policy,
isolated generation and all 44 Markdown documents. `git diff --check` passed.

A separate clean, committed temporary copy passed preflight, project selection,
the six-project CI matrix, ignored generation without Git changes, product checks,
snapshot integrity verification and source-only bootstrap. All 25 previously tracked
reproducible exports are removed from the source tree in this change.

Native checks were not run: Docker's daemon was unavailable and the desktop KiCad
was 10.0.6, while the fixtures require 10.0.0 or 10.0.5. Hosted OS and pinned native
jobs still need to run on the proposed change. No hosted settings, releases or Git
history were changed by this audit.

## Decisions that belong to the adopting team

The template had no repository-wide license declaration at the time of this audit.
The original scaffold is now published under 0BSD. Adopting teams choose terms for
their own work; [licensing and adoption](LICENSING.md) explains how bootstrap keeps
the upstream root notice and history out of the company's first commit.

Set real CODEOWNERS, hosted branch rules, identities, toolchain installation records,
release authority and evidence retention before production adoption. The included
examples are training fixtures; their component choices and disabled training checks
are not production defaults. Start real unreleased boards with the development scaffold; apply production
controls before production readiness.

Exact native toolchains remain pinned to the declared images. A portable policy pass
is not evidence that hosted Windows/Linux jobs or pinned KiCad containers have run.
The installed desktop version must match a project's pin before native validation.

Dependency versions are pinned directly in `pyproject.toml`; a complete transitive
hash lock and offline package/container distribution are not implemented. Teams that
need those distribution guarantees should extend the same installation boundary.
