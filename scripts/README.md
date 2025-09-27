# Release Build System

This directory contains the PyInstaller configuration for creating BMSE MIDI executables across different platforms.

## Building Executables

Run these commands from the project root directory after activating your virtual environment and installing PyInstaller:

**Windows:**
```cmd
.venv\Scripts\activate.bat
pip install pyinstaller
pyinstaller scripts\bmse_midi-windows.spec --clean
```

**macOS:**
```bash
source .venv/bin/activate
pip install pyinstaller
pyinstaller scripts/bmse_midi-macos.spec --clean
```

**Linux:**
```bash
source .venv/bin/activate
pip install pyinstaller
pyinstaller scripts/bmse_midi-linux.spec --clean
```

### Output Locations

- **Windows & Linux:** `dist/bmse_midi/` (contains executable and dependencies)
- **macOS:** `dist/bmse_midi.app/` (application bundle)

## Automated Builds

GitHub Actions automatically builds and creates releases for all platforms when a tag starting with 'v' is pushed, or when manually triggered.

## Configuration

`spec_common.py` contains shared PyInstaller settings, while platform-specific `.spec` files handle platform-specific configurations.

## Troubleshooting

If issues arise, check `spec_common.py` for missing imports or data files, and use the `--clean` flag or delete the `build/` directory.
