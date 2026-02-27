"""Endpoint discovery: show exposed ports and accessible URLs for running containers."""

import json

from rich.table import Table

from docker_manager.cli.colors import console
from docker_manager.cli.input import pause
from docker_manager.cli.output import print_header, print_warning
from docker_manager.core.docker import run_docker


def _build_url(host_binding: dict, container_port: str) -> str:
    """Build a clickable URL from a host port binding."""
    host_ip = host_binding.get("HostIp", "0.0.0.0")
    host_port = host_binding.get("HostPort", "")
    if not host_port:
        return ""
    if host_ip in ("0.0.0.0", "::"):
        host_ip = "localhost"
    scheme = "https" if container_port.startswith("443") else "http"
    return f"{scheme}://{host_ip}:{host_port}"


def show_endpoints() -> None:
    """Show all exposed endpoints (ports/URLs) for running containers."""
    print_header("Exposed Endpoints")

    result = run_docker("ps -q")
    if not result.stdout.strip():
        print_warning("No running containers.")
        pause()
        return

    container_ids = result.stdout.strip().split("\n")

    tbl = Table(show_header=True, header_style="bold cyan", border_style="dim",
                pad_edge=True, expand=False)
    tbl.add_column("Container", style="bold")
    tbl.add_column("Image", style="dim")
    tbl.add_column("Port", style="cyan")
    tbl.add_column("URL", style="green")
    tbl.add_column("Status", style="dim")

    found_any = False

    for cid in container_ids:
        inspect_result = run_docker(
            f"inspect --format '{{{{json .}}}}' {cid}"
        )
        if inspect_result.returncode != 0 or not inspect_result.stdout.strip():
            continue

        try:
            data = json.loads(inspect_result.stdout.strip())
        except json.JSONDecodeError:
            continue

        name = data.get("Name", "").lstrip("/")
        image = data.get("Config", {}).get("Image", "N/A")
        status = data.get("State", {}).get("Status", "unknown")
        ports = data.get("NetworkSettings", {}).get("Ports", {})

        if not ports:
            tbl.add_row(name, image, "[dim]none[/dim]", "[dim]--[/dim]", status)
            found_any = True
            continue

        first = True
        for container_port, bindings in ports.items():
            if bindings:
                for binding in bindings:
                    url = _build_url(binding, container_port)
                    host_port = binding.get("HostPort", "")
                    port_display = f"{host_port} -> {container_port}"
                    tbl.add_row(
                        name if first else "",
                        image if first else "",
                        port_display,
                        f"[link={url}]{url}[/link]" if url else "--",
                        status if first else "",
                    )
                    first = False
                    found_any = True
            else:
                tbl.add_row(
                    name if first else "",
                    image if first else "",
                    container_port,
                    "[dim]not published[/dim]",
                    status if first else "",
                )
                first = False
                found_any = True

    if found_any:
        console.print(tbl)
    else:
        print_warning("No endpoints found.")

    pause()


def show_container_env() -> None:
    """Show environment variables for a selected running container."""
    print_header("Container Environment")

    result = run_docker(
        "ps --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Ports}}'"
    )
    if not result.stdout.strip():
        print_warning("No running containers.")
        pause()
        return

    containers = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        containers.append(parts)
        ports_info = parts[3] if len(parts) > 3 and parts[3] else "no ports"
        console.print(f"  {len(containers)}) [bold]{parts[1]}[/bold]  [dim]{parts[2]}[/dim]  [cyan]{ports_info}[/cyan]")

    choice = console.input("\n[cyan]Select container (0 to cancel): [/cyan]").strip()
    if not choice.isdigit() or int(choice) == 0 or int(choice) > len(containers):
        return

    cid = containers[int(choice) - 1][0]
    name = containers[int(choice) - 1][1]

    env_result = run_docker(f"inspect --format '{{{{json .Config.Env}}}}' {cid}")
    print_header(f"Env: {name}")

    if env_result.stdout.strip():
        try:
            env_vars = json.loads(env_result.stdout.strip())
            tbl = Table(show_header=True, header_style="bold cyan", border_style="dim",
                        pad_edge=True, expand=False)
            tbl.add_column("Variable", style="bold")
            tbl.add_column("Value")
            for var in sorted(env_vars):
                if "=" in var:
                    k, v = var.split("=", 1)
                    tbl.add_row(k, v)
                else:
                    tbl.add_row(var, "")
            console.print(tbl)
        except json.JSONDecodeError:
            console.print("  [dim]Unable to parse environment[/dim]")
    else:
        console.print("  [dim]No environment variables[/dim]")

    pause()
