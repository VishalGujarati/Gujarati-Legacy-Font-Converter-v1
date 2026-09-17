# ============================================================
# Hari / Harikrishna Legacy Gujarati
# Unicode File Writer
# ============================================================

from pathlib import Path
from typing import Optional


# ============================================================
# SAVE UNICODE FILE
# ============================================================

def save_unicode_file(
    path: str,
    text: str,
) -> None:
    """
    Save Unicode Gujarati text as UTF-8 with BOM.

    UTF-8 with BOM gives good compatibility with
    Windows applications such as Notepad and Excel.
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
# ALIAS
# ============================================================

write_unicode_file = save_unicode_file
write_file = save_unicode_file
save_file = save_unicode_file


# ============================================================
# READ-BACK VERIFICATION
# ============================================================

def verify_unicode_file(
    path: str,
) -> bool:
    """
    Verify that a saved file can be read back as UTF-8.
    """

    file_path = Path(path)

    if not file_path.exists():
        return False

    try:

        file_path.read_text(
            encoding="utf-8-sig"
        )

        return True

    except (UnicodeDecodeError, OSError):

        return False


# ============================================================
# TEST
# ============================================================

def run_tests():

    print("=" * 70)
    print("UNICODE FILE WRITER TEST")
    print("=" * 70)

    passed = 0
    failed = 0

    # --------------------------------------------------------
    # Test 1
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
    # Test 2
    # --------------------------------------------------------

    if callable(write_unicode_file):

        print(
            "[PASS] write_unicode_file available"
        )

        passed += 1

    else:

        print(
            "[FAIL] write_unicode_file available"
        )

        failed += 1

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    if callable(write_file):

        print(
            "[PASS] write_file available"
        )

        passed += 1

    else:

        print(
            "[FAIL] write_file available"
        )

        failed += 1

    # --------------------------------------------------------
    # Test 4
    #
    # Use a temporary file.
    # --------------------------------------------------------

    test_path = (
        Path(__file__).resolve().parent
        / "__unicode_writer_test__.txt"
    )

    test_text = (
        "ગુજરાતી પરીક્ષણ\n"
        "આરોપી સાથે પોતાની મરજીથી"
    )

    try:

        save_unicode_file(
            str(test_path),
            test_text,
        )

        if verify_unicode_file(
            str(test_path)
        ):

            print(
                "[PASS] Unicode write/read verification"
            )

            passed += 1

        else:

            print(
                "[FAIL] Unicode write/read verification"
            )

            failed += 1

    finally:

        # Remove test file.
        if test_path.exists():

            test_path.unlink()

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