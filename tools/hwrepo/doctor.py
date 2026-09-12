"""Read-only environment diagnostics for adopting and checking the template."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from tools.check_toolchain import assessment, observed_version, toolchain

from .models import EnvironmentCheck, TemplateDoctorReport
from .template import preflight

MINIMUM_PYTHON = (3, 12)


def command_output(argv: tuple[str, ...]) -> str | None:
    """Return concise successful command output without exposing interactive prompts."""
    try:
        result = subprocess.run(
            argv, text=True, capture_output=True, check=False, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    output = result.stdout.strip() or result.stderr.strip()
    return output.splitlines()[0] if result.returncode == 0 and output else None


def environment_check(
    identifier: str,
    required: bool,
    expected: str,
    observed: str | None,
    success: bool,
    success_action: str,
    failure_action: str,
) -> EnvironmentCheck:
    """Create one stable diagnostic row with required/optional failure semantics."""
    status = "PASS" if success else ("FAIL" if required else "OPTIONAL")
    return EnvironmentCheck(
        id=identifier,
        required=required,
        status=status,
        expected=expected,
        observed=observed,
        next_action=success_action if success else failure_action,
    )


def doctor(
    root: Path,
    native: bool = False,
    toolchain_id: str | None = None,
    cli: str = "kicad-cli",
) -> TemplateDoctorReport:
    """Inspect prerequisites; native mode accepts Docker or one exact local KiCad CLI."""
    resolved = root.resolve()
    checks: list[EnvironmentCheck] = []

    python_version = ".".join(str(value) for value in sys.version_info[:3])
    python_ok = sys.version_info[:2] >= MINIMUM_PYTHON
    checks.append(environment_check(
        "python", True, "Python 3.12 or newer", python_version, python_ok,
        "Python can run the supported policy tools.",
        "Install Python 3.12 or newer, recreate the virtual environment, and reinstall .[dev].",
    ))

    git_path = shutil.which("git")
    git_version = None if git_path is None else command_output((git_path, "--version"))
    checks.append(environment_check(
        "git", True, "Git available on PATH", git_version, git_version is not None,
        "Git is available for source and release provenance.",
        "Install Git and make it available on PATH.",
    ))
    git_repository = None if git_path is None else command_output(
        (
            git_path,
            "-c",
            f"safe.directory={resolved.as_posix()}",
            "-C",
            str(resolved),
            "rev-parse",
            "--is-inside-work-tree",
        )
    )
    checks.append(environment_check(
        "git-repository", True, "Repository is inside a Git worktree", git_repository,
        git_repository == "true", "The repository can record source provenance.",
        "Initialize or clone the Git repository before using the guided adoption command.",
    ))

    template = preflight(resolved)
    checks.append(environment_check(
        "template", True, "Complete template contract", template.template_version,
        template.status == "PASS", "The template contract is complete.",
        "Run tools.template preflight and repair the reported missing or invalid template input.",
    ))

    docker_path = shutil.which("docker")
    docker_version = None if docker_path is None else command_output(
        (docker_path, "version", "--format", "{{.Server.Version}}")
    )

    local_version: str | None = None
    local_ok = False
    expected_local = "Optional exact local KiCad CLI"
    if toolchain_id is not None:
        try:
            record = toolchain(resolved, toolchain_id)
            checks.append(environment_check(
                "toolchain", True, f"One catalogued {toolchain_id} record", record.kicad_version,
                True, "The selected toolchain is catalogued.",
                "Select a toolchain ID from catalog/toolchains.json.",
            ))
            local_version = observed_version(cli)
            local_ok = assessment(record, local_version).status == "PASS"
            expected_local = f"KiCad {record.kicad_version} for {toolchain_id}"
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            checks.append(environment_check(
                "toolchain", True, f"One catalogued {toolchain_id} record", str(exc),
                False, "The selected toolchain is catalogued.",
                "Select a toolchain ID from catalog/toolchains.json.",
            ))

    native_ok = docker_version is not None or local_ok
    checks.append(environment_check(
        "docker", False, "Running Docker daemon for digest-pinned native checks",
        docker_version, docker_version is not None,
        "Docker can run the catalogued KiCad images.",
        "Start Docker, or select an exact installed KiCad CLI with --toolchain and --cli.",
    ))
    checks.append(environment_check(
        "kicad-cli", False, expected_local, local_version, local_ok,
        "The installed KiCad CLI matches the selected toolchain.",
        "This is optional when Docker is available; otherwise install the selected exact KiCad version.",
    ))
    if native:
        checks.append(environment_check(
            "native-runner", True, "Running Docker or an exact selected KiCad CLI",
            "docker" if docker_version is not None else ("kicad-cli" if local_ok else None),
            native_ok, "Native checks can run on this machine.",
            "Start Docker or pass --toolchain with a matching --cli executable.",
        ))

    failed = tuple(check for check in checks if check.status == "FAIL")
    return TemplateDoctorReport(
        native_requested=native,
        checks=tuple(checks),
        status="FAIL" if failed else "PASS",
        next_actions=tuple(dict.fromkeys(check.next_action for check in failed)),
    )
