"""Typed, safe template preflight, bootstrap and migration-plan command line."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .hwrepo.importing import import_project
from .hwrepo.initialization import initialize
from .hwrepo.models import ProjectKind
from .hwrepo.scaffold import new_project
from .hwrepo.template import bootstrap, plan_upgrade, preflight


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "preflight", "bootstrap", "upgrade-plan", "new-project", "import-project"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--project-id")
    parser.add_argument("--target-version")
    parser.add_argument("--kind", choices=[kind.value for kind in ProjectKind], default="pcb")
    parser.add_argument("--toolchain")
    parser.add_argument("--source", type=Path, help="Existing .kicad_pro file to import")
    parser.add_argument("--dry-run", action="store_true", help="Preview an import without writing files")
    args = parser.parse_args()
    if args.command != "import-project" and (args.dry_run or args.source is not None):
        parser.error("--source and --dry-run require import-project")
    if args.command == "init":
        if args.project_id is None:
            parser.error("init requires --project-id (the repository identity)")
        result = initialize(args.root, args.project_id)
    elif args.command == "import-project":
        if args.project_id is None or args.toolchain is None or args.source is None:
            parser.error("import-project requires --source, --project-id and --toolchain")
        result = import_project(args.root, args.source, args.project_id, args.toolchain, args.dry_run)
    elif args.command == "new-project":
        if args.project_id is None or args.toolchain is None:
            parser.error("new-project requires --project-id and --toolchain")
        result = new_project(args.root, args.project_id, ProjectKind(args.kind), args.toolchain)
    elif args.command == "preflight":
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
