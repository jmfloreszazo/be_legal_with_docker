"""Volume operations: list, remove unused, remove all."""

from docker_manager.cli.input import confirm, pause
from docker_manager.cli.output import (
    print_header,
    print_success,
    print_table,
    print_warning,
)
from docker_manager.core.docker import run_docker


def list_volumes() -> None:
    """List all Docker volumes."""
    print_header("Docker Volumes")
    result = run_docker(
        "volume ls --format '{{.Name}}\t{{.Driver}}\t{{.Mountpoint}}'"
    )
    if not result.stdout.strip():
        print_warning("No volumes found.")
        pause()
        return

    rows = [line.split("\t") for line in result.stdout.strip().split("\n")]
    print_table(["NAME", "DRIVER", "MOUNTPOINT"], rows)
    pause()


def remove_unused_volumes() -> None:
    """Remove all unused volumes."""
    print_header("Remove Unused Volumes")
    result = run_docker("volume ls -f dangling=true -q")
    if not result.stdout.strip():
        print_warning("No unused volumes.")
        pause()
        return

    count = len(result.stdout.strip().split("\n"))
    print_warning(f"Found {count} unused volume(s).")

    if confirm(f"Remove {count} unused volume(s)? Data will be lost!"):
        run_docker("volume prune -f", capture=False)
        print_success("Unused volumes removed.")
    pause()


def remove_all_volumes() -> None:
    """Remove ALL volumes (force)."""
    print_header("Remove ALL Volumes")
    result = run_docker("volume ls -q")
    if not result.stdout.strip():
        print_warning("No volumes to remove.")
        pause()
        return

    count = len(result.stdout.strip().split("\n"))
    print_warning(f"This will remove ALL {count} volume(s) and their data!")

    if confirm("Are you absolutely sure? ALL DATA WILL BE LOST"):
        run_docker("volume rm -f $(docker volume ls -q)", capture=False)
        print_success("All volumes removed.")
    pause()
