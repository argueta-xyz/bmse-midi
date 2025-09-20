# PowerShell script to install Windows dependencies for BlackMagic Speed Editor MIDI

param(
    [switch]$Force
)

Write-Host "Installing Windows dependencies for BlackMagic Speed Editor MIDI" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges to install loopMIDI." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Chocolatey is installed
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if (-not $chocoInstalled) {
    Write-Host "Installing Chocolatey package manager..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "Chocolatey installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install Chocolatey: $_" -ForegroundColor Red
        Write-Host "Please install loopMIDI manually from: https://www.tobias-erichsen.de/software/loopmidi.html" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Install loopMIDI
Write-Host "Installing loopMIDI..." -ForegroundColor Yellow
try {
    if ($Force) {
        choco install loopmidi -y --force
    } else {
        choco install loopmidi -y
    }
    Write-Host "loopMIDI installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to install loopMIDI: $_" -ForegroundColor Red
    Write-Host "Please install loopMIDI manually from: https://www.tobias-erichsen.de/software/loopmidi.html" -ForegroundColor Yellow
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        Write-Host "Python dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "requirements.txt not found, installing basic dependencies..." -ForegroundColor Yellow
        pip install hid mido python-rtmidi
    }
} catch {
    Write-Host "Failed to install Python dependencies: $_" -ForegroundColor Red
    Write-Host "Please install manually: pip install hid mido python-rtmidi" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run setup_windows_midi.ps1 to configure the virtual MIDI port" -ForegroundColor White
Write-Host "2. Run python speed-editor-midi.py to start the MIDI controller" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
