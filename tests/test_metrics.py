"""Current-state metrics tests; historical tracking remains an external system."""
from __future__ import annotations

import unittest
from datetime import date

from tests.support import reference_root
from tools.hwrepo.metrics import collect, deviation_metrics
from tools.hwrepo.models import DeviationStatus, ReleaseDeviation

ROOT = reference_root()


class TemplateMetricsTests(unittest.TestCase):
    def test_current_policy_metrics_are_non_authorizing(self) -> None:
        report = collect(ROOT, today=date(2026, 9, 7))
        self.assertTrue(all(metric.status == "PASS" for metric in report.checks))
        self.assertEqual(report.stale_evidence, 0)
        self.assertFalse(report.build_authorized)

    def test_deviation_metrics_preserve_status_and_expiry_counts(self) -> None:
        values = (
            ReleaseDeviation(
                id="DV-APPROVED",
                scope=("status-indicator-system",),
                owner="Configuration manager",
                reason="Test-only approved deviation.",
                status=DeviationStatus.APPROVED,
                expires=date(2026, 9, 8),
                evidence=("EV-1",),
            ),
            ReleaseDeviation(
                id="DV-EXPIRED",
                scope=("status-indicator-system",),
                owner="Configuration manager",
                reason="Test-only open deviation.",
                status=DeviationStatus.OPEN,
                expires=date(2026, 9, 6),
                evidence=("EV-2",),
            ),
        )
        report = deviation_metrics(values, today=date(2026, 9, 7))
        self.assertEqual((report.total, report.approved, report.open, report.expired), (2, 1, 1, 1))


if __name__ == "__main__":
    unittest.main()
