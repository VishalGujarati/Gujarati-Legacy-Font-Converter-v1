# ============================================================
# Hari / Harikrishna Legacy Gujarati -> Unicode
# Application Service Layer
#
# This module sits between the public API and the future GUI.
#
# GUI
#   ↓
# service.py
#   ↓
# api.py
#   ↓
# conversion engine
#
# The GUI should not need to know about internal converter
# modules.
# ============================================================

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Union


# ============================================================
# INTERNAL IMPORTS
# ============================================================

try:
    from .api import (
        convert_text as api_convert_text,
        convert_file as api_convert_file,
        convert_folder as api_convert_folder,
    )

    from .error_handling import (
        ApplicationError,
        ErrorCode,
        create_error,
        exception_to_error,
    )

except ImportError:

    from api import (
        convert_text as api_convert_text,
        convert_file as api_convert_file,
        convert_folder as api_convert_folder,
    )

    from error_handling import (
        ApplicationError,
        ErrorCode,
        create_error,
        exception_to_error,
    )


# ============================================================
# TYPES
# ============================================================

PathLike = Union[str, Path]


# ============================================================
# SERVICE RESULT
# ============================================================

@dataclass
class ServiceResult:
    """
    Standard result returned by the service layer.

    The GUI can use this single structure for successful
    operations and failures.
    """

    success: bool

    operation: str

    message: str = ""

    data: Any = None

    error: Optional[ApplicationError] = None

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict:
        """
        Convert the result into a JSON-safe dictionary.
        """

        return {
            "success": self.success,

            "operation": self.operation,

            "message": self.message,

            "data": self.data,

            "error": (
                self.error.to_dict()
                if self.error is not None
                else None
            ),

            "warnings": list(
                self.warnings
            ),
        }


# ============================================================
# TEXT SERVICE
# ============================================================

def convert_text(
    text: str,
    font: str = "Hari / Harikrishna",
) -> ServiceResult:
    """
    Convert legacy Gujarati text.

    This function never exposes an unexpected exception to
    the caller. Errors are returned as ServiceResult.error.
    """

    operation = "convert_text"

    if not isinstance(text, str):

        error = create_error(
            ErrorCode.INVALID_INPUT,
            "Text input is not a string.",
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )

    try:

        converted = api_convert_text(
            text,
            font=font,
        )

        return ServiceResult(
            success=True,
            operation=operation,
            message=(
                "Text converted successfully."
            ),
            data={
                "input_text": text,
                "output_text": converted,
                "input_characters": len(text),
                "output_characters": len(
                    converted
                ),
            },
        )

    except Exception as exc:

        error = exception_to_error(
            exc
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )


# ============================================================
# FILE SERVICE
# ============================================================

def convert_file(
    input_path: PathLike,
    output_path: Optional[PathLike] = None,
    overwrite: bool = False,
    font: str = "Hari / Harikrishna",
) -> ServiceResult:
    """
    Convert one legacy file.

    Returns a ServiceResult instead of exposing exceptions
    directly to the GUI.
    """

    operation = "convert_file"

    source = Path(input_path)

    destination = (
        Path(output_path)
        if output_path is not None
        else None
    )

    # --------------------------------------------------------
    # Input validation
    # --------------------------------------------------------

    if not source.exists():

        error = create_error(
            ErrorCode.FILE_NOT_FOUND,
            "Input file does not exist.",
            source_path=str(source),
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )

    if not source.is_file():

        error = create_error(
            ErrorCode.NOT_A_FILE,
            "Input path is not a file.",
            source_path=str(source),
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )

    try:

        result = api_convert_file(
            source,
            destination,
            overwrite=overwrite,
            font=font,
        )

        return ServiceResult(
            success=True,
            operation=operation,
            message=(
                "File converted successfully."
            ),
            data=result,
        )

    except Exception as exc:

        error = exception_to_error(
            exc,
            source_path=str(source),
            output_path=(
                str(destination)
                if destination is not None
                else None
            ),
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )


# ============================================================
# FOLDER SERVICE
# ============================================================

def convert_folder(
    input_directory: PathLike,
    output_directory: Optional[PathLike] = None,
    overwrite: bool = False,
    font: str = "Hari / Harikrishna",
) -> ServiceResult:
    """
    Convert all supported files in a folder.
    """

    operation = "convert_folder"

    source = Path(
        input_directory
    )

    destination = (
        Path(output_directory)
        if output_directory is not None
        else None
    )

    # --------------------------------------------------------
    # Input validation
    # --------------------------------------------------------

    if not source.exists():

        error = create_error(
            ErrorCode.DIRECTORY_NOT_FOUND,
            "Input directory does not exist.",
            source_path=str(source),
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )

    if not source.is_dir():

        error = create_error(
            ErrorCode.NOT_A_DIRECTORY,
            "Input path is not a directory.",
            source_path=str(source),
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )

    try:

        result = api_convert_folder(
            source,
            destination,
            overwrite=overwrite,
            font=font,
        )

        # ----------------------------------------------------
        # Batch conversion can complete with some failures.
        # ----------------------------------------------------

        if result.get(
            "failed_files",
            0,
        ) > 0:

            warnings = [
                (
                    f"{result['failed_files']} "
                    "file(s) could not be converted."
                )
            ]

            return ServiceResult(
                success=False,
                operation=operation,
                message=(
                    "Folder conversion completed "
                    "with errors."
                ),
                data=result,
                warnings=warnings,
            )

        return ServiceResult(
            success=True,
            operation=operation,
            message=(
                "Folder converted successfully."
            ),
            data=result,
        )

    except Exception as exc:

        error = exception_to_error(
            exc,
            source_path=str(source),
            output_path=(
                str(destination)
                if destination is not None
                else None
            ),
        )

        return ServiceResult(
            success=False,
            operation=operation,
            message=error.user_message,
            error=error,
        )


# ============================================================
# RESULT HELPERS
# ============================================================

def is_success(
    result: ServiceResult,
) -> bool:
    """
    Return True when an operation succeeded.
    """

    return result.success


def get_message(
    result: ServiceResult,
) -> str:
    """
    Return the user-facing message.
    """

    return result.message


def get_error(
    result: ServiceResult,
) -> Optional[ApplicationError]:
    """
    Return the structured error, if any.
    """

    return result.error


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    import tempfile

    print("=" * 70)
    print(
        "HARI APPLICATION SERVICE TEST"
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
    # Text conversion
    # --------------------------------------------------------

    result = convert_text(
        "a[v)"
    )

    check(
        "text service success",
        result.success,
        True,
    )

    check(
        "text service output",
        result.data["output_text"],
        "એવી",
    )

    check(
        "text service operation",
        result.operation,
        "convert_text",
    )

    # --------------------------------------------------------
    # Text invalid input
    # --------------------------------------------------------

    result = convert_text(
        123
    )

    check(
        "text invalid input",
        result.success,
        False,
    )

    check(
        "text invalid error",
        result.error.code,
        ErrorCode.INVALID_INPUT,
    )

    # --------------------------------------------------------
    # File conversion
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source = (
            root / "sample.txt"
        )

        source.write_bytes(
            "a[v)\r\nh&km".encode(
                "latin-1"
            )
        )

        output = (
            root / "output.txt"
        )

        result = convert_file(
            source,
            output,
        )

        check(
            "file service success",
            result.success,
            True,
        )

        check(
            "file service operation",
            result.operation,
            "convert_file",
        )

        check(
            "file service output exists",
            output.exists(),
            True,
        )

        check(
            "file service output content",
            output.read_bytes().decode(
                "utf-8-sig"
            ),
            "એવી\r\nહુકમ",
        )

        # ----------------------------------------------------
        # Missing file
        # ----------------------------------------------------

        missing = (
            root / "missing.txt"
        )

        result = convert_file(
            missing
        )

        check(
            "missing file handled",
            result.success,
            False,
        )

        check(
            "missing file error",
            result.error.code,
            ErrorCode.FILE_NOT_FOUND,
        )

        # ----------------------------------------------------
        # Existing output
        # ----------------------------------------------------

        result = convert_file(
            source,
            output,
        )

        check(
            "existing output handled",
            result.success,
            False,
        )

        check(
            "existing output error",
            result.error.code,
            ErrorCode.OUTPUT_EXISTS,
        )

        # ----------------------------------------------------
        # Explicit overwrite
        # ----------------------------------------------------

        result = convert_file(
            source,
            output,
            overwrite=True,
        )

        check(
            "overwrite service success",
            result.success,
            True,
        )

        # ----------------------------------------------------
        # Folder conversion
        # ----------------------------------------------------

        input_folder = (
            root / "input"
        )

        input_folder.mkdir()

        (
            input_folder / "one.txt"
        ).write_bytes(
            "a[v)".encode(
                "latin-1"
            )
        )

        (
            input_folder / "two.txt"
        ).write_bytes(
            "h&km".encode(
                "latin-1"
            )
        )

        output_folder = (
            root / "output"
        )

        result = convert_folder(
            input_folder,
            output_folder,
        )

        check(
            "folder service success",
            result.success,
            True,
        )

        check(
            "folder service total",
            result.data[
                "total_files"
            ],
            2,
        )

        check(
            "folder service successful",
            result.data[
                "successful_files"
            ],
            2,
        )

        check(
            "folder service failed",
            result.data[
                "failed_files"
            ],
            0,
        )

        # ----------------------------------------------------
        # Missing folder
        # ----------------------------------------------------

        missing_folder = (
            root / "missing_folder"
        )

        result = convert_folder(
            missing_folder
        )

        check(
            "missing folder handled",
            result.success,
            False,
        )

        check(
            "missing folder error",
            result.error.code,
            ErrorCode.DIRECTORY_NOT_FOUND,
        )

        # ----------------------------------------------------
        # Path is file, not directory
        # ----------------------------------------------------

        result = convert_folder(
            source
        )

        check(
            "file as folder handled",
            result.success,
            False,
        )

        check(
            "file as folder error",
            result.error.code,
            ErrorCode.NOT_A_DIRECTORY,
        )

    # --------------------------------------------------------
    # Result helpers
    # --------------------------------------------------------

    success_result = convert_text(
        "a[v)"
    )

    check(
        "is_success helper",
        is_success(success_result),
        True,
    )

    check(
        "get_message helper",
        get_message(
            success_result
        ),
        "Text converted successfully.",
    )

    failed_result = convert_text(
        123
    )

    check(
        "get_error helper",
        get_error(
            failed_result
        ).code,
        ErrorCode.INVALID_INPUT,
    )

    # --------------------------------------------------------
    # Dictionary conversion
    # --------------------------------------------------------

    result_dict = (
        success_result.to_dict()
    )

    check(
        "service result dictionary",
        isinstance(
            result_dict,
            dict,
        ),
        True,
    )

    check(
        "service dictionary success",
        result_dict["success"],
        True,
    )

    check(
        "service dictionary operation",
        result_dict["operation"],
        "convert_text",
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