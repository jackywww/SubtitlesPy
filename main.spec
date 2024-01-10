# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[
        'E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\paddleocr',
        'E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\paddle\\libs',
        'E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\numpy.libs',
        'E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\PIL'
    ],
    binaries=[
        ('E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\paddleocr', '.'),
        ('E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\paddle\libs','.'),
        ('E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\numpy.libs','.'),
        ('E:\\anaconda3\\envs\\videoenv\\lib\\site-packages\\PIL', '.')
    ],
    datas=[],
    hiddenimports=[
        'paddleocr',
        'PIL',
        'tkinter',
        'numpy',
        'PIL._tkinter_finder',
        'addict',
        'yapf'
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
