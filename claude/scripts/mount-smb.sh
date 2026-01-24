#!/bin/bash
# Mount SMB share helper
# Usage: ./mount-smb.sh [--unmount]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../host.env"

if [ "$1" = "--unmount" ] || [ "$1" = "-u" ]; then
    echo "Unmounting ${SMB_MOUNT_POINT}..."
    diskutil unmount force "${SMB_MOUNT_POINT}" 2>/dev/null || true
    echo "Done"
    exit 0
fi

# Check if already mounted
if mount | grep -q "${SMB_MOUNT_POINT}"; then
    echo "Already mounted: ${SMB_MOUNT_POINT}"
    exit 0
fi

# Create mount point if needed
mkdir -p "${SMB_MOUNT_POINT}"

# Mount
echo "Mounting ${SMB_SHARE} to ${SMB_MOUNT_POINT}..."
mount_smbfs "${SMB_SHARE}" "${SMB_MOUNT_POINT}"
echo "Done"
