# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for macOS .app bundle.
Run:  pyinstaller build_macos.spec
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChatBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(BASE, 'assets', 'icon.icns'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChatBot',
)

app = BUNDLE(
    coll,
    name='ChatBot.app',
    icon=os.path.join(BASE, 'assets', 'icon.icns'),
    bundle_identifier='com.chatbot.app',
    info_plist={
        'CFBundleName': 'ChatBot',
        'CFBundleDisplayName': 'ChatBot',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
)
