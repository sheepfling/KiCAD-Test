"""Tests for deterministic Markdown layout and repository-documentation policy."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from tools.hwrepo.contracts import write_model
from tools.hwrepo.documentation import check
from tools.hwrepo.models import DocumentationException, DocumentationPolicy


class DocumentationPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory[str]()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()

    def write_policy(
        self,
        roots: tuple[str, ...] = ("README.md",),
        exceptions: tuple[DocumentationException, ...] = (),
    ) -> None:
        write_model(
            self.root / "docs/documentation-policy.json",
            DocumentationPolicy(roots=roots, exceptions=exceptions),
        )

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def codes(self) -> set[str]:
        return {finding.code for finding in check(self.root).issues}

    def test_valid_document_graph_passes(self) -> None:
        self.write_policy()
        self.write("README.md", "# Root\n\n[Guide](docs/guide.md#usage)\n")
        self.write("docs/guide.md", "# Guide\n\n## Usage\n")

        report = check(self.root)

        self.assertEqual(report.status, "PASS")
        self.assertEqual(report.documents, 2)

    def test_case_mismatch_and_missing_fragment_fail(self) -> None:
        self.write_policy()
        self.write(
            "README.md",
            "# Root\n\n[Wrong case](docs/Guide.md)\n[Bad fragment](#not-here)\n",
        )
        self.write("docs/guide.md", "# Guide\n")

        self.assertEqual(self.codes(), {"DOC101", "DOC103", "DOC105"})

    def test_path_escape_and_orphan_fail(self) -> None:
        self.write_policy()
        self.write("README.md", "# Root\n\n[Escape](../outside.md)\n")
        self.write("docs/orphan.md", "# Orphan\n")

        self.assertEqual(self.codes(), {"DOC101", "DOC105"})

    def test_unsafe_policy_path_fails_closed(self) -> None:
        self.write_policy(roots=("../outside.md",))
        self.write("README.md", "# Root\n")

        self.assertEqual(self.codes(), {"DOC900"})

    def test_layout_rules_fail_before_review(self) -> None:
        self.write_policy()
        self.write("README.md", "# Root\n\tTabbed\n\n#### Skipped\n\n```python\n")

        self.assertEqual(self.codes(), {"MD001", "MD003", "MD005"})

    def test_active_scoped_exception_is_used_but_expired_exception_fails(self) -> None:
        active = DocumentationException(
            id="permit-tabs",
            code="MD001",
            path="README.md",
            reason="Compatibility fixture under review.",
            expires=date(2026, 9, 8),
        )
        expired = DocumentationException(
            id="expired-example",
            code="MD002",
            path="README.md",
            reason="Demonstrates expiry enforcement.",
            expires=date(2026, 9, 6),
        )
        self.write_policy(exceptions=(active, expired))
        self.write("README.md", "# Root\n\tCompatibility fixture\n")

        report = check(self.root, today=date(2026, 9, 7))

        self.assertEqual(report.status, "FAIL")
        self.assertEqual({finding.code for finding in report.issues}, {"DOC201"})


if __name__ == "__main__":
    unittest.main()
