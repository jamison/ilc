import json
import sys
from io import StringIO
from unittest.mock import Mock

from fastapi.testclient import TestClient
from ilc_core.asgi import app
from ilc_core.cli.ep_task_cli import (
    CONNECT_TIMEOUT_S,
    READ_TIMEOUT_S,
    HttpClient,
    run_ep_task_cli,
)

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
        "difficulty_factor": "1.0",
        "verification_method": "hash-match",
        "task_state": "proposed",
        "timestamp_created": 1700000000,
        "ecu.estimate": "0.5",
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


def test_http_client_get_uses_bifurcated_timeouts(monkeypatch):
    response = Mock()
    called = {}

    def fake_get(url, timeout):
        called["url"] = url
        called["timeout"] = timeout
        return response

    monkeypatch.setattr("ilc_core.cli.ep_task_cli.requests.get", fake_get)
    client_wrapper = HttpClient("http://127.0.0.1:8000")
    assert client_wrapper.get("/test") is response
    assert called["url"] == "http://127.0.0.1:8000/test"
    assert called["timeout"] == (CONNECT_TIMEOUT_S, READ_TIMEOUT_S)


def test_http_client_post_uses_bifurcated_timeouts(monkeypatch):
    response = Mock()
    called = {}

    def fake_post(url, json, timeout):
        called["url"] = url
        called["json"] = json
        called["timeout"] = timeout
        return response

    monkeypatch.setattr("ilc_core.cli.ep_task_cli.requests.post", fake_post)
    client_wrapper = HttpClient("http://127.0.0.1:8000")
    assert client_wrapper.post("/test", {"ok": True}) is response
    assert called["url"] == "http://127.0.0.1:8000/test"
    assert called["json"] == {"ok": True}
    assert called["timeout"] == (CONNECT_TIMEOUT_S, READ_TIMEOUT_S)
