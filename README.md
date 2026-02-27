# Be Legal with Docker

A toolkit for enterprise developers who need **Docker** in their daily workflow — set up properly, licensed correctly, and ready for production.

## Why This Repository?

In large corporations, container tooling choices matter. Licensing, support contracts, and compliance requirements shape what you can actually use. This repo provides a fully working Docker-based development environment inside **WSL2 on Windows**, plus a management CLI — all using **Docker CE** (Community Edition), which is free for development use.

## Contents

| Folder | Description |
|--------|-------------|
| [wsl_setup/](wsl_setup/README.md) | WSL2 configuration guide + automated setup script (Node.js, Java, .NET, ZSH, Docker CE) |
| [docker_manager/](docker_manager/README.md) | Interactive Python CLI for managing Docker resources (containers, images, volumes, networks, compose, cleanup) |

---

## Docker vs Podman vs Rancher Desktop — Licensing Overview

| Aspect | Docker CE (Engine) | Docker Desktop | Podman | Rancher Desktop |
|--------|--------------------|----------------|--------|-----------------|
| **License** | Apache 2.0 | Free < 250 employees / $5M revenue; paid otherwise | Apache 2.0 | Apache 2.0 |
| **Daemon** | `dockerd` (root or rootless) | Docker Engine wrapped in a VM | Daemonless | `dockerd` or `containerd` |
| **Compose** | `docker compose` plugin | Included | `podman-compose` (limited) | Included |
| **BuildKit** | `docker buildx` plugin | Included | `buildah` (different CLI) | Included |
| **Windows support** | WSL2 only | Native app + WSL2 | WSL2 or native (limited) | Native app + WSL2 |
| **OCI compatible** | Yes | Yes | Yes | Yes |
| **Enterprise support** | Community only | Docker Business plans | Red Hat (via RHEL/OpenShift) | SUSE |
| **Kubernetes built-in** | No | Yes (single node) | No | Yes (K3s) |
| **Ecosystem compatibility** | Full (de facto standard) | Full | Mostly compatible | Full (uses Docker or containerd) |

### Why Docker CE in WSL2?

- **Zero licensing cost** — Docker Engine (CE) is Apache 2.0 licensed with no employee/revenue restrictions.
- **Full compatibility** — All Docker Hub images, Compose files, and CI/CD pipelines work without modification.
- **No Docker Desktop required** — Avoids the per-seat licensing that affects companies with 250+ employees or $10M+ revenue.
- **WSL2 performance** — Near-native Linux performance on Windows; no extra VM layer.

### When to Consider Alternatives

- **Podman** — If your organization is Red Hat-centric and you need rootless containers without a daemon. Be aware that Compose support is limited and some Docker plugins won't work.
- **Rancher Desktop** — If you need a GUI-based experience with built-in Kubernetes (K3s). Good alternative when Docker Desktop licensing is a concern but you want a desktop app.

---

## Kubernetes — What About Orchestration?

This repository focuses on **local container development**, not orchestration. If you need Kubernetes locally, consider:

| Tool | Description | Best For |
|------|-------------|----------|
| [Kind](https://kind.sigs.k8s.io/) | Kubernetes IN Docker — runs clusters as Docker containers | CI/CD testing, multi-node simulation |
| [K3s](https://k3s.io/) | Lightweight Kubernetes by Rancher/SUSE | Edge, IoT, resource-constrained environments |
| [Minikube](https://minikube.sigs.k8s.io/) | Official local Kubernetes | Learning, development |
| [K3d](https://k3d.io/) | K3s inside Docker | Quick disposable clusters |

> A separate repository for Kubernetes local development (Kind/K3s) may be added in the future.

---

## Getting Started

1. **Set up WSL2** — Follow the [WSL2 Setup Guide](wsl_setup/README.md) to configure your Windows machine and install the development stack.

2. **Use Docker Manager** — Run the [Docker Manager CLI](docker_manager/README.md) to manage your containers:
   ```bash
   python -m docker_manager
   ```

---

## License

This repository is provided as-is for educational and development purposes. The tools referenced (Docker CE, Podman, etc.) are subject to their own respective licenses.
