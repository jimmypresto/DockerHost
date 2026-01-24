# WSL2 SSH Port Proxy Fix

## Problem

SSH to jimmy-gmktec fails with no IP connection because WSL2's internal IP address changes on restart, which obsoletes the previous Windows firewall port proxy rule.

## Solution

On **jimmy-gmktec** (Windows host), open PowerShell as Administrator and run:

### 1. Get current WSL2 IP address

```powershell
wsl hostname -I
```

Example output:
```
172.24.232.46
```

### 2. Add/update port proxy rule

```powershell
netsh interface portproxy add v4tov4 listenport=10022 listenaddress=0.0.0.0 connectport=10022 connectaddress=<WSL2_IP>
```

Example:
```powershell
netsh interface portproxy add v4tov4 listenport=10022 listenaddress=0.0.0.0 connectport=10022 connectaddress=172.24.232.46
```

### 3. Verify port proxy rules

```powershell
netsh interface portproxy show all
```

Expected output:
```
Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
0.0.0.0         22          172.17.40.47    22
0.0.0.0         10022       172.24.232.46   10022
```

## Notes

- This must be done from an elevated PowerShell prompt on the Windows host
- The WSL2 IP address changes each time WSL restarts
- Port 10022 forwards to WSL2's SSH daemon
