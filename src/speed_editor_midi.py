#!/usr/bin/env python3

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Add the project root to sys.path for local module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'external', 'blackmagic-speededitor'))
from bmd import (
    SpeedEditor,
    SpeedEditorHandler,
    SpeedEditorJogLed,
    SpeedEditorJogMode,
    SpeedEditorKey,
    SpeedEditorLed,
)
from src.key_types import (
    BaseKey,
    SingleKey,
    ToggleKey,
    JogKey,
    ProfileKey,
    KeyBehavior,
    KeyRegistry,
    create_key_from_config
)

import mido
import hid
import platform

def setup_logging(log_level='ERROR'):
    """Configure logging with the specified level."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Speed Editor MIDI Controller')
    parser.add_argument('--log-level', '-l',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       default='ERROR',
                       help='Set the logging level (default: ERROR)')
    parser.add_argument('--config-path',
                       default='config/key_mappings.json',
                       help='Path to the key mappings configuration file (default: config/key_mappings.json)')
    return parser.parse_args()

class MidiHandler(SpeedEditorHandler):
	def __init__(self, se, config_path):
		self.se = se
		self.keys = []
		self.leds = 0
		self.se.set_leds(self.leds)

		# Load configuration
		with open(config_path, 'r') as f:
			self.config = json.load(f)
		self.current_profile = 'edit'  # Default profile
		self.profile_registries = {}  # Store KeyRegistry for each profile
		self._initialize_key_registries()

		# Set up jog modes from config
		self.jog_modes = self._setup_jog_modes()

		self._set_jog_mode_for_key(SpeedEditorKey.SHTL)

		# Legacy jog state tracking - no longer needed with stateful keys
		# All jog state is now managed by individual JogKey objects

		# MIDI output setup
		self.midi_out = self._setup_midi_output()

	def _setup_midi_output(self):
		"""Set up MIDI output with Windows virtual port support."""
		if platform.system() == 'Windows':
			try:
				# Import Windows-specific MIDI setup
				from windows.midi_setup import get_midi_output_port
				midi_out = get_midi_output_port()
				if midi_out:
					print(f'MIDI output connected to: {midi_out.name}')
					return midi_out
			except ImportError:
				logger.warning('Windows MIDI setup module not found, using default MIDI setup')
			except Exception as e:
				logger.error(f'Windows MIDI setup failed: {e}')

		# Fallback to standard MIDI setup
		try:
			midi_out = mido.open_output()
			print(f'MIDI output connected to: {midi_out.name}')
			return midi_out
		except Exception as e:
			logger.error(f'Failed to open MIDI output: {e}')
			logger.error('Available MIDI ports:')
			for port in mido.get_output_names():
				logger.error(f'  - {port}')
			return None

	def _initialize_key_registries(self):
		"""Initialize KeyRegistry objects for each profile."""
		for profile_name, profile_data in self.config['profiles'].items():
			registry = KeyRegistry()

			for key_name, key_config in profile_data['mappings'].items():
				try:
					# Get the MIDI note value from the SpeedEditorKey enum
					key_enum = getattr(SpeedEditorKey, key_name)
					midi_note = key_enum.value

					# Get LED bit for this key
					try:
						led_enum = getattr(SpeedEditorLed, key_name)
						led_bit = led_enum.value
					except AttributeError:
						led_bit = 0  # No LED for this key

					# Create the appropriate key object
					key_obj = create_key_from_config(key_name, midi_note, led_bit, key_config)
					registry.add_key(key_obj)

				except AttributeError:
					logger.warning(f"Unknown key name: {key_name}")
					continue

			self.profile_registries[profile_name] = registry
			logger.debug(f"Initialized {len(registry)} keys for profile '{profile_name}'")

	def _setup_jog_modes(self):
		"""Set up jog modes from configuration."""
		jog_modes = {}
		for key_name, mode_config in self.config['jog_modes'].items():
			key_enum = getattr(SpeedEditorKey, key_name)
			led_enum = getattr(SpeedEditorJogLed, mode_config['led'])
			mode_enum = getattr(SpeedEditorJogMode, mode_config['mode'])
			jog_modes[key_enum] = (led_enum, mode_enum)
		return jog_modes


	def set_profile(self, profile_name):
		"""Switch to a different profile."""
		if profile_name in self.config['profiles']:
			self.current_profile = profile_name

			# Update LEDs to match the new profile's key states
			registry = self.profile_registries.get(profile_name)
			if registry:
				self._sync_leds_with_registry(registry)

			logger.info(f"Switched to profile: {profile_name}")
		else:
			logger.error(f"Profile {profile_name} not found")

	def _sync_leds_with_registry(self, registry):
		"""Sync LEDs with the current state of keys in the registry."""
		# Get current LED state from all keys in the registry
		led_state = registry.get_current_led_state()
		self.leds = led_state
		self.se.set_leds(self.leds)
		logger.debug(f"Synced LEDs with registry for profile {self.current_profile}")

	def send_startup_profile_message(self):
		"""Send MIDI message for the startup profile to sync external software."""
		registry = self.profile_registries.get(self.current_profile)
		if not registry:
			logger.error(f"No registry found for profile: {self.current_profile}")
			return

		if self.current_profile == 'edit':
			# Send TIMELINE key press to switch to edit profile
			midi_msgs, led_updates = registry.handle_key_press('TIMELINE')
			self._process_midi_messages(midi_msgs)
			self._process_led_updates(led_updates)
			# Send release too
			midi_msgs, led_updates = registry.handle_key_release('TIMELINE')
			self._process_midi_messages(midi_msgs)
			self._process_led_updates(led_updates)
			logger.info(f"Sent startup profile message for: {self.current_profile}")
		elif self.current_profile == 'library':
			# Send SOURCE key press to switch to library profile
			midi_msgs, led_updates = registry.handle_key_press('SOURCE')
			self._process_midi_messages(midi_msgs)
			self._process_led_updates(led_updates)
			# Send release too
			midi_msgs, led_updates = registry.handle_key_release('SOURCE')
			self._process_midi_messages(midi_msgs)
			self._process_led_updates(led_updates)
			logger.info(f"Sent startup profile message for: {self.current_profile}")
		else:
			logger.warning(f"No startup message defined for profile: {self.current_profile}")

	def get_key(self, key_name: str) -> BaseKey:
		"""Get the key object for a key in the current profile."""
		registry = self.profile_registries.get(self.current_profile)
		if registry:
			return registry.get_key(key_name)
		return None

	def get_key_mapping(self, key_name):
		"""Get the mapping for a key in the current profile (legacy method)."""
		profile = self.config['profiles'][self.current_profile]
		return profile['mappings'].get(key_name, {})

	def _set_jog_mode_for_key(self, key: SpeedEditorKey):
		"""Set jog mode for a key (still needed for hardware setup)."""
		if key not in self.jog_modes:
			return
		self.se.set_jog_leds(self.jog_modes[key][0])
		self.se.set_jog_mode(self.jog_modes[key][1])

	# Legacy MIDI methods removed - now using _process_midi_messages()

	def jog(self, mode: SpeedEditorJogMode, value):
		logger.debug(f"Jog mode {mode:d} : {value:d} - keys: {self.keys}")

		# Get current profile registry
		registry = self.profile_registries.get(self.current_profile)
		if not registry:
			return

		# Find currently active keys with jog capability
		active_joggable_keys = []
		for key in self.keys:
			key_obj = registry.get_key(key.name)
			if key_obj and key_obj.behavior == KeyBehavior.JOG:
				active_joggable_keys.append(key)

		if not active_joggable_keys:
			return

		# Use the first active joggable key (should only be one at a time)
		current_key = active_joggable_keys[0]

		# Handle jog input through the key object
		midi_msgs = registry.handle_jog(current_key.name, value, mode)
		self._process_midi_messages(midi_msgs)

	def key(self, keys: List[SpeedEditorKey]):
		kl = ', '.join([k.name for k in keys])
		if not kl:
			kl = 'None'
		logger.debug(f"Keys held: {kl:s}")

		# Get current profile registry
		registry = self.profile_registries.get(self.current_profile)
		if not registry:
			logger.error(f"No registry found for profile: {self.current_profile}")
			return

		# Find keys being released
		for k in self.keys:
			if k not in keys and k != SpeedEditorKey.NONE:
				midi_msgs, led_updates = registry.handle_key_release(k.name)
				self._process_midi_messages(midi_msgs)
				self._process_led_updates(led_updates)

		# Handle newly pressed keys
		for k in keys:
			if k != SpeedEditorKey.NONE and k not in self.keys:
				logger.debug(f"Processing newly pressed key: {k.name}")

				# Handle profile switching keys specially
				if k == SpeedEditorKey.SOURCE:
					midi_msgs, led_updates = registry.handle_key_press(k.name)
					self._process_midi_messages(midi_msgs)
					self._process_led_updates(led_updates)
					self.set_profile('library')
					continue
				elif k == SpeedEditorKey.TIMELINE:
					midi_msgs, led_updates = registry.handle_key_press(k.name)
					self._process_midi_messages(midi_msgs)
					self._process_led_updates(led_updates)
					self.set_profile('edit')
					continue

				# Handle all other keys through the registry
				midi_msgs, led_updates = registry.handle_key_press(k.name)
				self._process_midi_messages(midi_msgs)
				self._process_led_updates(led_updates)

		# Update the current keys list
		self.keys = keys

	def _process_midi_messages(self, midi_msgs: List):
		"""Process a list of MidiMessage objects."""
		if not self.midi_out:
			return

		for midi_msg in midi_msgs:
			try:
				if midi_msg.msg_type == 'note_on':
					msg = mido.Message('note_on', note=midi_msg.note, velocity=midi_msg.velocity, channel=midi_msg.channel-1)
				elif midi_msg.msg_type == 'note_off':
					msg = mido.Message('note_off', note=midi_msg.note, velocity=midi_msg.velocity, channel=midi_msg.channel-1)
				elif midi_msg.msg_type == 'control_change':
					msg = mido.Message('control_change', channel=midi_msg.channel-1, control=midi_msg.note, value=midi_msg.velocity)
				else:
					logger.error(f"Unknown MIDI message type: {midi_msg.msg_type}")
					continue

				self.midi_out.send(msg)
				logger.debug(f"MIDI {midi_msg.msg_type}: {midi_msg.velocity} (note: {midi_msg.note}, channel: {midi_msg.channel})")
			except Exception as e:
				logger.error(f'MIDI send error: {e}')

	def _process_led_updates(self, led_updates: List):
		"""Process a list of LedUpdate objects."""
		for led_update in led_updates:
			if led_update.state:
				# LED ON: set bit (normal logic - we had this backwards!)
				self.leds |= led_update.led_bit
			else:
				# LED OFF: clear bit (normal logic - we had this backwards!)
				self.leds &= ~led_update.led_bit

		# Apply LED changes if any updates were made
		if led_updates:
			self.se.set_leds(self.leds)
			logger.debug(f"Updated LEDs: {[f'bit {l.led_bit} {"ON" if l.state else "OFF"}' for l in led_updates]}")

	def battery(self, charging: bool, level: int):
		print(f"Battery {level:d} %{' and charging' if charging else '':s}")


if __name__ == '__main__':
	# Parse command line arguments
	args = parse_arguments()

	# Set up logging with the specified level
	logger = setup_logging(args.log_level)

	print(f'Started at {datetime.now()}')
	print('Speed Editor MIDI Controller')
	print('Available MIDI ports:')
	midi_ports = mido.get_output_names()
	if midi_ports:
		for port in midi_ports:
			print(f'  - {port}')
	else:
		logger.warning('  No MIDI output ports found')
	logger.info('')

	se = None
	try:
		print('Initializing Speed Editor...')
		se = SpeedEditor()
		timeout = se.authenticate()
		logger.info(f"Speed Editor connected. Timeout: {timeout:d}")
		handler = MidiHandler(se, args.config_path)
		se.set_handler(handler)

		# Send startup profile switch message
		handler.send_startup_profile_message()

		print('Speed Editor connected. Press keys to send MIDI...')
		print('Press Ctrl+C to exit')

		while True:
			se.poll(timeout=100)  # Add timeout to allow Ctrl+C interruption (100ms)
	except Exception as e:
		logger.error(f'Speed Editor not found: {e}')
		logger.error('Please connect your BlackMagic Speed Editor and try again.')
		logger.error('Make sure it\'s connected via USB and not being used by another application.')
	except KeyboardInterrupt:
		print('\nExiting...')
	finally:
		# Clean shutdown
		if se and hasattr(se, 'handler') and hasattr(se.handler, 'midi_out') and se.handler.midi_out:
			se.handler.midi_out.close()
		if se and hasattr(se, 'dev'):
			se.dev.close()
		# Force exit to prevent timer thread issues
		import os
		os._exit(0)
