#!/bin/bash

#===============================================================================
# WSL2 Development Environment Setup Script
# Run this script inside WSL2 (Ubuntu) to configure your dev environment
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

#===============================================================================
# Configuration Variables - Modify as needed
#===============================================================================

INSTALL_ZSH=${INSTALL_ZSH:-true}
INSTALL_NVM=${INSTALL_NVM:-true}
INSTALL_SDKMAN=${INSTALL_SDKMAN:-true}
INSTALL_DOTNET=${INSTALL_DOTNET:-true}
INSTALL_DOCKER=${INSTALL_DOCKER:-true}
NODE_VERSION=${NODE_VERSION:-"--lts"}
JAVA_VERSION=${JAVA_VERSION:-"23-tem"}
DOTNET_VERSION=${DOTNET_VERSION:-"10.0"}

#===============================================================================
# Pre-flight checks
#===============================================================================

print_header "WSL2 Development Environment Setup"

# Check if running in WSL
if ! grep -qEi "(microsoft|wsl)" /proc/version &> /dev/null; then
    print_error "This script must be run inside WSL2!"
    exit 1
fi

print_success "Running in WSL2"

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    print_info "Detected: $NAME $VERSION_ID"
fi

#===============================================================================
# System Update
#===============================================================================

print_header "Updating System Packages"

sudo apt update
sudo apt upgrade -y

print_success "System updated"

#===============================================================================
# Essential Tools
#===============================================================================

print_header "Installing Essential Tools"

sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    unzip \
    zip \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    tree \
    jq \
    vim \
    nano

print_success "Essential tools installed"

#===============================================================================
# Git Configuration
#===============================================================================

print_header "Configuring Git"

git config --global core.autocrlf input
git config --global init.defaultBranch main

# Check if git user is configured
if [ -z "$(git config --global user.name)" ]; then
    print_warning "Git user.name not set. Configure with:"
    echo "    git config --global user.name \"Your Name\""
fi

if [ -z "$(git config --global user.email)" ]; then
    print_warning "Git user.email not set. Configure with:"
    echo "    git config --global user.email \"your@email.com\""
fi

print_success "Git configured"

#===============================================================================
# ZSH + Oh My Zsh
#===============================================================================

if [ "$INSTALL_ZSH" = true ]; then
    print_header "Installing ZSH + Oh My Zsh"

    sudo apt install -y zsh

    # Install Oh My Zsh (unattended)
    if [ ! -d "$HOME/.oh-my-zsh" ]; then
        sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
        print_success "Oh My Zsh installed"
    else
        print_info "Oh My Zsh already installed"
    fi

    # Set ZSH as default shell
    if [ "$SHELL" != "$(which zsh)" ]; then
        chsh -s $(which zsh)
        print_success "ZSH set as default shell"
    fi

    # Add useful plugins to .zshrc
    if [ -f "$HOME/.zshrc" ]; then
        # Update plugins line if using default
        sed -i 's/plugins=(git)/plugins=(git docker docker-compose npm node)/' "$HOME/.zshrc"
    fi

    print_success "ZSH configured"
fi

#===============================================================================
# NVM (Node Version Manager)
#===============================================================================

if [ "$INSTALL_NVM" = true ]; then
    print_header "Installing NVM and Node.js"

    export NVM_DIR="$HOME/.nvm"

    if [ ! -d "$NVM_DIR" ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        print_success "NVM installed"
    else
        print_info "NVM already installed"
    fi

    # Load NVM
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

    # Install Node.js
    nvm install $NODE_VERSION
    nvm use $NODE_VERSION
    nvm alias default node

    print_success "Node.js $(node --version) installed"

    # Install global packages
    npm install -g npm@latest
    npm install -g yarn pnpm

    print_success "npm, yarn, pnpm installed"
fi

#===============================================================================
# SDKMAN (Java)
#===============================================================================

if [ "$INSTALL_SDKMAN" = true ]; then
    print_header "Installing SDKMAN and Java"

    export SDKMAN_DIR="$HOME/.sdkman"

    if [ ! -d "$SDKMAN_DIR" ]; then
        curl -s "https://get.sdkman.io" | bash
        print_success "SDKMAN installed"
    else
        print_info "SDKMAN already installed"
    fi

    # Load SDKMAN
    [ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ] && source "$SDKMAN_DIR/bin/sdkman-init.sh"

    # Install Java
    sdk install java $JAVA_VERSION

    print_success "Java installed"

    # Install Maven and Gradle
    sdk install maven
    sdk install gradle

    print_success "Maven and Gradle installed"
fi

#===============================================================================
# .NET SDK
#===============================================================================

if [ "$INSTALL_DOTNET" = true ]; then
    print_header "Installing .NET SDK"

    # Add Microsoft package repository
    wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    rm packages-microsoft-prod.deb

    sudo apt update
    sudo apt install -y dotnet-sdk-$DOTNET_VERSION

    print_success ".NET SDK $DOTNET_VERSION installed"
fi

#===============================================================================
# Docker (Native in WSL)
#===============================================================================

if [ "$INSTALL_DOCKER" = true ]; then
    print_header "Installing Docker"

    # Remove old versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Install prerequisites
    sudo apt install -y ca-certificates curl gnupg

    # Add Docker official GPG key
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null || true
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt update

    # Install Docker Engine, CLI, Compose plugin, and Buildx
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add user to docker group (no sudo needed for docker commands)
    sudo usermod -aG docker $USER

    # Start Docker service
    sudo service docker start

    # Configure Docker autostart via /etc/wsl.conf
    WSL_CONF="/etc/wsl.conf"
    if ! grep -q "\[boot\]" "$WSL_CONF" 2>/dev/null; then
        echo "" | sudo tee -a "$WSL_CONF" >/dev/null
        echo "[boot]" | sudo tee -a "$WSL_CONF" >/dev/null
        echo "command=service docker start" | sudo tee -a "$WSL_CONF" >/dev/null
        print_success "Docker autostart configured in /etc/wsl.conf"
    elif ! grep -q "command.*service.*docker" "$WSL_CONF" 2>/dev/null; then
        sudo sed -i '/^\[boot\]/a command=service docker start' "$WSL_CONF"
        print_success "Docker autostart added to existing [boot] section"
    else
        print_info "Docker autostart already configured in /etc/wsl.conf"
    fi

    # Configure passwordless sudo for docker service commands
    SUDOERS_FILE="/etc/sudoers.d/docker-autostart"
    REAL_USER="${SUDO_USER:-$USER}"
    if [ ! -f "$SUDOERS_FILE" ]; then
        echo "$REAL_USER ALL=(ALL) NOPASSWD: /usr/sbin/service docker start, /usr/sbin/service docker stop, /usr/sbin/service docker restart, /usr/sbin/service docker status" | sudo tee "$SUDOERS_FILE" >/dev/null
        sudo chmod 440 "$SUDOERS_FILE"
        if sudo visudo -cf "$SUDOERS_FILE" &>/dev/null; then
            print_success "Passwordless Docker service management configured"
        else
            sudo rm -f "$SUDOERS_FILE"
            print_warning "Could not configure passwordless sudo (non-critical)"
        fi
    fi

    # Verify installation
    if docker --version &> /dev/null; then
        print_success "Docker $(docker --version | awk '{print $3}') installed"
    fi
    if docker compose version &> /dev/null; then
        print_success "Docker Compose $(docker compose version --short) installed"
    fi

    print_warning "Log out and back in (or run 'newgrp docker') for group to take effect"
fi

#===============================================================================
# Create Project Directory Structure
#===============================================================================

print_header "Creating Directory Structure"

mkdir -p ~/projects
mkdir -p ~/tools
mkdir -p ~/scripts

print_success "Directories created: ~/projects, ~/tools, ~/scripts"

#===============================================================================
# VS Code Server Check
#===============================================================================

print_header "VS Code Integration"

if command -v code &> /dev/null; then
    print_success "VS Code CLI available"
    print_info "Open projects with: code ~/projects/your-project"
else
    print_warning "VS Code CLI not found"
    print_info "Open VS Code in Windows and install the 'WSL' extension"
    print_info "Then run 'code .' from WSL terminal"
fi

#===============================================================================
# Generate and install .wslconfig on Windows
#===============================================================================

print_header "Configuring .wslconfig (Windows Resource Limits)"

# Detect Windows username
WIN_USER=$(cmd.exe /C "echo %USERNAME%" 2>/dev/null | tr -d '\r\n' || echo "")
# Filter out system/service accounts
if [ -z "$WIN_USER" ] || [ "$WIN_USER" = "WsiAccount" ] || [ "$WIN_USER" = "SYSTEM" ]; then
    WIN_USER=$(ls /mnt/c/Users/ 2>/dev/null | grep -v -E "^(Public|Default|Default User|All Users|desktop.ini|WsiAccount|defaultuser0)$" | head -1)
fi
# Second fallback: SUDO_USER's name might match Windows user
REAL_USER="${SUDO_USER:-$USER}"
if [ -z "$WIN_USER" ] && [ -d "/mnt/c/Users/$REAL_USER" ]; then
    WIN_USER="$REAL_USER"
fi

WSLCONFIG_PATH="/mnt/c/Users/$WIN_USER/.wslconfig"
WSLCONFIG_TEMPLATE="$HOME/wslconfig-template.txt"

# Detect real hardware
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))
TOTAL_CPUS=$(nproc)

# Calculate optimal values
RECOMMENDED_RAM=$((TOTAL_RAM_GB / 2))
[ "$RECOMMENDED_RAM" -lt 4 ] && RECOMMENDED_RAM=4

RECOMMENDED_CPUS=$((TOTAL_CPUS / 2))
[ "$RECOMMENDED_CPUS" -lt 2 ] && RECOMMENDED_CPUS=2

RECOMMENDED_SWAP=$((RECOMMENDED_RAM / 4))
[ "$RECOMMENDED_SWAP" -lt 2 ] && RECOMMENDED_SWAP=2

print_info "Hardware detected: ${TOTAL_RAM_GB}GB RAM, ${TOTAL_CPUS} CPUs"
print_info "Recommended:       memory=${RECOMMENDED_RAM}GB, processors=${RECOMMENDED_CPUS}, swap=${RECOMMENDED_SWAP}GB"

WSLCONFIG_CONTENT="# WSL2 Resource Configuration
# Generated by wsl2-setup.sh on $(date +%Y-%m-%d)
# Hardware: ${TOTAL_RAM_GB}GB RAM, ${TOTAL_CPUS} CPUs
#
# To apply changes: wsl --shutdown (from PowerShell)

[wsl2]
memory=${RECOMMENDED_RAM}GB
processors=${RECOMMENDED_CPUS}
swap=${RECOMMENDED_SWAP}GB
localhostForwarding=true

# Disable page reporting for more predictable memory usage
# pageReporting=false

# Enable nested virtualization (Docker-in-Docker, Kind, etc.)
# nestedVirtualization=true"

# Save template locally (always)
echo "$WSLCONFIG_CONTENT" > "$WSLCONFIG_TEMPLATE"
print_success "Template saved: $WSLCONFIG_TEMPLATE"

# Install directly to Windows if possible
if [ -n "$WIN_USER" ] && [ -d "/mnt/c/Users/$WIN_USER" ]; then
    if [ -f "$WSLCONFIG_PATH" ]; then
        print_info "Existing .wslconfig found — backing up"
        cp "$WSLCONFIG_PATH" "${WSLCONFIG_PATH}.bak.$(date +%Y%m%d%H%M%S)"
    fi
    echo "$WSLCONFIG_CONTENT" > "$WSLCONFIG_PATH"
    print_success ".wslconfig installed at: C:\\Users\\${WIN_USER}\\.wslconfig"
    print_warning "Run 'wsl --shutdown' from PowerShell to apply."
else
    print_warning "Could not detect Windows user home."
    print_info "Copy manually: cp $WSLCONFIG_TEMPLATE /mnt/c/Users/YOUR_USERNAME/.wslconfig"
fi

#===============================================================================
# Summary
#===============================================================================

print_header "Installation Complete!"

echo -e "Installed components:"
echo -e "  • Essential build tools"
echo -e "  • Git (with WSL-optimized config)"
[ "$INSTALL_ZSH" = true ] && echo -e "  • ZSH + Oh My Zsh"
[ "$INSTALL_NVM" = true ] && echo -e "  • NVM + Node.js $(node --version 2>/dev/null || echo '')"
[ "$INSTALL_SDKMAN" = true ] && echo -e "  • SDKMAN + Java"
[ "$INSTALL_DOTNET" = true ] && echo -e "  • .NET SDK $DOTNET_VERSION"
[ "$INSTALL_DOCKER" = true ] && echo -e "  • Docker (with autostart configured)"

echo ""
print_warning "IMPORTANT NEXT STEPS:"
echo ""
echo "1. Restart WSL from PowerShell to apply .wslconfig limits:"
echo "   wsl --shutdown"
echo ""
echo "2. Start a new terminal session to apply all changes"
echo "   Docker will start automatically — no manual 'sudo service docker start' needed."
echo ""
echo "3. Keep your code in: ~/projects/"
echo "   NOT in /mnt/c/ (slow!)"
echo ""
echo "4. (Optional) Auto-start WSL on Windows login:"
echo "   Run windows-autostart.ps1 from PowerShell (as Admin)"
echo ""

if [ "$INSTALL_ZSH" = true ]; then
    print_info "Restart your terminal or run: exec zsh"
fi

print_success "Setup complete!"
