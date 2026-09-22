from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from ilc_core.cli import d2e_submit_cli
from ilc_core.cli import ecu_status_cli
from ilc_core.cli.d2e_agent_cli import (
    AGENT_GENERATE_CLI_VERSION,
    handle_agent_generate,
)
from ilc_core.cli.d2e_submit_cli import SubmitCommandError, _apply_source_refs
from ilc_core.cli.ecu_status_cli import (
    ECU_STATUS_CLI_VERSION,
    EcuStatusCliError,
    handle_ecu_status,
    normalize_ecu_status_payload,
)
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.identity.bls_backend import keypair_from_ikm_hex


VALID_AGENT_ID = "a" * 96
ROOT = Path(__file__).resolve().parents[1]


def _fake_keygen(tmp_path: Path, *, pubkey: str | None = None) -> Path:
    secret_key_hex, public_key_hex = keypair_from_ikm_hex("11" * 32)
    emitted_pubkey = pubkey or public_key_hex
    script = tmp_path / "keygen"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import pathlib, sys",
                "args = sys.argv[1:]",
                "out = pathlib.Path(args[args.index('--out') + 1])",
                "out.parent.mkdir(parents=True, exist_ok=True)",
                f"out.write_text({secret_key_hex!r} + '\\n', encoding='utf-8')",
                f"print({emitted_pubkey!r})",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def _node_id() -> str:
    return node_id_from_obj({"phase": "GAP-ECU-CLI-SURFACE-00", "n": 1})


def test_agent_generate_uses_bls_keygen_and_returns_public_rc_agent_id(tmp_path: Path) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"
    secret_key_hex, public_key_hex = keypair_from_ikm_hex("11" * 32)

    result = handle_agent_generate(str(key_path), str(_fake_keygen(tmp_path)))

    assert result["version"] == AGENT_GENERATE_CLI_VERSION
    assert result["agent_id"] == public_key_hex
    assert result["_raw"] == public_key_hex
    assert result["agent_id_format"] == "cdl-017-bls-g1-pubkey"
    assert result["public_rc_submit_compatible"] is True
    assert key_path.read_text(encoding="utf-8").strip() == secret_key_hex


def test_agent_generate_stdout_is_bare_agent_id(tmp_path: Path) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"
    _, public_key_hex = keypair_from_ikm_hex("11" * 32)
    proc = subprocess.run(
        [
            os.environ.get("PYTHON", ".venv/bin/python"),
            "-m",
            "ilc_core.cli",
            "agent",
            "generate",
            "--keygen-binary",
            str(_fake_keygen(tmp_path)),
            "--output",
            str(key_path),
        ],
        capture_output=True,
        check=True,
        text=True,
    )

    assert proc.stdout == f"{public_key_hex}\n"
    assert proc.stderr == ""


def test_agent_generate_rejects_ed25519_sized_output(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="agent_generate_invalid_public_agent_id"):
        handle_agent_generate(
            str(tmp_path / "identity" / "signing_key.hex"),
            str(_fake_keygen(tmp_path, pubkey="d" * 64)),
        )


def test_agent_generate_refuses_to_overwrite_existing_secret(tmp_path: Path) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"
    key_path.parent.mkdir(parents=True)
    key_path.write_text("existing\n", encoding="utf-8")

    with pytest.raises(ValueError, match="agent_generate_output_exists"):
        handle_agent_generate(str(key_path), str(_fake_keygen(tmp_path)))


def test_agent_generate_rejects_secret_public_mismatch(tmp_path: Path) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"

    with pytest.raises(ValueError, match="agent_generate_secret_public_mismatch"):
        handle_agent_generate(str(key_path), str(_fake_keygen(tmp_path, pubkey="b" * 96)))

    assert not key_path.exists()


def test_agent_generate_timeout_cleans_partial_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"

    def fake_run(*_args: object, **_kwargs: object) -> object:
        key_path.write_text("1" * 64 + "\n", encoding="utf-8")
        raise subprocess.TimeoutExpired(cmd="keygen", timeout=30)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(ValueError, match="agent_generate_keygen_timeout"):
        handle_agent_generate(str(key_path), str(_fake_keygen(tmp_path)))

    assert not key_path.exists()


def test_agent_generate_falls_back_to_packageable_python_bls_backend(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"
    monkeypatch.delenv("ILC_AGENT_BLS_KEYGEN_BINARY", raising=False)
    monkeypatch.setattr("ilc_core.cli.d2e_agent_cli._default_keygen_binary", lambda: tmp_path / "missing-keygen")

    result = handle_agent_generate(str(key_path))

    assert re.fullmatch(r"[0-9a-f]{96}", result["agent_id"])
    assert result["agent_id_generation_backend"] == "python_py_ecc_bls_backend"
    assert re.fullmatch(r"[0-9a-f]{64}", key_path.read_text(encoding="utf-8").strip())


def test_source_refs_are_inserted_under_payload_content() -> None:
    ref = _node_id()
    payload = {
        "content": {"claim": "hello"},
        "epistemic_type": "objective",
        "parent_node_ids": [],
        "primitive_type": "observation",
    }

    patched = _apply_source_refs(payload, [ref])

    assert patched["content"]["source_refs"] == [ref]
    assert "source_refs" not in payload["content"]


def test_source_refs_require_content_object() -> None:
    with pytest.raises(SubmitCommandError, match="content"):
        _apply_source_refs({"content": "not-an-object"}, [_node_id()])


def test_source_refs_reject_non_cid_values() -> None:
    with pytest.raises(SubmitCommandError) as exc_info:
        _apply_source_refs({"content": {}}, ["artifact:genesis_intent"])

    assert exc_info.value.token == "source_refs_cid_invalid"


def test_source_refs_reject_more_than_64_values() -> None:
    refs = [_node_id()] * 65

    with pytest.raises(SubmitCommandError) as exc_info:
        _apply_source_refs({"content": {}}, refs)

    assert exc_info.value.token == "source_refs_count_exceeded"


def test_submit_handler_applies_source_refs_before_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class Result:
        primitive = "assert.truth"
        creates_node = True
        node_primitive_type = "observation"
        edges: list[object] = []

    def fake_validate(envelope: dict[str, object]) -> Result:
        captured.update(envelope)
        return Result()

    monkeypatch.setattr(d2e_submit_cli, "validate_truth_primitive_submission", fake_validate)
    ref = _node_id()
    result = d2e_submit_cli.handle_submit(
        argparse.Namespace(
            primitive="assert.truth",
            agent_id=VALID_AGENT_ID,
            epoch=1,
            payload_json=json.dumps({"content": {}, "primitive_type": "observation"}),
            payload_file=None,
            sig="UNSIGNED",
            signing_key=None,
            source_refs=[ref],
        )
    )

    assert result["primitive"] == "assert.truth"
    assert captured["payload"]["content"]["source_refs"] == [ref]


def test_ecu_status_normalizes_endpoint_response() -> None:
    result = normalize_ecu_status_payload(
        {
            "agent_id": VALID_AGENT_ID,
            "pending_attribution_quote": "0.20",
            "committed_ecu_balance": "0",
            "status": "quote_visible",
            "quote_epoch": 1,
        },
        agent_id=VALID_AGENT_ID,
        endpoint="https://validator.example/ecu/status",
    )

    assert result["version"] == ECU_STATUS_CLI_VERSION
    assert result["pending_attribution_quote"] == "0.20"
    assert result["committed_ecu_balance"] == "0"
    assert result["non_claim"] == "ecu_committed_balance_zero_until_observe_00"


def test_ecu_status_requires_endpoint() -> None:
    with pytest.raises(EcuStatusCliError, match="ecu_status_endpoint_missing"):
        handle_ecu_status(argparse.Namespace(agent_id=VALID_AGENT_ID, endpoint="", timeout=10.0))


def test_ecu_status_does_not_accept_invalid_agent_id() -> None:
    with pytest.raises(EcuStatusCliError, match="ecu_status_agent_id_invalid"):
        handle_ecu_status(argparse.Namespace(agent_id="A" * 96, endpoint="https://e.example", timeout=10.0))


def test_ecu_status_fetches_json_from_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, str] = {}

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def __init__(self) -> None:
            self._sent = False

        def read(self, _limit: int) -> bytes:
            if self._sent:
                return b""
            self._sent = True
            return json.dumps(
                {
                    "agent_id": VALID_AGENT_ID,
                    "pending_attribution_quote": "1.25",
                    "committed_ecu_balance": "0",
                    "status": "quote_visible",
                }
            ).encode("utf-8")

    def fake_open(request: object, *, timeout: float) -> Response:
        seen["url"] = request.full_url
        seen["timeout"] = str(timeout)
        return Response()

    monkeypatch.setattr("ilc_core.cli.ecu_status_cli._open_status_request", fake_open)
    result = handle_ecu_status(
        argparse.Namespace(
            agent_id=VALID_AGENT_ID,
            endpoint="https://validator.example/ecu/status",
            timeout=5.0,
        )
    )

    assert seen["url"].endswith(f"?agent_id={VALID_AGENT_ID}")
    assert result["pending_attribution_quote"] == "1.25"


def test_ecu_status_rejects_nonfinite_decimal_response() -> None:
    with pytest.raises(EcuStatusCliError, match="ecu_status_pending_attribution_quote_invalid"):
        normalize_ecu_status_payload(
            {"agent_id": VALID_AGENT_ID, "pending_attribution_quote": "NaN", "committed_ecu_balance": "0"},
            agent_id=VALID_AGENT_ID,
            endpoint="https://validator.example/ecu/status",
        )


def test_ecu_status_requires_agent_id_in_response() -> None:
    with pytest.raises(EcuStatusCliError, match="ecu_status_agent_id_missing"):
        normalize_ecu_status_payload(
            {"pending_attribution_quote": "0", "committed_ecu_balance": "0"},
            agent_id=VALID_AGENT_ID,
            endpoint="https://validator.example/ecu/status",
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"agent_id": VALID_AGENT_ID, "pending_attribution_quote": "-0.1", "committed_ecu_balance": "0"},
        {"agent_id": VALID_AGENT_ID, "pending_attribution_quote": "0", "committed_ecu_balance": "-1"},
    ],
)
def test_ecu_status_rejects_negative_decimal_response(payload: dict[str, str]) -> None:
    with pytest.raises(EcuStatusCliError, match="invalid"):
        normalize_ecu_status_payload(
            payload,
            agent_id=VALID_AGENT_ID,
            endpoint="https://validator.example/ecu/status",
        )


def test_ecu_status_rejects_invalid_quote_epoch() -> None:
    with pytest.raises(EcuStatusCliError, match="ecu_status_quote_epoch_invalid"):
        normalize_ecu_status_payload(
            {
                "agent_id": VALID_AGENT_ID,
                "pending_attribution_quote": "0",
                "committed_ecu_balance": "0",
                "quote_epoch": {"nested": "bad"},
            },
            agent_id=VALID_AGENT_ID,
            endpoint="https://validator.example/ecu/status",
        )


@pytest.mark.parametrize(
    ("endpoint", "token"),
    [
        ("http://validator.example/ecu/status", "ecu_status_endpoint_https_required"),
        ("https://user:pass@validator.example/ecu/status", "ecu_status_endpoint_userinfo_forbidden"),
    ],
)
def test_ecu_status_rejects_unsafe_endpoint_forms(endpoint: str, token: str) -> None:
    with pytest.raises(EcuStatusCliError, match=token):
        handle_ecu_status(argparse.Namespace(agent_id=VALID_AGENT_ID, endpoint=endpoint, timeout=10.0))


def test_ecu_status_redirect_handler_forbids_redirects() -> None:
    handler = ecu_status_cli._NoRedirectHandler()

    with pytest.raises(EcuStatusCliError, match="ecu_status_redirect_forbidden"):
        handler.redirect_request(
            object(),
            object(),
            302,
            "Found",
            {},
            "https://attacker.example/collect",
        )


def test_ecu_status_is_stateless_on_endpoint_missing(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli",
            "--graph-state",
            str(graph_path),
            "ecu",
            "status",
            "--agent-id",
            VALID_AGENT_ID,
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert proc.returncode == 1
    assert "ecu_status_endpoint_missing_GAP_ECU_CLI_SURFACE_00" in proc.stderr
    assert not graph_path.exists()


def test_submit_signing_surfaces_signature_without_graph_store(tmp_path: Path) -> None:
    private_key = ed25519.Ed25519PrivateKey.generate()
    key_path = tmp_path / "hotkey.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
    )
    key_path.chmod(0o600)

    result = d2e_submit_cli.handle_submit(
        argparse.Namespace(
            primitive="assert.truth",
            agent_id=VALID_AGENT_ID,
            epoch=1,
            payload_json=json.dumps(
                {
                    "content": {},
                    "epistemic_type": "objective",
                    "parent_node_ids": [],
                    "primitive_type": "observation",
                }
            ),
            payload_file=None,
            sig="UNSIGNED",
            signing_key=key_path.resolve().as_uri(),
            source_refs=[],
        )
    )

    assert result["signature"]["sig_scheme"]
    assert len(result["signature"]["sig_pubkey_hex"]) == 64


def test_submit_signing_missing_key_uses_stable_error_token(tmp_path: Path) -> None:
    with pytest.raises(SubmitCommandError) as exc_info:
        d2e_submit_cli.handle_submit(
            argparse.Namespace(
                primitive="assert.truth",
                agent_id=VALID_AGENT_ID,
                epoch=1,
                payload_json=json.dumps(
                    {
                        "content": {},
                        "epistemic_type": "objective",
                        "parent_node_ids": [],
                        "primitive_type": "observation",
                    }
                ),
                payload_file=None,
                sig="UNSIGNED",
                signing_key=(tmp_path / "missing.pem").resolve().as_uri(),
                source_refs=[],
            )
        )

    assert exc_info.value.token == "submit_signing_key_invalid"


def test_source_contains_public_cli_tokens() -> None:
    agent_source = (ROOT / "ilc_core/cli/d2e_agent_cli.py").read_text(encoding="utf-8")
    submit_source = (ROOT / "ilc_core/cli/d2e_submit_cli.py").read_text(encoding="utf-8")
    status_source = (ROOT / "ilc_core/cli/ecu_status_cli.py").read_text(encoding="utf-8")

    assert "cdl-017-bls-g1-pubkey" in agent_source
    assert "source_refs_content_object_required" in submit_source
    assert "ecu_status_endpoint_unreachable" in status_source
    assert "random" not in agent_source
    assert re.search(r"^[0-9a-f]{96}$", VALID_AGENT_ID)
