"""Fail-closed static lint for declared KiCad projects and controlled catalogs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from validate import hashes


PROJECT_STATUSES: set[str] = {"training_fixture", "engineering", "release_candidate"}
PART_FIELDS: set[str] = {"id", "manufacturer", "mpn", "datasheet_url", "lifecycle", "status"}
LIBRARY_FIELDS: set[str] = {"id", "version", "path", "owner", "status"}


def read_json(path: Path, label: str, issues: list[str]) -> dict[str, Any]:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"{label}: cannot read JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        issues.append(f"{label}: expected a JSON object")
        return {}
    return data


def repository_path(root: Path, value: Any, label: str, issues: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        issues.append(f"{label}: expected a non-empty repository-relative path")
        return None
    normalized: PurePosixPath = PurePosixPath(value.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts or normalized == PurePosixPath("."):
        issues.append(f"{label}: unsafe repository path {value!r}")
        return None
    path: Path = root.joinpath(*normalized.parts)
    if root not in path.resolve().parents and path.resolve() != root:
        issues.append(f"{label}: escapes the repository root")
        return None
    return path


def records_by_id(data: dict[str, Any], key: str, label: str, issues: list[str]) -> dict[str, dict[str, Any]]:
    records: Any = data.get(key)
    if not isinstance(records, list):
        issues.append(f"{label}: {key!r} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            issues.append(f"{label}: {key}[{index}] needs a non-empty id")
            continue
        identifier: str = record["id"]
        if identifier in result:
            issues.append(f"{label}: duplicate id {identifier!r}")
            continue
        result[identifier] = record
    return result


def lint(root: Path, selected: list[str] | None = None) -> dict[str, Any]:
    """Lint all declared project inputs or an explicit project subset."""
    root = root.resolve()
    issues: list[str] = []
    registry: dict[str, Any] = read_json(root / "catalog/projects.json", "project registry", issues)
    catalogs: Any = registry.get("catalogs")
    if not isinstance(catalogs, dict):
        issues.append("project registry: catalogs must be an object")
        catalogs = {}

    parts_path = repository_path(root, catalogs.get("parts"), "parts catalog", issues)
    interfaces_path = repository_path(root, catalogs.get("interfaces"), "interface catalog", issues)
    libraries_path = repository_path(root, catalogs.get("libraries"), "library catalog", issues)
    parts = records_by_id(read_json(parts_path, "parts catalog", issues) if parts_path else {}, "parts", "parts catalog", issues)
    interfaces = records_by_id(read_json(interfaces_path, "interface catalog", issues) if interfaces_path else {}, "interfaces", "interface catalog", issues)
    libraries = records_by_id(read_json(libraries_path, "library catalog", issues) if libraries_path else {}, "libraries", "library catalog", issues)

    for identifier, record in parts.items():
        missing: set[str] = PART_FIELDS - set(record)
        if missing:
            issues.append(f"part {identifier}: missing required fields {sorted(missing)}")
    for identifier, record in interfaces.items():
        pins: Any = record.get("pins")
        if not isinstance(record.get("revision"), str) or not record["revision"]:
            issues.append(f"interface {identifier}: needs a revision")
        if not isinstance(pins, list) or not pins:
            issues.append(f"interface {identifier}: needs a non-empty pins list")
            continue
        numbers: set[str] = set()
        for index, pin in enumerate(pins):
            required: tuple[str, ...] = ("number", "signal", "direction")
            if not isinstance(pin, dict) or not all(isinstance(pin.get(field), str) and pin[field] for field in required):
                issues.append(f"interface {identifier}: pin {index} needs number, signal, and direction")
                continue
            if pin["number"] in numbers:
                issues.append(f"interface {identifier}: duplicate pin number {pin['number']!r}")
            numbers.add(pin["number"])
    for identifier, record in libraries.items():
        missing = LIBRARY_FIELDS - set(record)
        if missing:
            issues.append(f"library {identifier}: missing required fields {sorted(missing)}")
            continue
        path = repository_path(root, record["path"], f"library {identifier} path", issues)
        if path is not None and not path.is_dir():
            issues.append(f"library {identifier}: declared path is missing: {record['path']}")

    raw_projects: Any = registry.get("projects")
    if not isinstance(raw_projects, list) or not raw_projects:
        issues.append("project registry: projects must be a non-empty list")
        raw_projects = []
    project_map: dict[str, dict[str, Any]] = {}
    for index, project in enumerate(raw_projects):
        if not isinstance(project, dict) or not isinstance(project.get("id"), str) or not project["id"]:
            issues.append(f"project registry: projects[{index}] needs a non-empty id")
            continue
        if project["id"] in project_map:
            issues.append(f"project registry: duplicate project id {project['id']!r}")
            continue
        project_map[project["id"]] = project

    requested: list[str] = list(project_map) if selected is None else selected
    for identifier in requested:
        if identifier not in project_map:
            issues.append(f"project registry: unknown project {identifier!r}")
            continue
        project = project_map[identifier]
        status: Any = project.get("status")
        if status not in PROJECT_STATUSES:
            issues.append(f"project {identifier}: unsupported status {status!r}")
        config_path = repository_path(root, project.get("config"), f"project {identifier} config", issues)
        project_file = repository_path(root, project.get("project"), f"project {identifier} file", issues)
        if project_file is not None and not project_file.is_file():
            issues.append(f"project {identifier}: project file is missing")
        config = read_json(config_path, f"project {identifier} config", issues) if config_path else {}
        required_config: tuple[str, ...] = (
            "project_id", "project", "kicad_version", "image", "source_roots", "required_inputs",
            "components", "nets", "expected_ignored_checks", "not_for_manufacture",
        )
        missing_config: list[str] = [key for key in required_config if key not in config]
        if missing_config:
            issues.append(f"project {identifier}: config missing required keys {missing_config}")
        if config.get("project_id") != identifier:
            issues.append(f"project {identifier}: config project_id must match registry id")
        if config.get("project") != project.get("project"):
            issues.append(f"project {identifier}: config project path must match registry")
        if not isinstance(config.get("kicad_version"), str) or not config["kicad_version"]:
            issues.append(f"project {identifier}: config needs an exact kicad_version")
        if not isinstance(config.get("image"), str) or "@sha256:" not in config["image"]:
            issues.append(f"project {identifier}: config image must be digest-pinned")
        if status == "training_fixture" and config.get("not_for_manufacture") is not True:
            issues.append(f"project {identifier}: training fixture must remain marked not_for_manufacture")
        try:
            source: dict[str, str] = hashes(root, config.get("source_roots", ["boards"]))
            expected: Any = config.get("required_inputs")
            if not isinstance(expected, list) or set(source) != set(expected):
                issues.append(f"project {identifier}: required_inputs do not match declared source_roots")
        except (OSError, TypeError, ValueError) as exc:
            issues.append(f"project {identifier}: invalid source scope: {exc}")

        identity: Any = project.get("component_identity")
        if not isinstance(identity, dict) or not isinstance(identity.get("required"), bool) or not isinstance(identity.get("part_ids"), list):
            issues.append(f"project {identifier}: component_identity requires boolean required and list part_ids")
            identity = {"required": False, "part_ids": []}
        if status != "training_fixture" and not identity["required"]:
            issues.append(f"project {identifier}: non-fixture projects must require component identity")
        part_ids: list[Any] = identity["part_ids"]
        if identity["required"] and not part_ids:
            issues.append(f"project {identifier}: component identity is required but no part ids are declared")
        for part_id in part_ids:
            if not isinstance(part_id, str) or part_id not in parts:
                issues.append(f"project {identifier}: unknown approved part {part_id!r}")
        interface_ids: Any = project.get("interfaces", [])
        if not isinstance(interface_ids, list):
            issues.append(f"project {identifier}: interfaces must be a list")
            interface_ids = []
        for interface_id in interface_ids:
            if not isinstance(interface_id, str) or interface_id not in interfaces:
                issues.append(f"project {identifier}: unknown interface {interface_id!r}")
        library_ids: Any = project.get("library_ids", [])
        if not isinstance(library_ids, list):
            issues.append(f"project {identifier}: library_ids must be a list")
            library_ids = []
        for library_id in library_ids:
            if not isinstance(library_id, str) or library_id not in libraries:
                issues.append(f"project {identifier}: unknown library {library_id!r}")

    return {
        "schema_version": "0.1",
        "lane": "STATIC_GOVERNANCE_LINT",
        "projects": requested,
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project", action="append", dest="projects")
    parser.add_argument("--all", action="store_true", help="Lint every declared project (the default).")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = lint(args.root, None if args.all or not args.projects else args.projects)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
