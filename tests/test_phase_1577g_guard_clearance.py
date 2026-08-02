from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ilc_core.consensus.production_bridge import (
    ConsensusBridgeConfig,
    ILCConsensusGrpcReadAdapter,
    verify_validator_cert_against_graph,
)
from ilc_core.consensus.validator_endpoint_assertion import (
    ValidatorEndpointAssertion,
    validator_assertion_candidate_id,
)


MANIFEST_PATH = Path("docs/specs/ilc_validator_endpoint_assertions_manifest_1577f_v0.1.json")
VERIFY_INSTANT = datetime(2026, 8, 3, tzinfo=timezone.utc)


class ManifestAtlas:
    def __init__(
        self,
        assertions: list[dict[str, Any]],
        edges: list[dict[str, Any]] | None = None,
    ) -> None:
        self._nodes = {
            validator_assertion_candidate_id(item["validator_agent_id"]): item
            for item in assertions
        }
        self._edges = list(edges or [])

    def get_node(self, candidate_id: str) -> dict[str, Any] | None:
        return self._nodes.get(candidate_id)

    def iter_edges(self) -> list[dict[str, Any]]:
        return self._edges


class RecordingRpc:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[tuple[object, int]] = []

    def __call__(self, request: object, *, timeout: int) -> object:
        self.calls.append((request, timeout))
        return self.response


class FakeReadStub:
    def __init__(self) -> None:
        self.GetEpoch = RecordingRpc(SimpleNamespace(current_epoch=9))


def _manifest() -> dict[str, Any]:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _assertions() -> list[dict[str, Any]]:
    assertions = _manifest()["assertions"]
    assert isinstance(assertions, list)
    return assertions


def _first_assertion() -> dict[str, Any]:
    return _assertions()[0]


def _cert_der_for(assertion: dict[str, Any]) -> bytes:
    endpoint = str(assertion["grpc_endpoint"])
    host, _, _port = endpoint.partition(":")
    validator_id = host.rsplit("-", maxsplit=1)[-1]
    cert_path = (
        Path(str(_manifest()["config_root"]))
        / "certs"
        / f"validator_{validator_id}_cert.der"
    )
    der = cert_path.read_bytes()
    assert hashlib.sha256(der).hexdigest() == assertion["tls_cert_sha256_fingerprint"]
    return der


def _atlas() -> ManifestAtlas:
    manifest = _manifest()
    return ManifestAtlas(manifest["assertions"], manifest["revision_edges"])


def _passes_bls(*_args: object) -> bool:
    return True


def test_m009_manifest_backed_cert_assertion_verifies_after_guard_clearance() -> None:
    assertion = _first_assertion()

    assert (
        verify_validator_cert_against_graph(
            validator_agent_id=assertion["validator_agent_id"],
            presented_cert_der=_cert_der_for(assertion),
            atlas_reader=_atlas(),
            expected_bls_public_key_hex=assertion["bls_public_key_hex"],
            network_id=_manifest()["network_id"],
            bls_verifier=_passes_bls,
            now_utc=VERIFY_INSTANT,
        )
        is True
    )


def test_m009_manifest_backed_wrong_fingerprint_is_rejected() -> None:
    assertion = _first_assertion()

    with pytest.raises(ValueError, match="validator_cert_fingerprint_mismatch"):
        verify_validator_cert_against_graph(
            validator_agent_id=assertion["validator_agent_id"],
            presented_cert_der=b"wrong-phase-1577g-cert",
            atlas_reader=_atlas(),
            expected_bls_public_key_hex=assertion["bls_public_key_hex"],
            network_id=_manifest()["network_id"],
            bls_verifier=_passes_bls,
            now_utc=VERIFY_INSTANT,
        )


def test_m009_manifest_backed_inline_superseded_assertion_is_rejected() -> None:
    assertion = dict(_first_assertion())
    assertion["revised_by"] = "validator_grpc_endpoint_assertion:replacement"

    with pytest.raises(ValueError, match="validator_cert_assertion_superseded"):
        verify_validator_cert_against_graph(
            validator_agent_id=assertion["validator_agent_id"],
            presented_cert_der=_cert_der_for(assertion),
            atlas_reader=ManifestAtlas([assertion]),
            expected_bls_public_key_hex=assertion["bls_public_key_hex"],
            network_id=_manifest()["network_id"],
            bls_verifier=_passes_bls,
            now_utc=VERIFY_INSTANT,
        )


def test_m009_manifest_backed_not_yet_valid_assertion_is_rejected() -> None:
    assertion = _first_assertion()

    with pytest.raises(ValueError, match="validator_cert_assertion_not_yet_valid"):
        verify_validator_cert_against_graph(
            validator_agent_id=assertion["validator_agent_id"],
            presented_cert_der=_cert_der_for(assertion),
            atlas_reader=_atlas(),
            expected_bls_public_key_hex=assertion["bls_public_key_hex"],
            network_id=_manifest()["network_id"],
            bls_verifier=_passes_bls,
            now_utc=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )


def test_m009_manifest_backed_expired_assertion_is_rejected() -> None:
    assertion = _first_assertion()

    with pytest.raises(ValueError, match="validator_cert_assertion_expired"):
        verify_validator_cert_against_graph(
            validator_agent_id=assertion["validator_agent_id"],
            presented_cert_der=_cert_der_for(assertion),
            atlas_reader=_atlas(),
            expected_bls_public_key_hex=assertion["bls_public_key_hex"],
            network_id=_manifest()["network_id"],
            bls_verifier=_passes_bls,
            now_utc=datetime(2027, 8, 3, tzinfo=timezone.utc),
        )


def test_adapter_with_m009_manifest_config_verifies_once_then_caches() -> None:
    assertion = _first_assertion()
    stub = FakeReadStub()
    cert_calls = 0

    def cert_provider() -> bytes:
        nonlocal cert_calls
        cert_calls += 1
        return _cert_der_for(assertion)

    adapter = ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(
            target=assertion["grpc_endpoint"],
            graph_binding_validator_agent_id=assertion["validator_agent_id"],
            graph_binding_expected_bls_public_key_hex=assertion["bls_public_key_hex"],
            graph_binding_network_id=_manifest()["network_id"],
        ),
        stub=stub,
        validator_graph_binding_atlas_reader=_atlas(),
        validator_graph_binding_cert_der_provider=cert_provider,
        validator_graph_binding_bls_verifier=_passes_bls,
        validator_graph_binding_now_utc=VERIFY_INSTANT,
    )

    assert adapter.get_epoch() == 9
    assert adapter.get_epoch() == 9
    assert cert_calls == 1
    assert len(stub.GetEpoch.calls) == 2


def test_adapter_without_graph_binding_config_fails_closed_without_monkeypatch() -> None:
    stub = FakeReadStub()
    adapter = ILCConsensusGrpcReadAdapter(
        ConsensusBridgeConfig(target="validator.example:7101"),
        stub=stub,
    )

    with pytest.raises(
        ValueError,
        match="validator_cert_graph_binding_config_missing_phase_1577b_fix1",
    ):
        adapter.get_epoch()
    assert stub.GetEpoch.calls == []


def test_manifest_assertions_are_parseable_under_cdl_105_schema() -> None:
    loaded = [ValidatorEndpointAssertion.from_dict(item) for item in _assertions()]

    assert len(loaded) == 4
    assert {assertion.validator_agent_id for assertion in loaded} == {
        item["validator_agent_id"] for item in _manifest()["assertion_index"]
    }
