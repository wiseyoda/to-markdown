"""Tests for MCP server setup and tool registration (mcp/server.py)."""


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

    def test_exactly_four_tools_registered(self):
        from to_markdown.mcp.server import mcp

        tools = mcp._tool_manager.list_tools()
        assert len(tools) == 4


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
        for param in ["clean", "summary", "images"]:
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
            handle_convert_batch,
            handle_convert_file,
            handle_get_status,
            handle_list_formats,
        )

        assert all(
            callable(f)
            for f in [
                handle_convert_file,
                handle_convert_batch,
                handle_list_formats,
                handle_get_status,
            ]
        )
