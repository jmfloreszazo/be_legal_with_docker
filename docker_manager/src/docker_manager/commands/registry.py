"""Registry operations: list/remove images grouped by registry source."""

from docker_manager.cli.colors import console
from docker_manager.cli.input import confirm, pause
from docker_manager.cli.output import print_header, print_success, print_warning
from docker_manager.core.docker import run_docker


def _classify_registry(repo: str) -> str:
    """Determine the registry from a repository name."""
    if "/" in repo and ("." in repo.split("/")[0] or ":" in repo.split("/")[0]):
        return repo.split("/")[0]
    return "Docker Hub (default)"


def list_registry_images() -> None:
    """List images grouped by their source registry."""
    print_header("Registry Images")

    result = run_docker("images --format '{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'")
    if not result.stdout.strip():
        print_warning("No images found.")
        pause()
        return

    registries: dict[str, list[list[str]]] = {}
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        registry = _classify_registry(parts[0]) if parts else "unknown"
        registries.setdefault(registry, []).append(parts)

    for registry, images in registries.items():
        console.print(f"\n  [bold magenta]{registry}[/bold magenta]")
        console.rule(style="dim", characters="─")
        for img in images:
            tag = img[1] if len(img) > 1 else "latest"
            size = img[3] if len(img) > 3 else "?"
            console.print(f"    {img[0]}:{tag}  ({size})")

    pause()


def remove_registry_images() -> None:
    """Remove all images from a specific registry."""
    print_header("Remove Images by Registry")

    result = run_docker("images --format '{{.Repository}}:{{.Tag}}'")
    if not result.stdout.strip():
        print_warning("No images found.")
        pause()
        return

    registries: dict[str, list[str]] = {}
    for line in result.stdout.strip().split("\n"):
        repo = line.strip()
        registry = _classify_registry(repo.split(":")[0] if ":" in repo else repo)
        registries.setdefault(registry, []).append(repo)

    registry_list = list(registries.keys())
    for i, reg in enumerate(registry_list, 1):
        print(f"  {i}) {reg} ({len(registries[reg])} image(s))")

    choice = console.input("\n[cyan]Select registry (0 to cancel): [/cyan]").strip()
    if not choice.isdigit() or int(choice) == 0 or int(choice) > len(registry_list):
        return

    selected = registry_list[int(choice) - 1]
    images = registries[selected]

    print_warning(f"Will remove {len(images)} image(s) from '{selected}':")
    for img in images:
        print(f"    {img}")

    if confirm(f"\nRemove all {len(images)} image(s)?"):
        for img in images:
            run_docker(f"rmi -f {img}")
        print_success(f"All images from '{selected}' removed.")
    pause()
