"""Release-readiness tests; all release checks remain read-only and non-authorizing."""
from __future__ import annotations

import hashlib
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tests.support import reference_root
from tools.hwrepo.contracts import read_model, write_model
from tools.hwrepo.models import (
    DeviationStatus,
    InterfacesCatalog,
    LibrariesCatalog,
    ProductRecord,
    ReleaseArtifact,
    ReleaseArtifactKind,
    ReleaseClass,
    ReleaseDeviation,
    ReleaseInterface,
    ReleaseLibrary,
    ReleaseManifest,
    ReleaseStatus,
    ReleaseVariant,
)
from tools.hwrepo.release import check

ROOT = reference_root()
COMMIT = "a" * 40


class ReleaseReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="release-readiness-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "template"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "build", ".evidence", "__pycache__"),
        )
        product_path = self.root / "examples/products/status-indicator-system/product.json"
        product = read_model(product_path, ProductRecord)
        write_model(product_path, product.model_copy(update={"maturity": "engineering_review"}))

    def manifest(self, **updates: object) -> ReleaseManifest:
        artifact_path = self.root / "docs/workflow/PRODUCT_WORKFLOW.md"
        base = ReleaseManifest(
            release_id="status-review-A",
            release_class=ReleaseClass.ENGINEERING_REVIEW,
            status=ReleaseStatus.CANDIDATE,
            source_commit=COMMIT,
            toolchain_id="kicad-10.0.5",
            variants=(
                ReleaseVariant(
                    product="status-indicator-system",
                    product_revision="A",
                    variant="STANDARD",
                    variant_revision="A",
                ),
            ),
            libraries=tuple(
                ReleaseLibrary(
                    id=library.id,
                    version=library.version,
                    provenance_sha256=library.provenance_sha256,
                    licensing_sha256=library.licensing_sha256,
                )
                for library in read_model(
                    self.root / "catalog/libraries.json", LibrariesCatalog
                ).libraries
            ),
            interfaces=tuple(
                ReleaseInterface(id=interface.id, revision=interface.revision)
                for interface in read_model(
                    self.root / "catalog/interfaces.json", InterfacesCatalog
                ).interfaces
            ),
            checks={
                "repository": "PASS",
                "product_model": "PASS",
                "generation_drift": "PASS",
                "harness": "PASS",
                "kicad": "PASS",
            },
            artifacts=(
                ReleaseArtifact(
                    id="review-workflow-record",
                    kind=ReleaseArtifactKind.REVIEW_RECORD,
                    path="docs/workflow/PRODUCT_WORKFLOW.md",
                    sha256=hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
                    intended_use="Independent engineering review workflow record.",
                ),
            ),
        )
        return base.model_copy(update=updates)

    def git(self, _root: Path, *args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return COMMIT
        if args == ("status", "--porcelain=v1", "--untracked-files=all"):
            return ""
        raise AssertionError(f"Unexpected Git query: {args}")

    def test_self_declared_passing_checks_cannot_supply_release_evidence(self) -> None:
        with patch("tools.hwrepo.release.git", side_effect=self.git):
            report = check(self.root, self.manifest())
        self.assertEqual(report.status, "FAIL", report.issues)
        self.assertIn("RELEASE_EVIDENCE", {finding.code for finding in report.issues})
        self.assertFalse(report.build_authorized)

    def test_commit_mismatch_and_open_deviation_fail(self) -> None:
        deviation = ReleaseDeviation(
            id="DV-1",
            scope=("training-uno-indicator",),
            owner="Configuration manager",
            reason="Demonstrates a blocked release deviation.",
            status=DeviationStatus.OPEN,
            expires=date(2026, 9, 8),
            evidence=(),
        )
        manifest = self.manifest(source_commit="b" * 40, deviations=(deviation,))
        with patch("tools.hwrepo.release.git", side_effect=self.git):
            report = check(self.root, manifest, today=date(2026, 9, 7))
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(
            {finding.code for finding in report.issues},
            {"RELEASE_COMMIT", "DEVIATION_STATUS", "DEVIATION_EVIDENCE", "RELEASE_EVIDENCE"},
        )

    def test_prototype_rejects_candidate_training_level_controls(self) -> None:
        manifest = self.manifest(release_class=ReleaseClass.PROTOTYPE)
        with patch("tools.hwrepo.release.git", side_effect=self.git):
            report = check(self.root, manifest)
        self.assertEqual(report.status, "FAIL")
        self.assertTrue(
            {"RELEASE_MATURITY", "RELEASE_STATUS", "RELEASE_APPROVAL", "RELEASE_TAG"}
            .issubset({finding.code for finding in report.issues})
        )

    def test_release_class_enforces_the_catalogued_assurance_floor(self) -> None:
        product_path = self.root / "examples/products/status-indicator-system/product.json"
        product = read_model(product_path, ProductRecord)
        write_model(product_path, product.model_copy(update={"maturity": "prototype"}))
        manifest = self.manifest(release_class=ReleaseClass.PROTOTYPE)
        with patch("tools.hwrepo.release.git", side_effect=self.git):
            report = check(self.root, manifest)
        self.assertIn("RELEASE_ASSURANCE", {finding.code for finding in report.issues})

    def test_revision_and_library_binding_cannot_be_stale(self) -> None:
        base = self.manifest()
        variant = base.variants[0].model_copy(update={"variant_revision": "B"})
        library = base.libraries[0].model_copy(update={"version": "0.1.1"})
        manifest = base.model_copy(update={"variants": (variant,), "libraries": (library,)})
        with patch("tools.hwrepo.release.git", side_effect=self.git):
            report = check(self.root, manifest)
        self.assertEqual(report.status, "FAIL")
        self.assertTrue(
            {"RELEASE_VARIANT_REVISION", "RELEASE_LIBRARY"}.issubset(
                {finding.code for finding in report.issues}
            )
        )


if __name__ == "__main__":
    unittest.main()
