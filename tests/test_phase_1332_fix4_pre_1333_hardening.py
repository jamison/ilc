from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ilc_core.crypto import cbor_canonical
from ilc_core.network import peer as peer_module
from ilc_core.network.d2d import gossip_peer_registry
from ilc_core.network.d2d import http_gossip_transport_runtime as http_runtime
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.rc.atlas_graph_discipline import (
    build_atlas_g_006_public_rc_graph_reachability_gate,
)
from ilc_core.rc.source_allowlist_export_rehearsal import (
    build_source_allowlist_export_rehearsal,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest
from ilc_core.sidecars.transport_principal_admission import (
    ADMISSION_DECISION_STATE,
    TransportPrincipalAdmissionParams,
    TransportPrincipalAdmissionSidecarError,
    build_transport_principal_admission_decision,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
ATLAS_PATH = ROOT / "ilc_core/rc/atlas_graph_discipline.py"
SOURCE_EXPORT_PATH = ROOT / "ilc_core/rc/source_allowlist_export_rehearsal.py"
TRANSPORT_ADMISSION_PATH = ROOT / "ilc_core/sidecars/transport_principal_admission.py"


def _function_node(path: Path, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"function_not_found:{path}:{name}")


def _function_line_count(path: Path, name: str) -> int:
    node = _function_node(path, name)
    assert node.end_lineno is not None
    return node.end_lineno - node.lineno + 1


def _transport_context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1332-fix4-authenticated-handshake-material",
        handshake_nonce="phase-1332-fix4-nonce",
        issued_epoch=90,
        expires_epoch=96,
        current_epoch=92,
    )


@pytest.mark.parametrize(
    "endpoint",
    (
        "https://127.0.0.1",
        "https://10.0.0.1:9443",
        "https://[::1]:9443",
        "https://localhost",
        "https://service.localhost",
        "https://2130706433",
        "https://0x7f000001",
    ),
)
def test_fix4_peer_registry_rejects_private_address_literals(endpoint: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        gossip_peer_registry.validate_peer_endpoint(endpoint)

    assert str(exc_info.value) == gossip_peer_registry.PRIVATE_PEER_ENDPOINT_TOKEN


def test_fix4_private_endpoint_rejection_has_explicit_test_opt_in() -> None:
    assert (
        gossip_peer_registry.validate_peer_endpoint(
            "https://127.0.0.1:9443",
            allow_private_address_literals=True,
        )
        == "https://127.0.0.1:9443"
    )


def test_fix4_http_transport_rejects_private_peer_before_network_open() -> None:
    transport = http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind=http_runtime.TRANSPORT_KIND_HTTP,
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="/definitely/not/read/cert.pem",
            tls_key_path="/definitely/not/read/key.pem",
        )
    )

    with pytest.raises(ValueError) as exc_info:
        transport.send_gossip(
            "https://127.0.0.1:9443",
            gossip_type="claim",
            channel="cid:phase1332fix4",
            epoch=92,
            signature="0" * 128,
            payload=b"{}",
        )

    assert str(exc_info.value) == gossip_peer_registry.PRIVATE_PEER_ENDPOINT_TOKEN


def test_fix4_peer_manager_rejects_private_peer_addresses_by_default() -> None:
    manager = peer_module.PeerManager(local_port=8000)

    with pytest.raises(ValueError) as exc_info:
        manager.add_peer("10.0.0.2", 8100)

    assert str(exc_info.value) == gossip_peer_registry.PRIVATE_PEER_ENDPOINT_TOKEN


def test_fix4_cbor_rejects_oversize_input_before_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    def _forbidden_decode(_payload: bytes) -> object:
        raise AssertionError("cbor2.loads_must_not_be_called_for_oversize_input")

    monkeypatch.setattr(cbor_canonical.cbor2, "loads", _forbidden_decode)

    with pytest.raises(ValueError, match="cbor_input_exceeds_max_bytes_phase_1332_fix4"):
        cbor_canonical.cbor_loads(
            b"x" * (cbor_canonical.MAX_CANONICAL_CBOR_INPUT_BYTES + 1)
        )


def test_fix4_transport_principal_params_dataclass_preserves_decision_contract() -> None:
    params = TransportPrincipalAdmissionParams(
        transport_principal_context=_transport_context(),
        current_epoch=92,
    )

    decision = build_transport_principal_admission_decision(params)

    assert decision["current_epoch"] == 92
    assert decision["state"] == ADMISSION_DECISION_STATE
    assert decision["public_mode_blockers"]


def test_fix4_transport_principal_params_reject_mixed_legacy_arguments() -> None:
    params = TransportPrincipalAdmissionParams(
        transport_principal_context=_transport_context(),
        current_epoch=92,
    )

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as exc_info:
        build_transport_principal_admission_decision(params, current_epoch=92)

    assert exc_info.value.token == "transport_principal_admission_params_invalid_phase_1332_fix4"


def test_fix4_registry_integrity_refactor_preserves_manifest_validation() -> None:
    registry = build_sidecar_registry_manifest()

    assert registry["package_profile_integrity"][
        "confidential_coordination_gossip_policy_manifest"
    ]["local_only"] is True
    assert registry["package_profile_integrity"][
        "public_fetch_p2p_readiness_candidate_manifest"
    ]["public_p2p_enabled"] is False


def test_fix4_atlas_and_source_refactors_preserve_gate_outputs() -> None:
    atlas_gate = build_atlas_g_006_public_rc_graph_reachability_gate()
    source_rehearsal = build_source_allowlist_export_rehearsal(repo_root=ROOT)

    assert atlas_gate["status"] == "pass"
    assert atlas_gate["release_artifact_status"] == "not_authorized"
    assert source_rehearsal["result"] == "pass"
    assert source_rehearsal["mode"] == "dry_run_rehearsal_only"


def test_fix4_blocker_functions_are_split_below_release_gate_limit() -> None:
    assert _function_line_count(REGISTRY_PATH, "_validate_package_profile_integrity") <= 80
    assert (
        _function_line_count(
            ATLAS_PATH,
            "build_atlas_g_006_public_rc_graph_reachability_gate",
        )
        <= 120
    )
    assert _function_line_count(SOURCE_EXPORT_PATH, "build_source_allowlist_export_rehearsal") <= 120


def test_fix4_transport_principal_builder_uses_params_object_boundary() -> None:
    node = _function_node(
        TRANSPORT_ADMISSION_PATH,
        "build_transport_principal_admission_decision",
    )
    arg_count = len(node.args.posonlyargs) + len(node.args.args) + len(node.args.kwonlyargs)

    assert arg_count <= 2
    assert "class TransportPrincipalAdmissionParams" in TRANSPORT_ADMISSION_PATH.read_text(
        encoding="utf-8"
    )
