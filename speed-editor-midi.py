#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from typing import List

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

class MidiHandler(SpeedEditorHandler):
	JOG = {
		SpeedEditorKey.SHTL: (SpeedEditorJogLed.SHTL, SpeedEditorJogMode.ABSOLUTE_DEADZERO),
		SpeedEditorKey.JOG: (SpeedEditorJogLed.JOG, SpeedEditorJogMode.RELATIVE_2),
		SpeedEditorKey.SCRL: (SpeedEditorJogLed.SCRL, SpeedEditorJogMode.RELATIVE_2),
	}

	JOGGABLE_KEYS = [
		SpeedEditorKey.CAM1,
		SpeedEditorKey.CAM2,
		SpeedEditorKey.CAM3,
		SpeedEditorKey.CAM4,
		SpeedEditorKey.CAM5,
		SpeedEditorKey.CAM6,
		SpeedEditorKey.CAM7,
		SpeedEditorKey.CAM8,
		SpeedEditorKey.CAM9
	]

	def __init__(self, se):
		self.se = se
		self.keys = []
		self.leds = 0
		self.se.set_leds(self.leds)
		self._set_jog_mode_for_key(SpeedEditorKey.SCRL)

		self.midi_max = 127
		self.midi_center = 64

		# Jog wheel state tracking
		self.last_jog_value = None
		self.jog_center = self.midi_center  # MIDI center value
		self.jog_sensitivity = 50000  # Max value for full range
		self.jog_deadband = 10  # Deadband around center

		# Double-tap detection for joggable keys
		self.double_tap_timeout = 500  # milliseconds
		self.key_tap_times = {}  # Track last tap time for each key
		self.double_tapped_keys = set()  # Track which keys were double-tapped

		# MIDI output setup
		try:
			self.midi_out = mido.open_output()
			print(f'MIDI output connected to: {self.midi_out.name}')
		except Exception as e:
			print(f'Failed to open MIDI output: {e}')
			print('Available MIDI ports:')
			for port in mido.get_output_names():
				print(f'  - {port}')
			self.midi_out = None


	def _set_jog_mode_for_key(self, key: SpeedEditorKey):
		if key not in self.JOG:
			return
		self.se.set_jog_leds(self.JOG[key][0])
		self.se.set_jog_mode(self.JOG[key][1])

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

		key_indices = []
		for i, key in enumerate(self.JOGGABLE_KEYS):
			if key in self.keys:
				key_indices.append(i)


		# Handle different jog modes appropriately
		if mode == SpeedEditorJogMode.ABSOLUTE_DEADZERO:
			# Absolute mode: map -4096 to +4096 range to 0-127
			midi_value = max(0, min(self.midi_max, int(self.midi_center + (value / self.midi_center))))
		elif mode in [SpeedEditorJogMode.RELATIVE_2, SpeedEditorJogMode.RELATIVE_0]:
			# Relative modes: value is the delta directly
			# Check deadband first
			if abs(value) < self.jog_deadband:
				midi_value = self.midi_center  # Stay at center
			else:
				normalized_delta = max( -1.0, min( 1.0, (value / self.jog_sensitivity) ) )
				midi_offset = normalized_delta * self.midi_center
				midi_value = int(self.midi_center + midi_offset)
				midi_value = max(0, min(self.midi_max, midi_value))
		elif mode == SpeedEditorJogMode.ABSOLUTE_CONTINUOUS:
			# Absolute continuous mode
			midi_value = max(0, min(self.midi_max, int(self.midi_center + (value / self.midi_center))))
		else:
			midi_value = 64  # Center position

		try:
			for i in key_indices:
				msg = mido.Message('control_change', channel=0, control=i, value=midi_value)
				self.midi_out.send(msg)
				print(f"Jog MIDI value: {midi_value} for key {i}")
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
				if k in self.JOGGABLE_KEYS:
					# Only send note_off if we sent note_on (double tap)
					if k in self.double_tapped_keys:
						self._send_midi('note_off', k)
						self.double_tapped_keys.discard(k)  # Remove from set
				else:
					self._send_midi('note_off', k)

		# Send note on for newly pressed keys
		for k in keys:
			if k != SpeedEditorKey.NONE:
				if k in self.JOGGABLE_KEYS:
					# Handle double-tap detection for joggable keys
					current_time = datetime.now().timestamp() * 1000

					if k in self.key_tap_times:
						time_since_last = current_time - self.key_tap_times[k]
						if time_since_last <= self.double_tap_timeout:
							# Double tap detected - send MIDI note
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
					self._send_midi('note_on', k)

		# Find keys being released and toggle led if there is one
		for k in self.keys:
			if k not in keys:
				if k in self.JOGGABLE_KEYS:
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
