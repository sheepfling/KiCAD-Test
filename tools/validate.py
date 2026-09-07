"""Fail-closed synthetic KiCad check; this is not hardware approval."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def local_state(path: Path) -> bool:
    """Only known non-source KiCad preferences/cache files are excluded."""
    return path.suffix == ".kicad_prl" or path.name == "fp-info-cache"
####


def hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / "boards").rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Source symlink is not allowed: {path}")
        ####
        if path.is_file() and not local_state(path):
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
        ####
    ####
    return result
####


def check_report(path: Path, kind: str, config: dict[str, Any] | None = None) -> int:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data.get("kicad_version"):
        raise ValueError("Missing KiCad report identity")
    ####
    if kind not in {"erc", "drc"}:
        raise ValueError("Unsupported report kind")
    ####
    if config is not None:
        if data["kicad_version"] != config["kicad_version"]:
            raise ValueError("Report toolchain identity differs")
        ####
        if data.get("$schema") != f"https://schemas.kicad.org/{kind}.v1.json":
            raise ValueError("Unexpected report schema")
        ####
        if data.get("included_severities") != ["error", "warning", "exclusion"]:
            raise ValueError("Report must include errors, warnings and exclusions")
        ####
        ignored: Any = data.get("ignored_checks")
        if not isinstance(ignored, list) or any(not isinstance(v, dict) for v in ignored):
            raise ValueError("Missing ignored-check inventory")
        ####
        keys: list[str] = [str(item.get("key", "")) for item in ignored]
        if sorted(keys) != sorted(config["expected_ignored_checks"][kind]):
            raise ValueError(f"Disabled-check inventory changed: {keys}")
        ####
    ####
    lists: list[Any]
    if kind == "erc":
        sheets: Any = data.get("sheets")
        if not isinstance(sheets, list) or not sheets:
            raise ValueError("Missing ERC sheets")
        ####
        if any(not isinstance(sheet, dict) for sheet in sheets):
            raise ValueError("Malformed ERC sheet")
        ####
        lists = [sheet.get("violations") for sheet in sheets]
    else:
        lists = [data.get(key) for key in ("violations", "unconnected_items", "schematic_parity")]
    ####
    if any(not isinstance(items, list) for items in lists):
        raise ValueError(f"Missing or malformed {kind} findings")
    ####
    return sum(len(items) for items in lists)
####


def check_netlist(path: Path, config: dict[str, Any]) -> dict[str, Any]:
    tree: ET.Element = ET.parse(path).getroot()
    components: dict[str, dict[str, str]] = {}
    for comp in tree.findall("./components/comp"):
        ref: str = comp.attrib["ref"]
        if ref in components:
            raise ValueError("Duplicate reference in netlist")
        ####
        components[ref] = {
            "value": comp.findtext("value", ""), "footprint": comp.findtext("footprint", ""),
        }
    ####
    nets: dict[str, list[str]] = {}
    for net in tree.findall("./nets/net"):
        name: str = net.attrib["name"].lstrip("/")
        if name in nets:
            raise ValueError("Duplicate normalized net name")
        ####
        nets[name] = sorted(f"{node.attrib['ref']}.{node.attrib['pin']}" for node in net.findall("node"))
    ####
    if components != config["components"] or nets != config["nets"]:
        raise ValueError(f"Independent netlist contract mismatch: {components=}, {nets=}")
    ####
    return {"components": components, "nets": nets}
####


def svg_files(output: Path, name: str) -> list[Path]:
    files: list[Path] = (
        list((output / "schematic").glob("*.svg"))
        if name == "schematic_svg" else [output / "pcb.svg"]
    )
    if not files or any(not p.is_file() or p.stat().st_size == 0 for p in files):
        raise ValueError("Missing SVG export")
    ####
    for path in files:
        if ET.parse(path).getroot().tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Export is not an SVG document")
        ####
    ####
    return files
####


def execute(argv: list[str], cwd: Path, output: Path, name: str) -> dict[str, Any]:
    record: dict[str, Any] = {"argv": argv, "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            argv, cwd=cwd, text=True, capture_output=True, timeout=180, check=False,
        )
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except (OSError, subprocess.TimeoutExpired) as exc:
        record.update(returncode=127, error=str(exc))
    ####
    (output / f"{name}.command.json").write_text(json.dumps(record, indent=2) + "\n")
    return record
####


def validate(root: Path, output: Path, cli: str) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    checks: dict[str, Any] = {}
    summary: dict[str, Any] = {
        "schema_version": "0.3", "lane": "KICAD_CLI", "not_for_manufacture": True,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "checked_commit": os.environ.get("CHECKED_SHA", "LOCAL_UNBOUND"),
        "pr_head_commit": os.environ.get("PR_HEAD_SHA"), "checks": checks,
    }
    before: dict[str, str] = {}
    try:
        config: dict[str, Any] = json.loads((root / "pilot.json").read_text())
        before = hashes(root)
        required: set[str] = set(config["required_inputs"])
        if set(before) != required or config.get("not_for_manufacture") is not True:
            raise ValueError(f"Input inventory differs; missing={required-set(before)}, extra={set(before)-required}")
        ####
        checks["source_scope"] = {"status": "PASS", "sha256": before}
        executable: str | None = shutil.which(cli)
        if executable is None:
            raise ValueError("KiCad executable is missing")
        ####
        version: dict[str, Any] = execute([executable, "version"], root, output, "version")
        actual: str = str(version.get("stdout", "")).strip()
        if version["returncode"] != 0 or actual != config["kicad_version"]:
            raise ValueError(f"Expected KiCad {config['kicad_version']}; observed {actual!r}")
        ####
        checks["toolchain"] = {"status": "PASS", "version": actual, "image": config["image"]}
        base: Path = root / config["project"]
        commands: dict[str, list[str]] = {
            "erc": ["sch", "erc", "--format", "json", "--severity-all", "--exit-code-violations", "--output", str(output / "erc.json"), str(base.with_suffix(".kicad_sch"))],
            "drc": ["pcb", "drc", "--format", "json", "--severity-all", "--exit-code-violations", "--schematic-parity", "--refill-zones", "--output", str(output / "drc.json"), str(base.with_suffix(".kicad_pcb"))],
            "netlist": ["sch", "export", "netlist", "--format", "kicadxml", "--output", str(output / "netlist.xml"), str(base.with_suffix(".kicad_sch"))],
            "schematic_svg": ["sch", "export", "svg", "--output", str(output / "schematic"), str(base.with_suffix(".kicad_sch"))],
            "pcb_svg": ["pcb", "export", "svg", "--layers", "F.Cu,F.SilkS,Edge.Cuts,Cmts.User", "--output", str(output / "pcb.svg"), str(base.with_suffix(".kicad_pcb"))],
        }
        for name, args in commands.items():
            record: dict[str, Any] = execute([executable, *args], root, output, name)
            checks[name] = {"status": "FAIL", "returncode": record["returncode"]}
            try:
                if record["returncode"] != 0:
                    raise ValueError(f"KiCad command failed with {record['returncode']}")
                ####
                if name in {"erc", "drc"}:
                    count: int = check_report(output / f"{name}.json", name, config)
                    checks[name]["findings"] = count
                    checks[name]["expected_ignored_checks"] = config["expected_ignored_checks"][name]
                    if count:
                        raise ValueError(f"{count} findings, including exclusions")
                    ####
                elif name == "netlist":
                    checks[name]["contract"] = check_netlist(output / "netlist.xml", config)
                    with (output / "bom.csv").open("w", newline="") as stream:
                        writer: Any = csv.writer(stream)
                        writer.writerow(["Reference", "Value", "Footprint", "Disposition"])
                        for ref, item in config["components"].items():
                            writer.writerow([ref, item["value"], item["footprint"], "NOT FOR MANUFACTURE"])
                        ####
                    ####
                else:
                    checks[name]["files"] = [
                        str(p.relative_to(output)) for p in svg_files(output, name)
                    ]
                ####
                checks[name]["status"] = "PASS"
            except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as exc:
                checks[name]["error"] = str(exc)
            ####
        ####
    except (ValueError, OSError, KeyError, TypeError) as exc:
        checks["preflight"] = {"status": "FAIL", "error": str(exc)}
    ####
    try:
        summary["local_only_files"] = [
            str(p.relative_to(root)) for p in sorted((root / "boards").rglob("*"))
            if p.is_file() and local_state(p)
        ]
        after: dict[str, str] = hashes(root)
        checks["source_unchanged"] = {"status": "PASS" if before == after else "FAIL", "sha256_after": after}
    except (OSError, ValueError) as exc:
        checks["source_unchanged"] = {"status": "FAIL", "error": str(exc)}
    ####
    required_checks: set[str] = {"source_scope", "toolchain", "erc", "drc", "netlist", "schematic_svg", "pcb_svg", "source_unchanged"}
    complete: bool = required_checks.issubset(checks)
    summary["status"] = "PASS" if complete and all(c["status"] == "PASS" for c in checks.values()) else "FAIL"
    summary["artifacts_sha256"] = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*")) if p.is_file()
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
####


def main() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cli", default="kicad-cli")
    args: argparse.Namespace = parser.parse_args()
    summary: dict[str, Any] = validate(args.root.resolve(), args.output.resolve(), args.cli)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "PASS" else 1
####


if __name__ == "__main__":
    sys.exit(main())
####
