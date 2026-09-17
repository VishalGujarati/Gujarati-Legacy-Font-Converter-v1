# ============================================================
# HARI / HARIKRISHNA LEGACY CONVERSION ENGINE
# ============================================================
#
# High-level conversion engine.
#
# This module:
#
#   1. Protects obvious ASCII English
#   2. Sends legacy text through text_pipeline
#   3. Normalizes Unicode
#   4. Produces diagnostics
#   5. Calculates conversion confidence
#
# IMPORTANT:
#
# Actual Hari legacy conversion rules live in:
#
#       hari_decoder.py
#       text_pipeline.py
#
# This file must NOT contain a large Gujarati word dictionary.
#
# ============================================================


from dataclasses import dataclass, field
from typing import Dict, List
import re


# ============================================================
# IMPORTS
# ============================================================

try:
    from .text_pipeline import convert_text as pipeline_convert_text
    from .unicode_normalizer import normalize_gujarati
    from .hari_decoder import map_character

except ImportError:
    from text_pipeline import convert_text as pipeline_convert_text
    from unicode_normalizer import normalize_gujarati
    from hari_decoder import map_character


# ============================================================
# RESULT OBJECT
# ============================================================

@dataclass
class ConversionResult:

    original_text: str

    decoded_text: str

    unicode_text: str

    total_characters: int

    converted_characters: int

    unresolved_characters: List[str] = field(
        default_factory=list
    )

    unresolved_count: int = 0

    unresolved_by_character: Dict[str, int] = field(
        default_factory=dict
    )

    legacy_ascii_count: int = 0

    gujarati_count: int = 0

    warnings: List[str] = field(
        default_factory=list
    )

    confidence: str = "UNKNOWN"


# ============================================================
# GUJARATI CHARACTER HELPERS
# ============================================================

def is_gujarati_character(ch: str) -> bool:

    if not ch:
        return False

    code = ord(ch)

    return (
        0x0A80
        <= code
        <= 0x0AFF
    )


def is_gujarati_letter(ch: str) -> bool:

    if not ch:
        return False

    code = ord(ch)

    return (
        0x0A85
        <= code
        <= 0x0AB9
    )


def is_gujarati_mark(ch: str) -> bool:

    if not ch:
        return False

    code = ord(ch)

    return (
        0x0ABE
        <= code
        <= 0x0ACD
    )


def is_gujarati_digit(ch: str) -> bool:

    if not ch:
        return False

    code = ord(ch)

    return (
        0x0AE6
        <= code
        <= 0x0AEF
    )


# ============================================================
# SOURCE ANALYSIS
# ============================================================

def analyze_source_text(
    text: str,
) -> Dict[str, object]:

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )

    character_counts: Dict[str, int] = {}

    ascii_count = 0
    extended_count = 0
    whitespace_count = 0

    for ch in text:

        character_counts[ch] = (
            character_counts.get(ch, 0) + 1
        )

        code = ord(ch)

        if ch in "\r\n\t ":

            whitespace_count += 1

        elif code <= 127:

            ascii_count += 1

        else:

            extended_count += 1

    return {
        "total_characters": len(text),
        "ascii_count": ascii_count,
        "extended_count": extended_count,
        "whitespace_count": whitespace_count,
        "unique_characters": len(character_counts),
        "character_counts": character_counts,
    }


# ============================================================
# OUTPUT ANALYSIS
# ============================================================

def analyze_unicode_output(
    text: str,
) -> Dict[str, int]:

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )

    gujarati_count = 0
    gujarati_letters = 0
    gujarati_marks = 0
    gujarati_digits = 0

    for ch in text:

        if is_gujarati_character(ch):

            gujarati_count += 1

        if is_gujarati_letter(ch):

            gujarati_letters += 1

        elif is_gujarati_mark(ch):

            gujarati_marks += 1

        elif is_gujarati_digit(ch):

            gujarati_digits += 1

    return {
        "total_characters": len(text),
        "gujarati_count": gujarati_count,
        "gujarati_letters": gujarati_letters,
        "gujarati_marks": gujarati_marks,
        "gujarati_digits": gujarati_digits,
    }


# ============================================================
# UNRESOLVED CHARACTER DETECTION
# ============================================================

def find_unresolved_characters(
    text: str,
):
    """
    Find suspicious non-ASCII, non-Gujarati characters.
    """

    unresolved: Dict[str, int] = {}

    for ch in text:

        if ch in "\r\n\t ":
            continue

        if is_gujarati_character(ch):
            continue

        if ord(ch) < 128:
            continue

        unresolved[ch] = (
            unresolved.get(ch, 0) + 1
        )

    characters = list(
        unresolved.keys()
    )

    return (
        characters,
        unresolved,
    )


# ============================================================
# ASCII PROTECTION
# ============================================================

def _is_uppercase_ascii(ch: str) -> bool:

    return (
        isinstance(ch, str)
        and len(ch) == 1
        and "A" <= ch <= "Z"
    )


def _is_probably_english_ascii_token(token: str) -> bool:
    """
    Protect an ASCII alphabetic token when it contains a letter that
    is not a Hari legacy glyph. This is structural, not a Gujarati
    word dictionary.

    Example: ``which`` remains ``which`` because ``w`` is not a Hari
    legacy glyph. Fully Hari-compatible lowercase words remain eligible
    for decoding because the legacy format itself has no language flag.
    """
    if not token:
        return False

    stripped = token.strip(".,;:!?()[]{}\\\"'\\t\\r\\n")
    if not stripped:
        return False

    if not all(("A" <= ch <= "Z") or ("a" <= ch <= "z") for ch in stripped):
        return False

    return any(map_character(ch) is None for ch in stripped)


def _split_protected_ascii_runs(
    text: str,
):
    """
    Protect obvious English uppercase runs.

    Hari legacy Gujarati also uses uppercase ASCII
    characters as glyphs.

    AT[Sn is a verified Hari sequence for સ્ટેશન,
    so AT must not be protected in that case.
    """

    # A Hari document legitimately uses capital ASCII characters for glyphs
    # (notably A, R, O and #).  Treating capital runs as English caused
    # sequences such as ``ATD`` (સ્ટડ) to survive unconverted.  English
    # tokens with non-Hari characters are still protected below.
    return [(text, False)] if text else []

    parts = []

    i = 0
    start = 0

    while i < len(text):

        if _is_uppercase_ascii(text[i]):

            run_start = i

            while (
                i < len(text)
                and _is_uppercase_ascii(text[i])
            ):
                i += 1

            run = text[
                run_start:i
            ]

            # AT[Sn = સ્ટેશન
            is_hari_station = (
                run == "AT"
                and text.startswith(
                    "[Sn",
                    i,
                )
            )

            if (
                len(run) >= 3
                and not is_hari_station
            ):

                if run_start > start:
                    parts.append(
                        (
                            text[
                                start:run_start
                            ],
                            False,
                        )
                    )

                parts.append(
                    (
                        run,
                        True,
                    )
                )

                start = i

            continue

        i += 1

    if start < len(text):
        parts.append(
            (
                text[start:],
                False,
            )
        )

    if not parts and text:
        parts.append(
            (
                text,
                False,
            )
        )

    return parts


# ============================================================
# SAFE PIPELINE CONVERSION
# ============================================================

def _decode_with_safe_ascii(
    text: str,
) -> str:

    if not isinstance(text, str):
        raise TypeError(
            "text must be a Python string"
        )

    if not text:
        return ""

    parts = _split_protected_ascii_runs(
        text
    )

    output = []

    for part, protected in parts:

        if protected:
            output.append(part)
            continue

        # Protect ordinary ASCII words which contain a character that
        # is not part of the Hari legacy alphabet (for example "which").
        # Do this at token level so spaces and punctuation are preserved.
        tokens = re.split(r"(\\s+)", part)
        token_output = []

        for token in tokens:
            if _is_probably_english_ascii_token(token):
                token_output.append(token)
            else:
                token_output.append(pipeline_convert_text(token))

        converted = "".join(token_output)

        output.append(
            converted
        )

    return "".join(output)


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    original_text: str,
    unicode_text: str,
    unresolved_count: int,
) -> str:

    if not original_text:

        return "HIGH"

    if unresolved_count == 0:

        return "HIGH"

    ratio = (
        unresolved_count
        / len(original_text)
    )

    if ratio > 0.10:

        return "LOW"

    return "REVIEW"


# ============================================================
# WARNINGS
# ============================================================

def generate_warnings(
    original_text: str,
    unicode_text: str,
    unresolved_count: int,
) -> List[str]:

    warnings = []

    if unresolved_count > 0:

        warnings.append(
            "Some non-Gujarati characters remain unresolved. "
            "Review the converted document."
        )

    output_info = analyze_unicode_output(
        unicode_text
    )

    if (
        len(original_text) > 10
        and output_info["gujarati_count"] == 0
    ):

        warnings.append(
            "No Gujarati Unicode characters were detected "
            "in the output."
        )

    if (
        len(original_text) > 0
        and unresolved_count
        / len(original_text)
        > 0.10
    ):

        warnings.append(
            "A significant portion of the conversion "
            "could not be confidently interpreted."
        )

    return warnings


# ============================================================
# MAIN CONVERSION
# ============================================================

def convert(
    text: str,
) -> ConversionResult:

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )

    source_info = analyze_source_text(
        text
    )

    decoded = _decode_with_safe_ascii(
        text
    )

    normalized = normalize_gujarati(
        decoded
    )

    (
        unresolved_characters,
        unresolved_by_character,
    ) = find_unresolved_characters(
        normalized
    )

    unresolved_count = sum(
        unresolved_by_character.values()
    )

    output_info = analyze_unicode_output(
        normalized
    )

    warnings = generate_warnings(
        text,
        normalized,
        unresolved_count,
    )

    confidence = calculate_confidence(
        text,
        normalized,
        unresolved_count,
    )

    return ConversionResult(

        original_text=text,

        decoded_text=decoded,

        unicode_text=normalized,

        total_characters=source_info[
            "total_characters"
        ],

        converted_characters=output_info[
            "gujarati_count"
        ],

        unresolved_characters=(
            unresolved_characters
        ),

        unresolved_count=(
            unresolved_count
        ),

        unresolved_by_character=(
            unresolved_by_character
        ),

        legacy_ascii_count=(
            source_info["ascii_count"]
        ),

        gujarati_count=(
            output_info["gujarati_count"]
        ),

        warnings=warnings,

        confidence=confidence,
    )


# ============================================================
# SIMPLE TEXT API
# ============================================================

def convert_text(
    text: str,
) -> str:

    return convert(
        text
    ).unicode_text


# ============================================================
# REPORT
# ============================================================

def print_report(
    result: ConversionResult,
) -> None:

    print()

    print("=" * 70)
    print("HARI CONVERSION REPORT")
    print("=" * 70)

    print(
        f"Input characters      : "
        f"{result.total_characters}"
    )

    print(
        f"Gujarati output        : "
        f"{result.gujarati_count}"
    )

    print(
        f"Unresolved characters : "
        f"{result.unresolved_count}"
    )

    print(
        f"Confidence             : "
        f"{result.confidence}"
    )

    if result.unresolved_by_character:

        print()
        print(
            "UNRESOLVED CHARACTERS"
        )

        for ch, count in (
            result.unresolved_by_character.items()
        ):

            print(
                f"{ch!r} "
                f"U+{ord(ch):04X} "
                f"count={count}"
            )

    if result.warnings:

        print()
        print("WARNINGS")

        for warning in result.warnings:

            print(
                f"- {warning}"
            )

    print("=" * 70)


# ============================================================
# TESTS
# ============================================================

def run_tests():

    print("=" * 70)
    print("HARI LEGACY ENGINE TEST")
    print("=" * 70)

    passed = 0
    failed = 0

    def check(
        name,
        actual,
        expected,
    ):

        nonlocal passed
        nonlocal failed

        if actual == expected:

            print(
                f"[PASS] {name}"
            )

            passed += 1

        else:

            print(
                f"[FAIL] {name}"
            )

            print(
                f"       Expected: {expected!r}"
            )

            print(
                f"       Actual:   {actual!r}"
            )

            failed += 1

    # --------------------------------------------------------
    # Basic conversion
    # --------------------------------------------------------

    result = convert(
        "a[v)"
    )

    check(
        "basic conversion",
        result.unicode_text,
        "એવી",
    )

    # --------------------------------------------------------
    # Structural conversion
    # --------------------------------------------------------

    result = convert(
        "T*>kmi>"
    )

    check(
        "structural sequence conversion",
        result.unicode_text,
        "ટૂંકમાં",
    )

    # --------------------------------------------------------
    # Standalone conjunct
    # --------------------------------------------------------

    result = convert(
        "k\\"
    )

    check(
        "conjunct conversion",
        result.unicode_text,
        "ક્ર",
    )

    # --------------------------------------------------------
    # Gujarati detection
    # --------------------------------------------------------

    check(
        "Gujarati output detection",
        is_gujarati_character("ક"),
        True,
    )

    check(
        "non-Gujarati detection",
        is_gujarati_character("A"),
        False,
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    result = convert(
        "a[v)"
    )

    check(
        "clean confidence",
        result.confidence,
        "HIGH",
    )

    # --------------------------------------------------------
    # Unknown character
    # --------------------------------------------------------

    unknown = "¤"

    result = convert(
        unknown
    )

    check(
        "unknown character preservation",
        result.unicode_text,
        unknown,
    )

    check(
        "unknown character diagnostic",
        result.unresolved_count > 0,
        True,
    )

    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    result = convert("")

    check(
        "empty input",
        result.unicode_text,
        "",
    )

    check(
        "empty input confidence",
        result.confidence,
        "HIGH",
    )

    # --------------------------------------------------------
    # ASCII safety
    # --------------------------------------------------------

    result = convert(
        "ABC 123"
    )

    check(
        "ASCII preservation",
        result.unicode_text,
        "ABC ૧૨૩",
    )

    # --------------------------------------------------------
    # Mixed input
    # --------------------------------------------------------

    result = convert(
        "ABC a[v) 123"
    )

    check(
        "mixed ASCII and legacy conversion",
        result.unicode_text,
        "ABC એવી ૧૨૩",
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print()

    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print("=" * 70)

    if failed:

        raise SystemExit(1)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()
