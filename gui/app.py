# ============================================================
# Gujarati Legacy Font Converter
# Modern lightweight desktop GUI
# ============================================================

import json
import os
import sys
import webbrowser
import ctypes
import threading
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# INTERNAL IMPORTS
# ============================================================

try:
    from converter.service import convert_text, convert_file, convert_folder
    from converter.font_profiles import FONT_NAMES, get_font_profile
except ImportError as exc:
    raise ImportError(
        "Unable to load the converter engine. "
        "Please run this application from the Gujarati Legacy Font Converter project."
    ) from exc

try:
    from backend.telemetry import (
        register_installation,
        record_usage,
        submit_feedback,
    )
except ImportError:
    register_installation = None
    record_usage = None
    submit_feedback = None

try:
    from backend.control import get_software_control
except ImportError:
    get_software_control = None

# ============================================================
# PUBLIC APP INFORMATION
# ============================================================

APP_TITLE = "Gujarati Legacy Font Converter"
APP_VERSION = "1.0.1"
COMPANY_NAME = "Passion Projects"
OWNER_NAME = "@vishalgujarati"
AUTHOR = f"Developed by {COMPANY_NAME}"
GITHUB_URL = "https://github.com/VishalGujarati"
GITHUB_RELEASES_URL = GITHUB_URL
SUPPORT_URL = "https://u.payu.in/srWL9ANC66kC"
WEBSITE_URL = "https://passionprojects.in/"
PROJECT_YEAR = "2026"
CONVERSION_WARNING = "Warning: Converted text may contain errors. Please verify before final use."
FEEDBACK_URL = GITHUB_URL
LOGO_PATH = PROJECT_ROOT / "assets" / "software_logo.png"

# Modern, but deliberately simple colors so Tkinter remains lightweight.
BG = "#F5F7FB"
CARD = "#FFFFFF"
TEXT = "#172033"
MUTED = "#667085"
ACCENT = "#4F46E5"
ACCENT_HOVER = "#4338CA"
TEAL = "#0F766E"
BORDER = "#D9DEEA"
INPUT_BG = "#FBFCFE"

# ============================================================
# DISPLAY FONTS
# ============================================================
# Input: bundled Hari legacy font.
# Output: prefer Lohit Gujarati, then use compatible fallbacks.
HARI_FONT_NAME = "HARI"
DEFAULT_INPUT_FONT = "Hari / Harikrishna"
UNICODE_FONT_PREFERENCE = (
    "Lohit Gujarati",
    "Shruti",
    "Noto Sans Gujarati",
    "Nirmala UI",
    "Arial Unicode MS",
)

# ============================================================
# LOCAL SETTINGS
# ============================================================

SETTINGS_DIR = Path.home() / ".hari_unicode_converter"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "font_size": 13,
    "remember_folder": True,
    "confirm_overwrite": True,
    "last_folder": "",
    "telemetry_enabled": False,
    "privacy_notice_seen": False,
}


def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    try:
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as handle:
                stored = json.load(handle)
            if isinstance(stored, dict):
                settings.update(stored)
    except Exception:
        pass
    return settings


def save_settings(settings):
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with SETTINGS_FILE.open("w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============================================================
# MAIN APPLICATION
# ============================================================

class HariUnicodeConverterApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.font_size = int(self.settings.get("font_size", 13))

        # Load bundled legacy fonts into the current Windows session.
        # This does not install them permanently for the user.
        self._font_handles = self._load_legacy_fonts()
        self._hari_font_handle = bool(self._font_handles)

        self.input_font_name = HARI_FONT_NAME
        self.unicode_font = self._find_unicode_gujarati_font()

        # Optional side-by-side comparison scrolling.
        self.compare_scroll_var = tk.BooleanVar(value=False)
        self._syncing_scroll = False

        self._app_logo = self._load_app_logo()

        self.title(APP_TITLE)

        # Identify the running application correctly in Ubuntu/Linux docks.
        # This prevents the generic Tk icon from being used for the window.
        if sys.platform.startswith("linux"):
            try:
                self.wm_class(
                    "GujaratiLegacyFontConverter",
                    "GujaratiLegacyFontConverter",
                )
            except tk.TclError:
                pass

        if self._app_logo is not None:
            try:
                self.iconphoto(True, self._app_logo)
            except tk.TclError:
                pass
        self.configure(bg=BG)
        self._set_responsive_main_geometry()

        self._configure_style()
        self._build_interface()
        self._bind_shortcuts()

        if not self.settings.get("privacy_notice_seen", False):
            self.after(150, self._show_first_run_privacy)

        self._start_telemetry()
        # Automatic remote software-control checks are disabled in the release build.
        # Updates can be checked manually when that feature is intentionally enabled.

    def _load_app_logo(self):
        """Load the product logo for the window icon and in-app branding."""
        try:
            if not LOGO_PATH.exists():
                return None
            image = tk.PhotoImage(file=str(LOGO_PATH))
            # Keep the large source file intact while using a lightweight
            # display-sized copy for Tkinter.
            factor = max(1, image.width() // 96)
            if factor > 1:
                image = image.subsample(factor, factor)
            return image
        except Exception:
            return None

    # ========================================================
    # OPTIONAL ANONYMOUS TELEMETRY
    # ========================================================

    def _start_telemetry(self):
        if not self.settings.get("telemetry_enabled", True):
            return
        if register_installation is None:
            return
        threading.Thread(
            target=self._register_installation_background,
            daemon=True,
        ).start()

    def _register_installation_background(self):
        try:
            register_installation(APP_VERSION)
        except Exception:
            pass

    def _record_usage_background(self, event_type):
        if not self.settings.get("telemetry_enabled", True):
            return
        if record_usage is None:
            return
        threading.Thread(
            target=self._record_usage_worker,
            args=(event_type,),
            daemon=True,
        ).start()

    @staticmethod
    def _record_usage_worker(event_type):
        try:
            record_usage(event_type, APP_VERSION)
        except Exception:
            pass

    # ========================================================
    # SOFTWARE CONTROL
    # ========================================================

    def _start_software_control_check(self):
        if get_software_control is None:
            return
        threading.Thread(
            target=self._software_control_worker,
            daemon=True,
        ).start()

    def _software_control_worker(self):
        try:
            control = get_software_control(APP_VERSION)
            if not control:
                return

            status = str(control.get("status", "active")).lower()
            latest_version = str(control.get("latest_version", "") or "").strip()
            minimum_version = str(control.get("minimum_version", "") or "").strip()
            message = str(control.get("message", "") or "").strip()
            release_notes = str(control.get("release_notes", "") or "").strip()
            download_url = str(control.get("download_url", "") or "").strip()

            # Fail-open: no server response / malformed response
            # must never stop the offline converter.
            if status == "discontinued":
                notice = message or "This software has been discontinued."
                self.after(
                    0,
                    lambda: self._show_software_notice(
                        "Software Notice",
                        notice,
                        True,
                    ),
                )
                return

            if status == "maintenance":
                notice = message or "This software is currently under maintenance."
                self.after(
                    0,
                    lambda: self._show_software_notice(
                        "Software Notice",
                        notice,
                        False,
                    ),
                )
                return

            # Notify the user when a newer release exists.
            # This is informational only. The converter remains usable.
            if latest_version and self._version_is_newer(latest_version, APP_VERSION):
                self.after(
                    0,
                    lambda: self._show_update_notice(
                        latest_version,
                        release_notes,
                        download_url,
                    ),
                )
                return

            # If the admin sets a minimum version but does not provide a
            # newer-version field, show a warning. This never blocks conversion.
            if minimum_version and self._version_is_newer(minimum_version, APP_VERSION):
                self.after(
                    0,
                    lambda: self._show_minimum_version_notice(
                        minimum_version,
                        minimum_version,
                        download_url,
                    ),
                )
        except Exception:
            # Never let telemetry/control failures affect conversion.
            pass

    def _check_for_updates_manual(self):
        """Check the Supabase software-control record without blocking the GUI."""
        button = getattr(self, "update_button", None)
        if button is not None:
            button.configure(state="disabled", text="Checking…")
        threading.Thread(
            target=self._manual_update_worker,
            daemon=True,
        ).start()

    def _manual_update_worker(self):
        try:
            if get_software_control is None:
                self.after(0, lambda: self._manual_update_result(False, "Update service is unavailable right now."))
                return

            control = get_software_control(APP_VERSION)
            if not control:
                self.after(0, lambda: self._manual_update_result(False, "Could not reach the update service."))
                return

            status = str(control.get("status", "active")).lower()
            latest_version = str(control.get("latest_version", "") or "").strip()
            release_notes = str(control.get("release_notes", "") or "").strip()
            download_url = str(control.get("download_url", "") or "").strip()

            if status == "maintenance":
                self.after(0, lambda: self._manual_update_result(False, "The update service is currently under maintenance."))
                return

            if status == "discontinued":
                self.after(0, lambda: self._manual_update_result(False, "This software has been discontinued."))
                return

            if latest_version and self._version_is_newer(latest_version, APP_VERSION):
                self.after(
                    0,
                    lambda: self._show_update_notice(latest_version, release_notes, download_url),
                )
                self.after(0, self._reset_update_button)
                return

            self.after(0, lambda: self._manual_update_result(True, f"You are using the latest version ({APP_VERSION})."))
        except Exception:
            self.after(0, lambda: self._manual_update_result(False, "Could not check for updates right now."))

    def _manual_update_result(self, success, message):
        self._reset_update_button()
        window = tk.Toplevel(self)
        window.title("Check for Updates")
        window.transient(self)
        window.grab_set()
        window.resizable(False, False)
        window.configure(bg=BG)

        frame = tk.Frame(window, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame, text="No update available" if success else "Update check",
            bg=CARD, fg=TEAL if success else TEXT,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=22, pady=(20, 8))
        tk.Label(
            frame, text=message, bg=CARD, fg=MUTED,
            font=("Segoe UI", 10), wraplength=440, justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 18))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", padx=22, pady=(0, 20))
        ttk.Button(
            buttons, text="View GitHub Releases", style="Secondary.TButton",
            command=lambda: self._open_url(GITHUB_RELEASES_URL),
        ).pack(side="right")
        ttk.Button(
            buttons, text="Close", style="Accent.TButton",
            command=window.destroy,
        ).pack(side="right", padx=(0, 8))

        self._center_window(window, 500, 220)

    def _reset_update_button(self):
        button = getattr(self, "update_button", None)
        if button is not None:
            button.configure(state="normal", text="↻ Check for Updates")

    @staticmethod
    def _version_tuple(version):
        try:
            parts = []
            for part in str(version).strip().lstrip("vV").split("."):
                digits = "".join(ch for ch in part if ch.isdigit())
                parts.append(int(digits or "0"))
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts[:3])
        except Exception:
            return (0, 0, 0)

    @classmethod
    def _version_is_newer(cls, candidate, current):
        return cls._version_tuple(candidate) > cls._version_tuple(current)

    def _show_update_notice(self, latest_version, release_notes, download_url):
        window = tk.Toplevel(self)
        window.title("Update Available")
        window.transient(self)
        window.grab_set()
        window.resizable(False, False)
        window.configure(bg=BG)

        frame = tk.Frame(window, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="A new version is available",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=22, pady=(20, 5))

        tk.Label(
            frame,
            text=f"Current version: {APP_VERSION}\nLatest version: {latest_version}",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 14))

        if release_notes:
            tk.Label(
                frame,
                text="What's new",
                bg=CARD,
                fg=TEXT,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", padx=22, pady=(0, 5))

            notes = tk.Text(
                frame,
                height=6,
                width=58,
                wrap="word",
                bg=INPUT_BG,
                fg=TEXT,
                relief="flat",
                borderwidth=0,
                padx=10,
                pady=8,
            )
            notes.insert("1.0", release_notes)
            notes.configure(state="disabled")
            notes.pack(fill="both", padx=22, pady=(0, 16))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", padx=22, pady=(0, 20))

        if download_url:
            ttk.Button(
                buttons,
                text="Download Update",
                style="Accent.TButton",
                command=lambda: self._open_url(download_url),
            ).pack(side="right")

        ttk.Button(
            buttons,
            text="Later",
            style="Secondary.TButton",
            command=window.destroy,
        ).pack(side="right", padx=(0, 8))

        self._center_window(window, 500, 390 if release_notes else 300)

    def _show_minimum_version_notice(self, minimum_version, latest_version, download_url):
        message = (
            f"Your version ({APP_VERSION}) is older than the minimum supported "
            f"version ({minimum_version}).\n\n"
            f"Please update to version {latest_version} when convenient."
        )

        if download_url:
            answer = messagebox.askyesno(
                "Update Recommended",
                message + "\n\nOpen the download page now?",
                parent=self,
            )
            if answer:
                self._open_url(download_url)
        else:
            messagebox.showwarning("Update Recommended", message, parent=self)

    def _show_software_notice(self, title, message, blocking=False):
        # "blocking" is intentionally informational only.
        # The converter remains usable even if the backend says
        # discontinued. This prevents a server outage from killing
        # an offline installation.
        messagebox.showinfo(title, message, parent=self)

    # ========================================================
    # FEEDBACK
    # ========================================================

    def _show_feedback(self):
        window = tk.Toplevel(self)
        window.title("Feedback / Report Conversion")
        window.transient(self)
        window.grab_set()
        window.resizable(False, False)
        window.configure(bg=BG)

        frame = tk.Frame(
            window,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(
            frame,
            text="Feedback / Report Conversion",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ttk.Label(
            frame,
            text=(
                "Help improve the converter by reporting a wrong or missing mapping. "
                "Only submit text you choose to send."
            ),
            style="CardMuted.TLabel",
            wraplength=520,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        ttk.Label(
            frame,
            text="Legacy text (optional)",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=20)

        source_box = tk.Text(
            frame,
            height=4,
            width=64,
            font=(self.input_font_name, self.font_size),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            padx=8,
            pady=8,
        )
        source_box.pack(fill="x", padx=20, pady=(5, 10))

        # Prefill the current source text, but do not send it automatically.
        source_text = self.input_text.get("1.0", "end-1c")
        if source_text:
            source_box.insert("1.0", source_text[:5000])

        ttk.Label(
            frame,
            text="Expected Unicode Gujarati (optional)",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=20)

        expected_box = tk.Text(
            frame,
            height=4,
            width=64,
            font=(self.unicode_font, self.font_size),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            padx=8,
            pady=8,
        )
        expected_box.pack(fill="x", padx=20, pady=(5, 10))

        current_result = self.output_text.get("1.0", "end-1c")
        if current_result:
            expected_box.insert("1.0", current_result[:5000])

        ttk.Label(
            frame,
            text="Additional message (optional)",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=20)

        message_box = tk.Text(
            frame,
            height=3,
            width=64,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            padx=8,
            pady=8,
        )
        message_box.pack(fill="x", padx=20, pady=(5, 5))

        ttk.Label(
            frame,
            text=(
                "Privacy: feedback is sent to the project only when you press Submit. "
                "Do not include personal or confidential information."
            ),
            style="CardMuted.TLabel",
            wraplength=520,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", padx=20, pady=(4, 18))

        ttk.Button(
            buttons,
            text="Cancel",
            style="Secondary.TButton",
            command=window.destroy,
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            buttons,
            text="Submit Feedback",
            style="Accent.TButton",
            command=lambda: self._submit_feedback_window(
                window,
                source_box,
                expected_box,
                message_box,
            ),
        ).pack(side="right")

        self._center_window(window, 600, 650)

    def _submit_feedback_window(
        self,
        window,
        source_box,
        expected_box,
        message_box,
    ):
        if submit_feedback is None:
            messagebox.showerror(
                "Feedback Unavailable",
                "The feedback service is currently unavailable.",
                parent=window,
            )
            return

        source = source_box.get("1.0", "end-1c").strip()
        expected = expected_box.get("1.0", "end-1c").strip()
        message = message_box.get("1.0", "end-1c").strip()

        if not source and not expected and not message:
            messagebox.showwarning(
                "No Feedback",
                "Please enter some feedback before submitting.",
                parent=window,
            )
            return

        # Feedback is deliberately sent in the background so a slow
        # internet connection never freezes the converter.
        threading.Thread(
            target=self._submit_feedback_worker,
            args=(source[:5000], expected[:5000], message[:3000], window),
            daemon=True,
        ).start()

        messagebox.showinfo(
            "Feedback",
            "Thank you. Your feedback is being submitted.",
            parent=window,
        )
        window.destroy()

    @staticmethod
    def _submit_feedback_worker(source, expected, message, window):
        try:
            submit_feedback(
                source_text=source,
                expected_text=expected,
                message=message,
                app_version=APP_VERSION,
            )
        except Exception:
            pass

    # ========================================================
    # STYLE
    # ========================================================

    def _load_legacy_fonts(self):
        """
        Load the bundled legacy fonts privately on Windows.

        The font files are only registered for this application
        session. They are never installed permanently.
        """
        if not sys.platform.startswith("win"):
            return []

        font_files = [
            PROJECT_ROOT / "assets" / "hari.ttf",
            PROJECT_ROOT / "assets" / "LMG-Arun.ttf",
            PROJECT_ROOT / "assets" / "Lohit BKMAN.ttf",
        ]

        handles = []

        try:
            FR_PRIVATE = 0x10

            for font_path in font_files:
                if not font_path.exists():
                    continue

                result = ctypes.windll.gdi32.AddFontResourceExW(
                    str(font_path),
                    FR_PRIVATE,
                    0,
                )

                if result:
                    handles.append(font_path)

        except Exception:
            pass

        return handles

    def _font_display_name(self, font_name):
        profile = get_font_profile(font_name)
        return profile["display_font"]

    def _font_changed(self, event=None):
        selected = self.font_var.get().strip()

        try:
            profile = get_font_profile(selected)
        except ValueError:
            selected = DEFAULT_INPUT_FONT
            self.font_var.set(selected)
            profile = get_font_profile(selected)

        self.input_font_name = profile["display_font"]

        if hasattr(self, "input_text"):
            self.input_text.configure(
                font=(self.input_font_name, self.font_size)
            )

        self.status_var.set(
            f"Input font: {selected}"
        )

    def _find_unicode_gujarati_font(self):
        """Choose the best installed Unicode Gujarati display font."""
        try:
            available = {name.lower(): name for name in tkfont.families(self)}
        except tk.TclError:
            available = {}

        for font_name in UNICODE_FONT_PREFERENCE:
            if font_name.lower() in available:
                return available[font_name.lower()]

        return "TkDefaultFont"

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Give the native ttk combobox popup a cleaner, modern appearance on Windows.
        self.option_add("*TCombobox*Listbox.background", CARD)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", "white")
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))
        self.option_add("*TCombobox*Listbox.borderWidth", 0)

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure(
            "TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Muted.TLabel",
            background=BG,
            foreground=MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Title.TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 21, "bold"),
        )
        style.configure(
            "Author.TLabel",
            background=BG,
            foreground=ACCENT,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Privacy.TLabel",
            background=BG,
            foreground=TEAL,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Warning.TLabel",
            background="#FFFBEB",
            foreground="#92400E",
            font=("Segoe UI", 8),
        )
        style.configure(
            "BrandFooter.TLabel",
            background=BG,
            foreground=MUTED,
            font=("Segoe UI", 8),
        )
        style.configure(
            "Identity.TLabel",
            background=BG,
            foreground=ACCENT,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Link.TLabel",
            background=CARD,
            foreground=ACCENT,
            font=("Segoe UI", 9, "underline"),
        )
        style.configure(
            "Modern.TCombobox",
            fieldbackground=INPUT_BG,
            foreground=TEXT,
            background=CARD,
            bordercolor=BORDER,
            lightcolor=ACCENT,
            darkcolor=BORDER,
            padding=(12, 9),
            arrowsize=18,
            borderwidth=1,
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", INPUT_BG), ("focus", "#EEF2FF")],
            foreground=[("readonly", TEXT)],
            bordercolor=[("focus", ACCENT)],
            lightcolor=[("focus", ACCENT)],
            darkcolor=[("focus", ACCENT)],
        )
        style.configure(
            "CardTitle.TLabel",
            background=CARD,
            foreground=TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "CardMuted.TLabel",
            background=CARD,
            foreground=MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "TNotebook",
            background=BG,
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            padding=(18, 9),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", CARD)],
            foreground=[("selected", ACCENT), ("!selected", MUTED)],
        )
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="white",
            borderwidth=0,
            padding=(18, 9),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER)],
            foreground=[("disabled", "#D0D5DD"), ("!disabled", "white")],
        )
        style.configure(
            "Secondary.TButton",
            background=CARD,
            foreground=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=(15, 8),
            font=("Segoe UI", 10),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#EEF2FF")],
            foreground=[("active", ACCENT)],
        )
        style.configure(
            "TEntry",
            fieldbackground=CARD,
            foreground=TEXT,
            bordercolor=BORDER,
            padding=7,
        )
        style.configure(
            "Horizontal.TProgressbar",
            background=ACCENT,
            troughcolor="#E6E9F2",
            borderwidth=0,
        )

    # ========================================================
    # INTERFACE
    # ========================================================

    def _build_interface(self):
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=24, pady=(18, 12))

        left = ttk.Frame(header)
        left.pack(side="left", fill="x", expand=True)

        title_row = ttk.Frame(left)
        title_row.pack(anchor="w", fill="x")
        title_text = ttk.Frame(title_row)
        title_text.pack(side="left", fill="x", expand=True)
        ttk.Label(title_text, text=APP_TITLE, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_text,
            text="Convert Hari / Harikrishna and LMG Arun / Lohit BKMAN to Unicode Gujarati",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 0))
        ttk.Label(
            title_text,
            text="Free - Local - Privacy-focused  - Made for Gujarati users",
            style="Identity.TLabel",
        ).pack(anchor="w", pady=(5, 0))
        ttk.Label(
            left,
            text="Your documents stay on your computer. Text and files are never uploaded.",
            style="Privacy.TLabel",
        ).pack(anchor="w", pady=(7, 0))

        right = ttk.Frame(header)
        right.pack(side="right", anchor="n")
        self.update_button = ttk.Button(
            right,
            text="Check for Updates",
            style="Secondary.TButton",
            command=self._check_for_updates_manual,
        )
        self.update_button.pack(side="left", padx=(0, 7))
        ttk.Button(
            right, text="Settings", style="Secondary.TButton", command=self._show_settings
        ).pack(side="left", padx=(0, 7))
        ttk.Button(
            right, text="About", style="Secondary.TButton", command=self._show_about
        ).pack(side="left", padx=(0, 7))
        ttk.Button(
            right,
            text="Feedback",
            style="Secondary.TButton",
            command=self._show_feedback,
        ).pack(side="left", padx=(0, 7))
        ttk.Button(
            right,
            text="Support",
            style="Accent.TButton",
            command=lambda: self._open_url(SUPPORT_URL),
        ).pack(side="left")

        # Main notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.text_tab = ttk.Frame(notebook, padding=16)
        self.file_tab = ttk.Frame(notebook, padding=16)
        self.folder_tab = ttk.Frame(notebook, padding=16)

        notebook.add(self.text_tab, text="Text")
        notebook.add(self.file_tab, text="File")
        notebook.add(self.folder_tab, text="Folder")

        self._build_text_tab()
        self._build_file_tab()
        self._build_folder_tab()

        # Footer
        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=24, pady=(0, 16))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(footer, textvariable=self.status_var, style="Muted.TLabel").pack(side="left")
        ttk.Label(
            footer,
            text="Local conversion - Your document text and files stay on your computer and are never uploaded.",
            style="Muted.TLabel",
        ).pack(side="right")

    def _card(self, parent):
        frame = tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
        )
        return frame

    # ========================================================
    # SHARED CONVERSION NOTICE
    # ========================================================

    def _add_conversion_notice(self, parent):
        """Add a compact verification reminder to conversion pages."""
        notice = tk.Frame(
            parent,
            bg="#FFFBEB",
            highlightbackground="#FDE68A",
            highlightthickness=1,
            bd=0,
        )
        notice.pack(fill="x", pady=(8, 0))

        ttk.Label(
            notice,
            text=CONVERSION_WARNING,
            style="Warning.TLabel",
            anchor="center",
            justify="center",
            wraplength=900,
        ).pack(fill="x", padx=10, pady=(7, 7))

        ttk.Label(
            parent,
            text=f"Developed by Passion Projects - {PROJECT_YEAR}",
            style="BrandFooter.TLabel",
            anchor="center",
        ).pack(fill="x", pady=(5, 0))

    # ========================================================
    # TEXT TAB
    # ========================================================

    def _build_text_tab(self):
        ttk.Label(
            self.text_tab,
            text="Select the legacy Gujarati font, paste the text, and convert it to Unicode.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        font_row = ttk.Frame(self.text_tab)
        font_row.pack(fill="x", pady=(0, 8))

        ttk.Label(
            font_row,
            text="Input font:",
            style="CardTitle.TLabel",
        ).pack(side="left", padx=(0, 8))

        self.font_var = tk.StringVar(value=DEFAULT_INPUT_FONT)

        self.font_combo = ttk.Combobox(
            font_row,
            textvariable=self.font_var,
            values=FONT_NAMES,
            state="readonly",
            width=28,
            style="Modern.TCombobox",
        )
        self.font_combo.pack(side="left")
        self.font_combo.bind("<<ComboboxSelected>>", self._font_changed)

        # --------------------------------------------------------
        # ACTIONS
        # --------------------------------------------------------

        actions = ttk.Frame(self.text_tab)
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(
            actions,
            text="Convert",
            style="Accent.TButton",
            command=self._convert_text,
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Clear",
            style="Secondary.TButton",
            command=self._clear_text,
        ).pack(side="left", padx=(8, 0))

        self.copy_button = ttk.Button(
            actions,
            text="Copy Result",
            style="Secondary.TButton",
            command=self._copy_result,
        )
        self.copy_button.pack(side="left", padx=(8, 0))

        ttk.Button(
            actions,
            text="Paste",
            style="Secondary.TButton",
            command=self._paste_input,
        ).pack(side="left", padx=(8, 0))

        # Optional compare mode: scroll either editor and the other
        # editor follows at the same relative vertical position.
        self.compare_toggle = tk.Checkbutton(
            actions,
            text="Sync scroll  OFF",
            variable=self.compare_scroll_var,
            command=self._compare_scroll_changed,
            indicatoron=False,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
            cursor="hand2",
        )
        self.compare_toggle.pack(side="right", padx=(8, 0))
        self._refresh_compare_toggle()

        # --------------------------------------------------------
        # TWO FIXED-SIZE EDITOR PANES
        # --------------------------------------------------------
        #
        # Both panes always occupy the same layout-controlled area.
        # Text length never changes the size of either editor.
        # The main window itself remains resizable for different
        # screen resolutions.
        #

        editors = ttk.Frame(self.text_tab)
        editors.pack(fill="both", expand=True)
        editors.columnconfigure(0, weight=1, uniform="editor")
        editors.columnconfigure(1, weight=1, uniform="editor")
        editors.rowconfigure(0, weight=1)

        input_card = self._card(editors)
        input_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
        )

        output_card = self._card(editors)
        output_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
        )

        # --------------------------------------------------------
        # INPUT
        # --------------------------------------------------------

        ttk.Label(
            input_card,
            text="Legacy Gujarati",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ttk.Label(
            input_card,
            text="Source text",
            style="CardMuted.TLabel",
        ).pack(anchor="w", padx=12, pady=(0, 7))

        input_body = tk.Frame(input_card, bg=CARD)
        input_body.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 8),
        )

        input_editor = tk.Frame(input_body, bg=CARD)
        input_editor.pack(fill="both", expand=True)
        input_editor.grid_rowconfigure(0, weight=1)
        input_editor.grid_columnconfigure(0, weight=1)

        self.input_text = tk.Text(
            input_editor,
            wrap="word",
            undo=True,
            font=(self.input_font_name, self.font_size),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            spacing1=0,
            spacing2=0,
            spacing3=0,
        )
        self.input_text.grid(row=0, column=0, sticky="nsew")

        self.input_scrollbar = ttk.Scrollbar(
            input_editor,
            orient="vertical",
            command=lambda *args: self._scroll_editor(
                self.input_text, *args
            ),
        )
        self.input_scrollbar.grid(row=0, column=1, sticky="ns")

        self.input_text.configure(
            yscrollcommand=lambda first, last: self._editor_yset(
                "input", first, last
            )
        )

        # --------------------------------------------------------
        # OUTPUT
        # --------------------------------------------------------

        ttk.Label(
            output_card,
            text="Unicode Gujarati",
            style="CardTitle.TLabel",
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ttk.Label(
            output_card,
            text="Converted result",
            style="CardMuted.TLabel",
        ).pack(anchor="w", padx=12, pady=(0, 7))

        output_body = tk.Frame(output_card, bg=CARD)
        output_body.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 8),
        )

        output_editor = tk.Frame(output_body, bg=CARD)
        output_editor.pack(fill="both", expand=True)
        output_editor.grid_rowconfigure(0, weight=1)
        output_editor.grid_columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_editor,
            wrap="word",
            undo=False,
            font=(self.unicode_font, self.font_size),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            spacing1=0,
            spacing2=0,
            spacing3=0,
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        self.output_scrollbar = ttk.Scrollbar(
            output_editor,
            orient="vertical",
            command=lambda *args: self._scroll_editor(
                self.output_text, *args
            ),
        )
        self.output_scrollbar.grid(row=0, column=1, sticky="ns")

        self.output_text.configure(
            yscrollcommand=lambda first, last: self._editor_yset(
                "output", first, last
            )
        )

        # The result is deliberately read-only. This also avoids the
        # insertion caret appearing inside a Gujarati grapheme cluster,
        # which can make a correctly stored Unicode word look visually
        # broken while the caret is positioned inside it.
        self.output_text.configure(state="disabled")

        self.input_count_var = tk.StringVar(value="0 characters")
        ttk.Label(
            input_card,
            textvariable=self.input_count_var,
            style="CardMuted.TLabel",
        ).pack(anchor="e", padx=12, pady=(0, 10))

        self.output_count_var = tk.StringVar(value="0 characters")
        ttk.Label(
            output_card,
            textvariable=self.output_count_var,
            style="CardMuted.TLabel",
        ).pack(anchor="e", padx=12, pady=(0, 10))

        self.input_text.bind("<KeyRelease>", self._update_counts)

        # Mouse wheel support on both editors.
        for widget in (self.input_text, self.output_text):
            widget.bind(
                "<MouseWheel>",
                self._mousewheel_scroll,
                add="+",
            )
            # Linux/X11
            widget.bind(
                "<Button-4>",
                self._mousewheel_scroll,
                add="+",
            )
            widget.bind(
                "<Button-5>",
                self._mousewheel_scroll,
                add="+",
            )

        self._add_conversion_notice(self.text_tab)

    # ========================================================
    # EDITOR SCROLLING / COMPARISON
    # ========================================================

    def _compare_scroll_changed(self):
        self._refresh_compare_toggle()

        if self.compare_scroll_var.get():
            try:
                first = self.input_text.yview()[0]
                self._set_both_editor_positions(first)
            except tk.TclError:
                pass
            self.status_var.set("Sync scroll enabled.")
        else:
            self.status_var.set("Sync scroll disabled.")

    def _refresh_compare_toggle(self):
        if not hasattr(self, "compare_toggle"):
            return

        enabled = bool(self.compare_scroll_var.get())

        self.compare_toggle.configure(
            text="Sync scroll  ON" if enabled else "Sync scroll  OFF",
            bg=ACCENT if enabled else "#E9EDF5",
            fg="white" if enabled else MUTED,
            activebackground=ACCENT_HOVER if enabled else "#DDE3EE",
            activeforeground="white" if enabled else TEXT,
            selectcolor=ACCENT,
        )

    def _editor_yset(self, editor_name, first, last):
        scrollbar = (
            self.input_scrollbar
            if editor_name == "input"
            else self.output_scrollbar
        )
        scrollbar.set(first, last)

        if (
            not self.compare_scroll_var.get()
            or self._syncing_scroll
        ):
            return

        try:
            self._syncing_scroll = True

            other = (
                self.output_text
                if editor_name == "input"
                else self.input_text
            )
            other.yview_moveto(first)

            other_scrollbar = (
                self.output_scrollbar
                if editor_name == "input"
                else self.input_scrollbar
            )
            other_first, other_last = other.yview()
            other_scrollbar.set(other_first, other_last)

        finally:
            self._syncing_scroll = False

    def _scroll_editor(self, editor, *args):
        try:
            self._syncing_scroll = True
            editor.yview(*args)

            if self.compare_scroll_var.get():
                first = editor.yview()[0]
                other = (
                    self.output_text
                    if editor is self.input_text
                    else self.input_text
                )
                other.yview_moveto(first)
        finally:
            self._syncing_scroll = False

    def _set_both_editor_positions(self, fraction):
        try:
            self._syncing_scroll = True
            self.input_text.yview_moveto(fraction)
            self.output_text.yview_moveto(fraction)
        finally:
            self._syncing_scroll = False

    def _mousewheel_scroll(self, event):
        if getattr(event, "num", None) == 4:
            units = -3
        elif getattr(event, "num", None) == 5:
            units = 3
        else:
            delta = getattr(event, "delta", 0)

            if sys.platform == "darwin":
                units = -int(delta)
            else:
                units = -int(delta / 120)
                if units == 0 and delta:
                    units = -1 if delta > 0 else 1

        if self.compare_scroll_var.get():
            try:
                self._syncing_scroll = True
                self.input_text.yview_scroll(units, "units")
                first = self.input_text.yview()[0]
                self.output_text.yview_moveto(first)
            finally:
                self._syncing_scroll = False
        else:
            try:
                event.widget.yview_scroll(units, "units")
            except tk.TclError:
                return

        return "break"

    # ========================================================
    # FILE TAB
    # ========================================================

    def _build_file_tab(self):
        ttk.Label(
            self.file_tab,
            text="Convert a single legacy Gujarati file without modifying the source file. Supported: TXT, DOCX and ODT.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        file_font_row = ttk.Frame(self.file_tab)
        file_font_row.pack(fill="x", pady=(0, 10))

        ttk.Label(
            file_font_row,
            text="Input font:",
            style="CardTitle.TLabel",
        ).pack(side="left", padx=(0, 8))

        file_font_combo = ttk.Combobox(
            file_font_row,
            textvariable=self.font_var,
            values=FONT_NAMES,
            state="readonly",
            width=28,
            style="Modern.TCombobox",
        )
        file_font_combo.pack(side="left")
        file_font_combo.bind("<<ComboboxSelected>>", self._font_changed)

        card = self._card(self.file_tab)
        card.pack(fill="x")

        ttk.Label(card, text="Input file", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 5))
        input_row = ttk.Frame(card)
        input_row.pack(fill="x", padx=14, pady=(0, 12))
        self.file_input_var = tk.StringVar()
        ttk.Entry(input_row, textvariable=self.file_input_var).pack(side="left", fill="x", expand=True)
        ttk.Button(input_row, text="Browse", style="Secondary.TButton", command=self._browse_file).pack(side="left", padx=(8, 0))

        ttk.Label(card, text="Output file", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(4, 5))
        output_row = ttk.Frame(card)
        output_row.pack(fill="x", padx=14, pady=(0, 12))
        self.file_output_var = tk.StringVar()
        ttk.Entry(output_row, textvariable=self.file_output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(output_row, text="Choose", style="Secondary.TButton", command=self._browse_output_file).pack(side="left", padx=(8, 0))

        self.file_overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(card, text="Allow overwrite of existing output", variable=self.file_overwrite_var).pack(anchor="w", padx=14, pady=(0, 14))

        actions = ttk.Frame(self.file_tab)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Convert File", style="Accent.TButton", command=self._convert_file).pack(side="left")
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self._clear_file).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Open Output Folder", style="Secondary.TButton", command=self._open_file_output_folder).pack(side="left", padx=(8, 0))

        self.file_result_var = tk.StringVar(value="")
        ttk.Label(self.file_tab, textvariable=self.file_result_var, style="Muted.TLabel", wraplength=900).pack(anchor="w", pady=(14, 0))

        self._add_conversion_notice(self.file_tab)

    # ========================================================
    # FOLDER TAB
    # ========================================================

    def _build_folder_tab(self):
        ttk.Label(
            self.folder_tab,
            text="Convert supported legacy Gujarati files in a folder. Supported: TXT, DOCX and ODT. Source files are never modified.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        folder_font_row = ttk.Frame(self.folder_tab)
        folder_font_row.pack(fill="x", pady=(0, 10))

        ttk.Label(
            folder_font_row,
            text="Input font:",
            style="CardTitle.TLabel",
        ).pack(side="left", padx=(0, 8))

        folder_font_combo = ttk.Combobox(
            folder_font_row,
            textvariable=self.font_var,
            values=FONT_NAMES,
            state="readonly",
            width=28,
            style="Modern.TCombobox",
        )
        folder_font_combo.pack(side="left")
        folder_font_combo.bind("<<ComboboxSelected>>", self._font_changed)

        card = self._card(self.folder_tab)
        card.pack(fill="x")

        ttk.Label(card, text="Input folder", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 5))
        input_row = ttk.Frame(card)
        input_row.pack(fill="x", padx=14, pady=(0, 12))
        self.folder_input_var = tk.StringVar(value=self.settings.get("last_folder", ""))
        ttk.Entry(input_row, textvariable=self.folder_input_var).pack(side="left", fill="x", expand=True)
        ttk.Button(input_row, text="Browse", style="Secondary.TButton", command=self._browse_folder).pack(side="left", padx=(8, 0))

        ttk.Label(card, text="Output folder", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(4, 5))
        output_row = ttk.Frame(card)
        output_row.pack(fill="x", padx=14, pady=(0, 12))
        self.folder_output_var = tk.StringVar()
        ttk.Entry(output_row, textvariable=self.folder_output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(output_row, text="Choose", style="Secondary.TButton", command=self._browse_output_folder).pack(side="left", padx=(8, 0))

        self.folder_overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(card, text="Allow overwrite of existing output files", variable=self.folder_overwrite_var).pack(anchor="w", padx=14, pady=(0, 14))

        actions = ttk.Frame(self.folder_tab)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Convert Folder", style="Accent.TButton", command=self._convert_folder).pack(side="left")
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self._clear_folder).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Open Output Folder", style="Secondary.TButton", command=self._open_folder_output_folder).pack(side="left", padx=(8, 0))

        self.progress = ttk.Progressbar(self.folder_tab, mode="indeterminate")
        self.progress.pack(fill="x", pady=(16, 0))

        self.folder_result_var = tk.StringVar(value="")
        ttk.Label(self.folder_tab, textvariable=self.folder_result_var, style="Muted.TLabel", wraplength=900).pack(anchor="w", pady=(12, 0))

        self._add_conversion_notice(self.folder_tab)

    # ========================================================
    # SHORTCUTS / COUNTS
    # ========================================================

    def _bind_shortcuts(self):
        self.bind_all("<Control-Return>", lambda event: self._convert_text())
        self.bind_all("<Control-l>", lambda event: self._clear_text())
        self.bind_all("<Control-L>", lambda event: self._clear_text())
        self.bind_all("<Control-Shift-V>", lambda event: self._paste_input())

    def _update_counts(self, event=None):
        source = self.input_text.get("1.0", "end-1c")
        result = self.output_text.get("1.0", "end-1c")
        self.input_count_var.set(f"{len(source):,} characters")
        self.output_count_var.set(f"{len(result):,} characters")

    # ========================================================
    # TEXT ACTIONS
    # ========================================================

    def _convert_text(self):
        source = self.input_text.get("1.0", "end-1c")
        if not source:
            messagebox.showwarning("No Text", "Please enter legacy Gujarati text first.", parent=self)
            return

        self.status_var.set("Converting text...")
        self.update_idletasks()
        try:
            result = convert_text(
                source,
                font=self.font_var.get(),
            )
        except Exception as exc:
            self.status_var.set("Conversion failed.")
            messagebox.showerror(
                "Conversion Error",
                f"{type(exc).__name__}: {exc}",
                parent=self,
            )
            return

        if result.success:
            converted = result.data["output_text"]

            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", converted)
            self.output_text.configure(state="disabled")

            self._update_counts()
            self.input_text.yview_moveto(0.0)
            self.output_text.yview_moveto(0.0)
            self.status_var.set("Text converted successfully.")
            self._record_usage_background("text_conversion")
        else:
            self.status_var.set("Conversion failed.")
            self._show_error(result)

    def _clear_text(self):
        self.input_text.delete("1.0", "end")

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

        self._update_counts()
        self.input_text.yview_moveto(0.0)
        self.output_text.yview_moveto(0.0)
        self.status_var.set("Ready")

    def _copy_result(self):
        result = self.output_text.get("1.0", "end-1c")

        if not result:
            messagebox.showinfo(
                "No Result",
                "There is no converted text to copy.",
                parent=self,
            )
            return

        self.clipboard_clear()
        self.clipboard_append(result)
        self.update()

        self.status_var.set("Unicode result copied to clipboard.")

        # Give clear feedback and prevent repeated clicks for 3 seconds.
        self.copy_button.config(
            text="✓ Unicode Copied",
            state="disabled",
        )
        self.after(3000, self._reset_copy_button)

    def _reset_copy_button(self):
        self.copy_button.config(
            text="Copy Result",
            state="normal",
        )

    def _paste_input(self):
        try:
            value = self.clipboard_get()
        except tk.TclError:
            return
        self.input_text.insert("insert", value)
        self._update_counts()

    # ========================================================
    # FILE ACTIONS
    # ========================================================

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Legacy Gujarati File",
            filetypes=[("All files", "*.*"), ("Supported files", "*.txt *.text *.docx *.odt"), ("Text files", "*.txt *.text"), ("Word documents", "*.docx"), ("OpenDocument", "*.odt")],
            parent=self,
        )
        if not path:
            return
        self.file_input_var.set(path)
        source = Path(path)
        
        try:
            from converter.file_type import detect_file_type
            detected = detect_file_type(source)
        except Exception:
            detected = None
        output_suffix = detected or source.suffix or ".txt"
        self.file_output_var.set(str(source.parent / f"{source.stem}_unicode{output_suffix}"))

    def _browse_output_file(self):
        path = filedialog.asksaveasfilename(
            title="Choose Unicode Output File",
            defaultextension=".txt",
            filetypes=[("Supported files", "*.txt *.text *.docx *.odt"), ("Text files", "*.txt"), ("Word documents", "*.docx"), ("OpenDocument", "*.odt"), ("All files", "*.*")],
            parent=self,
        )
        if path:
            self.file_output_var.set(path)

    def _convert_file(self):
        input_path = self.file_input_var.get().strip()
        output_path = self.file_output_var.get().strip()

        if not input_path:
            messagebox.showwarning("No Input File", "Please select an input file.", parent=self)
            return
        if not output_path:
            messagebox.showwarning("No Output File", "Please choose an output file.", parent=self)
            return

        if self._should_confirm_overwrite(output_path, self.file_overwrite_var.get()):
            return

        self.status_var.set("Converting file...")
        self.update_idletasks()
        try:
            result = convert_file(
                input_path,
                output_path,
                overwrite=self.file_overwrite_var.get(),
                font=self.font_var.get(),
            )
        except Exception as exc:
            self.status_var.set("File conversion failed.")
            messagebox.showerror(
                "Conversion Error",
                f"{type(exc).__name__}: {exc}",
                parent=self,
            )
            return

        if result.success:
            self.file_result_var.set(f"Successfully converted:\n{result.data['output_path']}")
            self.status_var.set("File conversion completed.")
            self._record_usage_background("file_conversion")
            messagebox.showinfo("Conversion Complete", "The file was converted successfully.", parent=self)
        else:
            self.status_var.set("File conversion failed.")
            self._show_error(result)

    def _clear_file(self):
        self.file_input_var.set("")
        self.file_output_var.set("")
        self.file_result_var.set("")
        self.status_var.set("Ready")

    def _open_file_output_folder(self):
        path = self.file_output_var.get().strip()
        if path:
            self._open_folder(Path(path).parent)

    # ========================================================
    # FOLDER ACTIONS
    # ========================================================

    def _browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder Containing Legacy Gujarati Files", parent=self)
        if not path:
            return
        self.folder_input_var.set(path)
        self.folder_output_var.set(str(Path(path) / "Unicode_Output"))
        if self.settings.get("remember_folder", True):
            self.settings["last_folder"] = path
            save_settings(self.settings)

    def _browse_output_folder(self):
        path = filedialog.askdirectory(title="Choose Unicode Output Folder", parent=self)
        if path:
            self.folder_output_var.set(path)

    def _convert_folder(self):
        input_path = self.folder_input_var.get().strip()
        output_path = self.folder_output_var.get().strip()

        if not input_path:
            messagebox.showwarning("No Input Folder", "Please select an input folder.", parent=self)
            return
        if not output_path:
            messagebox.showwarning("No Output Folder", "Please choose an output folder.", parent=self)
            return

        self.status_var.set("Converting folder...")
        self.progress.start(10)
        self.update_idletasks()

        try:
            try:
                result = convert_folder(
                    input_path,
                    output_path,
                    overwrite=self.folder_overwrite_var.get(),
                    font=self.font_var.get(),
                )
            except Exception as exc:
                self.status_var.set("Folder conversion failed.")
                messagebox.showerror(
                    "Conversion Error",
                    f"{type(exc).__name__}: {exc}",
                    parent=self,
                )
                return
        finally:
            self.progress.stop()

        if result.success:
            data = result.data
            self.folder_result_var.set(
                "Conversion completed.\n"
                f"Total files: {data['total_files']}\n"
                f"Successful: {data['successful_files']}\n"
                f"Failed: {data['failed_files']}\n"
                f"Output folder: {data['output_directory']}"
            )
            self.status_var.set("Folder conversion completed.")
            self._record_usage_background("folder_conversion")
            messagebox.showinfo(
                "Conversion Complete",
                f"Converted {data['successful_files']} file(s) successfully.",
                parent=self,
            )
        else:
            self.status_var.set("Folder conversion completed with errors.")
            if result.data is not None:
                data = result.data
                self.folder_result_var.set(
                    "Conversion completed with errors.\n"
                    f"Total files: {data['total_files']}\n"
                    f"Successful: {data['successful_files']}\n"
                    f"Failed: {data['failed_files']}\n"
                    f"Output folder: {data['output_directory']}"
                )
                messagebox.showwarning(
                    "Conversion Completed with Errors",
                    f"Successful: {data['successful_files']}\nFailed: {data['failed_files']}",
                    parent=self,
                )
            else:
                self._show_error(result)

    def _clear_folder(self):
        self.folder_input_var.set("")
        self.folder_output_var.set("")
        self.folder_result_var.set("")
        self.status_var.set("Ready")

    def _open_folder_output_folder(self):
        path = self.folder_output_var.get().strip()
        if path:
            self._open_folder(Path(path))

    # ========================================================
    # SETTINGS
    # ========================================================

    def _show_first_run_privacy(self):
        window = tk.Toplevel(self)
        window.title("Privacy")
        window.transient(self)
        window.grab_set()
        window.resizable(False, False)
        window.configure(bg=BG)

        frame = tk.Frame(
            window,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="Your privacy matters",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(20, 8))

        tk.Label(
            frame,
            text=(
                "Your documents stay on your computer.\n"
                "The converter does not upload your text or files."
            ),
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
            justify="center",
        ).pack(pady=(0, 12))

        tk.Label(
            frame,
            text=(
                "Anonymous usage statistics are disabled by default.\n"
                "You can opt in from Settings if you want to help."
            ),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="center",
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text=(
                "The core converter works locally and does not require\n"
                "an online conversion service."
            ),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="center",
        ).pack(pady=(0, 14))

        ttk.Button(
            frame,
            text="Continue",
            style="Accent.TButton",
            command=lambda: self._close_first_run_privacy(window),
        ).pack(pady=(0, 20))

        self._center_window(window, 500, 340)

    def _close_first_run_privacy(self, window):
        self.settings["privacy_notice_seen"] = True
        save_settings(self.settings)
        window.destroy()

    # ========================================================
    # SETTINGS
    # ========================================================

    def _show_settings(self):
        window = tk.Toplevel(self)
        window.title("Settings")
        window.transient(self)
        window.grab_set()
        window.configure(bg=BG)
        window.resizable(True, True)
        window.minsize(520, 500)

        frame = tk.Frame(
            window, bg=CARD, highlightbackground=BORDER, highlightthickness=1
        )
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="Settings", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", padx=22, pady=(20, 3)
        )
        ttk.Label(
            frame,
            text="Preferences are saved only when you press Save.",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(0, 16))

        font_section = tk.Frame(frame, bg=CARD)
        font_section.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 6))
        font_section.grid_columnconfigure(0, weight=1)
        tk.Label(
            font_section, text="Editor font size", bg=CARD, fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky="w")
        font_var = tk.IntVar(value=self.font_size)
        font_spin = ttk.Spinbox(
            font_section, from_=10, to=24, textvariable=font_var, width=6
        )
        font_spin.grid(row=0, column=1, sticky="e")

        tk.Label(
            frame,
            text="Applies to both Hari and Unicode text editors.",
            bg=CARD, fg=MUTED, font=("Segoe UI", 8),
        ).grid(row=3, column=0, sticky="w", padx=22, pady=(0, 10))

        remember_var = tk.BooleanVar(value=self.settings.get("remember_folder", True))
        overwrite_var = tk.BooleanVar(value=self.settings.get("confirm_overwrite", True))
        telemetry_var = tk.BooleanVar(value=self.settings.get("telemetry_enabled", True))

        def add_toggle(row_number, title, description, variable):
            row = tk.Frame(
                frame, bg=INPUT_BG, highlightbackground=BORDER, highlightthickness=1
            )
            row.grid(row=row_number, column=0, sticky="ew", padx=22, pady=5)
            row.grid_columnconfigure(0, weight=1)

            text_frame = tk.Frame(row, bg=INPUT_BG)
            text_frame.grid(row=0, column=0, sticky="ew", padx=(13, 8), pady=9)
            text_frame.grid_columnconfigure(0, weight=1)

            tk.Label(
                text_frame, text=title, bg=INPUT_BG, fg=TEXT,
                font=("Segoe UI", 9, "bold")
            ).grid(row=0, column=0, sticky="w")
            tk.Label(
                text_frame, text=description, bg=INPUT_BG, fg=MUTED,
                font=("Segoe UI", 8), wraplength=330, justify="left", anchor="w"
            ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

            state_text = tk.StringVar()
            toggle = tk.Checkbutton(
                row, variable=variable, indicatoron=False, width=7, relief="flat",
                bd=0, highlightthickness=0, font=("Segoe UI", 8, "bold"),
                padx=8, pady=5, cursor="hand2",
            )
            toggle.grid(row=0, column=1, sticky="e", padx=(0, 12), pady=9)

            def refresh_toggle():
                enabled = bool(variable.get())
                state_text.set("ON" if enabled else "OFF")
                toggle.configure(
                    textvariable=state_text,
                    bg=ACCENT if enabled else "#E9EDF5",
                    fg="white" if enabled else MUTED,
                    activebackground=ACCENT_HOVER if enabled else "#DDE3EE",
                    activeforeground="white" if enabled else TEXT,
                    selectcolor=ACCENT,
                )
            toggle.configure(command=refresh_toggle)
            refresh_toggle()
            return refresh_toggle

        toggle_refreshers = [
            add_toggle(4, "Remember last folder",
                       "Restore the last folder used by the Folder converter.", remember_var),
            add_toggle(5, "Confirm before overwriting",
                       "Ask before replacing an existing output file.", overwrite_var),
            add_toggle(6, "Share anonymous usage statistics",
                       "Helps improve the free converter. Your text and files are never uploaded.", telemetry_var),
        ]

        buttons = ttk.Frame(frame)
        buttons.grid(row=7, column=0, sticky="ew", padx=22, pady=(18, 20))
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)
        buttons.grid_columnconfigure(2, weight=1)

        ttk.Button(
            buttons, text="Reset to Defaults", style="Secondary.TButton",
            command=lambda: self._reset_settings_controls(
                font_var, remember_var, overwrite_var, telemetry_var, toggle_refreshers
            ),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(
            buttons, text="Cancel", style="Secondary.TButton",
            command=window.destroy,
        ).grid(row=0, column=1, sticky="ew", padx=3)
        ttk.Button(
            buttons, text="Save", style="Accent.TButton",
            command=lambda: self._save_settings_window(
                window, font_var, remember_var, overwrite_var, telemetry_var
            ),
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        self._center_window(window, 580, 570)

    def _reset_settings_controls(
        self,
        font_var,
        remember_var,
        overwrite_var,
        telemetry_var,
        toggle_refreshers,
    ):
        font_var.set(DEFAULT_SETTINGS["font_size"])
        remember_var.set(DEFAULT_SETTINGS["remember_folder"])
        overwrite_var.set(DEFAULT_SETTINGS["confirm_overwrite"])
        telemetry_var.set(DEFAULT_SETTINGS["telemetry_enabled"])
        for refresh in toggle_refreshers:
            refresh()
        # The toggle buttons refresh when clicked. Their variables are
        # reset immediately; Save is still required to persist the reset.
        messagebox.showinfo(
            "Defaults Restored",
            "Default values are restored in this window. Press Save to apply them.",
            parent=self,
        )

    def _save_settings_window(self, window, font_var, remember_var, overwrite_var, telemetry_var, toggle_refreshers=None):
        try:
            size = max(10, min(24, int(font_var.get())))
        except (TypeError, ValueError):
            size = 13

        self.font_size = size
        self.settings["font_size"] = size
        self.settings["remember_folder"] = bool(remember_var.get())
        old_telemetry = bool(self.settings.get("telemetry_enabled", True))
        new_telemetry = bool(telemetry_var.get())

        self.settings["confirm_overwrite"] = bool(overwrite_var.get())
        self.settings["telemetry_enabled"] = new_telemetry
        save_settings(self.settings)

        if new_telemetry and not old_telemetry:
            self._start_telemetry()

        self.input_text.configure(font=(self.input_font_name, self.font_size))
        self.output_text.configure(font=(self.unicode_font, self.font_size))
        window.destroy()
        self.status_var.set(f"Settings saved. Font size: {self.font_size}")

    # ========================================================
    # ABOUT
    # ========================================================

    def _show_about(self):
        window = tk.Toplevel(self)
        window.title(f"About {APP_TITLE}")
        window.transient(self)
        window.grab_set()
        window.resizable(False, False)
        window.configure(bg=BG)
        if self._app_logo is not None:
            try:
                window.iconphoto(True, self._app_logo)
            except tk.TclError:
                pass

        frame = tk.Frame(window, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        if self._app_logo is not None:
            tk.Label(
                frame, image=self._app_logo, bg=CARD, bd=0, highlightthickness=0
            ).pack(pady=(18, 4))

        tk.Label(
            frame,
            text=APP_TITLE,
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=(2, 4))

        tk.Label(
            frame,
            text="Convert Hari / Harikrishna and LMG Arun / Lohit BKMAN to Unicode Gujarati",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack()

        tk.Label(
            frame,
            text=f"Version {APP_VERSION}",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(pady=(8, 0))

        tk.Label(
            frame,
            text=f"Created by {OWNER_NAME}",
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(12, 2))

        github = tk.Label(
            frame,
            text="github.com/VishalGujarati",
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 9, "underline"),
            cursor="hand2",
        )
        github.pack(pady=(0, 6))
        github.bind("<Button-1>", lambda event: self._open_url(GITHUB_URL))

        website = tk.Label(
            frame,
            text="passionprojects.in",
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 8, "underline"),
            cursor="hand2",
        )
        website.pack(pady=(0, 10))
        website.bind("<Button-1>", lambda event: self._open_url(WEBSITE_URL))

        tk.Label(
            frame,
            text=f"Developed by {COMPANY_NAME}",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
        ).pack(pady=(0, 4))

        tk.Label(
            frame,
            text=f"© {PROJECT_YEAR} Passion Projects",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(pady=(0, 12))

        tk.Label(
            frame,
            text="Developed with AI tools and free online resources.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(pady=(0, 12))

        tk.Label(
            frame,
            text="Made for Gujarati users • Free and local",
            bg=CARD,
            fg=TEAL,
            font=("Segoe UI", 9, "bold"),
        ).pack(pady=(0, 12))

        tk.Label(
            frame,
            text="This is free software. If it saves you time,\nyou can support future Gujarati tools and projects.",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
            justify="center",
        ).pack(pady=(0, 12))

        buttons = ttk.Frame(frame)
        buttons.pack(pady=(0, 8))
        ttk.Button(
            buttons,
            text="☕ Support Passion Projects",
            style="Accent.TButton",
            command=lambda: self._open_url(SUPPORT_URL),
        ).pack(side="left")

        privacy = tk.Frame(
            frame, bg="#F0FDFA", highlightbackground="#99F6E4", highlightthickness=1
        )
        privacy.pack(fill="x", padx=18, pady=(10, 18))
        tk.Label(
            privacy,
            text="🔒 Your documents stay on your computer",
            bg="#F0FDFA",
            fg=TEAL,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(10, 3))
        tk.Label(
            privacy,
            text="Conversion happens locally. Your text and files are never uploaded.",
            bg="#F0FDFA",
            fg=TEXT,
            font=("Segoe UI", 8),
            justify="center",
        ).pack(pady=(0, 10))

        self._center_window(window, 560, 650)

    # ========================================================
    # HELPERS
    # ========================================================

    def _set_responsive_main_geometry(self):
        """Choose a safe starting size for the user's screen."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Comfortable starting size on normal desktop and laptop displays.
        # The window remains resizable and the two editors share equal width.
        width = min(1200, max(900, int(screen_w * 0.88)))
        height = min(800, max(620, int(screen_h * 0.82)))

        # Respect smaller displays.
        width = min(width, max(760, screen_w - 24))
        height = min(height, max(540, screen_h - 48))

        self.geometry(f"{width}x{height}")

        # Keep the minimum small enough for common 1280x720 / 1366x768
        # Windows and Ubuntu displays.
        min_width = min(900, max(720, screen_w - 24))
        min_height = min(620, max(520, screen_h - 48))
        self.minsize(min_width, min_height)

    def _center_window(self, window, width, height):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(width, max(420, screen_w - 40))
        height = min(height, max(420, screen_h - 80))
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        x = max(10, min(x, screen_w - width - 10))
        y = max(10, min(y, screen_h - height - 40))
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _open_url(self, url):
        if url:
            webbrowser.open(url)

    def _open_folder(self, path):
        try:
            path = Path(path)
            if not path.exists():
                messagebox.showinfo("Folder Not Found", "The output folder does not exist yet.", parent=self)
                return

            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as exc:
            messagebox.showerror("Unable to Open Folder", str(exc), parent=self)

    def _should_confirm_overwrite(self, output_path, overwrite_enabled):
        if not overwrite_enabled and Path(output_path).exists():
            messagebox.showwarning(
                "Output Already Exists",
                "The output file already exists. Enable overwrite if you want to replace it.",
                parent=self,
            )
            return True

        if overwrite_enabled and self.settings.get("confirm_overwrite", True) and Path(output_path).exists():
            answer = messagebox.askyesno(
                "Confirm Overwrite",
                "The output file already exists. Do you want to replace it?",
                parent=self,
            )
            return not answer

        return False

    def destroy(self):
        # Remove private legacy font registrations when the app closes.
        if sys.platform.startswith("win"):
            try:
                for font_path in getattr(self, "_font_handles", []):
                    ctypes.windll.gdi32.RemoveFontResourceExW(
                        str(font_path),
                        0x10,
                        0,
                    )
            except Exception:
                pass

        super().destroy()

    def _show_error(self, result):
        if result.error is not None:
            error = result.error
            details = error.user_message
            if error.technical_message:
                details += "\n\nTechnical details:\n" + error.technical_message
            messagebox.showerror("Conversion Error", details, parent=self)
        else:
            messagebox.showerror(
                "Conversion Error",
                result.message or "An unknown error occurred.",
                parent=self,
            )


# ============================================================
# ENTRY POINT
# ============================================================

def main():
    app = HariUnicodeConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
