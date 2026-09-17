"""
Optional remote software-control check.

This is deliberately fail-open:
if Supabase is unavailable, the converter continues to work.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error

from .config import SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY


def get_software_control(app_version: str) -> dict | None:
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        return None

    # Read only the control row. Adjust the filter if the table
    # schema is later expanded.
    url = (
        f"{SUPABASE_URL}/rest/v1/software_control"
        "?select=status,current_version,minimum_version,message"
        "&limit=1"
    )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Authorization": f"Bearer {SUPABASE_PUBLISHABLE_KEY}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            if not 200 <= response.status < 300:
                return None

            body = response.read().decode("utf-8")
            rows = json.loads(body)

            if isinstance(rows, list) and rows:
                row = rows[0]
                return row if isinstance(row, dict) else None

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        ValueError,
    ):
        return None

    return None
