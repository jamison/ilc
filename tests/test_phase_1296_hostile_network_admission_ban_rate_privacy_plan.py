from pathlib import Path

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.network.d2d.transport_principal_public_path_preflight import (
    PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN,
    TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
    build_transport_principal_public_path_preflight,
)
from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1296_g8_hostile_network_admission_ban_rate_privacy_plan.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = (
    "docs/phases/"
    "phase_1296_hostile_network_admission_ban_rate_privacy_plan_walkthrough.md"
)
LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
TP_HELPER = "ilc_core/network/d2d/transport_principal_public_path_preflight.py"

REQUIRED_TOKENS = (
    "hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1",
    "hostile_network_plan_verdict_phase_1296=plan_recorded_no_activation",
    "transport_principal_admission_policy_not_activated_phase_1296",
    "transport_principal_ban_registry_not_activated_phase_1296",
    "transport_principal_rate_limit_state_not_activated_phase_1296",
    "transport_principal_privacy_policy_not_activated_phase_1296",
    "requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296",
    "werner_overlay_not_activated_phase_1296",
    "public_p2p_not_activated_phase_1296",
    "public_fetch_serving_not_enabled_phase_1296",
    "public_sidecar_projection_serving_not_enabled_phase_1296",
    "public_rc_remains_blocked_after_phase_1296",
    "phase_1297_sidecar_public_safe_projection_schema_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1296-authenticated-handshake-material",
        handshake_nonce="phase-1296-nonce",
        issued_epoch=40,
        expires_epoch=46,
        current_epoch=43,
    )


def _preflight() -> dict[str, object]:
    return build_transport_principal_public_path_preflight(
        transport_principal_context=_context(),
        current_epoch=43,
        privacy_mode="rotating_pseudonymous_transport_principal",
    )


def test_phase_1296_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:8]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1296_prompt_uses_active_1289_1302_hostile_network_scope() -> None:
    prompt_path = ROOT / PROMPT
    prompt = read(PROMPT)

    assert validate(prompt_path) == []
    assert "Hostile-Network Admission Ban Rate Privacy Plan" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "window_1289_1296_closed_phase_1296" not in prompt
    assert "Window 1289-1296 Closure Gate" not in prompt


def test_phase_1296_active_lock_controls_hostile_network_scope() -> None:
    lock = read(LOCK)
    guidance = read(GUIDANCE)
    spec = read(SPEC)

    assert "| 8 | 1296 | Hostile-network admission, ban, rate-limit, privacy plan | SENSITIVE |" in lock
    assert "| 1296 | Hostile-network admission, ban, rate-limit, privacy plan | SENSITIVE" in guidance
    assert "active 1289-1302 sequence lock controls this phase" in spec


def test_phase_1296_helper_readback_keeps_authenticated_transport_principal_only() -> None:
    context = _context()
    preflight = _preflight()

    assert str(context["admission_key"]).startswith("tp_admission:")
    assert str(context["ban_key"]).startswith("tp_ban:")
    assert str(context["rate_limit_key"]).startswith("tp_rate:")
    assert str(context["replay_key"]).startswith("tp_replay:")
    assert context["requester_id_fallback_allowed"] is False
    assert context["client_ip_rate_limit_key_allowed"] is False
    assert context["agent_id_rate_limit_key_allowed"] is False

    assert preflight["fallback_policy"]["rate_limit_identity_source"] == "authenticated_transport_principal"
    assert preflight["fallback_policy"]["requester_id_fallback_allowed"] is False
    assert preflight["fallback_policy"]["client_ip_rate_limit_key_allowed"] is False
    assert preflight["fallback_policy"]["agent_id_rate_limit_key_allowed"] is False
    assert preflight["fallback_policy"]["harness_identity_rate_limit_key_allowed"] is False
    assert preflight["security_controls"]["privacy_mode"] == "rotating_pseudonymous_transport_principal"
    assert preflight["authorization_flags"]["public_p2p_enabled"] is False
    assert preflight["authorization_flags"]["public_fetch_serving_enabled"] is False

    with pytest.raises(ValueError, match="transport_principal_forbidden_identity_fallback"):
        build_transport_principal_context(
            credential_kind="client_ip",
            credential_material="client_ip:203.0.113.10",
            handshake_nonce="phase-1296-fallback-nonce",
            issued_epoch=40,
            expires_epoch=46,
            current_epoch=43,
        )

    with pytest.raises(ValueError, match=TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN):
        build_transport_principal_public_path_preflight(
            transport_principal_context=context,
            current_epoch=43,
            public_p2p_enabled=True,
        )

    with pytest.raises(ValueError, match=PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN):
        build_transport_principal_public_path_preflight(
            transport_principal_context=context,
            current_epoch=43,
            public_fetch_serving_enabled=True,
        )


def test_phase_1296_records_stale_helper_and_no_promotion_boundary() -> None:
    helper = read(TP_HELPER)
    spec = read(SPEC)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper
    assert "cdl087_not_ratified_by_phase_1277" in helper
    assert "not directly promotable" in spec
    assert "CDL-087 is now ratified" in spec
    assert "Phase 1277 helper is still not directly promotable" in spec
    assert "helper promotion" in spec
    assert "marker removal" in spec


def test_phase_1296_records_future_control_contracts_without_activation() -> None:
    spec = read(SPEC)

    for phrase in (
        "Future Admission Policy Contract",
        "Future Ban Registry Contract",
        "Future Rate-Limit State Contract",
        "Future Privacy Policy Contract",
        "authenticated TransportPrincipal material",
        "bounded state",
        "epoch/sequence validity",
        "fail-closed",
        "High-cardinality spam",
        "Slow request bodies",
        "Privacy correlation",
        "Werner pressure misuse",
    ):
        assert phrase in spec

    for token in (
        "transport_principal_admission_policy_not_activated_phase_1296",
        "transport_principal_ban_registry_not_activated_phase_1296",
        "transport_principal_rate_limit_state_not_activated_phase_1296",
        "transport_principal_privacy_policy_not_activated_phase_1296",
        "werner_overlay_not_activated_phase_1296",
    ):
        assert token in spec


def test_phase_1296_non_claims_keep_public_paths_and_economics_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "TransportPrincipal public-path activation",
            "admission policy activation",
            "ban registry activation",
            "public rate-limit state",
            "privacy policy activation",
            "Werner overlay activation",
            "public credential issuer authority",
            "public P2P",
            "public fetch serving",
            "public sidecar/projection serving",
            "non-loopback bind",
            "wildcard bind",
            "public host bind",
            "listener",
            "peer discovery",
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


def test_phase_1296_updates_frontier_without_public_rc_claim() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1289-1302 is OPEN through Phase 1296" in planning
    assert "Window 1289-1302 is open through Phase 1296" in capsule
    assert "Window 1289-1302 OPEN through Phase 1296" in roadmap
    assert "Phase 1297 is sensitive" in planning
    assert "Phase 1297 is sensitive" in capsule
    assert "Phase 1297 is the next sensitive phase" in roadmap

    assert "Window 1289-1302 is OPEN through Phase 1295" in planning
    assert "Window 1289-1302 is open through Phase 1295" in capsule
    assert "Window 1289-1302 OPEN through Phase 1295" in roadmap
    assert "Phase 1296 is sensitive" in planning
    assert "Phase 1296 is sensitive" in capsule
    assert "Phase 1296 is the next sensitive phase" in roadmap

    assert "public_rc_remains_blocked_after_phase_1296" in planning
    assert "public_rc_remains_blocked_after_phase_1296" in capsule
    assert "public_rc_remains_blocked_after_phase_1296" in roadmap


def test_phase_1296_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" not in register


def test_phase_1296_graph_delta_records_docs_only_plan() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md -> transport/identity",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1296_g8_hostile_network_admission_ban_rate_privacy_plan.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1296_hostile_network_admission_ban_rate_privacy_plan.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1296_hostile_network_admission_ban_rate_privacy_plan_walkthrough.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
