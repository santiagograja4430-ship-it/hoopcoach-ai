# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_all

BASE_DIR = Path(SPECPATH)

mp_datas, mp_binaries, mp_hiddenimports = collect_all("mediapipe")
ul_datas, ul_binaries, ul_hiddenimports = collect_all("ultralytics")

datas = [
    (
        str(BASE_DIR / "App" / "yolo11n.pt"),
        "App"
    ),
]

datas += mp_datas
datas += ul_datas

binaries = []
binaries += mp_binaries
binaries += ul_binaries

hiddenimports = []
hiddenimports += mp_hiddenimports
hiddenimports += ul_hiddenimports

a = Analysis(
    [str(BASE_DIR / "App" / "main.py")],

    pathex=[
        str(BASE_DIR),
        str(BASE_DIR / "App"),
    ],

    binaries=binaries,
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

    [],

    exclude_binaries=True,

    name="HoopCoachAI",

    debug=False,
    bootloader_ignore_signals=False,

    strip=False,
    upx=True,

    console=True,

    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,

    a.binaries,
    a.datas,

    strip=False,
    upx=True,

    upx_exclude=[],

    name="HoopCoachAI",
)