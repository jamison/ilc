from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1249_g8_window_1249_1256_sequence_lock.md",
    "antigravity_prompt__phase_1250_g8_gap14_adapter_extraction_import_debt.md",
    "antigravity_prompt__phase_1251_g8_gap14_package_ci_and_profile_size_audit.md",
    "antigravity_prompt__phase_1252_g8_gap13_claimability_resolution_boundary.md",
    "antigravity_prompt__phase_1253_g8_transport_principal_identity_and_http_downgrade.md",
    "antigravity_prompt__phase_1254_g8_atlas_g_004_005_high_authority_dependency_bridge.md",
    "antigravity_prompt__phase_1255_g8_tla_refinement_and_allowlist_export.md",
    "antigravity_prompt__phase_1256_g8_window_1249_1256_closure_gate.md",
)

SENSITIVE_PROMPTS = (
    "antigravity_prompt__phase_1249_g8_window_1249_1256_sequence_lock.md",
    "antigravity_prompt__phase_1252_g8_gap13_claimability_resolution_boundary.md",
    "antigravity_prompt__phase_1256_g8_window_1249_1256_closure_gate.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1249_1256_guidance_is_planning_only_and_points_to_sequence_lock() -> None:
    text = _text(GUIDANCE)
    assert "window_1249_1256_candidate_phase_grouping_recorded_after_phase_1248" in text
    assert "window_1249_1256_not_open_until_sequence_lock" in text
    assert "This document does not open Window 1249-1256" in text
    assert "GO Phase 1249" in text


def test_window_1249_1256_guidance_routes_all_candidate_phases() -> None:
    text = _text(GUIDANCE)
    for phase in range(1249, 1257):
        assert f"| {phase} |" in text
        assert f"antigravity_prompt__phase_{phase}_" in text

    assert "Gap 14 adapter extraction" in text
    assert "Gap 13 claimability resolution boundary" in text
    assert "TransportPrincipal identity spec" in text
    assert "ATLAS-G-004/005" in text
    assert "TLA+ refinement notes and allowlist-export procedure" in text


def test_window_1249_1256_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1249_1256_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text


def test_window_1249_1256_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1249_1256_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1249_1256_claimability_prompt_preserves_existing_boundary() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1252_g8_gap13_claimability_resolution_boundary.md"
    )
    assert "public_claimability_runtime_not_activated_phase_1252" in text
    assert "epoch_commit_settlement_not_agent_manual_claim_default_phase_1252" in text
    assert "rc0_1_balance_visibility_does_not_imply_public_claimability" in text
    assert "ecu_accrual_reaches_ilc_balance_only_through_epoch_commit" in text


def test_window_1249_1256_planning_index_points_to_draft_but_not_execution() -> None:
    text = _text(ROOT / "docs/PLANNING_INDEX.md")
    assert "ilc_window_1249_1256_candidate_phase_grouping_v0.1.md" in text
    assert "executable prompt drafts for Phases 1249-1256" in text
    assert "explicit `GO Phase 1249`" in text
    assert "Does not open Window 1249-1256" in text
