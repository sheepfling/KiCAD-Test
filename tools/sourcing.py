"""Validate a typed, manually captured supplier-offer snapshot without network access."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .hwrepo.contracts import read_model, repo_path
from .hwrepo.models import PolicyIssue, SourcingSnapshot, SourcingSnapshotReport
from .hwrepo.sourcing import check


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, help="Repository-relative sourcing snapshot")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        result = check(root, read_model(repo_path(root, args.snapshot), SourcingSnapshot))
    except (OSError, ValueError) as exc:
        result = SourcingSnapshotReport(
            snapshot_id="unreadable-snapshot",
            offers=0,
            status="FAIL",
            issues=(
                PolicyIssue(
                    code="SOURCING_LOAD",
                    location=args.snapshot,
                    message=str(exc),
                ),
            ),
        )
        print(str(exc), file=sys.stderr)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
