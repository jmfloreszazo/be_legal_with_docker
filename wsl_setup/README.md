# WSL2 Setup — Complete Configuration Guide

Complete setup for a WSL2 development environment on Windows, optimized for use with VS Code and Docker.

> **Goal:** Properly configure WSL2 for professional development with VS Code.

---

## Table of Contents

1. [What's Included](#whats-included)
2. [Prerequisites — BIOS/UEFI](#1-prerequisites--biosuefi)
3. [WSL2 Installation](#2-wsl2-installation)
4. [Resource Configuration](#3-resource-configuration-critical)
5. [Disk Performance](#4-disk-performance)
6. [VS Code Configuration](#5-vs-code-configuration)
7. [Docker Integration](#6-docker-integration)
8. [Performance Optimizations](#7-performance-optimizations)
9. [Common Problems and Solutions](#8-common-problems-and-solutions)
10. [Quick Start — Setup Script](#9-quick-start--setup-script)
11. [Configuration Variables](#10-configuration-variables)
12. [After Installation](#11-after-installation)
13. [Validation Commands](#12-validation-commands)
14. [Useful WSL Commands](#13-useful-wsl-commands)
15. [Recommended Work Structure](#14-recommended-work-structure)
16. [Docker Autostart Configuration](#15-docker-autostart-configuration)
17. [Executive Summary](#16-executive-summary)

---

## What's Included

### Setup Script (`wsl2-setup.sh`)

Automated installation of a full development stack inside WSL2 Ubuntu:

| Tool | Version | Manager | Purpose |
|------|---------|---------|---------|
| **Node.js** | LTS (latest) | NVM | JavaScript/TypeScript runtime |
| **Java** | 23 (Temurin) | SDKMAN | JVM development |
| **.NET SDK** | 10.0 | Microsoft APT | C# / F# / .NET development |
| **ZSH** | latest | apt + Oh My Zsh | Enhanced shell experience |
| **Docker** | latest (CE) | Docker APT repo | Container runtime (Docker Engine + Compose + Buildx) |

### Autostart Script (`wsl2-autostart.sh`)

Configures Docker to start automatically when WSL boots:

- Adds `[boot] command=service docker start` to `/etc/wsl.conf`
- Enables `systemd` if available (Windows 11 22H2+)
- Configures passwordless `sudo` for Docker service commands
- Verifies `.wslconfig` on the Windows side

### Windows Autostart Script (`windows-autostart.ps1`)

Creates a Windows Task Scheduler entry to boot WSL and Docker on Windows login:

- Runs `wsl.exe -d Ubuntu -u root -- service docker start` at logon
- Supports custom distro names (`-DistroName`)
- Removable with `-Remove` flag
- Requires Administrator privileges

---

## 1. Prerequisites — BIOS/UEFI

### Verify virtualization is enabled

**In BIOS/UEFI:**
- **Intel:** VT-x Enabled
- **AMD:** SVM Enabled

**Verify in Windows:**
```powershell
systeminfo | find "Virtualization"
```

Should show:
```
Virtualization Enabled In Firmware: Yes
```

---

## 2. WSL2 Installation

```powershell
# Clean installation
wsl --install

# Verify version
wsl --status
# Should show: Default Version: 2

# List installed distros
wsl -l -v

# If any is on v1, convert to v2
wsl --set-version Ubuntu 2
```

**Recommended distro:** Ubuntu 22.04 LTS or Ubuntu 24.04 LTS.

---

## 3. Resource Configuration (CRITICAL)

> ⚠️ **By default WSL2 can consume all available RAM.**

### Create configuration file

> **Note:** Both `wsl2-setup.sh` and `wsl2-autostart.sh` auto-detect your hardware and create this file with optimal values. You should not need to create it manually.

The file is located at `C:\Users\YOUR_USERNAME\.wslconfig`:

```ini
[wsl2]
memory=8GB          # Auto: 50% of total RAM
processors=6        # Auto: 50% of total CPUs
swap=2GB            # Auto: 25% of assigned memory
localhostForwarding=true
```

### Auto-calculated recommendations

| Total RAM | CPUs | memory | processors | swap |
|-----------|------|--------|------------|------|
| 8 GB      | 4    | 4 GB   | 2          | 2 GB |
| 16 GB     | 12   | 8 GB   | 6          | 2 GB |
| 32 GB     | 16   | 16 GB  | 8          | 4 GB |
| 64 GB     | 24   | 32 GB  | 12         | 8 GB |

### Apply changes

```powershell
wsl --shutdown
```

---

## 4. Disk Performance

### ❌ NEVER work in

```
/mnt/c/Users/...
```
Accessing the Windows disk from WSL is **extremely slow** (9p filesystem bridge).

### ✅ ALWAYS work in

```
/home/yourusername/projects
```

You can still browse WSL files from Windows via:
```
\\wsl$\Ubuntu\home\yourusername\project
```

---

## 5. VS Code Configuration

### Required extensions

1. **WSL** (Microsoft) — Mandatory
2. **Remote Development** pack — Recommended

### Correct way to open projects

```bash
# From WSL terminal
cd ~/projects/my-project
code .
```

### Verify connection

In the bottom-left corner of VS Code you should see:
```
WSL: Ubuntu
```

### ⚠️ DO NOT

- Open a Windows folder and then connect to WSL
- Work in `/mnt/c/`

---

## 6. Docker Integration

The setup script installs **Docker CE** (Community Edition) directly inside WSL from the official Docker APT repository. This includes:

- `docker-ce` — Docker Engine
- `docker-compose-plugin` — Docker Compose v2
- `docker-buildx-plugin` — BuildKit builder

No Docker Desktop is required. Docker runs natively inside your WSL2 distro.

If Docker is already running via **Docker Desktop** and you prefer that approach, set `INSTALL_DOCKER=false` when running the script and enable WSL integration in Docker Desktop:

```
Settings → Resources → WSL Integration → Enable your distro
```

### Starting Docker after a reboot

WSL2 does not use `systemd` by default, so Docker does not start automatically after a `wsl --shutdown` or a Windows reboot. You need to start it manually:

```bash
sudo service docker start
```

To verify it's running:

```bash
docker info --format '{{.ServerVersion}}'
```

> **Tip:** Add `sudo service docker start` to your `~/.zshrc` or `~/.bashrc` to auto-start Docker when you open a WSL terminal.

### Accessing Docker containers from Windows

WSL2 supports **localhost forwarding** — any port exposed by a Docker container inside WSL is automatically accessible from Windows at `http://localhost:<port>`.

**Requirements:**

1. `.wslconfig` must have `localhostForwarding=true` (see [Resource Configuration](#3-resource-configuration-critical))
2. Containers must publish ports with `-p` flag

**Example — Running Jenkins:**

```bash
# Inside WSL terminal
docker run -d --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

Then open in your **Windows browser**:

```
http://localhost:8080
```

This works for any containerized service — backends, frontends, databases, CI tools:

| Service | Docker command | Windows URL |
|---------|---------------|-------------|
| Jenkins | `-p 8080:8080` | `http://localhost:8080` |
| PostgreSQL | `-p 5432:5432` | `localhost:5432` (via client) |
| Nginx | `-p 80:80` | `http://localhost` |
| React dev | `-p 3000:3000` | `http://localhost:3000` |
| .NET API | `-p 5000:5000` | `http://localhost:5000` |

### Using Docker from Windows (PowerShell, CMD, Windows Terminal)

You do **not** need Docker Desktop nor Docker CLI installed on Windows. The only requirement is WSL with Docker installed inside it.

**The rule is simple:** any `docker` command that works inside WSL works from Windows adding `wsl` as prefix.

| Inside WSL | From PowerShell / CMD |
|------------|----------------------|
| `docker ps` | `wsl docker ps` |
| `docker images` | `wsl docker images` |
| `docker logs jenkins` | `wsl docker logs jenkins` |
| `docker stop myapp` | `wsl docker stop myapp` |
| `docker pull nginx` | `wsl docker pull nginx` |
| `docker compose up -d` | `wsl docker compose up -d` |
| `docker compose down` | `wsl docker compose down` |
| `docker compose logs -f` | `wsl docker compose logs -f` |
| `docker build -t myimg .` | `wsl docker build -t myimg .` |
| `docker exec -it db bash` | `wsl docker exec -it db bash` |
| `docker volume ls` | `wsl docker volume ls` |
| `docker network ls` | `wsl docker network ls` |
| `docker system prune -f` | `wsl docker system prune -f` |

**Examples from PowerShell:**

```powershell
# Check Docker version
wsl docker version

# Check Docker Compose version
wsl docker compose version

# List running containers
wsl docker ps

# View container logs
wsl docker logs jenkins

# Stop a container
wsl docker stop jenkins

# Pull an image
wsl docker pull nginx:latest

# Run a compose project (use Linux paths)
wsl docker compose -f /home/jmfloreszazo/projects/myapp/docker-compose.yml up -d

# Interactive shell inside a container
wsl docker exec -it mycontainer bash
```

**From CMD (same syntax):**

```cmd
wsl docker ps
wsl docker compose up -d
```

> **Important:**
> - The `wsl` prefix routes the command to your default WSL distro where Docker is installed.
> - File paths inside `wsl docker` commands must use **Linux paths** (`/home/...`), not Windows paths (`C:\...`).
> - To reference a Windows file, use `/mnt/c/Users/...` instead of `C:\Users\...`.
> - This works from **PowerShell**, **CMD**, and **Windows Terminal** — all behave identically.

### Firewall considerations

If `localhost` does not work from Windows:

1. **Check Windows Firewall** — WSL2 uses a virtual network adapter. Some corporate firewalls block traffic between Windows and WSL. Add an inbound rule for the port.
2. **Try the WSL IP directly:**
   ```bash
   # Inside WSL
   hostname -I
   ```
   Then use that IP from Windows: `http://172.x.x.x:8080`
3. **Restart WSL** to apply `.wslconfig` changes:
   ```powershell
   wsl --shutdown
   ```

---

## 7. Performance Optimizations

### Windows Defender Exclusions

Exclude these paths from antivirus scanning:
```
%USERPROFILE%\AppData\Local\Packages\Canonical*
%USERPROFILE%\AppData\Local\Docker
```

### Git Configuration

```bash
git config --global core.autocrlf input
```

---

## 8. Common Problems and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| WSL consumes infinite RAM | No limits configured | Create `.wslconfig` + `wsl --shutdown` |
| VS Code slow | Code in `/mnt/c` | Move to `/home/user` |
| Git extremely slow | Cross-filesystem operations | `git config --global core.autocrlf input` |
| Extensions not working | Installed only in Windows | Install in WSL (click "Install in WSL") |
| Docker not running after reboot | WSL has no systemd | `sudo service docker start` |
| `localhost:8080` not reachable | `localhostForwarding` missing | Add `localhostForwarding=true` to `.wslconfig` + `wsl --shutdown` |
| `docker` not found in PowerShell | Docker is in WSL, not Windows | Use `wsl docker ps` instead |
| Port blocked from Windows | Corporate firewall | Add inbound rule or use WSL IP (`hostname -I`) |

---

## 9. Quick Start — Setup Script

```bash
# From WSL terminal
cd ~/

# Clone or copy the script
chmod +x wsl2-setup.sh

# Run with all defaults (Node + Java + .NET + ZSH + Docker)
./wsl2-setup.sh

# Or customize what to install
INSTALL_SDKMAN=false INSTALL_DOTNET=false ./wsl2-setup.sh
```

---

## 10. Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INSTALL_ZSH` | `true` | ZSH + Oh My Zsh |
| `INSTALL_NVM` | `true` | NVM + Node.js LTS |
| `INSTALL_SDKMAN` | `true` | SDKMAN + Java 23 |
| `INSTALL_DOTNET` | `true` | .NET SDK 10.0 |
| `INSTALL_DOCKER` | `true` | Docker CE + Compose + Buildx |
| `NODE_VERSION` | `--lts` | Node version to install via NVM |
| `JAVA_VERSION` | `23-tem` | Java version to install via SDKMAN |
| `DOTNET_VERSION` | `10.0` | .NET SDK version |

---

## 11. After Installation

The setup script automatically detects your hardware and installs `.wslconfig` in your Windows user folder with optimal values:

| Setting | Auto-calculated as |
|---------|-------------------|
| `memory` | 50% of total RAM (min 4GB) |
| `processors` | 50% of total CPUs (min 2) |
| `swap` | 25% of assigned memory (min 2GB) |
| `localhostForwarding` | Always `true` |

**Example for a 16GB / 12-core machine:**

```ini
[wsl2]
memory=8GB
processors=6
swap=2GB
localhostForwarding=true
```

A backup template is also saved at `~/wslconfig-template.txt`.

After the script finishes:

1. Restart WSL from PowerShell to apply resource limits:
   ```powershell
   wsl --shutdown
   ```

2. Always keep your code inside WSL filesystem:
   ```
   /home/yourusername/projects/   <-- FAST (ext4)
   /mnt/c/Users/...              <-- SLOW (9p filesystem bridge)
   ```

4. Open VS Code from WSL terminal:
   ```bash
   cd ~/projects/my-project
   code .
   ```

---

## 12. Validation Commands

### From WSL terminal

```bash
# Verify kernel
uname -a

# Verify resources
htop

# Verify disk space
df -h

# Verify filesystem is ext4
mount | grep "on / "

# Verify Docker
docker --version
docker compose version
docker info --format '{{.ServerVersion}}'
```

### From Windows PowerShell

```powershell
# Verify Docker is reachable from Windows
wsl docker version
wsl docker ps

# Verify port forwarding (start a test container first)
wsl docker run -d --rm -p 8888:80 nginx:alpine
# Then open http://localhost:8888 in your Windows browser
```

---

## 13. Useful WSL Commands

```powershell
# Shutdown WSL completely
wsl --shutdown

# Restart specific distro
wsl -t Ubuntu

# View status
wsl --status

# Export distro (backup)
wsl --export Ubuntu ubuntu-backup.tar

# Import distro
wsl --import Ubuntu-New C:\WSL\Ubuntu-New ubuntu-backup.tar

# Update WSL
wsl --update
```

---

## 14. Recommended Work Structure

```
/home/user/
├── projects/
│   ├── dotnet-project/
│   ├── node-project/
│   └── java-project/
├── tools/
└── scripts/
```

---

## 15. Docker Autostart Configuration

After running `wsl2-setup.sh`, Docker is configured to start automatically when WSL boots. If you already ran the setup before this feature was added, use the standalone `wsl2-autostart.sh` script.

### Step 1 — Configure Docker autostart inside WSL

```bash
# From WSL terminal
chmod +x wsl2-autostart.sh
./wsl2-autostart.sh
```

This configures `/etc/wsl.conf`:

```ini
[boot]
command=service docker start
```

And sets up passwordless sudo so the boot command runs without a password prompt.

### Step 2 — Restart WSL to apply

```powershell
# From PowerShell
wsl --shutdown
```

Open a new WSL terminal — Docker will be running automatically:

```bash
docker info --format '{{.ServerVersion}}'
# Should print version number without requiring 'sudo service docker start'
```

### Step 3 (Optional) — Auto-start WSL on Windows login

By default, WSL only starts when you open a terminal. To have WSL and Docker start at Windows login:

```powershell
# From PowerShell (Run as Administrator)
.\windows-autostart.ps1
```

This creates a Windows Task Scheduler entry that runs:

```
wsl.exe -d Ubuntu -u root -- service docker start
```

**Customization:**

```powershell
# Use a different distro
.\windows-autostart.ps1 -DistroName "Ubuntu-24.04"

# Overwrite existing task
.\windows-autostart.ps1 -Force

# Remove the task
.\windows-autostart.ps1 -Remove

# Test immediately
schtasks /Run /TN "WSL2-Docker-Autostart"
```

### What happens after setup

| Event | Docker behavior |
|-------|----------------|
| **Windows login** | WSL starts + Docker starts (if `windows-autostart.ps1` was run) |
| **Open WSL terminal** | Docker is already running |
| **`wsl --shutdown`** | Next WSL start auto-starts Docker via `wsl.conf` |
| **Windows reboot** | Same as Windows login |
| **Docker crash** | Manually restart with `sudo service docker restart` |

### Verifying autostart

```bash
# Inside WSL — check Docker is running without manual start
docker ps

# Check wsl.conf is configured
cat /etc/wsl.conf

# Check sudoers rule exists
sudo cat /etc/sudoers.d/docker-autostart
```

```powershell
# From PowerShell — check the scheduled task
schtasks /Query /TN "WSL2-Docker-Autostart"

# Check Docker is reachable
wsl docker ps
```

---

## 16. Executive Summary

| Aspect | Correct Configuration |
|--------|----------------------|
| **Virtualization** | Enabled in BIOS |
| **WSL Version** | WSL 2 |
| **RAM assigned** | ~50% of total (max) |
| **Code location** | `/home/user/` |
| **VS Code** | Open with `code .` from WSL |
| **Docker** | Docker CE inside WSL (or Docker Desktop with WSL integration) |
| **localhost forwarding** | `localhostForwarding=true` in `.wslconfig` |
| **Docker from PowerShell** | `wsl docker ps`, `wsl docker logs ...` |
| **Start Docker** | Automatic via `/etc/wsl.conf` `[boot] command` |
| **WSL auto-boot** | Optional: `windows-autostart.ps1` (Task Scheduler) |
| **Antivirus** | Exclude WSL paths |

---

> **Note:** Properly configured WSL2 is practically indistinguishable from native Linux for development. Poorly configured, it's a performance nightmare.
