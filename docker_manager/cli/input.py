"""User input helpers: pause, confirm, clear screen."""

import os

from docker_manager.cli.colors import Colors


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    """Wait for the user to press Enter."""
    print()
    input(f"{Colors.DIM}Press Enter to continue...{Colors.NC}")


def confirm(msg: str) -> bool:
    """Ask for yes/no confirmation. Returns True only on 'y'/'yes'."""
    answer = input(f"{Colors.YELLOW}{msg} (y/N): {Colors.NC}").strip().lower()
    return answer in ("y", "yes")
