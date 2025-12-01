import json
import sys
from io import StringIO
from fastapi.testclient import TestClient
from ilc_core.server import app
from ilc_core.cli.ep_task_cli import run_ep_task_cli

client = TestClient(app)

def test_cli_schema(capsys):
    """Test 'schema' subcommand prints JSON schema."""
    exit_code = run_ep_task_cli(["schema"], client=client)
    assert exit_code == 0
    
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "properties" in output
    assert "EpistemicWorkTask" in output.get("title", "")

def test_cli_submit_stdin(capsys, monkeypatch):
    """Test 'submit' subcommand reading from stdin."""
    payload = {
        "task_id": "task:cli:test",
        "task_class": "star.map.embedding",
        "agent_id": "agent:cli",
        "region_scope": ["global"],
        "difficulty_factor": 1.0,
        "verification_method": "hash-match",
        "task_state": "proposed",
        "timestamp_created": 1700000000,
        "ecu.estimate": 0.5,
    }
    
    # Mock stdin
    monkeypatch.setattr("sys.stdin", StringIO(json.dumps(payload)))
    
    exit_code = run_ep_task_cli(["submit"], client=client)
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "Accepted EpistemicWorkTask" in captured.out
    assert "task:cli:test" in captured.out

def test_cli_demo(capsys):
    """Test 'demo' subcommand."""
    exit_code = run_ep_task_cli(["demo"], client=client)
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "Success!" in captured.out
    assert "task:demo:cli" in captured.out
