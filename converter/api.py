from __future__ import annotations

# ============================================================
# Hari / Harikrishna Legacy Gujarati -> Unicode
# Public Application API
#
# This module is the stable entry point for the converter.
#
# Other parts of the application should preferably call this
# module instead of importing internal converter modules
# directly.
# ============================================================

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .document_converter import SUPPORTED_DOCUMENT_EXTENSIONS, convert_document
except ImportError:
    from document_converter import SUPPORTED_DOCUMENT_EXTENSIONS, convert_document


# ============================================================
# INTERNAL IMPORTS
# ============================================================

try:
    from .hari_decoder import decode_hari_text as _hari_convert_text
except ImportError:
    from hari_decoder import decode_hari_text as _hari_convert_text

try:
    from .font_profiles import get_font_profile
except ImportError:
    from font_profiles import get_font_profile

try:
    from .file_type import detect_file_type
except ImportError:
    from file_type import detect_file_type

try:
    from .font_utils import choose_unicode_output_font
except ImportError:
    from font_utils import choose_unicode_output_font


# ============================================================
# TYPES
# ============================================================

PathLike = Union[str, Path]


# ============================================================
# VERSION
# ============================================================

API_VERSION = "1.0.1"


# ============================================================
# INPUT DECODING
# ============================================================

def _decode_legacy_file_bytes(data: bytes) -> tuple[str, str]:
    """Read a saved Hari text file without corrupting extended glyphs.

    Text copied from Word or Notepad is commonly saved as UTF-8, even though
    its *characters* are Hari legacy glyphs.  Decoding such a file as
    Latin-1 splits every extended glyph into mojibake.  Genuine old ANSI
    files are still supported through Windows-1252, with Latin-1 retained as
    the lossless final fallback.
    """
    try:
        return data.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        pass

    try:
        return data.decode("cp1252"), "cp1252"
    except UnicodeDecodeError:
        return data.decode("latin-1"), "latin-1"


# ============================================================
# TEXT CONVERSION
# ============================================================

def convert_text(
    text: str,
    font: str = "Hari / Harikrishna",
    context_before: str = "",
    context_after: str = "",
) -> str:
    """
    Convert one legacy Gujarati text string to Unicode Gujarati.

    Hari / Harikrishna uses the verified hari_decoder directly.
    LMG Arun / Lohit BKMAN uses the shared Arun-family decoder.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a Python string")

    profile = get_font_profile(font)

    if profile["family"] == "hari":
        return _hari_convert_text(text)

    if profile["family"] == "arun":
        try:
            from .arun import convert_arun_text
        except ImportError:
            from arun import convert_arun_text

        return convert_arun_text(
            text,
            context_before=context_before,
            context_after=context_after,
        )

    raise ValueError(
        f"Unsupported font family: {profile['family']}"
    )


# ============================================================
# FILE CONVERSION
# ============================================================

def convert_file(
    input_path: PathLike,
    output_path: Optional[PathLike] = None,
    overwrite: bool = False,
    font: str = "Hari / Harikrishna",
) -> Dict[str, Any]:
    """Convert one legacy Gujarati file safely.

    Normal extensions are handled directly. Files without an extension are
    identified from their package structure (DOCX/ODT) or conservative text
    detection. The conversion algorithms themselves are unchanged.
    """
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Input file does not exist: {source}")
    if not source.is_file():
        raise ValueError(f"Input path is not a file: {source}")

    detected = detect_file_type(source)
    if detected is None:
        raise ValueError(
            "Unsupported or unrecognized file. Supported files: TXT, DOCX and ODT."
        )

    destination = (
        source.with_name(source.stem + "_unicode" + (detected or source.suffix))
        if output_path is None else Path(output_path)
    )
    source_resolved = source.resolve()
    destination_resolved = destination.resolve()
    if source_resolved == destination_resolved:
        raise ValueError("Input and output files must be different.")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {destination}")

    if detected in SUPPORTED_DOCUMENT_EXTENSIONS:
        profile = get_font_profile(font)
        output_font = choose_unicode_output_font()
        import tempfile
        temp_source = None
        actual_source = source
        if source.suffix.lower() != detected:
            temp_source = Path(tempfile.mkstemp(prefix="glfc_src_", suffix=detected, dir=str(source.parent))[1])
            try:
                temp_source.write_bytes(source.read_bytes())
                actual_source = temp_source
                result = convert_document(
                    actual_source,
                    destination,
                    lambda text, context_before="", context_after="": convert_text(
                        text,
                        font=font,
                        context_before=context_before,
                        context_after=context_after,
                    ),
                    overwrite=overwrite,
                    legacy_font_names=set(profile.get("legacy_font_names", set())),
                    output_font=output_font,
                )
            finally:
                try:
                    temp_source.unlink(missing_ok=True)
                except Exception:
                    pass
        else:
            result = convert_document(
                actual_source,
                destination,
                lambda text, context_before="", context_after="": convert_text(
                        text,
                        font=font,
                        context_before=context_before,
                        context_after=context_after,
                    ),
                overwrite=overwrite,
                legacy_font_names=set(profile.get("legacy_font_names", set())),
                output_font=output_font,
            )
        result["input_path"] = str(source)
        result["detected_type"] = detected
        return result

    data = source.read_bytes()
    legacy_text, input_encoding = _decode_legacy_file_bytes(data)
    unicode_text = convert_text(legacy_text, font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".tmp")
    try:
        temp.write_text(unicode_text, encoding="utf-8-sig", newline="")
        temp.replace(destination)
    except Exception:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass
        raise
    return {
        "success": True,
        "input_path": str(source),
        "output_path": str(destination),
        "input_characters": len(legacy_text),
        "input_encoding": input_encoding,
        "output_characters": len(unicode_text),
        "output_text": unicode_text,
        "detected_type": detected,
    }


# ============================================================
# FOLDER CONVERSION
# ============================================================

def convert_folder(
    input_directory: PathLike,
    output_directory: Optional[PathLike] = None,
    overwrite: bool = False,
    font: str = "Hari / Harikrishna",
) -> Dict[str, Any]:
    """Recursively convert supported TXT/DOCX/ODT files, including extensionless files."""
    source_directory = Path(input_directory)
    if not source_directory.exists():
        raise FileNotFoundError(f"Input directory does not exist: {source_directory}")
    if not source_directory.is_dir():
        raise ValueError(f"Input path is not a directory: {source_directory}")

    destination_directory = (
        source_directory / "Unicode_Output"
        if output_directory is None else Path(output_directory)
    )
    destination_directory.mkdir(parents=True, exist_ok=True)

    source_resolved = source_directory.resolve()
    output_resolved = destination_directory.resolve()
    files = []
    for path in source_directory.rglob("*"):
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(output_resolved)
            continue
        except ValueError:
            pass
        if detect_file_type(path) is not None:
            files.append(path)
    files.sort(key=lambda p: str(p.relative_to(source_directory)).lower())

    results: List[Dict[str, Any]] = []
    successful = failed = 0
    for source in files:
        detected = detect_file_type(source)
        relative_parent = source.relative_to(source_directory).parent
        suffix = detected or source.suffix
        destination = destination_directory / relative_parent / (source.stem + "_unicode" + suffix)
        try:
            result = convert_file(
                source,
                destination,
                overwrite=overwrite,
                font=font,
            )
            results.append(result)
            successful += 1
        except Exception as exc:
            results.append({
                "success": False,
                "input_path": str(source),
                "output_path": str(destination),
                "error": f"{type(exc).__name__}: {exc}",
            })
            failed += 1

    return {
        "success": failed == 0,
        "input_directory": str(source_directory),
        "output_directory": str(destination_directory),
        "total_files": len(files),
        "successful_files": successful,
        "failed_files": failed,
        "results": results,
    }


# ============================================================
# API INFORMATION
# ============================================================

def get_api_info() -> Dict[str, str]:
    """
    Return basic public API information.
    """

    return {
        "name":
            "Gujarati Legacy Font Converter",

        "api_version":
            API_VERSION,

        "purpose":
            (
                "Hari/Harikrishna and LMG Arun/Lohit BKMAN "
                "legacy Gujarati to Unicode conversion"
            ),
    }


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    import tempfile

    print("=" * 70)
    print(
        "HARI PUBLIC API TEST"
    )
    print("=" * 70)

    passed = 0
    failed = 0

    def check(
        name: str,
        actual: Any,
        expected: Any,
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
    # Basic API
    # --------------------------------------------------------

    check(
        "text conversion",
        convert_text("a[v)"),
        "એવી",
    )

    check(
        "conjunct conversion",
        convert_text(r"k\m)nl"),
        "ક્રિમીનલ",
    )

    check(
        "Unicode normalization",
        convert_text("airi[p)"),
        "આરોપી",
    )

    # LMG-Arun O-matra regression tests.  Legacy typists may enter AA + E
    # or E + AA to produce the same Gujarati O-matra visually.
    check(
        "Arun O-matra AA+E",
        convert_text("ZF[H", font="LMG Arun / Lohit BKMAN"),
        "રોજ",
    )

    check(
        "Arun O-matra E+AA",
        convert_text("Z[FH", font="LMG Arun / Lohit BKMAN"),
        "રોજ",
    )

    check(
        "Arun consonant AA remains AA",
        convert_text("ZF", font="LMG Arun / Lohit BKMAN"),
        "રા",
    )

    check(
        "Arun consonant E remains E",
        convert_text("Z[H", font="LMG Arun / Lohit BKMAN"),
        "રેજ",
    )

    # --------------------------------------------------------
    # Type validation
    # --------------------------------------------------------

    type_error = False

    try:

        convert_text(123)

    except TypeError:

        type_error = True

    check(
        "text type validation",
        type_error,
        True,
    )

    # --------------------------------------------------------
    # File API
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source = (
            root
            / "sample.txt"
        )

        source.write_bytes(
            "a[v)\r\nh&km".encode(
                "latin-1"
            )
        )

        output = (
            root
            / "output.txt"
        )

        result = convert_file(
            source,
            output,
        )

        check(
            "file conversion success",
            result["success"],
            True,
        )

        check(
            "output file exists",
            output.exists(),
            True,
        )

        output_text = (
            output.read_bytes()
            .decode("utf-8-sig")
        )

        check(
            "file Unicode output",
            output_text,
            "એવી\r\nહુકમ",
        )

        # ----------------------------------------------------
        # Existing output protection
        # ----------------------------------------------------

        protected = False

        try:

            convert_file(
                source,
                output,
            )

        except FileExistsError:

            protected = True

        check(
            "existing output protection",
            protected,
            True,
        )

        # ----------------------------------------------------
        # Explicit overwrite
        # ----------------------------------------------------

        overwrite_result = (
            convert_file(
                source,
                output,
                overwrite=True,
            )
        )

        check(
            "explicit overwrite",
            overwrite_result["success"],
            True,
        )

        # ----------------------------------------------------
        # Folder API
        # ----------------------------------------------------

        folder = (
            root
            / "input"
        )

        folder.mkdir()

        (
            folder
            / "one.txt"
        ).write_bytes(
            "a[v)".encode(
                "latin-1"
            )
        )

        (
            folder
            / "two.txt"
        ).write_bytes(
            "h&km".encode(
                "latin-1"
            )
        )

        output_folder = (
            root
            / "folder_output"
        )

        batch_result = (
            convert_folder(
                folder,
                output_folder,
            )
        )

        check(
            "folder conversion success",
            batch_result["success"],
            True,
        )

        check(
            "folder total",
            batch_result["total_files"],
            2,
        )

        check(
            "folder successful",
            batch_result[
                "successful_files"
            ],
            2,
        )

        check(
            "folder failed",
            batch_result[
                "failed_files"
            ],
            0,
        )

        check(
            "folder output one",
            (
                output_folder
                / "one_unicode.txt"
            ).exists(),
            True,
        )

        check(
            "folder output two",
            (
                output_folder
                / "two_unicode.txt"
            ).exists(),
            True,
        )

    # --------------------------------------------------------
    # API information
    # --------------------------------------------------------

    info = get_api_info()

    check(
        "API information",
        isinstance(
            info,
            dict,
        ),
        True,
    )

    check(
        "API version",
        info["api_version"],
        API_VERSION,
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
