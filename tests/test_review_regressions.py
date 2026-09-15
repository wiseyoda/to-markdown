"""Real CLI subprocess and MCP stdio regressions for the September P1 review."""

import asyncio
import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import to_markdown
from to_markdown.core.batch import convert_batch, convert_batch_async
from to_markdown.core.constants import MAX_MCP_OUTPUT_CHARS, TASK_DB_FILENAME
from to_markdown.core.tasks import TaskStore


@pytest.fixture
def isolated_env(tmp_path):
    return {
        "PATH": os.environ["PATH"],
        "PYTHONPATH": str(Path(to_markdown.__file__).parents[1]),
        "TO_MARKDOWN_DATA_DIR": str(tmp_path / ".tasks"),
        "GEMINI_API_KEY": "",
        "PYTHON_DOTENV_DISABLED": "1",
    }


@pytest.fixture
def store(isolated_env):
    store = TaskStore(Path(isolated_env["TO_MARKDOWN_DATA_DIR"]) / TASK_DB_FILENAME)
    yield store
    store.close()


def cli(env, *args):
    return subprocess.run(
        [sys.executable, "-m", "to_markdown.cli", *map(str, args)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def wait_task(store, task_id):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        task = store.get(task_id)
        if task.is_done:
            return task
        time.sleep(0.05)
    pytest.fail(f"Worker did not finish: {store.get(task_id)}")


def test_cli_background_status_and_cancel_without_input(tmp_path, isolated_env, store):
    source = tmp_path / "sample.html"
    source.write_text("<h1>Background works</h1><p>Preserve this body.</p>")
    started = cli(isolated_env, source, "--background", "--no-clean")
    assert started.returncode == 0, started.stderr
    task_id = started.stdout.strip()
    task = wait_task(store, task_id)
    assert task.status.value == "completed", task.error
    assert "Background works" in source.with_suffix(".md").read_text()
    status = cli(isolated_env, "--status", task_id)
    assert status.returncode == 0 and "completed" in status.stdout
    pending = store.create(str(source))
    cancelled = cli(isolated_env, "--cancel", pending.id)
    assert cancelled.returncode == 0, cancelled.stderr
    assert store.get(pending.id).status.value == "cancelled"
    assert cli(isolated_env, "--background").returncode != 0
    assert cli(isolated_env, "--status", task_id, "--cancel", pending.id).returncode != 0


@asynccontextmanager
async def mcp_session(isolated_env):
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "to_markdown.mcp"], env=isolated_env
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        yield session


async def call(session, tool, **arguments):
    result = await session.call_tool(tool, arguments)
    assert not result.isError, result
    return "\n".join(block.text for block in result.content if block.type == "text")


async def test_mcp_batch_preserves_source_and_existing_output(tmp_path, isolated_env):
    async with mcp_session(isolated_env) as session:
        source = tmp_path / "notes.md"
        source.write_bytes(b"# Hand-authored\n\nKEEP EXACTLY\n")
        other = tmp_path / "other.html"
        other.write_text("<p>new output</p>")
        before = source.read_bytes()
        response = await call(session, "convert_batch", directory_path=str(tmp_path), clean=False)
        assert source.read_bytes() == before
        assert "**Skipped**: 1" in response
        assert "new output" in other.with_suffix(".md").read_text()


@pytest.mark.parametrize("batch", [False, True])
async def test_mcp_background_preserves_existing_output(tmp_path, isolated_env, store, batch):
    async with mcp_session(isolated_env) as session:
        docs = tmp_path / "docs"
        docs.mkdir()
        source = docs / "report.html"
        source.write_text("<p>replacement</p>")
        output = docs / "report.md"
        output.write_text("Original user notes")
        response = await call(
            session, "start_conversion", file_path=str(docs if batch else source), clean=False
        )
        task_id = response.split("**Task ID**: ", 1)[1].splitlines()[0]
        task = await asyncio.to_thread(wait_task, store, task_id)
        assert task.status.value == "failed", task
        assert output.read_text() == "Original user notes"
        assert source.read_text() == "<p>replacement</p>"


@pytest.mark.parametrize("stem", ["report", "Report"])
@pytest.mark.parametrize("custom_output", [False, True])
@pytest.mark.parametrize("force", [False, True])
@pytest.mark.parametrize("async_mode", [False, True])
async def test_batch_collisions_are_reported_before_writes(
    tmp_path, custom_output, force, async_mode, stem
):
    files = [tmp_path / f"{stem}.html", tmp_path / "report.txt"]
    for source in files:
        source.write_text("Distinct source " + source.suffix)
    output_dir = tmp_path / "out" if custom_output else None
    kwargs = {"output_dir": output_dir, "force": force}
    result = (
        await convert_batch_async(files, **kwargs)
        if async_mode
        else await asyncio.to_thread(convert_batch, files, quiet=True, **kwargs)
    )
    assert not result.succeeded
    assert len(result.failed) == 2
    assert all("Output collision" in error for _, error in result.failed)
    assert not list(tmp_path.rglob("*.md"))
    assert all(source.read_text() == "Distinct source " + source.suffix for source in files)


async def test_mcp_collision_keeps_unrelated_success(tmp_path, isolated_env):
    async with mcp_session(isolated_env) as session:
        for name in ("report.html", "report.txt", "unique.txt"):
            (tmp_path / name).write_text("Body of " + name)
        response = await call(session, "convert_batch", directory_path=str(tmp_path), clean=False)
        assert "**Succeeded**: 1" in response and "**Failed**: 2" in response
        assert not (tmp_path / "report.md").exists()
        assert "Body of unique.txt" in (tmp_path / "unique.md").read_text()


async def test_large_mcp_response_persists_full_unique_artifact(tmp_path, isolated_env):
    async with mcp_session(isolated_env) as session:
        source = tmp_path / "large.md"
        body = "A long document paragraph.\n\n" * (MAX_MCP_OUTPUT_CHARS // 10) + "FINAL TAIL"
        source.write_text(body)
        response = await call(session, "convert_file", file_path=str(source), clean=False)
        artifact = Path(response.split("Full content available at: ", 1)[1].splitlines()[0])
        assert artifact.is_absolute() and artifact != source
        assert artifact.read_text().endswith("FINAL TAIL\n")
        assert len(artifact.read_text()) > MAX_MCP_OUTPUT_CHARS
        assert source.read_text() == body
        repeated = await call(session, "convert_file", file_path=str(source), clean=False)
        second = Path(repeated.split("Full content available at: ", 1)[1].splitlines()[0])
        assert second != artifact and artifact.exists() and second.exists()


def test_cli_batch_collision_with_force(tmp_path, isolated_env):
    for name in ("report.html", "report.txt"):
        (tmp_path / name).write_text("Source " + name)
    result = cli(isolated_env, tmp_path, "--force", "--no-clean")
    assert result.returncode != 0
    assert "Output collision" in result.stdout + result.stderr
    assert not (tmp_path / "report.md").exists()
