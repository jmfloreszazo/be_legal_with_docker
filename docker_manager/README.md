# Docker Manager

Interactive CLI tool for common Docker operations. Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output.

## Quick Start

```bash
# Easiest way — just run the script
cd docker_manager
bash run.sh
```

Or manually:

```bash
cd docker_manager
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS / WSL
pip install -r requirements.txt

# Run the tool
PYTHONPATH=src python -m docker_manager
```

## Features

| Menu | Operations |
|------|-----------|
| **Dashboard** | Quick overview: running/total containers, images, volumes, networks, disk usage |
| **Containers** | List running/all, inspect (ports, env, mounts, IPs), view logs, live tail, endpoints, env viewer, stop all, remove stopped |
| **Images** | List all, list dangling, remove dangling, remove ALL |
| **Volumes** | List all, remove unused, remove ALL |
| **Networks** | List all, inspect (connected containers, subnet, gateway), remove unused |
| **Endpoints** | Show exposed ports and accessible URLs for all running containers |
| **Live Logs** | Real-time log streaming with `docker logs --follow` (Ctrl+C to stop) |
| **Registry** | List images grouped by registry source, remove images by registry |
| **Compose** | List running Docker Compose v2 projects |
| **Cleanup** | Selective cleanup (pick resources) or full `docker system prune` |

## Project Structure

```text
docker_manager/
├── pyproject.toml             # Package metadata & dependencies
├── requirements.txt           # Pip dependencies
├── run.sh                     # One-command launcher
├── README.md
└── src/
    └── docker_manager/
        ├── __init__.py
        ├── __main__.py          # Entry point
        ├── cli/
        │   ├── colors.py        # Rich console & theme
        │   ├── output.py        # Panels, tables, styled messages
        │   └── input.py         # pause, confirm, clear_screen
        ├── core/
        │   └── docker.py        # run_docker, docker_json, check_docker
        ├── commands/
        │   ├── dashboard.py     # Resource overview
        │   ├── containers.py    # Container operations
        │   ├── images.py        # Image operations
        │   ├── volumes.py       # Volume operations
        │   ├── networks.py      # Network operations
        │   ├── endpoints.py     # Exposed ports, URLs, container env
        │   ├── livelogs.py      # Real-time log streaming
        │   ├── registry.py      # Registry grouping & removal
        │   ├── compose.py       # Compose project listing
        │   └── cleanup.py       # Selective & full prune
        └── menus/
            └── menus.py         # Interactive menu navigation
```

### Architecture

| Layer | Responsibility |
|-------|---------------|
| `cli/` | Presentation — colors, formatted output, user input |
| `core/` | Infrastructure — Docker CLI execution |
| `commands/` | Business logic — one module per resource type |
| `menus/` | Navigation — menu rendering and routing |

## Requirements

- Python 3.10+
- Docker CLI installed and daemon running (WSL2 or native Linux)
- `rich>=13.0` (installed via `pip install -r requirements.txt`)

## Cross-Platform Support

Docker Manager works from both **WSL2** and **Windows PowerShell**:

| Environment | How it works |
|-------------|-------------|
| WSL2 / Linux | Calls `docker` directly |
| Windows PowerShell | Routes commands via `wsl docker` automatically |

When running from PowerShell, Docker Manager detects the Windows environment and
prefixes all Docker commands with `wsl` so the Docker daemon inside WSL2 is used
transparently.

## Usage Examples

```bash
# From the docker_manager directory (WSL / Linux)
PYTHONPATH=src python -m docker_manager

# Or use the launcher script
bash run.sh
```

```powershell
# From Windows PowerShell
cd docker_manager
$env:PYTHONPATH="src"
python -m docker_manager
```

## Destructive Operations

All destructive actions (remove, prune) require explicit confirmation before executing. The cleanup menu supports:

- **Selective cleanup** — pick individual resource types to prune
- **Full cleanup** — `docker system prune --volumes` with optional `-a` flag

## License

MIT
