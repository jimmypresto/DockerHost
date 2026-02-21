# DockerHost

## Environment
- Windows 11 host running WSL2 (Ubuntu 24.04)
- Docker volumes use `/mnt/d/DockerHost/...` paths (not Windows-style `c:/` or `d:/`)
- `C:\DockerHost` is a symlink to `D:\DockerHost`

## Key Rules
- Follow the [debugging principles](docs/debugging-principles.md) — diagnose before fixing, change one thing at a time, preserve what works
- LinuxServer.io images use s6-overlay: entrypoint is `/init`, do not call `/init` again in CMD
- See [docs/docker-services.md](docs/docker-services.md) for service inventory and firewall rules
- See [docs/jimmy-gmktec-setup.md](docs/jimmy-gmktec-setup.md) for hardware/software details
