#!/bin/bash
cd "$(dirname "$0")"

# Create venv if missing
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Ensure Docker is running
sudo service docker start 2>/dev/null

# Launch
PYTHONPATH=src python -m docker_manager
