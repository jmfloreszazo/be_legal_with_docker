"""Interactive menus for Docker Manager."""

import sys

from docker_manager.cli.colors import Colors
from docker_manager.cli.input import clear_screen
from docker_manager.cli.output import print_header, print_success
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
from docker_manager.commands.images import (
    list_dangling_images,
    list_images,
    remove_all_images,
    remove_dangling_images,
)
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
    """Generic menu loop.

    Args:
        title: Header text.
        options: List of (color, label, callback). Use None callback for 'Back'.
    """
    while True:
        clear_screen()
        print_header(title)
        for i, (color, label, _) in enumerate(options):
            print(f"  {color}{i}){Colors.NC} {label}")

        choice = input(f"\n{Colors.CYAN}Select: {Colors.NC}").strip()
        if choice == "0":
            return
        if choice.isdigit() and 1 <= int(choice) < len(options):
            _, _, action = options[int(choice)]
            if action:
                action()


def containers_menu() -> None:
    _run_menu("Containers", [
        (Colors.RED,   "Back",                                   None),
        (Colors.GREEN, "List running containers",                list_running_containers),
        (Colors.GREEN, "List all containers (running + stopped)", list_all_containers),
        (Colors.GREEN, "Inspect container (ports, env, mounts)", inspect_container),
        (Colors.GREEN, "View container logs",                    container_logs),
        (Colors.GREEN, "Stop all running containers",            stop_all_containers),
        (Colors.GREEN, "Remove stopped containers",              remove_stopped_containers),
    ])


def images_menu() -> None:
    _run_menu("Images", [
        (Colors.RED,    "Back",                      None),
        (Colors.GREEN,  "List all images",           list_images),
        (Colors.GREEN,  "List dangling images",      list_dangling_images),
        (Colors.GREEN,  "List images by registry",   list_registry_images),
        (Colors.YELLOW, "Remove dangling images",    remove_dangling_images),
        (Colors.YELLOW, "Remove images by registry", remove_registry_images),
        (Colors.RED,    "Remove ALL images",         remove_all_images),
    ])


def volumes_menu() -> None:
    _run_menu("Volumes", [
        (Colors.RED,    "Back",               None),
        (Colors.GREEN,  "List all volumes",   list_volumes),
        (Colors.YELLOW, "Remove unused volumes", remove_unused_volumes),
        (Colors.RED,    "Remove ALL volumes",    remove_all_volumes),
    ])


def networks_menu() -> None:
    _run_menu("Networks", [
        (Colors.RED,    "Back",                              None),
        (Colors.GREEN,  "List all networks",                 list_networks),
        (Colors.GREEN,  "Inspect network (connected containers)", inspect_network),
        (Colors.YELLOW, "Remove unused networks",            remove_unused_networks),
    ])


def cleanup_menu() -> None:
    _run_menu("Cleanup & Maintenance", [
        (Colors.RED,    "Back",                               None),
        (Colors.YELLOW, "Selective cleanup (pick what to remove)", selective_cleanup),
        (Colors.RED,    "FULL CLEANUP (remove everything unused)", full_cleanup),
    ])


def main_menu() -> None:
    """Top-level menu loop."""
    while True:
        clear_screen()
        print(f"""
{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   {Colors.BOLD}   🐳  Docker Manager  🐳   {Colors.BLUE}                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
""")
        print(f"  {Colors.GREEN}1){Colors.NC} Dashboard (quick overview)")
        print(f"  {Colors.GREEN}2){Colors.NC} Containers")
        print(f"  {Colors.GREEN}3){Colors.NC} Images")
        print(f"  {Colors.GREEN}4){Colors.NC} Volumes")
        print(f"  {Colors.GREEN}5){Colors.NC} Networks")
        print(f"  {Colors.GREEN}6){Colors.NC} Compose Projects")
        print(f"  {Colors.YELLOW}7){Colors.NC} Cleanup & Maintenance")
        print(f"  {Colors.RED}0){Colors.NC} Exit")

        choice = input(f"\n{Colors.CYAN}Select: {Colors.NC}").strip()
        actions = {
            "1": show_dashboard,
            "2": containers_menu,
            "3": images_menu,
            "4": volumes_menu,
            "5": networks_menu,
            "6": list_compose_projects,
            "7": cleanup_menu,
        }
        if choice == "0":
            print_success("Goodbye!")
            sys.exit(0)
        if choice in actions:
            actions[choice]()
