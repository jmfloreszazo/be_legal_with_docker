"""Dashboard: quick overview of all Docker resources."""

from docker_manager.cli.colors import Colors
from docker_manager.cli.input import pause
from docker_manager.cli.output import print_header
from docker_manager.core.docker import run_docker


def show_dashboard() -> None:
    """Show a quick overview of all Docker resources."""
    print_header("Docker Dashboard")

    containers_running = [c for c in run_docker("ps -q").stdout.strip().split("\n") if c]
    containers_all = [c for c in run_docker("ps -aq").stdout.strip().split("\n") if c]
    images = [i for i in run_docker("images -q").stdout.strip().split("\n") if i]
    volumes = [v for v in run_docker("volume ls -q").stdout.strip().split("\n") if v]
    networks = [n for n in run_docker("network ls -q").stdout.strip().split("\n") if n]

    disk = run_docker(
        "system df --format '{{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}'"
    )

    print(f"  {Colors.GREEN}Running containers:{Colors.NC}  {len(containers_running)}")
    print(f"  {Colors.CYAN}Total containers:{Colors.NC}    {len(containers_all)}")
    print(f"  {Colors.BLUE}Images:{Colors.NC}              {len(images)}")
    print(f"  {Colors.MAGENTA}Volumes:{Colors.NC}             {len(volumes)}")
    print(f"  {Colors.YELLOW}Networks:{Colors.NC}            {len(networks)}")

    if disk.returncode == 0 and disk.stdout.strip():
        print(f"\n  {Colors.BOLD}Disk Usage:{Colors.NC}")
        print(f"  {'Type':<16} {'Count':<10} {'Size':<12} {'Reclaimable':<12}")
        print(f"  {'─' * 16} {'─' * 10} {'─' * 12} {'─' * 12}")
        for line in disk.stdout.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) >= 4:
                print(f"  {parts[0]:<16} {parts[1]:<10} {parts[2]:<12} {parts[3]:<12}")

    pause()
