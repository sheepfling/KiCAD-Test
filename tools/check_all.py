"""Run actual KiCad validation for one declared project or every declared project."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from lint_registry import lint
from validate import validate


def selected_projects(root: Path, requested: list[str] | None) -> list[dict[str, Any]]:
    registry: Any = json.loads((root / "catalog/projects.json").read_text(encoding="utf-8"))
    projects: Any = registry.get("projects") if isinstance(registry, dict) else None
    if not isinstance(projects, list):
        raise ValueError("Project registry has no projects list")
    available: dict[str, dict[str, Any]] = {
        item["id"]: item for item in projects
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    identifiers: list[str] = list(available) if requested is None else requested
    unknown: list[str] = [identifier for identifier in identifiers if identifier not in available]
    if unknown:
        raise ValueError(f"Unknown project ids: {unknown}")
    return [available[identifier] for identifier in identifiers]


def check_all(root: Path, output: Path, cli: str, requested: list[str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite retained evidence: {output}")
    output.mkdir(parents=True)
    governance: dict[str, Any] = lint(root, requested)
    rows: list[dict[str, Any]] = []
    if governance["status"] == "PASS":
        for project in selected_projects(root, requested):
            identifier: str = project["id"]
            report: dict[str, Any] = validate(root, output / identifier, cli, Path(project["config"]))
            rows.append({"id": identifier, "status": report["status"], "summary": f"{identifier}/summary.json"})
    result: dict[str, Any] = {
        "schema_version": "0.1",
        "lane": "KICAD_CLI_ALL_PROJECTS",
        "governance": governance,
        "projects": rows,
        "status": "PASS" if governance["status"] == "PASS" and rows and all(row["status"] == "PASS" for row in rows) else "FAIL",
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cli", default="kicad-cli")
    parser.add_argument("--project", action="append", dest="projects")
    parser.add_argument("--all", action="store_true", help="Check every declared project (the default).")
    args = parser.parse_args()
    result = check_all(args.root, args.output.resolve(), args.cli, None if args.all or not args.projects else args.projects)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
