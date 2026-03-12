# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Windows .exe installer.
Run on Windows:  pyinstaller build_windows.spec
"""

import os

block_cipher = None
BASE = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(BASE, 'chatbot.py')],
    pathex=[BASE],
    binaries=[],
    datas=[
        (os.path.join(BASE, 'config.json'), '.'),
    ],
    hiddenimports=[
        'requests',
        'bs4',
        'markdown',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Single-file .exe for Windows
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChatBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(BASE, 'assets', 'icon.ico'),
)
