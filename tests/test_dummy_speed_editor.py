import pytest
import time
from typing import List, Callable, Optional
import sys
import os
import importlib.util

# Adjust path to import from the main application
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Get the path to the blackmagic-speededitor directory
bmd_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'external', 'blackmagic-speededitor')
bmd_path = os.path.join(bmd_dir, 'bmd.py')

# Load the bmd module dynamically
spec = importlib.util.spec_from_file_location("bmd", bmd_path)
bmd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bmd)

# Get the path to speed_editor_midi.py
speed_editor_midi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'speed_editor_midi.py')

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

@pytest.fixture
def mock_midi_handler_fixture():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "key_mappings.json")

    mock_se_instance = MockSpeedEditor(lambda keys: None, lambda mode, value: None, lambda led_state: None)
    mock_midi_handler_instance = MidiHandler(mock_se_instance, config_path)
    return mock_midi_handler_instance, mock_se_instance

class TestDummySpeedEditor:
    def test_key_press_and_release(self, mock_midi_handler_fixture):
        mock_midi_handler, mock_se = mock_midi_handler_fixture

        # Simulate a single key press (e.g., CUT)
        mock_midi_handler.key([SpeedEditorKey.CUT])
        assert (mock_se.led_states[-1] & SpeedEditorLed.CUT.value) == SpeedEditorLed.CUT.value

        # Simulate key release
        mock_midi_handler.key([])
        # For a toggle key, the LED state should persist after release, so no assertion here.

    def test_toggle_key(self, mock_midi_handler_fixture):
        mock_midi_handler, mock_se = mock_midi_handler_fixture

        # Simulate a toggle key press (e.g., CUT for toggle on)
        mock_midi_handler.key([SpeedEditorKey.CUT])
        assert (mock_se.led_states[-1] & SpeedEditorLed.CUT.value) == SpeedEditorLed.CUT.value

        # Simulate key release for the toggle key
        mock_midi_handler.key([])

        # Simulate a toggle key press (e.g., CUT again for toggle off)
        mock_midi_handler.key([SpeedEditorKey.CUT])
        assert (mock_se.led_states[-1] & SpeedEditorLed.CUT.value) == 0

    def test_jog_wheel_movement(self, mock_midi_handler_fixture):
        mock_midi_handler, mock_se = mock_midi_handler_fixture

        # Simulate a jog wheel movement
        mock_midi_handler.jog(SpeedEditorJogMode.RELATIVE_2, 100000)
        # Add assertions based on expected MIDI messages or internal state changes
        # For now, we'll just check if the jog handler was called
        # Assertions for specific MIDI messages would require more complex mocking of mido

    def test_profile_switch(self, mock_midi_handler_fixture):
        mock_midi_handler, mock_se = mock_midi_handler_fixture

        # Simulate profile switch to 'edit' via TIMELINE key
        mock_midi_handler.key([SpeedEditorKey.TIMELINE])
        assert mock_midi_handler.current_profile == 'edit'

        # Simulate key release
        mock_midi_handler.key([])

        # Simulate profile switch to 'library' via SOURCE key
        mock_midi_handler.key([SpeedEditorKey.SOURCE])
        assert mock_midi_handler.current_profile == 'library'

        mock_midi_handler.key([])

    def test_key_press_in_new_profile(self, mock_midi_handler_fixture):
        mock_midi_handler, mock_se = mock_midi_handler_fixture

        # Switch to 'edit' profile
        mock_midi_handler.key([SpeedEditorKey.TIMELINE])
        mock_midi_handler.key([])

        # Simulate a key press in the 'edit' profile (e.g., STOP_PLAY)
        mock_midi_handler.key([SpeedEditorKey.STOP_PLAY])
        # Assertions for specific MIDI messages or internal state changes
        # This would require more sophisticated mocking of MIDI messages
        mock_midi_handler.key([])
