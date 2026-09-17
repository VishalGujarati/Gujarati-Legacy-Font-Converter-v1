# ============================================================
# Hari / Harikrishna Legacy Gujarati Converter
# Batch Conversion Engine
#
# Author: Vishal Chauhan
#
# PURPOSE
# -------
# Safely convert multiple Hari/Harikrishna legacy text files
# into Unicode Gujarati files.
#
# This module contains NO Gujarati word dictionary.
#
# Architecture:
#
#     Legacy files
#          ↓
#     legacy_reader
#          ↓
#     legacy_engine
#          ↓
#     conversion validation
#          ↓
#     Unicode writer
#          ↓
#     Converted files + report
#
# DESIGN PRINCIPLES
# -----------------
# 1. Never silently destroy source data.
# 2. Never overwrite source files by default.
# 3. Preserve line boundaries.
# 4. Preserve unknown characters.
# 5. Continue processing if one file fails.
# 6. Return a complete report.
# 7. Keep GUI separate from conversion logic.
# ============================================================

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ============================================================
# IMPORTS
# ============================================================

try:
    from .legacy_engine import convert
    from .conversion_validator import validate_conversion
except ImportError:
    from legacy_engine import convert
    from conversion_validator import validate_conversion


# ============================================================
# RESULT CLASSES
# ============================================================

@dataclass
class BatchFileResult:
    """
    Result for one converted file.
    """

    source_path: str
    output_path: Optional[str] = None

    success: bool = False

    input_characters: int = 0
    output_characters: int = 0

    gujarati_characters: int = 0

    unresolved_count: int = 0

    confidence: str = "UNKNOWN"

    warnings: List[str] = field(
        default_factory=list
    )

    error: Optional[str] = None


@dataclass
class BatchConversionResult:
    """
    Complete result for a batch conversion.
    """

    source_directory: str
    output_directory: str

    total_files: int = 0
    successful_files: int = 0
    failed_files: int = 0

    files: List[BatchFileResult] = field(
        default_factory=list
    )


# ============================================================
# FILE DISCOVERY
# ============================================================

def find_text_files(
    source_directory: str,
) -> List[Path]:
    """
    Find .txt files inside source_directory.

    Files are returned in deterministic alphabetical order.
    """

    source = Path(source_directory)

    if not source.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {source}"
        )

    if not source.is_dir():
        raise NotADirectoryError(
            f"Source path is not a directory: {source}"
        )

    files = [
        path
        for path in source.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".txt"
    ]

    return sorted(
        files,
        key=lambda path: path.name.lower(),
    )


# ============================================================
# SAFE TEXT READING
# ============================================================

def read_text_file(
    path: Path,
) -> str:
    """
    Read a legacy text file.

    UTF-16 and UTF-8 BOM files are handled first.

    UTF-8 is tried next.

    Latin-1 is the final fallback because it preserves
    every byte value from 0x00 through 0xFF.
    """

    data = path.read_bytes()

    # --------------------------------------------------------
    # UTF-16 BOM
    # --------------------------------------------------------

    if (
        data.startswith(b"\xff\xfe")
        or data.startswith(b"\xfe\xff")
    ):
        return data.decode("utf-16")

    # --------------------------------------------------------
    # UTF-8 BOM
    # --------------------------------------------------------

    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")

    # --------------------------------------------------------
    # Normal UTF-8
    # --------------------------------------------------------

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        pass

    # --------------------------------------------------------
    # Legacy byte-preserving fallback
    # --------------------------------------------------------

    return data.decode("latin-1")


# ============================================================
# SAFE OUTPUT WRITING
# ============================================================

def write_unicode_file(
    path: Path,
    text: str,
) -> None:
    """
    Write Unicode Gujarati as UTF-8 with BOM.

    The BOM improves compatibility with older Windows
    applications.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        text,
        encoding="utf-8-sig",
        newline="",
    )


# ============================================================
# SINGLE FILE CONVERSION
# ============================================================

def convert_single_file(
    source_path: Path,
    output_path: Path,
) -> BatchFileResult:
    """
    Convert one legacy file.

    The source file is never modified.
    """

    result = BatchFileResult(
        source_path=str(source_path),
        output_path=str(output_path),
    )

    try:
        # ----------------------------------------------------
        # READ
        # ----------------------------------------------------

        source_text = read_text_file(
            source_path
        )

        # ----------------------------------------------------
        # CONVERT
        # ----------------------------------------------------

        conversion = convert(
            source_text
        )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        try:
            validation = validate_conversion(
                source_text,
                conversion.unicode_text,
            )
        except TypeError:
            validation = None

        # ----------------------------------------------------
        # WRITE
        # ----------------------------------------------------

        write_unicode_file(
            output_path,
            conversion.unicode_text,
        )

        # ----------------------------------------------------
        # RESULT INFORMATION
        # ----------------------------------------------------

        result.success = True

        result.input_characters = (
            conversion.total_characters
        )

        result.output_characters = (
            len(conversion.unicode_text)
        )

        result.gujarati_characters = (
            conversion.gujarati_count
        )

        result.unresolved_count = (
            conversion.unresolved_count
        )

        result.confidence = (
            conversion.confidence
        )

        result.warnings.extend(
            conversion.warnings
        )

        # ----------------------------------------------------
        # OPTIONAL VALIDATION INFORMATION
        # ----------------------------------------------------

        if validation is not None:

            if isinstance(validation, dict):

                warnings = validation.get(
                    "warnings"
                )

                if isinstance(warnings, list):

                    result.warnings.extend(
                        str(item)
                        for item in warnings
                    )

                valid = validation.get(
                    "valid"
                )

                if valid is False:

                    result.warnings.append(
                        "Conversion validator reported "
                        "that this file requires review."
                    )

        return result

    except Exception as exc:

        result.success = False

        result.error = (
            f"{type(exc).__name__}: {exc}"
        )

        return result


# ============================================================
# BATCH CONVERSION
# ============================================================

def convert_directory(
    source_directory: str,
    output_directory: str,
    overwrite: bool = False,
) -> BatchConversionResult:
    """
    Convert all .txt files in a directory.

    Source files are never modified.

    Existing output files are not overwritten unless
    overwrite=True.
    """

    source = Path(
        source_directory
    )

    output = Path(
        output_directory
    )

    files = find_text_files(
        str(source)
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    batch_result = BatchConversionResult(
        source_directory=str(source),
        output_directory=str(output),
        total_files=len(files),
    )

    for source_path in files:

        output_path = (
            output
            / f"{source_path.stem}_unicode.txt"
        )

        # ----------------------------------------------------
        # EXISTING OUTPUT PROTECTION
        # ----------------------------------------------------

        if (
            output_path.exists()
            and not overwrite
        ):

            file_result = BatchFileResult(
                source_path=str(source_path),
                output_path=str(output_path),
                success=False,
                error=(
                    "Output file already exists. "
                    "Use overwrite=True to replace it."
                ),
            )

            batch_result.files.append(
                file_result
            )

            batch_result.failed_files += 1

            continue

        # ----------------------------------------------------
        # CONVERT SINGLE FILE
        # ----------------------------------------------------

        file_result = convert_single_file(
            source_path,
            output_path,
        )

        batch_result.files.append(
            file_result
        )

        if file_result.success:
            batch_result.successful_files += 1
        else:
            batch_result.failed_files += 1

    return batch_result


# ============================================================
# REPORT
# ============================================================

def print_batch_report(
    result: BatchConversionResult,
) -> None:
    """
    Print a human-readable batch conversion report.
    """

    print()
    print("=" * 70)
    print("HARI BATCH CONVERSION REPORT")
    print("=" * 70)

    print(
        f"Source directory : {result.source_directory}"
    )

    print(
        f"Output directory : {result.output_directory}"
    )

    print(
        f"Total files      : {result.total_files}"
    )

    print(
        f"Successful       : {result.successful_files}"
    )

    print(
        f"Failed           : {result.failed_files}"
    )

    print()

    for index, file_result in enumerate(
        result.files,
        1,
    ):

        print(
            f"{index:03d}. "
            f"{Path(file_result.source_path).name}"
        )

        print(
            f"     Status      : "
            f"{'SUCCESS' if file_result.success else 'FAILED'}"
        )

        if file_result.output_path:

            print(
                f"     Output      : "
                f"{file_result.output_path}"
            )

        if file_result.success:

            print(
                f"     Characters  : "
                f"{file_result.input_characters} -> "
                f"{file_result.output_characters}"
            )

            print(
                f"     Gujarati    : "
                f"{file_result.gujarati_characters}"
            )

            print(
                f"     Unresolved  : "
                f"{file_result.unresolved_count}"
            )

            print(
                f"     Confidence  : "
                f"{file_result.confidence}"
            )

        if file_result.error:

            print(
                f"     ERROR       : "
                f"{file_result.error}"
            )

        if file_result.warnings:

            print(
                "     Warnings:"
            )

            for warning in file_result.warnings:

                print(
                    f"       - {warning}"
                )

    print("=" * 70)


# ============================================================
# TEST HELPERS
# ============================================================

def _create_test_file(
    path: Path,
    text: str,
) -> None:
    """
    Create a small legacy test file using Latin-1.
    """

    path.write_bytes(
        text.encode("latin-1")
    )


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    import tempfile

    print("=" * 70)
    print("HARI BATCH CONVERTER TEST")
    print("=" * 70)

    passed = 0
    failed = 0

    def check(
        name: str,
        actual,
        expected,
    ) -> None:

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
                f"       Expected: {expected!r}"
            )

            print(
                f"       Actual:   {actual!r}"
            )

            failed += 1

    # --------------------------------------------------------
    # TEMPORARY TEST ENVIRONMENT
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source = (
            root / "legacy"
        )

        output = (
            root / "unicode"
        )

        source.mkdir()

        # ----------------------------------------------------
        # TEST FILES
        # ----------------------------------------------------

        _create_test_file(
            source / "document1.txt",
            "a[v)\r\nh&km",
        )

        _create_test_file(
            source / "document2.txt",
            "T*>kmi>\r\nABC 123",
        )

        # ----------------------------------------------------
        # FILE DISCOVERY
        # ----------------------------------------------------

        files = find_text_files(
            str(source)
        )

        check(
            "file discovery",
            len(files),
            2,
        )

        # ----------------------------------------------------
        # BATCH CONVERSION
        # ----------------------------------------------------

        result = convert_directory(
            str(source),
            str(output),
        )

        check(
            "batch total",
            result.total_files,
            2,
        )

        check(
            "successful files",
            result.successful_files,
            2,
        )

        check(
            "failed files",
            result.failed_files,
            0,
        )

        # ----------------------------------------------------
        # OUTPUT FILE 1
        # ----------------------------------------------------

        output1 = (
            output
            / "document1_unicode.txt"
        )

        check(
            "output file 1 exists",
            output1.exists(),
            True,
        )

        if output1.exists():

            text1 = output1.read_bytes().decode(
                "utf-8-sig"
            )

            check(
                "output file 1 content",
                text1,
                "એવી\r\nહુકમ",
            )

        # ----------------------------------------------------
        # OUTPUT FILE 2
        # ----------------------------------------------------

        output2 = (
            output
            / "document2_unicode.txt"
        )

        check(
            "output file 2 exists",
            output2.exists(),
            True,
        )

        if output2.exists():

            text2 = output2.read_bytes().decode(
                "utf-8-sig"
            )

            check(
                "output file 2 content",
                text2,
                "ટૂંકમાં\r\nABC ૧૨૩",
            )

        # ----------------------------------------------------
        # SOURCE FILES MUST REMAIN UNCHANGED
        # ----------------------------------------------------

        original1 = (
            source
            / "document1.txt"
        ).read_bytes()

        original2 = (
            source
            / "document2.txt"
        ).read_bytes()

        check(
            "source file 1 preserved",
            original1,
            "a[v)\r\nh&km".encode(
                "latin-1"
            ),
        )

        check(
            "source file 2 preserved",
            original2,
            "T*>kmi>\r\nABC 123".encode(
                "latin-1"
            ),
        )

        # ----------------------------------------------------
        # EXISTING OUTPUT PROTECTION
        # ----------------------------------------------------

        result2 = convert_directory(
            str(source),
            str(output),
        )

        check(
            "existing output protection",
            result2.failed_files,
            2,
        )

        # ----------------------------------------------------
        # EXPLICIT OVERWRITE
        # ----------------------------------------------------

        result3 = convert_directory(
            str(source),
            str(output),
            overwrite=True,
        )

        check(
            "explicit overwrite",
            result3.successful_files,
            2,
        )

    # --------------------------------------------------------
    # FINAL RESULT
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