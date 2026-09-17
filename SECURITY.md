# Security and release policy

Gujarati Legacy Font Converter is designed as an offline-first desktop converter.

## Principles

- Core conversion runs locally.
- Automatic telemetry is disabled by default.
- Automatic remote software-control checks are disabled in the release startup path.
- No document contents are uploaded for core conversion.
- User feedback submission is explicit and user initiated.
- Original input files are preserved by default.
- Input and output paths must not resolve to the same file.
- Existing outputs are not replaced unless overwrite is explicitly requested.
- Temporary outputs are used before replacing final output files.
- DOCX/ODT files are processed as document packages; their contents are not executed.

## Code protection

A packaged Python executable is not impossible to reverse engineer. PyInstaller packaging mainly prevents casual source distribution. Stronger protection can be considered later by compiling the most sensitive conversion modules to native extensions and by using code signing.

Do not use anti-analysis or antivirus-evasion techniques. They can reduce trust and increase false-positive risk.

## Defender / SmartScreen

Unsigned new software may be shown as unrecognized or have a SmartScreen warning. This is not solved by disguising the program. Use normal packaging, stable release hashes, reproducible build records, and code signing when financially practical. If a legitimate release is incorrectly detected as malware, investigate the detection and submit the file to Microsoft rather than instructing users to disable security software.
