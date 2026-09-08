"""Typed, safe template preflight, bootstrap and migration-plan command line."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .hwrepo.template import bootstrap, plan_upgrade, preflight


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "bootstrap", "upgrade-plan"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--project-id")
    parser.add_argument("--target-version")
    args = parser.parse_args()
    if args.command == "preflight":
        result = preflight(args.root)
    elif args.command == "bootstrap":
        if args.destination is None or args.project_id is None:
            parser.error("bootstrap requires --destination and --project-id")
        result = bootstrap(args.root, args.destination, args.project_id)
    else:
        if args.target_version is None:
            parser.error("upgrade-plan requires --target-version")
        result = plan_upgrade(args.root, args.target_version)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
