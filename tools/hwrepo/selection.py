"""Typed project-selection helpers for local and hosted automation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discovery import load_registry
from .models import ProjectRecord, ProjectRegistry


@dataclass(frozen=True)
class ProjectSelector:
    """OR-match explicit IDs/tags, then subtract projects bearing excluded tags."""

    project_ids: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    excluded_tags: tuple[str, ...] = ()

    @property
    def active(self) -> bool:
        return bool(self.project_ids or self.tags or self.excluded_tags)


def duplicate_values(values: tuple[str, ...], label: str) -> None:
    duplicates = {
        value
        for value in values
        if sum(candidate.casefold() == value.casefold() for candidate in values) > 1
    }
    if duplicates:
        raise ValueError(f"Duplicate {label}: {sorted(duplicates)}")


def select_projects(
    registry: ProjectRegistry, selector: ProjectSelector
) -> tuple[ProjectRecord, ...]:
    """Resolve deterministic project selection without scanning CAD sources."""
    duplicate_values(selector.project_ids, "project IDs")
    duplicate_values(selector.tags, "included tags")
    duplicate_values(selector.excluded_tags, "excluded tags")
    available = {project.id: project for project in registry.projects}
    unknown = sorted(set(selector.project_ids) - set(available))
    if unknown:
        raise ValueError(f"Unknown project IDs: {unknown}")
    include_tags = frozenset(selector.tags)
    excluded_tags = frozenset(selector.excluded_tags)
    has_inclusions = bool(selector.project_ids or selector.tags)
    selected = tuple(
        project
        for project in registry.projects
        if (
            not has_inclusions
            or project.id in selector.project_ids
            or bool(include_tags & frozenset(project.tags))
        )
        and not (excluded_tags & frozenset(project.tags))
    )
    if not selected:
        raise ValueError("No projects matched the requested IDs/tags after exclusions")
    return selected


def resolve_project_ids(root: Path, selector: ProjectSelector) -> tuple[str, ...]:
    """Load the authoritative registry and return selected project identities."""
    registry = load_registry(root)
    return tuple(project.id for project in select_projects(registry, selector))
