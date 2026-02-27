"""Formatted output helpers for the terminal."""

from docker_manager.cli.colors import Colors


def print_header(title: str) -> None:
    """Print a styled section header."""
    width = 64
    print(f"\n{Colors.BLUE}{'═' * width}{Colors.NC}")
    print(f"{Colors.BLUE}  {title}{Colors.NC}")
    print(f"{Colors.BLUE}{'═' * width}{Colors.NC}\n")


def print_success(msg: str) -> None:
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_warning(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")


def print_error(msg: str) -> None:
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")


def print_info(msg: str) -> None:
    print(f"{Colors.CYAN}→ {msg}{Colors.NC}")


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a simple ASCII table with auto-sized columns."""
    if not rows:
        print_warning("No data to display.")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = "  ".join(
        f"{Colors.BOLD}{h:<{col_widths[i]}}{Colors.NC}" for i, h in enumerate(headers)
    )
    print(header_line)
    print("  ".join("─" * w for w in col_widths))

    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else 20
            cells.append(f"{str(cell):<{w}}")
        print("  ".join(cells))
