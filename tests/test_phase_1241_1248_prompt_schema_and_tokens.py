from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1241_g8_window_1241_1248_sequence_lock.md",
    "antigravity_prompt__phase_1242_g8_roadmap_v1_1_controlling_public_rc_reconciliation.md",
    "antigravity_prompt__phase_1243_g8_gap14_package_profile_contracts_and_import_boundary_inventory.md",
    "antigravity_prompt__phase_1244_g8_ilc_logic_import_boundary_lint_and_protocol_stubs.md",
    "antigravity_prompt__phase_1245_g8_openclaw_nemoclaw_skill_preview_dependency_isolation.md",
    "antigravity_prompt__phase_1246_g8_cdl_087_governance_review_and_ratification_disposition.md",
    "antigravity_prompt__phase_1247_g8_atlas_g_001_003_graph_discipline_slice.md",
    "antigravity_prompt__phase_1248_g8_window_1241_1248_coherence_and_closure_gate.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1241_1248_prompts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1241_1248_prompts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text


def test_window_1241_1248_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_agents_reminds_agents_to_follow_prompt_schema_and_token_search() -> None:
    text = _text(ROOT / "AGENTS.md")
    assert "## Antigravity Prompt Schema Reminder" in text
    assert "docs/antigravity_tasks/README.md" in text
    assert "tools/validate_phase_prompt.py" in text
    assert "Required Tokens" in text
    assert "§0c claim-enumeration discipline" in text
    assert "before the phase-close\ncommit" in text


def test_prompt_schema_requires_status_before_phase_close_commit() -> None:
    text = _text(ROOT / "docs/antigravity_tasks/README.md")
    assert "update walkthrough + STATUS" in text
    assert "commit with git" in text
    assert "phase-close/backfill\ncommit" in text
    assert "before writing the\nwalkthrough or STATUS update" in text
