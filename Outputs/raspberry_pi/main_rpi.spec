# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

# Collect static assets for CustomTkinter and Librosa
datas = [
    ('../../ml_core/accent_svm_pipeline.joblib', 'ml_core'),
]
datas += collect_data_files('customtkinter')
datas += collect_data_files('librosa')

hiddenimports = [
    'sounddevice',
    'soundfile',
    'numpy',
    'scipy',
    'scipy.signal',
    'librosa',
    'sklearn',
    'sklearn.utils._typedefs',
    'joblib',
    'customtkinter',
]

a = Analysis(
    ['../../main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AccentClassifier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX often causes issues on ARM architectures (Raspberry Pi)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Useful for debugging terminal output and audio device selection on Raspberry Pi
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
