#!/bin/bash
# Resolve remote host IP dynamically and optionally update host.env
# Usage: ./resolve-host.sh [--update]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST_ENV="${SCRIPT_DIR}/../host.env"

# DNS server (router)
DNS_SERVER="192.168.86.1"
HOSTNAME="jimmy-gmktec"

# Resolve IP
RESOLVED_IP=$(dig @${DNS_SERVER} ${HOSTNAME}. +short 2>/dev/null | head -1)

if [ -z "$RESOLVED_IP" ]; then
    echo "Error: Could not resolve ${HOSTNAME} via ${DNS_SERVER}"
    exit 1
fi

echo "Resolved: ${HOSTNAME} -> ${RESOLVED_IP}"

# Check current IP in host.env
if [ -f "$HOST_ENV" ]; then
    CURRENT_IP=$(grep "^REMOTE_HOST=" "$HOST_ENV" | cut -d'"' -f2)

    if [ "$CURRENT_IP" = "$RESOLVED_IP" ]; then
        echo "IP unchanged: ${RESOLVED_IP}"
    else
        echo "IP changed: ${CURRENT_IP} -> ${RESOLVED_IP}"

        if [ "$1" = "--update" ]; then
            # Update host.env with new IP
            sed -i.bak "s/REMOTE_HOST=\"[^\"]*\"/REMOTE_HOST=\"${RESOLVED_IP}\"/" "$HOST_ENV"
            echo "Updated host.env"
        else
            echo "Run with --update to update host.env"
        fi
    fi
fi
