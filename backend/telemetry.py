"""
Anonymous backend communication for Hari Unicode Converter.

This module uses only Python's standard library.
No document or conversion text is sent by telemetry.
"""

from __future__ import annotations

import json
import platform
import uuid
import urllib.request
import urllib.error
from pathlib import Path

from .config import SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY


APP_DATA_DIR = Path.home() / ".hari_unicode_converter"
INSTALLATION_FILE = APP_DATA_DIR / "installation_id"


def get_installation_id() -> str:
    try:
        if INSTALLATION_FILE.exists():
            value = INSTALLATION_FILE.read_text(encoding="utf-8").strip()
            if value:
                return value

        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        installation_id = str(uuid.uuid4())
        INSTALLATION_FILE.write_text(installation_id, encoding="utf-8")
        return installation_id
    except Exception:
        return str(uuid.uuid4())


def _request(table: str, data: dict, timeout: int = 5) -> bool:
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        return False

    url = f"{SUPABASE_URL}/rest/v1/{table}"
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Authorization": f"Bearer {SUPABASE_PUBLISHABLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 300
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
    ):
        return False


def _platform_info() -> dict:
    return {
        "platform": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
    }


def register_installation(app_version: str) -> bool:
    info = _platform_info()
    data = {
        "installation_id": get_installation_id(),
        "app_version": app_version,
        "platform": info["platform"],
        "os_version": info["os_version"],
        "architecture": info["architecture"],
    }
    return _request("installations", data)


def record_usage(event_type: str, app_version: str) -> bool:
    info = _platform_info()
    data = {
        "installation_id": get_installation_id(),
        "event_type": event_type,
        "app_version": app_version,
        "platform": info["platform"],
    }
    return _request("usage_events", data)


def submit_feedback(
    source_text: str = "",
    expected_text: str = "",
    message: str = "",
    app_version: str = "",
) -> bool:
    """
    Send only the feedback the user explicitly submitted.
    This is NOT telemetry and is never sent automatically.
    """

    data = {
        "feedback_type": "conversion_report",
        "message": message,
        "hari_text": source_text,
        "unicode_text": expected_text,
        "app_version": app_version,
    }

    return _request("feedback", data, timeout=10)
