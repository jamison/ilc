from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1265_1272_candidate_phase_grouping_v0.1.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1265_g8_window_1265_1272_sequence_lock.md",
    "antigravity_prompt__phase_1266_g8_cdl087_sensitive_ratification_review.md",
    "antigravity_prompt__phase_1267_g8_transport_principal_runtime_identity_pre_public_path.md",
    "antigravity_prompt__phase_1268_g8_sidecar_loopback_projection_endpoint_boundary.md",
    "antigravity_prompt__phase_1269_g8_werner_default_topology_pressure_profile.md",
    "antigravity_prompt__phase_1270_g8_gap13_claimability_conversion_sweeper_preflight.md",
    "antigravity_prompt__phase_1271_g8_atlas_g_006_public_rc_graph_reachability_gate.md",
    "antigravity_prompt__phase_1272_g8_window_1265_1272_closure_gate.md",
)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

SENSITIVE_PROMPTS = (
    "antigravity_prompt__phase_1265_g8_window_1265_1272_sequence_lock.md",
    "antigravity_prompt__phase_1266_g8_cdl087_sensitive_ratification_review.md",
    "antigravity_prompt__phase_1270_g8_gap13_claimability_conversion_sweeper_preflight.md",
    "antigravity_prompt__phase_1272_g8_window_1265_1272_closure_gate.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1265_1272_guidance_is_planning_only_and_points_to_sequence_lock() -> None:
    text = _text(GUIDANCE)

    assert "window_1265_1272_candidate_phase_grouping_recorded_after_phase_1264" in text
    assert "window_1265_1272_not_open_until_sequence_lock" in text
    assert "This document does not open Window 1265-1272" in text
    assert "GO Phase 1265" in text


def test_window_1265_1272_guidance_routes_all_candidate_phases() -> None:
    text = _text(GUIDANCE)

    for phase in range(1265, 1273):
        assert f"| {phase} |" in text
        assert f"antigravity_prompt__phase_{phase}_" in text

    for concept in (
        "CDL-087 sensitive ratification review",
        "TransportPrincipal runtime identity",
        "Sidecar loopback projection endpoint",
        "Werner default SIM-FETCH topology-pressure profile",
        "Gap 13 claimability conversion-sweeper preflight",
        "ATLAS-G-006 public-RC graph reachability gate",
    ):
        assert concept in text


def test_window_1265_1272_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1265_1272_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text


def test_window_1265_1272_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1265_1272_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1265_1272_preserves_public_non_claims() -> None:
    guidance = _text(GUIDANCE)
    assert "ratify CDL-087" in guidance
    assert "authorize public sidecar/projection serving" in guidance
    assert "authorize ECU minting" in guidance
    assert "authorize ILC settlement or withdrawal runtime" in guidance

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "Public RC claim" in text or "public-RC claim" in text


def test_phase_1266_prompt_requires_default_no_ratification_token() -> None:
    text = _text(
        PROMPT_DIR / "antigravity_prompt__phase_1266_g8_cdl087_sensitive_ratification_review.md"
    )
    guidance = _text(GUIDANCE)
    token = "cdl_087_ratification_not_executed_by_default_phase_1266"

    assert token in _required_tokens(text)
    assert token in guidance


def test_window_1265_1272_planning_index_points_to_guidance_and_open_lock() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")

    assert "ilc_window_1265_1272_candidate_phase_grouping_v0.1.md" in text
    assert "ilc_phase_1265_1272_sequence_lock_v0.1.md" in text
    assert "Window 1265-1272 OPEN / PASS through Phase 1268" in text
    assert "cdl_087_sensitive_ratification_review_phase_1266.v0.1" in text
    assert "transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1" in text
    assert "sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1" in text
