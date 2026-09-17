"""Conservative file-type detection for legacy Gujarati conversion.

Supports normal extensions and documents whose filename has no extension.
DOCX/ODT detection is based on the ZIP package structure. Extensionless
non-binary files are treated as text only when they pass a conservative
text-file heuristic.
"""
from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile, ZipFile

DOCX = ".docx"
ODT = ".odt"
TEXT = ".txt"
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".text"}


def _looks_like_text(data: bytes) -> bool:
    if not data:
        return True
    sample = data[:8192]
    if b"\x00" in sample:
        return False
    # Accept common UTF-8/Windows text and legacy single-byte text.
    try:
        sample.decode("utf-8")
        return True
    except UnicodeDecodeError:
        pass
    try:
        sample.decode("cp1252")
        return True
    except UnicodeDecodeError:
        return False


def detect_file_type(path: str | Path) -> str | None:
    p = Path(path)
    ext = p.suffix.lower()
    if ext in SUPPORTED_TEXT_EXTENSIONS:
        return ext
    if ext in {DOCX, ODT}:
        return ext
    if not p.is_file():
        return None

    try:
        with ZipFile(p, "r") as z:
            names = {n.lower().lstrip("/") for n in z.namelist()}
            if "[content_types].xml" in names and "word/document.xml" in names:
                return DOCX
            if "mimetype" in names:
                try:
                    mimetype = z.read("mimetype").decode("ascii", "ignore").strip()
                except Exception:
                    mimetype = ""
                if mimetype == "application/vnd.oasis.opendocument.text":
                    return ODT
            if "content.xml" in names and any(n.startswith("meta-inf/") for n in names):
                return ODT
    except (BadZipFile, OSError, ValueError):
        pass

    try:
        with p.open("rb") as fh:
            return TEXT if _looks_like_text(fh.read(8192)) else None
    except OSError:
        return None


def output_suffix(detected_type: str | None) -> str:
    if detected_type in {DOCX, ODT, TEXT}:
        return detected_type
    return ""
