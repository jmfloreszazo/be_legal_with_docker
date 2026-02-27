#!/usr/bin/env python3
"""Entry point for Docker Manager.

Usage:
    python -m docker_manager
    python docker_manager/__main__.py
"""

import sys

from docker_manager.cli.output import print_info
from docker_manager.core.docker import check_docker
from docker_manager.menus.menus import main_menu


def main() -> None:
    check_docker()
    main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_info("Interrupted. Goodbye!")
        sys.exit(0)
