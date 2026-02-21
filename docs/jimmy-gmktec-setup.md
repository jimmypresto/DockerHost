# Jimmy-GMKtec Setup

## Hardware
- **Device**: GMKtec mini PC
- **CPU**: AMD Ryzen 7 8845HS w/ Radeon 780M Graphics (15 threads visible to WSL)
- **RAM**: 38 GB
- **Storage**:
  - C: drive — 476 GB (248 GB used)
  - D: drive — 932 GB (299 GB used)
  - `C:\DockerHost` is a **symlink** → `D:\DockerHost` (the real data lives on D:)
  - In WSL: `/mnt/c/DockerHost` → `/mnt/d/DockerHost`

## OS & Runtime
- **Host OS**: Windows 11 (WSL2)
- **WSL Distro**: Ubuntu 24.04.1 LTS
- **Kernel**: 5.15.167.4-microsoft-standard-WSL2
- **Docker**: 29.2.1
- **Docker Compose**: v5.0.2
- **Node.js**: v20.20.0 / npm 10.8.2
- **Python**: 3.12.3 (pip3 NOT installed)
- **Claude Code**: 2.1.50 (`/home/jimmy/.local/bin/claude`)

## GitHub
- **Account**: jimmypresto
- **gh CLI**: Authenticated via PAT token, HTTPS protocol
- **SSH**: Working (`git@github.com`), key `~/.ssh/id_ed25519`
- **Git user**: Jimmy Presto / jimmy.presto@gmail.com
- **SSH config**: `jimmy-gmktec` → 192.168.86.38:10022

## Common Utilities
All present: curl, wget, jq, htop, vim, nano, rsync, ssh

## Project Layout
- **Repo**: `git@github.com:jimmypresto/DockerHost.git`
- **Working directory**: `/mnt/d/DockerHost`
- **Volume paths**: Standardized to `/mnt/d/DockerHost/...` across all docker-compose files

## Scheduled Tasks

### WSL2 (Linux side)
- **crontab**: Empty — no user cron jobs
- **systemd timers**: Only default Ubuntu (apt-daily, logrotate, man-db, tmpfiles-clean)

### Windows Host
| Task | State |
|------|-------|
| Reboot Every 5AM | Ready |
| AMDInstallLauncher | Ready |
| AMDLinkUpdate | Ready |
| OneDrive Reporting/Update/Startup | Ready |
| StartAUEP | Running |
| StartCN | Ready |
| StartCNBM | Ready |
| StartDVR | Ready |
