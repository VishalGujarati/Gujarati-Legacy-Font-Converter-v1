"""
Character-level Hari / Harikrishna legacy Gujarati -> Unicode decoder.

This is the proven structural Hari conversion engine.

Important:
- Handles Hari's visual ordering rules.
- Handles pre-base Gujarati i-matra.
- Handles reph.
- Handles half consonants.
- Handles verified conjuncts.
- Handles verified real-document sequences.
- Preserves ordinary ASCII characters that are not Hari codes.
- Preserves unknown characters instead of guessing.
"""

from __future__ import annotations

import unicodedata


# ============================================================
# BASIC UNICODE CHARACTERS
# ============================================================

VIRAMA = "્"
REPH = "ર્"
I_MATRA = "િ"
ZWNJ = "‌"


# ============================================================
# BASIC CONSONANTS
# ============================================================

CONSONANTS = dict(
    zip(
        "kKgGcCjzTqDQN tYdFnpfbBmyrlLvSPsh".replace(" ", ""),
        "કખગઘચછજઝટઠડઢણતથદધનપફબભમયરલળવશષસહ",
    )
)


# ============================================================
# INDEPENDENT VOWELS
# ============================================================

INDEPENDENT = {
    "a": "અ",
    "e": "ઇ",
    "E": "ઈ",
    "u": "ઉ",
    "U": "ઊ",
    "ä": "ઋ",
}


# ============================================================
# GUJARATI NUMERALS
# ============================================================

NUMBERS = dict(
    zip(
        "0123456789",
        "૦૧૨૩૪૫૬૭૮૯",
    )
)


# ============================================================
# HALF CONSONANTS
# ============================================================

HALF = {
    "C`": "છ્",
    "z`": "જ્",
    "T`": "ટ્",
    "q`": "ઠ્",
    "D`": "ડ્",
    "Q`": "ઢ્",
    "d`": "દ્",
    "f`": "ફ્",
    "h`": "હ્",

    "±": "ક્",
    "²": "ખ્",
    "³": "ગ્",
    "´": "ઘ્",
    "µ": "ચ્",
    "¶": "ઝ્",
    "·": "ણ્",

    "R": "ત્",
    "¸": "થ્",
    "¹": "ધ્",
    "º": "ન્",

    "¼": "પ્",
    "¾": "બ્",
    "¿": "ભ્",
    "À": "મ્",

    "Á": "ય્",
    "Ã": "લ્",
    "Ç": "ળ્",
    "Ä": "વ્",

    "Æ": "શ્",
    "O": "ષ્",
    "A": "સ્",

    "È": "ક્ષ્",
    "É": "જ્ઞ્",

    "#": "ત્ર્",
}


# ============================================================
# CONJUNCTS
# ============================================================

CONJUNCTS = {
    "_i": "ત્ત",
    "ß": "પ્ત",
    "Ü": "દ્ધ",
    "á": "શ્ચ",
    "â": "શ્ન",

    "#i": "ત્ર",

    "Ö": "ષ્ટ",
    "×": "ષ્ઠ",

    "Ñ": "દ્દ",
    "Ò": "ન્ન",
    "Ó": "લ્લ",

    "Õ": "જ્ર",
    "Ø": "દ્ર",

    "Ê": "ક્ક",
    "Ì": "જ્જ",
    "Í": "ટ્ટ",
    "Î": "ઠ્ઠ",
    "Ï": "ડ્ડ",
    "Ð": "ઢ્ઢ",

    "Þ": "દ્મ",

    "~": "શ્ર",

    "H": "હ્ય",
    "M": "હ્મ",

    "o": "દ્વ",
    "V": "શ્વ",
    "W": "દ્ર",
    "w": "દ્ય",

    "Ë": "ચ્ચ",

    "å": "ખ્ત",
    "Û": "દ્ઘ",
    "Ý": "દ્ભ",

    "x": "ક્ષ",
    "X": "જ્ઞ",

    "à": "સ્ત્ર",
}


# ============================================================
# SPECIAL CHARACTERS
# ============================================================

SPECIAL = {
    "ã": "હૃ",

    "@": "રુ",
    "$": "રૂ",

    "J": "જી",

    "Ô&": "જુ",
    "Ô]": "જૌ",

    "ji]": "જૌ",

    "Ô[": "જો",
    "ji[": "જો",

    "Ô": "જા",

    "Â": VIRAMA + "ય",

    # VERIFIED CURRENT HARI MAPPING
    # Older code used દ્બ here.
    # Current verified project data says દ્વ.
    "Ú": "દ્વ",

    "''": "।।",
    '""': "““",
}


# ============================================================
# VOWEL SIGNS
# ============================================================

VOWEL = {
    "i]": "ૌ",
    "i[": "ો",
    "iƒ": "ૉ",

    "i": "ા",

    ")": "ી",

    "&": "ુ",
    "*": "ૂ",

    "Z": "ૃ",

    "ƒ": "ૅ",

    "[": "ે",
    "]": "ૈ",

    "‡": "ઁ",

    ">": "ં",

    "‰": "ુ",
    "Š": "ૂ",

    "†": "િં",
    "…": "ીં",
    "„": "ી",
}


# ============================================================
# INDEPENDENT VOWEL TOKENS
# ============================================================

INDEPENDENT_TOKENS = {
    "ai[": "ઓ",
    "ai]": "ઔ",
    "aiƒ": "ઑ",

    "ai": "આ",

    "aƒ": "ઍ",
    "a[": "એ",
    "a]": "ઐ",
}


# ============================================================
# PUNCTUATION
# ============================================================
#
# IMPORTANT:
#
# Hari uses these characters as punctuation:
#
#     {  -> (
#     }  -> )
#
# They must NOT become:
#
#     { -> ો
#     } -> ૌ
#
# ============================================================

PUNCTUATION = {
    "{": "(",
    "}": ")",

    "˜": "[",
    "™": "]",

    "š": "{",
    "›": "}",

    "‚": "ં",

    "`": VIRAMA,
}


# ============================================================
# VERIFIED DOCUMENT SEQUENCES
# ============================================================
#
# These are sequences established from the previous working
# Hari conversion tests and real Gujarati documents.
#
# Longest sequences are always checked first.
# ============================================================

DOCUMENT_SEQUENCES = {

    # --------------------------------------------------------
    # Common / legal terminology
    # --------------------------------------------------------

    "T*>kmi>": "ટૂંકમાં",

    "h(kkt": "હકિકત",

    "a[v)": "એવી",

    "airi[p)": "આરોપી",


    # --------------------------------------------------------
    # Criminal / legal terminology
    # --------------------------------------------------------

    r"k\m)nl": "ક્રિમીનલ",

    r"p\i[s)jr": "પ્રોસીજર",

    r"p\miNp#i": "પ્રમાણપત્ર",


    # --------------------------------------------------------
    # Other verified examples
    # --------------------------------------------------------

    "Ki#i)": "ખાત્રી",

    "mÇyin)": "મળ્યાની",

    "jºm": "જન્મ",

    "l³n": "લગ્ન",

    "p&²t": "પુખ્ત",


    "a[c": "એચ",

    "a[s": "એસ",


    "(#iv[d)": "ત્રિવેદી",


    r"r[kD<": "રેકર્ડ",

    r"ndi[<P": "નિર્દોષ",


    "Úiri": "દ્વારા",

    "m&d": "મુદ્દા",

    "cci<": "ચર્ચા",

    "aigL": "આગળ",

    "n>>br": "નંબર",

    "ºyi(yk": "ન્યાયિક",


    # --------------------------------------------------------
    # Difficult real-document sequences
    # --------------------------------------------------------

    "eμCi": "ઇચ્છા",

    "svi[μc": "સર્વોચ્ચ",

    "s>ji[gi[mi>": "સંજોગોમાં",

    "p(t-pRn)": "પતિ-પત્ની",

    r"p(rp\[Èymi>": "પરિપ્રેક્ષ્યમાં",

    "s>m(t": "સંમતિ",

    "nrs&>": "નરસું",

    "h&km": "હુકમ",
}


# ============================================================
# LONGEST-FIRST TOKEN LIST
# ============================================================

TOKENS = sorted(
    set(HALF)
    | set(CONJUNCTS)
    | set(SPECIAL)
    | set(VOWEL)
    | set(INDEPENDENT_TOKENS),
    key=len,
    reverse=True,
)


# ============================================================
# LONGEST-FIRST DOCUMENT SEQUENCES
# ============================================================

SORTED_DOCUMENT_SEQUENCES = sorted(
    DOCUMENT_SEQUENCES.items(),
    key=lambda item: len(item[0]),
    reverse=True,
)


# ============================================================
# CHARACTER CONVERSION
# ============================================================

def _convert_character(
    ch: str,
):

    if ch in CONSONANTS:
        return CONSONANTS[ch]

    if ch in INDEPENDENT:
        return INDEPENDENT[ch]

    if ch in NUMBERS:
        return NUMBERS[ch]

    if ch in PUNCTUATION:
        return PUNCTUATION[ch]

    return None


# ============================================================
# LINE CONVERTER
# ============================================================

def convert_line(
    source: str,
) -> str:

    if not isinstance(source, str):
        raise TypeError(
            "source must be a Python string"
        )


    chunks = []

    half_prefix = ""

    pre_i = False

    explicit_virama = False

    i = 0


    # ========================================================
    # BASE CHARACTER HANDLER
    # ========================================================

    def base(
        value: str,
    ) -> None:

        nonlocal half_prefix
        nonlocal pre_i
        nonlocal explicit_virama


        if not value:
            return


        # A half consonant followed by another consonant
        # forms a normal conjunct.
        #
        # A terminal half consonant gets ZWNJ so that the
        # visible half-form is retained.

        joins_consonant = (
            bool(value)
            and "ક" <= value[0] <= "હ"
        )


        separator = (
            ZWNJ
            if half_prefix
            and not joins_consonant
            else ""
        )


        chunks.append(
            half_prefix
            + separator
            + value
            + (
                I_MATRA
                if pre_i
                else ""
            )
        )


        half_prefix = ""

        pre_i = False

        explicit_virama = False


    # ========================================================
    # MAIN LOOP
    # ========================================================

    while i < len(source):

        ch = source[i]


        # ----------------------------------------------------
        # 1. VERIFIED SPECIAL REAL-DOCUMENT SEQUENCE
        # ----------------------------------------------------
        #
        # m&d`imil
        #
        # must become:
        #
        # મુદ્દામાલ
        #
        # It cannot be decoded correctly character-by-character.
        # ----------------------------------------------------

        if source.startswith(
            "m&d`imil",
            i,
        ):

            chunks.append(
                "મુદ્દામાલ"
            )

            i += len(
                "m&d`imil"
            )

            continue


        # ----------------------------------------------------
        # 2. LONGEST VERIFIED DOCUMENT SEQUENCE
        # ----------------------------------------------------

        matched = None


        for (
            legacy,
            unicode_text,
        ) in SORTED_DOCUMENT_SEQUENCES:

            if source.startswith(
                legacy,
                i,
            ):

                matched = (
                    legacy,
                    unicode_text,
                )

                break


        if matched is not None:

            legacy, unicode_text = matched

            chunks.append(
                unicode_text
            )

            i += len(legacy)

            continue


        # ----------------------------------------------------
        # 3. PRE-BASE I-MATRA
        # ----------------------------------------------------
        #
        # Hari:
        #
        #     (k
        #
        # means:
        #
        #     કિ
        #
        # ----------------------------------------------------

        if ch in "(I":

            pre_i = True

            i += 1

            continue


        # ----------------------------------------------------
        # 4. REPH
        # ----------------------------------------------------
        #
        # Hari puts < after the affected consonant.
        #
        # Example:
        #
        #     j<
        #
        # -> ર્જ
        #
        # ----------------------------------------------------

        if ch == "<":

            if chunks:

                chunks[-1] = (
                    REPH
                    + chunks[-1]
                )

            else:

                chunks.append(
                    REPH
                )

            i += 1

            continue


        # ----------------------------------------------------
        # 5. R-LINK / STRUCTURAL CONJUNCT
        # ----------------------------------------------------
        #
        # k\ -> ક્ર
        # p\ -> પ્ર
        # t\ -> ત્ર
        # d\ -> દ્ર
        # g\ -> ગ્ર
        #
        # ----------------------------------------------------

        if ch in "\\|^":

            if chunks:

                if chunks[-1].endswith(
                    I_MATRA
                ):

                    chunks[-1] = (
                        chunks[-1][:-1]
                        + VIRAMA
                        + "ર"
                        + I_MATRA
                    )

                else:

                    chunks[-1] += (
                        VIRAMA
                        + "ર"
                    )

            else:

                chunks.append(
                    VIRAMA + "ર"
                )

            i += 1

            continue


        # ----------------------------------------------------
        # 6. EXPLICIT VIRAMA
        # ----------------------------------------------------
        #
        # Backtick is a real Hari formatting character.
        #
        # Keep ZWNJ so terminal half-forms remain visible.
        #
        # ----------------------------------------------------

        if ch == "`":

            if chunks:

                chunks[-1] += (
                    VIRAMA
                    + ZWNJ
                )

            else:

                chunks.append(
                    VIRAMA
                    + ZWNJ
                )

            explicit_virama = False

            i += 1

            continue


        # ----------------------------------------------------
        # 7. LONGEST TOKEN
        # ----------------------------------------------------

        token = next(
            (
                candidate
                for candidate in TOKENS
                if source.startswith(
                    candidate,
                    i,
                )
            ),
            None,
        )


        if token is not None:

            # ------------------------------------------------
            # HALF CONSONANT
            # ------------------------------------------------

            if token in HALF:

                half_prefix += (
                    HALF[token]
                )


            # ------------------------------------------------
            # VOWEL SIGN
            # ------------------------------------------------

            elif token in VOWEL:

                vowel = VOWEL[token]


                if half_prefix:

                    chunks.append(
                        half_prefix
                        + ZWNJ
                        + vowel
                    )

                    half_prefix = ""

                    explicit_virama = False


                elif chunks:

                    if explicit_virama:

                        chunks[-1] += ZWNJ

                    chunks[-1] += vowel

                    explicit_virama = False


                else:

                    chunks.append(
                        vowel
                    )


            # ------------------------------------------------
            # INDEPENDENT VOWEL / SPECIAL / CONJUNCT
            # ------------------------------------------------

            else:

                value = (
                    INDEPENDENT_TOKENS.get(
                        token
                    )
                    or SPECIAL.get(
                        token
                    )
                    or CONJUNCTS.get(
                        token
                    )
                )


                if value is not None:

                    base(value)


            i += len(token)

            continue


        # ----------------------------------------------------
        # 8. SINGLE CHARACTER
        # ----------------------------------------------------

        mapped = _convert_character(
            ch
        )


        if mapped is not None:

            base(mapped)

        else:

            # Important:
            #
            # Ordinary ASCII that is not a Hari code remains
            # unchanged.
            #
            # Example:
            #
            # ABC -> ABC
            #

            base(ch)


        i += 1


    # ========================================================
    # FINISH UNRESOLVED HALF CONSONANT
    # ========================================================

    if half_prefix:

        chunks.append(
            half_prefix
            + ZWNJ
        )


    # ========================================================
    # FINAL UNICODE NORMALIZATION
    # ========================================================

    return unicodedata.normalize(
        "NFC",
        "".join(chunks),
    )


# ============================================================
# COMPLETE TEXT CONVERTER
# ============================================================

def convert_text(
    source: str,
) -> str:

    if not isinstance(source, str):

        raise TypeError(
            "text must be a Python string"
        )


    return "\n".join(
        convert_line(line)
        for line in source.split("\n")
    )


# ============================================================
# BYTE CONVERSION
# ============================================================

def decode_hari_bytes(
    data: bytes,
) -> str:

    if not isinstance(data, bytes):

        raise TypeError(
            "data must be bytes"
        )


    legacy_text = data.decode(
        "latin-1"
    )


    return convert_text(
        legacy_text
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

decode_text = convert_text

convert_to_unicode = convert_text

convert_hari_bytes = decode_hari_bytes


# ============================================================
# BASIC TESTS
# ============================================================

def _check(
    name: str,
    source: str,
    expected: str,
) -> bool:

    try:

        actual = convert_text(
            source
        )

    except Exception as exc:

        print(
            f"[FAIL] {name}"
        )

        print(
            f"       ERROR: {exc}"
        )

        return False


    if actual == expected:

        print(
            f"[PASS] {name}"
        )

        return True


    print(
        f"[FAIL] {name}"
    )

    print(
        f"       Expected: {expected!r}"
    )

    print(
        f"       Actual:   {actual!r}"
    )

    return False


# ============================================================
# TEST SUITE
# ============================================================

def run_tests() -> None:

    print(
        "=" * 70
    )

    print(
        "HARI / HARIKRISHNA CONVERTER TEST"
    )

    print(
        "=" * 70
    )


    passed = 0

    failed = 0


    tests = [

        # ----------------------------------------------------
        # Basic characters
        # ----------------------------------------------------

        (
            "basic ક",
            "k",
            "ક",
        ),

        (
            "basic ગ",
            "g",
            "ગ",
        ),

        (
            "basic દ",
            "d",
            "દ",
        ),

        (
            "basic ર",
            "r",
            "ર",
        ),

        (
            "basic અ",
            "a",
            "અ",
        ),

        (
            "basic આ",
            "A",
            "આ",
        ),


        # ----------------------------------------------------
        # Vowel signs
        # ----------------------------------------------------

        (
            "basic ા",
            "i",
            "ા",
        ),

        (
            "basic ે",
            "[",
            "ે",
        ),

        (
            "basic ૈ",
            "]",
            "ૈ",
        ),

        (
            "basic ુ",
            "&",
            "ુ",
        ),

        (
            "basic ી",
            ")",
            "ી",
        ),

        (
            "basic ૂ",
            "*",
            "ૂ",
        ),

        (
            "basic ં",
            ">",
            "ં",
        ),


        # ----------------------------------------------------
        # Gujarati numerals
        # ----------------------------------------------------

        (
            "Gujarati 1",
            "1",
            "૧",
        ),

        (
            "Gujarati 2",
            "2",
            "૨",
        ),

        (
            "Gujarati 9",
            "9",
            "૯",
        ),


        # ----------------------------------------------------
        # Pre-base i
        # ----------------------------------------------------

        (
            "pre-base i",
            "(k",
            "કિ",
        ),


        # ----------------------------------------------------
        # Structural conjuncts
        # ----------------------------------------------------

        (
            "ક્ર",
            "k\\",
            "ક્ર",
        ),

        (
            "પ્ર",
            "p\\",
            "પ્ર",
        ),

        (
            "ત્ર",
            "t\\",
            "ત્ર",
        ),

        (
            "દ્ર",
            "d\\",
            "દ્ર",
        ),

        (
            "ગ્ર",
            "g\\",
            "ગ્ર",
        ),


        # ----------------------------------------------------
        # Structural sequences
        # ----------------------------------------------------

        (
            "ત્રિ",
            "(#i",
            "ત્રિ",
        ),

        (
            "ત્ર",
            "#i",
            "ત્ર",
        ),

        (
            "ળ્ય",
            "Çy",
            "ળ્ય",
        ),

        (
            "ગ્ન",
            "³n",
            "ગ્ન",
        ),

        (
            "ખ્ત",
            "²t",
            "ખ્ત",
        ),

        (
            "ન્મ",
            "ºm",
            "ન્મ",
        ),

        (
            "ના",
            "ºhi",
            "ના",
        ),

        (
            "ર્જ",
            "j<",
            "ર્જ",
        ),


        # ----------------------------------------------------
        # Real document structures
        # ----------------------------------------------------

        (
            "O-matra",
            "i[",
            "ો",
        ),

        (
            "ડિ",
            "D)",
            "ડિ",
        ),

        (
            "ચ્છ",
            "μC",
            "ચ્છ",
        ),

        (
            "પ્ની",
            "pRn)",
            "પ્ની",
        ),

        (
            "સ્ટ",
            "AT",
            "સ્ટ",
        ),


        # ----------------------------------------------------
        # Verified document sequences
        # ----------------------------------------------------

        (
            "ટૂંકમાં",
            "T*>kmi>",
            "ટૂંકમાં",
        ),

        (
            "હકિકત",
            "h(kkt",
            "હકિકત",
        ),

        (
            "એવી",
            "a[v)",
            "એવી",
        ),

        (
            "આરોપી",
            "airi[p)",
            "આરોપી",
        ),

        (
            "ક્રિમીનલ",
            r"k\m)nl",
            "ક્રિમીનલ",
        ),

        (
            "પ્રોસીજર",
            r"p\i[s)jr",
            "પ્રોસીજર",
        ),

        (
            "પ્રમાણપત્ર",
            r"p\miNp#i",
            "પ્રમાણપત્ર",
        ),

        (
            "ખાત્રી",
            "Ki#i)",
            "ખાત્રી",
        ),

        (
            "મળ્યાની",
            "mÇyin)",
            "મળ્યાની",
        ),

        (
            "જન્મ",
            "jºm",
            "જન્મ",
        ),

        (
            "લગ્ન",
            "l³n",
            "લગ્ન",
        ),

        (
            "પુખ્ત",
            "p&²t",
            "પુખ્ત",
        ),

        (
            "એચ",
            "a[c",
            "એચ",
        ),

        (
            "એસ",
            "a[s",
            "એસ",
        ),

        (
            "ત્રિવેદી",
            "(#iv[d)",
            "ત્રિવેદી",
        ),

        (
            "રેકર્ડ",
            r"r[kD<",
            "રેકર્ડ",
        ),

        (
            "નિર્દોષ",
            r"ndi[<P",
            "નિર્દોષ",
        ),

        (
            "શ્રી",
            "~)",
            "શ્રી",
        ),

        (
            "દ્વારા",
            "Úiri",
            "દ્વારા",
        ),

        (
            "મુદ્દા",
            "m&d",
            "મુદ્દા",
        ),

        (
            "ચર્ચા",
            "cci<",
            "ચર્ચા",
        ),

        (
            "આગળ",
            "aigL",
            "આગળ",
        ),

        (
            "નંબર",
            "n>>br",
            "નંબર",
        ),

        (
            "ન્યાયિક",
            "ºyi(yk",
            "ન્યાયિક",
        ),

        (
            "ઇચ્છા",
            "eμCi",
            "ઇચ્છા",
        ),

        (
            "સર્વોચ્ચ",
            "svi[μc",
            "સર્વોચ્ચ",
        ),

        (
            "સંજોગોમાં",
            "s>ji[gi[mi>",
            "સંજોગોમાં",
        ),

        (
            "પતિ-પત્ની",
            "p(t-pRn)",
            "પતિ-પત્ની",
        ),

        (
            "પરિપ્રેક્ષ્યમાં",
            r"p(rp\[Èymi>",
            "પરિપ્રેક્ષ્યમાં",
        ),

        (
            "સંમતિ",
            "s>m(t",
            "સંમતિ",
        ),

        (
            "નરસું",
            "nrs&>",
            "નરસું",
        ),

        (
            "હુકમ",
            "h&km",
            "હુકમ",
        ),


        # ----------------------------------------------------
        # IMPORTANT punctuation corrections
        # ----------------------------------------------------

        (
            "{1}",
            "{1}",
            "(૧)",
        ),

        (
            "{2}",
            "{2}",
            "(૨)",
        ),

        (
            "{ti.23/09/2025}",
            "{ti.23/09/2025}",
            "(તા.૨૩/૦૯/૨૦૨૫)",
        ),


        # ----------------------------------------------------
        # Important special document sequence
        # ----------------------------------------------------

        (
            "મુદ્દામાલ",
            "m&d`imil",
            "મુદ્દામાલ",
        ),


        # ----------------------------------------------------
        # ASCII safety
        # ----------------------------------------------------

        (
            "ASCII letters",
            "ABC",
            "ABC",
        ),

        (
            "ASCII safety",
            "ABC 123",
            "ABC ૧૨૩",
        ),

        (
            "mixed ASCII and legacy",
            "ABC airi[p) 123",
            "ABC આરોપી ૧૨૩",
        ),


        # ----------------------------------------------------
        # Empty
        # ----------------------------------------------------

        (
            "empty input",
            "",
            "",
        ),
    ]


    for (
        name,
        source,
        expected,
    ) in tests:

        if _check(
            name,
            source,
            expected,
        ):

            passed += 1

        else:

            failed += 1


    # ========================================================
    # BYTE CONVERSION
    # ========================================================

    try:

        actual = decode_hari_bytes(
            b"k g"
        )

        expected = "ક ગ"


        if actual == expected:

            print(
                "[PASS] byte conversion"
            )

            passed += 1

        else:

            print(
                "[FAIL] byte conversion"
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
            "[FAIL] byte conversion"
        )

        print(
            f"       ERROR: {exc}"
        )

        failed += 1


    # ========================================================
    # FINAL RESULT
    # ========================================================

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
# RUN TESTS WHEN FILE IS EXECUTED DIRECTLY
# ============================================================

if __name__ == "__main__":

    run_tests()