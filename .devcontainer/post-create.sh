#!/bin/bash

# This script runs after the container is created.
# The 'set -e' command ensures that the script will exit immediately if a command fails.
set -e

echo "--- Running post-create script ---"

# Create and activate virtual environment
echo "Creating and activating virtual environment..."
python3 -m venv .venv

# Install Python dependencies from requirements.txt
echo "Installing requirements..."
pip install -r ./egppkrapi/requirements.txt -r ./egppy/requirements.txt -r ./requirements.txt
pip install -e ./egpcommon
pip install -e ./egppkrapi
pip install -e ./egppy
pip install -e ./egpdb
pip install -e ./egpseed
pip install -e ./egpdbmgr

# Done
echo "--- Post-create script finished ---"