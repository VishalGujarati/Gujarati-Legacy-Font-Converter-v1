"""
Hari / Harikrishna legacy Gujarati -> Unicode decoder.

This module provides the public decoder API used by the
application.

The actual conversion engine is the proven harikrishna.py
implementation.

Keeping one conversion engine prevents:
    GUI
    API
    text pipeline
    diagnostics

from producing different Hari results.
"""

from __future__ import annotations

from typing import (
    Optional,
    Tuple,
    List,
    Dict,
    Any,
)

try:

    from .harikrishna import (
        convert_text,
        convert_line,
        decode_hari_bytes,
        decode_text,
        convert_to_unicode,
        convert_hari_bytes,

        CONSONANTS,
        INDEPENDENT,
        NUMBERS,
        HALF,
        CONJUNCTS,
        SPECIAL,
        VOWEL,
        INDEPENDENT_TOKENS,
        PUNCTUATION,
        DOCUMENT_SEQUENCES,
        SORTED_DOCUMENT_SEQUENCES,
        TOKENS,
    )

except ImportError:

    from harikrishna import (
        convert_text,
        convert_line,
        decode_hari_bytes,
        decode_text,
        convert_to_unicode,
        convert_hari_bytes,

        CONSONANTS,
        INDEPENDENT,
        NUMBERS,
        HALF,
        CONJUNCTS,
        SPECIAL,
        VOWEL,
        INDEPENDENT_TOKENS,
        PUNCTUATION,
        DOCUMENT_SEQUENCES,
        SORTED_DOCUMENT_SEQUENCES,
        TOKENS,
    )


# ============================================================
# PUBLIC MAP
# ============================================================

DIRECT_MAP: Dict[str, str] = {}


DIRECT_MAP.update(
    CONSONANTS
)

DIRECT_MAP.update(
    INDEPENDENT
)

DIRECT_MAP.update(
    NUMBERS
)

DIRECT_MAP.update(
    PUNCTUATION
)


# ============================================================
# SINGLE CHARACTER MAPPING
# ============================================================

def map_character(
    ch: str,
) -> Optional[str]:

    if not isinstance(ch, str):

        raise TypeError(
            "ch must be a Python string"
        )


    if len(ch) != 1:

        raise ValueError(
            "map_character() expects exactly one character"
        )


    if ch in DIRECT_MAP:

        return DIRECT_MAP[ch]


    # Vowel signs are generally structural and are therefore
    # handled by the main Hari engine. They are nevertheless
    # exposed here for compatibility.

    if ch in VOWEL:

        return VOWEL[ch]


    # Some special one-character codes are also exposed.

    if ch in SPECIAL:

        return SPECIAL[ch]


    if ch in CONJUNCTS:

        return CONJUNCTS[ch]


    return None


# ============================================================
# FIND VERIFIED SEQUENCE
# ============================================================

def find_sequence(
    text: str,
    position: int,
) -> Optional[
    Tuple[str, str]
]:

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )


    if position < 0:

        return None


    if position >= len(text):

        return None


    for (
        legacy,
        unicode_text,
    ) in SORTED_DOCUMENT_SEQUENCES:

        if text.startswith(
            legacy,
            position,
        ):

            return (
                legacy,
                unicode_text,
            )


    return None


# ============================================================
# MAIN PUBLIC DECODER
# ============================================================

def decode_hari_text(
    text: str,
) -> str:
    """
    Decode Hari / Harikrishna legacy Gujarati text.
    """

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )


    return convert_text(
        text
    )


# ============================================================
# ALIASES
# ============================================================

decode_text = decode_hari_text

convert_to_unicode = decode_hari_text

convert_hari_bytes = decode_hari_bytes


# ============================================================
# GUJARATI UNICODE TEST
# ============================================================

def is_gujarati_unicode(
    ch: str,
) -> bool:

    if not ch:

        return False


    code = ord(ch)


    return (
        0x0A80
        <= code
        <= 0x0AFF
    )


# ============================================================
# UNKNOWN CHARACTER DETECTION
# ============================================================

def find_unknown_characters(
    text: str,
) -> List[str]:
    """
    Find unresolved non-ASCII legacy characters.

    Ordinary ASCII is intentionally not reported as unknown.
    """

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )


    unknown = []

    seen = set()

    i = 0


    while i < len(text):

        # ----------------------------------------------------
        # Verified sequence
        # ----------------------------------------------------

        match = find_sequence(
            text,
            i,
        )


        if match is not None:

            i += len(
                match[0]
            )

            continue


        # ----------------------------------------------------
        # Special m&d`imil sequence
        # ----------------------------------------------------

        if text.startswith(
            "m&d`imil",
            i,
        ):

            i += len(
                "m&d`imil"
            )

            continue


        ch = text[i]


        # ----------------------------------------------------
        # Whitespace
        # ----------------------------------------------------

        if ch in "\r\n\t ":

            i += 1

            continue


        # ----------------------------------------------------
        # Existing Unicode Gujarati
        # ----------------------------------------------------

        if is_gujarati_unicode(ch):

            i += 1

            continue


        # ----------------------------------------------------
        # Known legacy character
        # ----------------------------------------------------

        if map_character(ch) is not None:

            i += 1

            continue


        # ----------------------------------------------------
        # ASCII
        # ----------------------------------------------------

        if ord(ch) < 128:

            i += 1

            continue


        # ----------------------------------------------------
        # Unknown non-ASCII
        # ----------------------------------------------------

        if ch not in seen:

            unknown.append(ch)

            seen.add(ch)


        i += 1


    return unknown


# ============================================================
# CONVERSION DIAGNOSTICS
# ============================================================

def conversion_diagnostics(
    text: str,
) -> Dict[str, Any]:

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )


    output = decode_hari_text(
        text
    )


    unknown = find_unknown_characters(
        text
    )


    gujarati_count = sum(
        0x0A80 <= ord(ch) <= 0x0AFF
        for ch in output
    )


    ascii_count = sum(
        ord(ch) < 128
        for ch in output
    )


    return {
        "input_characters": len(text),

        "output_characters": len(output),

        "gujarati_characters": gujarati_count,

        "ascii_characters": ascii_count,

        "unknown_characters": unknown,

        "unknown_count": len(unknown),

        "clean": len(unknown) == 0,

        "output": output,
    }


# ============================================================
# LEGACY INSPECTION
# ============================================================

def inspect_legacy_text(
    text: str,
) -> List[Dict[str, Any]]:

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )


    rows = []


    for index, ch in enumerate(text):

        code = ord(ch)


        mapped = map_character(
            ch
        )


        sequence_match = find_sequence(
            text,
            index,
        )


        if sequence_match is not None:

            sequence = sequence_match[0]

            sequence_result = sequence_match[1]

            status = "sequence"


        elif mapped is not None:

            sequence = None

            sequence_result = None

            status = "mapped"


        elif is_gujarati_unicode(ch):

            sequence = None

            sequence_result = None

            status = "unicode"


        elif ord(ch) < 128:

            sequence = None

            sequence_result = None

            status = "ascii"


        else:

            sequence = None

            sequence_result = None

            status = "UNRESOLVED"


        rows.append(
            {
                "index": index,

                "character": ch,

                "code": code,

                "hex": f"0x{code:02X}",

                "unicode": f"U+{code:04X}",

                "mapped": mapped,

                "sequence": sequence,

                "sequence_result": sequence_result,

                "status": status,
            }
        )


    return rows


# ============================================================
# PRINT DIAGNOSTIC REPORT
# ============================================================

def print_legacy_report(
    text: str,
) -> None:

    print()

    print(
        "=" * 100
    )

    print(
        "HARI LEGACY CHARACTER REPORT"
    )

    print(
        "=" * 100
    )


    for row in inspect_legacy_text(
        text
    ):

        print(
            f"{row['index']:4} | "
            f"{row['character']!r:6} | "
            f"{row['code']:3} | "
            f"{row['hex']:>6} | "
            f"{row['unicode']:>8} | "
            f"{row['status']:10} | "
            f"mapped={row['mapped']!r} | "
            f"sequence={row['sequence']!r} | "
            f"result={row['sequence_result']!r}"
        )


    print(
        "=" * 100
    )


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    print(
        "=" * 70
    )

    print(
        "HARI DECODER PUBLIC API TEST"
    )

    print(
        "=" * 70
    )


    tests = [

        (
            "{1}",
            "(૧)",
        ),

        (
            "{2}",
            "(૨)",
        ),

        (
            "{ti.23/09/2025}",
            "(તા.૨૩/૦૯/૨૦૨૫)",
        ),

        (
            "airi[p)",
            "આરોપી",
        ),

        (
            r"k\m)nl",
            "ક્રિમીનલ",
        ),

        (
            r"p\i[s)jr",
            "પ્રોસીજર",
        ),

        (
            r"p\miNp#i",
            "પ્રમાણપત્ર",
        ),

        (
            "(#iv[d)",
            "ત્રિવેદી",
        ),

        (
            r"r[kD<",
            "રેકર્ડ",
        ),

        (
            r"ndi[<P",
            "નિર્દોષ",
        ),

        (
            "Úiri",
            "દ્વારા",
        ),

        (
            "m&d",
            "મુદ્દા",
        ),

        (
            "m&d`imil",
            "મુદ્દામાલ",
        ),

        (
            "~)",
            "શ્રી",
        ),

        (
            "ABC",
            "ABC",
        ),

        (
            "ABC 123",
            "ABC ૧૨૩",
        ),

        (
            "ABC airi[p) 123",
            "ABC આરોપી ૧૨૩",
        ),

        (
            "",
            "",
        ),
    ]


    passed = 0

    failed = 0


    for source, expected in tests:

        try:

            actual = decode_hari_text(
                source
            )


            if actual == expected:

                print(
                    f"[PASS] {source!r} -> {actual!r}"
                )

                passed += 1

            else:

                print(
                    f"[FAIL] {source!r}"
                )

                print(
                    f"       Expected: {expected!r}"
                )

                print(
                    f"       Actual:   {actual!r}"
                )

                failed += 1


        except Exception as exc:

            print(
                f"[FAIL] {source!r}"
            )

            print(
                f"       ERROR: {exc}"
            )

            failed += 1


    print()

    print(
        "=" * 70
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        "=" * 70
    )


    if failed:

        raise SystemExit(1)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()