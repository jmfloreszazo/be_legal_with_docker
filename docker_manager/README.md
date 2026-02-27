# Docker Manager

Interactive CLI tool for common Docker operations. No dependencies required — pure Python 3.

## Quick Start

```bash
python -m docker_manager
```

## Features

| Menu | Operations |
|------|-----------|
| **Dashboard** | Quick overview: running/total containers, images, volumes, networks, disk usage |
| **Containers** | List running/all, inspect (ports, env, mounts, IPs), view logs, stop all, remove stopped |
| **Images** | List all, list dangling, remove dangling, remove ALL |
| **Volumes** | List all, remove unused, remove ALL |
| **Networks** | List all, inspect (connected containers, subnet, gateway), remove unused |
| **Registry** | List images grouped by registry source, remove images by registry |
| **Compose** | List running Docker Compose v2 projects |
| **Cleanup** | Selective cleanup (pick resources) or full `docker system prune` |

## Project Structure

```
docker_manager/
├── __init__.py
├── __main__.py              # Entry point
├── cli/
│   ├── colors.py            # ANSI color constants
│   ├── output.py            # print_header, print_table, print_success, ...
│   └── input.py             # pause, confirm, clear_screen
├── core/
│   └── docker.py            # run_docker, docker_json, check_docker
├── commands/
│   ├── dashboard.py         # Resource overview
│   ├── containers.py        # Container operations
│   ├── images.py            # Image operations
│   ├── volumes.py           # Volume operations
│   ├── networks.py          # Network operations
│   ├── registry.py          # Registry grouping & removal
│   ├── compose.py           # Compose project listing
│   └── cleanup.py           # Selective & full prune
└── menus/
    └── menus.py              # Interactive menu navigation
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
- Docker CLI installed and daemon running

## Usage Examples

```bash
# Run from the parent directory
python -m docker_manager

# Or directly
python docker_manager/__main__.py
```

## Destructive Operations

All destructive actions (remove, prune) require explicit confirmation before executing. The cleanup menu supports:

- **Selective cleanup** — pick individual resource types to prune
- **Full cleanup** — `docker system prune --volumes` with optional `-a` flag

## License

MIT
