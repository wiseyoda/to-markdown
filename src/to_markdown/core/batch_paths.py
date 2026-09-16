"""Preflight batch destinations before any conversion can write output."""

import contextlib
from collections import Counter
from pathlib import Path

from to_markdown.core.constants import DEFAULT_OUTPUT_EXTENSION


def plan_batch_outputs(
    files: list[Path], output_dir: Path | None, batch_root: Path | None
) -> tuple[dict[Path, Path], list[tuple[Path, str]]]:
    """Reject ambiguous destinations and outputs that would replace another input.

    Do not let force bypass collision checks: it authorizes replacing existing
    outputs, not discarding another conversion or an input in the same batch.
    """
    destinations = []
    for source in files:
        output = source.resolve().with_suffix(DEFAULT_OUTPUT_EXTENSION)
        if output_dir is not None:
            relative = Path()
            if batch_root is not None:
                with contextlib.suppress(ValueError):
                    relative = source.resolve().parent.relative_to(batch_root.resolve())
            output = output_dir / relative / (source.stem + DEFAULT_OUTPUT_EXTENSION)
        destinations.append(output.resolve())

    # Conservatively reject case aliases too: macOS commonly uses a
    # case-insensitive filesystem, including for not-yet-created outputs.
    counts = Counter(str(path).casefold() for path in destinations)
    sources = {str(source.resolve()).casefold() for source in files}
    outputs = {}
    failures = []
    for source, output in zip(files, destinations, strict=True):
        key = str(output).casefold()
        if counts[key] > 1:
            failures.append((source, f"Output collision: multiple inputs target {output}"))
        elif key in sources and key != str(source.resolve()).casefold():
            failures.append((source, f"Output collision: destination is a batch input: {output}"))
        else:
            outputs[source] = output
    return outputs, failures
