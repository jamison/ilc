from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_ccss_004_public_activation_boundary_spec_v0.1.md"
OBL_REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1568_fix3_ccss004_public_activation_boundary_walkthrough.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix3_g10_ccss004_public_activation_boundary.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_boundary_spec_exists_and_records_native_sidecar_only_routing() -> None:
    text = _read(SPEC)

    assert "ccss_004_routing_native_sidecar_only_no_public_transport_path" in text
    assert "native-sidecar-only with no public transport path" in text
    assert "CCSS_004_PUBLIC_TRANSPORT_NOT_ACTIVATED = True" in text
    assert "does not activate public P2P" in text
    assert "does not activate public RC" in text


def test_spec_contains_operator_visible_non_claims() -> None:
    text = _read(SPEC)

    for non_claim in (
        "CCSS-004 does not provide anonymity",
        "CCSS-004 does not claim unlinkability",
        "CCSS-004 does not claim `(epsilon, delta)`-differential privacy",
        "CCSS-004 does not provide Signal-equivalent protection",
        "traffic-analysis resistance only",
    ):
        assert non_claim in text


def test_spec_cites_existing_fail_closed_surfaces() -> None:
    text = _read(SPEC)

    for required in (
        "ccss_004_public_network_forbidden_phase_1327",
        'decision_state="rejected_public_network"',
        "public_confidential_coordination_serving_enabled",
        "public_sidecar_serving_enabled",
        "Deterministic runtime jitter seed is rejected",
    ):
        assert required in text


def test_obl047_closed_with_boundary_scope_only() -> None:
    text = _read(OBL_REGISTER)

    assert "| OBL-047 |" in text
    assert "closed - native-sidecar-only public activation boundary recorded" in text
    assert "ccss_004_routing_native_sidecar_only_no_public_transport_path" in text
    assert "does not activate public confidential coordination serving" in text


def test_status_tokens_and_no_pre_rc_public_transport_token() -> None:
    text = _read(STATUS)

    for token in (
        "obl_047_closed_phase_1568_fix3",
        "ccss_004_public_activation_boundary_spec_committed",
        "ccss_004_fail_closed_guard_review_complete",
        "ccss_004_no_anonymity_overclaim_rules_committed",
        "ccss_004_routing_native_sidecar_only_no_public_transport_path",
        "public_path_remains_blocked_phase_1568_fix3",
    ):
        assert token in text

    assert "ccss_004_routing_pre_rc_with_guard_and_spec" not in text
    assert "ccss_004_public_transport_activated" not in text
    assert "public_confidential_coordination_serving_enabled_phase_1568_fix3" not in text


def test_walkthrough_and_prompt_are_present_with_required_boundaries() -> None:
    walkthrough = _read(WALKTHROUGH)
    prompt = _read(PROMPT)

    assert "No ellipses in walkthrough." in walkthrough
    assert "ccss_004_routing_native_sidecar_only_no_public_transport_path" in walkthrough
    assert "No runtime files were modified" in walkthrough
    assert "python -m pytest tests/test_phase_1568_fix3_ccss004_public_activation_boundary.py -q" in walkthrough
    assert "Phase 1568-Fix3-G10" in prompt
