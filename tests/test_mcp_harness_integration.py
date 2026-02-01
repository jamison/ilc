"""
MCP Harness Integration Tests.

Validates tool payloads against the MCP schema and ensures
additionalProperties enforcement works correctly.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ilc_core.mcp.schema import (
    load_mcp_tools_schema,
    get_tool_schema,
    validate_tool_payload,
)


# Path to fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mcp"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


class TestSchemaLoader:
    """Test schema loading utilities."""

    def test_load_schema_succeeds(self) -> None:
        """Schema file loads successfully."""
        schema = load_mcp_tools_schema()
        assert "tools" in schema
        assert "name" in schema

    def test_schema_loads_from_package_resources(self) -> None:
        """Schema can be loaded via importlib.resources from package."""
        from importlib import resources
        
        pkg_files = resources.files("ilc_core.mcp.schemas")
        schema_file = pkg_files.joinpath("ilc_mcp_tools_mvp_schema_v0.1.json")
        # Assert file exists and is readable
        with schema_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert "tools" in data

    def test_all_four_tools_present(self) -> None:
        """All MVP tools are defined in schema."""
        schema = load_mcp_tools_schema()
        tool_names = {t["name"] for t in schema["tools"]}
        
        expected = {
            "ilc.capabilities.get",
            "ilc.task.get",
            "ilc.block.get",
            "ilc.bundle.submit",
        }
        assert expected.issubset(tool_names)

    def test_get_tool_schema_found(self) -> None:
        """get_tool_schema returns matching tool."""
        schema = load_mcp_tools_schema()
        tool = get_tool_schema(schema, "ilc.capabilities.get")
        assert tool["name"] == "ilc.capabilities.get"

    def test_get_tool_schema_not_found(self) -> None:
        """get_tool_schema raises KeyError for missing tool."""
        schema = load_mcp_tools_schema()
        with pytest.raises(KeyError):
            get_tool_schema(schema, "ilc.nonexistent.tool")


class TestCapabilitiesGet:
    """Test ilc.capabilities.get payloads."""

    @pytest.fixture
    def tool_schema(self) -> dict:
        schema = load_mcp_tools_schema()
        return get_tool_schema(schema, "ilc.capabilities.get")

    def test_valid_input(self, tool_schema) -> None:
        """Valid input payload passes validation."""
        payload = load_fixture("capabilities_get_input.json")
        validate_tool_payload(tool_schema, payload, mode="input")

    def test_valid_output(self, tool_schema) -> None:
        """Valid output payload passes validation."""
        payload = load_fixture("capabilities_get_output.json")
        validate_tool_payload(tool_schema, payload, mode="output")

    def test_input_rejects_extra_property(self, tool_schema) -> None:
        """Input rejects additional properties."""
        payload = {"extra_key": "not_allowed"}
        with pytest.raises(ValueError) as exc_info:
            validate_tool_payload(tool_schema, payload, mode="input")
        assert "extra_key" in str(exc_info.value).lower() or "additional" in str(exc_info.value).lower()


class TestTaskGet:
    """Test ilc.task.get payloads."""

    @pytest.fixture
    def tool_schema(self) -> dict:
        schema = load_mcp_tools_schema()
        return get_tool_schema(schema, "ilc.task.get")

    def test_valid_input(self, tool_schema) -> None:
        """Valid input payload passes validation."""
        payload = load_fixture("task_get_input.json")
        validate_tool_payload(tool_schema, payload, mode="input")

    def test_valid_output(self, tool_schema) -> None:
        """Valid output payload passes validation."""
        payload = load_fixture("task_get_output.json")
        validate_tool_payload(tool_schema, payload, mode="output")

    def test_input_rejects_extra_property(self, tool_schema) -> None:
        """Input rejects additional properties."""
        payload = {"filters": {}, "unknown_field": True}
        with pytest.raises(ValueError):
            validate_tool_payload(tool_schema, payload, mode="input")


class TestBlockGet:
    """Test ilc.block.get payloads."""

    @pytest.fixture
    def tool_schema(self) -> dict:
        schema = load_mcp_tools_schema()
        return get_tool_schema(schema, "ilc.block.get")

    def test_valid_input(self, tool_schema) -> None:
        """Valid input payload passes validation."""
        payload = load_fixture("block_get_input.json")
        validate_tool_payload(tool_schema, payload, mode="input")

    def test_valid_output(self, tool_schema) -> None:
        """Valid output payload passes validation."""
        payload = load_fixture("block_get_output.json")
        validate_tool_payload(tool_schema, payload, mode="output")

    def test_input_rejects_extra_property(self, tool_schema) -> None:
        """Input rejects additional properties."""
        payload = {"cid": "bafy...", "not_valid": 123}
        with pytest.raises(ValueError):
            validate_tool_payload(tool_schema, payload, mode="input")


class TestBundleSubmit:
    """Test ilc.bundle.submit payloads."""

    @pytest.fixture
    def tool_schema(self) -> dict:
        schema = load_mcp_tools_schema()
        return get_tool_schema(schema, "ilc.bundle.submit")

    def test_valid_input(self, tool_schema) -> None:
        """Valid input payload passes validation."""
        payload = load_fixture("bundle_submit_input.json")
        validate_tool_payload(tool_schema, payload, mode="input")

    def test_valid_output(self, tool_schema) -> None:
        """Valid output payload passes validation."""
        payload = load_fixture("bundle_submit_output.json")
        validate_tool_payload(tool_schema, payload, mode="output")

    def test_input_rejects_extra_property(self, tool_schema) -> None:
        """Input rejects additional properties."""
        payload = {"task_id": "t1", "roots": ["cid1"], "bad_key": "nope"}
        with pytest.raises(ValueError):
            validate_tool_payload(tool_schema, payload, mode="input")
