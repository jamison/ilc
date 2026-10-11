from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ilc_core.cli import d2e_submit_cli
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.identity.bls_backend import keypair_from_ikm_hex


TEST_SECRET_HEX, TEST_AGENT_ID = keypair_from_ikm_hex("6d" * 32)


def _submit_args(**overrides: Any) -> argparse.Namespace:
    values: dict[str, Any] = {
        "primitive": "assert.truth",
        "payload_json": json.dumps(
            {
                "content": {"claim": "native QUIC CLI wiring smoke"},
                "primitive_type": "observation",
                "epistemic_type": "objective",
                "parent_node_ids": [],
            },
            separators=(",", ":"),
            sort_keys=True,
        ),
        "payload_file": None,
        "agent_id": TEST_AGENT_ID,
        "epoch": 1,
        "sig": "UNSIGNED",
        "signing_key": None,
        "source_refs": [],
        "endpoint": "",
        "quic_endpoint": "127.0.0.1:4433",
        "tls_fingerprint": "",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


@pytest.fixture(autouse=True)
def _isolate_submit_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", TEST_SECRET_HEX)
    monkeypatch.delenv("ILC_TRUTH_SUBMIT_ENDPOINT", raising=False)
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    monkeypatch.setattr(
        d2e_submit_cli,
        "_ILC_AGENT_BLS_KEY_DEFAULT_PATH",
        tmp_path / "no-default-key.hex",
    )


def test_submit_help_lists_quic_flags() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "submit", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--quic-endpoint" in result.stdout
    assert "--tls-fingerprint" in result.stdout


def test_quic_endpoint_validation_rejects_malformed_values() -> None:
    for value in ["", "https://example.test:443", "example.test/path", "user@example.test:443", "example.test:0"]:
        args = _submit_args(quic_endpoint=value)
        if not value:
            assert d2e_submit_cli._quic_endpoint_from_args(args) == ""
            continue
        with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
            d2e_submit_cli._quic_endpoint_from_args(args)
        assert exc_info.value.token == "submit_quic_endpoint_invalid"


def test_tls_fingerprint_validation_requires_lowercase_sha256_hex() -> None:
    assert d2e_submit_cli._tls_fingerprint_from_args(
        _submit_args(tls_fingerprint="a" * 64)
    ) == "a" * 64

    for value in ["A" * 64, "a" * 63, "g" * 64]:
        with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
            d2e_submit_cli._tls_fingerprint_from_args(_submit_args(tls_fingerprint=value))
        assert exc_info.value.token == "submit_quic_tls_fingerprint_invalid"


def test_quic_transport_rejects_https_endpoint_conflict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
        d2e_submit_cli.handle_submit(
            _submit_args(endpoint="https://validator.example/api/v1/truth/submit")
        )
    assert exc_info.value.token == "submit_transport_ambiguous"

    monkeypatch.setenv("ILC_TRUTH_SUBMIT_ENDPOINT", "https://validator.example/api/v1/truth/submit")
    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info_env:
        d2e_submit_cli.handle_submit(_submit_args())
    assert exc_info_env.value.token == "submit_transport_ambiguous"


def test_submit_quic_dispatch_requires_client_binary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ilc_core.consensus.binary_paths.installed_consensus_binary_command",
        lambda _name: None,
    )

    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
        d2e_submit_cli._submit_quic_dispatch(
            {"ok": True},
            quic_endpoint="127.0.0.1:4433",
            tls_fingerprint=None,
        )

    assert exc_info.value.token == "native_submit_client_binary_not_found"


def test_handle_submit_quic_dispatches_canonical_json_without_newline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    node_id = node_id_from_obj({"phase": "GAP-NATIVE-QUIC-RECEIVER-CLI-00", "case": "ok"})
    seen: dict[str, Any] = {}

    def fake_run(
        argv: list[str],
        *,
        input: bytes,
        stdout: int,
        stderr: int,
        timeout: int,
        check: bool,
    ) -> subprocess.CompletedProcess[bytes]:
        seen["argv"] = argv
        seen["input"] = input
        seen["stdout"] = stdout
        seen["stderr"] = stderr
        seen["timeout"] = timeout
        seen["check"] = check
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "receipt": {
                        "node_id": node_id,
                        "nodes_written": 1,
                        "edges_written": 0,
                        "native_submit_replay_written": 1,
                        "primitive": "assert.truth",
                    },
                    "node_id": node_id,
                    "primitive": "assert.truth",
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8"),
            stderr=b"",
        )

    monkeypatch.setattr(
        "ilc_core.consensus.binary_paths.installed_consensus_binary_command",
        lambda name: ("/tmp/ilc_native_submit_client",) if name == "ilc_native_submit_client" else None,
    )
    monkeypatch.setattr(d2e_submit_cli.subprocess, "run", fake_run)

    result = d2e_submit_cli.handle_submit(
        _submit_args(tls_fingerprint="b" * 64)
    )

    assert seen["argv"] == [
        "/tmp/ilc_native_submit_client",
        "--endpoint",
        "127.0.0.1:4433",
        "--expected-tls-fingerprint",
        "b" * 64,
    ]
    assert seen["input"].endswith(b"}")
    assert b"\n" not in seen["input"]
    submitted = json.loads(seen["input"].decode("utf-8"))
    assert submitted["agent_id"] == TEST_AGENT_ID
    assert isinstance(submitted["sig"], dict)
    assert submitted["sig"]["schema_version"] == "native_submit_sig.v0.1"
    assert result["node_id"] == node_id
    assert result["graph_persistence"] == "persisted"
    assert result["native_quic_endpoint"] == "127.0.0.1:4433"
    assert result["native_submit_sig"]["key_ref"] == TEST_AGENT_ID


def test_quic_dispatch_propagates_client_error_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ilc_core.consensus.binary_paths.installed_consensus_binary_command",
        lambda _name: ("/tmp/ilc_native_submit_client",),
    )
    monkeypatch.setattr(
        d2e_submit_cli.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args,
            1,
            stdout=b'{"ok":false,"error":"native_submit_sig_invalid_CDL_118"}',
            stderr=b"native_submit_sig_invalid_CDL_118",
        ),
    )

    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
        d2e_submit_cli._submit_quic_dispatch(
            {"v": 1},
            quic_endpoint="127.0.0.1:4433",
            tls_fingerprint=None,
        )

    assert exc_info.value.token == "native_submit_sig_invalid_CDL_118"


def test_quic_dispatch_rejects_oversized_or_invalid_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ilc_core.consensus.binary_paths.installed_consensus_binary_command",
        lambda _name: ("/tmp/ilc_native_submit_client",),
    )
    monkeypatch.setattr(
        d2e_submit_cli.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args,
            0,
            stdout=b"x" * (d2e_submit_cli._MAX_SUBMIT_ENDPOINT_RESPONSE_BYTES + 1),
            stderr=b"",
        ),
    )
    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
        d2e_submit_cli._submit_quic_dispatch(
            {"v": 1},
            quic_endpoint="127.0.0.1:4433",
            tls_fingerprint=None,
        )
    assert exc_info.value.token == "native_submit_quic_response_too_large"

    monkeypatch.setattr(
        d2e_submit_cli.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args,
            0,
            stdout=b"not json",
            stderr=b"",
        ),
    )
    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info_json:
        d2e_submit_cli._submit_quic_dispatch(
            {"v": 1},
            quic_endpoint="127.0.0.1:4433",
            tls_fingerprint=None,
        )
    assert exc_info_json.value.token == "native_submit_quic_response_invalid_json"


def test_https_path_still_uses_https_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    node_id = node_id_from_obj({"phase": "GAP-NATIVE-QUIC-RECEIVER-CLI-00", "case": "https"})
    seen: dict[str, Any] = {}

    class Response:
        def __init__(self) -> None:
            self._sent = False

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self, _limit: int) -> bytes:
            if self._sent:
                return b""
            self._sent = True
            return json.dumps(
                {
                    "ok": True,
                    "data": {
                        "node_id": node_id,
                        "edges": [],
                        "graph_persistence": "persisted",
                        "gossip_delivery": "deferred",
                    },
                }
            ).encode("utf-8")

    def fake_open(request: object, *, timeout: float) -> Response:
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data.decode("utf-8"))
        seen["timeout"] = timeout
        return Response()

    monkeypatch.setattr(d2e_submit_cli, "_open_submit_request", fake_open)

    result = d2e_submit_cli.handle_submit(
        _submit_args(
            endpoint="https://validator.example/api/v1/truth/submit",
            quic_endpoint="",
        )
    )

    assert seen["url"] == "https://validator.example/api/v1/truth/submit"
    assert result["node_id"] == node_id
    assert result["public_submit_endpoint"] == "https://validator.example/api/v1/truth/submit"
