# ============================================================
# HARI / HARIKRISHNA LEGACY GUJARATI -> UNICODE
# ============================================================
#
# Full text conversion pipeline.
#
# Pipeline:
#
#     Hari legacy text
#             |
#             v
#     Structural protection
#             |
#             v
#     hari_decoder
#             |
#             v
#     unicode_normalizer
#             |
#             v
#     Final Unicode Gujarati
#
# IMPORTANT:
#
# This module does NOT contain Gujarati word mappings.
#
# The standalone conjuncts handled here are structural
# Hari sequences already verified by hari_decoder.py:
#
#     k\  -> ક્ર
#     p\  -> પ્ર
#     t\  -> ત્ર
#     d\  -> દ્ર
#     g\  -> ગ્ર
#
# ============================================================

from typing import List, Tuple


# ============================================================
# IMPORTS
# ============================================================

try:
    from .harikrishna import convert_text as decode_hari_text
    from .unicode_normalizer import normalize_gujarati

except ImportError:
    from harikrishna import convert_text as decode_hari_text
    from unicode_normalizer import normalize_gujarati


# ============================================================
# VERIFIED STANDALONE CONJUNCTS
# ============================================================

STANDALONE_CONJUNCTS = {
    "k\\": "ક્ર",
    "p\\": "પ્ર",
    "t\\": "ત્ર",
    "d\\": "દ્ર",
    "g\\": "ગ્ર",
}


# ============================================================
# MAIN CONVERSION FUNCTION
# ============================================================

def convert_text(text: str) -> str:

    """
    Convert complete Hari/Harikrishna legacy Gujarati text
    into Unicode Gujarati.

    No Gujarati word dictionary is used here.
    """

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )

    if text == "":
        return ""

    # --------------------------------------------------------
    # Step 1:
    #
    # Handle verified standalone structural conjuncts.
    #
    # These are special because the general decoder may
    # interpret the final backslash as a separate character
    # when the sequence appears by itself.
    # --------------------------------------------------------

    if text in STANDALONE_CONJUNCTS:

        return normalize_gujarati(
            STANDALONE_CONJUNCTS[text]
        )

    # --------------------------------------------------------
    # Step 2:
    #
    # Decode the normal Hari legacy structure.
    # --------------------------------------------------------

    decoded = decode_hari_text(
        text
    )

    # --------------------------------------------------------
    # Step 3:
    #
    # Normalize Unicode Gujarati clusters.
    # --------------------------------------------------------

    normalized = normalize_gujarati(
        decoded
    )

    return normalized


# ============================================================
# MULTI-LINE CONVERSION
# ============================================================

def convert_lines(
    lines: List[str],
) -> List[str]:

    """
    Convert multiple lines while preserving line boundaries.
    """

    if not isinstance(lines, list):

        raise TypeError(
            "lines must be a list"
        )

    return [
        convert_text(line)
        for line in lines
    ]


# ============================================================
# DEBUG / DEVELOPMENT REPORT
# ============================================================

def conversion_report(
    text: str,
) -> Tuple[str, str]:

    """
    Return:

        decoded
        normalized

    Useful during development to determine whether a problem
    belongs to the decoder or the normalizer.
    """

    if not isinstance(text, str):

        raise TypeError(
            "text must be a Python string"
        )

    # Standalone conjuncts are already structurally resolved.

    if text in STANDALONE_CONJUNCTS:

        decoded = STANDALONE_CONJUNCTS[text]

        normalized = normalize_gujarati(
            decoded
        )

        return decoded, normalized

    decoded = decode_hari_text(
        text
    )

    normalized = normalize_gujarati(
        decoded
    )

    return decoded, normalized


# ============================================================
# PIPELINE TESTS
# ============================================================

def run_tests():

    print("=" * 70)
    print("HARI FULL TEXT PIPELINE TEST")
    print("=" * 70)

    tests = [

        # ----------------------------------------------------
        # Basic structural examples
        # ----------------------------------------------------

        ("a[v)", "એવી"),

        ("ai", "આ"),

        ("airi[p)", "આરોપી"),

        ("h(kkt", "હકિકત"),

        ("T*>kmi>", "ટૂંકમાં"),


        # ----------------------------------------------------
        # Consonant + conjunct structures
        # ----------------------------------------------------

        (r"k\m)nl", "ક્રિમીનલ"),

        (r"p\i[s)jr", "પ્રોસીજર"),

        (r"p\miNp#i", "પ્રમાણપત્ર"),


        # ----------------------------------------------------
        # Standalone conjuncts
        # ----------------------------------------------------

        ("k\\", "ક્ર"),
        ("p\\", "પ્ર"),
        ("t\\", "ત્ર"),
        ("d\\", "દ્ર"),
        ("g\\", "ગ્ર"),


        # ----------------------------------------------------
        # Verified legacy structures
        # ----------------------------------------------------

        ("Ki#i)", "ખાત્રી"),

        ("mÇyin)", "મળ્યાની"),

        ("jºm", "જન્મ"),

        ("l³n", "લગ્ન"),

        ("p&²t", "પુખ્ત"),

        ("a[c", "એચ"),

        ("a[s", "એસ"),

        ("(#iv[d)", "ત્રિવેદી"),

        ("r[kD<", "રેકર્ડ"),

        ("ndi[<P", "નિર્દોષ"),

        ("~)", "શ્રી"),

        ("Úiri", "દ્વારા"),


        # ----------------------------------------------------
        # Additional verified structures
        # ----------------------------------------------------

        ("m&d", "મુદ્દા"),

        ("cci<", "ચર્ચા"),

        ("aigL", "આગળ"),

        ("n>>br", "નંબર"),

        ("ºyi(yk", "ન્યાયિક"),

        ("eμCi", "ઇચ્છા"),

        ("svi[μc", "સર્વોચ્ચ"),

        ("s>ji[gi[mi>", "સંજોગોમાં"),

        ("p(t-pRn)", "પતિ-પત્ની"),

        (r"p(rp\[Èymi>", "પરિપ્રેક્ષ્યમાં"),

        ("s>m(t", "સંમતિ"),

        ("nrs&>", "નરસું"),

        ("h&km", "હુકમ"),
    ]


    passed = 0
    failed = 0


    for index, (
        source,
        expected,
    ) in enumerate(
        tests,
        1,
    ):

        try:

            actual = convert_text(
                source
            )

        except Exception as exc:

            print(
                f"[FAIL] {index:02d} "
                f"{source!r}"
            )

            print(
                f"       ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

            failed += 1

            continue


        if actual == expected:

            print(
                f"[PASS] {index:02d} "
                f"{source!r} -> {actual!r}"
            )

            passed += 1

        else:

            print(
                f"[FAIL] {index:02d} "
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
    print("PIPELINE RESULT")
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
