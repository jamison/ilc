from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.graph.sidecar_query_runtime import (
    export_sidecar_query_json,
    export_sidecar_query_ndjson,
)
from ilc_core.rc.local_skill_preview import (
    build_local_skill_preview_manifest,
    export_local_skill_preview_json,
)


SPEC_PATH = Path("docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1268_sidecar_loopback_projection_endpoint_boundary_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SIDECAR_RUNTIME_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")
LOCAL_PREVIEW_PATH = Path("ilc_core/rc/local_skill_preview.py")
PACKAGE_PROFILES_PATH = Path("ilc_core/rc/package_profiles.py")

REQUIRED_TOKENS = (
    "sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1",
    "sidecar_loopback_only_no_non_loopback_serving_phase_1268",
    "sidecar_public_path_still_blocked_phase_1268",
    "transport_principal_required_before_non_loopback_projection_phase_1268",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1268_records_required_tokens_everywhere() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough, status, planning, roadmap):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Window 1265-1272 OPEN / PASS through Phase 1268" in planning
    assert "public_rc_remains_blocked_after_phase_1268" in roadmap


def test_phase_1268_endpoint_decision_records_no_new_listener() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert "sidecar_loopback_endpoint_decision_phase_1268=record_boundary_no_new_listener" in text
        assert "No HTTP server" in text
        assert "non-loopback bind" in text
        assert "public sidecar/projection serving" in text


def test_phase_1268_local_skill_manifest_remains_loopback_or_subprocess_only() -> None:
    manifest = build_local_skill_preview_manifest()
    payload = json.loads(export_local_skill_preview_json({"manifest": manifest}))

    assert payload["manifest"]["loopback_or_subprocess_only"] is True
    assert payload["manifest"]["transport_principal_required_for_non_loopback"] is True
    assert payload["manifest"]["public_p2p_enabled"] is False
    assert payload["manifest"]["public_claimability_enabled"] is False
    assert payload["manifest"]["final_public_rc_claim"] is False
    assert payload["manifest"]["local_only"] is True


def test_phase_1268_sidecar_exports_are_canonical_bounded_and_float_safe() -> None:
    result = {
        "query_type": "phase_1268_loopback_boundary_check",
        "score": Decimal("0.125"),
        "nodes": [{"canonical_id": "node:a"}],
    }
    exported = export_sidecar_query_json(result, max_bytes=512)

    assert exported == json.dumps(
        json.loads(exported),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert json.loads(exported)["score"] == "0.125"

    with pytest.raises(ValueError, match="sidecar_export_size_exceeded"):
        export_sidecar_query_json({"payload": "x" * 64}, max_bytes=10)
    with pytest.raises(ValueError, match="sidecar_export_float_values_forbidden"):
        export_sidecar_query_json({"score": 1.0})
    with pytest.raises(ValueError, match="sidecar_export_ndjson_result_count_exceeded"):
        export_sidecar_query_ndjson([{"a": 1}, {"b": 2}], max_results=1)


def test_phase_1268_does_not_add_server_or_socket_surface() -> None:
    source = "\n".join(
        _read(path)
        for path in (SIDECAR_RUNTIME_PATH, LOCAL_PREVIEW_PATH, PACKAGE_PROFILES_PATH)
    )

    for forbidden in (
        "ThreadingHTTPServer",
        "BaseHTTPRequestHandler",
        "HTTPServer",
        "socket.socket",
        "serve_forever",
        "bind_host",
        "0.0.0.0",
        "::",
    ):
        assert forbidden not in source

    assert "Loopback-only sidecar profile" in source
    assert "Binding beyond loopback requires TransportPrincipal" in source


def test_phase_1268_records_broad_discovery_and_graph_node_boundary() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "Source expansion" in text
        assert "Unix socket" in text
        assert "subprocess" in text
        assert "canonical JSON" in text
        assert "NDJSON" in text
        assert "privacy" in text
        assert "Graph Node" in text


def test_phase_1268_preserves_cdl087_open_state_and_public_non_claims() -> None:
    register = _read(CDL_REGISTER_PATH)
    spec = _read(SPEC_PATH)

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    assert "| open |" in cdl087_rows[0]

    for phrase in (
        "CDL-087 ratification",
        "CDL register mutation",
        "Public RC claim",
        "Public P2P exposure",
        "Public fetch serving",
        "Public claimability activation",
        "ECU mint authorization",
        "ILC settlement or withdrawal runtime activation",
        "v0.2 signing",
    ):
        assert phrase in spec


def test_phase_1268_status_records_next_phase_and_graph_delta() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    assert "Phase 1269 - Werner default topology-pressure profile" in status
    assert "phase_1269_werner_default_topology_pressure_profile_next" in status

    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md -> sidecar/public_path",
        "graph_delta=support_tests_added:tests/test_phase_1268_sidecar_loopback_projection_endpoint_boundary.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1268_sidecar_loopback_projection_endpoint_boundary_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status
