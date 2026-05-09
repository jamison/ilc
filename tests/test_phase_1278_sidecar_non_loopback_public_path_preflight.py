from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.graph.sidecar_public_path_preflight import (
    CDL087_FIX_AFTER_1278_PLANNED_TOKEN,
    NO_NEW_PUBLIC_LISTENER_TOKEN,
    NON_LOOPBACK_BIND_NOT_ENABLED_TOKEN,
    PUBLIC_PROJECTION_ENDPOINT_NOT_ENABLED_TOKEN,
    SIDECAR_PUBLIC_PATH_PREFLIGHT_REF_PREFIX,
    SIDECAR_PUBLIC_PATH_PREFLIGHT_VERSION,
    SIDECAR_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
    TRANSPORT_PRINCIPAL_AND_CDL087_REQUIRED_TOKEN,
    build_sidecar_public_path_preflight,
    export_sidecar_public_path_preflight_json,
    sidecar_public_path_preflight_ref,
    validate_sidecar_public_path_preflight,
)
from ilc_core.graph.sidecar_query_runtime import (
    SIDECAR_QUERY_RUNTIME_VERSION,
    export_sidecar_query_json,
    export_sidecar_query_ndjson,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.network.d2d.transport_principal_public_path_preflight import (
    TRANSPORT_PRINCIPAL_PUBLIC_PATH_PREFLIGHT_VERSION,
    build_transport_principal_public_path_preflight,
)
from ilc_core.rc.local_skill_preview import (
    build_local_skill_preview_manifest,
    export_local_skill_preview_json,
)


MODULE_PATH = Path("ilc_core/graph/sidecar_public_path_preflight.py")
SIDECAR_RUNTIME_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")
LOCAL_PREVIEW_PATH = Path("ilc_core/rc/local_skill_preview.py")
PACKAGE_PROFILES_PATH = Path("ilc_core/rc/package_profiles.py")
SPEC_PATH = Path("docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1278_sidecar_non_loopback_public_path_preflight_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1",
    "sidecar_public_serving_not_enabled_phase_1278",
    "transport_principal_and_cdl087_required_before_public_projection_phase_1278",
    "no_new_public_listener_phase_1278",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _transport_principal_preflight() -> dict[str, object]:
    context = build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1278-authenticated-handshake-material",
        handshake_nonce="phase-1278-nonce",
        issued_epoch=30,
        expires_epoch=34,
        current_epoch=32,
    )
    return build_transport_principal_public_path_preflight(
        transport_principal_context=context,
        current_epoch=32,
    )


def _sidecar_preflight() -> dict[str, object]:
    return build_sidecar_public_path_preflight(
        transport_principal_preflight=_transport_principal_preflight(),
        current_epoch=32,
    )


def test_phase_1278_sidecar_preflight_binds_transport_principal_and_fails_closed() -> None:
    preflight = _sidecar_preflight()

    assert preflight["version"] == SIDECAR_PUBLIC_PATH_PREFLIGHT_VERSION
    assert preflight["state"] == "sidecar_public_path_preflight_only"
    assert preflight["sidecar_runtime_version"] == SIDECAR_QUERY_RUNTIME_VERSION
    assert (
        preflight["transport_principal_preflight_version"]
        == TRANSPORT_PRINCIPAL_PUBLIC_PATH_PREFLIGHT_VERSION
    )

    authorization_flags = preflight["authorization_flags"]
    assert isinstance(authorization_flags, dict)
    for flag in (
        "sidecar_public_serving_enabled",
        "public_projection_endpoint_enabled",
        "non_loopback_bind_enabled",
        "new_public_listener_enabled",
        "peer_discovery_enabled",
        "public_fetch_serving_enabled",
        "public_p2p_enabled",
        "cdl087_ratified",
        "transport_principal_public_path_authorized",
        "release_artifact_authorized",
    ):
        assert authorization_flags[flag] is False

    local_surface_policy = preflight["local_surface_policy"]
    assert isinstance(local_surface_policy, dict)
    assert local_surface_policy["in_process_import_allowed"] is True
    assert local_surface_policy["harness_subprocess_allowed"] is True
    assert local_surface_policy["public_host_bind_allowed"] is False
    assert local_surface_policy["wildcard_bind_allowed"] is False

    for key, prefix in (
        ("transport_principal_preflight_ref", "transport_principal_public_path_preflight_sha256:"),
        ("transport_principal_principal_id", "tp:"),
        ("transport_principal_rate_limit_key", "tp_rate:"),
        ("transport_principal_admission_key", "tp_admission:"),
        ("transport_principal_ban_key", "tp_ban:"),
        ("transport_principal_replay_key", "tp_replay:"),
        ("sidecar_preflight_sha256", ""),
    ):
        value = preflight[key]
        assert isinstance(value, str)
        assert value.startswith(prefix)
        assert len(value.removeprefix(prefix)) == 64

    for token in REQUIRED_TOKENS:
        assert token in preflight["tokens"]
    assert CDL087_FIX_AFTER_1278_PLANNED_TOKEN in preflight["tokens"]


@pytest.mark.parametrize(
    ("flag_name", "token"),
    (
        ("sidecar_public_serving_enabled", SIDECAR_PUBLIC_SERVING_NOT_ENABLED_TOKEN),
        ("public_projection_endpoint_enabled", PUBLIC_PROJECTION_ENDPOINT_NOT_ENABLED_TOKEN),
        ("non_loopback_bind_enabled", NON_LOOPBACK_BIND_NOT_ENABLED_TOKEN),
        ("new_public_listener_enabled", NO_NEW_PUBLIC_LISTENER_TOKEN),
        ("peer_discovery_enabled", NO_NEW_PUBLIC_LISTENER_TOKEN),
        ("public_fetch_serving_enabled", SIDECAR_PUBLIC_SERVING_NOT_ENABLED_TOKEN),
        ("public_p2p_enabled", SIDECAR_PUBLIC_SERVING_NOT_ENABLED_TOKEN),
        ("cdl087_ratified", TRANSPORT_PRINCIPAL_AND_CDL087_REQUIRED_TOKEN),
        (
            "transport_principal_public_path_authorized",
            TRANSPORT_PRINCIPAL_AND_CDL087_REQUIRED_TOKEN,
        ),
        ("release_artifact_authorized", "sidecar_release_artifact_not_authorized_phase_1278"),
    ),
)
def test_phase_1278_public_serving_and_authorization_flags_fail_closed(
    flag_name: str,
    token: str,
) -> None:
    kwargs = {
        "transport_principal_preflight": _transport_principal_preflight(),
        "current_epoch": 32,
        flag_name: True,
    }
    with pytest.raises(ValueError, match=token):
        build_sidecar_public_path_preflight(**kwargs)


def test_phase_1278_validate_rejects_tampering_and_float_values() -> None:
    preflight = _sidecar_preflight()

    tampered_listener = dict(preflight)
    tampered_listener["authorization_flags"] = dict(preflight["authorization_flags"])
    tampered_listener["authorization_flags"]["new_public_listener_enabled"] = True
    with pytest.raises(ValueError, match=NO_NEW_PUBLIC_LISTENER_TOKEN):
        validate_sidecar_public_path_preflight(tampered_listener, current_epoch=32)

    tampered_bind = dict(preflight)
    tampered_bind["local_surface_policy"] = dict(preflight["local_surface_policy"])
    tampered_bind["local_surface_policy"]["wildcard_bind_allowed"] = True
    with pytest.raises(ValueError, match=NO_NEW_PUBLIC_LISTENER_TOKEN):
        validate_sidecar_public_path_preflight(tampered_bind, current_epoch=32)

    current_epoch_mismatch = dict(preflight)
    current_epoch_mismatch["current_epoch"] = 33
    with pytest.raises(ValueError, match="sidecar_public_path_current_epoch_mismatch"):
        validate_sidecar_public_path_preflight(current_epoch_mismatch, current_epoch=32)

    float_tampered = dict(preflight)
    float_tampered["unexpected_float"] = 1.0
    with pytest.raises(ValueError, match="sidecar_public_path_float_values_forbidden"):
        validate_sidecar_public_path_preflight(float_tampered, current_epoch=32)

    hash_tampered = dict(preflight)
    hash_tampered["unexpected_text"] = "hash-mismatch"
    with pytest.raises(ValueError, match="sidecar_public_path_preflight_hash_mismatch"):
        validate_sidecar_public_path_preflight(hash_tampered, current_epoch=32)


def test_phase_1278_canonical_export_and_ref_are_stable() -> None:
    preflight = _sidecar_preflight()
    validated = validate_sidecar_public_path_preflight(preflight, current_epoch=32)
    exported = export_sidecar_public_path_preflight_json(preflight)

    assert exported == json.dumps(
        validated,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    assert json.loads(exported) == validated
    assert sidecar_public_path_preflight_ref(preflight) == (
        f"{SIDECAR_PUBLIC_PATH_PREFLIGHT_REF_PREFIX}:{preflight['sidecar_preflight_sha256']}"
    )


def test_phase_1278_existing_sidecar_exports_remain_local_bounded_and_float_safe() -> None:
    result = {
        "query_type": "phase_1278_sidecar_public_path_gate",
        "score": Decimal("0.25"),
        "nodes": [{"canonical_id": "node:phase-1278"}],
    }
    exported = export_sidecar_query_json(result, max_bytes=512)

    assert exported == json.dumps(
        json.loads(exported),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert json.loads(exported)["score"] == "0.25"

    with pytest.raises(ValueError, match="sidecar_export_size_exceeded"):
        export_sidecar_query_json({"payload": "x" * 64}, max_bytes=10)
    with pytest.raises(ValueError, match="sidecar_export_float_values_forbidden"):
        export_sidecar_query_json({"score": 1.0})
    with pytest.raises(ValueError, match="sidecar_export_ndjson_result_count_exceeded"):
        export_sidecar_query_ndjson([{"a": 1}, {"b": 2}], max_results=1)


def test_phase_1278_local_preview_manifest_remains_local_only() -> None:
    manifest = build_local_skill_preview_manifest()
    payload = json.loads(export_local_skill_preview_json({"manifest": manifest}))

    assert payload["manifest"]["loopback_or_subprocess_only"] is True
    assert payload["manifest"]["transport_principal_required_for_non_loopback"] is True
    assert payload["manifest"]["public_p2p_enabled"] is False
    assert payload["manifest"]["public_claimability_enabled"] is False
    assert payload["manifest"]["final_public_rc_claim"] is False
    assert payload["manifest"]["local_only"] is True


def test_phase_1278_modules_have_no_public_server_or_bind_surface() -> None:
    source = "\n".join(
        _read(path)
        for path in (
            MODULE_PATH,
            SIDECAR_RUNTIME_PATH,
            LOCAL_PREVIEW_PATH,
            PACKAGE_PROFILES_PATH,
        )
    )

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in source
    for forbidden in (
        "ThreadingHTTPServer",
        "BaseHTTPRequestHandler",
        "HTTPServer",
        "socket.socket",
        "socket.bind",
        "serve_forever",
        "bind_host",
        "0.0.0.0",
        "requests.",
        "aiohttp",
    ):
        assert forbidden not in source

    assert "Loopback-only sidecar profile" in source
    assert "Binding beyond loopback requires TransportPrincipal" in source


def test_phase_1278_docs_status_planning_and_roadmap_record_required_tokens() -> None:
    for path in (SPEC_PATH, WALKTHROUGH_PATH, STATUS_PATH, PLANNING_INDEX_PATH, ROADMAP_PATH):
        text = _read(path)
        for token in REQUIRED_TOKENS:
            assert token in text
        assert CDL087_FIX_AFTER_1278_PLANNED_TOKEN in text

    planning = _read(PLANNING_INDEX_PATH)
    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in planning
    assert "CDL-087 is RATIFIED" in planning


def test_phase_1278_records_broad_discovery_non_claims_and_later_cdl087_ratification() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    register = _read(CDL_REGISTER_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "Source expansion" in text
        assert "sidecar" in text
        assert "projection endpoint" in text
        assert "loopback" in text
        assert "non-loopback" in text
        assert "public serving" in text
        assert "listener" in text
        assert "TransportPrincipal" in text
        assert "CDL-087" in text
        assert "privacy" in text

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    assert "| ratified |" in cdl087_rows[0]
    assert "ratified_phase: 1278 Fix1" in cdl087_rows[0]


def test_phase_1278_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_code_added:ilc_core/graph/sidecar_public_path_preflight.py -> sidecar/public_path",
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md -> sidecar/public_path",
        "graph_delta=support_tests_added:tests/test_phase_1278_sidecar_non_loopback_public_path_preflight.py -> validation",
        "graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security",
        "graph_delta=support_only:docs/phases/phase_1278_sidecar_non_loopback_public_path_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status
