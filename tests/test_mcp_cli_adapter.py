"""
MCP CLI Adapter Tests.

Tests for the MCP command-line interface.
"""

import json
import subprocess
import tempfile
from pathlib import Path


class TestMCPCLIAdapter:
    """Tests for mcp_cli.py."""

    def test_cli_invokes_tool_and_logs(self) -> None:
        """CLI invokes tool and creates audit log."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "ilc_core.cli.mcp_cli",
                    "--tool",
                    "ilc.capabilities.get",
                    "--payload",
                    "{}",
                    "--data-dir",
                    tmp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent),
            )
            
            assert result.returncode == 0, f"CLI failed: {result.stderr}"
            
            # Verify stdout is valid JSON with expected field
            output = json.loads(result.stdout.strip())
            assert "protocol_version" in output
            
            # Verify audit log exists with mcp_tool_call event
            log_file = Path(tmp_dir) / "event_log.ndjson"
            assert log_file.exists(), "Event log file should exist"
            
            log_content = log_file.read_text()
            assert "mcp_tool_call" in log_content

    def test_cli_rejects_invalid_json(self) -> None:
        """CLI exits non-zero for invalid JSON payload."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "ilc_core.cli.mcp_cli",
                    "--tool",
                    "ilc.capabilities.get",
                    "--payload",
                    "{invalid json",
                    "--data-dir",
                    tmp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent),
            )
            
            assert result.returncode != 0
            assert "Invalid JSON" in result.stderr
