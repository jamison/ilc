# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.cli import upgrade_cli
from ilc_core.cli.main import _build_parser
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release import artifact_fetch, upgrade_check
from ilc_core.release.artifact_fetch import ArtifactFetchError
from ilc_core.release.current_policy import CurrentPolicyEvaluationInput
from ilc_core.release.current_policy_view import (
    MAX_POLICY_VIEW_FILE_BYTES,
    CurrentPolicyViewError,
    load_current_policy_evaluation_input,
)
from ilc_core.release.upgrade_state import (
    advance_current_policy_high_water_mark,
    read_current_policy_high_water_mark,
    read_upgrade_state,
    write_upgrade_state,
)


WHEEL_BYTES = b"row-26-authorized-wheel"


class _Response:
    status_code = 200

    def __init__(self, body: bytes) -> None:
        self.body = body
        self.headers = {"Content-Length": str(len(body))}

    def iter_content(self, *, chunk_size: int):
        yield self.body

    def close(self) -> None:
        return None


def _policy_input(*, marker: str = "initial") -> CurrentPolicyEvaluationInput:
    return CurrentPolicyEvaluationInput(
        release_assertion_cid=f"fixture-assertion-{marker}",
        software_release_cid=f"fixture-release-{marker}",
        artifact_cids=(f"fixture-artifact-{marker}",),
        network_id="ilc-public-rc-01-testnet-harness",
        channel="public_rc",
        policy_id="ilc-public-rc-current-policy-v1",
        policy_public_key_hex="00",
        policy_claims=(),
        authoritative_policy_head_cid=f"fixture-head-{marker}",
        authoritative_validation_epoch=0,
        observer_validation_epoch=0,
        observer_highest_seen_sequence=0,
        bootstrap_policy_head_cid=f"fixture-head-{marker}",
        bootstrap_binding_evidence_cid=f"fixture-binding-{marker}",
        bootstrap_binding_bundle_json=b"{}",
    )


def _assertion() -> dict:
    artifact_body = {
        "artifact_id": "ilc-artifact:row-26-wheel",
        "artifact_type": "wheel",
        "filename": "ilc_core-9.9.9-py3-none-any.whl",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": "9.9.9",
        "pypi_url": "https://example.test/ilc_core.whl",
        "schema_version": "artifact_node.v0.1",
        "sha256": hashlib.sha256(WHEEL_BYTES).hexdigest(),
        "size_bytes": len(WHEEL_BYTES),
    }
    artifact = {**artifact_body, "cid": node_id_from_obj(artifact_body)}
    return {
        "artifact_nodes": [artifact],
        "release_attestation_edges": [
            {"target": artifact["cid"], "artifact_sha256": artifact["sha256"]}
        ],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": {
            "artifact_cids": [artifact["cid"]],
            "package_name": "ilc-core",
            "version": "9.9.9",
        },
    }


def _validation(*, status: str = "verified_current_policy") -> dict:
    return {
        "package_name": "ilc-core",
        "available_version": "9.9.9",
        "full_release_graph_binding_verified": True,
        "current_release_eligibility_status": status,
    }


def _upgrade_result(*, authorized: bool, status: str) -> dict:
    return {
        "available_version": "9.9.9",
        "release_assertion_payload": _assertion(),
        "candidate_version_relation": "newer",
        "candidate_upgrade_available": True,
        "authorized_upgrade_available": authorized,
        "current_release_eligibility_status": status,
    }


def _apply_args(tmp_path: Path, *, dry_run: bool) -> argparse.Namespace:
    return argparse.Namespace(
        upgrade_subcommand="apply",
        endpoint="",
        state_path=str(tmp_path / "upgrade_state.json"),
        policy_view=str(tmp_path / "policy-view.json"),
        dry_run=dry_run,
        json=True,
    )


def _policy_view() -> dict:
    return {
        "schema_version": "release_current_policy_view.v0.1",
        "release_assertion_cid": "fixture-assertion",
        "software_release_cid": "fixture-release",
        "artifact_cids": ["fixture-artifact"],
        "network_id": "ilc-public-rc-01-testnet-harness",
        "channel": "public_rc",
        "policy_id": "ilc-public-rc-current-policy-v1",
        "policy_public_key_hex": "00",
        "policy_claims": [
            {"claim_cid": "fixture-claim", "node_record": {"fixture": "claim"}}
        ],
        "authoritative_policy_head_cid": "fixture-head",
        "authoritative_validation_epoch": 0,
        "observer_validation_epoch": 0,
        "bootstrap_policy_head_cid": "fixture-head",
        "bootstrap_binding_evidence_cid": "fixture-binding",
        "bootstrap_binding_bundle": {"fixture": "binding"},
    }


def _write_policy_view(path: Path, view: dict | None = None) -> None:
    path.write_text(json.dumps(view or _policy_view()), encoding="utf-8")


def _patch_authorized_fetch(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    events: list[str] = []

    def validate(payload, **kwargs):
        events.append("validate")
        return _validation()

    def gate(result):
        events.append("authorize")
        upgrade_check.require_arbitrary_source_release_authorized(result)

    def get(*args, **kwargs):
        events.append("transport")
        return _Response(WHEEL_BYTES)

    monkeypatch.setattr(artifact_fetch, "validate_release_assertion", validate)
    monkeypatch.setattr(artifact_fetch, "require_arbitrary_source_release_authorized", gate)
    monkeypatch.setattr(artifact_fetch.requests, "get", get)
    return events


def test_fetch_without_policy_input_fails_before_transport(monkeypatch) -> None:
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: pytest.fail("transport called without policy evidence"),
    )
    with pytest.raises(ArtifactFetchError) as exc:
        artifact_fetch.fetch_and_verify(_assertion(), policy_evaluation_input=None)
    assert exc.value.token == "artifact_fetch_eligibility_unresolved"


def test_upgrade_apply_parser_requires_explicit_policy_view() -> None:
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["upgrade", "apply"])
    args = parser.parse_args(
        ["upgrade", "apply", "--policy-view", "/tmp/untrusted-policy-view.json"]
    )
    assert args.policy_view == "/tmp/untrusted-policy-view.json"


def test_typed_unresolved_policy_stops_before_transport(monkeypatch) -> None:
    monkeypatch.setattr(
        artifact_fetch,
        "validate_release_assertion",
        lambda payload, **kwargs: _validation(status="unresolved"),
    )
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: pytest.fail("transport called for unresolved policy"),
    )
    with pytest.raises(ArtifactFetchError) as exc:
        artifact_fetch.fetch_and_verify(
            _assertion(), policy_evaluation_input=_policy_input(marker="unresolved")
        )
    assert exc.value.token == "artifact_fetch_eligibility_gate_failed"
    assert str(exc.value) == (
        "artifact_fetch_eligibility_gate_failed:"
        "arbitrary_source_current_release_eligibility_required"
    )


def test_authorization_precedes_transport(monkeypatch) -> None:
    events = _patch_authorized_fetch(monkeypatch)
    path = artifact_fetch.fetch_and_verify(
        _assertion(), policy_evaluation_input=_policy_input()
    )
    try:
        assert path.read_bytes() == WHEEL_BYTES
        assert events == ["validate", "authorize", "transport"]
    finally:
        path.unlink(missing_ok=True)
        path.parent.rmdir()


def test_dry_run_requires_authorization_and_verifies_bytes_without_install(
    monkeypatch, tmp_path
) -> None:
    events = _patch_authorized_fetch(monkeypatch)
    monkeypatch.setattr(upgrade_cli, "_load_apply_policy_input", lambda **kwargs: _policy_input())
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: _upgrade_result(
            authorized=True, status="verified_current_policy"
        ),
    )
    monkeypatch.setattr(
        upgrade_cli.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("pip invoked during dry-run"),
    )
    result = upgrade_cli.run_upgrade_command(_apply_args(tmp_path, dry_run=True))
    assert result["status"] == "upgrade_apply_dry_run_verified"
    assert result["verified_artifact_size_bytes"] == len(WHEEL_BYTES)
    assert events == ["validate", "authorize", "transport"]


def test_dry_run_unresolved_policy_stops_before_transport(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(upgrade_cli, "_load_apply_policy_input", lambda **kwargs: _policy_input())
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: _upgrade_result(authorized=False, status="unresolved"),
    )
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: pytest.fail("transport called for unresolved apply"),
    )
    with pytest.raises(upgrade_cli.UpgradeCliError) as exc:
        upgrade_cli.run_upgrade_command(_apply_args(tmp_path, dry_run=True))
    assert exc.value.token == "upgrade_apply_no_authorized_upgrade_available"


def test_apply_rejects_unauthorized_candidate(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(upgrade_cli, "_load_apply_policy_input", lambda **kwargs: _policy_input())
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: _upgrade_result(
            authorized=False, status="bounded_compatibility_source"
        ),
    )
    monkeypatch.setattr(
        artifact_fetch,
        "fetch_and_verify",
        lambda *args, **kwargs: pytest.fail("fetch called for unauthorized candidate"),
    )
    with pytest.raises(upgrade_cli.UpgradeCliError) as exc:
        upgrade_cli.run_upgrade_command(_apply_args(tmp_path, dry_run=False))
    assert exc.value.token == "upgrade_apply_no_authorized_upgrade_available"


def _result_validation() -> dict:
    return {
        "assertion_cid": "fixture-assertion",
        "available_version": "9.9.9",
        "channel": "public_rc",
        "artifact_cids": ["fixture-artifact"],
        "artifact_release_authority_verified": True,
        "current_release_eligibility_evidence": {"reason": "unresolved"},
        "current_release_eligibility_status": "unresolved",
        "full_release_graph_binding_verified": True,
        "graph_provenance_delegation_evidence": {},
        "graph_provenance_delegation_status": "verified",
        "graph_provenance_delegation_valid_at_submission": True,
        "graph_provenance_status": "verified",
        "graph_provenance_verified": True,
        "graph_submission_provenance_verified": True,
        "package_name": "ilc-core",
        "release_authority": "fixture",
        "release_key_pubkey": "fixture",
        "release_signature_verified": True,
        "signature_scheme": "fixture",
        "verified_attestation_count": 1,
    }


def test_compatibility_discovery_is_never_authorized(monkeypatch) -> None:
    monkeypatch.setattr(upgrade_check, "validate_release_assertion", lambda *args, **kwargs: _result_validation())
    result = upgrade_check._build_upgrade_result(
        {"fixture": "payload"},
        discovery_source="https_endpoint",
        endpoint="https://example.test/latest.json",
        installed_version_resolver=lambda: "1.0.0",
        now=datetime(2026, 10, 24, tzinfo=timezone.utc),
    )
    assert result["candidate_version_relation"] == "newer"
    assert result["candidate_upgrade_available"] is True
    assert result["authorized_upgrade_available"] is False
    assert result["current_release_eligibility_status"] == "bounded_compatibility_source"


def test_unknown_installed_version_is_not_candidate_upgrade(monkeypatch) -> None:
    monkeypatch.setattr(upgrade_check, "validate_release_assertion", lambda *args, **kwargs: _result_validation())
    result = upgrade_check._build_upgrade_result(
        {"fixture": "payload"},
        discovery_source="https_endpoint",
        endpoint="https://example.test/latest.json",
        installed_version_resolver=lambda: "development-build",
        now=datetime(2026, 10, 24, tzinfo=timezone.utc),
    )
    assert result["candidate_version_relation"] == "unknown"
    assert result["candidate_upgrade_available"] is False
    assert result["authorized_upgrade_available"] is False


@pytest.mark.parametrize(
    ("raw", "token"),
    [
        (b"{}", "current_policy_view_fields_invalid"),
        (
            b'{"schema_version":"release_current_policy_view.v0.1",'
            b'"schema_version":"duplicate"}',
            "current_policy_view_duplicate_key",
        ),
        (b"[]", "current_policy_view_root_invalid"),
        (b'\xff', "current_policy_view_json_invalid"),
    ],
)
def test_policy_view_malformed_inputs_fail_closed(tmp_path, raw, token) -> None:
    path = tmp_path / "policy-view.json"
    path.write_bytes(raw)
    with pytest.raises(CurrentPolicyViewError) as exc:
        load_current_policy_evaluation_input(path, observer_highest_seen_sequence=0)
    assert exc.value.token == token


def test_policy_view_oversized_input_fails_closed(tmp_path) -> None:
    path = tmp_path / "policy-view.json"
    path.write_bytes(b" " * (MAX_POLICY_VIEW_FILE_BYTES + 1))
    with pytest.raises(CurrentPolicyViewError) as exc:
        load_current_policy_evaluation_input(path, observer_highest_seen_sequence=0)
    assert exc.value.token == "current_policy_view_too_large"


def test_policy_view_uses_independent_high_water_mark(tmp_path) -> None:
    path = tmp_path / "policy-view.json"
    _write_policy_view(path)
    loaded = load_current_policy_evaluation_input(
        path, observer_highest_seen_sequence=17
    )
    assert loaded.observer_highest_seen_sequence == 17
    assert "observer_highest_seen_sequence" not in _policy_view()


def test_policy_view_change_before_install_prevents_pip(monkeypatch, tmp_path) -> None:
    inputs = iter((_policy_input(marker="download"), _policy_input(marker="install")))
    monkeypatch.setattr(upgrade_cli, "_load_apply_policy_input", lambda **kwargs: next(inputs))
    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **kwargs: _upgrade_result(
            authorized=True, status="verified_current_policy"
        ),
    )
    wheel = tmp_path / "download" / "ilc_core-9.9.9-py3-none-any.whl"
    wheel.parent.mkdir()
    wheel.write_bytes(WHEEL_BYTES)
    monkeypatch.setattr(upgrade_cli, "fetch_and_verify", lambda *args, **kwargs: wheel)
    monkeypatch.setattr(
        upgrade_cli,
        "validate_release_assertion",
        lambda payload, **kwargs: _validation(status="unresolved"),
    )
    monkeypatch.setattr(
        upgrade_cli.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("pip invoked after policy replacement"),
    )
    with pytest.raises(upgrade_cli.UpgradeCliError) as exc:
        upgrade_cli.run_upgrade_command(_apply_args(tmp_path, dry_run=False))
    assert exc.value.token == "arbitrary_source_current_release_eligibility_required"


def test_upgrade_result_write_preserves_and_advances_policy_high_water(
    monkeypatch, tmp_path
) -> None:
    state_path = tmp_path / "upgrade_state.json"
    initial = advance_current_policy_high_water_mark(
        {},
        policy_id="ilc-public-rc-current-policy-v1",
        network_id="ilc-public-rc-01-testnet-harness",
        channel="public_rc",
        accepted_sequence=3,
    )
    write_upgrade_state(initial, state_path)
    result = {
        "current_release_eligibility_status": "verified_current_policy",
        "current_release_eligibility_evidence": {
            "policy_id": "ilc-public-rc-current-policy-v1",
            "network_id": "ilc-public-rc-01-testnet-harness",
            "channel": "public_rc",
            "policy_sequence": 4,
        },
    }
    upgrade_check._write_upgrade_result_preserving_policy_state(
        result, state_path=state_path
    )
    stored = read_upgrade_state(state_path)
    assert read_current_policy_high_water_mark(
        stored,
        policy_id="ilc-public-rc-current-policy-v1",
        network_id="ilc-public-rc-01-testnet-harness",
        channel="public_rc",
    ) == 4


def test_watcher_metadata_preserves_policy_high_water(tmp_path) -> None:
    state_path = tmp_path / "upgrade_state.json"
    initial = advance_current_policy_high_water_mark(
        {},
        policy_id="ilc-public-rc-current-policy-v1",
        network_id="ilc-public-rc-01-testnet-harness",
        channel="public_rc",
        accepted_sequence=5,
    )
    write_upgrade_state(initial, state_path)
    upgrade_cli._write_watcher_state(
        {"checked_at_utc": "2026-10-24T00:00:00Z"},
        state_path=state_path,
        interval_seconds=60,
        daemon=False,
    )
    stored = read_upgrade_state(state_path)
    assert read_current_policy_high_water_mark(
        stored,
        policy_id="ilc-public-rc-current-policy-v1",
        network_id="ilc-public-rc-01-testnet-harness",
        channel="public_rc",
    ) == 5
