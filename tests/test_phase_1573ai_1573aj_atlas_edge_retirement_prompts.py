from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT_AI = (
    REPO_ROOT
    / "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1573ai_g8_atlas_edge_retirement_rehearsal.md"
)
PROMPT_AJ = (
    REPO_ROOT
    / "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1573aj_g8_atlas_edge_retirement_apply.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_read(path).split())


def test_1573ai_prompt_is_non_mutating_rehearsal() -> None:
    text = _read(PROMPT_AI)
    flat = _flat(PROMPT_AI)

    assert "# Phase 1573ai-G8: Atlas Edge Retirement Migration Rehearsal" in text
    assert "**Sensitivity:** **NON-SENSITIVE**" in text
    assert "evidence-only dry-run; no LMDB write" in text
    assert "`REFERENCES`" in text
    assert "`IMPLEMENTS_MODULE`" in text
    assert "`RATIFICATION_EVIDENCE_FOR`" in text
    assert "`USES`" in text
    assert "`OPENED_FOR`" in text
    assert "`PRELOCK_FOR`" in text
    assert "lmdb_mutated" in text
    assert "false" in text
    assert "This phase does not mutate LMDB" in flat


def test_1573ai_prompt_requires_complete_classification_and_apply_gate() -> None:
    text = _read(PROMPT_AI)

    assert "safe_scripted_recipe" in text
    assert "needs_manual_source_read" in text
    assert "preserve_as_exception" in text
    assert "atlas_edge_retirement_apply_ready_phase_1573ai" in text
    assert "atlas_edge_retirement_apply_deferred_with_receipt_phase_1573ai" in text
    assert "Emit exactly one of:" in text


def test_1573ai_prompt_patches_1574_gate() -> None:
    text = _read(PROMPT_AI)

    assert "Patch `docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md`" in text
    assert "atlas_edge_retirement_rehearsal_complete_phase_1573ai" in text
    assert "atlas_edge_retirement_migration_applied_phase_1573aj" in text
    assert "atlas_edge_retirement_apply_deferred_with_receipt_phase_1573ai" in text


def test_1573aj_prompt_halts_without_ready_token() -> None:
    text = _read(PROMPT_AJ)
    flat = _flat(PROMPT_AJ)

    assert "# Phase 1573aj-G8: Atlas Edge Retirement Migration Apply" in text
    assert "if and only if Phase 1573ai emits" in text
    assert "atlas_edge_retirement_apply_ready_phase_1573ai" in text
    assert "halt; do not apply" in text
    assert "atlas_edge_retirement_apply_deferred_with_receipt_phase_1573ai" in text
    assert "halt; manual review required" in text
    assert "If the rehearsal JSON and live LMDB disagree" in flat
    assert "Do not improvise a partial migration" in flat


def test_1573aj_prompt_preserves_lmdb_and_public_boundaries() -> None:
    text = _read(PROMPT_AJ)

    assert "Use one writer process only. No parallel LMDB writes." in text
    assert "no dangling edges" in text
    assert "payload edge count matches row count" in text
    assert "edge ID debt is zero" in text
    assert "This phase does not sign Genesis or Atlas artifacts." in text
    assert "This phase does not push a public mirror." in text
    assert "This phase does not clear public RC." in text
