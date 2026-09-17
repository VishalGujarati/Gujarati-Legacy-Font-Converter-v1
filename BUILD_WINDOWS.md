# Windows x64 release build

## Target

- Windows 7 SP1 x64 through Windows 11 x64
- Python 3.8.10 x64
- PyInstaller 5.13.2
- Inno Setup 6
- 64-bit only

Windows 7 is a legacy compatibility target. Windows 7 itself is no longer supported by Microsoft for security updates.

## Recommended build machine

Use a real Windows x64 machine or a Windows x64 GitHub Actions runner. The final Windows executable must be built on Windows; PyInstaller is not a cross-compiler.

## Local Windows build

1. Install Python 3.8.10 x64 and make sure the Python launcher `py` is available.
2. Install Inno Setup 6.
3. Extract this project.
4. Open Command Prompt in the `Legacy_to_Unicode Converter` folder.
5. Run:

    build\\build_windows.bat

6. If that succeeds, run:

    build\\make_installer.bat

7. The installer will be placed in the `Output` folder.

Expected files:

- `dist\\GujaratiLegacyFontConverter\\GujaratiLegacyFontConverter.exe`
- `Output\\GujaratiLegacyFontConverter-1.0.1-Setup-x64.exe`

## GitHub Actions build (recommended if you do not have Windows)

1. Create a GitHub repository.
2. Upload the contents of this project to the repository.
3. Push the project to GitHub.
4. Open GitHub Actions and select **Windows release build**.
5. Click **Run workflow**.
6. Download the generated artifact named `GujaratiLegacyFontConverter-1.0.1-Windows-x64`.

The workflow uses a Windows x64 runner, Python 3.8.10, PyInstaller 5.13.2, and Inno Setup.

## Before distribution

Test the installer on clean Windows x64 installations. At minimum test:

- Windows 7 SP1 x64
- Windows 10 x64
- Windows 11 x64

Test both single-file and folder conversion for Hari/Harikrishna and LMG Arun/Lohit BKMAN. Test TXT, DOCX, ODT, and extensionless documents where applicable.

Generate a SHA-256 hash for the final installer and archive the exact installer, source commit, build configuration, and hash together.

## Security

The release deliberately avoids antivirus-evasion behavior. Do not add self-modifying code, hidden PowerShell execution, process injection, persistence, runtime executable downloads, or instructions telling users to disable Defender.

Code signing can be added later when a signing certificate is available. No signing certificate is required to perform the build.
