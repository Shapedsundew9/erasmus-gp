#!/bin/bash

# This script runs after the container is created.
# The 'set -e' command ensures that the script will exit immediately if a command fails.
set -e

echo "--- Running post-create script ---"

# Activating the virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
./.venv/bin/pip install -r requirements-dev.txt

# Install Python dependencies from requirements.txt
echo "Installing requirements..."
.venv/bin/pip install --upgrade pip
find . -name "requirements.txt" -exec ./.venv/bin/pip install -r {} \;
.venv/bin/pip install -e ./egpcommon
.venv/bin/pip install -e ./egppkrapi
.venv/bin/pip install -e ./egppy
.venv/bin/pip install -e ./egpdb
.venv/bin/pip install -e ./egpdbmgr

# Copy public keys to the devcontainer shared folder
echo "Copying public keys to devcontainer shared folder..."
sudo cp ./egpcommon/data/public_keys/* /usr/local/share/egp/public_keys/

# Add aliases to .bashrc
echo "Adding custom aliases to .bashrc..."
echo "# My Custom Aliases" >> ~/.bashrc
echo "alias profile='.venv/bin/python -m cProfile -o profile.prof -m unittest discover && .venv/bin/python -m snakeviz profile.prof'" >> ~/.bashrc
echo "alias generate='.venv/bin/python ./egpcommon/egpcommon/gp_db_config.py --write && .venv/bin/python ./egpseed/egpseed/generate_types.py --write && .venv/bin/python ./egpseed/egpseed/generate_meta_codons.py --write && .venv/bin/python ./egpseed/egpseed/generate_codons.py --write'" >> ~/.bashrc

# Generate data files
echo "Generating data files..."
mkdir -p ./egpdbmgr/egpdbmgr/data
.venv/bin/python ./egpcommon/egpcommon/gp_db_config.py --write

# Higher layer configuration tooling
if [ -d "/workspaces/egpseed" ]; then
    echo "Detected egpseed folder in /workspaces. Installing and generating data from there..."
    .venv/bin/pip install -e /workspaces/egpseed
    .venv/bin/python /workspaces/egpseed/egpseed/generate_types.py --write
    .venv/bin/python /workspaces/egpseed/egpseed/generate_meta_codons.py --write
    .venv/bin/python /workspaces/egpseed/egpseed/generate_codons.py --write
fi

# Done
echo "--- Post-create script finished ---"
