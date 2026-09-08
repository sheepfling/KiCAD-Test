"""Unit tests for the single CI entry point that GitHub invokes."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools.ci import main, project_static_pipeline, run_command, static_pipeline
from tools.hwrepo.models import CommandEvidence

ROOT = Path(__file__).resolve().parents[1]


def evidence(returncode: int) -> CommandEvidence:
    return CommandEvidence(
        argv=("quality-tool",),
        started_utc=datetime.now(timezone.utc).isoformat(),
        returncode=returncode,
    )


class CiDriverTests(unittest.TestCase):
    def test_missing_quality_tool_is_a_typed_failure(self) -> None:
        result = run_command(ROOT, "intentionally-absent-quality-tool")
        self.assertEqual(result.returncode, 127)
        self.assertIsNotNone(result.error)

    def test_static_pipeline_requires_every_quality_command(self) -> None:
        with patch("tools.ci.run_command", side_effect=(evidence(0), evidence(0), evidence(1))):
            result = static_pipeline(ROOT, None)
        self.assertEqual(result.registry.status, "PASS")
        self.assertEqual(result.documentation.status, "PASS")
        self.assertEqual(result.unit_tests.returncode, 1)
        self.assertEqual(result.status, "FAIL")

    def test_project_pipeline_skips_repository_wide_python_quality_commands(self) -> None:
        with patch("tools.ci.run_command") as command:
            result = project_static_pipeline(ROOT, ("controller",))
        command.assert_not_called()
        self.assertEqual(result.scope, "project_static")
        self.assertEqual(result.projects, ("controller",))
        self.assertEqual(result.status, "PASS")

    def test_module_entrypoint_scopes_a_local_project_check(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "tools.ci", "--project", "controller"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["scope"], "project_static")
        self.assertNotIn("ruff", report)

    def test_module_entrypoint_selects_projects_by_metadata_tag(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "tools.ci", "--tag", "status-led"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            report["projects"],
            [
                "arduino-uno-status-led",
                "raspberry-pi-status-led",
                "status-indicator-wiring",
                "status-indicator-harness-interface",
            ],
        )

    def test_matrix_mode_is_one_json_line_for_github_output(self) -> None:
        with (
            patch.object(sys, "argv", ["ci.py", "--matrix"]),
            patch("sys.stdout", new_callable=StringIO) as output,
        ):
            self.assertEqual(main(), 0)
        self.assertEqual(len(output.getvalue().splitlines()), 1)

    def test_module_entrypoint_resolves_the_package_without_path_injection(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "tools.ci", "--matrix"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("include", json.loads(result.stdout))

    def test_metrics_mode_uses_the_central_ci_driver(self) -> None:
        with (
            patch.object(sys, "argv", ["ci.py", "--metrics"]),
            patch("sys.stdout", new_callable=StringIO) as output,
        ):
            self.assertEqual(main(), 0)
        self.assertEqual(json.loads(output.getvalue())["lane"], "TEMPLATE_METRICS")

    def test_workflow_delegates_policy_work_to_the_driver(self) -> None:
        workflow = (ROOT / ".github/workflows/kicad-template.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotRegex(
            workflow,
            r"\bpython(?:3)?\s+(?!-m\b)[^\n]*tools[/\\][^\n]*\.py",
        )
        for command in ("tools/ci_matrix.py", "tools/check_all.py", "tools/fault_probe.py"):
            self.assertNotIn(command, workflow)
        self.assertNotIn("tools/ci.py", workflow)
        for mode in ("tools.ci --matrix", "tools.ci --kicad", "tools.ci --fault-probes"):
            self.assertIn(mode, workflow)


if __name__ == "__main__":
    unittest.main()
