"""
Hari / Harikrishna Conjunct Engine
==================================

This module handles:

1. Half-consonants
2. Legacy conjunct glyphs
3. Decomposition of conjuncts into Gujarati logical components
4. Basic consonant + virama + consonant composition

IMPORTANT:
    This module does NOT contain Gujarati word mappings.

A conjunct such as:

    ક્ક
    જ્જ
    ટ્ટ
    દ્દ
    ત્ર
    દ્વ

is a character/consonant structure, not a word.

The Harikrishna template has separate tables for half consonants
and conjuncts/other characters.
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


# ============================================================
# GUJARATI VIRAMA
# ============================================================

VIRAMA = "્"


# ============================================================
# CONJUNCT DATA MODEL
# ============================================================

@dataclass(frozen=True)
class Conjunct:
    """
    Represents a Gujarati consonant cluster.

    Example:

        Conjunct("ક", "ક")
        represents
        ક્ + ક
        => ક્ક

    For a three-consonant cluster:

        Conjunct("ક", "ષ", "મ")
        represents
        ક્ + ષ્ + મ
    """

    consonants: Tuple[str, ...]

    def __post_init__(self):
        if not self.consonants:
            raise ValueError("A conjunct must contain at least one consonant.")

        for consonant in self.consonants:
            if not isinstance(consonant, str):
                raise TypeError("Consonants must be strings.")

            if len(consonant) != 1:
                raise ValueError(
                    f"Invalid consonant {consonant!r}: "
                    "expected one Gujarati character."
                )

    def to_unicode(self) -> str:
        """
        Convert the internal consonant sequence to Unicode
        logical order using Gujarati viramas.

        Example:

            ("ક", "ર")
            -> "ક્ર"
        """

        if len(self.consonants) == 1:
            return self.consonants[0]

        result = []

        for index, consonant in enumerate(self.consonants):

            result.append(consonant)

            if index < len(self.consonants) - 1:
                result.append(VIRAMA)

        return "".join(result)

    def first(self) -> str:
        return self.consonants[0]

    def last(self) -> str:
        return self.consonants[-1]

    def __str__(self) -> str:
        return self.to_unicode()


# ============================================================
# VERIFIED LEGACY CONJUNCT GLYPHS
# ============================================================
#
# These correspond to the extended legacy characters used by
# the Harikrishna template.
#
# The numeric keys are the Latin-1 character values used when
# reading the old font data byte-for-byte.
#
# ============================================================

LEGACY_CONJUNCTS = {
    # 202
    202: Conjunct(("ક", "ક")),

    # 203 intentionally unresolved
    203: None,

    # 204
    204: Conjunct(("જ", "જ")),

    # 205
    205: Conjunct(("ટ", "ટ")),

    # 206
    206: Conjunct(("ઠ", "ઠ")),

    # 207
    207: Conjunct(("ડ", "ડ")),

    # 208
    208: Conjunct(("ઢ", "ઢ")),

    # 209
    209: Conjunct(("દ", "દ")),

    # 210
    210: Conjunct(("ન", "ન")),

    # 211
    211: Conjunct(("લ", "લ")),

    # 212 is not a normal conjunct.
    # It is retained as a special legacy form.
    212: None,

    # 213 = જ્ર
    213: Conjunct(("જ", "ર")),

    # 214 = ષ્ટ
    214: Conjunct(("ષ", "ટ")),

    # 215 = ષ્ઠ
    215: Conjunct(("ષ", "ઠ")),

    # 216 unresolved
    216: None,

    # 217 = દ્ગ
    217: Conjunct(("દ", "ગ")),

    # 218 = દ્વ
    218: Conjunct(("દ", "વ")),

    # 219-229 not yet sufficiently established
    219: None,
    220: None,
    221: None,
    222: None,
    223: None,
    224: None,
    225: None,
    226: None,
    227: None,
    228: None,
    229: None,
}


# ============================================================
# HALF-CONSONANT DATA
# ============================================================
#
# The mapping module owns the actual character table.
# Here we expose the structural interpretation.
#
# ============================================================

HALF_CONSONANT_CODES = {
    177: "ક",
    178: "ખ",
    179: "ગ",
    180: "ઘ",

    181: "ચ",
    182: "છ",
    183: "જ",
    184: "ઝ",

    185: "ટ",
    186: "ઠ",
    187: "ડ",
    188: "ઢ",

    190: "ણ",

    191: "ત",
    192: "થ",
    193: "દ",
    194: "ધ",
    195: "ન",

    196: "પ",
    197: "ફ",
    198: "બ",
    199: "ભ",
    200: "મ",

    201: "ય",
}


# ============================================================
# DIRECT LEGACY CHARACTER HELPERS
# ============================================================

def legacy_char(code: int) -> str:
    """
    Convert a legacy numeric code to its Python character.

    Example:

        legacy_char(202)
        -> '\\xca'
    """

    if not 0 <= code <= 255:
        raise ValueError("Legacy code must be between 0 and 255.")

    return chr(code)


def is_half_consonant_code(code: int) -> bool:
    """
    Return True if the legacy code represents a half consonant.
    """

    return code in HALF_CONSONANT_CODES


def is_conjunct_code(code: int) -> bool:
    """
    Return True if the code is a known conjunct glyph.
    """

    value = LEGACY_CONJUNCTS.get(code)

    return value is not None


# ============================================================
# HALF-CONSONANT CONVERSION
# ============================================================

def half_consonant_to_unicode(code: int) -> Optional[str]:
    """
    Convert a half-consonant legacy code to Unicode.

    Example:

        177 -> ક્
    """

    consonant = HALF_CONSONANT_CODES.get(code)

    if consonant is None:
        return None

    return consonant + VIRAMA


# ============================================================
# CONJUNCT CONVERSION
# ============================================================

def conjunct_from_code(code: int) -> Optional[Conjunct]:
    """
    Return the structural conjunct represented by a legacy code.

    Unknown conjunct codes return None.

    We intentionally do NOT guess unknown glyphs.
    """

    return LEGACY_CONJUNCTS.get(code)


def conjunct_to_unicode(code: int) -> Optional[str]:
    """
    Convert a known legacy conjunct code directly to Unicode.
    """

    conjunct = conjunct_from_code(code)

    if conjunct is None:
        return None

    return conjunct.to_unicode()


# ============================================================
# GENERIC CONSONANT CLUSTER CREATION
# ============================================================

def make_conjunct(*consonants: str) -> Conjunct:
    """
    Create a Gujarati conjunct from consonant characters.

    Example:

        make_conjunct("ક", "ર")
        -> Conjunct(("ક", "ર"))

        .to_unicode()
        -> ક્ર
    """

    return Conjunct(tuple(consonants))


def compose_consonants(*consonants: str) -> str:
    """
    Compose one or more Gujarati consonants into logical Unicode.

    Examples:

        compose_consonants("ક")
            -> ક

        compose_consonants("ક", "ર")
            -> ક્ર

        compose_consonants("ષ", "ટ")
            -> ષ્ટ
    """

    return make_conjunct(*consonants).to_unicode()


# ============================================================
# KNOWN CONJUNCT LOOKUP BY UNICODE
# ============================================================

UNICODE_TO_CONJUNCT_CODE = {}

for code, conjunct in LEGACY_CONJUNCTS.items():

    if conjunct is None:
        continue

    unicode_value = conjunct.to_unicode()

    # Keep the first verified legacy code if duplicates ever
    # appear in the table.
    UNICODE_TO_CONJUNCT_CODE.setdefault(
        unicode_value,
        code,
    )


def find_legacy_code_for_conjunct(unicode_text: str) -> Optional[int]:
    """
    Find the known legacy code corresponding to a Unicode
    conjunct.

    This is primarily useful for diagnostics and future
    Unicode -> Hari work.

    It is NOT used by the Hari -> Unicode converter.
    """

    return UNICODE_TO_CONJUNCT_CODE.get(unicode_text)


# ============================================================
# DIAGNOSTIC REPORT
# ============================================================

def conjunct_summary() -> dict:
    """
    Return statistics about the currently known conjunct table.
    """

    total = len(LEGACY_CONJUNCTS)

    resolved = sum(
        value is not None
        for value in LEGACY_CONJUNCTS.values()
    )

    unresolved = total - resolved

    return {
        "total_codes": total,
        "resolved": resolved,
        "unresolved": unresolved,
        "half_consonants": len(HALF_CONSONANT_CODES),
    }


def print_conjunct_table() -> None:
    """
    Print the current conjunct table for diagnostics.
    """

    print()
    print("=" * 70)
    print("HARI / HARIKRISHNA CONJUNCT TABLE")
    print("=" * 70)

    for code in sorted(LEGACY_CONJUNCTS):

        conjunct = LEGACY_CONJUNCTS[code]

        if conjunct is None:
            result = "UNRESOLVED"
        else:
            result = conjunct.to_unicode()

        print(
            f"{code:3} | "
            f"U+{code:04X} | "
            f"{result}"
        )

    print("=" * 70)


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("HARI CONJUNCT ENGINE TEST")
    print("=" * 70)

    tests = [
        (202, "ક્ક"),
        (204, "જ્જ"),
        (205, "ટ્ટ"),
        (206, "ઠ્ઠ"),
        (207, "ડ્ડ"),
        (208, "ઢ્ઢ"),
        (209, "દ્દ"),
        (210, "ન્ન"),
        (211, "લ્લ"),
        (213, "જ્ર"),
        (214, "ષ્ટ"),
        (215, "ષ્ઠ"),
        (217, "દ્ગ"),
        (218, "દ્વ"),
    ]

    passed = 0
    failed = 0

    for code, expected in tests:

        actual = conjunct_to_unicode(code)

        if actual == expected:
            print(
                f"[PASS] {code} -> {actual!r}"
            )
            passed += 1
        else:
            print(
                f"[FAIL] {code} -> "
                f"expected {expected!r}, "
                f"actual {actual!r}"
            )
            failed += 1

    print()

    generic_tests = [
        (("ક", "ર"), "ક્ર"),
        (("પ", "ર"), "પ્ર"),
        (("દ", "વ"), "દ્વ"),
        (("ત", "ર"), "ત્ર"),
        (("સ", "ત", "ર"), "સ્ત્ર"),
    ]

    for consonants, expected in generic_tests:

        actual = compose_consonants(*consonants)

        if actual == expected:
            print(
                f"[PASS] "
                f"{''.join(consonants)} -> {actual!r}"
            )
            passed += 1
        else:
            print(
                f"[FAIL] "
                f"{''.join(consonants)} -> "
                f"expected {expected!r}, "
                f"actual {actual!r}"
            )
            failed += 1

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)
    print("Passed:", passed)
    print("Failed:", failed)

    if failed:
        raise SystemExit(1)