#!/bin/bash

#===============================================================================
# WSL2 Docker Autostart Configuration
# Run this script inside WSL2 to configure Docker to start automatically
# when WSL boots — no manual 'sudo service docker start' needed.
#
# Author: Jose Maria Flores Zazo · https://jmfloreszazo.com
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() { echo -e "${GREEN}[OK]  $1${NC}"; }
print_warning() { echo -e "${YELLOW}[!!]  $1${NC}"; }
print_error()   { echo -e "${RED}[ERR] $1${NC}"; }
print_info()    { echo -e "${BLUE}[->]  $1${NC}"; }

#===============================================================================
# Pre-flight checks
#===============================================================================

print_header "WSL2 Docker Autostart Configuration"

if ! grep -qEi "(microsoft|wsl)" /proc/version &>/dev/null; then
    print_error "This script must be run inside WSL2."
    exit 1
fi

if ! command -v docker &>/dev/null; then
    print_error "Docker is not installed. Run wsl2-setup.sh first."
    exit 1
fi

print_success "Running in WSL2"
print_success "Docker found: $(docker --version 2>/dev/null | awk '{print $3}')"

# Resolve the real user (not root when run with sudo)
REAL_USER="${SUDO_USER:-$USER}"
if [ "$REAL_USER" = "root" ]; then
    REAL_USER=$(logname 2>/dev/null || echo "")
fi
if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then
    # Last resort: first non-system user with a home
    REAL_USER=$(awk -F: '$3 >= 1000 && $3 < 65534 {print $1; exit}' /etc/passwd)
fi
print_info "Real user: $REAL_USER"

#===============================================================================
# Detect systemd support
#===============================================================================

print_header "Detecting Init System"

WSL_VERSION=$(wsl.exe --version 2>/dev/null | head -1 | tr -d '\r' || echo "unknown")
SUPPORTS_SYSTEMD=false

# WSL 0.67.6+ supports systemd (Windows 11 22H2+)
if command -v systemctl &>/dev/null && systemctl --version &>/dev/null 2>&1; then
    SUPPORTS_SYSTEMD=true
    print_info "systemd is available on this system"
else
    print_info "systemd not available — will use [boot] command approach"
fi

#===============================================================================
# Configure /etc/wsl.conf
#===============================================================================

print_header "Configuring /etc/wsl.conf"

WSL_CONF="/etc/wsl.conf"
BACKUP="/etc/wsl.conf.bak.$(date +%Y%m%d%H%M%S)"

# Backup existing wsl.conf if it exists
if [ -f "$WSL_CONF" ]; then
    sudo cp "$WSL_CONF" "$BACKUP"
    print_info "Backup created: $BACKUP"
fi

# Read existing content (if any)
EXISTING=""
if [ -f "$WSL_CONF" ]; then
    EXISTING=$(cat "$WSL_CONF")
fi

# --- Strategy: use [boot] command to start Docker ---
# This works on ALL WSL2 versions and does not require systemd.

if echo "$EXISTING" | grep -q "\[boot\]"; then
    # [boot] section exists — check if command is already set
    if echo "$EXISTING" | grep -q "command.*=.*docker\|command.*=.*service"; then
        print_info "[boot] command already configured in $WSL_CONF"
        print_info "Current content:"
        grep -A2 "\[boot\]" "$WSL_CONF"
    else
        # Append command under existing [boot] section
        sudo sed -i '/^\[boot\]/a command=service docker start' "$WSL_CONF"
        print_success "Added 'command=service docker start' to existing [boot] section"
    fi
else
    # Add [boot] section
    echo "" | sudo tee -a "$WSL_CONF" >/dev/null
    echo "[boot]" | sudo tee -a "$WSL_CONF" >/dev/null
    echo "command=service docker start" | sudo tee -a "$WSL_CONF" >/dev/null
    print_success "Added [boot] section with Docker autostart"
fi

# --- Optionally enable systemd if supported ---
if [ "$SUPPORTS_SYSTEMD" = true ]; then
    if echo "$EXISTING" | grep -q "systemd.*=.*true"; then
        print_info "systemd already enabled"
    else
        print_info "Enabling systemd for full service management..."
        if echo "$EXISTING" | grep -q "\[boot\]"; then
            # Add systemd=true under [boot] if not present
            if ! grep -q "systemd" "$WSL_CONF"; then
                sudo sed -i '/^\[boot\]/a systemd=true' "$WSL_CONF"
            fi
        fi
        print_success "systemd enabled — Docker will start via systemd unit"

        # Enable Docker service in systemd
        sudo systemctl enable docker 2>/dev/null || true
        print_success "Docker service enabled in systemd"
    fi
fi

# --- Ensure interop is enabled (needed for wsl.exe calls from inside WSL) ---
if ! echo "$EXISTING" | grep -q "\[interop\]"; then
    echo "" | sudo tee -a "$WSL_CONF" >/dev/null
    echo "[interop]" | sudo tee -a "$WSL_CONF" >/dev/null
    echo "enabled=true" | sudo tee -a "$WSL_CONF" >/dev/null
    echo "appendWindowsPath=true" | sudo tee -a "$WSL_CONF" >/dev/null
    print_success "Interop section added"
fi

#===============================================================================
# Configure sudoers for passwordless docker service start
#===============================================================================

print_header "Configuring Passwordless Docker Start"

SUDOERS_FILE="/etc/sudoers.d/docker-autostart"

if [ ! -f "$SUDOERS_FILE" ]; then
    echo "$REAL_USER ALL=(ALL) NOPASSWD: /usr/sbin/service docker start, /usr/sbin/service docker stop, /usr/sbin/service docker restart, /usr/sbin/service docker status" | sudo tee "$SUDOERS_FILE" >/dev/null
    sudo chmod 440 "$SUDOERS_FILE"
    # Validate sudoers syntax
    if sudo visudo -cf "$SUDOERS_FILE" &>/dev/null; then
        print_success "Passwordless Docker service management configured for user '$REAL_USER'"
    else
        print_error "Sudoers syntax error — removing file"
        sudo rm -f "$SUDOERS_FILE"
    fi
else
    print_info "Sudoers rule already exists: $SUDOERS_FILE"
fi

#===============================================================================
# Detect hardware and create/update .wslconfig on Windows side
#===============================================================================

print_header "Configuring Windows .wslconfig"

WIN_USER=$(cmd.exe /C "echo %USERNAME%" 2>/dev/null | tr -d '\r\n' || echo "")
# Filter out system/service accounts
if [ -z "$WIN_USER" ] || [ "$WIN_USER" = "WsiAccount" ] || [ "$WIN_USER" = "SYSTEM" ]; then
    # Fallback: detect from /mnt/c/Users — find directories with actual user profiles
    WIN_USER=$(ls /mnt/c/Users/ 2>/dev/null | grep -v -E "^(Public|Default|Default User|All Users|desktop.ini|WsiAccount|defaultuser0)$" | head -1)
fi
# Second fallback: check if REAL_USER's home has a matching Windows path
if [ -z "$WIN_USER" ] && [ -d "/mnt/c/Users/$REAL_USER" ]; then
    WIN_USER="$REAL_USER"
fi

if [ -n "$WIN_USER" ]; then
    WSLCONFIG_PATH="/mnt/c/Users/$WIN_USER/.wslconfig"
    print_info "Windows user detected: $WIN_USER"

    # --- Detect real hardware ---
    TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))
    TOTAL_CPUS=$(nproc)

    # --- Calculate optimal values ---
    # Memory: 50% of total RAM (minimum 4GB, keeps rest for Windows)
    RECOMMENDED_RAM=$((TOTAL_RAM_GB / 2))
    [ "$RECOMMENDED_RAM" -lt 4 ] && RECOMMENDED_RAM=4

    # Processors: 50% of total (minimum 2, keeps rest for Windows)
    RECOMMENDED_CPUS=$((TOTAL_CPUS / 2))
    [ "$RECOMMENDED_CPUS" -lt 2 ] && RECOMMENDED_CPUS=2

    # Swap: 25% of assigned RAM (minimum 2GB)
    RECOMMENDED_SWAP=$((RECOMMENDED_RAM / 4))
    [ "$RECOMMENDED_SWAP" -lt 2 ] && RECOMMENDED_SWAP=2

    print_info "Hardware detected:"
    print_info "  Total RAM:  ${TOTAL_RAM_GB}GB  ->  WSL assigned: ${RECOMMENDED_RAM}GB (50%)"
    print_info "  Total CPUs: ${TOTAL_CPUS}      ->  WSL assigned: ${RECOMMENDED_CPUS} (50%)"
    print_info "  Swap:       ${RECOMMENDED_SWAP}GB"

    if [ -f "$WSLCONFIG_PATH" ]; then
        print_info "Existing .wslconfig found:"
        cat "$WSLCONFIG_PATH"
        echo ""

        # Check if key settings are present
        HAS_MEM=$(grep -qi "^memory" "$WSLCONFIG_PATH" 2>/dev/null && echo "yes" || echo "no")
        HAS_CPU=$(grep -qi "^processors" "$WSLCONFIG_PATH" 2>/dev/null && echo "yes" || echo "no")
        HAS_FWD=$(grep -qi "localhostForwarding.*=.*true" "$WSLCONFIG_PATH" 2>/dev/null && echo "yes" || echo "no")

        NEEDS_UPDATE=false
        [ "$HAS_MEM" = "no" ] && NEEDS_UPDATE=true
        [ "$HAS_CPU" = "no" ] && NEEDS_UPDATE=true
        [ "$HAS_FWD" = "no" ] && NEEDS_UPDATE=true

        if [ "$NEEDS_UPDATE" = true ]; then
            # Backup and recreate
            cp "$WSLCONFIG_PATH" "${WSLCONFIG_PATH}.bak.$(date +%Y%m%d%H%M%S)"
            print_info "Backup created. Updating .wslconfig..."
        else
            print_success ".wslconfig already has memory, processors, and localhostForwarding"
            print_info "No changes needed. To regenerate, delete .wslconfig and re-run."
            NEEDS_UPDATE=false
        fi
    else
        NEEDS_UPDATE=true
        print_info ".wslconfig does not exist — creating it."
    fi

    if [ "$NEEDS_UPDATE" = true ]; then
        cat > "$WSLCONFIG_PATH" << EOF
# WSL2 Resource Configuration
# Generated by wsl2-autostart.sh on $(date +%Y-%m-%d)
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
# nestedVirtualization=true
EOF
        print_success ".wslconfig created at: C:\\Users\\${WIN_USER}\\.wslconfig"
        print_info "Values: memory=${RECOMMENDED_RAM}GB, processors=${RECOMMENDED_CPUS}, swap=${RECOMMENDED_SWAP}GB"
        echo ""
        print_warning "Run 'wsl --shutdown' from PowerShell to apply resource limits."
    fi
else
    print_warning "Could not detect Windows username."
    print_info "Create .wslconfig manually at C:\\Users\\YOUR_USERNAME\\.wslconfig"
fi

#===============================================================================
# Show final wsl.conf
#===============================================================================

print_header "Final /etc/wsl.conf"

cat "$WSL_CONF"

#===============================================================================
# Summary
#===============================================================================

print_header "Autostart Configuration Complete"

echo -e "What was configured:"
echo -e "  - [boot] command=service docker start  (Docker auto-starts with WSL)"
[ "$SUPPORTS_SYSTEMD" = true ] && echo -e "  - systemd=true  (full service management)"
echo -e "  - Passwordless sudo for docker service commands"
echo -e "  - Interop enabled for Windows integration"
echo ""
print_warning "REQUIRED: Restart WSL to apply changes"
echo ""
echo "  From PowerShell:"
echo "    wsl --shutdown"
echo ""
echo "  Then open a new WSL terminal — Docker will start automatically."
echo ""
print_info "Optional: Run windows-autostart.ps1 from PowerShell (as Admin)"
print_info "to also auto-start WSL on Windows login."
echo ""
print_success "Done!"
