"""Thin read-only CLI for typed release-readiness validation."""
from __future__ import annotations

import argparse
from pathlib import Path

from .hwrepo.contracts import read_model, repo_path
from .hwrepo.models import ReleaseManifest
from .hwrepo.release import check


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Repository-relative release manifest")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        manifest = read_model(repo_path(root, args.manifest), ReleaseManifest)
        report = check(root, manifest)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(report.model_dump_json(indent=2))
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
