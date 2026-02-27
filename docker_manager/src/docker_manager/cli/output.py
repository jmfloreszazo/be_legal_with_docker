"""Formatted output helpers using Rich."""

from rich.panel import Panel
from rich.table import Table

from docker_manager.cli.colors import console


def print_header(title: str) -> None:
    """Print a styled section header inside a panel."""
    console.print()
    console.print(Panel(f"[header]{title}[/header]", border_style="cyan", width=62))
    console.print()


def print_success(msg: str) -> None:
    console.print(f"[success]✓ {msg}[/success]")


def print_warning(msg: str) -> None:
    console.print(f"[warning]⚠ {msg}[/warning]")


def print_error(msg: str) -> None:
    console.print(f"[error]✗ {msg}[/error]")


def print_info(msg: str) -> None:
    console.print(f"[info]→ {msg}[/info]")


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a rich formatted table."""
    if not rows:
        print_warning("No data to display.")
        return

    table = Table(show_header=True, header_style="bold cyan", border_style="dim",
                  show_lines=False, pad_edge=True, expand=False)

    for h in headers:
        table.add_column(h)

    for row in rows:
        table.add_row(*[str(c) for c in row])

    console.print(table)
