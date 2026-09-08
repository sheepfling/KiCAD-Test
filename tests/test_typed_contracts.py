"""Typed-contract tests: raw JSON exists only here at the file boundary."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from tools.hwrepo.contracts import read_model
from tools.hwrepo.generation import (
    bom_rows,
    csv_bytes,
    drift,
    electrical_view,
    generate,
    library_sbom,
    system_view,
)
from tools.hwrepo.models import (
    Assembly,
    LibrariesCatalog,
    ProductRecord,
    ProjectRegistry,
)
from tools.hwrepo.product import check, load_repository, validate_product

ROOT = Path(__file__).resolve().parents[1]


class TypedContractsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = load_repository(ROOT)
        cls.product = cls.repository.products[0]

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="typed-contract-")
        self.addCleanup(self.temporary.cleanup)
        self.temp = Path(self.temporary.name)

    def codes(self, product: ProductRecord) -> set[str]:
        return {
            issue.code
            for issue in validate_product(
                ROOT,
                product,
                self.repository.parts,
                self.repository.interfaces,
                self.repository.projects,
            )
        }

    def product_with(self, **updates: object) -> ProductRecord:
        return self.product.model_copy(update=updates)

    def stage(self) -> Path:
        for directory in (
            "boards",
            "catalog",
            "configs",
            "product",
            "docs",
            "generated",
            "libraries",
            "firmware",
            "schemas",
        ):
            shutil.copytree(ROOT / directory, self.temp / directory)
        shutil.copy2(ROOT / "pilot.json", self.temp / "pilot.json")
        return self.temp

    def test_loaded_records_are_models_with_immutable_sequences(self) -> None:
        self.assertEqual(check(ROOT).status, "PASS")
        self.assertIsInstance(self.product, ProductRecord)
        self.assertIsInstance(self.product.assemblies, tuple)
        self.assertIsInstance(self.product.assemblies[0], Assembly)
        with self.assertRaises((TypeError, ValidationError)):
            self.product.id = "changed"

    def test_json_boundary_rejects_unknown_wrong_typed_and_duplicate_values(self) -> None:
        raw = self.product.model_dump(mode="json", by_alias=True)
        raw["invented"] = True
        path = self.temp / "unknown.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaises(ValueError):
            read_model(path, ProductRecord)
        raw = self.product.model_dump(mode="json", by_alias=True)
        raw["assemblies"][0]["members"][0]["quantity"] = "1"
        path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaises(ValueError):
            read_model(path, ProductRecord)
        path.write_text('{"id":"one","id":"two"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            read_model(path, ProductRecord)

    def test_semantic_validation_consumes_typed_objects(self) -> None:
        second = self.product.assemblies[1]
        unknown_member = second.members[0].model_copy(update={"item": "missing-part"})
        unknown_assembly = second.model_copy(
            update={"members": (unknown_member, *second.members[1:])}
        )
        product = self.product_with(
            assemblies=(self.product.assemblies[0], unknown_assembly, *self.product.assemblies[2:])
        )
        self.assertIn("PART_REF", self.codes(product))

        bad_terminal = self.product.terminals[0].model_copy(update={"pin": "999"})
        product = self.product_with(
            terminals=(bad_terminal, *self.product.terminals[1:])
        )
        self.assertIn("KICAD_TERMINAL", self.codes(product))

        duplicate_wire = self.product.connections[0].model_copy(update={"id": "C-OTHER"})
        product = self.product_with(
            connections=(*self.product.connections, duplicate_wire)
        )
        self.assertIn("TERMINAL_ALLOCATION", self.codes(product))

    def test_relationship_variant_harness_and_mechanical_rules_remain_typed(self) -> None:
        functional = self.product.connections[2].model_copy(update={"harness": "H-STATUS"})
        product = self.product_with(
            connections=(*self.product.connections[:2], functional, *self.product.connections[3:])
        )
        self.assertIn("HARNESS_REF", self.codes(product))

        invalid_variant = self.product.variants[0].model_copy(update={"exclude": ("UNO",)})
        product = self.product_with(
            variants=(invalid_variant, *self.product.variants[1:])
        )
        self.assertIn("VARIANT_ENDPOINT", self.codes(product))

        bad_handoff = self.product.mechanical[0].model_copy(update={"instances": ("MISSING",)})
        product = self.product_with(
            mechanical=(bad_handoff,)
        )
        self.assertIn("MECHANICAL_INSTANCE", self.codes(product))

    def test_deterministic_bom_has_typed_rows_and_functional_links_are_excluded(self) -> None:
        standard = self.product.variants[0]
        rows = bom_rows(self.product, self.repository.parts, standard)
        self.assertEqual(rows[0].part_id, "training-generic-cable")
        self.assertTrue(all(row.disposition == "NOT FOR MANUFACTURE" for row in rows))
        self.assertEqual(
            csv_bytes(rows),
            csv_bytes(bom_rows(self.product, self.repository.parts, standard)),
        )
        view = electrical_view(self.product, standard)
        self.assertEqual(
            tuple(connection.id for connection in view.connections),
            ("C-RETURN", "C-SIGNAL"),
        )
        system = system_view(self.product, standard)
        self.assertEqual(
            [(connection.id, connection.kind.value) for connection in system.connections],
            [
                ("C-MOUNT", "mechanical"),
                ("C-RETURN", "electrical"),
                ("C-SIGNAL", "electrical"),
                ("C-STATUS-ROLE", "functional"),
            ],
        )

    def test_typed_generator_drift_detection(self) -> None:
        root = self.stage()
        generate(root)
        self.assertEqual(drift(root), ())
        target = root / "generated/product/status-indicator-system/STANDARD.bom.csv"
        target.write_text("stale", encoding="utf-8")
        self.assertIn("GENERATION_DRIFT: generated/product/status-indicator-system/STANDARD.bom.csv", drift(root))

    def test_library_sbom_is_deterministic_and_retains_evidence_hashes(self) -> None:
        sbom = library_sbom(ROOT)
        self.assertEqual([library.id for library in sbom.libraries], ["library-status-led-training"])
        self.assertFalse(sbom.build_authorized)
        catalog = read_model(ROOT / "catalog/libraries.json", LibrariesCatalog)
        self.assertEqual(
            sbom.libraries[0].provenance_sha256,
            catalog.libraries[0].provenance_sha256,
        )

    def test_registry_is_deserialized_as_a_closed_model(self) -> None:
        registry = read_model(ROOT / "catalog/projects.json", ProjectRegistry)
        self.assertEqual(registry.projects[0].id, "controller")
        self.assertEqual(registry.catalogs.parts, "catalog/parts.json")


if __name__ == "__main__":
    unittest.main()
