"""Typed template bootstrap and migration-plan tests."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.hwrepo.contracts import read_model, write_model
from tools.hwrepo.models import TemplateAdoptionRecord, TemplateUpgrade, TemplateUpgradesCatalog
from tools.hwrepo.template import bootstrap, plan_upgrade, preflight

ROOT = Path(__file__).resolve().parents[1]


class TemplateToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="template-tools-")
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / "source-template"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "build", ".evidence", "__pycache__"),
        )

    def test_preflight_accepts_the_declared_template_contract(self) -> None:
        report = preflight(self.root)
        self.assertEqual(report.status, "PASS", report.issues)
        self.assertEqual(report.template_version, "0.1.0")
        self.assertFalse(report.build_authorized)

    def test_preflight_rejects_a_missing_required_template_path(self) -> None:
        (self.root / "tools/ci.py").unlink()
        report = preflight(self.root)
        self.assertEqual(report.status, "FAIL")
        self.assertIn("TEMPLATE_REQUIRED_PATH", {issue.code for issue in report.issues})

    def test_bootstrap_creates_a_non_git_copy_with_pending_adoption_record(self) -> None:
        destination = self.parent / "adopting-repository"
        with patch("tools.hwrepo.template.working_tree_is_clean", return_value=True):
            report = bootstrap(self.root, destination, "example-board")
        self.assertEqual(report.status, "PASS", report.issues)
        self.assertFalse((destination / ".git").exists())
        adoption = read_model(destination / "template-adoption.json", TemplateAdoptionRecord)
        self.assertEqual(adoption.project_id, "example-board")
        self.assertEqual(adoption.status, "needs_adoption")

    def test_upgrade_plan_requires_one_forward_catalog_path(self) -> None:
        catalog_path = self.root / "templates/template-upgrades.json"
        catalog = read_model(catalog_path, TemplateUpgradesCatalog)
        write_model(
            catalog_path,
            catalog.model_copy(
                update={
                    "upgrades": (
                        TemplateUpgrade(
                            id="template-0.1-to-0.2",
                            from_version="0.1.0",
                            to_version="0.2.0",
                            breaking=True,
                            steps=(
                                "Review the documented migration before changing source.",
                                "Run static and native checks after the reviewed update.",
                            ),
                        ),
                    )
                }
            ),
        )
        report = plan_upgrade(self.root, "0.2.0")
        self.assertEqual(report.status, "PASS", report.issues)
        self.assertEqual([upgrade.id for upgrade in report.upgrades], ["template-0.1-to-0.2"])

    def test_upgrade_plan_rejects_missing_forward_path(self) -> None:
        report = plan_upgrade(self.root, "0.2.0")
        self.assertEqual(report.status, "FAIL")
        self.assertIn("TEMPLATE_UPGRADE_PATH", {issue.code for issue in report.issues})


if __name__ == "__main__":
    unittest.main()
