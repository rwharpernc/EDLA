# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for EDLA (Elite Dangerous Log Analyzer)
# 
# To build executable:
#   pyinstaller EDLA.spec
#
# Author: R.W. Harper
# Last Updated: 2025-12-09

from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('documents', 'documents'),  # Include documentation
        ('assets', 'assets'),        # Include assets (icons, etc.)
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EDLA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico' if Path('assets/app.ico').exists() else None,
)

