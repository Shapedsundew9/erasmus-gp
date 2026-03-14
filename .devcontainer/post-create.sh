#!/bin/bash

# This script runs after the container is created.
# The 'set -e' command ensures that the script will exit immediately if a command fails.
set -e

echo "--- Running post-create script ---"

# Activating the virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements-dev.txt

# Install Python dependencies from requirements.txt
echo "Installing requirements..."
find . -name "requirements.txt" -exec ./.venv/bin/pip install -r {} \;
.venv/bin/pip install -e ./egpcommon
.venv/bin/pip install -e ./egppkrapi
.venv/bin/pip install -e ./egppy
.venv/bin/pip install -e ./egpdb
.venv/bin/pip install -e ./egpdbmgr

# Install bitdict in editable mode
if [ ! -d "/workspaces/bitdict" ]; then
    echo "Cloning bitdict repository..."
    git clone --depth 1 --branch devel https://github.com/Shapedsundew9/bitdict.git /workspaces/bitdict
else
    echo "bitdict repository already exists, updating..."
    git -C /workspaces/bitdict pull
fi
.venv/bin/pip install -e /workspaces/bitdict

# Copy public keys to the devcontainer shared folder
echo "Copying public keys to devcontainer shared folder..."
sudo cp ./egpcommon/data/public_keys/* /usr/local/share/egp/public_keys/

# Add aliases to .bashrc
echo "Adding custom aliases to .bashrc..."
echo "# My Custom Aliases" >> ~/.bashrc
echo "alias profile='/workspaces/erasmus-gp/.venv/bin/python -m cProfile -o profile.prof -m unittest discover && /workspaces/erasmus-gp/.venv/bin/python -m snakeviz profile.prof'" >> ~/.bashrc

# If egp seed is installed, add an alias for the generate script
if [ -d "/workspaces/egpseed" ]; then
    echo "alias generate='/workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_gcabc_json.py --write && /workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_types.py --write && /workspaces/erasmus-gp/.venv/bin/python /workspaces/egpseed/egpseed/generate_codons.py --write'" >> ~/.bashrc
fi
# Sync the codon and types def data
echo "Syncing GitHub data..."
./.venv/bin/python3 /workspaces/erasmus-gp/egpcommon/egpcommon/manage_github_data.py download

# Install CLI's
echo "Installing CLI tools..."
npm install -g @google/gemini-cli

# Install spec-kit
echo "Installing spec-kit..."
./.venv/bin/pip install uv
. ./.venv/bin/activate
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Done
echo "--- Post-create script finished ---"
