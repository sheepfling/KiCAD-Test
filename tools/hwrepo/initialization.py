"""Initialize a fork without changing fixtures or overwriting adopted designs."""
from __future__ import annotations

from pathlib import Path

from .contracts import read_model, repo_path
from .licensing import template_license
from .models import (
    InterfacesCatalog,
    LibrariesCatalog,
    PartsCatalog,
    PolicyIssue,
    ProductIndex,
    ProjectDiscovery,
    TemplateAdoptionRecord,
    TemplateContract,
    TemplateInitReport,
)


def initialize(root: Path, project_id: str) -> TemplateInitReport:
    """Validate all inputs first; repeated initialization preserves adopter work."""
    root = root.resolve()
    before: dict[Path, bytes | None] = {}
    try:
        contract = read_model(root / "templates/template-contract.json", TemplateContract)
        adoption = TemplateAdoptionRecord(template_version=contract.template_version,
                                          project_id=project_id, status="initialized")
        record_path = repo_path(root, "template-adoption.json")
        if record_path.exists():
            previous = read_model(record_path, TemplateAdoptionRecord)
            if previous.project_id != project_id:
                raise ValueError("This fork is already assigned a different project ID")
            if previous.status == "initialized":
                return TemplateInitReport(status="PASS", project_id=project_id)
        # Initialization retires only known reference records, never adopter data.
        for directory in ("projects", "products", "libraries"):
            for path in repo_path(root, directory).iterdir():
                if path.name != "README.md":
                    raise ValueError(f"Initialize before adding designs: {directory}/{path.name}")
        names = ("projects.json", "products.json", "parts.json", "interfaces.json", "libraries.json")
        for name in names:
            live = repo_path(root, f"catalog/{name}")
            fixture = repo_path(root, f"examples/catalog/{name}")
            if live.read_bytes() != fixture.read_bytes():
                raise ValueError(f"Refusing to replace customized catalog/{name}")
        discovery = read_model(root / "catalog/projects.json", ProjectDiscovery)
        updates = {
            "catalog/projects.json": discovery.model_copy(update={"project_roots": ("projects",)}),
            "catalog/products.json": ProductIndex(schema_version="1", products=()),
            "catalog/parts.json": PartsCatalog(schema_version="0.1", parts=()),
            "catalog/interfaces.json": InterfacesCatalog(schema_version="0.1", interfaces=()),
            "catalog/libraries.json": LibrariesCatalog(schema_version="0.1", libraries=()),
            "template-adoption.json": adoption,
        }
        payloads: dict[Path, bytes | None] = {
            repo_path(root, name): (model.model_dump_json(indent=2) + "\n").encode()
            for name, model in updates.items()
        }
        readme = repo_path(root, "README.md")
        _, _, remaining = readme.read_text(encoding="utf-8").partition("\n")
        payloads[readme] = (f"# {project_id}\n" + remaining).encode()
        license_path = template_license(root)
        if license_path is not None:
            payloads[license_path] = None
        before = {path: path.read_bytes() if path.exists() else None for path in payloads}
        for path, content in payloads.items():
            if content is None:
                path.unlink()
            else:
                path.write_bytes(content)
        return TemplateInitReport(status="PASS", project_id=project_id,
                                  changed=tuple(path.relative_to(root).as_posix() for path in payloads),
                                  removed=() if license_path is None else ("LICENSE",))
    except (OSError, ValueError) as exc:
        for path, content in before.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        return TemplateInitReport(status="FAIL", project_id=project_id,
                                  issues=(PolicyIssue(code="TEMPLATE_INIT", location="repository",
                                                      message=str(exc)),))
