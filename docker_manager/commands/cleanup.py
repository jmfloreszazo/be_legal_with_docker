"""Cleanup operations: selective and full Docker system prune."""

from docker_manager.cli.colors import Colors
from docker_manager.cli.input import confirm, pause
from docker_manager.cli.output import print_header, print_info, print_success, print_warning
from docker_manager.core.docker import run_docker


def full_cleanup() -> None:
    """Nuclear option: remove everything unused."""
    print_header("FULL CLEANUP - Remove Everything")

    print_warning("This will remove:")
    print("  • All stopped containers")
    print("  • All unused networks")
    print("  • All dangling images")
    print("  • All unused volumes")
    print("  • Build cache")
    print()

    if not confirm("Proceed with full cleanup?"):
        return

    aggressive = confirm("Also remove ALL unused images (not just dangling)?")

    print()
    if aggressive:
        print_info("Running: docker system prune -a --volumes -f")
        run_docker("system prune -a --volumes -f", capture=False)
    else:
        print_info("Running: docker system prune --volumes -f")
        run_docker("system prune --volumes -f", capture=False)

    print()
    print_success("Cleanup complete.")
    pause()


_CLEANUP_OPTIONS = [
    ("Stopped containers", "container prune -f"),
    ("Dangling images", "image prune -f"),
    ("ALL unused images", "image prune -a -f"),
    ("Unused volumes", "volume prune -f"),
    ("Unused networks", "network prune -f"),
    ("Build cache", "builder prune -f"),
]


def selective_cleanup() -> None:
    """Selective cleanup with individual options."""
    print_header("Selective Cleanup")

    for i, (desc, _) in enumerate(_CLEANUP_OPTIONS, 1):
        print(f"  {i}) {desc}")

    print(f"\n  {Colors.DIM}Enter numbers separated by commas (e.g., 1,2,4){Colors.NC}")
    choices = input(f"{Colors.CYAN}Select options (0 to cancel): {Colors.NC}").strip()

    if choices == "0":
        return

    selected = []
    for c in choices.split(","):
        c = c.strip()
        if c.isdigit() and 1 <= int(c) <= len(_CLEANUP_OPTIONS):
            selected.append(_CLEANUP_OPTIONS[int(c) - 1])

    if not selected:
        print_warning("No valid options selected.")
        pause()
        return

    print_info("Will clean:")
    for desc, _ in selected:
        print(f"    • {desc}")

    if confirm("\nProceed?"):
        for desc, cmd in selected:
            print_info(f"Cleaning: {desc}...")
            run_docker(cmd, capture=False)
        print_success("Selective cleanup complete.")

    pause()
