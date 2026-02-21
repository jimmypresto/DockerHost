# DockerHost

## Environment
- Windows 11 host running WSL2 (Ubuntu 24.04)
- Docker volumes must use `/mnt/d/DockerHost/...` paths (not Windows-style `c:/` or `d:/`)
- `C:\DockerHost` is a symlink to `D:\DockerHost`

## Doc Hygiene
Before creating, modifying, or committing docs: remove content that covers general knowledge or things you can check live with a command. Keep only what's specific to this environment and can't be discovered programmatically.

## Docs
- [docs/docker-services.md](docs/docker-services.md) — service inventory and firewall rules
- [docs/jimmy-gmktec-setup.md](docs/jimmy-gmktec-setup.md) — hardware and storage details
