# -*- mode: python ; coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'scripts'))
from spec_common import COMMON_ANALYSIS_CONFIG, COMMON_EXE_CONFIG, COMMON_COLLECT_CONFIG

block_cipher = None

a = Analysis(**COMMON_ANALYSIS_CONFIG)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    **COMMON_EXE_CONFIG,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    **COMMON_COLLECT_CONFIG,
)

app = BUNDLE(
    coll,
    name='bmse_midi.app',
    icon=None,
    bundle_identifier='com.bmse.midi',
)
