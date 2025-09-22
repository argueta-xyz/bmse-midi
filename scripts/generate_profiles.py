#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os
import json

# Add the parent directory to the path to import bmd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib.util
spec = importlib.util.spec_from_file_location("bmd", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blackmagic-speededitor", "bmd.py"))
bmd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bmd)
SpeedEditorKey = bmd.SpeedEditorKey

def load_json_config(config_path):
    """Load the JSON configuration file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def _add_setting_element(root, channel, command_string, note=None, controller=None):
    setting = ET.SubElement(root, 'setting')
    setting.set('channel', str(channel))
    if note is not None:
        setting.set('note', str(note))
    if controller is not None:
        setting.set('controller', str(controller))
    setting.set('command_string', command_string)

def create_xml_profile(profile_name, profile_data):
    """Create XML profile from JSON data.

    MIDI Channel System:
    - Toggle on: Channel 1 (complete note_on/note_off pair when toggling ON)
    - Toggle off: Channel 2 (complete note_on/note_off pair when toggling OFF)
    - Single tap: Channel 1 (note_on when pressed, note_off when released)
    - Double tap: Channel 2 (note_on when double-tapped, note_off when released)
    - Jog wheel: Channel 3 (continuous control changes)

    Note: Toggleable keys create TWO entries in the XML - one for each channel
    """
    root = ET.Element('settings')

    # Add mappings for each key
    for key_name, key_config in profile_data['mappings'].items():
        # Convert string key name to SpeedEditorKey enum
        try:
            key_enum = getattr(SpeedEditorKey, key_name)
        except AttributeError:
            print(f"Warning: Unknown key {key_name}")
            continue

        key_type = key_config.get('type')
        actions = key_config.get('actions', {})

        if not key_type:
            print(f"Warning: Key {key_name} is missing a 'type' in its configuration. Skipping.")
            continue

        if key_type == 'SINGLE':
            command = actions.get('press')
            if command:
                _add_setting_element(root, '1', command, note=key_enum.value)
        elif key_type == 'TOGGLE':
            toggle_on = actions.get('on')
            toggle_off = actions.get('off')
            if toggle_on and toggle_off:
                # Toggle ON events go on channel 1
                _add_setting_element(root, '1', toggle_on, note=key_enum.value)

                # Toggle OFF events go on channel 2
                _add_setting_element(root, '2', toggle_off, note=key_enum.value)
            else:
                print(f"Warning: Toggle key {key_name} requires both 'on' and 'off' actions. Skipping.")
        elif key_type == 'JOG':
            jog_command = actions.get('jog')
            double_tap = actions.get('double_tap')
            if jog_command:
                _add_setting_element(root, '3', jog_command, controller=key_enum.value)
            if double_tap:
                _add_setting_element(root, '2', double_tap, note=key_enum.value)
            if not jog_command and not double_tap:
                print(f"Warning: Jog key {key_name} requires either a 'jog' or 'double_tap' action. Skipping.")
        elif key_type == 'PROFILE':
            command = actions.get('press')
            if command:
                _add_setting_element(root, '1', command, note=key_enum.value)
        else:
            print(f"Warning: Unknown key type {key_type} for key {key_name}. Skipping.")

    return root


def format_xml(element):
    """Format XML with proper indentation."""
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = ET.fromstring(rough_string)

    # Add XML declaration
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n\n'

    # Convert to string and format
    rough_string = ET.tostring(reparsed, 'utf-8')
    rough_string = rough_string.decode('utf-8')

    # Simple formatting - add newlines between settings
    lines = rough_string.split('>')
    formatted_lines = []
    for i, line in enumerate(lines):
        if line.strip():
            if i < len(lines) - 1:
                formatted_lines.append(line + '>')
            else:
                formatted_lines.append(line)

    return xml_str + '\n'.join(formatted_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_profiles.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]

    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found")
        sys.exit(1)

    # Load configuration
    config = load_json_config(config_path)

    # Create profiles directory if it doesn't exist
    profiles_dir = Path('profiles')
    profiles_dir.mkdir(exist_ok=True)

    # Generate XML files for each profile
    for profile_key, profile_data in config['profiles'].items():
        xml_root = create_xml_profile(profile_key, profile_data)
        xml_content = format_xml(xml_root)

        # Write to file
        output_file = profiles_dir / f"{profile_data['name']}.xml"
        with open(output_file, 'w') as f:
            f.write(xml_content)

        print(f"Generated {output_file}")

if __name__ == '__main__':
    main()
