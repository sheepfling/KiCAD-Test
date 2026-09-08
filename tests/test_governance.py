"""Tests for the repository-wide project and catalog lint."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.check_toolchain import assessment, toolchain
from tools.ci_matrix import build_matrix
from tools.hwrepo.contracts import read_model, write_model
from tools.hwrepo.models import ComponentIdentity, PartsCatalog, ProjectConfig, ProjectRegistry
from tools.hwrepo.selection import ProjectSelector, resolve_project_ids
from tools.lint_registry import lint

ROOT: Path = Path(__file__).resolve().parents[1]


class GovernanceLintTests(unittest.TestCase):
    def test_all_declared_projects_pass_static_lint(self) -> None:
        result = lint(ROOT)
        self.assertEqual(result.status, "PASS", result.issues)
        self.assertEqual(
            result.projects,
            (
                "controller",
                "arduino-uno-status-led",
                "raspberry-pi-status-led",
                "status-indicator-wiring",
                "passive-signal-reference",
                "status-indicator-harness-interface",
            ),
        )

    def test_individual_project_lint_passes(self) -> None:
        result = lint(ROOT, ["controller"])
        self.assertEqual(result.status, "PASS", result.issues)

    def test_project_metadata_selectors_include_and_exclude_tags(self) -> None:
        self.assertEqual(
            resolve_project_ids(ROOT, ProjectSelector(tags=("legacy",))),
            ("controller",),
        )
        self.assertEqual(
            resolve_project_ids(ROOT, ProjectSelector(tags=("status-led",))),
            (
                "arduino-uno-status-led",
                "raspberry-pi-status-led",
                "status-indicator-wiring",
                "status-indicator-harness-interface",
            ),
        )
        self.assertEqual(
            resolve_project_ids(ROOT, ProjectSelector(excluded_tags=("legacy",))),
            (
                "arduino-uno-status-led",
                "raspberry-pi-status-led",
                "status-indicator-wiring",
                "passive-signal-reference",
                "status-indicator-harness-interface",
            ),
        )
        with self.assertRaisesRegex(ValueError, "No projects matched"):
            resolve_project_ids(ROOT, ProjectSelector(tags=("absent",)))

    def test_ci_matrix_can_be_limited_to_a_tag_selected_project(self) -> None:
        matrix = build_matrix(ROOT, ("controller",))
        self.assertEqual([entry.project for entry in matrix.include], ["controller"])

    def test_unknown_project_fails_closed(self) -> None:
        result = lint(ROOT, ["not-a-project"])
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(any("unknown project" in issue for issue in result.issues))

    def test_duplicate_project_tag_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / "template"
            shutil.copytree(
                ROOT,
                staged,
                ignore=shutil.ignore_patterns(".git", "build", ".evidence", "__pycache__"),
            )
            registry_path = staged / "catalog/projects.json"
            registry = read_model(registry_path, ProjectRegistry)
            duplicate_tagged = registry.projects[0].model_copy(
                update={"tags": ("legacy", "LEGACY")}
            )
            write_model(
                registry_path,
                registry.model_copy(
                    update={"projects": (duplicate_tagged, *registry.projects[1:])}
                ),
            )
            self.assertIn("project controller: duplicate metadata tag", lint(staged).issues)

    def test_ci_matrix_uses_each_project_pin(self) -> None:
        matrix = build_matrix(ROOT)
        self.assertEqual(
            [row.project for row in matrix.include],
            [
                "controller",
                "arduino-uno-status-led",
                "raspberry-pi-status-led",
                "status-indicator-wiring",
                "passive-signal-reference",
                "status-indicator-harness-interface",
            ],
        )
        for row in matrix.include:
            self.assertEqual(row.kicad_version, "10.0.5")
            self.assertIn("@sha256:", row.image)

    def test_toolchain_catalog_is_the_single_source_of_version_identity(self) -> None:
        record = toolchain(ROOT, "kicad-10.0.5")
        self.assertEqual(record.kicad_version, "10.0.5")
        self.assertEqual(assessment(record, "10.0.5").status, "PASS")
        self.assertEqual(assessment(record, "10.0.6").status, "FAIL")

    def test_library_provenance_or_licensing_change_requires_catalog_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / "template"
            shutil.copytree(
                ROOT,
                staged,
                ignore=shutil.ignore_patterns(".git", "build", ".evidence", "__pycache__"),
            )
            provenance = staged / "libraries/status-led/PROVENANCE.md"
            provenance.write_text(
                provenance.read_text(encoding="utf-8") + "\nUnexpected change.\n",
                encoding="utf-8",
            )
            issues = lint(staged).issues
            self.assertIn(
                "library library-status-led-training: provenance record hash does not match",
                issues,
            )

    def test_part_alternate_must_be_a_distinct_controlled_part(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / "template"
            shutil.copytree(
                ROOT,
                staged,
                ignore=shutil.ignore_patterns(".git", "build", ".evidence", "__pycache__"),
            )
            catalog_path = staged / "catalog/parts.json"
            catalog = read_model(catalog_path, PartsCatalog)
            first = catalog.parts[0].model_copy(
                update={"approved_alternates": (catalog.parts[0].id,)}
            )
            write_model(catalog_path, catalog.model_copy(update={"parts": (first, *catalog.parts[1:])}))
            issues = lint(staged).issues
            self.assertIn(
                f"part {first.id}: unknown or self approved alternate {first.id}",
                issues,
            )

    def test_production_profile_fails_closed_without_identity_or_governance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            staged: Path = Path(temporary) / "template"
            shutil.copytree(ROOT, staged, ignore=shutil.ignore_patterns(".git", "build", ".evidence", "__pycache__"))
            registry_path: Path = staged / "catalog/projects.json"
            registry = read_model(registry_path, ProjectRegistry)
            project = registry.projects[0].model_copy(
                update={
                    "status": "engineering",
                    "assurance_profile": "production",
                    "component_identity": ComponentIdentity(required=False, part_ids=()),
                }
            )
            write_model(
                registry_path,
                registry.model_copy(update={"projects": (project, *registry.projects[1:])}),
            )
            config_path: Path = staged / "pilot.json"
            config = read_model(config_path, ProjectConfig)
            write_model(
                config_path,
                config.model_copy(
                    update={"assurance_profile": "production", "not_for_manufacture": False}
                ),
            )
            issues = lint(staged, ["controller"]).issues
            self.assertTrue(any("production profile cannot disable ERC or DRC checks" in issue for issue in issues))
            self.assertTrue(any("production profile must require component identity" in issue for issue in issues))
            self.assertTrue(any("mechanical_handoff" in issue for issue in issues))
            self.assertTrue(any("governance" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
