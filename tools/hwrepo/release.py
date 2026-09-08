"""Typed, read-only release-readiness validation; it never creates a release."""
from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Iterable
from datetime import date, datetime, timezone
from pathlib import Path

from .contracts import read_model, repo_path
from .models import (
    Assurance,
    DeviationStatus,
    InterfacesCatalog,
    LibrariesCatalog,
    PolicyIssue,
    ProductRecord,
    ProjectConfig,
    ProjectRecord,
    ProjectRegistry,
    ReleaseArtifactKind,
    ReleaseAssurancePolicy,
    ReleaseClass,
    ReleaseManifest,
    ReleasePoliciesCatalog,
    ReleaseReadinessReport,
    ReleaseStatus,
    ToolchainsCatalog,
)
from .product import ProductRepository, load_repository

REQUIRED_CHECKS = frozenset(
    {"repository", "product_model", "generation_drift", "harness", "kicad"}
)
MATURITY_ORDER = {
    "training": 0,
    "engineering_review": 1,
    "prototype": 2,
    "pilot": 3,
    "production": 4,
}
RELEASE_MATURITY = {
    ReleaseClass.ENGINEERING_REVIEW: "engineering_review",
    ReleaseClass.PROTOTYPE: "prototype",
    ReleaseClass.PILOT: "pilot",
    ReleaseClass.PRODUCTION: "production",
}
REQUIRED_ARTIFACT_KINDS = {
    ReleaseClass.ENGINEERING_REVIEW: frozenset({ReleaseArtifactKind.REVIEW_RECORD}),
    ReleaseClass.PROTOTYPE: frozenset(
        {
            ReleaseArtifactKind.BOM,
            ReleaseArtifactKind.SCHEMATIC_EXPORT,
            ReleaseArtifactKind.PCB_EXPORT,
            ReleaseArtifactKind.VALIDATION_REPORT,
        }
    ),
    ReleaseClass.PILOT: frozenset(
        {
            ReleaseArtifactKind.BOM,
            ReleaseArtifactKind.SCHEMATIC_EXPORT,
            ReleaseArtifactKind.PCB_EXPORT,
            ReleaseArtifactKind.VALIDATION_REPORT,
        }
    ),
    ReleaseClass.PRODUCTION: frozenset(
        {
            ReleaseArtifactKind.BOM,
            ReleaseArtifactKind.SCHEMATIC_EXPORT,
            ReleaseArtifactKind.PCB_EXPORT,
            ReleaseArtifactKind.VALIDATION_REPORT,
            ReleaseArtifactKind.FABRICATION_PACKAGE,
            ReleaseArtifactKind.ASSEMBLY_PACKAGE,
        }
    ),
}
ASSURANCE_ORDER = {
    Assurance.NOT_APPLICABLE: -1,
    Assurance.UNKNOWN: 0,
    Assurance.ASSUMED: 1,
    Assurance.INFERRED: 2,
    Assurance.OBSERVED: 3,
    Assurance.MANUFACTURER_DOCUMENTED: 4,
    Assurance.VERIFIED: 5,
}


def git(root: Path, *args: str) -> str:
    """Read one Git fact without altering the worktree, index, refs or remotes."""
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def issue(code: str, location: str, message: str) -> PolicyIssue:
    """Create a concise, typed release-readiness finding."""
    return PolicyIssue(code=code, location=location, message=message)


def selected_products(
    repository: ProductRepository, manifest: ReleaseManifest, issues: list[PolicyIssue]
) -> tuple[ProductRecord, ...]:
    """Resolve every explicit product/variant selection once and fail unknown values."""
    products = {product.id: product for product in repository.products}
    selected: dict[str, ProductRecord] = {}
    seen: set[tuple[str, str]] = set()
    for selection in manifest.variants:
        key = (selection.product, selection.variant)
        if key in seen:
            issues.append(issue("RELEASE_VARIANT", selection.product, "Duplicate product/variant selection"))
            continue
        seen.add(key)
        product = products.get(selection.product)
        if product is None:
            issues.append(issue("RELEASE_PRODUCT", selection.product, "Unknown product"))
            continue
        if selection.variant not in {variant.id for variant in product.variants}:
            issues.append(
                issue("RELEASE_VARIANT", selection.product, f"Unknown variant {selection.variant}")
            )
            continue
        variant = next(variant for variant in product.variants if variant.id == selection.variant)
        if selection.product_revision != product.revision:
            issues.append(
                issue("RELEASE_PRODUCT_REVISION", selection.product, "Product revision does not match")
            )
        if selection.variant_revision != variant.revision:
            issues.append(
                issue("RELEASE_VARIANT_REVISION", selection.variant, "Variant revision does not match")
            )
        selected[product.id] = product
    if not manifest.variants:
        issues.append(issue("RELEASE_VARIANT", "variants", "At least one product/variant is required"))
    return tuple(selected[identifier] for identifier in sorted(selected))


def product_scope(product: ProductRecord) -> frozenset[str]:
    """Return the stable IDs a release deviation may explicitly affect."""
    return frozenset(
        (
            product.id,
            *(assembly.id for assembly in product.assemblies),
            *(terminal.id for terminal in product.terminals),
            *(connection.id for connection in product.connections),
            *(harness.id for harness in product.harnesses),
            *(handoff.id for handoff in product.mechanical),
            *(variant.id for variant in product.variants),
        )
    )


def selected_project_records(
    repository: ProductRepository, products: Iterable[ProductRecord]
) -> tuple[ProjectRecord, ...]:
    """Resolve controlled KiCad projects used by the selected product definitions."""
    projects: dict[str, ProjectRecord] = {}
    for product in products:
        for assembly in product.assemblies:
            if assembly.project_id is None:
                continue
            project = repository.projects.get(assembly.project_id)
            if project is None:
                raise ValueError(f"Selected product uses unknown project {assembly.project_id}")
            projects[project.id] = project
    return tuple(projects[identifier] for identifier in sorted(projects))


def configured_toolchains(root: Path, projects: Iterable[ProjectRecord]) -> frozenset[str]:
    """Resolve declared toolchain identities used by selected KiCad projects."""
    registry = read_model(repo_path(root, "catalog/projects.json"), ProjectRegistry)
    toolchains = read_model(repo_path(root, registry.catalogs.toolchains), ToolchainsCatalog)
    known = {record.id for record in toolchains.toolchains}
    used: set[str] = set()
    for project in projects:
        config = read_model(repo_path(root, project.config), ProjectConfig)
        if config.toolchain_id not in known:
            raise ValueError(f"Project has unknown toolchain {config.toolchain_id}")
        used.add(config.toolchain_id)
    return frozenset(used)


def validate_dependencies(
    root: Path,
    projects: Iterable[ProjectRecord],
    manifest: ReleaseManifest,
    findings: list[PolicyIssue],
) -> None:
    """Bind release records to every selected shared-library/interface revision."""
    registry = read_model(repo_path(root, "catalog/projects.json"), ProjectRegistry)
    libraries = {
        record.id: record
        for record in read_model(
            repo_path(root, registry.catalogs.libraries), LibrariesCatalog
        ).libraries
    }
    interfaces = {
        record.id: record
        for record in read_model(
            repo_path(root, registry.catalogs.interfaces), InterfacesCatalog
        ).interfaces
    }
    expected_libraries = {library_id for project in projects for library_id in project.library_ids}
    expected_interfaces = {
        interface_id for project in projects for interface_id in project.interfaces
    }
    release_libraries = {record.id: record for record in manifest.libraries}
    release_interfaces = {record.id: record for record in manifest.interfaces}
    if len(release_libraries) != len(manifest.libraries):
        findings.append(issue("RELEASE_LIBRARY", "libraries", "Duplicate library identity"))
    if len(release_interfaces) != len(manifest.interfaces):
        findings.append(issue("RELEASE_INTERFACE", "interfaces", "Duplicate interface identity"))
    if set(release_libraries) != expected_libraries:
        findings.append(
            issue("RELEASE_LIBRARY", "libraries", "Manifest libraries differ from selected projects")
        )
    if set(release_interfaces) != expected_interfaces:
        findings.append(
            issue("RELEASE_INTERFACE", "interfaces", "Manifest interfaces differ from selected projects")
        )
    for identifier in sorted(expected_libraries):
        catalog = libraries.get(identifier)
        selected = release_libraries.get(identifier)
        if catalog is None or selected is None:
            continue
        if (
            selected.version != catalog.version
            or selected.provenance_sha256 != catalog.provenance_sha256
            or selected.licensing_sha256 != catalog.licensing_sha256
        ):
            findings.append(
                issue("RELEASE_LIBRARY", identifier, "Library version or evidence hash does not match")
            )
    for identifier in sorted(expected_interfaces):
        catalog = interfaces.get(identifier)
        selected = release_interfaces.get(identifier)
        if catalog is None or selected is None:
            continue
        if selected.revision != catalog.revision:
            findings.append(
                issue("RELEASE_INTERFACE", identifier, "Interface revision does not match")
            )


def assurance_policy(root: Path, release_class: ReleaseClass) -> ReleaseAssurancePolicy:
    """Load one explicit assurance floor for the selected release maturity."""
    registry = read_model(repo_path(root, "catalog/projects.json"), ProjectRegistry)
    policies = read_model(
        repo_path(root, registry.catalogs.release_policies), ReleasePoliciesCatalog
    ).policies
    matching = tuple(policy for policy in policies if policy.release_class is release_class)
    if len(matching) != 1:
        raise ValueError(f"Need exactly one assurance policy for {release_class.value}")
    return matching[0]


def validate_assurance(
    products: Iterable[ProductRecord],
    policy: ReleaseAssurancePolicy,
    findings: list[PolicyIssue],
) -> None:
    """Require every retained semantic claim to meet the maturity-specific floor."""
    required = ASSURANCE_ORDER[policy.minimum_assurance]
    for product in products:
        claims = (*product.connections, *product.harnesses, *product.mechanical)
        for claim in claims:
            if ASSURANCE_ORDER[claim.assurance] < required:
                findings.append(
                    issue(
                        "RELEASE_ASSURANCE",
                        claim.id,
                        f"{policy.release_class.value} requires at least "
                        f"{policy.minimum_assurance.value}",
                    )
                )


def check(root: Path, manifest: ReleaseManifest, today: date | None = None) -> ReleaseReadinessReport:
    """Validate candidate release closure without authorizing build, tag or publication."""
    resolved_root = root.resolve()
    findings: list[PolicyIssue] = []
    repository = load_repository(resolved_root)
    findings.extend(repository.issues)
    products = selected_products(repository, manifest, findings)
    try:
        projects = selected_project_records(repository, products)
        validate_dependencies(resolved_root, projects, manifest, findings)
    except (OSError, ValueError) as exc:
        findings.append(issue("RELEASE_DEPENDENCY", "projects", str(exc)))
        projects = ()
    try:
        head = git(resolved_root, "rev-parse", "HEAD")
        if head != manifest.source_commit:
            findings.append(issue("RELEASE_COMMIT", "source_commit", "Manifest does not name HEAD"))
        if git(resolved_root, "status", "--porcelain=v1", "--untracked-files=all"):
            findings.append(issue("RELEASE_DIRTY", "repository", "Release candidate requires a clean worktree"))
    except (OSError, subprocess.SubprocessError) as exc:
        findings.append(issue("RELEASE_GIT", "repository", str(exc)))

    required_maturity = RELEASE_MATURITY[manifest.release_class]
    try:
        validate_assurance(products, assurance_policy(resolved_root, manifest.release_class), findings)
    except (OSError, ValueError) as exc:
        findings.append(issue("RELEASE_ASSURANCE_POLICY", "release_policies", str(exc)))
    for product in products:
        if MATURITY_ORDER[product.maturity] < MATURITY_ORDER[required_maturity]:
            findings.append(
                issue(
                    "RELEASE_MATURITY",
                    product.id,
                    f"{manifest.release_class.value} requires at least {required_maturity}",
                )
            )
        if manifest.release_class is not ReleaseClass.ENGINEERING_REVIEW and (
            product.blocking_issues or any(handoff.open_items for handoff in product.mechanical)
        ):
            findings.append(
                issue("RELEASE_BLOCKER", product.id, "Blocking product or mechanical items remain"))

    try:
        used_toolchains = configured_toolchains(resolved_root, projects)
        if manifest.toolchain_id not in used_toolchains or len(used_toolchains) != 1:
            findings.append(
                issue(
                    "RELEASE_TOOLCHAIN",
                    "toolchain_id",
                    "Manifest must match exactly one selected project toolchain",
                )
            )
    except (OSError, ValueError) as exc:
        findings.append(issue("RELEASE_TOOLCHAIN", "toolchain_id", str(exc)))

    missing_checks = sorted(
        name for name in REQUIRED_CHECKS if manifest.checks.get(name) != "PASS"
    )
    if missing_checks:
        findings.append(
            issue("RELEASE_CHECK", "checks", f"Required passing checks missing: {missing_checks}"))

    artifact_ids: set[str] = set()
    artifact_kinds: set[ReleaseArtifactKind] = set()
    for artifact in manifest.artifacts:
        if artifact.id in artifact_ids:
            findings.append(issue("RELEASE_ARTIFACT", artifact.id, "Duplicate artifact identity"))
        artifact_ids.add(artifact.id)
        artifact_kinds.add(artifact.kind)
        try:
            path = repo_path(resolved_root, artifact.path)
            if not path.is_file():
                raise ValueError("missing artifact")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != artifact.sha256:
                raise ValueError("SHA-256 does not match")
        except (OSError, ValueError) as exc:
            findings.append(issue("RELEASE_ARTIFACT", artifact.path, str(exc)))
    if not manifest.artifacts:
        findings.append(issue("RELEASE_ARTIFACT", "artifacts", "At least one retained artifact is required"))
    required_artifact_kinds = set(REQUIRED_ARTIFACT_KINDS[manifest.release_class])
    if manifest.release_class in {ReleaseClass.PILOT, ReleaseClass.PRODUCTION} and any(
        product.harnesses for product in products
    ):
        required_artifact_kinds.add(ReleaseArtifactKind.HARNESS_EXPORT)
    missing_artifact_kinds = sorted(
        kind.value for kind in required_artifact_kinds - artifact_kinds
    )
    if missing_artifact_kinds:
        findings.append(
            issue(
                "RELEASE_ARTIFACT_KIND",
                "artifacts",
                f"Required artifact kinds missing: {missing_artifact_kinds}",
            )
        )

    scope = frozenset(identifier for product in products for identifier in product_scope(product))
    evidence = frozenset(
        identifier for product in products for identifier in (record.id for record in product.evidence)
    )
    effective_today = today or datetime.now(timezone.utc).date()
    seen_deviations: set[str] = set()
    for deviation in manifest.deviations:
        if deviation.id in seen_deviations:
            findings.append(issue("DEVIATION_ID", deviation.id, "Duplicate deviation identity"))
        seen_deviations.add(deviation.id)
        if not deviation.scope or any(identifier not in scope for identifier in deviation.scope):
            findings.append(issue("DEVIATION_SCOPE", deviation.id, "Scope must name selected release IDs"))
        if deviation.status is not DeviationStatus.APPROVED:
            findings.append(issue("DEVIATION_STATUS", deviation.id, "Release deviation must be approved"))
        if deviation.expires < effective_today:
            findings.append(issue("DEVIATION_EXPIRY", deviation.id, "Release deviation has expired"))
        if not deviation.evidence or any(identifier not in evidence for identifier in deviation.evidence):
            findings.append(issue("DEVIATION_EVIDENCE", deviation.id, "Deviation needs scoped evidence"))

    requires_approval = manifest.release_class is not ReleaseClass.ENGINEERING_REVIEW
    if requires_approval and manifest.status is not ReleaseStatus.APPROVED:
        findings.append(issue("RELEASE_STATUS", "status", "Non-review releases must be approved"))
    if requires_approval and manifest.approval is None:
        findings.append(issue("RELEASE_APPROVAL", "approval", "Approval record is required"))
    if requires_approval and manifest.source_tag is None:
        findings.append(issue("RELEASE_TAG", "source_tag", "Annotated tag is required"))
    if manifest.source_tag is not None:
        try:
            if git(resolved_root, "cat-file", "-t", manifest.source_tag) != "tag":
                findings.append(issue("RELEASE_TAG", "source_tag", "Tag must be annotated"))
            if git(resolved_root, "rev-parse", f"{manifest.source_tag}^{{}}") != manifest.source_commit:
                findings.append(issue("RELEASE_TAG", "source_tag", "Tag does not resolve to source_commit"))
        except (OSError, subprocess.SubprocessError) as exc:
            findings.append(issue("RELEASE_TAG", "source_tag", str(exc)))

    return ReleaseReadinessReport(
        release_id=manifest.release_id,
        release_class=manifest.release_class,
        status="FAIL" if findings else "PASS",
        issues=tuple(findings),
    )
