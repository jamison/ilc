from __future__ import annotations

import argparse
import hashlib
import subprocess

import pytest
import requests

from ilc_core.cli import upgrade_cli
from ilc_core.cli.upgrade_cli import UpgradeCliError, run_upgrade_command
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release import artifact_fetch
from ilc_core.release.artifact_fetch import ArtifactFetchError, fetch_and_verify
from ilc_core.release.current_policy import CurrentPolicyEvaluationInput


WHEEL_BYTES = b"fake wheel bytes"
_POLICY_INPUT = CurrentPolicyEvaluationInput(
    release_assertion_cid="fixture-assertion",
    software_release_cid="fixture-release",
    artifact_cids=("fixture-artifact",),
    network_id="fixture-network",
    channel="public_rc",
    policy_id="fixture-policy",
    policy_public_key_hex="00",
    policy_claims=(),
    authoritative_policy_head_cid="fixture-head",
    authoritative_validation_epoch=0,
    observer_validation_epoch=0,
    observer_highest_seen_sequence=0,
    bootstrap_policy_head_cid="fixture-head",
    bootstrap_binding_evidence_cid="fixture-binding",
    bootstrap_binding_bundle_json=b"{}",
)


class _FakeResponse:
    def __init__(
        self,
        body: bytes,
        *,
        status_code: int = 200,
        content_length: int | None = None,
    ) -> None:
        self.body = body
        self.status_code = status_code
        self.headers = {"Content-Length": str(len(body) if content_length is None else content_length)}
        self.closed = False

    def iter_content(self, *, chunk_size: int):
        for index in range(0, len(self.body), chunk_size):
            yield self.body[index : index + chunk_size]

    def close(self) -> None:
        self.closed = True


def _artifact_node(body: bytes = WHEEL_BYTES, *, url: str = "https://example.test/wheel.whl"):
    artifact_body = {
        "artifact_id": "ilc-artifact:ilc-core-python-wheel-999@phase-1628",
        "artifact_type": "wheel",
        "filename": "ilc_core-9.9.9-py3-none-any.whl",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": "9.9.9",
        "pypi_url": url,
        "schema_version": "artifact_node.v0.1",
        "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
    }
    return {**artifact_body, "cid": node_id_from_obj(artifact_body)}


def _assertion(body: bytes = WHEEL_BYTES, *, url: str = "https://example.test/wheel.whl"):
    artifact_node = _artifact_node(body, url=url)
    return {
        "artifact_nodes": [artifact_node],
        "release_attestation_edges": [
            {
                "artifact_sha256": artifact_node["sha256"],
                "target": artifact_node["cid"],
            }
        ],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": {
            "artifact_cids": [artifact_node["cid"]],
            "package_name": "ilc-core",
            "version": "9.9.9",
        },
    }


def _refresh_artifact_metadata_cid(payload):
    artifact_node = payload["artifact_nodes"][0]
    artifact_body = {key: value for key, value in artifact_node.items() if key != "cid"}
    artifact_node["cid"] = node_id_from_obj(artifact_body)
    payload["release_attestation_edges"][0]["target"] = artifact_node["cid"]
    payload["software_release_node"]["artifact_cids"][0] = artifact_node["cid"]


def _patch_validation(monkeypatch):
    result = {
        "package_name": "ilc-core",
        "available_version": "9.9.9",
        "full_release_graph_binding_verified": True,
        "current_release_eligibility_status": "verified_current_policy",
    }
    monkeypatch.setattr(
        artifact_fetch,
        "validate_release_assertion",
        lambda payload, **kwargs: dict(result),
    )
    monkeypatch.setattr(
        upgrade_cli,
        "validate_release_assertion",
        lambda payload, **kwargs: dict(result),
    )
    monkeypatch.setattr(upgrade_cli, "_load_apply_policy_input", lambda **kwargs: _POLICY_INPUT)


def _fetch(payload):
    return fetch_and_verify(payload, policy_evaluation_input=_POLICY_INPUT)


def test_fetch_and_verify_happy_path(monkeypatch):
    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES),
    )

    path = _fetch(_assertion())

    try:
        assert path.read_bytes() == WHEEL_BYTES
        assert path.name == "ilc_core-9.9.9-py3-none-any.whl"
    finally:
        path.unlink(missing_ok=True)
        path.parent.rmdir()


def test_fetch_and_verify_sha256_mismatch_hard_stops(monkeypatch):
    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(b"wrong bytes"),
    )

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(_assertion())

    assert exc.value.token == "artifact_fetch_all_sources_failed"


def test_fetch_and_verify_cidv1_mismatch_hard_stops(monkeypatch):
    _patch_validation(monkeypatch)
    payload = _assertion()
    payload["artifact_nodes"][0]["cid"] = node_id_from_obj({"different": "artifact"})
    payload["release_attestation_edges"][0]["target"] = payload["artifact_nodes"][0]["cid"]

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(payload)

    assert exc.value.token == "artifact_fetch_artifact_cid_mismatch"


def test_fetch_and_verify_all_sources_fail(monkeypatch):
    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES, status_code=503),
    )

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(_assertion())

    assert exc.value.token == "artifact_fetch_all_sources_failed"


def test_fetch_and_verify_stream_error_is_tokenized(monkeypatch):
    class _BrokenResponse(_FakeResponse):
        def iter_content(self, *, chunk_size: int):
            raise requests.exceptions.ChunkedEncodingError("broken stream")
            yield b""

    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _BrokenResponse(WHEEL_BYTES),
    )

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(_assertion())

    assert exc.value.token == "artifact_fetch_all_sources_failed"
    assert isinstance(exc.value.__cause__, ArtifactFetchError)
    assert exc.value.__cause__.token == "artifact_fetch_source_failed"


def test_fetch_and_verify_size_mismatch_hard_stops(monkeypatch):
    _patch_validation(monkeypatch)
    payload = _assertion()
    payload["artifact_nodes"][0]["size_bytes"] = len(WHEEL_BYTES) + 1
    _refresh_artifact_metadata_cid(payload)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES),
    )

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(payload)

    assert exc.value.token == "artifact_fetch_all_sources_failed"
    assert isinstance(exc.value.__cause__, ArtifactFetchError)
    assert exc.value.__cause__.token == "artifact_fetch_size_mismatch"


def test_fetch_and_verify_declared_content_length_over_cap_hard_stops(monkeypatch):
    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(
            WHEEL_BYTES,
            content_length=len(WHEEL_BYTES) + artifact_fetch.ARTIFACT_DOWNLOAD_EXTRA_BYTES + 1,
        ),
    )

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(_assertion())

    assert exc.value.token == "artifact_fetch_all_sources_failed"
    assert isinstance(exc.value.__cause__, ArtifactFetchError)
    assert exc.value.__cause__.token == "artifact_fetch_size_exceeded"


def test_fetch_and_verify_streaming_body_over_cap_hard_stops(monkeypatch):
    class _OverCapResponse(_FakeResponse):
        def __init__(self) -> None:
            super().__init__(b"", content_length=0)

        def iter_content(self, *, chunk_size: int):
            yield b"x" * (artifact_fetch.ARTIFACT_DOWNLOAD_EXTRA_BYTES + len(WHEEL_BYTES) + 1)

    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _OverCapResponse(),
    )

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(_assertion())

    assert exc.value.token == "artifact_fetch_all_sources_failed"
    assert isinstance(exc.value.__cause__, ArtifactFetchError)
    assert exc.value.__cause__.token == "artifact_fetch_size_exceeded"


def test_fetch_and_verify_rejects_insecure_url(monkeypatch):
    _patch_validation(monkeypatch)

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(_assertion(url="http://example.test/wheel.whl"))

    assert exc.value.token == "artifact_fetch_source_url_invalid"


def test_fetch_and_verify_rejects_filename_traversal(monkeypatch):
    _patch_validation(monkeypatch)
    payload = _assertion()
    payload["artifact_nodes"][0]["filename"] = "../../ilc_core-9.9.9-py3-none-any.whl"
    _refresh_artifact_metadata_cid(payload)

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(payload)

    assert exc.value.token == "artifact_fetch_filename_invalid"


def test_fetch_and_verify_rejects_ambiguous_wheel_selection(monkeypatch):
    _patch_validation(monkeypatch)
    payload = _assertion()
    payload["artifact_nodes"].append(dict(payload["artifact_nodes"][0]))

    with pytest.raises(ArtifactFetchError) as exc:
        _fetch(payload)

    assert exc.value.token == "artifact_fetch_multiple_wheel_artifacts"


def test_upgrade_apply_dry_run_does_not_invoke_pip(monkeypatch, tmp_path):
    payload = _assertion()
    checked = {
        "available_version": "9.9.9",
        "release_assertion_payload": payload,
        "authorized_upgrade_available": True,
        "current_release_eligibility_status": "verified_current_policy",
    }
    pip_calls = []

    monkeypatch.setattr(upgrade_cli, "check_for_upgrade", lambda **kwargs: checked)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES),
    )
    monkeypatch.setattr(upgrade_cli.subprocess, "run", lambda *args, **kwargs: pip_calls.append(args))
    _patch_validation(monkeypatch)

    result = run_upgrade_command(
        argparse.Namespace(
            upgrade_subcommand="apply",
            endpoint="",
            state_path=str(tmp_path / "upgrade_state.json"),
            dry_run=True,
            json=True,
        )
    )

    assert result["status"] == "upgrade_apply_dry_run_verified"
    assert result["verified_artifact_filename"] == "ilc_core-9.9.9-py3-none-any.whl"
    assert result["verified_artifact_size_bytes"] == len(WHEEL_BYTES)
    assert "verified_artifact_path" not in result
    assert pip_calls == []  # pip not called


def test_upgrade_apply_sha256_mismatch_does_not_invoke_pip(monkeypatch, tmp_path):
    payload = _assertion()
    checked = {
        "available_version": "9.9.9",
        "release_assertion_payload": payload,
        "authorized_upgrade_available": True,
        "current_release_eligibility_status": "verified_current_policy",
    }
    pip_calls = []

    monkeypatch.setattr(upgrade_cli, "check_for_upgrade", lambda **kwargs: checked)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(b"wrong bytes"),
    )
    monkeypatch.setattr(upgrade_cli.subprocess, "run", lambda *args, **kwargs: pip_calls.append(args))
    _patch_validation(monkeypatch)

    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(
            argparse.Namespace(
                upgrade_subcommand="apply",
                endpoint="",
                state_path=str(tmp_path / "upgrade_state.json"),
                dry_run=False,
                json=True,
            )
        )

    assert exc.value.token == "artifact_fetch_all_sources_failed"
    assert pip_calls == []  # pip not called after failed verification


def test_upgrade_apply_success_invokes_pip_after_verification(monkeypatch, tmp_path):
    payload = _assertion()
    checked = {
        "available_version": "9.9.9",
        "release_assertion_payload": payload,
        "authorized_upgrade_available": True,
        "current_release_eligibility_status": "verified_current_policy",
    }
    pip_calls = []

    def fake_run(args, *, check, timeout):
        pip_calls.append((args, check, timeout))

    monkeypatch.setattr(upgrade_cli, "check_for_upgrade", lambda **kwargs: checked)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES),
    )
    monkeypatch.setattr(upgrade_cli.subprocess, "run", fake_run)
    _patch_validation(monkeypatch)

    result = run_upgrade_command(
        argparse.Namespace(
            upgrade_subcommand="apply",
            endpoint="",
            state_path=str(tmp_path / "upgrade_state.json"),
            dry_run=False,
            json=True,
        )
    )

    assert result["status"] == "upgrade_apply_success"
    assert len(pip_calls) == 2
    assert pip_calls[0][0][:4] == [upgrade_cli.sys.executable, "-m", "pip", "install"]
    assert pip_calls[0][1] is True
    assert pip_calls[0][2] == upgrade_cli.UPGRADE_APPLY_PIP_TIMEOUT_SECONDS
    assert pip_calls[1][0][:3] == [upgrade_cli.sys.executable, "-I", "-c"]
    assert pip_calls[1][0][-1] == "9.9.9"
    assert pip_calls[1][2] == upgrade_cli.UPGRADE_APPLY_VERIFY_TIMEOUT_SECONDS


def test_upgrade_apply_pip_failure_is_tokenized(monkeypatch, tmp_path):
    payload = _assertion()
    checked = {
        "available_version": "9.9.9",
        "release_assertion_payload": payload,
        "authorized_upgrade_available": True,
        "current_release_eligibility_status": "verified_current_policy",
    }

    def fake_run(args, *, check, timeout):
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(upgrade_cli, "check_for_upgrade", lambda **kwargs: checked)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES),
    )
    monkeypatch.setattr(upgrade_cli.subprocess, "run", fake_run)
    _patch_validation(monkeypatch)

    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(
            argparse.Namespace(
                upgrade_subcommand="apply",
                endpoint="",
                state_path=str(tmp_path / "upgrade_state.json"),
                dry_run=False,
                json=True,
            )
        )

    assert exc.value.token == "upgrade_apply_pip_install_failed"


def test_upgrade_apply_pip_timeout_is_tokenized(monkeypatch, tmp_path):
    payload = _assertion()
    checked = {
        "available_version": "9.9.9",
        "release_assertion_payload": payload,
        "authorized_upgrade_available": True,
        "current_release_eligibility_status": "verified_current_policy",
    }

    def fake_run(args, *, check, timeout):
        raise subprocess.TimeoutExpired(args, timeout)

    monkeypatch.setattr(upgrade_cli, "check_for_upgrade", lambda **kwargs: checked)
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(WHEEL_BYTES),
    )
    monkeypatch.setattr(upgrade_cli.subprocess, "run", fake_run)
    _patch_validation(monkeypatch)

    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(
            argparse.Namespace(
                upgrade_subcommand="apply",
                endpoint="",
                state_path=str(tmp_path / "upgrade_state.json"),
                dry_run=False,
                json=True,
            )
        )

    assert exc.value.token == "upgrade_apply_pip_install_timeout"


def test_upgrade_apply_missing_payload_is_tokenized(monkeypatch, tmp_path):
    _patch_validation(monkeypatch)
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: {
            "available_version": "9.9.9",
            "authorized_upgrade_available": True,
            "current_release_eligibility_status": "verified_current_policy",
        },
    )

    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(
            argparse.Namespace(
                upgrade_subcommand="apply",
                endpoint="",
                state_path=str(tmp_path / "upgrade_state.json"),
                dry_run=False,
                json=True,
            )
        )

    assert exc.value.token == "upgrade_apply_release_assertion_missing"


def test_upgrade_apply_no_authorized_upgrade_available_is_tokenized(monkeypatch, tmp_path):
    _patch_validation(monkeypatch)
    payload = _assertion()
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: {
            "available_version": "9.9.9",
            "release_assertion_payload": payload,
            "authorized_upgrade_available": False,
            "current_release_eligibility_status": "bounded_compatibility_source",
        },
    )

    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(
            argparse.Namespace(
                upgrade_subcommand="apply",
                endpoint="",
                state_path=str(tmp_path / "upgrade_state.json"),
                dry_run=False,
                json=True,
            )
        )

    assert exc.value.token == "upgrade_apply_no_authorized_upgrade_available"


def test_upgrade_apply_dry_run_no_authorized_upgrade_available_is_tokenized(
    monkeypatch, tmp_path
):
    _patch_validation(monkeypatch)
    payload = _assertion()
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: {
            "available_version": "9.9.9",
            "release_assertion_payload": payload,
            "authorized_upgrade_available": False,
            "current_release_eligibility_status": "bounded_compatibility_source",
        },
    )

    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(
            argparse.Namespace(
                upgrade_subcommand="apply",
                endpoint="",
                state_path=str(tmp_path / "upgrade_state.json"),
                dry_run=True,
                json=True,
            )
        )

    assert exc.value.token == "upgrade_apply_no_authorized_upgrade_available"
