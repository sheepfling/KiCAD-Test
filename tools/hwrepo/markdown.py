"""Typed SnakeMD builders for Markdown created by repository workflows."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from urllib.parse import quote

from snakemd import Document, Inline, MDList, Paragraph


def paragraph(document: Document, *content: str | Inline) -> None:
    """Append one structured paragraph while preserving inline semantics."""
    document.add_block(Paragraph(content))


def markdown_text(document: Document) -> str:
    """Render deterministic Markdown with exactly one final newline."""
    return f"{document}".rstrip("\n") + "\n"


def write_markdown(path: Path, document: Document) -> None:
    """Render one deterministic UTF-8 Markdown document with a final newline."""
    path.write_text(markdown_text(document), encoding="utf-8")


def retitled_document(source: str, title: str) -> Document:
    """Replace the first heading while preserving the authored document body."""
    _, separator, body = source.partition("\n")
    if not separator:
        raise ValueError("Markdown document must contain a title and body")
    document = Document()
    document.add_heading(title)
    remaining = body.strip("\n")
    if remaining:
        document.add_raw(remaining)
    return document


def design_notes() -> Document:
    document = Document()
    document.add_heading("Design notes")
    document.add_paragraph(
        "Record purpose, requirements, interfaces, design decisions and bring-up results here."
    )
    return document


def project_readme(project_id: str) -> Document:
    document = Document()
    document.add_heading(project_id)
    document.add_paragraph("Development project — NOT FOR MANUFACTURE.")
    paragraph(
        document,
        "Create the native project in ",
        Inline("kicad/", code=True),
        " using the toolchain selected in ",
        Inline("project.json", link="project.json"),
        ". Complete the source inventory and ",
        Inline("test contract", link="tests/contract.json"),
        ". See ",
        Inline("design notes", link="docs/README.md"),
        ".",
    )
    paragraph(
        document,
        "From the repository root: ",
        Inline(f"python -B -m tools.ci --project {project_id}", code=True),
        ".",
    )
    document.add_paragraph(
        "Checks will fail until the native files and engineering expectations exist."
    )
    return document


def imported_project_readme(
    project_id: str, project_path: str, upstream_documents: Iterable[str]
) -> Document:
    document = Document()
    document.add_heading(project_id)
    document.add_paragraph("Imported development project — NOT FOR MANUFACTURE.")
    paragraph(
        document,
        "Open ",
        Inline("the native project", link=quote(project_path)),
        ". Filenames and native bytes are preserved.",
    )
    paragraph(
        document,
        "Review the ",
        Inline("import receipt", link="docs/import.json"),
        ", including excluded files, and ",
        Inline("design notes", link="docs/README.md"),
        ". Complete the independent ",
        Inline("test contract", link="tests/contract.json"),
        " and ",
        Inline("project metadata", link="project.json"),
        ".",
    )
    paragraph(
        document,
        "From the repository root: ",
        Inline(f"python -B -m tools.ci --project {project_id}", code=True),
        ".",
    )
    document.add_paragraph(
        "Import success means source was copied, not that native validation passes."
    )
    links = tuple(
        Inline(f"Upstream {name}", link=quote(f"kicad/{name}"))
        for name in upstream_documents
    )
    if links:
        document.add_block(MDList(links))
    return document


def release_review(release_id: str, source_commit: str, release_class: str) -> Document:
    document = Document()
    document.add_heading(release_id)
    paragraph(
        document,
        "Source: ",
        Inline(source_commit, code=True),
        ". Class: ",
        Inline(release_class, code=True),
        ".",
    )
    document.add_paragraph(
        "Candidate for engineering review. This report records executed checks; "
        "it is not human approval."
    )
    document.add_paragraph(
        "Manufacturing and assembly files require review of layers, origin, "
        "population, and supplier requirements."
    )
    return document
