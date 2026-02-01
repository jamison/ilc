"""
MCP Schema Parity Test.

Ensures the packaged schema in ilc_core/mcp/schemas matches the
authoritative docs copy in docs/mcp.
"""

import json
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestSchemaParityDocsVsPackage:
    """Verify docs schema matches packaged schema."""

    def test_docs_schema_equals_packaged_schema(self) -> None:
        """docs/mcp schema must match ilc_core/mcp/schemas copy."""
        docs_path = PROJECT_ROOT / "docs" / "mcp" / "ilc_mcp_tools_mvp_schema_v0.1.json"
        packaged_path = PROJECT_ROOT / "ilc_core" / "mcp" / "schemas" / "ilc_mcp_tools_mvp_schema_v0.1.json"
        
        # Both files must exist
        assert docs_path.exists(), f"Docs schema not found: {docs_path}"
        assert packaged_path.exists(), f"Packaged schema not found: {packaged_path}"
        
        # Load both
        with open(docs_path, "r", encoding="utf-8") as f:
            docs_schema = json.load(f)
        
        with open(packaged_path, "r", encoding="utf-8") as f:
            packaged_schema = json.load(f)
        
        # Deep equality
        assert docs_schema == packaged_schema, (
            "Schema drift detected: docs/mcp and ilc_core/mcp/schemas must be identical"
        )
