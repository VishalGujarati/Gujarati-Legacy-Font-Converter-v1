"""
Hari / Harikrishna Legacy Font Mapping
======================================

V2 mapping layer.

IMPORTANT:
This file contains ONLY the underlying Hari/Harikrishna character map.

It deliberately does NOT contain:
    - Gujarati word mappings
    - document-specific words
    - sentence mappings
    - training examples
    - heuristic word replacements

Those belong in the decoder/test system, not in the character map.

The mapping is based primarily on the published Harikrishna template,
which is also used by Hari and several related legacy Gujarati fonts.
"""


# ============================================================
# BASIC CONSONANTS
# ============================================================
#
# Hari / Harikrishna normal and Shift keyboard characters.
#
# These are fundamental character mappings and are therefore
# appropriate for the mapping layer.
#
# ============================================================

FULL_CONSONANTS = {
    # ક વર્ગ
    "k": "ક",
    "K": "ખ",
    "g": "ગ",
    "G": "ઘ",

    # ચ વર્ગ
    "c": "ચ",
    "C": "છ",
    "j": "જ",
    "z": "ઝ",

    # ટ વર્ગ
    "T": "ટ",
    "q": "ઠ",
    "D": "ડ",
    "Q": "ઢ",
    "N": "ણ",

    # ત વર્ગ
    "Y": "થ",
    "t": "ત",
    "d": "દ",
    "F": "ધ",
    "n": "ન",

    # પ વર્ગ
    "p": "પ",
    "f": "ફ",
    "b": "બ",
    "B": "ભ",
    "m": "મ",

    # અંતસ્થ
    "y": "ય",
    "r": "ર",
    "l": "લ",
    "v": "વ",

    # ઉષ્મ
    "s": "સ",
    "S": "શ",
    "P": "ષ",
    "h": "હ",

    # અન્ય
    "L": "ળ",

    # Common combined forms assigned directly
    # by the Harikrishna keyboard layout.
    "x": "ક્ષ",
    "X": "જ્ઞ",
}


# ============================================================
# INDEPENDENT VOWELS
# ============================================================

VOWELS = {
    "a": "અ",
    "A": "આ",

    "e": "ઇ",
    "E": "ઈ",

    "u": "ઉ",
    "U": "ઊ",

    "R": "ઋ",

    "O": "ઓ",
    "o": "ઔ",
}


# ============================================================
# VOWEL SIGNS / ACCENTS
# ============================================================
#
# These are legacy keyboard characters representing Gujarati
# vowel signs and nasal/visarga marks.
#
# The decoder is responsible for putting these signs in the
# correct Unicode position.
#
# ============================================================

VOWEL_SIGNS = {
    # aa
    "i": "ા",
    "^": "ા",

    # e / ai
    "[": "ે",
    "]": "ૈ",

    # u / uu
    "&": "ુ",
    "*": "ૂ",

    # pre-base i
    "(": "િ",

    # ii
    ")": "ી",

    # vocalic r
    "Z": "ૃ",

    # anusvara / visarga
    ">": "ં",
    "~": "ં",
    "|": "ં",
    "?": "ઃ",

    # au / o
    "}": "ૌ",
    "{": "ો",
}


# ============================================================
# SPECIAL MULTI-CHARACTER KEY DEFINITIONS
# ============================================================
#
# These are not words.
#
# They are keyboard-level combined forms documented for
# Harikrishna-style typing.
#
# ============================================================

SPECIAL_KEY_SEQUENCES = {
    # J = જ + ી
    "J": "જી",

    # M = હ + ્ + મ
    "M": "હ્મ",

    # H = હ + ્ + ય
    "H": "હ્ય",

    # V = શ + ્ + વ
    "V": "શ્વ",

    # x = ક + ્ + ષ
    "x": "ક્ષ",

    # X = જ + ્ + ઞ
    "X": "જ્ઞ",

    # # = ત + ્ + ર
    "#": "ત્ર",

    # ~ is commonly used for શ્રી in the observed
    # Harikrishna keyboard material.
    "~": "શ્રી",
}


# ============================================================
# CONFIRMED SPECIAL LEGACY CHARACTER
# ============================================================
#
# This character was confirmed from the supplied real-document
# training corpus.
#
# Do NOT generalize this into a word mapping.
#
# ============================================================

CONFIRMED_SPECIAL_CHARACTERS = {
    "Ú": "દ્વ",
}


# ============================================================
# GUJARATI NUMERALS
# ============================================================

GUJARATI_NUMERALS = {
    "0": "૦",
    "1": "૧",
    "2": "૨",
    "3": "૩",
    "4": "૪",
    "5": "૫",
    "6": "૬",
    "7": "૭",
    "8": "૮",
    "9": "૯",
}


# ============================================================
# HALF CONSONANTS
# ============================================================
#
# These are ANSI/extended legacy characters.
#
# The Harikrishna template documents these as special characters
# inserted using Alt + 0 + character code.
#
# Example:
#     Alt + 0192 -> half મ
#
# Python ord() values below correspond to the legacy characters
# after reading the bytes as Latin-1.
#
# ============================================================

HALF_CONSONANTS = {
    177: "ક્",
    178: "ખ્",
    179: "ગ્",
    180: "ઘ્",

    181: "ચ્",
    182: "છ્",
    183: "જ્",
    184: "ઝ્",

    185: "ટ્",
    186: "ઠ્",
    187: "ડ્",
    188: "ઢ્",

    190: "ણ્",

    191: "ત્",
    192: "થ્",
    193: "દ્",
    194: "ધ્",
    195: "ન્",

    196: "પ્",
    197: "ફ્",
    198: "બ્",
    199: "ભ્",
    200: "મ્",

    201: "ય્",
}


# ============================================================
# CONJUNCTS AND OTHER EXTENDED CHARACTERS
# ============================================================
#
# IMPORTANT:
#
# We only place a value here when the mapping is sufficiently
# established.
#
# Unknown entries remain None.
#
# The decoder MUST preserve an unresolved character rather than
# guessing.
#
# ============================================================

CONJUNCTS_AND_OTHER = {

    202: "ક્ક",

    # 203 is intentionally unresolved.
    203: None,

    204: "જ્જ",
    205: "ટ્ટ",
    206: "ઠ્ઠ",
    207: "ડ્ડ",
    208: "ઢ્ઢ",
    209: "દ્દ",

    # These are retained from the established mapping.
    210: "ન્ન",
    211: "લ્લ",

    212: "જા",
    213: "જ્ર",

    214: "ષ્ટ",
    215: "ષ્ઠ",

    # Not sufficiently verified for V2 yet.
    216: None,

    217: "દ્ગ",
    218: "દ્વ",

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
# ACCENTS AND PUNCTUATION
# ============================================================
#
# These codes are retained as unresolved until their exact
# semantic meaning is established.
#
# Do not guess.
#
# ============================================================

ACCENTS_AND_PUNCTUATION = {
    130: None,
    131: None,
    132: None,
    133: None,
    134: None,
    135: None,
    136: None,
    137: None,
    138: None,
    145: None,
}


# ============================================================
# CHARACTER CATEGORY HELPERS
# ============================================================

VOWEL_SIGN_CHARS = frozenset(VOWEL_SIGNS.keys())

CONSONANT_CHARS = frozenset(FULL_CONSONANTS.keys())

VOWEL_CHARS = frozenset(VOWELS.keys())

SPECIAL_CHARS = frozenset(
    set(SPECIAL_KEY_SEQUENCES)
    | set(CONFIRMED_SPECIAL_CHARACTERS)
)


# ============================================================
# COMBINED DIRECT CHARACTER MAP
# ============================================================
#
# This is provided for compatibility with the decoder.
#
# It is NOT intended to be the complete conversion engine.
#
# ============================================================

CHAR_MAPPING = {}

CHAR_MAPPING.update(FULL_CONSONANTS)
CHAR_MAPPING.update(VOWELS)
CHAR_MAPPING.update(VOWEL_SIGNS)
CHAR_MAPPING.update(SPECIAL_KEY_SEQUENCES)
CHAR_MAPPING.update(CONFIRMED_SPECIAL_CHARACTERS)
CHAR_MAPPING.update(GUJARATI_NUMERALS)


# Extended legacy characters use their numeric character value.
for code, value in HALF_CONSONANTS.items():
    CHAR_MAPPING[chr(code)] = value


for code, value in CONJUNCTS_AND_OTHER.items():
    if value is not None:
        CHAR_MAPPING[chr(code)] = value


for code, value in ACCENTS_AND_PUNCTUATION.items():
    if value is not None:
        CHAR_MAPPING[chr(code)] = value


# ============================================================
# LOOKUP FUNCTIONS
# ============================================================

def lookup_character(ch: str):
    """
    Return the direct Unicode mapping for one legacy character.

    Returns None when the character is not known.
    """

    if not isinstance(ch, str):
        raise TypeError("ch must be a string")

    if len(ch) != 1:
        raise ValueError("lookup_character() expects exactly one character")

    return CHAR_MAPPING.get(ch)


def lookup_extended_code(code: int):
    """
    Look up an extended ANSI/legacy character code.
    """

    if code in HALF_CONSONANTS:
        return HALF_CONSONANTS[code]

    if code in CONJUNCTS_AND_OTHER:
        return CONJUNCTS_AND_OTHER[code]

    if code in ACCENTS_AND_PUNCTUATION:
        return ACCENTS_AND_PUNCTUATION[code]

    return None


def is_consonant(ch: str) -> bool:
    return ch in CONSONANT_CHARS


def is_vowel(ch: str) -> bool:
    return ch in VOWEL_CHARS


def is_vowel_sign(ch: str) -> bool:
    return ch in VOWEL_SIGN_CHARS


# ============================================================
# DIAGNOSTIC INFORMATION
# ============================================================

def mapping_summary() -> dict:
    """
    Return useful information for diagnostics/tests.
    """

    return {
        "full_consonants": len(FULL_CONSONANTS),
        "vowels": len(VOWELS),
        "vowel_signs": len(VOWEL_SIGNS),
        "numerals": len(GUJARATI_NUMERALS),
        "half_consonants": len(HALF_CONSONANTS),
        "conjuncts": len(CONJUNCTS_AND_OTHER),
        "punctuation_codes": len(ACCENTS_AND_PUNCTUATION),
        "resolved_conjuncts": sum(
            value is not None
            for value in CONJUNCTS_AND_OTHER.values()
        ),
        "unresolved_conjuncts": sum(
            value is None
            for value in CONJUNCTS_AND_OTHER.values()
        ),
    }


if __name__ == "__main__":

    print("=" * 70)
    print("HARI / HARIKRISHNA MAPPING SUMMARY")
    print("=" * 70)

    for key, value in mapping_summary().items():
        print(f"{key:25}: {value}")

    print()
    print("Basic examples:")
    print("k  ->", lookup_character("k"))
    print("r  ->", lookup_character("r"))
    print("a  ->", lookup_character("a"))
    print("(  ->", lookup_character("("))
    print("[  ->", lookup_character("["))
    print("x  ->", lookup_character("x"))
    print("X  ->", lookup_character("X"))

    print()
    print("Extended examples:")
    print("177 ->", lookup_extended_code(177))
    print("202 ->", lookup_extended_code(202))
    print("203 ->", lookup_extended_code(203))