"""
Object-oriented key type system for Speed Editor MIDI Controller.

This module defines different types of keys that are fully self-managing,
including their own state, LED control, and MIDI message generation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple, Callable
from enum import Enum
import time


class KeyBehavior(Enum):
    """Defines the different key behaviors."""
    SINGLE = "single"           # Single press/release
    TOGGLE = "toggle"           # Toggle on/off with state
    JOG = "jog"                # Jog wheel with double-tap
    PROFILE = "profile"         # Profile switching


class MidiMessage:
    """Represents a MIDI message to be sent."""
    def __init__(self, msg_type: str, note: int, velocity: int, channel: int):
        self.msg_type = msg_type  # 'note_on', 'note_off', 'control_change'
        self.note = note
        self.velocity = velocity
        self.channel = channel

    def __repr__(self):
        return f"MidiMessage({self.msg_type}, note={self.note}, vel={self.velocity}, ch={self.channel})"


class LedUpdate:
    """Represents an LED state update."""
    def __init__(self, led_bit: int, state: bool):
        self.led_bit = led_bit
        self.state = state  # True = ON, False = OFF

    def __repr__(self):
        return f"LedUpdate(bit={self.led_bit}, {'ON' if self.state else 'OFF'})"


class BaseKey(ABC):
    """Base class for all key types with self-managed state."""

    def __init__(self, name: str, midi_note: int, led_bit: int = 0):
        self.name = name
        self.midi_note = midi_note
        self.led_bit = led_bit
        self.is_pressed = False
        self.last_press_time = 0

    @property
    @abstractmethod
    def behavior(self) -> KeyBehavior:
        """Return the key behavior type."""
        pass

    @abstractmethod
    def on_press(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Handle key press. Returns (midi_messages, led_updates)."""
        pass

    @abstractmethod
    def on_release(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Handle key release. Returns (midi_messages, led_updates)."""
        pass

    def on_jog(self, value: int) -> List[MidiMessage]:
        """Handle jog wheel input. Override in jog keys."""
        return []

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate that the configuration is valid for this key type."""
        pass

    def reset_state(self):
        """Reset key to initial state."""
        self.is_pressed = False
        self.last_press_time = 0

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', note={self.midi_note})"


class SingleKey(BaseKey):
    """A key that sends a single MIDI message on press and release."""

    def __init__(self, name: str, midi_note: int, led_bit: int, command: str):
        super().__init__(name, midi_note, led_bit)
        self.command = command

    @property
    def behavior(self) -> KeyBehavior:
        return KeyBehavior.SINGLE

    def on_press(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Send note_on on press."""
        self.is_pressed = True
        self.last_press_time = time.time() * 1000

        midi_msgs = [MidiMessage('note_on', self.midi_note, 64, 1)]
        led_updates = []  # Single keys don't manage LEDs

        return midi_msgs, led_updates

    def on_release(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Send note_off on release."""
        self.is_pressed = False

        midi_msgs = [MidiMessage('note_off', self.midi_note, 64, 1)]
        led_updates = []

        return midi_msgs, led_updates

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Single keys should only have single_tap defined."""
        valid_keys = {'single_tap'}
        config_keys = {k for k, v in config.items() if v is not None}
        return config_keys.issubset(valid_keys) and 'single_tap' in config_keys


class ToggleKey(BaseKey):
    """A key that toggles between on/off states with LED feedback."""

    def __init__(self, name: str, midi_note: int, led_bit: int, toggle_on_command: str, toggle_off_command: str):
        super().__init__(name, midi_note, led_bit)
        self.toggle_on_command = toggle_on_command
        self.toggle_off_command = toggle_off_command
        self.is_toggled_on = False  # Internal toggle state

    @property
    def behavior(self) -> KeyBehavior:
        return KeyBehavior.TOGGLE

    def on_press(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Toggle state and send appropriate MIDI message."""
        self.is_pressed = True
        self.last_press_time = time.time() * 1000

        # Toggle the state
        self.is_toggled_on = not self.is_toggled_on

        if self.is_toggled_on:
            # Toggling ON: Channel 1, LED ON (inverted: clear bit)
            midi_msgs = [MidiMessage('note_on', self.midi_note, 64, 1)]
            led_updates = [LedUpdate(self.led_bit, True)]
        else:
            # Toggling OFF: Channel 2, LED OFF (inverted: set bit)
            midi_msgs = [MidiMessage('note_on', self.midi_note, 64, 2)]
            led_updates = [LedUpdate(self.led_bit, False)]

        return midi_msgs, led_updates

    def on_release(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Send note_off on the same channel as the note_on."""
        self.is_pressed = False

        # Send note_off on the same channel as the press
        channel = 1 if self.is_toggled_on else 2
        midi_msgs = [MidiMessage('note_off', self.midi_note, 64, channel)]
        led_updates = []  # LED was already updated on press

        return midi_msgs, led_updates

    def reset_state(self):
        """Reset toggle to OFF state."""
        super().reset_state()
        self.is_toggled_on = False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Toggle keys should have toggle_on and toggle_off defined."""
        valid_keys = {'toggle_on', 'toggle_off'}
        config_keys = {k for k, v in config.items() if v is not None}
        return config_keys.issubset(valid_keys) and 'toggle_on' in config_keys


class JogKey(BaseKey):
    """A key that supports jog wheel functionality with optional double-tap."""

    def __init__(self, name: str, midi_note: int, led_bit: int, jog_command: str, double_tap_command: Optional[str] = None):
        super().__init__(name, midi_note, led_bit)
        self.jog_command = jog_command
        self.double_tap_command = double_tap_command
        self.double_tap_timeout = 500  # milliseconds
        self.jog_accumulator = 64  # Start at MIDI center

    @property
    def behavior(self) -> KeyBehavior:
        return KeyBehavior.JOG

    def on_press(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Handle press - check for double tap if configured."""
        current_time = time.time() * 1000
        self.is_pressed = True

        midi_msgs = []
        led_updates = []

        if self.double_tap_command and self.last_press_time > 0:
            time_since_last = current_time - self.last_press_time
            if time_since_last <= self.double_tap_timeout:
                # Double tap detected - send on channel 2
                midi_msgs.append(MidiMessage('note_on', self.midi_note, 64, 2))
                # Turn on LED for jog mode
                led_updates.append(LedUpdate(self.led_bit, True))

        self.last_press_time = current_time
        return midi_msgs, led_updates

    def on_release(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Send note_off if we sent note_on."""
        self.is_pressed = False

        midi_msgs = []
        led_updates = []

        # If we're in jog mode (LED is on), send note_off and turn off LED
        # This is a simplification - in reality we'd track if we sent note_on
        if self.double_tap_command:
            midi_msgs.append(MidiMessage('note_off', self.midi_note, 64, 2))
            led_updates.append(LedUpdate(self.led_bit, False))

        return midi_msgs, led_updates

    def on_jog(self, value: int, mode: 'SpeedEditorJogMode' = None) -> List[MidiMessage]:
        """Handle jog wheel input - send control change on channel 3."""
        # Import here to avoid circular imports
        from bmd import SpeedEditorJogMode

        # Default mode if not provided
        if mode is None:
            mode = SpeedEditorJogMode.RELATIVE_2

        # Jog parameters (matching the original implementation)
        midi_max = 127
        midi_center = 64
        jog_sensitivity = 50000
        jog_deadband = 20

        # Handle different jog modes appropriately
        if mode == SpeedEditorJogMode.ABSOLUTE_DEADZERO:
            # Absolute mode: map -4096 to +4096 range to 0-127
            midi_value = max(0, min(midi_max, int(midi_center + (value / midi_center))))
        elif mode in [SpeedEditorJogMode.RELATIVE_2, SpeedEditorJogMode.RELATIVE_0]:
            # Relative modes: accumulate the delta
            if abs(value) < jog_deadband:
                midi_value = self.jog_accumulator  # Stay at current position
            else:
                normalized_delta = max(-1.0, min(1.0, (value / jog_sensitivity)))
                midi_offset = normalized_delta * 10  # Smaller steps for smoother control
                new_value = self.jog_accumulator + midi_offset
                midi_value = max(0, min(midi_max, int(new_value)))
                self.jog_accumulator = midi_value
        elif hasattr(SpeedEditorJogMode, 'ABSOLUTE_CONTINUOUS') and mode == SpeedEditorJogMode.ABSOLUTE_CONTINUOUS:
            # Absolute continuous mode
            midi_value = max(0, min(midi_max, int(midi_center + (value / midi_center))))
        else:
            midi_value = self.jog_accumulator  # Stay at current position

        return [MidiMessage('control_change', self.midi_note, int(midi_value), 3)]

    def reset_state(self):
        """Reset jog state."""
        super().reset_state()
        self.jog_accumulator = 64

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Jog keys should have jog defined, optionally double_tap."""
        valid_keys = {'jog', 'double_tap'}
        config_keys = {k for k, v in config.items() if v is not None}
        return config_keys.issubset(valid_keys) and 'jog' in config_keys


class ProfileKey(BaseKey):
    """A key that switches between profiles."""

    def __init__(self, name: str, midi_note: int, led_bit: int, command: str, target_profile: str):
        super().__init__(name, midi_note, led_bit)
        self.command = command
        self.target_profile = target_profile

    @property
    def behavior(self) -> KeyBehavior:
        return KeyBehavior.PROFILE

    def on_press(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Send profile switch command."""
        self.is_pressed = True
        self.last_press_time = time.time() * 1000

        midi_msgs = [MidiMessage('note_on', self.midi_note, 64, 1)]
        led_updates = []  # Profile keys don't manage their own LEDs

        return midi_msgs, led_updates

    def on_release(self) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Send note_off."""
        self.is_pressed = False

        midi_msgs = [MidiMessage('note_off', self.midi_note, 64, 1)]
        led_updates = []

        return midi_msgs, led_updates

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Profile keys should only have single_tap defined."""
        valid_keys = {'single_tap'}
        config_keys = {k for k, v in config.items() if v is not None}
        return config_keys.issubset(valid_keys) and 'single_tap' in config_keys


def create_key_from_config(name: str, midi_note: int, led_bit: int, config: Dict[str, Any]) -> BaseKey:
    """Factory function to create the appropriate key type from configuration."""

    # Count non-null configuration entries
    active_configs = {k: v for k, v in config.items() if v is not None}

    # Determine key type based on configuration
    if 'toggle_on' in active_configs:
        # Toggle key
        toggle_off = active_configs.get('toggle_off', active_configs['toggle_on'])
        return ToggleKey(name, midi_note, led_bit, active_configs['toggle_on'], toggle_off)

    elif 'jog' in active_configs:
        # Jog key
        double_tap = active_configs.get('double_tap')
        return JogKey(name, midi_note, led_bit, active_configs['jog'], double_tap)

    elif name in ['SOURCE', 'TIMELINE']:
        # Profile switching keys
        target_profile = 'library' if name == 'SOURCE' else 'edit'
        return ProfileKey(name, midi_note, led_bit, active_configs['single_tap'], target_profile)

    elif 'single_tap' in active_configs:
        # Single key
        return SingleKey(name, midi_note, led_bit, active_configs['single_tap'])

    else:
        # Default to single key with no command
        return SingleKey(name, midi_note, led_bit, "")


class KeyRegistry:
    """Registry to manage all keys in a profile with state management."""

    def __init__(self):
        self.keys: Dict[str, BaseKey] = {}

    def add_key(self, key: BaseKey):
        """Add a key to the registry."""
        self.keys[key.name] = key

    def get_key(self, name: str) -> Optional[BaseKey]:
        """Get a key by name."""
        return self.keys.get(name)

    def get_keys_by_behavior(self, behavior: KeyBehavior) -> List[BaseKey]:
        """Get all keys with a specific behavior."""
        return [key for key in self.keys.values() if key.behavior == behavior]

    def handle_key_press(self, key_name: str) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Handle a key press event."""
        key = self.get_key(key_name)
        if key:
            return key.on_press()
        return [], []

    def handle_key_release(self, key_name: str) -> Tuple[List[MidiMessage], List[LedUpdate]]:
        """Handle a key release event."""
        key = self.get_key(key_name)
        if key:
            return key.on_release()
        return [], []

    def handle_jog(self, key_name: str, value: int, mode=None) -> List[MidiMessage]:
        """Handle jog wheel input."""
        key = self.get_key(key_name)
        if key:
            return key.on_jog(value, mode)
        return []

    def reset_all_states(self):
        """Reset all keys to their initial state."""
        for key in self.keys.values():
            key.reset_state()

    def get_current_led_state(self) -> int:
        """Get the current LED state as a bitmask."""
        led_state = 0
        for key in self.keys.values():
            if key.behavior == KeyBehavior.TOGGLE and hasattr(key, 'is_toggled_on'):
                if key.is_toggled_on:
                    # LED ON means clear the bit (inverted logic)
                    led_state &= ~key.led_bit
                else:
                    # LED OFF means set the bit (inverted logic)
                    led_state |= key.led_bit
        return led_state

    def validate_all(self) -> bool:
        """Validate all keys in the registry."""
        return all(key.validate_config({}) for key in self.keys.values())

    def __iter__(self):
        """Allow iteration over keys."""
        return iter(self.keys.values())

    def __len__(self):
        """Return number of keys."""
        return len(self.keys)
