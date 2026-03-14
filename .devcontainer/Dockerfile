FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Update and install any necessary packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client \
    && mkdir -p /usr/local/share/egp/public_keys 

# Set the working directory
WORKDIR /workspaces
