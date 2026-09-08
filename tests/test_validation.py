"""Test the checker itself; these unit tests do not stand in for KiCad execution."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.check_all import check_all
from tools.hwrepo.contracts import read_model
from tools.hwrepo.models import PcbValidationContract, ProjectConfig
from tools.validate import check_netlist, check_report, hashes, validate

ROOT: Path = Path(__file__).resolve().parents[1]
JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root: Path = Path(self.temp.name)
        self.config = read_model(ROOT / "examples/configs/controller.json", ProjectConfig)
    ####

    def report(self, data: JsonValue) -> Path:
        path: Path = self.root / "report.json"
        path.write_text(json.dumps(data))
        return path
    ####

    def fixture(self) -> None:
        for directory in (
            "catalog",
            "examples",
            "docs",
        ):
            shutil.copytree(ROOT / directory, self.root / directory)
    ####

    def test_erc_clean(self) -> None:
        data: JsonObject = {"kicad_version": "10.0.0", "sheets": [{"violations": []}]}
        self.assertEqual(check_report(self.report(data), "erc"), 0)
    ####

    def test_erc_all_findings_count(self) -> None:
        data: JsonObject = {"kicad_version": "10.0.0", "sheets": [{"violations": [{"severity": "warning"}, {"excluded": True}]}]}
        self.assertEqual(check_report(self.report(data), "erc"), 2)
    ####

    def test_incomplete_reports_rejected(self) -> None:
        for data in ({}, [], {"kicad_version": "10.0.0"}, {"kicad_version": "10.0.0", "sheets": []}):
            with self.subTest(data=data), self.assertRaises((ValueError, TypeError)):
                check_report(self.report(data), "erc")
            ####
        ####
    ####

    def test_drc_clean_requires_parity(self) -> None:
        data: JsonObject = {"kicad_version": "10.0.0", "violations": [], "unconnected_items": [], "schematic_parity": []}
        self.assertEqual(check_report(self.report(data), "drc"), 0)
        del data["schematic_parity"]
        with self.assertRaises((TypeError, ValueError)):
            check_report(self.report(data), "drc")
        ####
    ####

    def test_drc_counts_every_category(self) -> None:
        data: JsonObject = {"kicad_version": "10.0.0", "violations": [{}], "unconnected_items": [{}], "schematic_parity": [{}]}
        self.assertEqual(check_report(self.report(data), "drc"), 3)
    ####

    def test_empty_netlist_cannot_pass(self) -> None:
        path: Path = self.root / "netlist.xml"
        path.write_text("<export><components/><nets/></export>")
        config = read_model(ROOT / "examples/configs/controller.json", ProjectConfig)
        self.assertIsInstance(config.validation, PcbValidationContract)
        with self.assertRaises(ValueError):
            check_netlist(path, config.validation)
        ####
    ####

    def test_fixture_inventory_matches(self) -> None:
        config = read_model(ROOT / "examples/configs/controller.json", ProjectConfig)
        self.assertEqual(set(hashes(ROOT, config.source_roots)), set(config.required_inputs))
    ####

    def test_missing_tool_is_failure(self) -> None:
        self.fixture()
        result = validate(self.root, self.root / "out", "intentionally-absent-kicad")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("missing", result.checks["preflight"].error or "")
    ####

    def test_missing_dependency_is_failure(self) -> None:
        self.fixture()
        (self.root / "examples/projects/pcb/controller/Pilot.kicad_sym").unlink()
        result = validate(self.root, self.root / "out", "intentionally-absent-kicad")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("inventory", result.checks["preflight"].error or "")
    ####

    def test_unknown_board_is_failure(self) -> None:
        self.fixture()
        (self.root / "examples/projects/pcb/controller/extra.kicad_pcb").write_text("unknown")
        result = validate(self.root, self.root / "out", "intentionally-absent-kicad")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("extra.kicad_pcb", result.checks["preflight"].error or "")
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
        before = hashes(self.root, self.config.source_roots)
        (self.root / "examples/projects/pcb/controller/controller.kicad_pro").write_text("{}")
        self.assertNotEqual(before, hashes(self.root, self.config.source_roots))
    ####

    def test_all_project_check_reports_missing_tool(self) -> None:
        self.fixture()
        result = check_all(self.root, self.root / "all-out", "intentionally-absent-kicad")
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.governance.status, "PASS")
        self.assertEqual(result.projects[0].id, "controller")
        self.assertEqual(result.projects[0].status, "FAIL")
    ####

    def test_declared_shared_library_root_is_hashed(self) -> None:
        self.fixture()
        library: Path = self.root / "libraries/shared"
        library.mkdir(parents=True)
        source: Path = library / "Example.kicad_sym"
        source.write_text("(kicad_symbol_lib (version 20231120) (generator test))")
        scoped = hashes(self.root, ["examples/projects/pcb", "libraries/shared"])
        self.assertIn("libraries/shared/Example.kicad_sym", scoped)
        self.assertNotEqual(hashes(self.root, self.config.source_roots), scoped)
    ####
if __name__ == "__main__":
    unittest.main()
