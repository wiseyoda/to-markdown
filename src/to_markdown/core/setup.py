"""Configuration wizard for first-time setup."""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from to_markdown.core.constants import (
    GEMINI_API_KEY_ENV,
    GEMINI_DEFAULT_MODEL,
    GEMINI_MODEL_ENV,
    SETUP_ENV_FILE,
    SETUP_GEMINI_KEY_URL,
    SETUP_VALIDATION_MAX_TOKENS,
    SETUP_VALIDATION_PROMPT,
)

console = Console(stderr=True)


def detect_existing_config(project_dir: Path) -> dict:
    """Detect existing .env configuration."""
    env_path = project_dir / SETUP_ENV_FILE
    result = {"has_env": False, "has_api_key": False, "api_key": None}

    if not env_path.exists():
        return result

    result["has_env"] = True
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith(f"{GEMINI_API_KEY_ENV}="):
            value = line.split("=", 1)[1].strip()
            if value:
                result["has_api_key"] = True
                result["api_key"] = value
            break

    return result


def write_env_file(project_dir: Path, api_key: str) -> None:
    """Write or update the .env file with the API key."""
    env_path = project_dir / SETUP_ENV_FILE
    lines: list[str] = []
    key_written = False

    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith(f"{GEMINI_API_KEY_ENV}="):
                lines.append(f"{GEMINI_API_KEY_ENV}={api_key}")
                key_written = True
            else:
                lines.append(line)

    if not key_written:
        lines.append(f"{GEMINI_API_KEY_ENV}={api_key}")

    env_path.write_text("\n".join(lines) + "\n")


def _check_llm_available() -> bool:
    """Check if google-genai SDK is importable."""
    try:
        import google.genai  # noqa: F401

        return True
    except ImportError:
        return False


def _make_test_call(api_key: str) -> str:
    """Make a test API call to validate the key."""
    import google.genai as genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.environ.get(GEMINI_MODEL_ENV, GEMINI_DEFAULT_MODEL),
        contents=SETUP_VALIDATION_PROMPT,
        config={"max_output_tokens": SETUP_VALIDATION_MAX_TOKENS},
    )
    return response.text


def validate_api_key(api_key: str) -> bool:
    """Validate an API key by making a test call to Gemini."""
    if not _check_llm_available():
        return True  # Can't validate without SDK, assume valid

    try:
        _make_test_call(api_key)
        return True
    except Exception:
        return False


def _find_project_dir() -> Path:
    """Find the project directory (where pyproject.toml lives)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def run_setup(project_dir: Path | None = None) -> None:
    """Run the interactive configuration wizard."""
    if project_dir is None:
        project_dir = _find_project_dir()

    console.print()
    console.print(
        Panel(
            "[bold]to-markdown Configuration Wizard[/bold]\n\n"
            "This wizard helps you set up optional smart features:\n"
            "  [cyan]--clean[/cyan]   Fix extraction artifacts via AI\n"
            "  [cyan]--summary[/cyan] Generate document summaries\n"
            "  [cyan]--images[/cyan]  Describe images via AI vision\n\n"
            "These features require a free Google Gemini API key.\n"
            "Core conversion works without any configuration.",
            title="Setup",
            border_style="blue",
        )
    )

    config = detect_existing_config(project_dir)

    if config["has_api_key"]:
        console.print("\n[green]API key already configured.[/green]")
        if not typer.confirm("Update the API key?", default=False):
            console.print("\n[green]Configuration unchanged.[/green]")
            _print_next_steps()
            return

    if not typer.confirm(
        "\nWould you like to set up a Gemini API key for smart features?", default=True
    ):
        console.print("\n[yellow]Skipped.[/yellow] Smart features disabled.")
        console.print("You can run [cyan]to-markdown --setup[/cyan] later to configure.")
        return

    url = SETUP_GEMINI_KEY_URL
    console.print(f"\nGet a free API key at: [link={url}]{url}[/link]")
    api_key = typer.prompt("\nPaste your API key", default="", show_default=False)

    if not api_key.strip():
        console.print("\n[yellow]No key entered.[/yellow] Smart features disabled.")
        return

    api_key = api_key.strip()

    console.print("\nValidating API key...", end=" ")
    if validate_api_key(api_key):
        console.print("[green]Valid![/green]")
        write_env_file(project_dir, api_key)
        console.print(f"\n[green]API key saved to {SETUP_ENV_FILE}[/green]")
    else:
        console.print("[red]Invalid or unreachable.[/red]")
        console.print("Key not saved. Check the key and try again.")
        console.print(f"You can also manually add to {SETUP_ENV_FILE}:")
        console.print(f"  {GEMINI_API_KEY_ENV}=your-key-here")
        return

    _print_next_steps()


def run_setup_quiet(project_dir: Path | None = None) -> None:
    """Non-interactive setup: validate existing configuration."""
    if project_dir is None:
        project_dir = _find_project_dir()

    config = detect_existing_config(project_dir)

    if not config["has_api_key"]:
        console.print("API key not configured. Smart features disabled.")
        return

    console.print("Validating existing API key...", end=" ")
    if validate_api_key(config["api_key"]):
        console.print("[green]Valid.[/green]")
        console.print("Smart features are available.")
    else:
        console.print("[red]Invalid or unreachable.[/red]")
        console.print("Check your API key in .env file.")


def _print_next_steps() -> None:
    """Print post-setup instructions."""
    console.print(
        Panel(
            "Try these commands:\n\n"
            "  [cyan]to-markdown file.pdf[/cyan]              Convert a file\n"
            "  [cyan]to-markdown file.pdf --clean[/cyan]      Fix extraction artifacts\n"
            "  [cyan]to-markdown file.pdf --summary[/cyan]    Add AI summary\n"
            "  [cyan]to-markdown file.pdf --images[/cyan]     Describe images\n"
            "  [cyan]to-markdown docs/[/cyan]                 Convert a directory",
            title="What's Next",
            border_style="green",
        )
    )
