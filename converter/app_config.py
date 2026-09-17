from __future__ import annotations

# ============================================================
# Hari / Harikrishna Legacy Gujarati -> Unicode
# Application Configuration
# ============================================================

from pathlib import Path


# ============================================================
# APPLICATION IDENTITY
# ============================================================

APP_NAME = "Gujarati Legacy Font Converter"

APP_VERSION = "1.0.1"

APP_AUTHOR = "VishalGujarati"

APP_DESCRIPTION = (
    "Free offline Gujarati legacy-font to Unicode converter "
    "for Hari/Harikrishna and LMG Arun/Lohit BKMAN."
)


# ============================================================
# SUPPORTED FILES
# ============================================================

SUPPORTED_EXTENSIONS = (
    ".txt",
    ".text",
    ".docx",
    ".odt",
)


# ============================================================
# ENCODINGS
# ============================================================

LEGACY_ENCODING = "latin-1"

UNICODE_ENCODING = "utf-8-sig"

INTERNAL_ENCODING = "utf-8"


# ============================================================
# OUTPUT SETTINGS
# ============================================================

DEFAULT_OUTPUT_DIRECTORY_NAME = (
    "Unicode_Output"
)

DEFAULT_OUTPUT_SUFFIX = "_unicode"


# ============================================================
# SAFETY SETTINGS
# ============================================================

DEFAULT_OVERWRITE = False

PRESERVE_SOURCE_FILES = True

CREATE_OUTPUT_DIRECTORY = True


# ============================================================
# REPORT SETTINGS
# ============================================================

REPORT_DIRECTORY_NAME = "Reports"

JSON_REPORT_EXTENSION = ".json"

TEXT_REPORT_EXTENSION = ".txt"


# ============================================================
# SESSION SETTINGS
# ============================================================

SESSION_DIRECTORY_NAME = "Sessions"

SESSION_FILE_EXTENSION = ".json"


# ============================================================
# APPLICATION DIRECTORY HELPERS
# ============================================================

def get_default_output_directory(
    source_directory: str | Path,
) -> Path:
    """
    Return the default Unicode output directory
    for a source directory.
    """

    source = Path(source_directory)

    return (
        source
        / DEFAULT_OUTPUT_DIRECTORY_NAME
    )


def get_report_directory(
    base_directory: str | Path,
) -> Path:
    """
    Return the directory used for reports.
    """

    base = Path(base_directory)

    return (
        base
        / REPORT_DIRECTORY_NAME
    )


def get_session_directory(
    base_directory: str | Path,
) -> Path:
    """
    Return the directory used for sessions.
    """

    base = Path(base_directory)

    return (
        base
        / SESSION_DIRECTORY_NAME
    )


# ============================================================
# OUTPUT FILE HELPER
# ============================================================

def make_output_filename(
    source_filename: str,
) -> str:
    """
    Create the default Unicode output filename.

    Example:

        order.txt
        ->
        order_unicode.txt
    """

    source = Path(
        source_filename
    )

    return (
        source.stem
        + DEFAULT_OUTPUT_SUFFIX
        + source.suffix
    )


# ============================================================
# CONFIGURATION DICTIONARY
# ============================================================

def get_config() -> dict:
    """
    Return the complete application configuration
    as a simple dictionary.

    Useful for the GUI, diagnostics, logging,
    and future packaging.
    """

    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "app_author": APP_AUTHOR,
        "app_description": APP_DESCRIPTION,

        "supported_extensions":
            list(SUPPORTED_EXTENSIONS),

        "legacy_encoding":
            LEGACY_ENCODING,

        "unicode_encoding":
            UNICODE_ENCODING,

        "internal_encoding":
            INTERNAL_ENCODING,

        "default_output_directory":
            DEFAULT_OUTPUT_DIRECTORY_NAME,

        "default_output_suffix":
            DEFAULT_OUTPUT_SUFFIX,

        "default_overwrite":
            DEFAULT_OVERWRITE,

        "preserve_source_files":
            PRESERVE_SOURCE_FILES,

        "create_output_directory":
            CREATE_OUTPUT_DIRECTORY,

        "report_directory":
            REPORT_DIRECTORY_NAME,

        "session_directory":
            SESSION_DIRECTORY_NAME,
    }


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_config() -> list[str]:
    """
    Validate application configuration.

    Returns an empty list when everything is valid.
    """

    errors = []

    if not APP_NAME.strip():

        errors.append(
            "APP_NAME cannot be empty."
        )

    if not APP_VERSION.strip():

        errors.append(
            "APP_VERSION cannot be empty."
        )

    if not SUPPORTED_EXTENSIONS:

        errors.append(
            "At least one file extension "
            "must be supported."
        )

    for extension in SUPPORTED_EXTENSIONS:

        if not extension.startswith("."):

            errors.append(
                f"Invalid file extension: "
                f"{extension}"
            )

    if not LEGACY_ENCODING:

        errors.append(
            "LEGACY_ENCODING cannot be empty."
        )

    if not UNICODE_ENCODING:

        errors.append(
            "UNICODE_ENCODING cannot be empty."
        )

    if not DEFAULT_OUTPUT_DIRECTORY_NAME.strip():

        errors.append(
            "Default output directory "
            "cannot be empty."
        )

    if not DEFAULT_OUTPUT_SUFFIX:

        errors.append(
            "Default output suffix "
            "cannot be empty."
        )

    return errors


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    print("=" * 70)
    print(
        "HARI APPLICATION CONFIGURATION TEST"
    )
    print("=" * 70)

    passed = 0
    failed = 0

    def check(
        name,
        actual,
        expected,
    ):

        nonlocal passed
        nonlocal failed

        if actual == expected:

            print(
                f"[PASS] {name}"
            )

            passed += 1

        else:

            print(
                f"[FAIL] {name}"
            )

            print(
                f"       Expected: "
                f"{expected!r}"
            )

            print(
                f"       Actual:   "
                f"{actual!r}"
            )

            failed += 1

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    check(
        "application name",
        APP_NAME,
        "Gujarati Legacy Font Converter",
    )

    check(
        "application version",
        APP_VERSION,
        "1.0.1",
    )

    # --------------------------------------------------------
    # Encodings
    # --------------------------------------------------------

    check(
        "legacy encoding",
        LEGACY_ENCODING,
        "latin-1",
    )

    check(
        "Unicode encoding",
        UNICODE_ENCODING,
        "utf-8-sig",
    )

    # --------------------------------------------------------
    # File extensions
    # --------------------------------------------------------

    check(
        "txt supported",
        ".txt" in SUPPORTED_EXTENSIONS,
        True,
    )

    check(
        "text supported",
        ".text" in SUPPORTED_EXTENSIONS,
        True,
    )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    output_directory = (
        get_default_output_directory(
            Path("C:/Test/Input")
        )
    )

    check(
        "default output directory",
        output_directory.name,
        DEFAULT_OUTPUT_DIRECTORY_NAME,
    )

    # --------------------------------------------------------
    # Report directory
    # --------------------------------------------------------

    report_directory = (
        get_report_directory(
            Path("C:/Test")
        )
    )

    check(
        "report directory",
        report_directory.name,
        REPORT_DIRECTORY_NAME,
    )

    # --------------------------------------------------------
    # Session directory
    # --------------------------------------------------------

    session_directory = (
        get_session_directory(
            Path("C:/Test")
        )
    )

    check(
        "session directory",
        session_directory.name,
        SESSION_DIRECTORY_NAME,
    )

    # --------------------------------------------------------
    # Output filename
    # --------------------------------------------------------

    check(
        "output filename",
        make_output_filename(
            "sample.txt"
        ),
        "sample_unicode.txt",
    )

    check(
        "output filename with spaces",
        make_output_filename(
            "Court Order 01.txt"
        ),
        "Court Order 01_unicode.txt",
    )

    # --------------------------------------------------------
    # Configuration dictionary
    # --------------------------------------------------------

    config = get_config()

    check(
        "configuration dictionary",
        isinstance(
            config,
            dict,
        ),
        True,
    )

    check(
        "configuration application name",
        config["app_name"],
        APP_NAME,
    )

    check(
        "configuration version",
        config["app_version"],
        APP_VERSION,
    )

    # --------------------------------------------------------
    # Configuration validation
    # --------------------------------------------------------

    errors = validate_config()

    check(
        "configuration validation",
        errors,
        [],
    )

    # --------------------------------------------------------
    # Safety settings
    # --------------------------------------------------------

    check(
        "overwrite disabled by default",
        DEFAULT_OVERWRITE,
        False,
    )

    check(
        "source preservation enabled",
        PRESERVE_SOURCE_FILES,
        True,
    )

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