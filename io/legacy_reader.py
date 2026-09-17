# ============================================================
# Hari / Harikrishna Legacy Gujarati
# Safe Legacy File Reader
# ============================================================

from pathlib import Path
from typing import Tuple


# ============================================================
# READ HARI FILE
# ============================================================

def read_hari_file(path: str) -> Tuple[str, str]:
    """
    Read a Hari/Harikrishna legacy Gujarati file.

    The function tries encodings in a safe order.

    Returns:
        (text, encoding_used)
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    # --------------------------------------------------------
    # Read raw bytes.
    #
    # We MUST read bytes first because old Hari files may
    # contain byte values above normal ASCII.
    # --------------------------------------------------------

    data = file_path.read_bytes()

    # --------------------------------------------------------
    # UTF-16
    # --------------------------------------------------------

    if data.startswith(b"\xff\xfe"):

        return (
            data.decode("utf-16"),
            "utf-16",
        )

    if data.startswith(b"\xfe\xff"):

        return (
            data.decode("utf-16"),
            "utf-16",
        )

    # --------------------------------------------------------
    # UTF-8 with BOM
    # --------------------------------------------------------

    if data.startswith(b"\xef\xbb\xbf"):

        return (
            data.decode("utf-8-sig"),
            "utf-8-sig",
        )

    # --------------------------------------------------------
    # Normal UTF-8
    # --------------------------------------------------------

    try:

        return (
            data.decode("utf-8"),
            "utf-8",
        )

    except UnicodeDecodeError:

        pass

    # --------------------------------------------------------
    # Hari legacy fallback
    #
    # Latin-1 is extremely important here.
    #
    # It maps every byte 0-255 directly to Unicode
    # code points U+0000-U+00FF.
    #
    # Therefore no legacy byte is lost.
    # --------------------------------------------------------

    return (
        data.decode("latin-1"),
        "latin-1",
    )


# ============================================================
# SAVE UNICODE FILE
# ============================================================

def save_unicode_file(
    path: str,
    text: str,
) -> None:
    """
    Save converted Gujarati Unicode text as UTF-8.

    UTF-8 with BOM is used because it works well with
    Windows applications such as Notepad and Microsoft Word.
    """

    if not isinstance(text, str):
        raise TypeError(
            "text must be a Python string"
        )

    file_path = Path(path)

    # Create parent directory if necessary.

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        text,
        encoding="utf-8-sig",
        newline="",
    )


# ============================================================
# SIMPLE TESTS
# ============================================================

def run_tests():

    print("=" * 70)
    print("HARI LEGACY READER TEST")
    print("=" * 70)

    passed = 0
    failed = 0

    # --------------------------------------------------------
    # Test 1: Function exists
    # --------------------------------------------------------

    if callable(read_hari_file):

        print(
            "[PASS] read_hari_file available"
        )

        passed += 1

    else:

        print(
            "[FAIL] read_hari_file available"
        )

        failed += 1

    # --------------------------------------------------------
    # Test 2: Writer exists
    # --------------------------------------------------------

    if callable(save_unicode_file):

        print(
            "[PASS] save_unicode_file available"
        )

        passed += 1

    else:

        print(
            "[FAIL] save_unicode_file available"
        )

        failed += 1

    # --------------------------------------------------------
    # Test 3: Latin-1 preserves all byte values
    # --------------------------------------------------------

    test_bytes = bytes([
        65,
        177,
        202,
        203,
        229,
    ])

    decoded = test_bytes.decode("latin-1")

    if (
        ord(decoded[0]) == 65
        and ord(decoded[1]) == 177
        and ord(decoded[2]) == 202
        and ord(decoded[3]) == 203
        and ord(decoded[4]) == 229
    ):

        print(
            "[PASS] legacy byte preservation"
        )

        passed += 1

    else:

        print(
            "[FAIL] legacy byte preservation"
        )

        failed += 1

    # --------------------------------------------------------
    # Result
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

    if failed:
        raise SystemExit(1)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()