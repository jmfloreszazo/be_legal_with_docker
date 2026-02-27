#===============================================================================
# Windows Autostart for WSL2 + Docker
# Run this script from PowerShell AS ADMINISTRATOR to create a Windows
# scheduled task that starts WSL and Docker on every Windows login.
#
# Author: Jose Maria Flores Zazo - https://jmfloreszazo.com
#===============================================================================

param(
    [string]$DistroName = "Ubuntu",
    [switch]$Remove,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$TaskName = "WSL2-Docker-Autostart"

function Write-Header($msg) {
    Write-Host ""
    Write-Host ("=" * 64) -ForegroundColor Blue
    Write-Host "  $msg" -ForegroundColor Blue
    Write-Host ("=" * 64) -ForegroundColor Blue
    Write-Host ""
}

function Write-Ok($msg)   { Write-Host "[OK]  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!!]  $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR] $msg" -ForegroundColor Red }
function Write-Inf($msg)  { Write-Host "[->]  $msg" -ForegroundColor Cyan }

#===============================================================================
# Admin check
#===============================================================================

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Err "This script must be run as Administrator."
    Write-Inf "Right-click PowerShell -> 'Run as Administrator'"
    exit 1
}

#===============================================================================
# Remove mode
#===============================================================================

if ($Remove) {
    Write-Header "Removing Scheduled Task: $TaskName"

    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:(-not $Force)
        Write-Ok "Task '$TaskName' removed."
    } else {
        Write-Warn "Task '$TaskName' does not exist."
    }
    exit 0
}

#===============================================================================
# Verify WSL
#===============================================================================

Write-Header "WSL2 Docker Autostart - Windows Task Scheduler"

Write-Inf "Checking WSL installation..."

$wslPath = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslPath) {
    Write-Err "wsl.exe not found. Install WSL first."
    exit 1
}
Write-Ok "WSL found at: $($wslPath.Source)"

# Check distro exists
$distros = wsl.exe --list --quiet 2>$null | Where-Object { $_ -match '\S' } | ForEach-Object { $_.Trim() -replace '\x00','' }
if ($distros -notcontains $DistroName) {
    Write-Err "Distro '$DistroName' not found. Available distros:"
    $distros | ForEach-Object { Write-Inf "  - $_" }
    Write-Inf "Use -DistroName parameter to specify a different distro."
    exit 1
}
Write-Ok "Distro found: $DistroName"

#===============================================================================
# Check if task already exists
#===============================================================================

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask -and -not $Force) {
    Write-Warn "Task '$TaskName' already exists."
    Write-Inf "Use -Force to overwrite, or -Remove to delete it."
    exit 0
}

if ($existingTask -and $Force) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Inf "Existing task removed (will recreate)."
}

#===============================================================================
# Create startup script
#===============================================================================

Write-Header "Creating Startup Configuration"

# The action: start WSL distro and run docker start as root
# wsl -d <distro> -u root -- service docker start
# This boots WSL if not running and starts Docker inside it.

$action = New-ScheduledTaskAction `
    -Execute "wsl.exe" `
    -Argument "-d $DistroName -u root -- service docker start"

Write-Ok "Action: wsl.exe -d $DistroName -u root -- service docker start"

#===============================================================================
# Configure trigger: at user logon
#===============================================================================

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
Write-Ok "Trigger: At logon for user '$env:USERNAME'"

#===============================================================================
# Configure settings
#===============================================================================

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Write-Ok "Settings: allow on battery, retry 3x, 5-min timeout"

#===============================================================================
# Register task
#===============================================================================

Write-Header "Registering Scheduled Task"

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Starts WSL2 ($DistroName) and Docker service on Windows login. Created by be_legal_with_docker setup." | Out-Null

Write-Ok "Task '$TaskName' registered successfully."

#===============================================================================
# Verify
#===============================================================================

Write-Header "Verification"

$task = Get-ScheduledTask -TaskName $TaskName
Write-Ok "Task Name:   $($task.TaskName)"
Write-Ok "Status:      $($task.State)"
Write-Ok "Trigger:     At logon"
Write-Ok "Command:     wsl.exe -d $DistroName -u root -- service docker start"

#===============================================================================
# Summary
#===============================================================================

Write-Header "Setup Complete"

Write-Host "What happens now:"
Write-Host "  1. When you log into Windows, WSL ($DistroName) will start automatically"
Write-Host "  2. Docker service will start inside WSL"
Write-Host "  3. Containers with restart policies will resume"
Write-Host "  4. Ports are forwarded to localhost (if .wslconfig has localhostForwarding=true)"
Write-Host ""
Write-Warn "Test it now by running:"
Write-Host "  schtasks /Run /TN `"$TaskName`""
Write-Host ""
Write-Inf "To remove this task later:"
Write-Host "  .\windows-autostart.ps1 -Remove"
Write-Host ""
Write-Ok "Done!"
