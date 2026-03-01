#!/bin/bash

set -u

LOG_FILE="/tmp/devcontainer-post-start.log"

echo "[$(date -Iseconds)] post-start: begin" | tee -a "$LOG_FILE"

mkdir -p /run/secrets
chmod 755 /run/secrets

echo "[$(date -Iseconds)] post-start: /run/secrets prepared" | tee -a "$LOG_FILE"

if [ -n "${POSTGRES_PASSWORD:-}" ]; then
    printf '%s' "${POSTGRES_PASSWORD}" > /run/secrets/db_password
    chmod 600 /run/secrets/db_password
    echo "[$(date -Iseconds)] post-start: wrote /run/secrets/db_password" | tee -a "$LOG_FILE"
else
    echo "[$(date -Iseconds)] post-start: POSTGRES_PASSWORD not set; db_password not written" | tee -a "$LOG_FILE"
fi

if [ -n "${PRIVATE_KEY_PEM_B64:-}" ]; then
    if printf '%s' "${PRIVATE_KEY_PEM_B64}" | base64 -d > /run/secrets/private_key 2>>"$LOG_FILE"; then
        chmod 600 /run/secrets/private_key
        echo "[$(date -Iseconds)] post-start: wrote /run/secrets/private_key" | tee -a "$LOG_FILE"
    else
        rm -f /run/secrets/private_key
        echo "[$(date -Iseconds)] post-start: PRIVATE_KEY_PEM_B64 invalid base64; private_key not written" | tee -a "$LOG_FILE"
    fi
else
    echo "[$(date -Iseconds)] post-start: PRIVATE_KEY_PEM_B64 not set; private_key not written" | tee -a "$LOG_FILE"
fi

echo "[$(date -Iseconds)] post-start: complete" | tee -a "$LOG_FILE"
