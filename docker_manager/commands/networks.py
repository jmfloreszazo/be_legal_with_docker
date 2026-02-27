"""Network operations: list, inspect, remove unused."""

import json

from docker_manager.cli.colors import console
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

    choice = console.input("\n[cyan]Select network (0 to cancel): [/cyan]").strip()
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
        console.print(detail.stdout)
        pause()
        return

    if not data:
        pause()
        return

    net = data[0]
    console.print(f"  [bold]Driver:[/bold]  {net.get('Driver', 'N/A')}")
    console.print(f"  [bold]Scope:[/bold]   {net.get('Scope', 'N/A')}")

    ipam = net.get("IPAM", {}).get("Config", [])
    if ipam:
        console.print(f"  [bold]Subnet:[/bold]  {ipam[0].get('Subnet', 'N/A')}")
        console.print(f"  [bold]Gateway:[/bold] {ipam[0].get('Gateway', 'N/A')}")

    containers = net.get("Containers", {})
    console.print(f"\n  [bold]Connected Containers ({len(containers)}):[/bold]")
    if containers:
        for cid, cinfo in containers.items():
            console.print(f"    • {cinfo.get('Name', cid[:12])} - {cinfo.get('IPv4Address', 'N/A')}")
    else:
        console.print("    [dim]No containers connected[/dim]")

    pause()


def remove_unused_networks() -> None:
    """Remove unused networks."""
    print_header("Remove Unused Networks")
    if confirm("Remove all unused networks?"):
        run_docker("network prune -f", capture=False)
        print_success("Unused networks removed.")
    pause()
