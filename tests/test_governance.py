"""Tests for the repository-wide project and catalog lint."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ci_matrix import build_matrix
from lint_registry import lint

ROOT: Path = Path(__file__).resolve().parents[1]


class GovernanceLintTests(unittest.TestCase):
    def test_all_declared_projects_pass_static_lint(self) -> None:
        result: dict[str, Any] = lint(ROOT)
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["projects"], ["controller"])

    def test_individual_project_lint_passes(self) -> None:
        result: dict[str, Any] = lint(ROOT, ["controller"])
        self.assertEqual(result["status"], "PASS", result["issues"])

    def test_unknown_project_fails_closed(self) -> None:
        result: dict[str, Any] = lint(ROOT, ["not-a-project"])
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("unknown project" in issue for issue in result["issues"]))

    def test_ci_matrix_uses_each_project_pin(self) -> None:
        matrix: dict[str, list[dict[str, str]]] = build_matrix(ROOT)
        self.assertEqual(matrix["include"][0]["project"], "controller")
        self.assertEqual(matrix["include"][0]["kicad_version"], "10.0.5")
        self.assertIn("@sha256:", matrix["include"][0]["image"])


if __name__ == "__main__":
    unittest.main()
