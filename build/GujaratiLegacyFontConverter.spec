# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).resolve().parent

# Windows-only version metadata is not supported by Linux PyInstaller builds.
exe_platform_options = {}
if sys.platform.startswith("win"):
    exe_platform_options.update({
        "icon": str(ROOT / "assets" / "software_logo.ico"),
        "version": str(ROOT / "build" / "version_info.txt"),
    })

hiddenimports = (
    collect_submodules("converter")
    + collect_submodules("backend")
    + ["ipaddress", "urllib.parse", "pathlib"]
)
datas = [
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / "LICENSE.txt"), "."),
    (str(ROOT / "THIRD-PARTY-NOTICES.txt"), "."),
]

a = Analysis(
    [str(ROOT / "gui" / "app.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "setuptools", "pip"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GujaratiLegacyFontConverter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=True,
    **exe_platform_options,
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=False, name="GujaratiLegacyFontConverter"
)
