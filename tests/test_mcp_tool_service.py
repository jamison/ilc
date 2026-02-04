"""
MCP Tool Service Tests.

Tests for the in-process MCP tool service.
"""

import json
import tempfile
from pathlib import Path

import jsonschema
import pytest

import ilc_core.mcp.service as svc_module
from ilc_core.node.node_v0 import ILCNodeV0
from ilc_core.mcp.node_service import NodeMCPToolService
from ilc_core.mcp.service import _load_audit_schema, _AUDIT_SCHEMA
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
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            node_service = NodeMCPToolService(node)
            
            node_service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1
            assert events[0].kind == "mcp_tool_call"

    def test_mcp_tool_call_logged_on_output_error(self) -> None:
        """Output validation failure is logged with status=error."""
        
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

    def test_mcp_audit_payload_schema_valid(self) -> None:
        """Logged audit payload validates against mcp_tool_call schema."""
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log, node_id="test-node-id")
            
            # Call a tool
            service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1
            
            # Validate payload against schema
            schema = _load_audit_schema()
            jsonschema.validate(instance=events[0].payload, schema=schema)
            
            # Check key fields
            assert events[0].payload["tool_name"] == "ilc.capabilities.get"
            assert events[0].payload["status"] == "ok"
            assert events[0].payload["node_id"] == "test-node-id"

    def test_mcp_audit_payload_schema_error_requires_error(self) -> None:
        """Error status events include error field and validate against schema."""
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(event_log=node.event_log, node_id="test-node-id")
            
            # Trigger an input validation error (missing required "cid" field)
            try:
                service.handle_request("ilc.block.get", {"want": "raw"})
            except ValueError:
                pass
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1
            
            # Validate payload against schema (error status requires error field)
            schema = _load_audit_schema()
            jsonschema.validate(instance=events[0].payload, schema=schema)
            
            # Check error is present
            assert events[0].payload["status"] == "error"
            assert "error" in events[0].payload

    def test_audit_sample_rate_zero(self) -> None:
        """sample_rate=0.0 logs no events."""
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(
                event_log=node.event_log,
                audit_sample_rate=0.0,
                audit_rng_seed=42,
            )
            
            # Call tool multiple times
            for _ in range(10):
                service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 0

    def test_audit_sample_rate_one(self) -> None:
        """sample_rate=1.0 logs all events."""
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            service = MCPToolService(
                event_log=node.event_log,
                audit_sample_rate=1.0,
                audit_rng_seed=42,
            )
            
            # Call tool multiple times
            for _ in range(5):
                service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 5

    def test_audit_rate_limit(self) -> None:
        """max_per_minute=1 drops events beyond the limit."""
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            node = ILCNodeV0(node_id="test-node", data_dir=Path(tmp_dir) / "data")
            # Fixed clock at minute 100
            fixed_clock = lambda: 6000.0
            service = MCPToolService(
                event_log=node.event_log,
                audit_max_per_minute=1,
                audit_clock=fixed_clock,
            )
            
            # First call logs
            service.handle_request("ilc.capabilities.get", {})
            # Second call should be dropped
            service.handle_request("ilc.capabilities.get", {})
            
            events = list(node.event_log.iter_events())
            assert len(events) == 1

    def test_audit_schema_loads_from_package(self) -> None:
        """Schema loads via package resources, not docs path."""
        import importlib.resources
        
        # Clear cached schema
        svc_module._AUDIT_SCHEMA = None
        
        # Load schema (should work via package resources)
        schema = _load_audit_schema()
        
        # Verify schema loaded successfully
        assert schema is not None
        assert schema.get("$id") == "mcp_tool_call_event_schema_v0.1"
        assert "tool_name" in schema.get("properties", {})
