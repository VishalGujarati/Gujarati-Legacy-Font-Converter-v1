# ============================================================
# Unicode Gujarati Output Font Utilities
# ============================================================

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

try:
    from .font_profiles import UNICODE_OUTPUT_FONT_PREFERENCE
except ImportError:
    from font_profiles import UNICODE_OUTPUT_FONT_PREFERENCE


def _normalize_name(name: str) -> str:
    return " ".join(str(name).strip().lower().split())


def _linux_font_families() -> set[str]:
    """Read installed font family names from fontconfig when available."""
    try:
        result = subprocess.run(
            ["fc-list", ":", "family"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return set()

    families: set[str] = set()
    for line in result.stdout.splitlines():
        for family in line.split(","):
            family = family.strip()
            if family:
                families.add(_normalize_name(family))
    return families


def _windows_font_families() -> set[str]:
    """Read installed Windows font family names without installing anything."""
    families: set[str] = set()

    try:
        import winreg

        registry_locations = (
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Fonts"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
        )

        for hive, path in registry_locations:
            try:
                key = winreg.OpenKey(
                    hive,
                    path,
                )
            except OSError:
                continue

            try:
                index = 0
                while True:
                    try:
                        name, _value, _kind = winreg.EnumValue(key, index)
                    except OSError:
                        break

                    # Registry names are normally like:
                    # "Lohit Gujarati (TrueType)"
                    clean = re_sub_font_suffix(name)
                    if clean:
                        families.add(_normalize_name(clean))
                    index += 1
            finally:
                winreg.CloseKey(key)

    except Exception:
        pass

    # User-installed fonts can live under the current user's profile.
    local_font_dir = (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Microsoft"
        / "Windows"
        / "Fonts"
    )
    if local_font_dir.exists():
        # We cannot reliably derive family names from filenames alone,
        # so the registry remains the primary source.
        pass

    return families


def re_sub_font_suffix(name: str) -> str:
    value = str(name).strip()
    for suffix in (" (TrueType)", " (OpenType)", " (Type 1)"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value.strip()


def installed_unicode_font_names() -> set[str]:
    """Return normalized installed font family names when detectable."""
    system = platform.system().lower()

    if system == "windows":
        return _windows_font_families()

    # Linux and most Unix desktops provide fontconfig.
    return _linux_font_families()


def choose_unicode_output_font() -> str:
    """
    Choose the preferred Unicode Gujarati font.

    Lohit Gujarati is always preferred when it is detectable.
    If detection is unavailable, it remains the safe default because
    Word and other document editors will perform their normal fallback.
    """
    installed = installed_unicode_font_names()

    if installed:
        for name in UNICODE_OUTPUT_FONT_PREFERENCE:
            if _normalize_name(name) in installed:
                return name

    return UNICODE_OUTPUT_FONT_PREFERENCE[0]


def is_unicode_gujarati_font_available(font_name: str) -> bool:
    installed = installed_unicode_font_names()
    return not installed or _normalize_name(font_name) in installed
