# Windows MIDI Setup

This directory contains scripts and information for setting up MIDI functionality on Windows, specifically for the BlackMagic Speed Editor.

## 1. Pre-installation for Windows

Some Python packages require a C++ compiler during installation. On Windows, you'll need:

**Visual Studio Build Tools**
1.  **Download the installer**: Go to the [Visual Studio Downloads page](https://visualstudio.microsoft.com/downloads/) and scroll down to "Tools for Visual Studio". Download the "Build Tools for Visual Studio".
2.  **Run the installer**: In the "Workloads" tab, check the box for "Desktop development with C++".

**Use the Correct Command Prompt**
To ensure the C++ compiler is correctly recognized, use the dedicated command prompt:
1.  Open the Windows Start Menu and type `x64 Native Tools`.
2.  Select the "x64 Native Tools Command Prompt for VS" to open it.
3.  In this new command prompt, navigate to your project folder.

### For HIDAPI DLL
If you encounter a `FileNotFoundError` related to `hidapi.dll` during or after installing Python dependencies, it means the underlying C library for the `hid` Python package is missing from your system PATH.

1.  **Download the `hidapi.dll` Library**: Go to the official [hidapi releases page on GitHub](https://github.com/libusb/hidapi/releases).
2.  **Locate the Correct DLL**: Download the appropriate `hidapi.dll` for your system (usually `x64` for 64-bit Windows).
3.  **Place the DLL**: Copy `hidapi.dll` into one of the following locations:
    *   The `System32` directory (e.g., `C:\Windows\System32`).
    *   The directory where your Python executable is located (e.g., `path\to\your\venv\Scripts`).
    *   Any directory included in your system's PATH environment variable.

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

