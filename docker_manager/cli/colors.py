"""Shared Rich console instance."""

from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "header": "bold cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "cyan",
    "muted": "dim",
    "accent": "magenta",
    "key": "bold white",
})

console = Console(theme=theme, highlight=False)
