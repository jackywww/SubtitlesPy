# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[
        '/home/jacky/anaconda3/envs/videoEnv/lib/python3.9/site-packages/paddleocr',
        '/home/jacky/anaconda3/envs/videoEnv/lib/python3.9/site-packages/paddle/libs',
        '/home/jacky/anaconda3/envs/videoEnv/lib/python3.9/site-packages/PIL'
    ],
    binaries=[
        ('/home/jacky/anaconda3/envs/videoEnv/lib/python3.9/site-packages/paddleocr', '.'),
        ('/home/jacky/anaconda3/envs/videoEnv/lib/python3.9/site-packages/paddle/libs','.'),
        ('/home/jacky/anaconda3/envs/videoEnv/lib/python3.9/site-packages/PIL', '.')
    ],
    datas=[],
    hiddenimports=[
        'paddleocr',
        'PIL',
        'tkinter',
        'PIL._tkinter_finder'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
