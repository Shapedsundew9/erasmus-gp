#!/bin/bash

# This script runs after the container is created.
# The 'set -e' command ensures that the script will exit immediately if a command fails.
set -e

echo "--- Running post-create script ---"

# Activating the virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Install Python dependencies from requirements.txt
echo "Installing requirements..."
.venv/bin/pip install --upgrade pip
find . -name "requirements.txt" -exec ./.venv/bin/pip install -r {} \;
.venv/bin/pip install -e ./egpcommon
.venv/bin/pip install -e ./egppkrapi
.venv/bin/pip install -e ./egppy
.venv/bin/pip install -e ./egpdb
.venv/bin/pip install -e ./egpseed
.venv/bin/pip install -e ./egpdbmgr

# Pre-Push Hooks script
chmod +x .devcontainer/pre-push-hooks.sh
./.devcontainer/pre-push-hooks.sh

# Generate data files
echo "Generating data files..."
.venv/bin/python ./egpseed/egpseed/generate_types.py --write
.venv/bin/python ./egpseed/egpseed/generate_meta_codons.py --write
.venv/bin/python ./egpseed/egpseed/generate_codons.py --write

# Done
echo "--- Post-create script finished ---"
