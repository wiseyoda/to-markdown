"""Tests for MCP server setup and tool registration (mcp/server.py)."""

import pytest
from unittest.mock import patch
from mcp.server.fastmcp.exceptions import ToolError


class TestServerCreation:
    """Tests for MCP server initialization."""

    def test_server_creates_successfully(self):
        from to_markdown.mcp.server import mcp

        assert mcp is not None
        assert mcp.name == "to-markdown"

    def test_run_server_is_callable(self):
        from to_markdown.mcp.server import run_server

        assert callable(run_server)


class TestToolRegistration:
    """Tests for tool registration on the MCP server."""

    def test_convert_file_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "convert_file" in tool_names

    def test_convert_batch_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "convert_batch" in tool_names

    def test_list_formats_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "list_formats" in tool_names

    def test_get_status_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "get_status" in tool_names

    def test_start_conversion_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "start_conversion" in tool_names

    def test_get_task_status_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "get_task_status" in tool_names

    def test_list_tasks_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "list_tasks" in tool_names

    def test_cancel_task_tool_registered(self):
        from to_markdown.mcp.server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "cancel_task" in tool_names

    def test_exactly_eight_tools_registered(self):
        from to_markdown.mcp.server import mcp

        tools = mcp._tool_manager.list_tools()
        assert len(tools) == 8


class TestToolSchemas:
    """Tests for tool parameter schemas."""

    def _get_tool(self, name: str):
        from to_markdown.mcp.server import mcp

        for tool in mcp._tool_manager.list_tools():
            if tool.name == name:
                return tool
        msg = f"Tool {name} not found"
        raise ValueError(msg)

    def test_convert_file_has_file_path_param(self):
        tool = self._get_tool("convert_file")
        schema = tool.parameters
        assert "file_path" in schema.get("properties", {})
        assert "file_path" in schema.get("required", [])

    def test_convert_file_optional_params(self):
        tool = self._get_tool("convert_file")
        props = tool.parameters.get("properties", {})
        for param in ["clean", "summary", "images", "sanitize"]:
            assert param in props

    def test_convert_batch_has_directory_path_param(self):
        tool = self._get_tool("convert_batch")
        schema = tool.parameters
        assert "directory_path" in schema.get("properties", {})
        assert "directory_path" in schema.get("required", [])

    def test_convert_batch_has_recursive_param(self):
        tool = self._get_tool("convert_batch")
        props = tool.parameters.get("properties", {})
        assert "recursive" in props

    def test_convert_batch_has_sanitize_param(self):
        tool = self._get_tool("convert_batch")
        props = tool.parameters.get("properties", {})
        assert "sanitize" in props

    def test_start_conversion_has_sanitize_param(self):
        tool = self._get_tool("start_conversion")
        props = tool.parameters.get("properties", {})
        assert "sanitize" in props

    def test_start_conversion_has_file_path_param(self):
        tool = self._get_tool("start_conversion")
        schema = tool.parameters
        assert "file_path" in schema.get("properties", {})
        assert "file_path" in schema.get("required", [])

    def test_get_task_status_has_task_id_param(self):
        tool = self._get_tool("get_task_status")
        schema = tool.parameters
        assert "task_id" in schema.get("properties", {})
        assert "task_id" in schema.get("required", [])

    def test_cancel_task_has_task_id_param(self):
        tool = self._get_tool("cancel_task")
        schema = tool.parameters
        assert "task_id" in schema.get("properties", {})
        assert "task_id" in schema.get("required", [])


class TestModuleImport:
    """Tests for module import behavior."""

    def test_mcp_package_importable(self):
        import to_markdown.mcp

        assert hasattr(to_markdown.mcp, "run_server")

    def test_server_importable(self):
        from to_markdown.mcp.server import mcp, run_server

        assert mcp is not None
        assert callable(run_server)

    def test_tools_importable(self):
        from to_markdown.mcp.tools import (
            handle_cancel_task,
            handle_convert_batch,
            handle_convert_file,
            handle_get_status,
            handle_get_task_status,
            handle_list_formats,
            handle_list_tasks,
            handle_start_conversion,
        )

        assert all(
            callable(f)
            for f in [
                handle_convert_file,
                handle_convert_batch,
                handle_list_formats,
                handle_get_status,
                handle_start_conversion,
                handle_get_task_status,
                handle_list_tasks,
                handle_cancel_task,
            ]
        )


class TestToolErrorTranslation:
    """Tests for ToolError translation in server wrappers."""

    async def test_convert_file_value_error(self):
        from to_markdown.mcp.server import convert_file

        with patch(
            "to_markdown.mcp.server.handle_convert_file", side_effect=ValueError("test value error")
        ):
            with pytest.raises(ToolError, match="test value error"):
                await convert_file("path/to/file")

    async def test_convert_file_generic_error(self):
        from to_markdown.mcp.server import convert_file

        with patch(
            "to_markdown.mcp.server.handle_convert_file", side_effect=Exception("test generic error")
        ):
            with pytest.raises(ToolError, match="Conversion failed: test generic error"):
                await convert_file("path/to/file")

    async def test_convert_batch_value_error(self):
        from to_markdown.mcp.server import convert_batch

        with patch(
            "to_markdown.mcp.server.handle_convert_batch",
            side_effect=ValueError("test batch value error"),
        ):
            with pytest.raises(ToolError, match="test batch value error"):
                await convert_batch("path/to/dir")

    async def test_convert_batch_generic_error(self):
        from to_markdown.mcp.server import convert_batch

        with patch(
            "to_markdown.mcp.server.handle_convert_batch",
            side_effect=Exception("test batch generic error"),
        ):
            with pytest.raises(ToolError, match="Batch conversion failed: test batch generic error"):
                await convert_batch("path/to/dir")

    def test_start_conversion_value_error(self):
        from to_markdown.mcp.server import start_conversion

        with patch(
            "to_markdown.mcp.server.handle_start_conversion",
            side_effect=ValueError("test start value error"),
        ):
            with pytest.raises(ToolError, match="test start value error"):
                start_conversion("path/to/file")

    def test_start_conversion_generic_error(self):
        from to_markdown.mcp.server import start_conversion

        with patch(
            "to_markdown.mcp.server.handle_start_conversion",
            side_effect=Exception("test start generic error"),
        ):
            with pytest.raises(ToolError, match="Failed to start conversion: test start generic error"):
                start_conversion("path/to/file")

    def test_get_task_status_value_error(self):
        from to_markdown.mcp.server import get_task_status

        with patch(
            "to_markdown.mcp.server.handle_get_task_status",
            side_effect=ValueError("test get status value error"),
        ):
            with pytest.raises(ToolError, match="test get status value error"):
                get_task_status("task-123")

    def test_get_task_status_generic_error(self):
        from to_markdown.mcp.server import get_task_status

        with patch(
            "to_markdown.mcp.server.handle_get_task_status",
            side_effect=Exception("test get status generic error"),
        ):
            with pytest.raises(ToolError, match="Failed to get task status: test get status generic error"):
                get_task_status("task-123")

    def test_cancel_task_value_error(self):
        from to_markdown.mcp.server import cancel_task

        with patch(
            "to_markdown.mcp.server.handle_cancel_task",
            side_effect=ValueError("test cancel value error"),
        ):
            with pytest.raises(ToolError, match="test cancel value error"):
                cancel_task("task-123")

    def test_cancel_task_generic_error(self):
        from to_markdown.mcp.server import cancel_task

        with patch(
            "to_markdown.mcp.server.handle_cancel_task",
            side_effect=Exception("test cancel generic error"),
        ):
            with pytest.raises(ToolError, match="Failed to cancel task: test cancel generic error"):
                cancel_task("task-123")

    def test_list_tasks_generic_error(self):
        from to_markdown.mcp.server import list_tasks

        with patch(
            "to_markdown.mcp.server.handle_list_tasks",
            side_effect=Exception("test list tasks generic error"),
        ):
            with pytest.raises(ToolError, match="Failed to list tasks: test list tasks generic error"):
                list_tasks()
