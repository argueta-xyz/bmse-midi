# PowerShell script to set up Windows MIDI for BlackMagic Speed Editor

Write-Host "Setting up Windows MIDI for BlackMagic Speed Editor" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check for loopMIDI installation
$loopMidiPaths = @(
    "C:\Program Files\loopMIDI\loopMIDI.exe",
    "C:\Program Files (x86)\loopMIDI\loopMIDI.exe",
    "$env:LOCALAPPDATA\loopMIDI\loopMIDI.exe"
)

$loopMidiPath = $null
foreach ($path in $loopMidiPaths) {
    if (Test-Path $path) {
        $loopMidiPath = $path
        break
    }
}

if (-not $loopMidiPath) {
    Write-Host ""
    Write-Host "loopMIDI not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install loopMIDI from:" -ForegroundColor Yellow
    Write-Host "https://www.tobias-erichsen.de/software/loopmidi.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "loopMIDI found at: $loopMidiPath" -ForegroundColor Green
Write-Host ""

# Check if loopMIDI is running
$loopMidiProcess = Get-Process -Name "loopMIDI" -ErrorAction SilentlyContinue
if ($loopMidiProcess) {
    Write-Host "loopMIDI is already running." -ForegroundColor Green
} else {
    Write-Host "Starting loopMIDI..." -ForegroundColor Yellow
    Start-Process -FilePath $loopMidiPath
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Virtual MIDI Port Setup Instructions:" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. In the loopMIDI window that just opened:" -ForegroundColor White
Write-Host "   - Enter 'BMSpeedEditor' in the 'New port-name' field" -ForegroundColor Gray
Write-Host "   - Click the '+' button to create the port" -ForegroundColor Gray
Write-Host "   - The port should appear in the list below" -ForegroundColor Gray
Write-Host ""
Write-Host "2. In MIDI2LR:" -ForegroundColor White
Write-Host "   - Go to File > Preferences" -ForegroundColor Gray
Write-Host "   - Set MIDI Input Device to 'loopMIDI Port: BMSpeedEditor'" -ForegroundColor Gray
Write-Host "   - Click OK" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run the Python script:" -ForegroundColor White
Write-Host "   python speed-editor-midi.py" -ForegroundColor Gray
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter when you have completed the setup"

Write-Host ""
Write-Host "Testing MIDI setup..." -ForegroundColor Yellow
try {
    python windows/midi_setup.py
} catch {
    Write-Host "Error running MIDI setup test: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete! You can now run: python speed-editor-midi.py" -ForegroundColor Green
Read-Host "Press Enter to exit"
