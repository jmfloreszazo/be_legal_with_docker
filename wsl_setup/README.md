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
16. [Executive Summary](#15-executive-summary)

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

Create `C:\Users\YOUR_USERNAME\.wslconfig`:

```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
localhostForwarding=true
```

### Recommendations based on total RAM

| Total RAM | Assign to WSL |
|-----------|---------------|
| 16 GB     | 6–8 GB        |
| 32 GB     | 12–16 GB      |
| 64 GB     | 16–24 GB      |

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

1. Copy the generated `.wslconfig` template to Windows:
   ```bash
   cp ~/wslconfig-template.txt /mnt/c/Users/YOUR_USERNAME/.wslconfig
   ```

2. Restart WSL from PowerShell:
   ```powershell
   wsl --shutdown
   ```

3. Always keep your code inside WSL filesystem:
   ```
   /home/yourusername/projects/   ← FAST (ext4)
   /mnt/c/Users/...              ← SLOW (9p filesystem bridge)
   ```

4. Open VS Code from WSL terminal:
   ```bash
   cd ~/projects/my-project
   code .
   ```

---

## 12. Validation Commands

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

## 15. Executive Summary

| Aspect | Correct Configuration |
|--------|----------------------|
| **Virtualization** | Enabled in BIOS |
| **WSL Version** | WSL 2 |
| **RAM assigned** | ~50% of total (max) |
| **Code location** | `/home/user/` |
| **VS Code** | Open with `code .` from WSL |
| **Docker** | Docker CE inside WSL (or Docker Desktop with WSL integration) |
| **Antivirus** | Exclude WSL paths |

---

> **Note:** Properly configured WSL2 is practically indistinguishable from native Linux for development. Poorly configured, it's a performance nightmare.
