# bmse-midi
Blackmagic Speed Editor MIDI Interface

## Installation

### Prerequisites
1. Install MIDI2LR
2. Edit Controllers.xml (OS dependent location) to set table_data.data.item["output"]["active"] = 0
3. Set profiles directory to `{REPO}/profiles`

### Windows Setup
Windows requires a virtual MIDI port to connect the Speed Editor to MIDI2LR:

**Option 1: Automated Setup (Recommended)**
```cmd
# Run the batch script
windows/setup_windows_midi.bat

# Or run the PowerShell script
powershell -ExecutionPolicy Bypass -File windows/setup_windows_midi.ps1
```

**Option 2: Manual Setup**
1. Download and install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Open loopMIDI and create a virtual port named "BMSpeedEditor"
3. In MIDI2LR, set MIDI Input Device to "loopMIDI Port: BMSpeedEditor"

**Troubleshooting**
If you're having issues with MIDI setup, run the diagnostic tool:
```cmd
python windows/diagnose_midi.py
```

This will check your system and provide specific recommendations.

### macOS/Linux Setup
No additional setup required - the script will automatically detect and use available MIDI ports.

## Running the Script

### Windows
```cmd
# Activate virtual environment (if using one)
.venv\Scripts\activate

# Run the MIDI controller
python speed-editor-midi.py
```

### macOS/Linux
```bash
# Activate virtual environment (if using one)
source .venv/bin/activate

# Run the MIDI controller
python3 speed-editor-midi.py
```

The script will automatically:
- Detect your Speed Editor
- Set up appropriate MIDI ports (including virtual ports on Windows)
- Load the configured key mappings
- Start listening for key presses and jog wheel movements

## Project Structure

```
bmse-midi/
├── blackmagic-speededitor/     # BlackMagic Speed Editor Python library
├── config/                     # Configuration files
│   ├── key_mappings.json      # Key mapping definitions
│   └── bmse-midi2lr.txt       # MIDI2LR configuration
├── profiles/                   # Generated XML profiles for MIDI2LR
│   ├── BMSpeedEditor-Edit.xml
│   └── BMSpeedEditor-Library.xml
├── scripts/                    # Utility scripts
│   └── generate_profiles.py   # Generate XML from JSON config
├── windows/                    # Windows-specific files
│   ├── midi_setup.py          # Windows MIDI port setup
│   ├── setup_windows_midi.bat # Windows setup script (batch)
│   ├── setup_windows_midi.ps1 # Windows setup script (PowerShell)
│   └── install_windows_dependencies.ps1 # Dependency installer
├── speed-editor-midi.py       # Main MIDI controller script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Configuration

Key mappings are defined in `config/key_mappings.json` and support multiple profiles with different interaction modes:

- **single_tap**: Command executed on single key press
- **double_tap**: Command executed on double key press (for keys with jog wheel support)
- **jog**: Command executed when turning jog wheel while key is held (for keys with jog wheel support)

### Profiles

#### Edit Profile
- **Purpose**: Photo editing with jog wheel support for parameter adjustment
- **Jog Wheel Keys**: CAM1-CAM9 keys support jog wheel interaction (defined by `jog` mapping)
- **Double-tap**: Resets the associated parameter
- **Jog**: Adjusts the parameter while key is held

#### Library Profile
- **Purpose**: Photo browsing and selection
- **Interaction**: Simple single-tap commands for navigation

### Generating XML Profiles

XML profiles are generated from the JSON configuration:

```bash
python3 scripts/generate_profiles.py config/key_mappings.json
```

This creates the XML files in the `profiles/` directory that MIDI2LR can load.

### Customizing Mappings

Edit `config/key_mappings.json` to customize key mappings:

1. Modify existing mappings in the `profiles` section
2. Add new profiles by creating new profile objects
3. Update jog modes in the `jog_modes` section
4. Regenerate XML profiles using the script above

Keys automatically support jog wheel functionality when they have a `jog` mapping defined in their profile configuration.

### MIDI Controller Mappings

The current mappings are shown in the generated XML files. Key features:

- **CAM1-CAM9**: Dual-function keys in edit mode (single-tap resets, jog adjusts)
- **Navigation keys**: Standard single-tap commands for photo navigation
- **Jog wheel**: Supports different modes (absolute, relative) for precise control
- **Profile switching**:
  - **SOURCE key**: Switches to library profile + executes `SwToMlibrary` command
  - **TIMELINE key**: Switches to edit profile + executes `SwToMdevelop` command
  - Runtime profile switching also supported via `set_profile()` method
