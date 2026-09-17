# Hari / Harikrishna Legacy Gujarati -> Unicode
# File Conversion Layer
#
# This module connects the file system with the conversion engine.
#
# IMPORTANT:
# No Gujarati word mappings belong here.
#
# Flow:
#
#   Legacy file
#       ↓
#   Read legacy bytes
#       ↓
#   Hari text pipeline
#       ↓
#   Unicode Gujarati
#       ↓
#   Validation
#       ↓
#   UTF-8 Unicode file


from pathlib import Path
from typing import Dict, Optional
import importlib.util


# ============================================================
# CORE CONVERTER IMPORTS
# ============================================================

try:
    from .text_pipeline import convert_text
    from .conversion_validator import validate_conversion

except ImportError:
    from text_pipeline import convert_text
    from conversion_validator import validate_conversion


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IO_FOLDER = PROJECT_ROOT / "io"


# ============================================================
# LOAD A PROJECT MODULE BY FILE PATH
# ============================================================

def load_project_module(
    module_name: str,
    filename: str,
):
    """
    Load one of our project's files directly.

    This is necessary because our project contains a folder
    named 'io', while Python itself also has a built-in
    module named 'io'.
    """

    module_path = IO_FOLDER / filename

    if not module_path.exists():
        raise FileNotFoundError(
            f"Project I/O file not found: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )

    if spec is None:
        raise ImportError(
            f"Could not create module specification for: "
            f"{module_path}"
        )

    if spec.loader is None:
        raise ImportError(
            f"Could not load module: {module_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


# ============================================================
# LOAD LEGACY READER
# ============================================================

legacy_reader_module = load_project_module(
    "hari_project_legacy_reader",
    "legacy_reader.py",
)


# ============================================================
# FIND READER FUNCTION
# ============================================================
#
# Different versions of our reader may use different names.
#
# We support the likely names here so the file converter does
# not depend on one particular implementation.


def _find_reader_function(module):
    """
    Find the available legacy-file reading function.
    """

    possible_names = [
        "read_hari_file",
        "read_legacy_file",
        "read_file",
        "read_text_file",
    ]

    for name in possible_names:

        function = getattr(
            module,
            name,
            None,
        )

        if callable(function):
            return function

    available = [
        name
        for name in dir(module)
        if not name.startswith("_")
    ]

    raise AttributeError(
        "No supported legacy reader function was found "
        "inside io/legacy_reader.py.\n\n"
        "Expected one of:\n"
        "  read_hari_file\n"
        "  read_legacy_file\n"
        "  read_file\n"
        "  read_text_file\n\n"
        f"Functions currently available: {available}"
    )


read_legacy_function = _find_reader_function(
    legacy_reader_module
)


# ============================================================
# LOAD UNICODE WRITER
# ============================================================

unicode_writer_module = load_project_module(
    "hari_project_unicode_writer",
    "unicode_writer.py",
)


# ============================================================
# FIND WRITER FUNCTION
# ============================================================

def _find_writer_function(module):
    """
    Find the available Unicode-file writing function.
    """

    possible_names = [
        "save_unicode_file",
        "write_unicode_file",
        "write_file",
        "save_file",
    ]

    for name in possible_names:

        function = getattr(
            module,
            name,
            None,
        )

        if callable(function):
            return function

    available = [
        name
        for name in dir(module)
        if not name.startswith("_")
    ]

    raise AttributeError(
        "No supported Unicode writer function was found "
        "inside io/unicode_writer.py.\n\n"
        "Expected one of:\n"
        "  save_unicode_file\n"
        "  write_unicode_file\n"
        "  write_file\n"
        "  save_file\n\n"
        f"Functions currently available: {available}"
    )


write_unicode_function = _find_writer_function(
    unicode_writer_module
)


# ============================================================
# READ LEGACY FILE
# ============================================================

def read_legacy_file(
    input_path: str,
):
    """
    Read a Hari legacy file.

    The reader may return either:

        (text, encoding)

    or simply:

        text

    We support both forms.
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Input file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Input path is not a file: {path}"
        )

    result = read_legacy_function(
        str(path)
    )

    # --------------------------------------------------------
    # Normal reader format:
    #
    #     (text, encoding)
    # --------------------------------------------------------

    if isinstance(result, tuple):

        if len(result) >= 2:

            text = result[0]
            encoding = result[1]

            return text, encoding

        if len(result) == 1:

            return result[0], "unknown"

    # --------------------------------------------------------
    # Simple reader format:
    #
    #     text
    # --------------------------------------------------------

    if isinstance(result, str):

        return result, "unknown"

    raise TypeError(
        "Legacy reader returned an unsupported result. "
        f"Received: {type(result).__name__}"
    )


# ============================================================
# WRITE UNICODE FILE
# ============================================================

def write_unicode_file(
    output_path: str,
    text: str,
) -> None:
    """
    Write Unicode Gujarati text using unicode_writer.py.
    """

    if not isinstance(text, str):
        raise TypeError(
            "text must be a Python string"
        )

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Most versions use:
    #
    #     save_unicode_file(path, text)
    #
    # Some may use:
    #
    #     write_unicode_file(path, text)
    #
    # Both are handled by write_unicode_function.

    write_unicode_function(
        str(path),
        text,
    )


# ============================================================
# OUTPUT PATH
# ============================================================

def create_output_path(
    input_path: str,
    output_path: Optional[str] = None,
) -> Path:
    """
    Create the output filename.

    Example:

        judgment.txt

    becomes:

        judgment_unicode.txt
    """

    source = Path(input_path)

    if output_path is not None:

        return Path(output_path)

    return source.with_name(
        source.stem + "_unicode" + source.suffix
    )


# ============================================================
# CONVERT TEXT
# ============================================================

def convert_file_text(
    text: str,
) -> str:
    """
    Convert complete Hari legacy text through the central
    text pipeline.
    """

    if not isinstance(text, str):
        raise TypeError(
            "text must be a Python string"
        )

    return convert_text(text)


# ============================================================
# CONVERT COMPLETE FILE
# ============================================================

def convert_file(
    input_path: str,
    output_path: Optional[str] = None,
) -> Dict:
    """
    Convert one complete Hari legacy file.

    Returns a dictionary containing:

        input path
        output path
        detected encoding
        source length
        converted length
        converted text
        validation report
    """

    # --------------------------------------------------------
    # 1. Read
    # --------------------------------------------------------

    input_file = Path(
        input_path
    )

    source_text, encoding_used = (
        read_legacy_file(
            str(input_file)
        )
    )

    # --------------------------------------------------------
    # 2. Convert
    # --------------------------------------------------------

    converted_text = convert_file_text(
        source_text
    )

    # --------------------------------------------------------
    # 3. Validate
    # --------------------------------------------------------

    validation = validate_conversion(
        source_text
    )

    # --------------------------------------------------------
    # 4. Output path
    # --------------------------------------------------------

    output_file = create_output_path(
        str(input_file),
        output_path,
    )

    # --------------------------------------------------------
    # 5. Write
    # --------------------------------------------------------

    write_unicode_file(
        str(output_file),
        converted_text,
    )

    # --------------------------------------------------------
    # 6. Return result
    # --------------------------------------------------------

    return {
        "input_path": str(input_file),
        "output_path": str(output_file),
        "encoding_used": encoding_used,
        "source_length": len(source_text),
        "converted_length": len(converted_text),
        "converted_text": converted_text,
        "validation": validation,
    }


# ============================================================
# SIMPLE API
# ============================================================

def convert_file_simple(
    input_path: str,
    output_path: Optional[str] = None,
) -> str:
    """
    Convert a file and return only the output path.

    This will be useful for the GUI later.
    """

    result = convert_file(
        input_path,
        output_path,
    )

    return result["output_path"]


# ============================================================
# REPORT
# ============================================================

def print_file_conversion_report(
    result: Dict,
) -> None:
    """
    Print a readable conversion report.
    """

    print()
    print("=" * 80)
    print("HARI FILE CONVERSION REPORT")
    print("=" * 80)

    print()
    print(
        f"Input file        : "
        f"{result['input_path']}"
    )

    print(
        f"Output file       : "
        f"{result['output_path']}"
    )

    print(
        f"Encoding detected : "
        f"{result['encoding_used']}"
    )

    print(
        f"Source length     : "
        f"{result['source_length']}"
    )

    print(
        f"Output length     : "
        f"{result['converted_length']}"
    )

    validation = result[
        "validation"
    ]

    print()
    print("VALIDATION")
    print("-" * 80)

    print(
        f"Gujarati characters        : "
        f"{validation['gujarati_characters']}"
    )

    print(
        f"Possible legacy characters : "
        f"{len(validation['possible_legacy_characters'])}"
    )

    print(
        f"Suspicious characters      : "
        f"{len(validation['suspicious_characters'])}"
    )

    print(
        f"Validation status          : "
        f"{validation['status']}"
    )

    print()
    print("=" * 80)


# ============================================================
# TESTS
# ============================================================

def run_tests():

    print("=" * 70)
    print("HARI FILE CONVERTER TEST")
    print("=" * 70)

    passed = 0
    failed = 0

    # --------------------------------------------------------
    # TEST 1
    # Automatic output filename
    # --------------------------------------------------------

    output = create_output_path(
        r"C:\Test\judgment.txt"
    )

    expected = Path(
        r"C:\Test\judgment_unicode.txt"
    )

    if output == expected:

        print(
            "[PASS] automatic output path"
        )

        passed += 1

    else:

        print(
            "[FAIL] automatic output path"
        )

        print(
            f"       Expected: {expected}"
        )

        print(
            f"       Actual:   {output}"
        )

        failed += 1

    # --------------------------------------------------------
    # TEST 2
    # Explicit output filename
    # --------------------------------------------------------

    output = create_output_path(
        r"C:\Test\input.txt",
        r"C:\Test\output.txt",
    )

    expected = Path(
        r"C:\Test\output.txt"
    )

    if output == expected:

        print(
            "[PASS] explicit output path"
        )

        passed += 1

    else:

        print(
            "[FAIL] explicit output path"
        )

        failed += 1

    # --------------------------------------------------------
    # TEST 3
    # Basic conversion
    # --------------------------------------------------------

    converted = convert_file_text(
        "a[v)"
    )

    if converted == "એવી":

        print(
            "[PASS] file text conversion"
        )

        passed += 1

    else:

        print(
            "[FAIL] file text conversion"
        )

        print(
            f"       Actual: {converted!r}"
        )

        failed += 1

    # --------------------------------------------------------
    # TEST 4
    # Structural conversion
    # --------------------------------------------------------

    converted = convert_file_text(
        "airi[p)"
    )

    if converted == "આરોપી":

        print(
            "[PASS] structural sequence conversion"
        )

        passed += 1

    else:

        print(
            "[FAIL] structural sequence conversion"
        )

        print(
            f"       Actual: {converted!r}"
        )

        failed += 1

    # --------------------------------------------------------
    # TEST 5
    # Project reader detected
    # --------------------------------------------------------

    if callable(
        read_legacy_function
    ):

        print(
            "[PASS] legacy reader loaded"
        )

        passed += 1

    else:

        print(
            "[FAIL] legacy reader loaded"
        )

        failed += 1

    # --------------------------------------------------------
    # TEST 6
    # Project writer detected
    # --------------------------------------------------------

    if callable(
        write_unicode_function
    ):

        print(
            "[PASS] Unicode writer loaded"
        )

        passed += 1

    else:

        print(
            "[FAIL] Unicode writer loaded"
        )

        failed += 1

    # --------------------------------------------------------
    # RESULT
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