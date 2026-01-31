"""
MCP Tool Service Tests.

Tests for the in-process MCP tool service.
"""

import pytest

from ilc_core.mcp.service import MCPToolService
from ilc_core.mcp.schema import (
    load_mcp_tools_schema,
    get_tool_schema,
    validate_tool_payload,
)


class TestMCPToolService:
    """Tests for MCPToolService."""

    def test_capabilities_get_returns_valid_output(self) -> None:
        """ilc.capabilities.get returns schema-valid output."""
        service = MCPToolService()
        schema = load_mcp_tools_schema()
        tool_schema = get_tool_schema(schema, "ilc.capabilities.get")
        
        # Input is empty object per schema
        result = service.handle_request("ilc.capabilities.get", {})
        
        # Should not raise
        validate_tool_payload(tool_schema, result, mode="output")
        assert "protocol_version" in result
        assert "supported_codecs" in result

    def test_task_get_returns_valid_output(self) -> None:
        """ilc.task.get returns schema-valid output."""
        service = MCPToolService()
        schema = load_mcp_tools_schema()
        tool_schema = get_tool_schema(schema, "ilc.task.get")
        
        # Input uses filters object per schema
        result = service.handle_request("ilc.task.get", {
            "filters": {"task_class": "custom", "limit": 5},
        })
        
        validate_tool_payload(tool_schema, result, mode="output")
        assert "tasks" in result

    def test_block_get_returns_valid_output(self) -> None:
        """ilc.block.get returns schema-valid output."""
        service = MCPToolService()
        schema = load_mcp_tools_schema()
        tool_schema = get_tool_schema(schema, "ilc.block.get")
        
        # Input uses cid per schema
        result = service.handle_request("ilc.block.get", {
            "cid": "bafyreihash123",
            "want": "raw",
            "allow_inline_bytes": True,
        })
        
        validate_tool_payload(tool_schema, result, mode="output")
        assert result["cid"] == "bafyreihash123"

    def test_bundle_submit_returns_valid_output(self) -> None:
        """ilc.bundle.submit returns schema-valid output."""
        service = MCPToolService()
        schema = load_mcp_tools_schema()
        tool_schema = get_tool_schema(schema, "ilc.bundle.submit")
        
        # Input uses task_id and roots per schema
        result = service.handle_request("ilc.bundle.submit", {
            "task_id": "task-001",
            "roots": ["bafyreihash123"],
            "blocks_inline": [
                {"cid": "bafyreihash123", "bytes_b64": "AAAA"},
            ],
        })
        
        validate_tool_payload(tool_schema, result, mode="output")
        assert result["accepted"] is True

    def test_unknown_tool_rejected(self) -> None:
        """Unknown tool names are rejected."""
        service = MCPToolService()
        
        with pytest.raises(ValueError, match="Unknown tool"):
            service.handle_request("ilc.nonexistent.tool", {})

    def test_invalid_payload_rejected_block_get(self) -> None:
        """Invalid payload for ilc.block.get is rejected (missing required cid)."""
        service = MCPToolService()
        
        # cid is required but missing
        with pytest.raises(ValueError):
            service.handle_request("ilc.block.get", {
                "want": "raw",
            })

    def test_invalid_payload_rejected_bundle_submit(self) -> None:
        """Invalid payload for ilc.bundle.submit is rejected (missing required fields)."""
        service = MCPToolService()
        
        # Missing required task_id and roots
        with pytest.raises(ValueError):
            service.handle_request("ilc.bundle.submit", {})

    def test_output_validation_enforced(self) -> None:
        """Output validation is enforced - invalid output raises ValueError."""
        service = MCPToolService()
        
        # Monkeypatch handler to return invalid output
        original_handler = service._handle_capabilities_get
        
        def bad_handler(payload):
            # Missing required fields like supported_codecs
            return {"protocol_version": "0.1"}
        
        service._handle_capabilities_get = bad_handler
        
        try:
            with pytest.raises(ValueError, match="Validation failed for output"):
                service.handle_request("ilc.capabilities.get", {})
        finally:
            service._handle_capabilities_get = original_handler

    def test_block_get_omits_bytes_when_not_allowed(self) -> None:
        """block.get omits bytes_b64 when allow_inline_bytes is False."""
        service = MCPToolService()
        
        result = service.handle_request("ilc.block.get", {
            "cid": "bafyreihash123",
            "want": "raw",
            "allow_inline_bytes": False,
        })
        
        assert "bytes_b64" not in result
        assert result["cid"] == "bafyreihash123"
        assert result["codec"] == "dag-cbor"
        assert result["size_bytes"] == 0


class TestMCPAuditTrail:
    """Tests for MCP audit trail logging."""

    def test_mcp_tool_call_logged_on_success(self) -> None:
        """Successful tool call is logged with status=ok."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log)
            
            service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1
            assert events[0].kind == "mcp_tool_call"
            assert events[0].payload["tool_name"] == "ilc.capabilities.get"
            assert events[0].payload["status"] == "ok"
            assert "input" in events[0].payload
            assert "output" in events[0].payload

    def test_mcp_tool_call_logged_on_error(self) -> None:
        """Failed tool call is logged with status=error."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log)
            
            # Invalid input - missing required cid
            try:
                service.handle_request("ilc.block.get", {"want": "raw"})
            except ValueError:
                pass
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1
            assert events[0].kind == "mcp_tool_call"
            assert events[0].payload["status"] == "error"
            assert "error" in events[0].payload
            assert events[0].payload["tool_name"] == "ilc.block.get"

    def test_mcp_tool_call_payload_guard(self) -> None:
        """Large payloads are summarized with digest."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        from ilc_core.mcp import service as svc_module
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log)
            
            # Temporarily lower threshold to trigger guard
            original_threshold = svc_module.PAYLOAD_SIZE_THRESHOLD
            svc_module.PAYLOAD_SIZE_THRESHOLD = 50
            
            try:
                service.handle_request("ilc.capabilities.get", {})
                
                events = list(node.event_log.iter_events())
                assert len(events) == 1
                # Output should be summarized (it's larger than 50 bytes)
                assert "output_summary" in events[0].payload
                assert "output_digest" in events[0].payload
                assert "output" not in events[0].payload
            finally:
                svc_module.PAYLOAD_SIZE_THRESHOLD = original_threshold

    def test_node_mcp_tool_service_logs_via_node(self) -> None:
        """NodeMCPToolService logs events to the node."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        from ilc_core.mcp.node_service import NodeMCPToolService
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            node_service = NodeMCPToolService(node)
            
            node_service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1
            assert events[0].kind == "mcp_tool_call"

    def test_mcp_tool_call_logged_on_output_error(self) -> None:
        """Output validation failure is logged with status=error."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log)
            
            # Monkeypatch handler to return invalid output
            original_handler = service._handle_capabilities_get
            
            def bad_handler(payload):
                # Missing required fields
                return {"protocol_version": "0.1"}
            
            service._handle_capabilities_get = bad_handler
            
            try:
                with pytest.raises(ValueError, match="Validation failed for output"):
                    service.handle_request("ilc.capabilities.get", {})
                
                events = list(node.event_log.iter_events())
                assert len(events) == 1
                assert events[0].kind == "mcp_tool_call"
                assert events[0].payload["status"] == "error"
                assert "error" in events[0].payload
                assert "output" in events[0].payload or "output_summary" in events[0].payload
            finally:
                service._handle_capabilities_get = original_handler

    def test_mcp_audit_redacts_bytes_b64(self) -> None:
        """Audit log redacts bytes_b64 fields from inline blocks."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log, node_id="test")
            
            # Call bundle.submit with blocks_inline containing bytes_b64
            payload = {
                "task_id": "test-task",
                "roots": ["bafyroot1"],
                "blocks_inline": [
                    {
                        "cid": "bafyblock1",
                        "bytes_b64": "c2Vuc2l0aXZlIGRhdGE=",
                    }
                ],
            }
            
            try:
                service.handle_request("ilc.bundle.submit", payload)
            except ValueError:
                pass  # Output validation may fail on stub, that's OK
            
            events = list(node.event_log.iter_events())
            assert len(events) >= 1
            
            # Check that raw bytes_b64 is NOT in log
            log_content = (Path(tmp_dir) / "data" / "event_log.ndjson").read_text()
            assert "c2Vuc2l0aXZlIGRhdGE=" not in log_content
            assert '"redacted": true' in log_content or '"redacted":true' in log_content

    def test_mcp_audit_redacts_bundle_bytes(self) -> None:
        """Audit log redacts bundle_bytes_b64 fields."""
        import tempfile
        from pathlib import Path
        from ilc_core.node.node_v0 import ILCNodeV0
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log, node_id="test")
            
            # Call bundle.submit with bundle_bytes_b64
            payload = {
                "task_id": "test-task",
                "roots": ["bafyroot1"],
                "bundle_bytes_b64": "bGFyZ2UgYnVuZGxlIGRhdGE=",
            }
            
            try:
                service.handle_request("ilc.bundle.submit", payload)
            except ValueError:
                pass  # Output validation may fail on stub
            
            events = list(node.event_log.iter_events())
            assert len(events) >= 1
            
            # Check that raw bundle_bytes_b64 is NOT in log
            log_content = (Path(tmp_dir) / "data" / "event_log.ndjson").read_text()
            assert "bGFyZ2UgYnVuZGxlIGRhdGE=" not in log_content
            assert '"redacted": true' in log_content or '"redacted":true' in log_content




