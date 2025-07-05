#!/bin/bash

# This script runs after the container is created.
# The 'set -e' command ensures that the script will exit immediately if a command fails.
set -e

echo "--- Running post-create script ---"

# Activating the virtual environment
echo "Activating virtual environment..."
source /workspaces/erasmus-gp/.venv/bin/activate

# Install Python dependencies from requirements.txt
echo "Installing requirements..."
/workspaces/erasmus-gp/.venv/bin/pip install --upgrade pip
/workspaces/erasmus-gp/.venv/bin/pip install -e ./egpcommon
/workspaces/erasmus-gp/.venv/bin/pip install -e ./egppkrapi
/workspaces/erasmus-gp/.venv/bin/pip install -e ./egppy
/workspaces/erasmus-gp/.venv/bin/pip install -e ./egpdb
/workspaces/erasmus-gp/.venv/bin/pip install -e ./egpseed
/workspaces/erasmus-gp/.venv/bin/pip install -e ./egpdbmgr

# Done
echo "--- Post-create script finished ---"