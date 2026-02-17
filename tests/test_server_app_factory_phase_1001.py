from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

import ilc_core.server as server
from ilc_core.asgi import app


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_server_module_no_longer_instantiates_app_at_import_time() -> None:
    assert not hasattr(server, "app")
    assert callable(server.create_app)


def test_asgi_module_exposes_app_instance() -> None:
    assert isinstance(app, FastAPI)


def test_run_node_uses_factory_path() -> None:
    text = (_repo_root() / "run_node.py").read_text(encoding="utf-8")
    assert 'uvicorn.run("ilc_core.server:create_app"' in text
    assert "factory=True" in text
