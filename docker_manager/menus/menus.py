"""Interactive menus for Docker Manager."""

import sys

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from docker_manager.cli.colors import console
from docker_manager.cli.input import clear_screen
from docker_manager.cli.output import print_header
from docker_manager.commands.cleanup import full_cleanup, selective_cleanup
from docker_manager.commands.compose import list_compose_projects
from docker_manager.commands.containers import (
    container_logs,
    inspect_container,
    list_all_containers,
    list_running_containers,
    remove_stopped_containers,
    stop_all_containers,
)
from docker_manager.commands.dashboard import show_dashboard
from docker_manager.commands.endpoints import show_container_env, show_endpoints
from docker_manager.commands.images import (
    list_dangling_images,
    list_images,
    remove_all_images,
    remove_dangling_images,
)
from docker_manager.commands.livelogs import live_logs
from docker_manager.commands.networks import (
    inspect_network,
    list_networks,
    remove_unused_networks,
)
from docker_manager.commands.registry import list_registry_images, remove_registry_images
from docker_manager.commands.volumes import (
    list_volumes,
    remove_all_volumes,
    remove_unused_volumes,
)


def _run_menu(title: str, options: list[tuple[str, str, callable]]) -> None:
    """Generic submenu loop using Rich.

    Args:
        title: Header text.
        options: List of (style, label, callback). Use None callback for 'Back'.
    """
    while True:
        clear_screen()
        print_header(title)
        for i, (style, label, _) in enumerate(options):
            console.print(f"  [{style}]{i})[/{style}] {label}")

        choice = console.input("\n[info]Select: [/info]").strip()
        if choice == "0":
            return
        if choice.isdigit() and 1 <= int(choice) < len(options):
            _, _, action = options[int(choice)]
            if action:
                action()


def containers_menu() -> None:
    _run_menu("Containers", [
        ("error",   "Back",                                   None),
        ("success", "List running containers",                list_running_containers),
        ("success", "List all containers (running + stopped)", list_all_containers),
        ("success", "Inspect container (ports, env, mounts)", inspect_container),
        ("success", "View container logs",                    container_logs),
        ("success", "Live tail logs (follow mode)",           live_logs),
        ("success", "Show exposed endpoints / URLs",          show_endpoints),
        ("success", "Show container environment",             show_container_env),
        ("success", "Stop all running containers",            stop_all_containers),
        ("success", "Remove stopped containers",              remove_stopped_containers),
    ])


def images_menu() -> None:
    _run_menu("Images", [
        ("error",   "Back",                      None),
        ("success", "List all images",           list_images),
        ("success", "List dangling images",      list_dangling_images),
        ("success", "List images by registry",   list_registry_images),
        ("warning", "Remove dangling images",    remove_dangling_images),
        ("warning", "Remove images by registry", remove_registry_images),
        ("error",   "Remove ALL images",         remove_all_images),
    ])


def volumes_menu() -> None:
    _run_menu("Volumes", [
        ("error",   "Back",                  None),
        ("success", "List all volumes",      list_volumes),
        ("warning", "Remove unused volumes", remove_unused_volumes),
        ("error",   "Remove ALL volumes",    remove_all_volumes),
    ])


def networks_menu() -> None:
    _run_menu("Networks", [
        ("error",   "Back",                                  None),
        ("success", "List all networks",                     list_networks),
        ("success", "Inspect network (connected containers)", inspect_network),
        ("warning", "Remove unused networks",                remove_unused_networks),
    ])


def cleanup_menu() -> None:
    _run_menu("Cleanup & Maintenance", [
        ("error",   "Back",                                   None),
        ("warning", "Selective cleanup (pick what to remove)", selective_cleanup),
        ("error",   "FULL CLEANUP (remove everything unused)", full_cleanup),
    ])


def _docker_status() -> Text:
    """Check if Docker daemon is reachable. Returns a Rich Text object."""
    try:
        from docker_manager.core.docker import run_docker
        result = run_docker("info --format '{{.ServerVersion}}'")
        if result.stdout and result.stdout.strip() and result.returncode == 0:
            ver = result.stdout.strip()
            txt = Text()
            txt.append("● ", style="bold green")
            txt.append("online", style="green")
            txt.append(f"  v{ver}", style="dim")
            return txt
    except Exception:
        pass
    txt = Text()
    txt.append("● ", style="bold red")
    txt.append("offline", style="red")
    return txt


def main_menu() -> None:
    """Top-level menu loop."""
    while True:
        clear_screen()
        status = _docker_status()

        # --- Build the banner ---
        logo = Text()
        logo.append("  ██████╗  ██╗   ██╗\n", style="bold cyan")
        logo.append("  ██╔══██╗ ███╗ ███║", style="bold cyan")
        logo.append("   Docker Manager\n", style="bold white")
        logo.append("  ██║  ██║ ████████║", style="bold cyan")
        logo.append("   Interactive CLI\n", style="dim")
        logo.append("  ██████╔╝ ██╔██╔██║\n", style="bold cyan")
        logo.append("  ╚═════╝  ╚═╝╚═╝╚═╝\n", style="bold cyan")

        banner = Text()
        banner.append_text(logo)
        banner.append("  Daemon: ", style="dim")
        banner.append_text(status)
        banner.append("\n\n")
        banner.append("  Jose Maria Flores Zazo", style="bold white")
        banner.append("  ", style="dim")
        banner.append("https://jmfloreszazo.com", style="cyan underline")

        console.print()
        console.print(Panel(banner, border_style="cyan", width=58, padding=(1, 2)))

        # --- Menu items ---
        menu = Table(show_header=False, show_edge=False, show_lines=False,
                     pad_edge=False, box=None, padding=(0, 1))
        menu.add_column(style="cyan", width=4, justify="right")
        menu.add_column(min_width=28)
        menu.add_column(style="dim")

        menu.add_row(" 1", "Dashboard",          "resource overview")
        menu.add_row(" 2", "Containers",         "list, inspect, stop, remove")
        menu.add_row(" 3", "Images",             "list, prune, registry")
        menu.add_row(" 4", "Volumes",            "persistent storage")
        menu.add_row(" 5", "Networks",           "connectivity and routing")
        menu.add_row(" 6", "Endpoints",          "exposed ports and URLs")
        menu.add_row(" 7", "Live Logs",          "real-time log streaming")
        menu.add_row(" 8", "Compose Projects",   "multi-container stacks")
        menu.add_row(" 9", "Cleanup",            "reclaim disk space")
        menu.add_row()
        menu.add_row("[dim] 0[/dim]", "[dim]Exit[/dim]", "")

        console.print(menu)
        console.print()
        console.rule(style="dim cyan")
        choice = console.input("  [bold white]>[/bold white] ").strip()

        actions = {
            "1": show_dashboard,
            "2": containers_menu,
            "3": images_menu,
            "4": volumes_menu,
            "5": networks_menu,
            "6": show_endpoints,
            "7": live_logs,
            "8": list_compose_projects,
            "9": cleanup_menu,
        }
        if choice == "0":
            clear_screen()
            console.print("\n  [cyan]Goodbye.[/cyan]\n")
            sys.exit(0)
        if choice in actions:
            actions[choice]()
