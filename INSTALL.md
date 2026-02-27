# Installing to-markdown

This guide walks you through installing to-markdown on your computer. No technical
experience required - just follow the steps for your operating system.

---

## What You Need

- A computer running **macOS** (10.15+) or **Windows** (10/11)
- An internet connection (for downloading dependencies)
- About 10 minutes

## Quick Install

### macOS

Open **Terminal** (search for "Terminal" in Spotlight, or find it in
Applications > Utilities).

```bash
# 1. Download the project
git clone https://github.com/wiseyoda/to-markdown.git
cd to-markdown

# 2. Run the installer
./install.sh
```

That's it! The installer handles everything: Python, dependencies, and setup.

### Windows

Open **PowerShell** (search for "PowerShell" in the Start menu).

```powershell
# 1. Download the project
git clone https://github.com/wiseyoda/to-markdown.git
cd to-markdown

# 2. Run the installer
.\install.ps1
```

> **Note**: If you see a "running scripts is disabled" error, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Then try `.\install.ps1` again.

---

## What the Installer Does

The install script automatically:

1. **Installs uv** (Python package manager) if not already installed
2. **Installs Python 3.14+** via uv if not already available
3. **Offers to install Tesseract** for OCR support (optional)
4. **Installs all project dependencies** (`uv sync --all-extras`)
5. **Validates the installation** by running `to-markdown --version`
6. **Sets up a shell alias** so you can use `to-markdown` from any directory

### Example Terminal Output (macOS)

```
  to-markdown installer for macOS

[1/7] Checking uv package manager
  OK uv 0.10.6

[2/7] Checking Python 3.14+
  OK Python 3.14.3 found

[3/7] Checking Tesseract OCR (optional)
  OK Tesseract found (tesseract 5.5.0)

[4/7] Installing dependencies
  OK All dependencies installed

[5/7] Validating installation
  OK to-markdown 0.1.0

[6/7] Setting up shell alias
  OK Added alias to /Users/you/.zshrc

[7/7] Installation complete!

  to-markdown is ready to use!

  Quick start:
    to-markdown yourfile.pdf          # Convert a file
    to-markdown docs/                 # Convert a directory
    to-markdown --setup               # Configure smart features (optional)
```

---

## After Installing

### Convert Your First File

Open a new terminal window (to pick up the shell alias), then:

```bash
to-markdown yourfile.pdf
```

This creates `yourfile.md` next to the original file.

### Convert a Directory

```bash
to-markdown docs/
```

This converts all supported files in the `docs/` folder.

### Set Up Smart Features (Optional)

to-markdown has AI-powered features that can clean up extraction artifacts,
generate summaries, and describe images. These require a free Google Gemini API key.

```bash
to-markdown --setup
```

The wizard will guide you through getting and configuring an API key.

---

## Troubleshooting

### "command not found: to-markdown"

**Cause**: The shell alias hasn't been loaded yet.

**Fix**: Open a new terminal window, or run:
```bash
source ~/.zshrc    # macOS (zsh)
source ~/.bashrc   # macOS/Linux (bash)
. $PROFILE         # Windows (PowerShell)
```

### "command not found: git"

**Cause**: Git is not installed.

**Fix**:
- macOS: Install Xcode Command Line Tools: `xcode-select --install`
- Windows: Download from https://git-scm.com/download/win

### "uv: command not found" after install

**Cause**: uv was installed but your terminal doesn't see it yet.

**Fix**: Close and reopen your terminal, then run `./install.sh` again.

### "Python 3.14 not available"

**Cause**: Python 3.14 hasn't been released for your platform yet.

**Fix**: The installer will automatically try Python 3.13 as a fallback.

### "running scripts is disabled" (Windows)

**Cause**: PowerShell execution policy blocks scripts.

**Fix**: Run this command in PowerShell (as Administrator if needed):
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Smart features say "GEMINI_API_KEY is not set"

**Cause**: You haven't configured an API key yet.

**Fix**: Run `to-markdown --setup` and follow the prompts, or manually add
your key to the `.env` file in the project directory:
```
GEMINI_API_KEY=your-key-here
```

### "Tesseract not found" warnings

**Cause**: Tesseract OCR is not installed. This only affects scanned PDFs and images.

**Fix**: Install Tesseract:
- macOS: `brew install tesseract`
- Windows: `winget install UB-Mannheim.TesseractOCR`

---

## Uninstalling

### macOS

```bash
cd to-markdown
./uninstall.sh
```

### Windows

```powershell
cd to-markdown
.\uninstall.ps1
```

The uninstaller removes the shell alias, virtual environment, and data files.
Your converted `.md` files are preserved.

To skip confirmation prompts: `./uninstall.sh --yes` or `.\uninstall.ps1 -Yes`

---

## For Developers

If you're a developer, you can also install manually:

```bash
# Clone and install
git clone https://github.com/wiseyoda/to-markdown.git
cd to-markdown
uv sync --all-extras

# Run directly
uv run to-markdown yourfile.pdf

# Run tests
uv run pytest
```

See [README.md](README.md) for full developer documentation.
