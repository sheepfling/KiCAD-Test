"""Generate manufacturer-facing files using explicit project export settings."""
from __future__ import annotations

import csv
from pathlib import Path

from ..validate import execute
from .contracts import read_model, repo_path, write_model
from .discovery import load_config, load_registry
from .evidence import digest, evidence_path, source_state, verify_source
from .models import (
    EvidenceFile,
    PartsCatalog,
    ProjectManifest,
    ReleaseExportReport,
    ReleaseExportSettings,
    SourceState,
)


def command_arguments(settings: ReleaseExportSettings, base: Path, output: Path) -> dict[str, tuple[str, ...]]:
    """One exporter table to extend; all destinations are controlled by this tool."""
    origin = ("--use-drill-file-origin",) if settings.coordinate_origin == "plot" else ()
    return {
        "gerbers": ("pcb", "export", "gerbers", "--layers", ",".join(settings.gerber_layers),
                    "--no-protel-ext", "--check-zones", *origin,
                    "--output", str(output / "fabrication"), str(base.with_suffix(".kicad_pcb"))),
        "drill": ("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
                  "--drill-origin", settings.coordinate_origin, "--excellon-units", "mm",
                  "--output", str(output / "fabrication"), str(base.with_suffix(".kicad_pcb"))),
        "position": ("pcb", "export", "pos", "--format", "csv", "--units", settings.position_units,
                     "--exclude-dnp", *origin, "--output", str(output / "assembly/positions.csv"),
                     str(base.with_suffix(".kicad_pcb"))),
        "bom": ("sch", "export", "bom", "--fields", "Reference,Value,Footprint,PART_ID,DNP",
                "--labels", "Reference,Value,Footprint,PartID,DNP", "--exclude-dnp",
                "--output", str(output / "assembly/bom.csv"), str(base.with_suffix(".kicad_sch"))),
    }


def export(root: Path, manifest_path: str, output: Path, cli: str) -> ReleaseExportReport:
    root, output = root.resolve(), output.absolute()
    relative = output.relative_to(root).as_posix()
    repo_path(root, relative)
    if not relative.startswith("build/"):
        raise ValueError("Release exports belong under the ignored build/ directory")
    config = load_config(root, manifest_path)
    manifest = read_model(repo_path(root, manifest_path), ProjectManifest)
    settings = manifest.release_exports
    if settings is None or manifest.kind.value != "pcb":
        raise ValueError("PCB release exports require project.json release_exports settings")
    source = source_state(root)
    if not source.clean or source.commit is None:
        raise ValueError("Release exports require clean committed source")
    output.mkdir(parents=True, exist_ok=False)
    (output / "assembly").mkdir()
    (output / "fabrication").mkdir()
    version = execute((cli, "version"), root, output, "version")
    if version.returncode != 0 or version.stdout.strip() != config.kicad_version:
        raise ValueError("Export executable must match the pinned project KiCad version")
    commands = {name: execute((cli, *arguments), root, output, name)
                for name, arguments in command_arguments(settings, repo_path(root, config.project), output).items()}
    if commands["bom"].returncode == 0:
        purchasing_bom(root, output / "assembly/bom.csv", output / "assembly/purchasing-bom.csv")
    expected = (tuple((output / "fabrication").glob("*.gbr")),
                tuple((output / "fabrication").glob("*.drl")),
                (output / "assembly/positions.csv", output / "assembly/bom.csv"))
    files = {path.relative_to(output).as_posix(): digest(path)
             for path in sorted(output.rglob("*")) if path.is_file()}
    passed = (all(command.returncode == 0 and command.error is None for command in commands.values())
              and all(group and all(path.is_file() and path.stat().st_size for path in group) for group in expected)
              and source_state(root) == source)
    report = ReleaseExportReport(project_id=config.project_id, source=source, toolchain_id=config.toolchain_id,
                                 settings=settings, commands={"version": version, **commands},
                                 artifacts_sha256=files, status="PASS" if passed else "FAIL")
    write_model(output / "exports.json", report)
    return report


def purchasing_bom(root: Path, native_bom: Path, output: Path) -> None:
    """Join native fitted references to the controlled part catalog, without hand edits."""
    registry = load_registry(root)
    parts = {part.id: part for part in read_model(repo_path(root, registry.catalogs.parts), PartsCatalog).parts}
    with native_bom.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        if reader.fieldnames != ["Reference", "Value", "Footprint", "PartID", "DNP"] or not rows:
            raise ValueError("Native BOM has no components or unexpected fields")
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Reference", "Value", "Footprint", "PartID", "Revision", "Manufacturer", "MPN", "Status"))
        for row in rows:
            part = parts.get(row["PartID"])
            if part is None:
                raise ValueError(f"BOM reference {row['Reference']} has no controlled PART_ID")
            writer.writerow((row["Reference"], row["Value"], row["Footprint"], part.id,
                             part.revision, part.manufacturer, part.mpn, part.status.value))


def verify_exports(root: Path, reference: EvidenceFile, source: SourceState,
                   project_id: str, manifest_path: str) -> ReleaseExportReport:
    path = evidence_path(root, reference)
    report = read_model(path, ReleaseExportReport)
    config = load_config(root, manifest_path)
    manifest = read_model(repo_path(root, manifest_path), ProjectManifest)
    verify_source(report.source, source)
    if (report.status != "PASS" or report.project_id != project_id
            or report.toolchain_id != config.toolchain_id or report.settings != manifest.release_exports):
        raise ValueError("Release exports differ from project or source settings")
    if set(report.commands) != {"version", "gerbers", "drill", "position", "bom"} or any(
        command.returncode != 0 or command.error is not None for command in report.commands.values()
    ):
        raise ValueError("Release export commands are incomplete or failed")
    if report.commands["version"].stdout.strip() != config.kicad_version:
        raise ValueError("Release exports used the wrong KiCad version")
    for name, expected in report.artifacts_sha256.items():
        if digest(repo_path(path.parent, name)) != expected:
            raise ValueError(f"Missing or changed release export: {name}")
    if not any(name.endswith(".gbr") for name in report.artifacts_sha256) or not any(
        name.endswith(".drl") for name in report.artifacts_sha256
    ) or not {"assembly/bom.csv", "assembly/positions.csv"} <= report.artifacts_sha256.keys():
        raise ValueError("Release exports lack fabrication or assembly files")
    return report
