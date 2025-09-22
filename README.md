# bmse-midi: Blackmagic Speed Editor for Lightroom Classic (MIDI2LR)

Use your Blackmagic Design Speed Editor as a customizable MIDI controller, optimized for integration with Adobe Lightroom Classic via MIDI2LR.

## Features

*   **Customizable Key Mappings**: Define MIDI messages for each Speed Editor key in `config/key_mappings.json`.
*   **Multiple Profiles**: Switch between different key mappings  for different workflows (e.g., 'Develop' and 'Library').
*   **Jog Wheel Support**: Configurable jog wheel behavior with different modes (shuttle, jog, scroll) and sensitivity.
*   **LED Feedback**: Visual feedback on the Speed Editor's LEDs based on key states and jog modes.
*   **Cross-Platform**: Supports Windows, macOS, and Linux.

## Installation

### Prerequisites

*   **Python 3.x**: Ensure you have Python 3 installed on your system.
*   **MIDI2LR (Optional)**: If you intend to use this with Adobe Lightroom Classic, download and install [MIDI2LR](https://github.com/rsjaffe/MIDI2LR).

### 1. Clone the Repository and Initialize Submodules

First, clone this repository and initialize the `blackmagic-speededitor` submodule:

```bash
git clone https://github.com/user/bmse-midi.git
cd bmse-midi
git submodule update --init --recursive
```

### 2. Create and Activate Python Virtual Environment

It's recommended to use a Python virtual environment to manage dependencies.

From the project root:

```bash
# Create virtual environment
(bmse-midi)$ python -m venv venv

# Activate virtual environment
# Windows PowerShell
(bmse-midi)$ .\venv\Scripts\activate

# macOS/Linux
(bmse-midi)$ source venv/bin/activate
```

### 3. Install Python Dependencies

Install the required Python packages for your operating system within the activated virtual environment. For Windows-specific considerations regarding Python dependencies (e.g., C++ compiler and `hidapi.dll`), please refer to `windows/README.md`.

From the project root:

```bash
# For Windows
(bmse-midi)$ pip install -r requirements_windows.txt

# For macOS/Linux
(bmse-midi)$ pip install -r requirements_macos.txt
```

### 4. Virtual MIDI Port Setup (Windows Only)

Windows requires a virtual MIDI port to connect the Speed Editor to MIDI2LR. Please refer to the detailed instructions in `windows/README.md` for setting up `loopMIDI` or an alternative.

### 5. MIDI2LR Configuration (Optional)

If you are using MIDI2LR, you can import the provided configuration file:

1.  Open MIDI2LR.
2.  Go to `File > Import Configuration...`.
3.  Navigate to the `config` directory in your project and select `bmse-midi2lr-windows.txt` (for Windows) or `bmse-midi2lr.txt` (for macOS/Linux).
4.  Click `Open`.

## Running the MIDI Controller

After completing the setup, you can run the main MIDI controller script.

From the project root (with your virtual environment activated):

```bash
(bmse-midi)$ python src/speed_editor_midi.py
```

The script will automatically:
*   Detect your Speed Editor.
*   Set up appropriate MIDI ports (referencing your virtual port on Windows).
*   Load the configured key mappings from `config/key_mappings.json`.
*   Start listening for key presses and jog wheel movements.

## Configuration

Key mappings and jog wheel behaviors are defined in `config/key_mappings.json`. This file supports multiple profiles.

### Structure of `key_mappings.json`

The configuration defines profiles, each containing mappings for Speed Editor keys. Keys can have different behaviors:

*   `SINGLE`: Executes a command on a single press.
*   `TOGGLE`: Toggles a state (e.g., LED on/off) and sends different commands for 'on' and 'off' transitions.
*   `JOG`: Activates jog wheel control when held, and can also have a 'double_tap' action.
*   `PROFILE`: Switches to a different profile.

### Customizing Mappings & Generating XML Profiles for MIDI2LR

The XML profiles that MIDI2LR consumes are generated from `config/key_mappings.json`.

They should never be updated by hand, just edit the JSON and run:

```bash
(bmse-midi)$ python src/generate_profiles.py
```

You will need to either restart MIDI2LR or just swap profiles.


## Project Structure

```
bmse-midi/
├── config/
│   ├── bmse-midi2lr-windows.txt
│   ├── bmse-midi2lr.txt
│   ├── key_mappings.json
│   ├── profiles/
│   │   ├── BMSpeedEditor-Edit.xml
│   │   └── BMSpeedEditor-Library.xml
├── external/
│   └── blackmagic-speededitor/  # Blackmagic Speed Editor Python library (Git submodule)
├── requirements_macos.txt
├── requirements_windows.txt
├── src/
│   ├── generate_profiles.py     # Script to generate XML profiles
│   ├── key_types.py             # Defines key behavior and types
│   └── speed_editor_midi.py     # Main MIDI controller script
├── tests/
│   ├── dummy_speed_editor.py    # Dummy Speed Editor for testing
│   └── test_dummy_speed_editor.py # Unit tests
└── windows/
    ├── diagnose_midi.py       # Windows MIDI diagnostic tool
    └── README.md              # Windows-specific setup instructions

```

## Attribution

This project utilizes the following Git submodule:

*   **blackmagic-speededitor**: A Python library for interacting with the Blackmagic Design Speed Editor. [https://github.com/octimot/blackmagic-speededitor](https://github.com/octimot/blackmagic-speededitor)

All of which is forked/inspired by:
*   **blackmagic-misc**: Miscellaneous projects related to Blackmagic Design products/software. [https://github.com/smunaut/blackmagic-misc](https://github.com/smunaut/blackmagic-misc)

Please refer to the respective repositories for their specific licensing information.

## AI Assistance 🤖

  This project has leveraged LLM's for various development tasks including code generation, refactoring suggestions, documentation improvements, and slight modifications to **Asimov's Three Laws**.

  ✨AI-assisted code has been ~~mostly~~ thoroughly reviewed and validated by flesh bags with fingers and keyboards, who retain all credit for its genius without any liability for its folly.✨