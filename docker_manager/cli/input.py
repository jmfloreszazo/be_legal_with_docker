"""User input helpers: pause, confirm, clear screen."""

import os

from rich.prompt import Confirm

from docker_manager.cli.colors import console


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    """Wait for the user to press Enter."""
    console.print()
    console.input("[muted]Press Enter to continue...[/muted]")


def confirm(msg: str) -> bool:
    """Ask for yes/no confirmation. Returns True only on 'y'/'yes'."""
    return Confirm.ask(f"[warning]{msg}[/warning]", default=False)
