from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1257_1264_candidate_phase_grouping_v0.1.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1257_g8_window_1257_1264_sequence_lock.md",
    "antigravity_prompt__phase_1258_g8_cdl087_production_candidate_evidence_readiness.md",
    "antigravity_prompt__phase_1259_g8_cdl087_serving_peer_evidence_slice.md",
    "antigravity_prompt__phase_1260_g8_cdl087_observability_and_limiter_regression.md",
    "antigravity_prompt__phase_1261_g8_sidecar_projection_endpoint_boundary.md",
    "antigravity_prompt__phase_1262_g8_werner_flow_governor_overlay_validation.md",
    "antigravity_prompt__phase_1263_g8_werner_flow_governor_cdl_decision.md",
    "antigravity_prompt__phase_1264_g8_window_1257_1264_closure_gate.md",
)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

SENSITIVE_PROMPTS = (
    "antigravity_prompt__phase_1257_g8_window_1257_1264_sequence_lock.md",
    "antigravity_prompt__phase_1258_g8_cdl087_production_candidate_evidence_readiness.md",
    "antigravity_prompt__phase_1263_g8_werner_flow_governor_cdl_decision.md",
    "antigravity_prompt__phase_1264_g8_window_1257_1264_closure_gate.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1257_1264_guidance_is_planning_only_and_points_to_sequence_lock() -> None:
    text = _text(GUIDANCE)
    assert "window_1257_1264_candidate_phase_grouping_recorded_after_phase_1256" in text
    assert "window_1257_1264_not_open_until_sequence_lock" in text
    assert "This document does not open Window 1257-1264" in text
    assert "GO Phase 1257" in text


def test_window_1257_1264_guidance_routes_all_candidate_phases() -> None:
    text = _text(GUIDANCE)
    for phase in range(1257, 1265):
        assert f"| {phase} |" in text
        assert f"antigravity_prompt__phase_{phase}_" in text

    assert "CDL-087 production-candidate evidence" in text
    assert "Tier A/B/C classification" in text
    assert "observability collection window" in text
    assert "Sidecar projection endpoint boundary" in text
    assert "Werner Flow Governor overlay validation" in text


def test_window_1257_1264_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1257_1264_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text


def test_window_1257_1264_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1257_1264_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1257_1264_preserves_public_non_claims() -> None:
    guidance = _text(GUIDANCE)
    assert "ratify CDL-087" in guidance
    assert "authorize public sidecar/projection serving" in guidance
    assert "authorize ECU minting" in guidance
    assert "authorize ILC settlement or withdrawal runtime" in guidance

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "Public RC claim" in text or "public-RC claim" in text


def test_window_1257_1264_planning_index_points_to_draft_but_not_execution() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")
    assert "ilc_window_1257_1264_candidate_phase_grouping_v0.1.md" in text
    assert "prompt drafts for Phases 1257-1264" in text
    assert "Does not open Window 1257-1264" in text
