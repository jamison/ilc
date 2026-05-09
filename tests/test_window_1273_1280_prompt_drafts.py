from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md"
AUDIT = (
    ROOT
    / "docs/specs/ilc_window_1273_1280_prompt_package_outside_audit_2026_05_09_v0.1.md"
)

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1273_g8_window_1273_1280_sequence_lock.md",
    "antigravity_prompt__phase_1274_g8_cdl048_conversion_sweeper_runtime_skeleton.md",
    "antigravity_prompt__phase_1275_g8_claimability_proof_binding_runtime_boundary.md",
    "antigravity_prompt__phase_1276_g8_cdl087_ratification_authorization_preflight.md",
    "antigravity_prompt__phase_1277_g8_transport_principal_public_path_adr_runtime_integration.md",
    "antigravity_prompt__phase_1278_g8_sidecar_non_loopback_public_path_preflight.md",
    "antigravity_prompt__phase_1279_g8_release_manifest_allowlist_prepublication_preflight.md",
    "antigravity_prompt__phase_1280_g8_window_1273_1280_closure_gate.md",
)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

SENSITIVE_PROMPTS = (
    "antigravity_prompt__phase_1273_g8_window_1273_1280_sequence_lock.md",
    "antigravity_prompt__phase_1274_g8_cdl048_conversion_sweeper_runtime_skeleton.md",
    "antigravity_prompt__phase_1275_g8_claimability_proof_binding_runtime_boundary.md",
    "antigravity_prompt__phase_1276_g8_cdl087_ratification_authorization_preflight.md",
    "antigravity_prompt__phase_1277_g8_transport_principal_public_path_adr_runtime_integration.md",
    "antigravity_prompt__phase_1278_g8_sidecar_non_loopback_public_path_preflight.md",
    "antigravity_prompt__phase_1280_g8_window_1273_1280_closure_gate.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1273_1280_guidance_is_planning_only_and_points_to_sequence_lock() -> None:
    text = _text(GUIDANCE)

    assert "window_1273_1280_candidate_phase_grouping_recorded_after_phase_1272" in text
    assert "window_1273_1280_not_open_until_sequence_lock" in text
    assert "This document does not open Window 1273-1280" in text
    assert "GO Phase 1273" in text


def test_window_1273_1280_guidance_routes_all_candidate_phases() -> None:
    text = _text(GUIDANCE)

    for phase in range(1273, 1281):
        assert f"| {phase} |" in text
        assert f"antigravity_prompt__phase_{phase}_" in text

    for concept in (
        "CDL-048 conversion-sweeper runtime skeleton",
        "Public claimability proof-binding runtime boundary",
        "CDL-087 ratification authorization preflight",
        "TransportPrincipal public-path ADR",
        "Sidecar non-loopback/public projection authorization preflight",
        "Release manifest and source allowlist pre-publication preflight",
    ):
        assert concept in text


def test_window_1273_1280_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1273_1280_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text


def test_window_1273_1280_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1273_1280_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1273_1280_preserves_public_non_claims() -> None:
    guidance = _text(GUIDANCE)
    assert "ratify CDL-087" in guidance
    assert "activate public claimability" in guidance
    assert "authorize public sidecar/projection serving" in guidance
    assert "authorize ECU minting" in guidance
    assert "authorize ILC settlement or withdrawal runtime" in guidance
    assert "authorize v0.2 signing" in guidance

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "Public RC claim" in text or "public-RC claim" in text


def test_window_1273_1280_human_escalation_is_embedded() -> None:
    guidance = _text(GUIDANCE)
    assert "human_question_escalation_required_for_uncertain_authority" in guidance
    assert "prompt the human reviewer" in guidance
    assert "Default to the narrower" in guidance

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## Human escalation rule" in text
        assert "prompt the human reviewer" in text


def test_phase_1276_prompt_requires_default_no_register_mutation() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1276_g8_cdl087_ratification_authorization_preflight.md"
    )
    guidance = _text(GUIDANCE)

    token = "cdl087_register_mutation_not_authorized_by_default_phase_1276"
    assert token in _required_tokens(text)
    assert token in guidance
    assert "explicit human ratification authorization" in text


def test_window_1273_1280_planning_index_points_to_open_sequence_lock() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")

    assert "ilc_phase_1273_1280_sequence_lock_v0.1.md" in text
    assert "ilc_window_1273_1280_candidate_phase_grouping_v0.1.md" in text
    assert "Window 1273-1280 OPEN through Phase 1274" in text
    assert "window_1273_1280_sequence_lock_committed" in text
    assert "cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1" in text
    assert "phase_1275_claimability_proof_binding_runtime_requires_explicit_go" in text
    assert "Phase 1275 is next and remains SENSITIVE" in text
    assert "Window 1265-1272 is CLOSED / PASS through Phase 1272" in text


def test_planning_index_session_start_canon_routes_to_current_frontier() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")
    session_start = text.split("## 1. Session-Start Canon", maxsplit=1)[1].split(
        "## 2.", maxsplit=1
    )[0]

    assert "Window 1273-1280 guidance" in session_start
    assert "ilc_window_1273_1280_candidate_phase_grouping_v0.1.md" in session_start
    assert "Window 1265-1272 handoff" in session_start
    assert "ilc_window_1265_1272_handoff_1272_v0.1.md" in session_start
    assert "Window 1249-1256 handoff** ⬅ CURRENT" not in session_start
    assert "Window 1249-1256 handoff** (closed reference)" in session_start


def test_window_1273_1280_outside_audit_records_hardening_without_authority_expansion() -> None:
    audit = _text(AUDIT)
    index = _text(ROOT / "docs/PLANNING_INDEX.md")

    assert "window_1273_1280_prompt_package_outside_audit_2026_05_09.v0.1" in audit
    assert "planning_index_session_start_frontier_hardened_after_audit" in audit
    assert "window_1273_1280_audit_no_authority_expansion" in audit
    assert "planning_index_session_start_canon_stale_after_window_1273_1280_prompt_draft" in audit
    assert "does not open Window 1273-1280" in audit
    assert "Window 1273-1280 OPEN through Phase 1274" in index
    assert "window_1273_1280_sequence_lock_committed" in index
    assert "ilc_window_1273_1280_prompt_package_outside_audit_2026_05_09_v0.1.md" in index
