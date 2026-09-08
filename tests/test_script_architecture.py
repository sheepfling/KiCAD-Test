"""Guard the typed scripting boundary used by policy and CI tools."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_MODULES = (
    "tools/hwrepo/product.py",
    "tools/hwrepo/generation.py",
    "tools/hwrepo/repository.py",
    "tools/hwrepo/documentation.py",
    "tools/hwrepo/release.py",
    "tools/hwrepo/metrics.py",
    "tools/hwrepo/sourcing.py",
    "tools/hwrepo/selection.py",
    "tools/hwrepo/template.py",
    "tools/lint_registry.py",
    "tools/check_toolchain.py",
    "tools/ci_matrix.py",
    "tools/check_all.py",
    "tools/ci.py",
    "tools/docs_policy.py",
    "tools/release.py",
    "tools/metrics.py",
    "tools/sourcing.py",
    "tools/template.py",
)
JSON_ADAPTERS = {
    "tools/hwrepo/contracts.py",
    "tools/validate.py",
    "tools/fault_probe.py",
}


class ScriptArchitectureTests(unittest.TestCase):
    def source(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_core_services_do_not_reintroduce_any_or_opaque_object_maps(self) -> None:
        for relative in CORE_MODULES:
            with self.subTest(module=relative):
                source = self.source(relative)
                tree = ast.parse(source, filename=relative)
                forbidden_names = {
                    node.id
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Name) and node.id == "Any"
                }
                self.assertEqual(forbidden_names, set())
                self.assertNotIn("dict[str, object]", source)
                self.assertNotIn("Mapping[str, object]", source)

    def test_raw_json_deserialization_is_limited_to_declared_adapters(self) -> None:
        all_modules = (*CORE_MODULES, *JSON_ADAPTERS)
        for relative in all_modules:
            with self.subTest(module=relative):
                calls_json_loads = "json.loads(" in self.source(relative)
                self.assertEqual(calls_json_loads, relative in JSON_ADAPTERS)

    def test_models_define_closed_inputs_and_typed_ci_outputs(self) -> None:
        source = self.source("tools/hwrepo/models.py")
        self.assertIn('extra="forbid"', source)
        self.assertIn("frozen=True", source)
        self.assertIn("class ValidationSummary", source)
        self.assertIn("class CheckAllSummary", source)
        self.assertIn("class ToolchainAssessment", source)
        self.assertIn("class DocumentationPolicyReport", source)
        self.assertIn("class ReleaseManifest", source)
        self.assertIn("class TemplateContract", source)
        self.assertIn("class SourcingSnapshot", source)
        self.assertIn("class TemplateMetricsReport", source)


if __name__ == "__main__":
    unittest.main()
