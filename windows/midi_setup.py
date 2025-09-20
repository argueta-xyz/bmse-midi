#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def is_windows():
    """Check if running on Windows."""
    return platform.system() == 'Windows'

def check_loopmidi_installed():
    """Check if loopMIDI is installed on Windows."""
    if not is_windows():
        return False
    
    # Common installation paths for loopMIDI
    possible_paths = [
        r"C:\Program Files\loopMIDI\loopMIDI.exe",
        r"C:\Program Files (x86)\loopMIDI\loopMIDI.exe",
        os.path.expanduser(r"~\AppData\Local\loopMIDI\loopMIDI.exe"),
        r"C:\Users\{}\AppData\Local\loopMIDI\loopMIDI.exe".format(os.getenv('USERNAME', '')),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return False

def create_virtual_midi_port(port_name="BMSpeedEditor"):
    """Create a virtual MIDI port using loopMIDI."""
    if not is_windows():
        print("Virtual MIDI port creation is only supported on Windows")
        return False
    
    loopmidi_path = check_loopmidi_installed()
    if not loopmidi_path:
        print("loopMIDI not found. Please install it from: https://www.tobias-erichsen.de/software/loopmidi.html")
        return False
    
    try:
        # Try to create a virtual MIDI port using loopMIDI command line
        # Note: loopMIDI doesn't have a direct command line interface for port creation
        # We'll need to use a different approach or provide instructions
        
        print(f"loopMIDI found at: {loopmidi_path}")
        print(f"Please manually create a virtual MIDI port named '{port_name}' in loopMIDI")
        print("1. Open loopMIDI")
        print(f"2. Enter '{port_name}' in the 'New port-name' field")
        print("3. Click the '+' button to create the port")
        print("4. Press Enter when done...")
        input()
        
        return True
        
    except Exception as e:
        print(f"Error creating virtual MIDI port: {e}")
        return False

def find_virtual_midi_ports():
    """Find available virtual MIDI ports."""
    import mido
    
    try:
        output_names = mido.get_output_names()
        virtual_ports = []
        
        # Look for common virtual MIDI port names
        virtual_keywords = ['loopMIDI', 'Virtual', 'BMSpeedEditor', 'MIDI']
        
        for port_name in output_names:
            if any(keyword in port_name for keyword in virtual_keywords):
                virtual_ports.append(port_name)
        
        return virtual_ports
    except Exception as e:
        print(f"Error finding MIDI ports: {e}")
        return []

def setup_windows_midi():
    """Set up MIDI for Windows with virtual port creation."""
    if not is_windows():
        return None
    
    print("Windows detected. Setting up virtual MIDI port...")
    
    # Check if loopMIDI is installed
    loopmidi_path = check_loopmidi_installed()
    if not loopmidi_path:
        print("\n" + "="*60)
        print("loopMIDI not found!")
        print("="*60)
        print("To use this MIDI controller on Windows, you need to install loopMIDI:")
        print("1. Download from: https://www.tobias-erichsen.de/software/loopmidi.html")
        print("2. Install loopMIDI")
        print("3. Create a virtual MIDI port named 'BMSpeedEditor'")
        print("4. Run this script again")
        print("="*60)
        return None
    
    # Try to find existing virtual ports
    virtual_ports = find_virtual_midi_ports()
    if virtual_ports:
        print(f"Found virtual MIDI ports: {virtual_ports}")
        return virtual_ports[0]  # Use the first one found
    
    # If no virtual ports found, try to create one
    print("No virtual MIDI ports found. Creating one...")
    if create_virtual_midi_port():
        # Wait a moment for the port to be created
        time.sleep(2)
        virtual_ports = find_virtual_midi_ports()
        if virtual_ports:
            print(f"Created virtual MIDI port: {virtual_ports[0]}")
            return virtual_ports[0]
    
    print("Could not create or find a virtual MIDI port")
    return None

def get_midi_output_port():
    """Get the best available MIDI output port."""
    import mido
    
    if is_windows():
        # On Windows, try to use a virtual MIDI port
        virtual_port = setup_windows_midi()
        if virtual_port:
            try:
                return mido.open_output(virtual_port)
            except Exception as e:
                print(f"Could not open virtual MIDI port {virtual_port}: {e}")
    
    # Fallback to any available MIDI port
    try:
        return mido.open_output()
    except Exception as e:
        print(f"Could not open any MIDI output port: {e}")
        return None

if __name__ == '__main__':
    if is_windows():
        setup_windows_midi()
    else:
        print("This script is designed for Windows MIDI setup")
