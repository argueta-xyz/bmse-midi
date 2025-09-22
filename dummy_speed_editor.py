import time
from typing import List, Callable, Optional

# Adjust path to import from the main application
import sys
import os
import importlib.util

# Add the current directory to sys.path to find speed_editor_midi.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Get the path to the blackmagic-speededitor directory
bmd_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blackmagic-speededitor')
bmd_path = os.path.join(bmd_dir, 'bmd.py')

# Load the bmd module dynamically
spec = importlib.util.spec_from_file_location("bmd", bmd_path)
bmd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bmd)

# Get the path to speed_editor_midi.py
speed_editor_midi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speed_editor_midi.py')

# Load the speed_editor_midi module dynamically
spec_midi = importlib.util.spec_from_file_location("speed_editor_midi", speed_editor_midi_path)
speed_editor_midi_module = importlib.util.module_from_spec(spec_midi)
spec_midi.loader.exec_module(speed_editor_midi_module)

MidiHandler = speed_editor_midi_module.MidiHandler

SpeedEditorKey = bmd.SpeedEditorKey
SpeedEditorJogMode = bmd.SpeedEditorJogMode
SpeedEditorLed = bmd.SpeedEditorLed

class MockSpeedEditor:
    """A mock SpeedEditor class for testing MidiHandler without physical hardware."""
    def __init__(self, key_handler: Callable[[List[SpeedEditorKey]], None],
                 jog_handler: Callable[[SpeedEditorJogMode, int], None],
                 led_handler: Callable[[int], None]):
        self.key_handler = key_handler
        self.jog_handler = jog_handler
        self.led_handler = led_handler
        self._stop_requested = False
        self.led_states = []
        self.jog_led_states = []
        self.jog_modes = []
        print("MockSpeedEditor initialized.")

    def read_loop(self):
        """Simulate the event loop where we can inject events."""
        print("MockSpeedEditor starting read loop. Ready for injected events.")
        while not self._stop_requested:
            time.sleep(0.1) # Simulate polling interval
        print("MockSpeedEditor stopping read loop.")

    def set_leds(self, led_state: int):
        """Mock LED setting - just log the state."""
        self.led_states.append(led_state)
        print(f"MockSpeedEditor received LED state: {bin(led_state)}")
        self.led_handler(led_state)

    def set_jog_leds(self, led_state: int):
        self.jog_led_states.append(led_state)
        print(f"MockSpeedEditor received JOG LED state: {bin(led_state)}")

    def set_jog_mode(self, mode: SpeedEditorJogMode):
        self.jog_modes.append(mode)
        print(f"MockSpeedEditor received JOG mode: {mode}")

    def stop(self):
        """Request to stop the read loop."""
        self._stop_requested = True
