from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1281_g8_window_1281_1288_sequence_lock.md",
    "antigravity_prompt__phase_1282_g8_context_capsule_v5_51_frontier_refresh.md",
    "antigravity_prompt__phase_1283_g8_public_claimability_authority_decision_preflight.md",
    "antigravity_prompt__phase_1284_g8_public_claimability_verifier_api_boundary_preflight.md",
    "antigravity_prompt__phase_1285_g8_transport_principal_public_path_activation_preflight.md",
    "antigravity_prompt__phase_1286_g8_sidecar_public_projection_privacy_serving_preflight.md",
    "antigravity_prompt__phase_1287_g8_release_publication_signing_authorization_preflight.md",
    "antigravity_prompt__phase_1288_g8_window_1281_1288_closure_gate.md",
)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

SENSITIVE_PROMPTS = (
    "antigravity_prompt__phase_1281_g8_window_1281_1288_sequence_lock.md",
    "antigravity_prompt__phase_1283_g8_public_claimability_authority_decision_preflight.md",
    "antigravity_prompt__phase_1284_g8_public_claimability_verifier_api_boundary_preflight.md",
    "antigravity_prompt__phase_1285_g8_transport_principal_public_path_activation_preflight.md",
    "antigravity_prompt__phase_1286_g8_sidecar_public_projection_privacy_serving_preflight.md",
    "antigravity_prompt__phase_1287_g8_release_publication_signing_authorization_preflight.md",
    "antigravity_prompt__phase_1288_g8_window_1281_1288_closure_gate.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1281_1288_guidance_is_planning_only_and_points_to_sequence_lock() -> None:
    text = _text(GUIDANCE)

    assert "window_1281_1288_candidate_phase_grouping_recorded_after_phase_1280" in text
    assert "window_1281_1288_not_open_until_sequence_lock" in text
    assert "This document does not open Window 1281-1288" in text
    assert "GO Phase 1281" in text


def test_window_1281_1288_guidance_routes_all_candidate_phases() -> None:
    text = _text(GUIDANCE)

    for phase in range(1281, 1289):
        assert f"| {phase} |" in text
        assert f"antigravity_prompt__phase_{phase}_" in text

    for concept in (
        "Context Capsule v5.51 frontier refresh",
        "Public claimability authority decision preflight",
        "Public claimability verifier/API boundary preflight",
        "TransportPrincipal public-path activation preflight",
        "Sidecar public projection privacy/serving preflight",
        "Release publication and v0.2 signing authorization preflight",
    ):
        assert concept in text


def test_window_1281_1288_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1281_1288_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text


def test_window_1281_1288_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1281_1288_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1281_1288_preserves_public_non_claims() -> None:
    guidance = _text(GUIDANCE)
    assert "authorize public RC" in guidance
    assert "activate public claimability" in guidance
    assert "authorize public sidecar/projection serving" in guidance
    assert "authorize ECU minting" in guidance
    assert "authorize ILC settlement or withdrawal runtime" in guidance
    assert "authorize v0.2 signing" in guidance

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "Public RC claim" in text or "public-RC claim" in text


def test_window_1281_1288_human_escalation_is_embedded() -> None:
    guidance = _text(GUIDANCE)
    assert "human_question_escalation_required_for_uncertain_authority" in guidance
    assert "prompt the human reviewer" in guidance
    assert "Default to the narrower" in guidance

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## Human escalation rule" in text
        assert "prompt the human reviewer" in text


def test_phase_1283_prompt_requires_default_no_public_claimability_activation() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1283_g8_public_claimability_authority_decision_preflight.md"
    )
    guidance = _text(GUIDANCE)

    token = "public_claimability_activation_not_authorized_by_default_phase_1283"
    assert token in _required_tokens(text)
    assert token in guidance
    assert "explicit human authorization" in text


def test_window_1281_1288_planning_index_points_to_candidate_not_execution() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")

    assert "ilc_window_1281_1288_candidate_phase_grouping_v0.1.md" in text
    assert "window_1281_1288_candidate_phase_grouping_recorded_after_phase_1280" in text
    assert "window_1281_1288_not_open_until_sequence_lock" in text
    assert "Window 1281-1288 is not open until an explicit Phase 1281 sequence lock" in text
    assert "ilc_window_1273_1280_handoff_1280_v0.1.md" in text
    assert "Window 1273-1280 remains CLOSED / PASS through Phase 1280" in text
    assert "public_rc_remains_blocked_after_phase_1280" in text
    assert "Exact-token `rg` is only a schema/completion check" in text


def test_planning_index_session_start_canon_routes_to_1281_candidate_package() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")
    session_start = text.split("## 1. Session-Start Canon", maxsplit=1)[1].split(
        "## 2.", maxsplit=1
    )[0]

    assert "Window 1281-1288 guidance" in session_start
    assert "ilc_window_1281_1288_candidate_phase_grouping_v0.1.md" in session_start
    assert "Window 1273-1280 handoff" in session_start
    assert "ilc_window_1273_1280_handoff_1280_v0.1.md" in session_start
    assert "Window 1281-1288 sequence lock" not in session_start
