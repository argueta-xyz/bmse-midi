#!/usr/bin/env python3
"""
Diagnostic script to help troubleshoot Windows MIDI setup issues
"""

import os
import sys
import subprocess
import platform

def check_system_info():
    """Check basic system information."""
    print("System Information")
    print("=" * 40)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Python: {sys.version}")
    print()

def check_midi_ports():
    """Check available MIDI ports."""
    print("Available MIDI Ports")
    print("=" * 40)
    try:
        import mido
        output_names = mido.get_output_names()
        input_names = mido.get_input_names()

        print("Output ports:")
        for i, port in enumerate(output_names, 1):
            print(f"  {i}. {port}")

        print("\nInput ports:")
        for i, port in enumerate(input_names, 1):
            print(f"  {i}. {port}")

        if not output_names and not input_names:
            print("No MIDI ports found!")
            print("This might indicate a driver issue.")

    except ImportError:
        print("mido library not installed. Install with: pip install mido")
    except Exception as e:
        print(f"Error checking MIDI ports: {e}")
    print()

def check_loopmidi_installation():
    """Check for loopMIDI installation."""
    print("loopMIDI Installation Check")
    print("=" * 40)

    # Check using where command
    print("Checking with 'where' command:")
    possible_names = ['loopMIDI', 'loopMidi', 'loopmidi', 'LoopMIDI']
    found_any = False

    for name in possible_names:
        try:
            result = subprocess.run(['where', name], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                print(f"  ✓ Found: {result.stdout.strip()}")
                found_any = True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            continue

    if not found_any:
        print("  ✗ Not found in PATH")

    # Check common installation paths
    print("\nChecking common installation paths:")
    possible_paths = [
        r"C:\Program Files\loopMIDI\loopMIDI.exe",
        r"C:\Program Files\loopMIDI\loopMidi.exe",
        r"C:\Program Files (x86)\loopMIDI\loopMIDI.exe",
        r"C:\Program Files (x86)\loopMIDI\loopMidi.exe",
        os.path.expanduser(r"~\AppData\Local\loopMIDI\loopMIDI.exe"),
        os.path.expanduser(r"~\AppData\Local\loopMIDI\loopMidi.exe"),
        r"C:\Program Files\Tobias Erichsen\loopMIDI\loopMIDI.exe",
        r"C:\Program Files\Tobias Erichsen\loopMIDI\loopMidi.exe",
    ]

    found_path = False
    for path in possible_paths:
        if os.path.exists(path):
            print(f"  ✓ Found: {path}")
            found_path = True

    if not found_path:
        print("  ✗ Not found in common locations")

    # Check if loopMIDI is running
    print("\nChecking if loopMIDI is running:")
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq loopMIDI.exe'],
                              capture_output=True, text=True, timeout=5)
        if 'loopMIDI.exe' in result.stdout:
            print("  ✓ loopMIDI is running")
        else:
            print("  ✗ loopMIDI is not running")
    except Exception as e:
        print(f"  ✗ Error checking process: {e}")

    print()

def check_alternative_midi_software():
    """Check for alternative virtual MIDI software."""
    print("Alternative Virtual MIDI Software")
    print("=" * 40)

    # Check for LoopBe1
    loopbe_paths = [
        r"C:\Program Files\LoopBe1\LoopBe1.exe",
        r"C:\Program Files (x86)\LoopBe1\LoopBe1.exe",
        r"C:\Program Files\NCH Software\LoopBe1\LoopBe1.exe",
    ]

    found_loopbe = False
    for path in loopbe_paths:
        if os.path.exists(path):
            print(f"  ✓ LoopBe1 found: {path}")
            found_loopbe = True

    if not found_loopbe:
        print("  ✗ LoopBe1 not found")

    # Check for other common virtual MIDI software
    other_software = [
        ("rtpMIDI", r"C:\Program Files\rtpMIDI\rtpMIDI.exe"),
        ("MIDI Yoke", r"C:\Program Files (x86)\MIDI Yoke\MYOKE.EXE"),
    ]

    for name, path in other_software:
        if os.path.exists(path):
            print(f"  ✓ {name} found: {path}")

    print()

def check_drivers():
    """Check for MIDI-related drivers."""
    print("MIDI Driver Check")
    print("=" * 40)

    try:
        # Check for teVirtualMIDI driver (used by loopMIDI)
        result = subprocess.run(['driverquery', '|', 'findstr', 'teVirtualMIDI'],
                              shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print("  ✓ teVirtualMIDI driver found")
        else:
            print("  ✗ teVirtualMIDI driver not found")
            print("    This driver is required for loopMIDI to work")
    except Exception as e:
        print(f"  ✗ Error checking drivers: {e}")

    print()

def provide_recommendations():
    """Provide recommendations based on findings."""
    print("Recommendations")
    print("=" * 40)

    try:
        import mido
        output_names = mido.get_output_names()

        if not output_names:
            print("No MIDI output ports found. Try:")
            print("1. Install loopMIDI: https://www.tobias-erichsen.de/software/loopmidi.html")
            print("2. Or install LoopBe1: https://www.nerds.de/en/loopbe1.html")
            print("3. Restart your computer after installation")
            print("4. Make sure to run the installer as Administrator")
        else:
            print("MIDI ports are available. You should be able to use the controller.")
            print("If you're still having issues, check MIDI2LR settings.")

    except ImportError:
        print("Install required Python packages:")
        print("  pip install mido python-rtmidi")
    except Exception as e:
        print(f"Error checking MIDI setup: {e}")

    print()

def main():
    """Run all diagnostic checks."""
    print("Windows MIDI Setup Diagnostic Tool")
    print("=" * 50)
    print()

    if platform.system() != 'Windows':
        print("This diagnostic tool is for Windows only.")
        return

    check_system_info()
    check_midi_ports()
    check_loopmidi_installation()
    check_alternative_midi_software()
    check_drivers()
    provide_recommendations()

    print("Diagnostic complete!")
    print("If you're still having issues, please share this output for troubleshooting.")

if __name__ == '__main__':
    main()
