"""Container operations: list, inspect, logs, stop, remove."""

import json

from docker_manager.cli.colors import Colors
from docker_manager.cli.input import confirm, pause
from docker_manager.cli.output import (
    print_header,
    print_info,
    print_success,
    print_table,
    print_warning,
)
from docker_manager.core.docker import docker_json, run_docker


def list_running_containers() -> None:
    """List all running containers with details."""
    print_header("Running Containers")
    result = run_docker(
        "ps --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"
    )
    if not result.stdout.strip():
        print_warning("No running containers.")
        pause()
        return

    rows = [line.split("\t") for line in result.stdout.strip().split("\n")]
    print_table(["ID", "NAME", "IMAGE", "STATUS", "PORTS"], rows)
    pause()


def list_all_containers() -> None:
    """List all containers (running + stopped)."""
    print_header("All Containers")
    result = run_docker(
        "ps -a --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}'"
    )
    if not result.stdout.strip():
        print_warning("No containers found.")
        pause()
        return

    rows = [line.split("\t") for line in result.stdout.strip().split("\n")]
    print_table(["ID", "NAME", "IMAGE", "STATUS", "SIZE"], rows)
    pause()


def inspect_container() -> None:
    """Inspect a specific container (ports, env, mounts, networks)."""
    print_header("Inspect Container")
    result = run_docker("ps -a --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}'")
    if not result.stdout.strip():
        print_warning("No containers found.")
        pause()
        return

    print("Available containers:")
    containers = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        containers.append(parts)
        print(f"  {len(containers)}) {parts[1]} ({parts[0][:12]}) - {parts[2]} [{parts[3]}]")

    choice = input(f"\n{Colors.CYAN}Select container number (0 to cancel): {Colors.NC}").strip()
    if not choice.isdigit() or int(choice) == 0 or int(choice) > len(containers):
        return

    container_id = containers[int(choice) - 1][0]
    container_name = containers[int(choice) - 1][1]

    print_header(f"Container: {container_name}")

    # Ports
    ports = run_docker(f"port {container_id}")
    print(f"{Colors.BOLD}Ports:{Colors.NC}")
    if ports.stdout.strip():
        for line in ports.stdout.strip().split("\n"):
            print(f"  {line}")
    else:
        print(f"  {Colors.DIM}No ports exposed{Colors.NC}")

    # Mounts
    mounts = docker_json(f"inspect --format '{{{{json .Mounts}}}}' {container_id}")
    print(f"\n{Colors.BOLD}Mounts:{Colors.NC}")
    if mounts:
        for m in mounts:
            src = m.get("Source", "N/A")
            dst = m.get("Destination", "N/A")
            mtype = m.get("Type", "N/A")
            print(f"  [{mtype}] {src} → {dst}")
    else:
        print(f"  {Colors.DIM}No mounts{Colors.NC}")

    # Environment variables
    env_result = run_docker(f"inspect --format '{{{{json .Config.Env}}}}' {container_id}")
    print(f"\n{Colors.BOLD}Environment Variables:{Colors.NC}")
    if env_result.stdout.strip():
        try:
            env_vars = json.loads(env_result.stdout.strip())
            for var in env_vars:
                print(f"  {var}")
        except json.JSONDecodeError:
            print(f"  {Colors.DIM}Unable to parse{Colors.NC}")

    # Networks
    net_result = run_docker(
        f"inspect --format '{{{{range $k, $v := .NetworkSettings.Networks}}}}"
        f"{{{{$k}}}}: {{{{$v.IPAddress}}}}{{{{\"\\n\"}}}}{{{{end}}}}' {container_id}"
    )
    print(f"\n{Colors.BOLD}Networks:{Colors.NC}")
    if net_result.stdout.strip():
        for line in net_result.stdout.strip().split("\n"):
            print(f"  {line}")

    pause()


def container_logs() -> None:
    """View logs of a container."""
    print_header("Container Logs")
    result = run_docker("ps -a --format '{{.ID}}\t{{.Names}}\t{{.Status}}'")
    if not result.stdout.strip():
        print_warning("No containers found.")
        pause()
        return

    containers = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        containers.append(parts)
        print(f"  {len(containers)}) {parts[1]} [{parts[2]}]")

    choice = input(f"\n{Colors.CYAN}Select container (0 to cancel): {Colors.NC}").strip()
    if not choice.isdigit() or int(choice) == 0 or int(choice) > len(containers):
        return

    container_id = containers[int(choice) - 1][0]
    lines = input(f"{Colors.CYAN}Number of lines (default 50): {Colors.NC}").strip()
    lines = lines if lines.isdigit() else "50"

    print()
    run_docker(f"logs --tail {lines} {container_id}", capture=False)
    pause()


def stop_all_containers() -> None:
    """Stop all running containers."""
    print_header("Stop All Containers")
    result = run_docker("ps -q")
    if not result.stdout.strip():
        print_warning("No running containers.")
        pause()
        return

    count = len(result.stdout.strip().split("\n"))
    print_info(f"Found {count} running container(s).")

    if confirm(f"Stop all {count} container(s)?"):
        run_docker("stop $(docker ps -q)", capture=False)
        print_success("All containers stopped.")
    pause()


def remove_stopped_containers() -> None:
    """Remove all stopped containers."""
    print_header("Remove Stopped Containers")
    result = run_docker("ps -a -f status=exited -f status=created -q")
    if not result.stdout.strip():
        print_warning("No stopped containers.")
        pause()
        return

    count = len(result.stdout.strip().split("\n"))
    print_info(f"Found {count} stopped container(s).")

    if confirm(f"Remove {count} stopped container(s)?"):
        run_docker("container prune -f", capture=False)
        print_success("Stopped containers removed.")
    pause()
