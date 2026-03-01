"""Batch processing: file discovery and multi-file conversion loop."""

import glob as glob_module
import logging
from dataclasses import dataclass, field
from pathlib import Path

from to_markdown.core.constants import (
    DEFAULT_OUTPUT_EXTENSION,
    EXIT_ERROR,
    EXIT_PARTIAL,
    EXIT_SUCCESS,
)
from to_markdown.core.extraction import UnsupportedFormatError
from to_markdown.core.pipeline import OutputExistsError, convert_file, convert_file_async

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Aggregated result from a batch conversion run."""

    succeeded: list[Path] = field(default_factory=list)
    failed: list[tuple[Path, str]] = field(default_factory=list)
    skipped: list[tuple[Path, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.succeeded) + len(self.failed) + len(self.skipped)

    @property
    def exit_code(self) -> int:
        if not self.succeeded and not self.failed and not self.skipped:
            return EXIT_ERROR
        if not self.succeeded:
            return EXIT_ERROR
        if self.failed:
            return EXIT_PARTIAL
        return EXIT_SUCCESS


def discover_files(source: Path, *, recursive: bool = True) -> list[Path]:
    """Discover convertible files in a directory.

    Skips hidden files/dirs (starting with '.') and files without extensions.
    Returns sorted list for deterministic processing order.
    """
    files: list[Path] = []
    iterator = source.rglob("*") if recursive else source.glob("*")

    for path in iterator:
        if not path.is_file():
            continue
        # Skip hidden files and files in hidden directories
        if any(part.startswith(".") for part in path.relative_to(source).parts):
            continue
        # Skip files without extensions
        if not path.suffix:
            continue
        files.append(path)

    return sorted(files)


def resolve_glob(pattern: str) -> list[Path]:
    """Resolve a glob pattern to a sorted list of file paths."""
    matches = [Path(p) for p in glob_module.glob(pattern) if Path(p).is_file()]
    return sorted(matches)


def _resolve_batch_output(
    input_path: Path,
    output_dir: Path,
    batch_root: Path | None,
) -> Path:
    """Resolve output path for a file in a batch, preserving directory structure."""
    if batch_root is not None:
        try:
            relative = input_path.parent.relative_to(batch_root)
            return output_dir / relative / (input_path.stem + DEFAULT_OUTPUT_EXTENSION)
        except ValueError:
            pass
    return output_dir / (input_path.stem + DEFAULT_OUTPUT_EXTENSION)


def convert_batch(
    files: list[Path],
    output_dir: Path | None = None,
    *,
    batch_root: Path | None = None,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
    fail_fast: bool = False,
    quiet: bool = False,
) -> BatchResult:
    """Convert multiple files to Markdown with progress reporting.

    Args:
        files: List of file paths to convert.
        output_dir: Output directory (mirrors input structure). None = next to source.
        batch_root: Root of the batch input (for relative path calculation).
        force: If True, overwrite existing output files.
        clean: If True, apply LLM artifact repair to each file.
        summary: If True, generate summary for each file.
        images: If True, describe images for each file.
        sanitize: If True, apply prompt injection sanitization to output.
        fail_fast: If True, stop on first error.
        quiet: If True, suppress progress output.

    Returns:
        BatchResult with succeeded, failed, and skipped lists.
    """
    result = BatchResult()

    progress_ctx = _make_progress(quiet, len(files))
    with progress_ctx as update_fn:
        for file_path in files:
            update_fn(file_path.name)
            out = None
            if output_dir is not None:
                out = _resolve_batch_output(file_path, output_dir, batch_root)

            try:
                converted = convert_file(
                    file_path,
                    output_path=out,
                    force=force,
                    clean=clean,
                    summary=summary,
                    images=images,
                    sanitize=sanitize,
                )
                result.succeeded.append(converted)
                logger.info("Converted: %s", file_path.name)
            except UnsupportedFormatError as exc:
                result.skipped.append((file_path, str(exc)))
                logger.debug("Skipped (unsupported): %s", file_path.name)
            except OutputExistsError as exc:
                result.skipped.append((file_path, f"Output exists: {exc}"))
                logger.debug("Skipped (exists): %s", file_path.name)
            except Exception as exc:
                result.failed.append((file_path, str(exc)))
                logger.warning("Failed: %s - %s", file_path.name, exc)
                if fail_fast:
                    break

    return result


async def convert_batch_async(
    files: list[Path],
    output_dir: Path | None = None,
    *,
    batch_root: Path | None = None,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
    fail_fast: bool = False,
) -> BatchResult:
    """Async version of convert_batch() for use inside a running event loop (e.g. MCP).

    Same behavior as convert_batch() but calls convert_file_async() directly,
    avoiding the asyncio.run() call that would crash inside FastMCP's event loop.
    No progress bar (MCP always passes quiet=True).
    """
    result = BatchResult()

    for file_path in files:
        out = None
        if output_dir is not None:
            out = _resolve_batch_output(file_path, output_dir, batch_root)

        try:
            converted = await convert_file_async(
                file_path,
                output_path=out,
                force=force,
                clean=clean,
                summary=summary,
                images=images,
                sanitize=sanitize,
            )
            result.succeeded.append(converted)
            logger.info("Converted: %s", file_path.name)
        except UnsupportedFormatError as exc:
            result.skipped.append((file_path, str(exc)))
            logger.debug("Skipped (unsupported): %s", file_path.name)
        except OutputExistsError as exc:
            result.skipped.append((file_path, f"Output exists: {exc}"))
            logger.debug("Skipped (exists): %s", file_path.name)
        except Exception as exc:
            result.failed.append((file_path, str(exc)))
            logger.warning("Failed: %s - %s", file_path.name, exc)
            if fail_fast:
                break

    return result


class _NoProgress:
    """Null progress context for quiet mode."""

    def __enter__(self):
        return lambda _name: None

    def __exit__(self, *_args):
        pass


class _RichProgress:
    """Rich progress bar wrapper for batch conversion."""

    def __init__(self, total: int) -> None:
        self._total = total
        self._progress = None
        self._task_id = None

    def __enter__(self):
        from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn

        self._progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[dim]{task.fields[filename]}"),
        )
        self._progress.__enter__()
        self._task_id = self._progress.add_task("Converting", total=self._total, filename="")
        return self._update

    def _update(self, filename: str) -> None:
        if self._progress is not None and self._task_id is not None:
            self._progress.update(self._task_id, advance=1, filename=filename)

    def __exit__(self, *args):
        if self._progress is not None:
            self._progress.__exit__(*args)


def _make_progress(quiet: bool, total: int) -> _NoProgress | _RichProgress:
    """Create appropriate progress context based on quiet flag."""
    if quiet:
        return _NoProgress()
    return _RichProgress(total)
