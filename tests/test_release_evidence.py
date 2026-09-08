"""Real Git/package lifecycle tests using explicitly synthetic check reports.

The hosted native lane separately prepares and restores a package from real KiCad.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path

from tests.support import initialize_git, reference_root
from tools.hwrepo.contracts import read_model, write_model
from tools.hwrepo.discovery import load_config
from tools.hwrepo.documentation import check as check_docs
from tools.hwrepo.evidence import digest, source_state, verify_native
from tools.hwrepo.models import (
    CheckEvidence,
    CommandEvidence,
    DeviationStatus,
    GenerationReport,
    ProjectTestsReport,
    ReleaseArtifact,
    ReleaseArtifactKind,
    ReleaseClass,
    ReleaseDeviation,
    ReleaseEvidence,
    ReleaseManifest,
    ReleaseStatus,
    StaticPipelineReport,
    ValidationSummary,
)
from tools.hwrepo.packaging import package, restore, verify
from tools.hwrepo.product import check as check_product
from tools.hwrepo.release import check
from tools.hwrepo.releasing import reference
from tools.hwrepo.repository import check_repository
from tools.lint_registry import lint


class ReleaseEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="kicad-release-test-")
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve()
        self.root = self.parent / "source"
        shutil.copytree(reference_root(), self.root, ignore=shutil.ignore_patterns(".git"))
        initialize_git(self.root)
        self.git("-c", "user.name=Scaffold test fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Synthetic release test source")
        self.project_id = "passive-signal-reference"
        self.config = load_config(self.root, f"examples/projects/{self.project_id}/project.json")
        self.source = source_state(self.root)
        self.assertTrue(self.source.clean)
        self.directory = self.root / "build/releases/test"
        self.directory.mkdir(parents=True)
        command = CommandEvidence(argv=("synthetic-unit-test-evidence",),
                                  started_utc="2026-01-01T00:00:00Z", returncode=0)
        portable = StaticPipelineReport(status="PASS", source=self.source,
                    registry=lint(self.root), repository=check_repository(self.root),
                    documentation=check_docs(self.root), product=check_product(self.root),
                    generation=GenerationReport(status="PASS", issues=()),
                    ruff=command, pyright=command, unit_tests=command,
                    project_tests=ProjectTestsReport(status="PASS", commands={}))
        write_model(self.directory / "portable.json", portable)
        native = self.directory / "native"
        native.mkdir()
        (native / "schematic").mkdir()
        (native / "schematic/sheet.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (native / "erc.json").write_text(json.dumps({
            "$schema": "https://schemas.kicad.org/erc.v1.json", "kicad_version": "10.0.5",
            "included_severities": ["error", "warning", "exclusion"],
            "ignored_checks": [{"key": name} for name in self.config.validation.expected_ignored_checks.erc],
            "sheets": [{"violations": []}],
        }), encoding="utf-8")
        for name in ("version", "erc", "schematic_svg"):
            write_model(native / f"{name}.command.json", command)
        hashes = {name: self.source.files_sha256[name] for name in self.config.required_inputs}
        checks = {name: CheckEvidence(status="PASS") for name in (
            "governance", "repository", "product_policy", "erc", "schematic_svg")}
        checks.update({"source_scope": CheckEvidence(status="PASS", source_hashes=hashes),
                       "source_unchanged": CheckEvidence(status="PASS", source_hashes=hashes),
                       "toolchain": CheckEvidence(status="PASS", observed_version="10.0.5", image=self.config.image)})
        self.native_path = native / "summary.json"
        write_model(self.native_path, ValidationSummary(timestamp_utc="2026-01-01T00:00:00Z",
                    source=self.source, checked_commit=self.source.commit or "", project_id=self.project_id,
                    project_kind=self.config.kind, assurance_profile="training", not_for_manufacture=True,
                    checks=checks, status="PASS", artifacts_sha256={
                        path.relative_to(native).as_posix(): digest(path) for path in native.rglob("*") if path.is_file()}))
        review = self.directory / "review.txt"
        review.write_text("Synthetic unit-test review record, not hardware approval.", encoding="utf-8")
        self.manifest = ReleaseManifest(release_id="test", release_class=ReleaseClass.ENGINEERING_REVIEW,
            status=ReleaseStatus.CANDIDATE, source_commit=self.source.commit or "", toolchain_id="kicad-10.0.5",
            projects=(self.project_id,), libraries=(), interfaces=(),
            evidence=ReleaseEvidence(portable=reference(self.root, self.directory / "portable.json"),
                                     native={self.project_id: reference(self.root, self.native_path)}),
            artifacts=(ReleaseArtifact(id="review", kind=ReleaseArtifactKind.REVIEW_RECORD,
                       path=review.relative_to(self.root).as_posix(), sha256=digest(review),
                       intended_use="Synthetic unit-test record"),))
        self.manifest_name = "build/releases/test/manifest.json"
        write_model(self.root / self.manifest_name, self.manifest)

    def git(self, *args: str) -> str:
        return subprocess.run(("git", "-C", str(self.root), *args), check=True, capture_output=True,
                              text=True).stdout.strip()

    def test_standalone_release_restores_exact_commit_and_verified_evidence(self) -> None:
        self.assertEqual(check(self.root, self.manifest).status, "PASS", check(self.root, self.manifest).issues)
        archive = self.parent / "release.zip"
        self.assertEqual(package(self.root, self.manifest_name, archive).status, "PASS")
        destination = self.parent / "restored"
        self.assertEqual(restore(archive, destination).status, "PASS")
        self.assertEqual(source_state(destination), self.source)
        self.assertEqual(verify(archive).status, "PASS")
        with self.assertRaisesRegex(ValueError, "already exists"):
            restore(archive, destination)

    def test_tag_is_added_after_source_commit_without_circular_manifest_commit(self) -> None:
        self.git("-c", "user.name=Scaffold test fixture", "-c", "user.email=fixture@example.invalid",
                 "tag", "-a", "test-review", "-m", "Synthetic unit-test tag")
        manifest = self.manifest.model_copy(update={"source_tag": "test-review"})
        write_model(self.root / self.manifest_name, manifest)
        archive = self.parent / "tagged.zip"
        self.assertEqual(package(self.root, self.manifest_name, archive).status, "PASS")
        self.assertEqual(restore(archive, self.parent / "restored").status, "PASS")

    def test_standalone_deviation_uses_retained_release_evidence(self) -> None:
        deviation = ReleaseDeviation(
            id="DV-standalone", scope=(self.project_id,), owner="Synthetic test owner",
            reason="Exercise standalone deviation evidence without a product record.",
            status=DeviationStatus.APPROVED, expires=date(9999, 12, 31), evidence=("review",),
        )
        manifest = self.manifest.model_copy(update={"deviations": (deviation,)})
        report = check(self.root, manifest)
        self.assertEqual(report.status, "PASS", report.issues)
        write_model(self.root / self.manifest_name, manifest)
        archive = self.parent / "deviation.zip"
        self.assertEqual(package(self.root, self.manifest_name, archive).status, "PASS")
        self.assertEqual(restore(archive, self.parent / "restored").status, "PASS")
        for field, value, code in (
            ("scope", ("unselected-board",), "DEVIATION_SCOPE"),
            ("evidence", ("missing-artifact",), "DEVIATION_EVIDENCE"),
            ("status", DeviationStatus.OPEN, "DEVIATION_STATUS"),
            ("expires", date(2000, 1, 1), "DEVIATION_EXPIRY"),
        ):
            with self.subTest(field=field):
                bad = manifest.model_copy(update={"deviations": (
                    deviation.model_copy(update={field: value}),)})
                self.assertIn(code, {issue.code for issue in check(self.root, bad).issues})

    def test_stale_source_and_missing_reports_fail_even_with_pass_labels(self) -> None:
        path = self.root / self.config.required_inputs[0]
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertEqual(check(self.root, self.manifest).status, "FAIL")
        self.git("restore", "--", self.config.required_inputs[0])
        self.native_path.unlink()
        self.assertIn("RELEASE_EVIDENCE", {issue.code for issue in check(self.root, self.manifest).issues})

    def test_assume_unchanged_does_not_hide_modified_source(self) -> None:
        name = self.config.required_inputs[0]
        self.git("update-index", "--assume-unchanged", "--", name)
        path = self.root / name
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertFalse(source_state(self.root).clean)
        self.assertEqual(check(self.root, self.manifest).status, "FAIL")

    def test_native_failure_cannot_be_hidden_by_rehashing_summary(self) -> None:
        native = read_model(self.native_path, ValidationSummary)
        bad = dict(native.checks)
        bad["erc"] = CheckEvidence(status="FAIL", returncode=5, findings=1)
        write_model(self.native_path, native.model_copy(update={"checks": bad}))
        with self.assertRaisesRegex(ValueError, "failed or missing"):
            verify_native(self.root, reference(self.root, self.native_path), self.source, self.project_id)

    def test_tampering_missing_extra_and_unsafe_archive_members_fail(self) -> None:
        archive = self.parent / "good.zip"
        package(self.root, self.manifest_name, archive)
        with zipfile.ZipFile(archive) as incoming:
            originals = {name: incoming.read(name) for name in incoming.namelist()}
        review_name = "payload/build/releases/test/review.txt"
        mutations = (
            {**originals, review_name: b"tampered"},
            {name: content for name, content in originals.items() if name != review_name},
            {**originals, "extra.txt": b"extra"},
            {**originals, "../escape.txt": b"unsafe"},
            {**originals, "payload/.git/config": b"unsafe"},
        )
        for index, files in enumerate(mutations):
            with self.subTest(index=index):
                bad = self.parent / f"bad-{index}.zip"
                with zipfile.ZipFile(bad, "w") as outgoing:
                    for name, content in files.items():
                        outgoing.writestr(name, content)
                destination = self.parent / f"rejected-{index}"
                with self.assertRaises((ValueError, FileNotFoundError)):
                    restore(bad, destination)
                self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
