from pathlib import Path

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.network.d2d.transport_principal_public_path_preflight import (
    PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN,
    REQUESTER_ID_FALLBACK_STILL_FORBIDDEN_TOKEN,
    TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
    build_transport_principal_public_path_preflight,
    validate_transport_principal_public_path_preflight,
)
from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1295_g8_release_allowlist_artifact_genesis_readiness_preflight.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = (
    "docs/phases/"
    "phase_1295_transport_principal_lifecycle_revocation_replay_preflight_walkthrough.md"
)
LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
TP_HELPER = "ilc_core/network/d2d/transport_principal_public_path_preflight.py"

REQUIRED_TOKENS = (
    "transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1",
    "transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable",
    "cdl087_ratified_but_phase_1277_helper_still_pre_ratification_gate_phase_1295",
    "transport_principal_public_path_helper_not_promoted_phase_1295",
    "transport_principal_lifecycle_policy_not_activated_phase_1295",
    "transport_principal_revocation_registry_not_activated_phase_1295",
    "transport_principal_replay_cache_not_activated_phase_1295",
    "requester_id_fallback_still_forbidden_phase_1295",
    "public_p2p_not_activated_phase_1295",
    "public_fetch_serving_not_enabled_phase_1295",
    "public_rc_remains_blocked_after_phase_1295",
    "phase_1296_hostile_network_admission_ban_rate_privacy_plan_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1295-authenticated-handshake-material",
        handshake_nonce="phase-1295-nonce",
        issued_epoch=30,
        expires_epoch=36,
        current_epoch=33,
    )


def _preflight() -> dict[str, object]:
    return build_transport_principal_public_path_preflight(
        transport_principal_context=_context(),
        current_epoch=33,
    )


def test_phase_1295_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:5]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1295_prompt_uses_active_1289_1302_transport_scope() -> None:
    prompt_path = ROOT / PROMPT
    prompt = read(PROMPT)

    assert validate(prompt_path) == []
    assert "TransportPrincipal Lifecycle Revocation Replay Preflight" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "release_allowlist_artifact_genesis_readiness_preflight_phase_1295.v0.1" not in prompt


def test_phase_1295_active_lock_controls_transport_scope() -> None:
    lock = read(LOCK)
    guidance = read(GUIDANCE)
    spec = read(SPEC)

    assert "| 7 | 1295 | TransportPrincipal lifecycle, revocation, replay preflight | SENSITIVE |" in lock
    assert "| 1295 | TransportPrincipal lifecycle, revocation, replay preflight | SENSITIVE" in guidance
    assert "active 1289-1302 sequence lock controls" in spec


def test_phase_1295_runtime_readback_keeps_helper_internal_and_not_promotable() -> None:
    preflight = _preflight()
    helper = read(TP_HELPER)
    spec = read(SPEC)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper
    assert "cdl087_not_ratified_by_phase_1277" in helper
    assert preflight["authorization_flags"]["cdl087_ratified"] is False
    assert preflight["authorization_flags"]["public_p2p_enabled"] is False
    assert preflight["authorization_flags"]["public_fetch_serving_enabled"] is False
    assert preflight["authorization_flags"]["non_loopback_projection_enabled"] is False

    assert "CDL-087 is now ratified by Phase 1278 Fix1" in spec
    assert "authorization_flags.cdl087_ratified == False" in spec
    assert "helper cannot be promoted directly" in spec
    assert "transport_principal_public_path_helper_not_promoted_phase_1295" in spec


def test_phase_1295_local_lifecycle_revocation_replay_checks_remain_fail_closed() -> None:
    preflight = _preflight()

    with pytest.raises(ValueError, match="transport_principal_public_path_epoch_window_invalid"):
        validate_transport_principal_public_path_preflight(
            {**preflight, "current_epoch": 37},
            current_epoch=37,
        )

    with pytest.raises(ValueError, match="transport_principal_public_path_revoked"):
        validate_transport_principal_public_path_preflight(
            preflight,
            current_epoch=33,
            revoked_credential_fingerprints={str(preflight["credential_fingerprint"])},
        )

    with pytest.raises(ValueError, match="transport_principal_public_path_replay_detected"):
        validate_transport_principal_public_path_preflight(
            preflight,
            current_epoch=33,
            replay_cache={str(preflight["replay_key"])},
        )

    public_tampered = dict(preflight)
    public_tampered["authorization_flags"] = dict(preflight["authorization_flags"])
    public_tampered["authorization_flags"]["public_p2p_enabled"] = True
    with pytest.raises(ValueError, match=TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN):
        validate_transport_principal_public_path_preflight(public_tampered, current_epoch=33)

    fetch_tampered = dict(preflight)
    fetch_tampered["authorization_flags"] = dict(preflight["authorization_flags"])
    fetch_tampered["authorization_flags"]["public_fetch_serving_enabled"] = True
    with pytest.raises(ValueError, match=PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN):
        validate_transport_principal_public_path_preflight(fetch_tampered, current_epoch=33)

    fallback_tampered = dict(preflight)
    fallback_tampered["fallback_policy"] = dict(preflight["fallback_policy"])
    fallback_tampered["fallback_policy"]["requester_id_fallback_allowed"] = True
    with pytest.raises(ValueError, match=REQUESTER_ID_FALLBACK_STILL_FORBIDDEN_TOKEN):
        validate_transport_principal_public_path_preflight(fallback_tampered, current_epoch=33)


def test_phase_1295_records_future_policy_gaps() -> None:
    spec = read(SPEC)

    for phrase in (
        "Public credential issuer authority",
        "Accepted public credential kinds",
        "Credential lifecycle",
        "Revocation registry",
        "Replay cache",
        "Admission state",
        "Ban state",
        "Rate-limit state",
        "Privacy mode",
        "CDL-087 post-ratification contract",
        "Helper export eligibility",
    ):
        assert phrase in spec


def test_phase_1295_non_claims_keep_public_paths_and_economics_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "TransportPrincipal public-path activation",
            "public credential issuer authority",
            "credential lifecycle policy activation",
            "public revocation registry activation",
            "public replay cache activation",
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
            "materialized export manifest",
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


def test_phase_1295_updates_frontier_without_public_rc_claim() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1289-1302 is OPEN through Phase 1295" in planning
    assert "Window 1289-1302 is open through Phase 1295" in capsule
    assert "Window 1289-1302 OPEN through Phase 1295" in roadmap
    assert "Phase 1296 is sensitive" in planning
    assert "Phase 1296 is sensitive" in capsule
    assert "Phase 1296 is the next sensitive phase" in roadmap

    assert "Window 1289-1302 is OPEN through Phase 1294" in planning
    assert "Window 1289-1302 is open through Phase 1294" in capsule
    assert "Window 1289-1302 OPEN through Phase 1294" in roadmap
    assert "Phase 1295 is sensitive" in planning
    assert "Phase 1295 is sensitive" in capsule
    assert "Phase 1295 is the next sensitive phase" in roadmap

    assert "public_rc_remains_blocked_after_phase_1295" in planning
    assert "public_rc_remains_blocked_after_phase_1295" in capsule
    assert "public_rc_remains_blocked_after_phase_1295" in roadmap


def test_phase_1295_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" not in register


def test_phase_1295_graph_delta_records_docs_only_preflight() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md -> transport/identity",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1295_g8_release_allowlist_artifact_genesis_readiness_preflight.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1295_transport_principal_lifecycle_revocation_replay_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1295_transport_principal_lifecycle_revocation_replay_preflight_walkthrough.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
