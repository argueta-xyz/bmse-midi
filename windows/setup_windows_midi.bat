@echo off
echo Setting up Windows MIDI for BlackMagic Speed Editor
echo ==================================================

echo.
echo Checking for loopMIDI installation...

REM Check common installation paths
set LOOPMIDI_PATH=""
if exist "C:\Program Files\loopMIDI\loopMIDI.exe" (
    set LOOPMIDI_PATH="C:\Program Files\loopMIDI\loopMIDI.exe"
) else if exist "C:\Program Files (x86)\loopMIDI\loopMIDI.exe" (
    set LOOPMIDI_PATH="C:\Program Files (x86)\loopMIDI\loopMIDI.exe"
) else if exist "%LOCALAPPDATA%\loopMIDI\loopMIDI.exe" (
    set LOOPMIDI_PATH="%LOCALAPPDATA%\loopMIDI\loopMIDI.exe"
)

if "%LOOPMIDI_PATH%"=="" (
    echo.
    echo loopMIDI not found!
    echo.
    echo Please install loopMIDI from:
    echo https://www.tobias-erichsen.de/software/loopmidi.html
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo loopMIDI found at: %LOOPMIDI_PATH%
echo.

REM Check if loopMIDI is running
tasklist /FI "IMAGENAME eq loopMIDI.exe" 2>NUL | find /I /N "loopMIDI.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo loopMIDI is already running.
) else (
    echo Starting loopMIDI...
    start "" %LOOPMIDI_PATH%
    timeout /t 3 >nul
)

echo.
echo ==================================================
echo Virtual MIDI Port Setup Instructions:
echo ==================================================
echo.
echo 1. In the loopMIDI window that just opened:
echo    - Enter "BMSpeedEditor" in the "New port-name" field
echo    - Click the "+" button to create the port
echo    - The port should appear in the list below
echo.
echo 2. In MIDI2LR:
echo    - Go to File > Preferences
echo    - Set MIDI Input Device to "loopMIDI Port: BMSpeedEditor"
echo    - Click OK
echo.
echo 3. Run the Python script:
echo    python speed-editor-midi.py
echo.
echo ==================================================
echo.
echo Press any key when you have completed the setup...
pause >nul

echo.
echo Testing MIDI setup...
python windows/midi_setup.py

echo.
echo Setup complete! You can now run: python speed-editor-midi.py
pause
