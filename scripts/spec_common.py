"""
Common PyInstaller configuration for BMSE MIDI
Shared across all platforms to reduce duplication
"""

import os

# Get project root (assuming we're running from project root)
PROJECT_ROOT = os.getcwd()

# Common Analysis configuration
COMMON_ANALYSIS_CONFIG = {
    'scripts': [os.path.join(PROJECT_ROOT, 'src', 'speed_editor_midi.py')],
    'pathex': [PROJECT_ROOT, os.path.join(PROJECT_ROOT, 'external', 'blackmagic-speededitor')],
    'binaries': [],
    'datas': [
        (os.path.join(PROJECT_ROOT, 'config'), 'config'),
        (os.path.join(PROJECT_ROOT, 'external'), 'external'),
    ],
    'hiddenimports': [
        'bmd',
        'mido',
        'mido.backends',
        'mido.backends.rtmidi',
        'hid',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'pkg_resources',
        'pkg_resources._vendor',
        'pkg_resources._vendor.appdirs',
    ],
    'hookspath': [],
    'hooksconfig': {},
    'runtime_hooks': [],
    'excludes': [],
    'cipher': None,
    'noarchive': False,
}

# Common EXE configuration
COMMON_EXE_CONFIG = {
    'exclude_binaries': True,
    'name': 'bmse_midi',
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': False,
    'upx': True,
    'console': True,
    'disable_windowed_traceback': False,
    'argv_emulation': False,
    'target_arch': None,
    'codesign_identity': None,
    'entitlements_file': None,
}

# Common COLLECT configuration
COMMON_COLLECT_CONFIG = {
    'strip': False,
    'upx': True,
    'upx_exclude': [],
    'name': 'bmse_midi',
}
