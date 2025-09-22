# Windows MIDI Setup

This directory contains scripts and information for setting up MIDI functionality on Windows, specifically for the BlackMagic Speed Editor.

## 1. Install Dependencies

To use the BlackMagic Speed Editor as a MIDI controller on Windows, you need to install a few dependencies:

### Manual Installation

1.  **Create and Activate Python Virtual Environment**:
    *   Ensure you have Python 3 installed.
    *   In your project's root directory, create a virtual environment:
        ```bash
        (bmse-midi)$ python -m venv venv
        ```
    *   Activate the virtual environment:
        ```bash
        (bmse-midi)$ .\venv\Scripts\activate
        ```

2.  **Install loopMIDI:**
    *   Download loopMIDI from [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html).
    *   Install loopMIDI. You may need to run the installer as an Administrator.
    *   Restart your computer after installation.

3.  **Install Python Dependencies:**
    *   Ensure you have Python 3 installed.
    *   In your project's root directory:
        ```bash
        (bmse-midi)$ pip install -r requirements_windows.txt
        ```

## 2. Configure Virtual MIDI Port

You need to create a virtual MIDI port that the BlackMagic Speed Editor will use.

### Manual Configuration

To use this MIDI controller on Windows, you need virtual MIDI software. loopMIDI is recommended.

#### Option 1 - loopMIDI (Recommended):

1.  Download from: [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)
2.  Install loopMIDI.
3.  Open the `loopMIDI` application.
4.  In the "New port-name" field, enter `BMSpeedEditor`.
5.  Click the `+` button to create the port. The port should appear in the list.

#### Option 2 - LoopBe1 (Alternative):

1.  Download from: [https://www.nerds.de/en/loopbe1.html](https://www.nerds.de/en/loopbe1.html)
2.  Install LoopBe1. It automatically creates a single virtual MIDI port.

## 3. Integrate with MIDI2LR

If you are using MIDI2LR, you can import the provided configuration file:

1.  Open MIDI2LR.
2.  Go to `File > Import Configuration...`.
3.  Navigate to the `config` directory in your `bmse-midi` project and select `bmse-midi2lr-windows.txt`.
4.  Click `Open`.

## 4. Run the MIDI Controller

After setting up the virtual MIDI port, you can run the main Python script from the project root:

```bash
(bmse-midi)$ python src/speed_editor_midi.py
```

## 5. Diagnostic Tool (`diagnose_midi.py`)

If you encounter any issues with your MIDI setup, you can use the `diagnose_midi.py` script to help troubleshoot.


```bash
(bmse-midi)/windows$ python diagnose_midi.py
```

