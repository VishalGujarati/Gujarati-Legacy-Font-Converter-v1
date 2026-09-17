# Hari/Harikrishna Legacy Gujarati -> Unicode
#
# Unicode cluster normalizer.
#
# This module handles Unicode character ordering after the
# Hari legacy decoder.
#
# IMPORTANT:
# No Gujarati word-by-word mappings belong here.


import unicodedata


# ============================================================
# CONSTANTS
# ============================================================

PREBASE_I = "િ"


# ============================================================
# GUJARATI BASE CHARACTER CHECK
# ============================================================

def is_gujarati_base(ch: str) -> bool:
    """
    Return True if the character can act as a Gujarati
    base character.

    This includes Gujarati consonants and independent vowels,
    but excludes Gujarati vowel signs and combining marks.
    """

    if not ch:
        return False

    code = ord(ch)

    # Gujarati Unicode block.
    if not (0x0A80 <= code <= 0x0AFF):
        return False

    # Gujarati vowel signs / combining marks.
    if 0x0ABE <= code <= 0x0ACC:
        return False

    # Gujarati virama.
    if code == 0x0ACD:
        return False

    # Other combining characters.
    if unicodedata.combining(ch) != 0:
        return False

    return True


# ============================================================
# PRE-BASE I-MATRA NORMALIZATION
# ============================================================

def normalize_prebase_i(text: str) -> str:
    """
    Repair Gujarati pre-base i-matra.

    Hari legacy decoding can produce:

        િક

    which logically means:

        કિ

    However, an already-correct sequence such as:

        કિ

    must NOT be changed.

    Therefore we only move the i-matra when:

        current character = િ
        next character = Gujarati base
        previous character is NOT a Gujarati base

    This prevents:

        હકિકત

    from becoming:

        હકકિત
    """

    result = []

    i = 0

    while i < len(text):

        ch = text[i]


        # ----------------------------------------------------
        # We only care about the Gujarati i-matra.
        # ----------------------------------------------------

        if ch == PREBASE_I:

            previous_is_base = (
                i > 0 and
                is_gujarati_base(text[i - 1])
            )

            next_is_base = (
                i + 1 < len(text) and
                is_gujarati_base(text[i + 1])
            )


            # ------------------------------------------------
            # If a Gujarati base is already immediately before
            # the i-matra, the i-matra is already correctly
            # attached to that base.
            #
            # Example:
            #
            #     કિ
            #
            # Leave it alone.
            # ------------------------------------------------

            if previous_is_base:

                result.append(ch)

                i += 1

                continue


            # ------------------------------------------------
            # If there is no base before it but a base after it,
            # this is the legacy pre-base representation.
            #
            # Example:
            #
            #     િક
            #
            # becomes:
            #
            #     કિ
            # ------------------------------------------------

            if not previous_is_base and next_is_base:

                result.append(text[i + 1])
                result.append(PREBASE_I)

                i += 2

                continue


        # ----------------------------------------------------
        # Normal character.
        # ----------------------------------------------------

        result.append(ch)

        i += 1


    return "".join(result)


# ============================================================
# MAIN NORMALIZER
# ============================================================

def normalize_gujarati(text: str) -> str:
    """
    Normalize decoded Gujarati Unicode text.

    Processing:

        1. NFC normalization
        2. Repair genuine pre-base i-matra
        3. Final NFC normalization
    """

    if not isinstance(text, str):
        raise TypeError("text must be a Python string")


    # --------------------------------------------------------
    # First NFC normalization.
    # --------------------------------------------------------

    text = unicodedata.normalize(
        "NFC",
        text
    )


    # --------------------------------------------------------
    # Repair only genuine pre-base i-matra sequences.
    # --------------------------------------------------------

    text = normalize_prebase_i(text)


    # --------------------------------------------------------
    # Final NFC normalization.
    # --------------------------------------------------------

    return unicodedata.normalize(
        "NFC",
        text
    )


# ============================================================
# TESTS
# ============================================================

def run_tests():

    print("=" * 70)

    print("UNICODE NORMALIZER TEST")

    print("=" * 70)


    tests = [

        # ----------------------------------------------------
        # Genuine pre-base i-matra
        # ----------------------------------------------------

        ("િક", "કિ"),
        ("િખ", "ખિ"),
        ("િગ", "ગિ"),
        ("િત", "તિ"),
        ("િપ", "પિ"),


        # ----------------------------------------------------
        # Already-correct i-matra
        # ----------------------------------------------------

        ("કિ", "કિ"),

        ("હકિકત", "હકિકત"),

        ("આરોપી", "આરોપી"),


        # ----------------------------------------------------
        # Conjuncts
        # ----------------------------------------------------

        ("ક્ર", "ક્ર"),
        ("પ્ર", "પ્ર"),
        ("ત્ર", "ત્ર"),
        ("દ્વ", "દ્વ"),
        ("ક્ષ", "ક્ષ"),


        # ----------------------------------------------------
        # Vowel signs
        # ----------------------------------------------------

        ("કે", "કે"),
        ("કો", "કો"),
        ("કૌ", "કૌ"),


        # ----------------------------------------------------
        # Independent vowels
        # ----------------------------------------------------

        ("અ", "અ"),
        ("આ", "આ"),
        ("એ", "એ"),
        ("ઓ", "ઓ"),
    ]


    passed = 0
    failed = 0


    for source, expected in tests:

        actual = normalize_gujarati(source)


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


    print()

    print("=" * 70)

    print("RESULT")

    print("=" * 70)

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


    if failed:
        raise SystemExit(1)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()