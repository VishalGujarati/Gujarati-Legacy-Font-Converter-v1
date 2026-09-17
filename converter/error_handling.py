# ============================================================
# Hari / Harikrishna Legacy Gujarati -> Unicode
# Centralized Error Handling
# ============================================================

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ============================================================
# ERROR CATEGORIES
# ============================================================

class ErrorCategory(Enum):
    """
    High-level categories used by the application.
    """

    INPUT = "input"

    FILE = "file"

    ENCODING = "encoding"

    CONVERSION = "conversion"

    OUTPUT = "output"

    VALIDATION = "validation"

    CONFIGURATION = "configuration"

    INTERNAL = "internal"


# ============================================================
# ERROR CODES
# ============================================================

class ErrorCode(Enum):
    """
    Stable error codes.

    The GUI can display friendly messages based on these
    codes without depending on Python exception text.
    """

    INVALID_INPUT = "E001"

    FILE_NOT_FOUND = "E002"

    NOT_A_FILE = "E003"

    DIRECTORY_NOT_FOUND = "E004"

    NOT_A_DIRECTORY = "E005"

    FILE_READ_FAILED = "E006"

    FILE_WRITE_FAILED = "E007"

    OUTPUT_EXISTS = "E008"

    UNSUPPORTED_FILE = "E009"

    INVALID_ENCODING = "E010"

    CONVERSION_FAILED = "E011"

    VALIDATION_FAILED = "E012"

    CONFIGURATION_FAILED = "E013"

    UNKNOWN_ERROR = "E999"


# ============================================================
# APPLICATION ERROR
# ============================================================

@dataclass
class ApplicationError:
    """
    Structured application error.

    This object separates:
        - what happened
        - where it happened
        - what the user should see
        - technical details for diagnostics
    """

    code: ErrorCode

    category: ErrorCategory

    message: str

    user_message: str

    technical_message: str = ""

    source_path: Optional[str] = None

    output_path: Optional[str] = None

    recoverable: bool = True

    exception_type: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert the error into a JSON-safe dictionary.
        """

        return {
            "code": self.code.value,
            "category": self.category.value,
            "message": self.message,
            "user_message": self.user_message,
            "technical_message":
                self.technical_message,
            "source_path":
                self.source_path,
            "output_path":
                self.output_path,
            "recoverable":
                self.recoverable,
            "exception_type":
                self.exception_type,
        }

    def __str__(self) -> str:
        """
        Human-readable technical representation.
        """

        location = ""

        if self.source_path:
            location += (
                f" source={self.source_path}"
            )

        if self.output_path:
            location += (
                f" output={self.output_path}"
            )

        return (
            f"[{self.code.value}] "
            f"{self.message}"
            f"{location}"
        )


# ============================================================
# FRIENDLY MESSAGES
# ============================================================

USER_MESSAGES = {

    ErrorCode.INVALID_INPUT:
        "The supplied input is not valid.",

    ErrorCode.FILE_NOT_FOUND:
        "The selected file could not be found.",

    ErrorCode.NOT_A_FILE:
        "The selected path is not a file.",

    ErrorCode.DIRECTORY_NOT_FOUND:
        "The selected folder could not be found.",

    ErrorCode.NOT_A_DIRECTORY:
        "The selected path is not a folder.",

    ErrorCode.FILE_READ_FAILED:
        "The file could not be read.",

    ErrorCode.FILE_WRITE_FAILED:
        "The converted file could not be saved.",

    ErrorCode.OUTPUT_EXISTS:
        "The output file already exists.",

    ErrorCode.UNSUPPORTED_FILE:
        "This file type is not supported.",

    ErrorCode.INVALID_ENCODING:
        "The file encoding could not be processed.",

    ErrorCode.CONVERSION_FAILED:
        "The text could not be converted.",

    ErrorCode.VALIDATION_FAILED:
        "The converted result did not pass validation.",

    ErrorCode.CONFIGURATION_FAILED:
        "The application configuration is invalid.",

    ErrorCode.UNKNOWN_ERROR:
        (
            "An unexpected error occurred. "
            "Please try again."
        ),
}


# ============================================================
# ERROR FACTORY
# ============================================================

def create_error(
    code: ErrorCode,
    message: str,
    *,
    technical_message: str = "",
    source_path: Optional[str] = None,
    output_path: Optional[str] = None,
    recoverable: bool = True,
    exception: Optional[BaseException] = None,
) -> ApplicationError:
    """
    Create a structured ApplicationError.
    """

    category_map = {

        ErrorCode.INVALID_INPUT:
            ErrorCategory.INPUT,

        ErrorCode.FILE_NOT_FOUND:
            ErrorCategory.FILE,

        ErrorCode.NOT_A_FILE:
            ErrorCategory.FILE,

        ErrorCode.DIRECTORY_NOT_FOUND:
            ErrorCategory.FILE,

        ErrorCode.NOT_A_DIRECTORY:
            ErrorCategory.FILE,

        ErrorCode.FILE_READ_FAILED:
            ErrorCategory.FILE,

        ErrorCode.FILE_WRITE_FAILED:
            ErrorCategory.OUTPUT,

        ErrorCode.OUTPUT_EXISTS:
            ErrorCategory.OUTPUT,

        ErrorCode.UNSUPPORTED_FILE:
            ErrorCategory.INPUT,

        ErrorCode.INVALID_ENCODING:
            ErrorCategory.ENCODING,

        ErrorCode.CONVERSION_FAILED:
            ErrorCategory.CONVERSION,

        ErrorCode.VALIDATION_FAILED:
            ErrorCategory.VALIDATION,

        ErrorCode.CONFIGURATION_FAILED:
            ErrorCategory.CONFIGURATION,

        ErrorCode.UNKNOWN_ERROR:
            ErrorCategory.INTERNAL,
    }

    category = category_map.get(
        code,
        ErrorCategory.INTERNAL,
    )

    if exception is not None:

        exception_type = type(
            exception
        ).__name__

        if not technical_message:

            technical_message = str(
                exception
            )

    else:

        exception_type = None

    user_message = USER_MESSAGES.get(
        code,
        USER_MESSAGES[
            ErrorCode.UNKNOWN_ERROR
        ],
    )

    return ApplicationError(
        code=code,
        category=category,
        message=message,
        user_message=user_message,
        technical_message=technical_message,
        source_path=source_path,
        output_path=output_path,
        recoverable=recoverable,
        exception_type=exception_type,
    )


# ============================================================
# EXCEPTION -> APPLICATION ERROR
# ============================================================

def exception_to_error(
    exception: BaseException,
    *,
    source_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> ApplicationError:
    """
    Convert a normal Python exception into a structured
    application error.

    This prevents raw Python exceptions from leaking into
    the GUI.
    """

    if isinstance(
        exception,
        FileNotFoundError,
    ):

        code = (
            ErrorCode.FILE_NOT_FOUND
        )

    elif isinstance(
        exception,
        IsADirectoryError,
    ):

        code = ErrorCode.NOT_A_FILE

    elif isinstance(
        exception,
        NotADirectoryError,
    ):

        code = (
            ErrorCode.NOT_A_DIRECTORY
        )

    elif isinstance(
        exception,
        FileExistsError,
    ):

        code = (
            ErrorCode.OUTPUT_EXISTS
        )

    elif isinstance(
        exception,
        PermissionError,
    ):

        code = (
            ErrorCode.FILE_WRITE_FAILED
        )

    elif isinstance(
        exception,
        UnicodeDecodeError,
    ):

        code = (
            ErrorCode.INVALID_ENCODING
        )

    elif isinstance(
        exception,
        UnicodeEncodeError,
    ):

        code = (
            ErrorCode.INVALID_ENCODING
        )

    elif isinstance(
        exception,
        TypeError,
    ):

        code = (
            ErrorCode.INVALID_INPUT
        )

    elif isinstance(
        exception,
        ValueError,
    ):

        code = (
            ErrorCode.INVALID_INPUT
        )

    else:

        code = (
            ErrorCode.UNKNOWN_ERROR
        )

    return create_error(
        code,
        str(exception)
        or exception.__class__.__name__,
        technical_message=str(
            exception
        ),
        source_path=source_path,
        output_path=output_path,
        exception=exception,
    )


# ============================================================
# SAFE EXECUTION
# ============================================================

def safe_execute(
    function,
    *args,
    source_path: Optional[str] = None,
    output_path: Optional[str] = None,
    **kwargs,
):
    """
    Execute a function safely.

    Returns:
        (success, result, error)

    Example:

        success, result, error = safe_execute(
            convert_text,
            text
        )
    """

    try:

        result = function(
            *args,
            **kwargs,
        )

        return (
            True,
            result,
            None,
        )

    except Exception as exc:

        error = exception_to_error(
            exc,
            source_path=source_path,
            output_path=output_path,
        )

        return (
            False,
            None,
            error,
        )


# ============================================================
# ERROR DISPLAY HELPERS
# ============================================================

def get_user_message(
    error: ApplicationError,
) -> str:
    """
    Return only the safe user-facing message.
    """

    return error.user_message


def get_technical_message(
    error: ApplicationError,
) -> str:
    """
    Return technical diagnostic information.
    """

    if error.technical_message:

        return error.technical_message

    return error.message


def is_recoverable(
    error: ApplicationError,
) -> bool:
    """
    Determine whether the application can continue.
    """

    return error.recoverable


# ============================================================
# TESTS
# ============================================================

def run_tests() -> None:

    print("=" * 70)
    print(
        "HARI ERROR HANDLING TEST"
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
    # Error creation
    # --------------------------------------------------------

    error = create_error(
        ErrorCode.FILE_NOT_FOUND,
        "Test file missing.",
        source_path="test.txt",
    )

    check(
        "error creation",
        isinstance(
            error,
            ApplicationError,
        ),
        True,
    )

    check(
        "error code",
        error.code,
        ErrorCode.FILE_NOT_FOUND,
    )

    check(
        "error category",
        error.category,
        ErrorCategory.FILE,
    )

    check(
        "user message",
        get_user_message(error),
        (
            "The selected file "
            "could not be found."
        ),
    )

    check(
        "source path",
        error.source_path,
        "test.txt",
    )

    # --------------------------------------------------------
    # Dictionary conversion
    # --------------------------------------------------------

    dictionary = error.to_dict()

    check(
        "dictionary conversion",
        isinstance(
            dictionary,
            dict,
        ),
        True,
    )

    check(
        "dictionary code",
        dictionary["code"],
        "E002",
    )

    # --------------------------------------------------------
    # FileNotFoundError
    # --------------------------------------------------------

    converted = exception_to_error(
        FileNotFoundError(
            "missing.txt"
        )
    )

    check(
        "FileNotFoundError mapping",
        converted.code,
        ErrorCode.FILE_NOT_FOUND,
    )

    # --------------------------------------------------------
    # FileExistsError
    # --------------------------------------------------------

    converted = exception_to_error(
        FileExistsError(
            "already exists"
        )
    )

    check(
        "FileExistsError mapping",
        converted.code,
        ErrorCode.OUTPUT_EXISTS,
    )

    # --------------------------------------------------------
    # Unicode error
    # --------------------------------------------------------

    unicode_error = exception_to_error(
        UnicodeDecodeError(
            "utf-8",
            b"\xff",
            0,
            1,
            "invalid byte",
        )
    )

    check(
        "UnicodeDecodeError mapping",
        unicode_error.code,
        ErrorCode.INVALID_ENCODING,
    )

    # --------------------------------------------------------
    # Type error
    # --------------------------------------------------------

    converted = exception_to_error(
        TypeError(
            "bad input"
        )
    )

    check(
        "TypeError mapping",
        converted.code,
        ErrorCode.INVALID_INPUT,
    )

    # --------------------------------------------------------
    # Value error
    # --------------------------------------------------------

    converted = exception_to_error(
        ValueError(
            "bad value"
        )
    )

    check(
        "ValueError mapping",
        converted.code,
        ErrorCode.INVALID_INPUT,
    )

    # --------------------------------------------------------
    # Safe execution success
    # --------------------------------------------------------

    def good_function(value):

        return value * 2

    success, result, error = (
        safe_execute(
            good_function,
            5,
        )
    )

    check(
        "safe execution success",
        success,
        True,
    )

    check(
        "safe execution result",
        result,
        10,
    )

    check(
        "safe execution no error",
        error,
        None,
    )

    # --------------------------------------------------------
    # Safe execution failure
    # --------------------------------------------------------

    def bad_function():

        raise FileNotFoundError(
            "missing"
        )

    success, result, error = (
        safe_execute(
            bad_function
        )
    )

    check(
        "safe execution failure",
        success,
        False,
    )

    check(
        "safe execution result empty",
        result,
        None,
    )

    check(
        "safe execution error",
        isinstance(
            error,
            ApplicationError,
        ),
        True,
    )

    check(
        "safe execution error code",
        error.code,
        ErrorCode.FILE_NOT_FOUND,
    )

    # --------------------------------------------------------
    # Technical message
    # --------------------------------------------------------

    technical = (
        get_technical_message(
            error
        )
    )

    check(
        "technical message",
        technical,
        "missing",
    )

    # --------------------------------------------------------
    # Recoverable
    # --------------------------------------------------------

    check(
        "recoverable error",
        is_recoverable(error),
        True,
    )

    # --------------------------------------------------------
    # String representation
    # --------------------------------------------------------

    error_string = str(error)

    check(
        "string representation",
        "[E002]" in error_string,
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