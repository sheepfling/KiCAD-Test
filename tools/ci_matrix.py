"""Emit one digest-pinned KiCad CI lane per declared project."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from lint_registry import lint


def build_matrix(root: Path) -> dict[str, list[dict[str, str]]]:
    root = root.resolve()
    governance: dict[str, Any] = lint(root)
    if governance["status"] != "PASS":
        raise ValueError(f"Refusing CI matrix for invalid registry: {governance['issues']}")
    registry: Any = json.loads((root / "catalog/projects.json").read_text(encoding="utf-8"))
    projects: Any = registry.get("projects") if isinstance(registry, dict) else None
    if not isinstance(projects, list):
        raise ValueError("Project registry has no projects list")
    include: list[dict[str, str]] = []
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("Project registry contains an invalid entry")
        identifier: Any = project.get("id")
        config_name: Any = project.get("config")
        if not isinstance(identifier, str) or not isinstance(config_name, str):
            raise ValueError("Project registry needs id and config strings")
        config: Any = json.loads((root / config_name).read_text(encoding="utf-8"))
        if not isinstance(config, dict) or not isinstance(config.get("image"), str) or not isinstance(config.get("kicad_version"), str):
            raise ValueError(f"Project {identifier} has no valid KiCad image/version")
        include.append({"project": identifier, "image": config["image"], "kicad_version": config["kicad_version"]})
    if not include:
        raise ValueError("Project registry contains no CI projects")
    return {"include": include}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(build_matrix(args.root), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
