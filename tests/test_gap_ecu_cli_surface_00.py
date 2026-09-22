from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli import d2e_submit_cli
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


VALID_AGENT_ID = "a" * 96


def _fake_keygen(tmp_path: Path, *, pubkey: str = "b" * 96) -> Path:
    script = tmp_path / "keygen"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import pathlib, sys",
                "args = sys.argv[1:]",
                "out = pathlib.Path(args[args.index('--out') + 1])",
                "out.parent.mkdir(parents=True, exist_ok=True)",
                "out.write_text('c' * 64 + '\\n', encoding='utf-8')",
                f"print({pubkey!r})",
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

    result = handle_agent_generate(str(key_path), str(_fake_keygen(tmp_path)))

    assert result["version"] == AGENT_GENERATE_CLI_VERSION
    assert result["agent_id"] == "b" * 96
    assert result["_raw"] == "b" * 96
    assert result["agent_id_format"] == "cdl-017-bls-g1-pubkey"
    assert result["public_rc_submit_compatible"] is True
    assert key_path.read_text(encoding="utf-8").strip() == "c" * 64


def test_agent_generate_stdout_is_bare_agent_id(tmp_path: Path) -> None:
    key_path = tmp_path / "identity" / "signing_key.hex"
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

    assert proc.stdout == f"{'b' * 96}\n"
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
    assert result["non_claim"] == "quote_visibility_only_not_committed_balance"


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

        def read(self, _limit: int) -> bytes:
            return json.dumps(
                {
                    "agent_id": VALID_AGENT_ID,
                    "pending_attribution_quote": "1.25",
                    "committed_ecu_balance": "0",
                    "status": "quote_visible",
                }
            ).encode("utf-8")

    def fake_urlopen(request: object, *, timeout: float) -> Response:
        seen["url"] = request.full_url
        seen["timeout"] = str(timeout)
        return Response()

    monkeypatch.setattr("ilc_core.cli.ecu_status_cli.urlopen", fake_urlopen)
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
            {"pending_attribution_quote": "NaN", "committed_ecu_balance": "0"},
            agent_id=VALID_AGENT_ID,
            endpoint="https://validator.example/ecu/status",
        )


def test_source_contains_public_cli_tokens() -> None:
    agent_source = Path("ilc_core/cli/d2e_agent_cli.py").read_text(encoding="utf-8")
    submit_source = Path("ilc_core/cli/d2e_submit_cli.py").read_text(encoding="utf-8")
    status_source = Path("ilc_core/cli/ecu_status_cli.py").read_text(encoding="utf-8")

    assert "cdl-017-bls-g1-pubkey" in agent_source
    assert "source_refs_content_object_required" in submit_source
    assert "ecu_status_endpoint_unreachable" in status_source
    assert "random" not in agent_source
    assert re.search(r"^[0-9a-f]{96}$", VALID_AGENT_ID)
