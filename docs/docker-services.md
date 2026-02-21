# Docker Services

All services are under `/mnt/d/DockerHost/services/`.

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
