from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.graph.sidecar_query_runtime import (
    DEFAULT_SIDECAR_EXPORT_MAX_BYTES,
    DEFAULT_SIDECAR_EXPORT_MAX_RESULTS,
    export_sidecar_query_json,
    export_sidecar_query_ndjson,
)
from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_sidecar_public_safe_projection_schema_1297_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1297_g8_sidecar_public_safe_projection_schema.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = (
    "docs/phases/"
    "phase_1297_sidecar_public_safe_projection_schema_walkthrough.md"
)
LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SIDECAR_HELPER = "ilc_core/graph/sidecar_public_path_preflight.py"
SIDECAR_RUNTIME = "ilc_core/graph/sidecar_query_runtime.py"

REQUIRED_TOKENS = (
    "sidecar_public_safe_projection_schema_phase_1297.v0.1",
    "sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving",
    "privacy_filtering_contract_recorded_phase_1297",
    "sidecar_public_projection_fields_not_served_phase_1297",
    "public_sidecar_projection_serving_not_enabled_phase_1297",
    "public_rc_remains_blocked_after_phase_1297",
    "phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1297_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:6]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1297_prompt_uses_active_1289_1302_schema_scope() -> None:
    prompt_path = ROOT / PROMPT
    prompt = read(PROMPT)

    assert validate(prompt_path) == []
    assert "Sidecar Public-Safe Projection Schema" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md" in prompt
    assert "ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "Window 1289-1296" not in prompt


def test_phase_1297_active_lock_controls_sidecar_schema_scope() -> None:
    lock = read(LOCK)
    guidance = read(GUIDANCE)
    spec = read(SPEC)

    assert "| 9 | 1297 | Sidecar public-safe projection schema | SENSITIVE |" in lock
    assert "| 1297 | Sidecar public-safe projection schema | SENSITIVE" in guidance
    assert "GO Phase 1297" in spec
    assert "schema recorded / no serving" in spec


def test_phase_1297_schema_records_deny_by_default_field_classification() -> None:
    spec = read(SPEC)

    for phrase in (
        "PublicSafeSidecarProjectionEnvelope",
        "Deny",
        "Allow candidate",
        "Redact or pseudonymize candidate",
        "Field classification is deny-by-default",
        "Unknown fields are rejected",
        "No raw AgentID",
        "No raw wallet",
        "No public claimability verdicts",
        "bounded response size",
        "Field-decision auditability",
    ):
        assert phrase in spec

    for denied_field in (
        "AgentID",
        "TransportPrincipal id",
        "credential fingerprint",
        "wallet balance",
        "stake",
        "ECU",
        "ILC",
        "settlement",
        "admission policy state",
        "ban registry state",
        "rate-limit state",
        "replay cache",
        "release keys",
        "Genesis Atlas signing material",
    ):
        assert denied_field in spec


def test_phase_1297_runtime_readback_keeps_sidecar_local_bounded_and_canonical() -> None:
    helper = read(SIDECAR_HELPER)
    runtime = read(SIDECAR_RUNTIME)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper
    assert "no listener, bind, or serving surface" in helper
    assert "does not open a\nlistener" in helper
    assert "bind a socket" in helper
    assert "serve projection data" in helper
    assert "enable peer discovery" in helper

    assert "DEFAULT_SIDECAR_EXPORT_MAX_BYTES = 10_000_000" in runtime
    assert "DEFAULT_SIDECAR_EXPORT_MAX_RESULTS = 1_000" in runtime
    assert "sort_keys=True" in runtime
    assert "allow_nan=False" in runtime
    assert "sidecar_export_float_values_forbidden" in runtime
    assert "sidecar_export_decimal_must_be_finite" in runtime
    assert DEFAULT_SIDECAR_EXPORT_MAX_BYTES == 10_000_000
    assert DEFAULT_SIDECAR_EXPORT_MAX_RESULTS == 1_000


def test_phase_1297_local_export_contract_rejects_float_nonfinite_and_unbounded_payloads() -> None:
    assert export_sidecar_query_json({"b": "2", "a": "1"}) == '{"a":"1","b":"2"}'
    assert export_sidecar_query_json({"value": Decimal("1.25")}) == '{"value":"1.25"}'
    assert export_sidecar_query_ndjson([{"b": "2"}, {"a": "1"}]) == '{"b":"2"}\n{"a":"1"}'

    with pytest.raises(ValueError, match="sidecar_export_float_values_forbidden"):
        export_sidecar_query_json({"value": 1.25})

    with pytest.raises(ValueError, match="sidecar_export_decimal_must_be_finite"):
        export_sidecar_query_json({"value": Decimal("NaN")})

    with pytest.raises(ValueError, match="sidecar_export_size_exceeded"):
        export_sidecar_query_json({"payload": "x" * 16}, max_bytes=8)

    with pytest.raises(ValueError, match="sidecar_export_ndjson_result_count_exceeded"):
        export_sidecar_query_ndjson([{"a": "1"}, {"b": "2"}], max_results=1)


def test_phase_1297_non_claims_keep_serving_release_and_economics_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "public sidecar/projection serving",
            "public projection endpoint",
            "non-loopback bind",
            "wildcard bind",
            "public host bind",
            "listener",
            "socket listener",
            "HTTP route",
            "peer discovery",
            "public fetch serving",
            "public P2P",
            "TransportPrincipal public-path activation",
            "public credential issuer authority",
            "public revocation registry",
            "public replay cache",
            "admission policy activation",
            "ban registry activation",
            "public rate-limit state",
            "privacy policy activation",
            "helper promotion",
            "marker removal",
            "source allowlist export",
            "public repository publication",
            "public package publication",
            "release artifact",
            "release-key generation",
            "release envelope",
            "public claimability",
            "public verifier service",
            "wallet withdrawal",
            "wallet transfer",
            "wallet spend",
            "ECU minting",
            "ILC settlement",
            "CDL-088",
            "Genesis",
            "v0.2 signing",
        ):
            assert phrase in text


def test_phase_1297_frontier_docs_advance_to_1298_without_activation() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)
    status = read(STATUS)

    assert "Window 1289-1302 is OPEN through Phase 1297" in planning
    assert "Window 1289-1302 is open through Phase 1297" in capsule
    assert "Window 1289-1302 OPEN through Phase 1297" in roadmap
    assert "Phase 1298 is sensitive" in planning
    assert "Phase 1298 is sensitive" in capsule
    assert "Phase 1298 is the next sensitive phase" in roadmap
    assert "Phase 1298 - Sidecar bind, listener, peer-discovery authority preflight" in status


def test_phase_1297_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    spec = read(SPEC)

    assert "sidecar_public_safe_projection_schema_phase_1297.v0.1" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL-088 opening" in spec
    assert "CDL mutation" in spec
