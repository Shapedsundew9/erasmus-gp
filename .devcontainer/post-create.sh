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
echo "alias profile='/workspaces/erasmus-gp/.venv/bin/python -m cProfile -o profile.prof -m unittest discover && /workspaces/erasmus-gp/.venv/bin/python -m snakeviz profile.prof'" >> ~/.bashrc

# Higher layer configuration tooling
if [ -d "/workspaces/egpseed" ]; then
    echo "Detected egpseed folder in /workspaces. Installing and generating data from there..."
    .venv/bin/pip install -e /workspaces/egpseed
    .venv/bin/python /workspaces/egpseed/egpseed/generate_gcabc_json.py --write
    .venv/bin/python /workspaces/egpseed/egpseed/generate_types.py --write
    .venv/bin/python /workspaces/egpseed/egpseed/generate_meta_codons.py --write
    .venv/bin/python /workspaces/egpseed/egpseed/generate_codons.py --write
    echo "alias generate='/workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_gcabc_json.py --write && /workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_types.py --write && /workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_meta_codons.py --write && /workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_codons.py --write'" >> ~/.bashrc
else
    DIR="/workspaces/erasmus-gp/egppy/egppy/data"
    URL="https://github.com/Shapedsundew9/erasmus-gp/releases/download/latest-data"
    
    # Use brace expansion to loop through all 4 file variations
    for f in {meta_,}codons.json{,.sig}; do
        curl -z "$DIR/$f" -L -o "$DIR/$f" "$URL/$f"
    done
    echo "alias pull='for f in {meta_,}codons.json{,.sig}; do p="/workspaces/erasmus-gp/egppy/egppy/data/$f"; curl -z "$p" -L -o "$p" "https://github.com/Shapedsundew9/erasmus-gp/releases/download/latest-data/$f"; done'" >> ~/.bashrc
fi

# Done
echo "--- Post-create script finished ---"
