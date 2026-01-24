# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

**Troubleshooting**: If SSH connection fails, the WSL2 IP may have changed. See [WSL2-SSH-PORTPROXY.md](WSL2-SSH-PORTPROXY.md) for fix.

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
- **K8s node**: `/mnt/d/DockerHost/claude/runs/{run-id}/`
- **Mac (via SMB)**: `~/gmktec/runs/{run-id}/`

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
