# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## DRY Policy (Don't Repeat Yourself)

**Important**: Host-dependent values should NOT be hardcoded throughout the codebase.

All host-specific configuration lives in `host.env`:
- Remote host IP, port, username
- Storage paths (`STORAGE_BASE`, `RUNS_STORAGE_PATH`)
- SMB share details

### Using DRY in Shell Commands

**Always source `host.env` before using variables:**
```bash
# Standard pattern for remote commands
source ~/gmktec/host.env && ~/gmktec/scripts/remote.sh "cd ${STORAGE_BASE}/projects && git status"

# Available variables after sourcing:
# REMOTE_HOST, REMOTE_PORT, REMOTE_USER, STORAGE_BASE, RUNS_STORAGE_PATH, SSH_CMD
```

**Or use helper scripts directly:**
```bash
~/gmktec/scripts/remote.sh kubectl get pods    # Instead of ssh -p 10022 jimmy@...
~/gmktec/scripts/mount-smb.sh                  # Instead of mount_smbfs ...
~/gmktec/scripts/resolve-host.sh --update      # Update IP if WSL2 IP changed
```

### Helper Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `remote.sh` | Execute command on remote host | `remote.sh "kubectl get pods"` |
| `remote.sh -i` | Interactive SSH session | `remote.sh -i` |
| `mount-smb.sh` | Mount SMB share | `mount-smb.sh` or `mount-smb.sh -u` (unmount) |
| `resolve-host.sh` | Show/update host IP | `resolve-host.sh` or `resolve-host.sh --update` |

### Updating host.env

If host values change (e.g., WSL2 IP changes):

```bash
# Option 1: Auto-update IP via DNS
~/gmktec/scripts/resolve-host.sh --update

# Option 2: Manual edit
vi ~/gmktec/host.env
# Change REMOTE_HOST="new.ip.address"
```

### Using DRY in Python

```python
from host_config import config
print(config.REMOTE_HOST)        # 192.168.86.38
print(config.RUNS_STORAGE_PATH)  # /mnt/d/DockerHost/claude/runs
print(config.ssh_prefix)         # ssh -p 10022 jimmy@192.168.86.38
```

### When Adding New Host-Dependent Values

1. Add to `host.env` first
2. Update `projects/template/host_config.py` to load it
3. Use the variable/config instead of hardcoding

## Prerequisites

Before starting work in this directory, mount the Samba share:

```bash
mount_smbfs //GUEST:@192.168.86.38/DockerHost/claude ~/gmktec
```

## Remote Host: jimmy-gmktec

### Network Access

- **Hostname**: jimmy-gmktec
- **DNS Resolution**: `dig @192.168.86.1 jimmy-gmktec.` → `192.168.86.38`
- **IP Address**: 192.168.86.38

### Services

| Service | Port | Status |
|---------|------|--------|
| SSH | 10022 | Verified |
| SMB | 445 | Verified |

### SSH Access

```bash
ssh -p 10022 jimmy@192.168.86.38
```

**Troubleshooting**: If SSH connection fails, the WSL2 IP may have changed. See [WSL2-SSH-PORTPROXY.md](docs/WSL2-SSH-PORTPROXY.md) for fix.

### Samba Share

- **Share Path**: `//192.168.86.38/DockerHost/claude`
- **Authentication**: GUEST (no password)
- **Mount Point**: `~/gmktec`
- **Remote Path**: `/mnt/d/DockerHost/claude` (Windows D: drive, NOT WSL2 home)

### Kubernetes Access

```bash
ssh -p 10022 jimmy@192.168.86.38 kubectl <command>
```

| Property | Value |
|----------|-------|
| Control Plane | https://kubernetes.docker.internal:6443 |
| Node | docker-desktop |
| K8s Version | v1.34.1 |
| Runtime | Docker 29.1.3 |

**Important - Docker Desktop K8s paths**:
- WSL2 sees Windows D: drive at: `/mnt/d/...`
- Docker Desktop K8s hostPath uses: `/mnt/host/d/...`
- These are different mounts - K8s job manifests MUST use `/mnt/host/d/...`

**Requirements for Docker Desktop K8s**:
1. Use Docker Desktop's built-in K8s (NOT Kind multi-node cluster)
2. Enable file sharing: Settings → Resources → File Sharing → Add `D:\DockerHost`

## Projects Directory

For K8s job runner template work, see the projects-specific documentation:

| File | Purpose |
|------|---------|
| `projects/CLAUDE.md` | Template reuse guide, customization |
| `projects/template/CLAUDE.md` | Working guide, commands |
| `projects/template/README.md` | User documentation |

### Quick Start

```bash
cd ~/gmktec/projects/template
./deploy.py infra    # Deploy infrastructure
./deploy.py status   # Check status
```

### Job Run Storage

Job outputs are stored at:
- **WSL2 (SSH)**: `/mnt/d/DockerHost/claude/runs/{run-id}/`
- **K8s hostPath**: `/mnt/host/d/DockerHost/claude/runs/{run-id}/`
- **Mac (via SMB)**: `~/gmktec/runs/{run-id}/`

Note: `host.env` defines both `RUNS_STORAGE_PATH` (for WSL2) and `K8S_RUNS_STORAGE_PATH` (for K8s).

## Local Environment Setup

If you need Python packages locally (PyYAML, kubernetes client, etc.):

```bash
cd ~/gmktec/projects/template
pip install -r requirements.txt
```

This installs: kubernetes, prefect, pyyaml, prometheus-client, requests.

**Note**: Most operations can run via SSH to the remote host which already has dependencies installed.

## Allowed Tools

The following commands are pre-approved to run without prompting:

```
Bash(ssh *)
Bash(git status*)
Bash(git add *)
Bash(git commit *)
Bash(git log*)
Bash(git diff*)
Bash(git branch*)
Bash(git checkout*)
Bash(git pull*)
Bash(git push*)
Bash(git fetch*)
Bash(kubectl *)
Bash(docker build *)
Bash(docker images*)
Bash(docker ps*)
Bash(docker inspect*)
Bash(docker logs*)
Bash(python *)
Bash(pip *)
Bash(mamba *)
Bash(conda *)
Bash(ls *)
Bash(mkdir *)
Bash(cp *)
Bash(mv *)
Bash(cat *)
Bash(head *)
Bash(tail *)
Bash(wc *)
Bash(curl *)
Bash(wget *)
Bash(sleep *)
Bash(echo *)
Bash(cd *)
Bash(pwd)
Bash(which *)
Bash(env)
Bash(printenv*)
```
