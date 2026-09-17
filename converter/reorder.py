"""
Gujarati Unicode Reordering Engine
==================================

Handles Unicode normalization and Gujarati vowel-sign placement.

Hari/Harikrishna legacy text often stores certain signs in a visual
keyboard order rather than the logical Unicode order.

Example:

    legacy:  (k
    mapped:  િક
    logical Gujarati: કિ

This module converts the intermediate Gujarati representation into
proper Unicode logical order.

IMPORTANT:
    This module contains NO Gujarati word-specific mappings.
"""

from __future__ import annotations

import unicodedata


# ============================================================
# GUJARATI UNICODE CONSTANTS
# ============================================================

VIRAMA = "\u0acd"

I_SIGN = "\u0abf"       # િ
E_SIGN = "\u0ac7"       # ે
AI_SIGN = "\u0ac8"      # ૈ
O_SIGN = "\u0acb"       # ો
AU_SIGN = "\u0acc"      # ૌ

ANUSVARA = "\u0a82"     # ં
VISARGA = "\u0a83"      # ઃ


# ============================================================
# GUJARATI RANGES
# ============================================================

GUJARATI_START = 0x0A80
GUJARATI_END = 0x0AFF


def is_gujarati_character(ch: str) -> bool:
    """
    Return True when ch belongs to the Gujarati Unicode block.
    """

    if not ch:
        return False

    code = ord(ch)

    return GUJARATI_START <= code <= GUJARATI_END


def is_gujarati_consonant(ch: str) -> bool:
    """
    Determine whether a character is a Gujarati consonant.

    This intentionally uses the Unicode Gujarati consonant range
    rather than a list of complete Gujarati words.
    """

    if not is_gujarati_character(ch):
        return False

    code = ord(ch)

    # Gujarati consonants:
    #
    # ક U+0A95
    # through
    # હ U+0AB9
    #
    # plus ળ U+0AB3
    #
    # There are vowels and other characters inside the broad range,
    # therefore explicit consonant ranges are used.

    return (
        0x0A95 <= code <= 0x0AB9
        and code not in {
            0x0AA0,  # ઠ? handled below by Unicode range logic
        }
    )


# Explicit consonant set.
#
# This is structural Unicode information, not word training.

GUJARATI_CONSONANTS = frozenset(
    "કખગઘઙ"
    "ચછજઝઞ"
    "ટઠડઢણ"
    "તથદધન"
    "પફબભમ"
    "યરલવ"
    "શષસહ"
    "ળ"
)


def is_consonant(ch: str) -> bool:
    return ch in GUJARATI_CONSONANTS


GUJARATI_INDEPENDENT_VOWELS = frozenset(
    "અઆઇઈઉઊઋએઐઓઔ"
)


def is_independent_vowel(ch: str) -> bool:
    return ch in GUJARATI_INDEPENDENT_VOWELS


GUJARATI_VOWEL_SIGNS = frozenset(
    "ાિીુૂૃેૈોૌંઃ"
)


def is_vowel_sign(ch: str) -> bool:
    return ch in GUJARATI_VOWEL_SIGNS


# ============================================================
# LEGACY INTERMEDIATE ORDER FIX
# ============================================================

def reorder_prebase_i(text: str) -> str:
    """
    Move legacy pre-base Gujarati i-matra into logical Unicode order.

    Legacy visual order can contain:

        િક  ->  કિ

    But an already-correct Unicode sequence such as:

        કિ

    must remain unchanged.

    Therefore, an i-matra is moved only when:
        1. it is followed by a Gujarati consonant, AND
        2. it is NOT already attached to a preceding consonant.

    This is a structural rule, not a word-specific rule.
    """

    result = []
    i = 0

    while i < len(text):

        ch = text[i]

        if ch == I_SIGN:

            previous_is_consonant = (
                i > 0 and is_consonant(text[i - 1])
            )

            next_is_consonant = (
                i + 1 < len(text)
                and is_consonant(text[i + 1])
            )

            # Legacy pre-base form:
            #
            #     િક
            #
            # becomes:
            #
            #     કિ
            #
            # But if the previous character is already a consonant,
            # the i-matra is already in logical Unicode order:
            #
            #     કિ
            #
            # Therefore do NOT move it.

            if next_is_consonant and not previous_is_consonant:

                result.append(text[i + 1])
                result.append(I_SIGN)

                i += 2
                continue

        result.append(ch)
        i += 1

    return "".join(result)


# ============================================================
# PRE-BASE VOWEL SIGNS
# ============================================================

def reorder_prebase_vowel_signs(text: str) -> str:
    """
    Normalize Gujarati pre-base vowel signs.

    Gujarati 'િ' is stored before the consonant in visual legacy
    order but after the consonant in logical Unicode order.

    Other vowel signs are normally represented after the consonant
    and therefore remain in place.
    """

    return reorder_prebase_i(text)


# ============================================================
# CONSONANT CLUSTER HANDLING
# ============================================================

def reorder_consonant_cluster(text: str) -> str:
    """
    Preserve logical Gujarati consonant clusters while normalizing
    their internal Unicode representation.

    Examples:

        ક્ર
        પ્ર
        ત્ર
        દ્વ
        ક્ષ

    are kept as logical Unicode sequences.
    """

    # At this stage we deliberately avoid aggressive rewriting.
    #
    # A Unicode consonant cluster can be represented as:
    #
    #     ક + ્ + ર
    #
    # and Unicode normalization should preserve that logical order.

    return text


# ============================================================
# COMBINING MARK NORMALIZATION
# ============================================================

def normalize_combining_marks(text: str) -> str:
    """
    Apply Unicode NFC normalization.

    This is the final Unicode-level normalization step.
    """

    return unicodedata.normalize("NFC", text)


# ============================================================
# MAIN REORDER FUNCTION
# ============================================================

def reorder_gujarati(text: str) -> str:
    """
    Perform Gujarati Unicode logical reordering.

    Pipeline:

        1. Move pre-base i-matra
        2. Preserve consonant clusters
        3. Normalize Unicode combining sequences
    """

    if not isinstance(text, str):
        raise TypeError("text must be a Python string")

    text = reorder_prebase_vowel_signs(text)

    text = reorder_consonant_cluster(text)

    text = normalize_combining_marks(text)

    return text


# ============================================================
# CLUSTER INSPECTION
# ============================================================

def inspect_cluster(text: str) -> list:
    """
    Return a structural representation of Gujarati characters.

    Useful while developing the converter.

    Example:

        inspect_cluster("હકિકત")

    returns character/type information without making any
    word-specific assumptions.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a Python string")

    rows = []

    for index, ch in enumerate(text):

        rows.append(
            {
                "index": index,
                "character": ch,
                "codepoint": f"U+{ord(ch):04X}",
                "name": unicodedata.name(
                    ch,
                    "UNKNOWN",
                ),
                "consonant": is_consonant(ch),
                "vowel": is_independent_vowel(ch),
                "vowel_sign": is_vowel_sign(ch),
                "virama": ch == VIRAMA,
            }
        )

    return rows


def print_cluster_report(text: str) -> None:
    """
    Print a readable Unicode structural report.
    """

    print()
    print("=" * 90)
    print("GUJARATI UNICODE STRUCTURE")
    print("=" * 90)

    for row in inspect_cluster(text):

        print(
            f"{row['index']:3} | "
            f"{row['character']} | "
            f"{row['codepoint']:8} | "
            f"{row['name']}"
        )

    print("=" * 90)


# ============================================================
# SELF TEST
# ============================================================

def run_tests() -> tuple[int, int]:

    tests = [
        # pre-base i
        ("િક", "કિ"),
        ("િખ", "ખિ"),
        ("િગ", "ગિ"),
        ("િત", "તિ"),
        ("િપ", "પિ"),

        # already logical
        ("કિ", "કિ"),
        ("હકિકત", "હકિકત"),

        # clusters
        ("ક્ર", "ક્ર"),
        ("પ્ર", "પ્ર"),
        ("ત્ર", "ત્ર"),
        ("દ્વ", "દ્વ"),
        ("ક્ષ", "ક્ષ"),

        # vowel signs that should remain after consonant
        ("કે", "કે"),
        ("કો", "કો"),
        ("કૌ", "કૌ"),

        # independent vowels
        ("અ", "અ"),
        ("આ", "આ"),
        ("એ", "એ"),
        ("ઓ", "ઓ"),
    ]

    passed = 0
    failed = 0

    for source, expected in tests:

        actual = reorder_gujarati(source)

        if actual == expected:

            print(
                f"[PASS] "
                f"{source!r} -> {actual!r}"
            )

            passed += 1

        else:

            print(
                f"[FAIL] "
                f"{source!r}"
            )

            print(
                f"       Expected: {expected!r}"
            )

            print(
                f"       Actual:   {actual!r}"
            )

            failed += 1

    print()
    print("=" * 70)
    print("REORDER TEST RESULT")
    print("=" * 70)
    print("Passed:", passed)
    print("Failed:", failed)

    return passed, failed


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    passed, failed = run_tests()

    if failed:
        raise SystemExit(1)