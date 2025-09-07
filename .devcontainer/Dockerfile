FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Update and install any necessary packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client

# Install bitdict dev dependency
RUN git clone --depth 1 --branch devel https://github.com/Shapedsundew9/bitdict.git /usr/local/share/bitdict
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/share/bitdict"

# Set the working directory
WORKDIR /workspaces
