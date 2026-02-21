# Docker Services

All services are under `/mnt/d/DockerHost/services/`. Volume paths are standardized to `/mnt/d/DockerHost/...`.

## Services

| Service | Key Ports | Notes |
|---------|-----------|-------|
| openvpn-deluge | 8112 (web UI), 6881, 10023 (SSH) | LinuxServer deluge + OpenVPN via NordVPN |
| frigate | 5000 (web), 1935 (RTMP), 8554-8555 (RTSP/WebRTC) | NVR / object detection |
| face-clustering | 7070 | Face recognition service |
| portainer | 9000, 9443 | Docker management UI (no compose file in repo) |
| homeassistant | — | Home automation (not currently running) |
| wyze-bridge | — | Wyze camera bridge (not currently running) |
| go2rtc | — | Camera streaming (not currently running) |
| rsyncd | — | Rsync daemon |
| deluge | — | Standalone deluge (separate from openvpn-deluge) |
| openvpn | — | Standalone OpenVPN |

## Windows Firewall Rules

### Existing Rules (as of 2026-02-21)
| Port | Protocol | Rule Name | Service |
|------|----------|-----------|---------|
| 5000 | TCP | Frigate UI 5000 | frigate |
| 8554 | TCP | rtsp 8554 | frigate |
| 1935 | TCP | Allow Port 1935 | frigate |
| 7070 | TCP | Face-clustering 7070 | face-clustering |
| 8112 | TCP | Allow Port 8112 | openvpn-deluge |
| 9000 | TCP | Allow Port 9000 | portainer |
| 10022 | TCP | WSL SSH10022 | openvpn |
| 2222 | TCP | WSL SSH | WSL SSH access |

### Missing Rules
| Port | Protocol | Service | Purpose |
|------|----------|---------|---------|
| 8555 | TCP+UDP | frigate | WebRTC live view |
| 6881 | TCP | openvpn-deluge | Torrent peer connections |
| 10023 | TCP | openvpn-deluge | SSH |
| 9443 | TCP | portainer | HTTPS web UI |

### Example PowerShell command (run as Administrator)
```powershell
New-NetFirewallRule -DisplayName "Frigate WebRTC 8555" -Direction Inbound -Protocol TCP -LocalPort 8555 -Action Allow -Profile Any
```

For UDP:
```powershell
New-NetFirewallRule -DisplayName "Frigate WebRTC 8555 UDP" -Direction Inbound -Protocol UDP -LocalPort 8555 -Action Allow -Profile Any
```

## Notes

### Docker Volume Paths
- All compose files use WSL2-style paths: `/mnt/d/DockerHost/...`
- Do NOT use Windows-style `c:/` or `d:/` paths — they fail under WSL2 Docker
- `C:\DockerHost` is a symlink to `D:\DockerHost`, so both resolve to the same place

### LinuxServer.io Images (deluge, openvpn-deluge)
- Use s6-overlay init system: entrypoint is `/init`, which starts services
- `command` (CMD) runs AFTER s6 starts services — do not call `/init` again in CMD
- If CMD exits, the container shuts down — keep a foreground process running (e.g., openvpn without `--daemon`)
