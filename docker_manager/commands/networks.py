"""Network operations: list, inspect, remove unused."""

import json

from docker_manager.cli.colors import Colors
from docker_manager.cli.input import confirm, pause
from docker_manager.cli.output import (
    print_header,
    print_success,
    print_table,
    print_warning,
)
from docker_manager.core.docker import run_docker


def list_networks() -> None:
    """List all Docker networks."""
    print_header("Docker Networks")
    result = run_docker(
        "network ls --format '{{.ID}}\t{{.Name}}\t{{.Driver}}\t{{.Scope}}'"
    )
    if not result.stdout.strip():
        print_warning("No networks found.")
        pause()
        return

    rows = [line.split("\t") for line in result.stdout.strip().split("\n")]
    print_table(["ID", "NAME", "DRIVER", "SCOPE"], rows)
    pause()


def inspect_network() -> None:
    """Inspect a network and show connected containers."""
    print_header("Inspect Network")
    result = run_docker("network ls --format '{{.ID}}\t{{.Name}}\t{{.Driver}}'")
    if not result.stdout.strip():
        print_warning("No networks found.")
        pause()
        return

    networks = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        networks.append(parts)
        print(f"  {len(networks)}) {parts[1]} ({parts[2]})")

    choice = input(f"\n{Colors.CYAN}Select network (0 to cancel): {Colors.NC}").strip()
    if not choice.isdigit() or int(choice) == 0 or int(choice) > len(networks):
        return

    net_name = networks[int(choice) - 1][1]
    print_header(f"Network: {net_name}")

    detail = run_docker(f"network inspect {net_name}")
    if detail.returncode != 0:
        return

    try:
        data = json.loads(detail.stdout)
    except json.JSONDecodeError:
        print(detail.stdout)
        pause()
        return

    if not data:
        pause()
        return

    net = data[0]
    print(f"  {Colors.BOLD}Driver:{Colors.NC}  {net.get('Driver', 'N/A')}")
    print(f"  {Colors.BOLD}Scope:{Colors.NC}   {net.get('Scope', 'N/A')}")

    ipam = net.get("IPAM", {}).get("Config", [])
    if ipam:
        print(f"  {Colors.BOLD}Subnet:{Colors.NC}  {ipam[0].get('Subnet', 'N/A')}")
        print(f"  {Colors.BOLD}Gateway:{Colors.NC} {ipam[0].get('Gateway', 'N/A')}")

    containers = net.get("Containers", {})
    print(f"\n  {Colors.BOLD}Connected Containers ({len(containers)}):{Colors.NC}")
    if containers:
        for cid, cinfo in containers.items():
            print(f"    • {cinfo.get('Name', cid[:12])} - {cinfo.get('IPv4Address', 'N/A')}")
    else:
        print(f"    {Colors.DIM}No containers connected{Colors.NC}")

    pause()


def remove_unused_networks() -> None:
    """Remove unused networks."""
    print_header("Remove Unused Networks")
    if confirm("Remove all unused networks?"):
        run_docker("network prune -f", capture=False)
        print_success("Unused networks removed.")
    pause()
