#!/bin/bash

# This script runs after the container is created.
# The 'set -e' command ensures that the script will exit immediately if a command fails.
set -e

echo "--- Running post-create script ---"

# Activating the virtual environment
echo "Creating virtual environment..."
python3 -m venv /workspace/erasmus-gp/.venv

# Install Python dependencies from requirements.txt
echo "Installing requirements..."
/workspaces/erasmus-gp/.venv/bin/pip install --upgrade pip
find . -name "requirements.txt" -exec ./.venv/bin/pip install -r {} \;
/workspace/erasmus-gp/.venv/bin/pip install -e ./egpcommon
/workspace/erasmus-gp/.venv/bin/pip install -e ./egppkrapi
/workspace/erasmus-gp/.venv/bin/pip install -e ./egppy
/workspace/erasmus-gp/.venv/bin/pip install -e ./egpdb
/workspace/erasmus-gp/.venv/bin/pip install -e ./egpseed
/workspace/erasmus-gp/.venv/bin/pip install -e ./egpdbmgr

# Done
echo "--- Post-create script finished ---"
