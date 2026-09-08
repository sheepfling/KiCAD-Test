"""One portable local/CI entry point. Static checks do not replace actual KiCad runs."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .ci_matrix import build_matrix
from .hwrepo.documentation import check as documentation_check
from .hwrepo.generation import drift
from .hwrepo.models import (
    CommandEvidence,
    GenerationReport,
    ProjectStaticPipelineReport,
    StaticPipelineReport,
)
from .hwrepo.product import check as product_check
from .hwrepo.repository import check_repository
from .hwrepo.selection import ProjectSelector, resolve_project_ids
from .lint_registry import lint


def run_command(root: Path, *argv: str) -> CommandEvidence:
    """Execute one quality tool and preserve its typed outcome for the CI report."""
    started = datetime.now(timezone.utc).isoformat()
    try:
        result = subprocess.run(
            argv,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        return CommandEvidence(
            argv=argv,
            started_utc=started,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except OSError as exc:
        return CommandEvidence(
            argv=argv,
            started_utc=started,
            returncode=127,
            error=str(exc),
        )


def project_static_pipeline(
    root: Path, selected: tuple[str, ...]
) -> ProjectStaticPipelineReport:
    """Run the fast local policy lane for selected boards and dependent products."""
    registry = lint(root, list(selected))
    repository = check_repository(root, selected)
    product = product_check(root, selected_project_ids=selected)
    try:
        errors = drift(root, selected)
        generation = GenerationReport(
            status="FAIL" if errors else "PASS",
            issues=errors,
        )
    except (OSError, ValueError) as exc:
        generation = GenerationReport(status="FAIL", issues=(str(exc),))
    passed = (
        registry.status == "PASS"
        and repository.status == "PASS"
        and product.status == "PASS"
        and generation.status == "PASS"
    )
    return ProjectStaticPipelineReport(
        status="PASS" if passed else "FAIL",
        projects=selected,
        registry=registry,
        repository=repository,
        product=product,
        generation=generation,
    )


def static_pipeline(
    root: Path, selected: list[str] | None
) -> StaticPipelineReport | ProjectStaticPipelineReport:
    """Run the full shared gate or the fast local lane for selected boards."""
    if selected is not None:
        return project_static_pipeline(root, tuple(selected))
    registry = lint(root)
    repository = check_repository(root)
    documentation = documentation_check(root)
    product = product_check(root)
    try:
        errors = drift(root)
        generation = GenerationReport(
            status="FAIL" if errors else "PASS",
            issues=errors,
        )
    except (OSError, ValueError) as exc:
        generation = GenerationReport(status="FAIL", issues=(str(exc),))
    ruff = run_command(root, "ruff", "check", "--no-cache", "tools", "tests")
    pyright = run_command(root, "pyright", "--pythonpath", sys.executable, "tools")
    unit_tests = run_command(
        root,
        sys.executable,
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v",
    )
    passed = (
        registry.status == "PASS"
        and repository.status == "PASS"
        and documentation.status == "PASS"
        and product.status == "PASS"
        and generation.status == "PASS"
        and ruff.returncode == 0
        and pyright.returncode == 0
        and unit_tests.returncode == 0
    )
    return StaticPipelineReport(
        status="PASS" if passed else "FAIL",
        registry=registry,
        repository=repository,
        documentation=documentation,
        product=product,
        generation=generation,
        ruff=ruff,
        pyright=pyright,
        unit_tests=unit_tests,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        action="append",
        help=(
            "Run the fast local lane for one project; checks its dependencies and "
            "dependent products, not unrelated historical projects"
        ),
    )
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        help="Select projects with any matching metadata tag; may be repeated",
    )
    parser.add_argument(
        "--exclude-tag",
        action="append",
        dest="excluded_tags",
        help="Remove projects with this metadata tag after selection; may be repeated",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root; defaults to the current working directory",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--matrix", action="store_true", help="Print the declared KiCad matrix.")
    mode.add_argument("--kicad", action="store_true", help="Execute one or more pinned KiCad checks.")
    mode.add_argument("--fault-probes", action="store_true", help="Run disposable KiCad negative probes.")
    mode.add_argument("--release", action="store_true", help="Validate one typed release candidate.")
    mode.add_argument("--metrics", action="store_true", help="Report current policy and deviation metrics.")
    parser.add_argument("--cli", default="kicad-cli")
    parser.add_argument("--output", type=Path, help="New evidence directory, required by KiCad modes.")
    parser.add_argument(
        "--manifest",
        help="Repository-relative typed release manifest, required by --release and optional for --metrics.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    selector = ProjectSelector(
        project_ids=tuple(args.project or ()),
        tags=tuple(args.tags or ()),
        excluded_tags=tuple(args.excluded_tags or ()),
    )
    try:
        selected = resolve_project_ids(root, selector) if selector.active else None
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.matrix:
        matrix = build_matrix(root, selected)
        # GitHub Actions consumes this mode through a one-line GITHUB_OUTPUT value.
        print(matrix.model_dump_json())
        return 0
    if args.kicad:
        if args.output is None:
            parser.error("--kicad requires a new --output directory")
        from .check_all import check_all

        kicad = check_all(
            root,
            args.output.resolve(),
            args.cli,
            None if selected is None else list(selected),
        )
        print(kicad.model_dump_json(indent=2))
        return 0 if kicad.status == "PASS" else 1
    if args.fault_probes:
        if selected is not None:
            parser.error("--fault-probes does not support project selectors")
        if args.output is None:
            parser.error("--fault-probes requires a new --output directory")
        from .fault_probe import probe

        fault_probes = probe(root, args.output.resolve())
        print(fault_probes.model_dump_json(indent=2))
        return 0 if fault_probes.status == "PASS" else 1
    if args.release:
        if selected is not None:
            parser.error("--release does not support project selectors")
        if args.manifest is None:
            parser.error("--release requires --manifest")
        from .hwrepo.contracts import read_model, repo_path
        from .hwrepo.models import ReleaseManifest
        from .hwrepo.release import check as release_check

        try:
            manifest = read_model(repo_path(root, args.manifest), ReleaseManifest)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        release = release_check(root, manifest)
        print(release.model_dump_json(indent=2))
        return 0 if release.status == "PASS" else 1
    if args.metrics:
        if selected is not None:
            parser.error("--metrics does not support project selectors")
        from .hwrepo.contracts import read_model, repo_path
        from .hwrepo.metrics import collect
        from .hwrepo.models import ReleaseManifest

        try:
            deviations = (
                ()
                if args.manifest is None
                else read_model(repo_path(root, args.manifest), ReleaseManifest).deviations
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        metrics = collect(root, deviations)
        print(metrics.model_dump_json(indent=2))
        return 0
    static = static_pipeline(root, None if selected is None else list(selected))
    print(static.model_dump_json(indent=2))
    return 0 if static.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
