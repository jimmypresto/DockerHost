#!/bin/bash
# Remote command execution helper
# Usage: ./remote.sh <command>
# Example: ./remote.sh kubectl get pods -n job-runner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../host.env"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command>"
    echo "Example: $0 kubectl get pods -n job-runner"
    echo ""
    echo "Or for interactive shell: $0 -i"
    exit 1
fi

if [ "$1" = "-i" ]; then
    # Interactive shell
    exec ssh -p "${REMOTE_PORT}" "${REMOTE_USER}@${REMOTE_HOST}"
else
    # Execute command
    exec ssh -p "${REMOTE_PORT}" "${REMOTE_USER}@${REMOTE_HOST}" "$@"
fi
