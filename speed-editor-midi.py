#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'blackmagic-speededitor'))
from bmd import (
    SpeedEditor,
    SpeedEditorHandler,
    SpeedEditorJogLed,
    SpeedEditorJogMode,
    SpeedEditorKey,
    SpeedEditorLed,
)

import mido
import hid
import platform

class MidiHandler(SpeedEditorHandler):
	def __init__(self, se, config_path='config/key_mappings.json'):
		self.se = se
		self.keys = []
		self.leds = 0
		self.se.set_leds(self.leds)

		# Load configuration
		self.config = self._load_config(config_path)
		self.current_profile = 'edit'  # Default profile

		# Set up jog modes from config
		self.jog_modes = self._setup_jog_modes()

		self._set_jog_mode_for_key(SpeedEditorKey.SHTL)

		self.midi_max = 127
		self.midi_center = 64

		# Jog wheel state tracking
		self.last_jog_value = None
		self.jog_center = self.midi_center  # MIDI center value
		self.jog_sensitivity = 50000  # Max value for full range
		self.jog_deadband = 20  # Increased deadband for better stability without feedback

		# Double-tap detection for joggable keys
		self.double_tap_timeout = 500  # milliseconds
		self.key_tap_times = {}  # Track last tap time for each key
		self.double_tapped_keys = set()  # Track which keys were double-tapped

		# Parameter state tracking for joggable keys
		self.parameter_states = {}  # Track current parameter values
		self.active_jog_key = None  # Currently active joggable key
		self.jog_accumulator = {}  # Accumulate jog values for smoother control

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
				print('Windows MIDI setup module not found, using default MIDI setup')
			except Exception as e:
				print(f'Windows MIDI setup failed: {e}')
		
		# Fallback to standard MIDI setup
		try:
			midi_out = mido.open_output()
			print(f'MIDI output connected to: {midi_out.name}')
			return midi_out
		except Exception as e:
			print(f'Failed to open MIDI output: {e}')
			print('Available MIDI ports:')
			for port in mido.get_output_names():
				print(f'  - {port}')
			return None

	def _load_config(self, config_path):
		"""Load the JSON configuration file."""
		with open(config_path, 'r') as f:
			return json.load(f)

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
			print(f"Switched to profile: {profile_name}")
		else:
			print(f"Profile {profile_name} not found")

	def get_key_mapping(self, key_name):
		"""Get the mapping for a key in the current profile."""
		profile = self.config['profiles'][self.current_profile]
		return profile['mappings'].get(key_name, {})

	def reset_jog_accumulator(self, key):
		"""Reset the jog accumulator for a specific key."""
		# Check if key has jog mapping in current profile
		key_mapping = self.get_key_mapping(key.name)
		if key_mapping.get('jog'):
			self.jog_accumulator[key] = self.midi_center
			print(f"Reset jog accumulator for {key.name}")


	def _set_jog_mode_for_key(self, key: SpeedEditorKey):
		if key not in self.jog_modes:
			return
		self.se.set_jog_leds(self.jog_modes[key][0])
		self.se.set_jog_mode(self.jog_modes[key][1])

	def _send_midi(self, msg_type, note_or_cc, velocity=64):
		if not self.midi_out:
			return

		try:
			if msg_type == 'note_on':
				msg = mido.Message('note_on', note=note_or_cc, velocity=velocity)
			elif msg_type == 'note_off':
				msg = mido.Message('note_off', note=note_or_cc, velocity=velocity)
			elif msg_type == 'control_change':
				msg = mido.Message('control_change', channel=0, control=note_or_cc, value=velocity)
			else:
				return

			self.midi_out.send(msg)
			print(f"MIDI value: {velocity} for key {note_or_cc}")
		except Exception as e:
			print(f'MIDI send error: {e}')

	def jog(self, mode: SpeedEditorJogMode, value):
		print(f"Jog mode {mode:d} : {value:d} - keys: {self.keys}")

		if not self.midi_out:
			return

		# Find currently active keys with jog mapping
		active_joggable_keys = []
		for key in self.keys:
			key_mapping = self.get_key_mapping(key.name)
			if key_mapping.get('jog'):
				active_joggable_keys.append(key)

		if not active_joggable_keys:
			return

		# Use the first active joggable key (should only be one at a time)
		current_key = active_joggable_keys[0]

		# If we switched to a different joggable key, reset accumulator
		if self.active_jog_key != current_key:
			self.active_jog_key = current_key
			self.jog_accumulator[current_key] = self.midi_center  # Start at center
			print(f"Switched to joggable key: {current_key.name}")

		# Handle different jog modes appropriately
		if mode == SpeedEditorJogMode.ABSOLUTE_DEADZERO:
			# Absolute mode: map -4096 to +4096 range to 0-127
			midi_value = max(0, min(self.midi_max, int(self.midi_center + (value / self.midi_center))))
		elif mode in [SpeedEditorJogMode.RELATIVE_2, SpeedEditorJogMode.RELATIVE_0]:
			# Relative modes: accumulate the delta
			if abs(value) < self.jog_deadband:
				midi_value = self.jog_accumulator.get(current_key, self.midi_center)  # Stay at current position
			else:
				normalized_delta = max(-1.0, min(1.0, (value / self.jog_sensitivity)))
				midi_offset = normalized_delta * 10  # Smaller steps for smoother control
				current_value = self.jog_accumulator.get(current_key, self.midi_center)
				new_value = current_value + midi_offset
				midi_value = max(0, min(self.midi_max, int(new_value)))
				self.jog_accumulator[current_key] = midi_value
		elif mode == SpeedEditorJogMode.ABSOLUTE_CONTINUOUS:
			# Absolute continuous mode
			midi_value = max(0, min(self.midi_max, int(self.midi_center + (value / self.midi_center))))
		else:
			midi_value = self.jog_accumulator.get(current_key, self.midi_center)  # Stay at current position

		try:
			msg = mido.Message('control_change', channel=0, control=current_key.value, value=midi_value)
			self.midi_out.send(msg)
			print(f"Jog MIDI value: {midi_value} for key {current_key.name} (index {current_key.value})")
		except Exception as e:
			print(f'Jog MIDI error: {e}')

	def key(self, keys: List[SpeedEditorKey]):
		kl = ', '.join([k.name for k in keys])
		if not kl:
			kl = 'None'
		print(f"Keys held: {kl:s}")

		# Find keys being released and send note off
		for k in self.keys:
			if k not in keys and k != SpeedEditorKey.NONE:
				# Jog & Single Tap are exclusive behaviors for a given key
				# Check if key has jog mapping
				key_mapping = self.get_key_mapping(k.name)
				if key_mapping.get('jog'):
					# Only send note_off if we sent note_on (double tap)
					if k in self.double_tapped_keys:
						self._send_midi('note_off', k)
						self.double_tapped_keys.discard(k)  # Remove from set
				else:
					self._send_midi('note_off', k)

		# Send note on for newly pressed keys
		for k in keys:
			if k != SpeedEditorKey.NONE:
				# Handle profile switching keys (but still execute their commands)
				if k == SpeedEditorKey.SOURCE:
					self.set_profile('library')
					# Also send the library switch command
					self._send_midi('note_on', k)
					continue
				elif k == SpeedEditorKey.TIMELINE:
					self.set_profile('edit')
					# Also send the develop switch command
					self._send_midi('note_on', k)
					continue

				# Get key mapping from current profile
				key_mapping = self.get_key_mapping(k.name)

				# Check if key has jog mapping
				key_mapping = self.get_key_mapping(k.name)
				if key_mapping.get('jog'):
					# Reset accumulator for this key when pressed
					self.reset_jog_accumulator(k)

					# Handle double-tap detection for joggable keys
					current_time = datetime.now().timestamp() * 1000

					if k in self.key_tap_times:
						time_since_last = current_time - self.key_tap_times[k]
						if time_since_last <= self.double_tap_timeout:
							# Double tap detected - send MIDI note if configured
							if key_mapping.get('double_tap'):
								self._send_midi('note_on', k)
								self.double_tapped_keys.add(k)  # Track that this key was double-tapped
								print(f"Double tap detected for {k.name}")
						else:
							# First tap - just record time
							self.key_tap_times[k] = current_time
					else:
						# First tap - just record time
						self.key_tap_times[k] = current_time

					# Always turn on LED for joggable keys
					self.leds |= getattr(SpeedEditorLed, k.name, 0)
					self.se.set_leds(self.leds)
				else:
					# Send single tap command if configured
					if key_mapping.get('single_tap'):
						self._send_midi('note_on', k)

		# Find keys being released and toggle led if there is one
		for k in self.keys:
			if k not in keys:
				# Check if key has jog mapping
				key_mapping = self.get_key_mapping(k.name)
				if key_mapping.get('jog'):
					# Just turn off LED for joggable keys
					self.leds &= ~getattr(SpeedEditorLed, k.name, 0)
					self.se.set_leds(self.leds)
				else:
					# Select jog mode
					self._set_jog_mode_for_key(k)

					# Toggle leds
					self.leds ^= getattr(SpeedEditorLed, k.name, 0)
					self.se.set_leds(self.leds)

		self.keys = keys

	def battery(self, charging: bool, level: int):
		print(f"Battery {level:d} %{' and charging' if charging else '':s}")


if __name__ == '__main__':
	print(datetime.now())
	print('Speed Editor MIDI Controller')
	print('Available MIDI ports:')
	midi_ports = mido.get_output_names()
	if midi_ports:
		for port in midi_ports:
			print(f'  - {port}')
	else:
		print('  No MIDI output ports found')
	print()

	se = None
	try:
		se = SpeedEditor()
		timeout = se.authenticate()
		print(f"Speed Editor connected. Timeout: {timeout:d}")
		se.set_handler(MidiHandler(se))

		print('Speed Editor connected. Press keys to send MIDI...')
		print('Press Ctrl+C to exit')

		while True:
			se.poll(timeout=100)  # Add timeout to allow Ctrl+C interruption (100ms)
	except hid.HIDException as e:
		print(f'Speed Editor not found: {e}')
		print('Please connect your BlackMagic Speed Editor and try again.')
		print('Make sure it\'s connected via USB and not being used by another application.')
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
