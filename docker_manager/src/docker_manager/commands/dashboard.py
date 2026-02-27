"""Dashboard: quick overview of all Docker resources."""

from rich.table import Table

from docker_manager.cli.colors import console
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

    console.print(f"  [green]Running containers:[/green]  {len(containers_running)}")
    console.print(f"  [cyan]Total containers:[/cyan]    {len(containers_all)}")
    console.print(f"  [blue]Images:[/blue]              {len(images)}")
    console.print(f"  [magenta]Volumes:[/magenta]             {len(volumes)}")
    console.print(f"  [yellow]Networks:[/yellow]            {len(networks)}")

    if disk.returncode == 0 and disk.stdout.strip():
        tbl = Table(show_edge=False, pad_edge=True)
        tbl.add_column("Type", style="bold", min_width=16)
        tbl.add_column("Count", min_width=10)
        tbl.add_column("Size", min_width=12)
        tbl.add_column("Reclaimable", min_width=12)
        for line in disk.stdout.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) >= 4:
                tbl.add_row(parts[0], parts[1], parts[2], parts[3])
        console.print()
        console.print(tbl)

    pause()
