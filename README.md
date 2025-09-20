# bmse-midi
Blackmagic Speed Editor MIDI Interface

## Installation
1. Install MIDI2LR
1. Edit Controllers.xml (OS dependent location) to set table_data.data.item["output"]["active"] = 0
1. Set profiles directory to `{REPO}/profiles`

## MIDI Controller Mappings

This document outlines the MIDI mappings for the Blackmagic Speed Editor when used with MIDI2LR. The mappings are divided into two profiles: "Edit" and "Library".

### Edit Profile (`BMSpeedEditor-Edit.xml`)

In this mode, `CAM1` through `CAM9` keys have dual functions. A double-tap will reset the associated parameter, while pressing and holding the key while turning the jog wheel will adjust the parameter.

| Speed Editor Key | MIDI2LR Command (Press) | MIDI2LR Command (Jog) |
| :--- | :--- | :--- |
| `STOP_PLAY` | `AutoTone` | |
| `CAM9` | `ResetHighlights` | `Highlights` |
| `CAM8` | `ResetContrast` | `Contrast` |
| `CAM7` | `ResetExposure` | `Exposure` |
| `CAM6` | `ResetBlacks` | `Blacks` |
| `CAM5` | `ResetWhites` | `Whites` |
| `CAM4` | `ResetShadows` | `Shadows` |
| `CAM3` | `ResetDehaze` | `Dehaze` |
| `CAM2` | `ResetClarity` | `Clarity` |
| `CAM1` | `ResetTexture` | `Texture` |
| `SOURCE` | `SwToMlibrary` | |
| `ROLL` | `Reject` | |
| `TRIM_OUT` | `RemoveFlag` | |
| `TRIM_IN` | `Pick` | |
| `OUT` | `Next` | |
| `IN` | `Prev` | |

### Library Profile (`BMSpeedEditor-Library.xml`)

| Speed Editor Key | MIDI2LR Command |
| :--- | :--- |
| `PLACE_ON_TOP` | `Ctrl + Shift + D (Select only active)` |
| `SOURCE` | `SwToMlibrary` |
| `SMART_INSRT` | `ShoVwloupe` |
| `APPND` | `ShoVwcompare` |
| `AUDIO_LEVEL` | `ShoVwcompare` |
| `RIPL_OWR` | `ShoVwsurvey` |
| `RIPL_DEL` | `ShoFullPreview` |
| `FULL_VIEW` | `ToggleZoomOffOn` |
| `TRIM_IN` | `Pick` |
| `ROLL` | `Reject` |
| `TRIM_OUT` | `RemoveFlag` |
| `CLOSE_UP` | `Select1Left` |
| `SRC_OWR` | `Select1Right` |
| `OUT` | `Next` |
| `IN` | `Prev` |
| `TIMELINE` | `SwToMdevelop` |
| `STOP_PLAY` | `AutoTone` |
