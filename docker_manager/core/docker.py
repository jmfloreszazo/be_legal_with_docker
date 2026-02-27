"""Docker command execution and pre-flight checks.

Supports running natively on Linux / WSL and also from Windows PowerShell
by routing commands through ``wsl docker`` when Docker CLI is not installed
locally on Windows.
"""

import json
import os
import shutil
import subprocess
import sys

from docker_manager.cli.output import print_error, print_info


def _is_windows() -> bool:
    return os.name == "nt"


def _docker_prefix() -> str:
    """Return the command prefix to reach the Docker CLI.

    On Linux / WSL          -> "docker"
    On Windows with docker  -> "docker"
    On Windows without it   -> "wsl docker"
    """
    if _is_windows() and not shutil.which("docker"):
        return "wsl docker"
    return "docker"


def run_cmd(
    cmd: str, capture: bool = True, check: bool = False
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd, shell=True, capture_output=capture, text=True, check=check
    )


def run_docker(args: str, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a docker CLI command (auto-detects Windows vs Linux)."""
    prefix = _docker_prefix()
    return run_cmd(f"{prefix} {args}", capture=capture)


def docker_json(args: str) -> list:
    """Run a docker command that returns JSON and parse it."""
    result = run_docker(args)
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def check_docker() -> None:
    """Verify that Docker is reachable and the daemon is running.

    On Windows without Docker CLI, falls back to ``wsl docker``.
    """
    prefix = _docker_prefix()

    # Quick connectivity test
    if _is_windows() and prefix.startswith("wsl"):
        # Ensure WSL itself is available
        if not shutil.which("wsl"):
            print_error("Neither Docker CLI nor WSL found on this system.")
            sys.exit(1)
    elif not shutil.which("docker"):
        print_error("Docker is not installed or not in PATH.")
        sys.exit(1)

    result = run_docker("info")
    if result.returncode != 0:
        print_error("Docker daemon is not running.")
        if _is_windows():
            print_info("Start Docker Desktop or run in WSL: sudo service docker start")
        else:
            print_info("Start the daemon: sudo service docker start")
        sys.exit(1)
