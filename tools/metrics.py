"""Print typed, read-only current metrics for template policy and release deviations."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .hwrepo.contracts import read_model, repo_path
from .hwrepo.metrics import collect
from .hwrepo.models import ReleaseManifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", help="Optional repository-relative release manifest")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        deviations = (
            ()
            if args.manifest is None
            else read_model(repo_path(root, args.manifest), ReleaseManifest).deviations
        )
        result = collect(root, deviations)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
