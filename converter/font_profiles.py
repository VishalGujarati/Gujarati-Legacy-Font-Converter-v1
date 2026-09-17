# ============================================================
# Gujarati Legacy Font Profiles
# ============================================================
#
# The converter intentionally exposes only two user-facing
# conversion families:
#
#   1. Hari / Harikrishna
#   2. LMG Arun / Lohit BKMAN
#
# The second family uses one shared Arun/LMG conversion engine.
# ============================================================

from __future__ import annotations


FONT_PROFILES = {
    "Hari / Harikrishna": {
        "family": "hari",
        "description": "Hari / Harikrishna legacy Gujarati",
        "display_font": "HARI",
        "font_file": "hari.ttf",
        "legacy_font_names": {
            "hari",
            "harikrishna",
            "hari font",
        },
    },

    "LMG Arun / Lohit BKMAN": {
        "family": "arun",
        "description": "LMG Arun / Lohit BKMAN legacy Gujarati",
        "display_font": "LMG-Arun",
        "font_file": "LMG-Arun.ttf",
        "legacy_font_names": {
            "lmg arun",
            "lmg-arun",
            "lmg_arun",
            "lohit bkman",
            "lohit bkman regular",
            "bkman",
        },
    },
}


FONT_NAMES = list(FONT_PROFILES.keys())


# Unicode output font preference for generated DOCX files.
# The first installed/available choice is used. Word itself can
# apply its normal font fallback when the preferred font is absent.
UNICODE_OUTPUT_FONT_PREFERENCE = (
    "Lohit Gujarati",
    "Noto Sans Gujarati",
    "Shruti",
    "Nirmala UI",
    "Arial Unicode MS",
)


def get_font_profile(font_name: str) -> dict:
    """Return the profile for a user-selected legacy font family."""
    if font_name not in FONT_PROFILES:
        raise ValueError(f"Unsupported legacy font: {font_name}")
    return FONT_PROFILES[font_name]


def get_legacy_font_names(font_name: str) -> set[str]:
    """Return normalized legacy font names accepted for a profile."""
    return set(get_font_profile(font_name)["legacy_font_names"])
