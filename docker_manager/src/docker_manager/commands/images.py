"""Image operations: list, dangling, remove."""

from docker_manager.cli.input import confirm, pause
from docker_manager.cli.output import (
    print_header,
    print_info,
    print_success,
    print_table,
    print_warning,
)
from docker_manager.core.docker import run_docker


def list_images() -> None:
    """List all Docker images."""
    print_header("Docker Images")
    result = run_docker(
        "images --format '{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}'"
    )
    if not result.stdout.strip():
        print_warning("No images found.")
        pause()
        return

    rows = [line.split("\t") for line in result.stdout.strip().split("\n")]
    print_table(["REPOSITORY", "TAG", "ID", "SIZE", "CREATED"], rows)
    pause()


def list_dangling_images() -> None:
    """List dangling (untagged) images."""
    print_header("Dangling Images (untagged)")
    result = run_docker(
        "images -f dangling=true --format '{{.ID}}\t{{.Size}}\t{{.CreatedSince}}'"
    )
    if not result.stdout.strip():
        print_warning("No dangling images.")
        pause()
        return

    rows = [line.split("\t") for line in result.stdout.strip().split("\n")]
    print_table(["ID", "SIZE", "CREATED"], rows)
    pause()


def remove_dangling_images() -> None:
    """Remove all dangling images."""
    print_header("Remove Dangling Images")
    result = run_docker("images -f dangling=true -q")
    if not result.stdout.strip():
        print_warning("No dangling images to remove.")
        pause()
        return

    count = len(result.stdout.strip().split("\n"))
    print_info(f"Found {count} dangling image(s).")

    if confirm(f"Remove {count} dangling image(s)?"):
        run_docker("image prune -f", capture=False)
        print_success("Dangling images removed.")
    pause()


def remove_all_images() -> None:
    """Remove ALL images (force)."""
    print_header("Remove ALL Images")
    result = run_docker("images -q")
    if not result.stdout.strip():
        print_warning("No images to remove.")
        pause()
        return

    count = len(set(result.stdout.strip().split("\n")))
    print_warning(f"This will remove ALL {count} image(s)!")

    if confirm("Are you sure? This cannot be undone"):
        run_docker("rmi -f $(docker images -aq)", capture=False)
        print_success("All images removed.")
    pause()
