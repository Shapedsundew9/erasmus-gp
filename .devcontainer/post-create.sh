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
pip install --upgrade pip
pip install -e ./egpcommon
pip install -e ./egppkrapi
pip install -e ./egppy
pip install -e ./egpdb
pip install -e ./egpseed
pip install -e ./egpdbmgr

# Done
echo "--- Post-create script finished ---"