"""Docker command execution and pre-flight checks."""

import json
import shutil
import subprocess
import sys

from docker_manager.cli.output import print_error, print_info


def run_cmd(
    cmd: str, capture: bool = True, check: bool = False
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd, shell=True, capture_output=capture, text=True, check=check
    )


def run_docker(args: str, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a docker CLI command."""
    return run_cmd(f"docker {args}", capture=capture)


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
    """Verify that Docker is installed and the daemon is running."""
    if not shutil.which("docker"):
        print_error("Docker is not installed or not in PATH.")
        sys.exit(1)
    result = run_docker("info")
    if result.returncode != 0:
        print_error("Docker daemon is not running.")
        print_info("Start Docker Desktop or run: sudo service docker start")
        sys.exit(1)
