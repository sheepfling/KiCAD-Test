"""Run real KiCad against disposable broken fixture copies; never edit tracked source."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from validate import validate


def probe(root: Path, output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []
    for name in ("malformed_pcb", "missing_library", "erc_open_pin", "drc_unrouted", "parity_value", "missing_tool", "unknown_board"):
        with tempfile.TemporaryDirectory(prefix="kicad-negative-") as temp:
            copy: Path = Path(temp)
            shutil.copytree(root / "boards", copy / "boards")
            shutil.copy2(root / "pilot.json", copy / "pilot.json")
            board: Path = copy / "boards/controller/controller.kicad_pcb"
            sch: Path = copy / "boards/controller/controller.kicad_sch"
            cli: str = "kicad-cli"
            expected: str = "preflight"
            if name == "malformed_pcb":
                board.write_text("This is not a KiCad PCB.\n")
                expected = "drc"
            elif name == "missing_library":
                (copy / "boards/controller/Pilot.kicad_sym").unlink()
            elif name == "erc_open_pin":
                text: str = sch.read_text()
                if "(xy 76.2 71.12)" not in text:
                    raise ValueError("Open-pin mutation anchor missing")
                ####
                sch.write_text(text.replace("(xy 76.2 71.12)", "(xy 78.74 71.12)", 1))
                expected = "erc"
            elif name == "drc_unrouted":
                text, count = re.subn(r'  \(segment \(start 100 100\)[^\n]*\)\n', "", board.read_text(), count=1)
                if count != 1:
                    raise ValueError("Track mutation anchor missing")
                ####
                board.write_text(text)
                expected = "drc"
            elif name == "parity_value":
                text = board.read_text()
                if '(property "Value" "1k"' not in text:
                    raise ValueError("Parity mutation anchor missing")
                ####
                board.write_text(text.replace('(property "Value" "1k"', '(property "Value" "999k"', 1))
                expected = "drc"
            elif name == "missing_tool":
                cli = "intentionally-missing-kicad-pilot-executable"
            else:
                (copy / "boards/unregistered").mkdir()
                (copy / "boards/unregistered/ghost.kicad_pcb").write_text("undeclared board\n")
            ####
            report: dict[str, Any] = validate(copy, output / name, cli)
            passed: bool = report["status"] == "FAIL" and report["checks"].get(expected, {}).get("status") == "FAIL"
            if name in {"erc_open_pin", "drc_unrouted", "parity_value"}:
                passed = passed and report["checks"][expected].get("returncode") == 5
            ####
            if name == "parity_value" and (output / name / "drc.json").exists():
                data: dict[str, Any] = json.loads((output / name / "drc.json").read_text())
                passed = passed and bool(data.get("schematic_parity"))
            ####
            rows.append({"id": name, "status": "PASS" if passed else "FAIL", "expected_failing_check": expected, "observed": report["checks"].get(expected)})
        ####
    ####
    result: dict[str, Any] = {"lane": "KICAD_CLI", "not_for_manufacture": True, "cases": rows, "status": "PASS" if all(r["status"] == "PASS" for r in rows) else "FAIL"}
    (output / "fault-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
####


def main() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args: argparse.Namespace = parser.parse_args()
    result: dict[str, Any] = probe(Path(__file__).resolve().parents[1], args.output.resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1
####


if __name__ == "__main__":
    sys.exit(main())
####
