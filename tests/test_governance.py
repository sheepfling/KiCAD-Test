"""Tests for the repository-wide project and catalog lint."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tests.support import reference_root
from tools.check_toolchain import assessment, toolchain
from tools.ci_matrix import build_matrix
from tools.hwrepo.contracts import read_model, write_model
from tools.hwrepo.models import (
    ComponentIdentity,
    GovernanceRecord,
    PartsCatalog,
    ProjectManifest,
    TeamPolicy,
)
from tools.hwrepo.selection import ProjectSelector, resolve_project_ids
from tools.lint_registry import lint, lint_governance_record

ROOT: Path = reference_root()


class GovernanceLintTests(unittest.TestCase):
    def test_two_person_policy_requires_independent_review_and_can_be_stricter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "catalog").mkdir()
            policy = TeamPolicy(rationale="Synthetic two-person unit-test policy")
            write_model(root / "catalog/team-policy.json", policy)
            record = GovernanceRecord(branch="main", required_status_checks=("Template acceptance",),
                authors=("author-A",), reviewers=("reviewer-B",), integrators=("author-A",),
                release_authorities=("author-A",), branch_protection_evidence=("fixture-record",),
                branch_protection_verified_at="2026-09-08")
            write_model(root / "governance.json", record)
            issues: list[str] = []
            lint_governance_record(root, "governance.json", "board", issues)
            self.assertEqual(issues, [])
            write_model(root / "governance.json", record.model_copy(update={"reviewers": ("AUTHOR-a",)}))
            lint_governance_record(root, "governance.json", "board", issues)
            self.assertTrue(any("independent" in issue for issue in issues))
            write_model(root / "governance.json", record)
            write_model(root / "catalog/team-policy.json", policy.model_copy(update={"minimum_actors": 3}))
            issues.clear()
            lint_governance_record(root, "governance.json", "board", issues)
            self.assertTrue(any("3 distinct" in issue for issue in issues))

    def test_all_declared_projects_pass_static_lint(self) -> None:
        result = lint(ROOT)
        self.assertEqual(result.status, "PASS", result.issues)
        self.assertEqual(
            result.projects,
            ('arduino-uno-status-led', 'controller', 'passive-signal-reference', 'raspberry-pi-status-led', 'status-indicator-harness-interface', 'status-indicator-wiring'),
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
            ('arduino-uno-status-led', 'raspberry-pi-status-led', 'status-indicator-harness-interface', 'status-indicator-wiring'),
        )
        self.assertEqual(
            resolve_project_ids(ROOT, ProjectSelector(excluded_tags=("legacy",))),
            ('arduino-uno-status-led', 'passive-signal-reference', 'raspberry-pi-status-led', 'status-indicator-harness-interface', 'status-indicator-wiring'),
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
            path = staged / "examples/projects/controller/project.json"
            manifest = read_model(path, ProjectManifest)
            write_model(path, manifest.model_copy(update={"tags": ("legacy", "LEGACY")}))
            self.assertIn("project controller: duplicate metadata tag", lint(staged).issues)

    def test_ci_matrix_uses_each_project_pin(self) -> None:
        matrix = build_matrix(ROOT)
        self.assertEqual(
            [row.project for row in matrix.include],
            ['arduino-uno-status-led', 'controller', 'passive-signal-reference', 'raspberry-pi-status-led', 'status-indicator-harness-interface', 'status-indicator-wiring'],
        )
        expected_versions = {
            "controller": "10.0.0",
            "arduino-uno-status-led": "10.0.5",
            "raspberry-pi-status-led": "10.0.5",
            "status-indicator-wiring": "10.0.5",
            "passive-signal-reference": "10.0.5",
            "status-indicator-harness-interface": "10.0.5",
        }
        for row in matrix.include:
            self.assertEqual(row.kicad_version, expected_versions[row.project])
            self.assertIn("@sha256:", row.image)

    def test_toolchain_catalog_is_the_single_source_of_version_identity(self) -> None:
        baseline = toolchain(ROOT, "kicad-10.0.0")
        self.assertEqual(baseline.kicad_version, "10.0.0")
        self.assertEqual(assessment(baseline, "10.0.0").status, "PASS")
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
            provenance = staged / "examples/libraries/status-led/PROVENANCE.md"
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
            path = staged / "examples/projects/controller/project.json"
            manifest = read_model(path, ProjectManifest)
            write_model(path, manifest.model_copy(update={
                "status": "engineering", "assurance_profile": "production",
                "component_identity": ComponentIdentity(required=False, part_ids=()),
            }))
            issues = lint(staged, ["controller"]).issues
            self.assertTrue(any("production profile cannot disable ERC or DRC checks" in issue for issue in issues))
            self.assertTrue(any("production profile must require component identity" in issue for issue in issues))
            self.assertTrue(any("mechanical_handoff" in issue for issue in issues))
            self.assertTrue(any("governance" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
