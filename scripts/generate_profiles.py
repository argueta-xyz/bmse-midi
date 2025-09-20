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

def create_xml_profile(profile_name, profile_data):
    """Create XML profile from JSON data."""
    root = ET.Element('settings')

    # Add mappings for each key
    for key_name, mappings in profile_data['mappings'].items():
        # Convert string key name to SpeedEditorKey enum
        try:
            key_enum = getattr(SpeedEditorKey, key_name)
        except AttributeError:
            print(f"Warning: Unknown key {key_name}")
            continue

        # Validate configuration
        single_tap = mappings.get('single_tap')
        double_tap = mappings.get('double_tap')
        jog = mappings.get('jog')

        # Check for invalid configurations
        if single_tap is not None and jog is not None:
            raise ValueError(f"Key {key_name} has both single_tap and jog mappings. Only one is allowed.")

        # Add single tap mapping OR jog wheel mapping (exclusive)
        if single_tap:
            setting = ET.SubElement(root, 'setting')
            setting.set('channel', '1')
            setting.set('note', str(key_enum.value))
            setting.set('command_string', single_tap)
        elif jog:
            # Use the key's enum value as CC number for jog wheel
            setting = ET.SubElement(root, 'setting')
            setting.set('channel', '1')
            setting.set('controller', str(key_enum.value))
            setting.set('command_string', jog)

        # Add double tap mapping if defined (can coexist with jog)
        if double_tap:
            setting = ET.SubElement(root, 'setting')
            setting.set('channel', '1')
            setting.set('note', str(key_enum.value))
            setting.set('command_string', double_tap)

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
