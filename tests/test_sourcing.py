"""Supplier-offer snapshots remain typed, local and non-authorizing."""
from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools.hwrepo.models import SourcingSnapshot, SupplierOffer
from tools.hwrepo.sourcing import check

ROOT = Path(__file__).resolve().parents[1]


class SourcingSnapshotTests(unittest.TestCase):
    def snapshot(self, **updates: object) -> SourcingSnapshot:
        base = SourcingSnapshot(
            snapshot_id="training-offer-observation",
            source_commit="a" * 40,
            observed_at=datetime(2026, 9, 7, tzinfo=timezone.utc),
            offers=(
                SupplierOffer(
                    id="offer-1",
                    part_id="training-generic-led-red-5mm",
                    supplier="Example supplier observation",
                    supplier_sku="EXAMPLE-LED-5MM",
                    source_url="https://example.invalid/offer",
                    region="test-only",
                    currency="USD",
                    quantity_break=1,
                    unit_price_minor=0,
                    availability="not a purchasing instruction",
                    lead_time_days=None,
                ),
            ),
        )
        return base.model_copy(update=updates)

    def test_known_part_offer_is_a_non_authorizing_snapshot(self) -> None:
        report = check(ROOT, self.snapshot())
        self.assertEqual(report.status, "PASS", report.issues)
        self.assertFalse(report.build_authorized)

    def test_unknown_part_offer_fails_closed(self) -> None:
        offer = self.snapshot().offers[0].model_copy(update={"part_id": "unknown-part"})
        report = check(ROOT, self.snapshot(offers=(offer,)))
        self.assertEqual(report.status, "FAIL")
        self.assertIn("SOURCING_PART", {issue.code for issue in report.issues})


if __name__ == "__main__":
    unittest.main()
