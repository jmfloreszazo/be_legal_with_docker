"""Docker Compose project listing."""

import json

from docker_manager.cli.input import pause
from docker_manager.cli.output import print_header, print_table, print_warning
from docker_manager.core.docker import run_cmd


def list_compose_projects() -> None:
    """List running Docker Compose projects."""
    print_header("Docker Compose Projects")

    result = run_cmd("docker compose ls --format json")
    if result.returncode != 0 or not result.stdout.strip():
        print_warning("Docker Compose v2 not available or no projects found.")
        pause()
        return

    try:
        projects = json.loads(result.stdout)
    except json.JSONDecodeError:
        print_warning("Unable to parse Compose projects.")
        pause()
        return

    if not projects:
        print_warning("No Compose projects running.")
        pause()
        return

    rows = [
        [p.get("Name", ""), p.get("Status", ""), p.get("ConfigFiles", "")]
        for p in projects
    ]
    print_table(["NAME", "STATUS", "CONFIG FILES"], rows)
    pause()
