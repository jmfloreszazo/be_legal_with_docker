"""Live log streaming: follow container logs in real time."""

from docker_manager.cli.colors import console
from docker_manager.cli.input import pause
from docker_manager.cli.output import print_header, print_info, print_warning
from docker_manager.core.docker import run_docker


def live_logs() -> None:
    """Follow container logs in real time (Ctrl+C to stop)."""
    print_header("Live Logs (follow mode)")

    result = run_docker(
        "ps --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}'"
    )
    if not result.stdout.strip():
        print_warning("No running containers.")
        pause()
        return

    containers = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        containers.append(parts)
        console.print(
            f"  {len(containers)}) [bold]{parts[1]}[/bold]  "
            f"[dim]{parts[2]}[/dim]  [cyan]{parts[3]}[/cyan]"
        )

    choice = console.input("\n[cyan]Select container (0 to cancel): [/cyan]").strip()
    if not choice.isdigit() or int(choice) == 0 or int(choice) > len(containers):
        return

    cid = containers[int(choice) - 1][0]
    name = containers[int(choice) - 1][1]

    tail = console.input(
        "[cyan]Initial lines to show (default 100): [/cyan]"
    ).strip()
    tail = tail if tail.isdigit() else "100"

    console.print()
    print_info(f"Following logs for [bold]{name}[/bold]  --  press Ctrl+C to stop")
    console.rule(style="dim")
    console.print()

    try:
        run_docker(f"logs --follow --tail {tail} {cid}", capture=False)
    except KeyboardInterrupt:
        console.print()
        print_info("Log stream stopped.")

    pause()
