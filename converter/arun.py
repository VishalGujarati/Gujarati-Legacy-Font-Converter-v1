# ============================================================
# Arun / LMG Family -> Unicode Gujarati Converter
# ============================================================
#
# MAPPING-LEVEL / STRUCTURAL DECODER
#
# IMPORTANT:
#   - Do NOT add individual Gujarati words here.
#   - arun_mapping.py contains the character mapping.
#   - This file handles how legacy characters interact.
#   - Hari / Harikrishna conversion is completely separate.
#
# ============================================================

from __future__ import annotations


try:
    from .arun_mapping import CHARACTER_MAP, SORTED_SEQUENCES
    from .unicode_normalizer import normalize_gujarati

except ImportError:
    from arun_mapping import CHARACTER_MAP, SORTED_SEQUENCES
    from unicode_normalizer import normalize_gujarati


# ============================================================
# LEGACY CONTROLS
# ============================================================

I_MATRA_INPUT = "l"
RFORM_INPUT = '"'

AA_INPUT = "F"
E_INPUT = "["
O_INPUT = "M"
AI_INPUT = "{"


# These characters continue a Gujarati conjunct / cluster.
CLUSTER_CONTROLS = {
    "|",
    "=",
}


# ============================================================
# BASIC HELPERS
# ============================================================

def _replace_last_character(
    text: str,
    replacement: str,
) -> str:

    if not text:
        return replacement

    return (
        text[:-1]
        + replacement
    )


def _normalize_arun_marks(
    text: str,
) -> str:
    # Structural cleanup for common legacy typist input artifacts.
    # This intentionally does not correct Gujarati spelling.
    import re

    gujarati_consonants = "કખગઘઙચછજઝઞટઠડઢણતથદધનપફબભમયરલવશષસહળ"
    vowel_signs = "ાિીુૂૃેૈોૌંઃ"

    # 1) A Gujarati vowel sign may be separated from its base by an
    #    ordinary space, e.g. "અ ે" or "ગ ા ે". A standalone vowel sign
    #    is not a valid Gujarati base, so joining these marks is safe.
    text = re.sub(
        rf"([\u0A80-\u0AFF]) +([{vowel_signs}])",
        r"\1\2",
        text,
    )
    # If there are multiple separated marks, the first pass can expose
    # another mark-to-mark space, e.g. ગ ા ે -> ગા ે.
    text = re.sub(
        rf"([{vowel_signs}]) +([{vowel_signs}])",
        r"\1\2",
        text,
    )

    # 2) Some legacy typing places AA between a half consonant and the next
    #    consonant: મ્ + ા + ય. Move the AA after that consonant. This must
    #    happen BEFORE the invalid-virama cleanup below.
    text = re.sub(
        rf"([{gujarati_consonants}])્ા([{gujarati_consonants}])",
        r"\1્\2ા",
        text,
    )

    # 3) A virama immediately followed by a vowel sign is structurally
    #    invalid Gujarati Unicode. In the legacy data this can happen when
    #    a half-form such as ળ્ was typed where the full consonant ળ was meant.
    text = re.sub(
        r"્(?=[ાિીુૂૃેૈોૌ])",
        "",
        text,
    )

    # 4) O-matra may be entered as AA + E or E + AA. Also collapse a
    #    duplicate AA typed after an already formed O/AU matra.
    return (
        text
        .replace("ાા", "ા")
        .replace("ાે", "ો")
        .replace("ેા", "ો")
        # Typists sometimes build AU-matra (ૌ) as AA + AI (ા + ૈ),
        # in either order. This is the same structural typing-order
        # problem as AA + E -> O (ો), and is not a dictionary correction.
        .replace("ાૈ", "ૌ")
        .replace("ૈા", "ૌ")
        .replace("અે", "એ")
        .replace("ોા", "ો")
        .replace("ૌા", "ૌ")
        .replace("આે", "ઓ")
        .replace("એા", "ઓ")
        .replace("આૈ", "ઔ")
        .replace("ૈઆ", "ઔ")
        .replace("ંુ", "ું")
        .replace("ંૂ", "ૂં")
    )

def _is_gujarati_base(
    ch: str,
) -> bool:

    if not ch:
        return False

    code = ord(ch)

    return (
        0x0A85 <= code <= 0x0AB9
    )


# ============================================================
# NUMBERS
# ============================================================

NUMERIC_CONTEXT_MAP = {

    # Unambiguous numeric glyphs used by the legacy encoding.
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

    "!": "૧",
    "@": "૨",
    "#": "૩",
    "$": "૪",
    "%": "૫",
    "^": "૬",
    "&": "૭",
    "*": "૮",
    "(": "૯",
    ")": "૦",

    "_": "૦",
}

# In LMG-Arun, these two source glyphs are intentionally ambiguous:
#   Z -> ર in normal Gujarati text, but ૨ in numeric text
#   5 -> પ in normal Gujarati text, but ૫ in numeric text
#
# We must NOT globally remap them. The original legacy author may have
# used the same source glyph for either meaning. Context is therefore used
# only when the glyph is part of a recognizable numeric expression.
AMBIGUOUS_NUMERIC_MAP = {
    "Z": "૨",
    "5": "૫",
}

# Numeric separators in the Arun encoding. They are not enough by
# themselves to make an ambiguous glyph numeric; there must also be at
# least one unambiguous numeric glyph in the same local expression.
NUMERIC_SEPARATORS = {
    "q",   # /
    "v",   # -
    "P",   # .
}

# A numeric expression may contain these source glyphs. This is deliberately
# conservative so ordinary Gujarati words containing Z/5 are not changed.
# A stray backslash is occasionally typed inside a date/number, e.g.
# Z5q\_5qZ# for 25/05/23. In ordinary Gujarati it still means anusvara,
# so it is treated as numeric noise only when the surrounding token is
# otherwise a recognizable numeric expression.
NUMERIC_EXPRESSION_CHARS = (
    set(NUMERIC_CONTEXT_MAP)
    | set(AMBIGUOUS_NUMERIC_MAP)
    | NUMERIC_SEPARATORS
    | {"\\"}
)


# 5 is deliberately excluded because it is ambiguous between પ and ૫.
# Z is not in NUMERIC_CONTEXT_MAP at all because it is ambiguous between ર and ૨.
# These legacy source glyphs are unambiguously numeric when they appear in
# an expression.  The ordinary ASCII digits 0-9 are *not* included here
# because in LMG-Arun they are also legacy Gujarati glyphs (for example 4
# maps to comma and 3 maps to ઘ).  They are handled by the older, more
# conservative numeric-boundary logic below.
STRONG_NUMERIC_GLYPHS = set("!@#$%^&*()_")


def _is_unambiguous_numeric_char(ch: str) -> bool:
    return ch in STRONG_NUMERIC_GLYPHS


def _ambiguous_char_is_numeric(
    text: str,
    position: int,
    context_before: str = "",
    context_after: str = "",
) -> bool:
    """Return True only when an ambiguous Z/5 is inside numeric context.

    The important distinction is:

        ZF  -> રા       (letter ર + aa matra)
        5F  -> પા       (letter પ + aa matra)

        #Zq_5 -> ૩૨/૦૫  (numeric expression)
        Z__5  -> ૨૦૦૫    (numeric expression)

    A standalone Z or 5 remains unchanged because the source encoding
    itself cannot tell us whether the author intended the letter or digit.
    """
    combined = context_before + text + context_after
    offset = len(context_before)
    position = offset + position
    text = combined

    ch = text[position]
    if ch not in AMBIGUOUS_NUMERIC_MAP:
        return False

    # A vowel sign/matra immediately following the ambiguous glyph is strong
    # evidence that it is the Gujarati consonant (ર or પ), not a digit.
    if position + 1 < len(text) and text[position + 1] in {
        "F", "[", "{", "]", "}", "l", "M",
    }:
        return False

    # Walk across one contiguous numeric expression. Do not cross whitespace
    # or unrelated letters.
    left = position
    while left > 0 and text[left - 1] in NUMERIC_EXPRESSION_CHARS:
        left -= 1

    right = position + 1
    while right < len(text) and text[right] in NUMERIC_EXPRESSION_CHARS:
        right += 1

    token = text[left:right]

    # Require at least one unambiguous numeric source glyph. This prevents
    # ordinary words such as 5Z from being guessed as numbers.
    if not any(_is_unambiguous_numeric_char(c) for c in token):
        return False

    # A separator must participate in the expression when the ambiguous
    # glyph is not directly adjacent to an unambiguous digit. This covers
    # dates such as Zq_5 and dates containing a stray backslash such as
    # Z5q\_5qZ#.
    if any(c in NUMERIC_SEPARATORS for c in token):
        return True

    # Plain runs such as Z__5 or 5__Z are numeric because the unambiguous
    # underscore/other numeric glyph is directly part of the same run.
    return True


def _backslash_is_numeric_noise(
    text: str,
    position: int,
    context_before: str = "",
    context_after: str = "",
) -> bool:
    """Return True for a stray backslash embedded in a numeric expression."""
    combined = context_before + text + context_after
    offset = len(context_before)
    position = offset + position
    text = combined

    if position < 0 or position >= len(text) or text[position] != "\\":
        return False

    left = position
    while left > 0 and text[left - 1] in NUMERIC_EXPRESSION_CHARS:
        left -= 1
    right = position + 1
    while right < len(text) and text[right] in NUMERIC_EXPRESSION_CHARS:
        right += 1
    token = text[left:right]

    return (
        any(c in NUMERIC_SEPARATORS for c in token)
        and any(_is_unambiguous_numeric_char(c) for c in token)
        and any(c in AMBIGUOUS_NUMERIC_MAP for c in token)
    )


def _numeric_context_value(
    text: str,
    position: int,
    context_before: str = "",
    context_after: str = "",
) -> str | None:

    combined = context_before + text + context_after
    offset = len(context_before)
    position = offset + position
    text = combined

    ch = text[position]

    # Ambiguous legacy glyphs need contextual interpretation.
    if ch in AMBIGUOUS_NUMERIC_MAP:
        if _ambiguous_char_is_numeric(
            text, position, context_before, context_after
        ):
            return AMBIGUOUS_NUMERIC_MAP[ch]
        return None

    if ch not in NUMERIC_CONTEXT_MAP:
        return None

    prev_ch = (
        text[position - 1]
        if position > 0
        else ""
    )

    next_ch = (
        text[position + 1]
        if position + 1 < len(text)
        else ""
    )

    numeric_boundary = {
        "_",
        "P",
        ".",
    }

    if (
        prev_ch in numeric_boundary
        and (
            next_ch in numeric_boundary
            or next_ch in NUMERIC_CONTEXT_MAP
            or next_ch in AMBIGUOUS_NUMERIC_MAP
        )
    ):

        return NUMERIC_CONTEXT_MAP[ch]


    if (
        next_ch in numeric_boundary
        and (
            prev_ch in NUMERIC_CONTEXT_MAP
            or prev_ch in AMBIGUOUS_NUMERIC_MAP
        )
    ):

        return NUMERIC_CONTEXT_MAP[ch]


    return None


# ============================================================
# BACKSLASH / ANUSVARA
# ============================================================

def _should_ignore_backslash(
    text: str,
    position: int,
) -> bool:

    """
    Arun / LMG structural rule.

    In this legacy font:

        \\  ->  ં

    The backslash must not be discarded just because
    a number follows it.
    """

    return False


def _convert_backslash(
    output: list[str],
) -> None:

    """
    Convert Arun backslash to Gujarati anusvara.

        \\ -> ં
    """

    output.append("ં")


# ============================================================
# PUNCTUATION
# ============================================================

def _should_preserve_literal_punctuation(
    text: str,
    position: int,
) -> bool:

    ch = text[position]

    next_ch = (
        text[position + 1]
        if position + 1 < len(text)
        else ""
    )


    # IMPORTANT:
    #
    # ',' is NOT punctuation in Arun.
    #
    # ',' -> લ
    # '4' -> ,
    #

    if ch in ":?":

        if (
            not next_ch
            or next_ch.isspace()
        ):

            return True


    # Parentheses used as normal punctuation.

    if ch == "(":

        closing = text.find(
            ")",
            position + 1,
        )

        if closing != -1:

            between = text[
                position + 1:
                closing
            ]

            if (
                "\n" not in between
                and "\r" not in between
                and len(between) <= 16
            ):

                return True


    if ch == ")":

        if "(" in text[:position]:

            opening = text.rfind(
                "(",
                0,
                position,
            )

            if opening >= 0:

                between = text[
                    opening + 1:
                    position
                ]

                if (
                    "\n" not in between
                    and "\r" not in between
                    and len(between) <= 16
                ):

                    return True


    return False


# ============================================================
# Q / ષ STRUCTURE
# ============================================================

def _q_is_full_sha(
    text: str,
    position: int,
) -> bool:

    """
    Decide whether Q is full ષ or half ષ્.

    Important examples:

        lJX[QF
        ↓
        વિશેષ

        lGNM"QF
        ↓
        નિર્દોષ

        lG,[QFEF.
        ↓
        નિલેષભાઈ

    Q represents full ષ in these structures.

    This is a structural rule, not a word mapping.
    """

    if position + 1 >= len(text):
        return True

    next_ch = text[
        position + 1
    ]


    # Q followed by whitespace/end is full ષ.

    if (
        not next_ch
        or next_ch.isspace()
    ):

        return True


    # Q followed by F and then another legacy glyph.

    if (
        next_ch == "F"
        and position + 2 < len(text)
    ):

        after_f = text[
            position + 2
        ]

        if (
            after_f.isupper()
            or after_f.isdigit()
            or after_f in {
                ",",
                ".",
                "-",
            }
        ):

            return True


    if next_ch in {
        "F",
        "[",
        "{",
        "]",
        "}",
        ",",
        ".",
        "4",
        ";",
        ":",
    }:

        return True


    return False


def _map_q(
    text: str,
    position: int,
) -> str:

    if _q_is_full_sha(
        text,
        position,
    ):

        return "ષ"


    return CHARACTER_MAP.get(
        "Q",
        "ષ્",
    )


# ============================================================
# પક્ષ STRUCTURAL RULE
# ============================================================

def _is_paksha_sequence(
    text: str,
    position: int,
) -> bool:

    """
    Detect the Arun / LMG sequence:

        51F

    This represents:

        પ + ક્ + ષ

    which gives:

        પક્ષ

    IMPORTANT:

    We do NOT add "પક્ષ" or any other word to the mapping.

    This is a character-level structural rule.

    Why this is necessary:

        1F

    normally represents the ક્ષ structure.

    But when it occurs immediately after:

        5

    the intended Gujarati construction is:

        પ + ક્ + ષ

        પક્ષ

    Therefore 51F must be handled before normal 1F
    processing.
    """

    if position < 0:
        return False

    if position + 2 >= len(text):
        return False

    return (
        text[position] == "5"
        and text[position + 1] == "1"
        and text[position + 2] == "F"
    )


def _convert_paksha_sequence(
    output: list[str],
) -> None:

    """
    Convert:

        51F

    to:

        પક્ષ

    This is deliberately kept as a structural conversion
    instead of adding individual words to arun_mapping.py.
    """

    output.append(
        "પક્ષ"
    )


# ============================================================
# LEGACY UNIT DECODER
# ============================================================

def _decode_one_legacy_unit(
    text: str,
    position: int,
) -> tuple[str, int]:

    # Longest known structural sequence first.

    for (
        legacy_sequence,
        unicode_sequence,
    ) in SORTED_SEQUENCES:

        if text.startswith(
            legacy_sequence,
            position,
        ):

            return (
                unicode_sequence,
                len(legacy_sequence),
            )


    ch = text[position]


    if ch == "Q":

        return (
            _map_q(
                text,
                position,
            ),
            1,
        )


    mapped = CHARACTER_MAP.get(
        ch
    )


    return (
        mapped
        if mapped is not None
        else ch,
        1,
    )


# ============================================================
# I-MATRA STRUCTURE
# ============================================================

def _convert_prebase_i(
    text: str,
    position: int,
) -> tuple[str, int] | None:

    if position >= len(text):
        return None


    value, consumed = (
        _decode_one_legacy_unit(
            text,
            position,
        )
    )


    if not value:
        return None


    if not _is_gujarati_base(
        value[0]
    ):

        return None


    position += consumed


    pieces = [
        value
    ]


    # Continue through conjunct controls.

    while (
        position < len(text)
        and text[position]
        in CLUSTER_CONTROLS
    ):

        control_value, control_consumed = (
            _decode_one_legacy_unit(
                text,
                position,
            )
        )

        pieces.append(
            control_value
        )

        position += (
            control_consumed
        )


    pieces.append(
        "િ"
    )


    return (
        "".join(pieces),
        position,
    )


# ============================================================
# R-FORM / REPH
# ============================================================

def _insert_rform_before_last_base(
    text: str,
) -> str:

    if not text:
        return "ર્"


    for index in range(
        len(text) - 1,
        -1,
        -1,
    ):

        if _is_gujarati_base(
            text[index]
        ):

            return (
                text[:index]
                + "ર્"
                + text[index:]
            )


    return (
        text
        + "ર્"
    )


# ============================================================
# VOWEL CONFLICT HANDLING
# ============================================================

def _append_aa(
    output: list[str],
) -> None:

    current = "".join(
        output
    )


    # Independent આ.

    if current.endswith("અ"):

        output[:] = [
            _replace_last_character(
                current,
                "આ",
            )
        ]

        return


    # Do not create duplicate aa marks.

    if current.endswith("ા"):
        return


    output.append(
        "ા"
    )


def _append_e(
    output: list[str],
) -> None:

    current = "".join(
        output
    )


    # Independent એ.

    if current.endswith("અ"):

        output[:] = [
            _replace_last_character(
                current,
                "એ",
            )
        ]

        return


    # Existing vowel already supplies the vowel.

    if current.endswith(
        (
            "ે",
            "ૈ",
            "ો",
            "ૌ",
        )
    ):

        return


    output.append(
        "ે"
    )


def _append_o(
    output: list[str],
) -> None:

    current = "".join(
        output
    )


    # Independent ઓ.

    if current.endswith("અ"):

        output[:] = [
            _replace_last_character(
                current,
                "ઓ",
            )
        ]

        return


    # Existing o / au.

    if current.endswith(
        (
            "ો",
            "ૌ",
        )
    ):

        return


    # Replace e / ai with o.

    if current.endswith(
        (
            "ે",
            "ૈ",
        )
    ):

        output[:] = [
            current[:-1]
            + "ો"
        ]

        return


    output.append(
        "ો"
    )


def _append_ai(
    output: list[str],
) -> None:

    current = "".join(
        output
    )


    if current.endswith("અ"):

        output[:] = [
            _replace_last_character(
                current,
                "ઐ",
            )
        ]

        return


    if current.endswith("આ"):

        output[:] = [
            _replace_last_character(
                current,
                "ઔ"
            )
        ]

        return


    if current.endswith(
        (
            "ૈ",
            "ૌ",
        )
    ):

        return


    output.append(
        "ૈ"
    )


# ============================================================
# Q + F STRUCTURAL RULE
# ============================================================

def _should_suppress_aa_after_q(
    text: str,
    position: int,
) -> bool:

    """
    Handle:

        QF

    where Q represents full ષ.

    Examples:

        lJX[QF
        ↓
        વિશેષ

        lGNM"QF
        ↓
        નિર્દોષ

        lG,[QFEF.
        ↓
        નિલેષભાઈ

    F is structural here and must not create ષા.
    """

    if position <= 0:
        return False


    if text[position - 1] != "Q":
        return False


    # QF at end of text.

    if position + 1 >= len(text):
        return True


    next_ch = text[
        position + 1
    ]


    # QF followed by whitespace.

    if next_ch.isspace():
        return True


    # QF followed by punctuation.

    if next_ch in {
        ",",
        ".",
        "4",
        ";",
        ":",
        ")",
        "(",
    }:

        return True


    # QF followed by another legacy character.

    if (
        next_ch.isupper()
        or next_ch.isdigit()
    ):

        return True


    return False


# ============================================================
# STANDALONE 1F / ક્ષ STRUCTURAL RULE
# ============================================================

def _should_suppress_f_after_standalone_ksha(
    text: str,
    position: int,
) -> bool:

    """
    Handle standalone:

        1F

    as:

        ક્ષ

    while keeping:

        1FF

    as:

        ક્ષા

    This is a structural rule.

    IMPORTANT:

        51F is handled separately as પક્ષ,
        so this rule does not interfere with પક્ષ.
    """

    if position <= 0:
        return False


    if text[position] != "F":
        return False


    # F must immediately follow 1.

    if text[position - 1] != "1":
        return False


    # 51F is પક્ષ and is handled by the dedicated
    # પક્ષ structural rule.

    if (
        position >= 2
        and text[position - 2] == "5"
    ):

        return False


    # If another F follows, this is 1FF = ક્ષા.

    if position + 1 < len(text):

        if text[position + 1] == "F":
            return False


    # End of text:

        # 1F = ક્ષ

    if position + 1 >= len(text):
        return True


    next_ch = text[
        position + 1
    ]


    # Before whitespace:

    if next_ch.isspace():
        return True


    # Before punctuation:

    if next_ch in {
        ",",
        ".",
        "4",
        ";",
        ":",
        ")",
        "(",
    }:

        return True


    return False


# ============================================================
# KSH / ક્ષ STRUCTURAL RULE
# ============================================================

def _should_suppress_f_in_ksha_sequence(
    text: str,
    position: int,
) -> bool:

    """
    Handle:

        1FGF

    Example:

        OlZIFN51FGF

        ↓

        ફરિયાદપક્ષના

    This is a character-sequence rule.
    """

    if position <= 0:
        return False


    if text[position] != "F":
        return False


    if text[position - 1] != "1":
        return False


    if position + 1 >= len(text):
        return False


    if text[position + 1] != "G":
        return False


    if position + 2 >= len(text):
        return False


    if text[position + 2] != "F":
        return False


    return True


# ============================================================
# DUPLICATE F AFTER KSH
# ============================================================

def _should_suppress_duplicate_f_after_ksha(
    text: str,
    position: int,
) -> bool:

    """
    Handle:

        1FF

    The second F is structural/duplicate.

    Therefore:

        1FF
        ↓
        ક્ષા
    """

    if position < 2:
        return False


    if text[position] != "F":
        return False


    if text[position - 1] != "F":
        return False


    if text[position - 2] != "1":
        return False


    return True


# ============================================================
# MAIN CONVERTER
# ============================================================

def convert_arun_text(
    text: str,
    context_before: str = "",
    context_after: str = "",
) -> str:

    if not isinstance(
        text,
        str,
    ):

        raise TypeError(
            "text must be a string"
        )


    if not text:
        return ""


    output: list[str] = []

    position = 0


    while position < len(text):

        # ====================================================
        # PAKSHA / પક્ષ STRUCTURAL SEQUENCE
        # ====================================================
        #
        # MUST happen before normal character mapping.
        #
        # 51F -> પક્ષ
        #
        # This prevents 1F from being interpreted as generic
        # ક્ષ in this specific structural context.
        # ====================================================

        if _is_paksha_sequence(
            text,
            position,
        ):

            _convert_paksha_sequence(
                output
            )

            position += 3

            continue


        # ====================================================
        # LONGEST STRUCTURAL SEQUENCES
        # ====================================================

        matched = None


        for (
            legacy_sequence,
            unicode_sequence,
        ) in SORTED_SEQUENCES:

            if text.startswith(
                legacy_sequence,
                position,
            ):

                matched = (
                    legacy_sequence,
                    unicode_sequence,
                )

                break


        if matched is not None:

            (
                legacy_sequence,
                unicode_sequence,
            ) = matched


            output.append(
                unicode_sequence
            )


            position += len(
                legacy_sequence
            )


            continue


        ch = text[position]


        # ====================================================
        # LITERAL PUNCTUATION
        # ====================================================

        if _should_preserve_literal_punctuation(
            text,
            position,
        ):

            output.append(
                ch
            )


            position += 1


            continue


        # ====================================================
        # NUMBERS
        # ====================================================

        numeric_value = (
            _numeric_context_value(
                text,
                position,
                context_before,
                context_after,
            )
        )


        if numeric_value is not None:

            output.append(
                numeric_value
            )


            position += 1


            continue


        # ====================================================
        # BACKSLASH / ANUSVARA
        # ====================================================

        if ch == "\\":

            if _backslash_is_numeric_noise(
                text, position, context_before, context_after
            ):
                position += 1
                continue

            if not _should_ignore_backslash(
                text,
                position,
            ):

                _convert_backslash(
                    output
                )


            position += 1


            continue


        # ====================================================
        # PRE-BASE I
        # ====================================================

        if ch == I_MATRA_INPUT:

            result = (
                _convert_prebase_i(
                    text,
                    position + 1,
                )
            )


            if result is not None:

                converted, new_position = (
                    result
                )


                output.append(
                    converted
                )


                position = (
                    new_position
                )


                continue


            output.append(
                "િ"
            )


            position += 1


            continue


        # ====================================================
        # R-FORM
        # ====================================================

        if ch == RFORM_INPUT:

            current = "".join(
                output
            )


            output[:] = [
                _insert_rform_before_last_base(
                    current
                )
            ]


            position += 1


            continue


        # ====================================================
        # AA / F
        # ====================================================

        if ch == AA_INPUT:

            # ------------------------------------------------
            # QF suppression
            # ------------------------------------------------

            if _should_suppress_aa_after_q(
                text,
                position,
            ):

                position += 1

                continue


            # ------------------------------------------------
            # Standalone 1F = ક્ષ
            # ------------------------------------------------

            if _should_suppress_f_after_standalone_ksha(
                text,
                position,
            ):

                position += 1

                continue


            # ------------------------------------------------
            # 1FGF structural suppression
            # ------------------------------------------------

            if _should_suppress_f_in_ksha_sequence(
                text,
                position,
            ):

                position += 1

                continue


            # ------------------------------------------------
            # Duplicate F in 1FF
            # ------------------------------------------------

            if _should_suppress_duplicate_f_after_ksha(
                text,
                position,
            ):

                position += 1

                continue


            _append_aa(
                output
            )


            position += 1


            continue


        # ====================================================
        # E
        # ====================================================

        if ch == E_INPUT:

            _append_e(
                output
            )


            position += 1


            continue


        # ====================================================
        # O
        # ====================================================

        if ch == O_INPUT:

            _append_o(
                output
            )


            position += 1


            continue


        # ====================================================
        # AI / AU
        # ====================================================

        if ch == AI_INPUT:

            _append_ai(
                output
            )


            position += 1


            continue


        # ====================================================
        # Q
        # ====================================================

        if ch == "Q":

            output.append(
                _map_q(
                    text,
                    position,
                )
            )


            position += 1


            continue


        # ====================================================
        # NORMAL CHARACTER
        # ====================================================

        mapped = CHARACTER_MAP.get(
            ch
        )


        output.append(
            mapped
            if mapped is not None
            else ch
        )


        position += 1


    # ========================================================
    # FINAL NORMALIZATION
    # ========================================================

    result = "".join(
        output
    )


    result = _normalize_arun_marks(
        result
    )


    return normalize_gujarati(
        result
    )


# ============================================================
# PUBLIC API
# ============================================================

def convert_text(
    text: str,
) -> str:

    return convert_arun_text(
        text
    )


def convert_lines(
    lines: list[str],
) -> list[str]:

    if not isinstance(
        lines,
        list,
    ):

        raise TypeError(
            "lines must be a list"
        )


    return [
        convert_arun_text(
            line
        )
        for line in lines
    ]


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    tests = [

        # ----------------------------------------------------
        # Basic mapping
        # ----------------------------------------------------

        ("A", "બ"),
        ("S", "ક"),
        ("G", "ન"),
        ("5", "પ"),
        ("1", "ક્ષ"),

        # ----------------------------------------------------
        # Ambiguous Z / 5: letter + matra must stay letters
        # ----------------------------------------------------

        ("ZF", "રા"),
        ("Z[", "રે"),
        ("Z{", "રૈ"),
        ("Z]", "રુ"),
        ("Z}", "રૂ"),
        ("Zl", "રિ"),
        ("ZM", "રો"),

        ("5F", "પા"),
        ("5[", "પે"),
        ("5{", "પૈ"),
        ("5]", "પુ"),
        ("5}", "પૂ"),
        ("5l", "પિ"),
        ("5M", "પો"),

        # AA + AI typing-order -> AU matra.
        ("DF{lBS", "મૌખિક"),
        ("RF{CF6", "ચૌહાણ"),
        ("માૈખિક", "મૌખિક"),
        ("ચૈાહાણ", "ચૌહાણ"),

        ("-", "ઢ"),
        (".", "ઈ"),
        (",", "લ"),
        ("4", ","),


        # ----------------------------------------------------
        # Vowels
        # ----------------------------------------------------

        ("VF", "આ"),
        ("V[", "એ"),
        ("VM", "ઓ"),
        ("V{", "ઐ"),


        # ----------------------------------------------------
        # Existing important structural cases
        # ----------------------------------------------------

        (
            "lS|DLG,",
            "ક્રિમીનલ",
        ),

        (
            'SIF"',
            "કર્યા",
        ),

        (
            "lG,[QFEF.",
            "નિલેષભાઈ",
        ),

        (
            "lJX[Q",
            "વિશેષ",
        ),

        (
            "NFB,",
            "દાખલ",
        ),

        (
            "V[0LxG,",
            "એડીશ્નલ",
        ),

        (
            "RFH\"XL8 NFB, YIF TFZLB",
            "ચાર્જશીટ દાખલ થયા તારીખ",
        ),


        # ----------------------------------------------------
        # Numeric context for ambiguous Z / 5
        # ----------------------------------------------------

        ("#Zq_*", "૩૨/૦૭"),
        ("&Zq_5", "૬૨/૦૫"),
        ("Z__5", "૨૦૦૫"),
        ("TFPZZv)vZ__5", "તા.૨૨-૯-૨૦૦૫"),
        ("Z5q\\_5qZ#", "૨૫/૦૫/૨૩"),
        ("TFP Z5q\\_5qZ#", "તા. ૨૫/૦૫/૨૩"),
        ("DFS\" (q5 YL ZH]", "માર્ક ૮/૫ થી રજુ"),
        ("EFJGUZ4", "ભાવનગર,"),

        # ----------------------------------------------------
        # Typist-order / malformed Gujarati mark handling
        # ----------------------------------------------------

        ("UF?F[F", "ગાળો"),
        ("NZdFIFG", "દરમ્યાન"),
        ("V [", "એ"),
        ("U F [", "ગો"),

        # Existing letter + matra behavior must remain unchanged.
        ("ZF", "રા"),
        ("5F", "પા"),

        # ----------------------------------------------------
        # ફરિયાદપક્ષ
        # ----------------------------------------------------

        (
            "OlZIFN51F",
            "ફરિયાદપક્ષ",
        ),

        (
            "OlZIFN51FGF",
            "ફરિયાદપક્ષના",
        ),


        # ----------------------------------------------------
        # પક્ષ STRUCTURAL TESTS
        # ----------------------------------------------------

        (
            "51F",
            "પક્ષ",
        ),

        (
            "51FS",
            "પક્ષક",
        ),

        (
            "51FGF",
            "પક્ષના",
        ),

        (
            "51FSFZM",
            "પક્ષકારો",
        ),


        # ----------------------------------------------------
        # ક્ષ / ક્ષા
        # ----------------------------------------------------

        (
            "1F",
            "ક્ષ",
        ),

        (
            "1FF",
            "ક્ષા",
        ),

        (
            "5ZL1FF",
            "પરીક્ષા",
        ),


        # ----------------------------------------------------
        # ષ WORDS
        # ----------------------------------------------------

        (
            "lJX[QF",
            "વિશેષ",
        ),

        (
            "lGNM\"QF",
            "નિર્દોષ",
        ),


        # ----------------------------------------------------
        # Structural vowel protection
        # ----------------------------------------------------

        (
            "0M[",
            "ડો",
        ),

        (
            "0M[ DF\\UL,F,",
            "ડો માંગીલાલ",
        ),


        # ----------------------------------------------------
        # BACKSLASH / ANUSVARA
        # ----------------------------------------------------

        (
            "\\",
            "ં",
        ),

        (
            "DF\\0JLIF",
            "માંડવીયા",
        ),

        (
            "VNF,TDF\\4D]P T/FHFP",
            "અદાલતમાં,મુ. તળાજા.",
        ),


        # ----------------------------------------------------
        # Unknown characters preserved
        # ----------------------------------------------------

        (
            "😀",
            "😀",
        ),
    ]


    passed = 0
    failed = 0


    print("=" * 70)
    print(
        "ARUN / LMG STRUCTURAL TEST"
    )
    print("=" * 70)


    for source, expected in tests:

        try:

            actual = convert_arun_text(
                source
            )

        except Exception as exc:

            print(
                f"[FAIL] {source!r}"
            )

            print(
                f"       ERROR: {exc}"
            )

            failed += 1

            continue


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

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print("=" * 70)


    if failed:

        raise SystemExit(1)


    print(
        "ALL ARUN / LMG TESTS PASSED"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()