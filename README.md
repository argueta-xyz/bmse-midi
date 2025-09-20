# bmse-midi
Blackmagic Speed Editor MIDI Interface

## Installation
1. Install MIDI2LR
2. Edit Controllers.xml (OS dependent location) to set table_data.data.item["output"]["active"] = 0
3. Set profiles directory to `{REPO}/profiles`

## Configuration

Key mappings are defined in `config/key_mappings.json` and support multiple profiles with different interaction modes:

- **single_tap**: Command executed on single key press
- **double_tap**: Command executed on double key press (for keys with jog wheel support)
- **jog**: Command executed when turning jog wheel while key is held (for keys with jog wheel support)

### Profiles

#### Edit Profile
- **Purpose**: Photo editing with jog wheel support for parameter adjustment
- **Jog Wheel Keys**: CAM1-CAM9 keys support jog wheel interaction (defined by `jog` mapping)
- **Double-tap**: Resets the associated parameter
- **Jog**: Adjusts the parameter while key is held

#### Library Profile
- **Purpose**: Photo browsing and selection
- **Interaction**: Simple single-tap commands for navigation

### Generating XML Profiles

XML profiles are generated from the JSON configuration:

```bash
python3 scripts/generate_profiles.py config/key_mappings.json
```

This creates the XML files in the `profiles/` directory that MIDI2LR can load.

### Customizing Mappings

Edit `config/key_mappings.json` to customize key mappings:

1. Modify existing mappings in the `profiles` section
2. Add new profiles by creating new profile objects
3. Update jog modes in the `jog_modes` section
4. Regenerate XML profiles using the script above

Keys automatically support jog wheel functionality when they have a `jog` mapping defined in their profile configuration.

### MIDI Controller Mappings

The current mappings are shown in the generated XML files. Key features:

- **CAM1-CAM9**: Dual-function keys in edit mode (single-tap resets, jog adjusts)
- **Navigation keys**: Standard single-tap commands for photo navigation
- **Jog wheel**: Supports different modes (absolute, relative) for precise control
- **Profile switching**:
  - **SOURCE key**: Switches to library profile + executes `SwToMlibrary` command
  - **TIMELINE key**: Switches to edit profile + executes `SwToMdevelop` command
  - Runtime profile switching also supported via `set_profile()` method
