"""Test the checker itself; these unit tests do not stand in for KiCad execution."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate import check_netlist, check_report, hashes, validate

ROOT: Path = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root: Path = Path(self.temp.name)
    ####

    def report(self, data: Any) -> Path:
        path: Path = self.root / "report.json"
        path.write_text(json.dumps(data))
        return path
    ####

    def fixture(self) -> None:
        shutil.copytree(ROOT / "boards", self.root / "boards")
        shutil.copy2(ROOT / "pilot.json", self.root / "pilot.json")
    ####

    def test_erc_clean(self) -> None:
        data: dict[str, Any] = {"kicad_version": "10.0.5", "sheets": [{"violations": []}]}
        self.assertEqual(check_report(self.report(data), "erc"), 0)
    ####

    def test_erc_all_findings_count(self) -> None:
        data: dict[str, Any] = {"kicad_version": "10.0.5", "sheets": [{"violations": [{"severity": "warning"}, {"excluded": True}]}]}
        self.assertEqual(check_report(self.report(data), "erc"), 2)
    ####

    def test_incomplete_reports_rejected(self) -> None:
        for data in ({}, [], {"kicad_version": "10.0.5"}, {"kicad_version": "10.0.5", "sheets": []}):
            with self.subTest(data=data), self.assertRaises((ValueError, TypeError)):
                check_report(self.report(data), "erc")
            ####
        ####
    ####

    def test_drc_clean_requires_parity(self) -> None:
        data: dict[str, Any] = {"kicad_version": "10.0.5", "violations": [], "unconnected_items": [], "schematic_parity": []}
        self.assertEqual(check_report(self.report(data), "drc"), 0)
        del data["schematic_parity"]
        with self.assertRaises(ValueError):
            check_report(self.report(data), "drc")
        ####
    ####

    def test_drc_counts_every_category(self) -> None:
        data: dict[str, Any] = {"kicad_version": "10.0.5", "violations": [{}], "unconnected_items": [{}], "schematic_parity": [{}]}
        self.assertEqual(check_report(self.report(data), "drc"), 3)
    ####

    def test_empty_netlist_cannot_pass(self) -> None:
        path: Path = self.root / "netlist.xml"
        path.write_text("<export><components/><nets/></export>")
        config: dict[str, Any] = json.loads((ROOT / "pilot.json").read_text())
        with self.assertRaises(ValueError):
            check_netlist(path, config)
        ####
    ####

    def test_fixture_inventory_matches(self) -> None:
        config: dict[str, Any] = json.loads((ROOT / "pilot.json").read_text())
        self.assertEqual(set(hashes(ROOT)), set(config["required_inputs"]))
    ####

    def test_missing_tool_is_failure(self) -> None:
        self.fixture()
        result: dict[str, Any] = validate(self.root, self.root / "out", "intentionally-absent-kicad")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("missing", result["checks"]["preflight"]["error"])
    ####

    def test_missing_dependency_is_failure(self) -> None:
        self.fixture()
        (self.root / "boards/controller/Pilot.kicad_sym").unlink()
        result: dict[str, Any] = validate(self.root, self.root / "out", "intentionally-absent-kicad")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("inventory", result["checks"]["preflight"]["error"])
    ####

    def test_unknown_board_is_failure(self) -> None:
        self.fixture()
        (self.root / "boards/extra").mkdir()
        (self.root / "boards/extra/extra.kicad_pcb").write_text("unknown")
        result: dict[str, Any] = validate(self.root, self.root / "out", "intentionally-absent-kicad")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("extra.kicad_pcb", result["checks"]["preflight"]["error"])
    ####

    def test_no_overwriting_retained_evidence(self) -> None:
        self.fixture()
        (self.root / "out").mkdir()
        with self.assertRaises(FileExistsError):
            validate(self.root, self.root / "out", "intentionally-absent-kicad")
        ####
    ####

    def test_source_hash_detects_mutation(self) -> None:
        self.fixture()
        before: dict[str, str] = hashes(self.root)
        (self.root / "boards/controller/controller.kicad_pro").write_text("{}")
        self.assertNotEqual(before, hashes(self.root))
    ####
####


if __name__ == "__main__":
    unittest.main()
####
