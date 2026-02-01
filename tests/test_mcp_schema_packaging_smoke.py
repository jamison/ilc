"""
MCP Schema Packaging Smoke Test.

Verifies schema loading works via package resources without repo-relative fallback.
Also includes fixture/schema drift guard to ensure all fixtures validate.
"""

import json
from pathlib import Path
from unittest import mock

import pytest

# Project root for fixture enumeration
PROJECT_ROOT = Path(__file__).parent.parent


class TestPackageResourceSmoke:
    """Verify schema loads via package resources, not repo fallback."""

    def test_loads_via_importlib_resources(self) -> None:
        """Schema loads from package resources when repo paths unavailable."""
        resources_called = {"called": False}
        
        # Save original functions
        from importlib import resources as real_resources
        from ilc_core.mcp import schema as schema_module
        
        original_files = real_resources.files
        
        def mock_files(package: str):
            if package == "ilc_core.mcp.schemas":
                resources_called["called"] = True
            return original_files(package)
        
        # Patch Path.exists to block fallback path search
        original_exists = Path.exists
        
        def mock_exists(self) -> bool:
            # Block any docs/mcp path
            if "docs/mcp" in str(self):
                return False
            return original_exists(self)
        
        with mock.patch.object(Path, "exists", mock_exists):
            with mock.patch.object(real_resources, "files", mock_files):
                # Reload to use patched functions
                result = schema_module.load_mcp_tools_schema()
        
        assert resources_called["called"], "importlib.resources was not used"
        assert "tools" in result
        assert "name" in result


class TestFixtureSchemaDriftGuard:
    """Ensure all MCP fixtures validate against their schema definitions."""

    def test_all_fixtures_validate_against_schema(self) -> None:
        """Every fixture file must pass schema validation."""
        from ilc_core.mcp.schema import (
            load_mcp_tools_schema,
            get_tool_schema,
            validate_tool_payload,
        )
        
        fixtures_dir = PROJECT_ROOT / "tests" / "fixtures" / "mcp"
        schema = load_mcp_tools_schema()
        
        # Map fixture prefix to tool name
        fixture_tool_map = {
            "capabilities_get": "ilc.capabilities.get",
            "task_get": "ilc.task.get",
            "block_get": "ilc.block.get",
            "bundle_submit": "ilc.bundle.submit",
        }
        
        fixture_files = list(fixtures_dir.glob("*.json"))
        assert len(fixture_files) > 0, "No fixture files found"
        
        validated_count = 0
        
        for fixture_path in fixture_files:
            name = fixture_path.stem  # e.g., "capabilities_get_input"
            
            # Determine mode from suffix
            if name.endswith("_input"):
                mode = "input"
                prefix = name[:-6]  # Remove "_input"
            elif name.endswith("_output"):
                mode = "output"
                prefix = name[:-7]  # Remove "_output"
            else:
                pytest.fail(f"Fixture {name} must end with _input or _output")
            
            # Resolve tool name
            tool_name = fixture_tool_map.get(prefix)
            assert tool_name is not None, (
                f"Unknown fixture prefix '{prefix}' in {fixture_path.name}. "
                f"Add mapping to fixture_tool_map."
            )
            
            # Load and validate
            with open(fixture_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            
            tool_schema = get_tool_schema(schema, tool_name)
            
            try:
                validate_tool_payload(tool_schema, payload, mode=mode)
                validated_count += 1
            except ValueError as e:
                pytest.fail(
                    f"Fixture {fixture_path.name} failed validation: {e}"
                )
        
        # Sanity check: we validated all 8 expected fixtures
        assert validated_count == 8, f"Expected 8 fixtures, validated {validated_count}"
