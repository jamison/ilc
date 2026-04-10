from __future__ import annotations

import importlib.util
import json
from pathlib import Path

LOGIC_GATE_PATH = Path("docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md")
README_PATH = Path("docs/tools/mempalace/README.md")
GUIDELINES_PATH = Path("docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md")
SCHEMA_PATH = Path("docs/specs/ilc_window_guidance_doc_schema_v0.1.md")
ACTIVE_WINDOW_PATH = Path("docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md")
SUPERSEDED_WINDOW_PATH = Path("docs/specs/ilc_window_607_615_candidate_phase_grouping_v0.1.md")
MANIFEST_PATH = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
BRIEF_SCRIPT = Path("tools/mempalace/render_retrieval_brief.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_logic_gate_profile_exists_and_contains_all_ten_gates() -> None:
    text = _read(LOGIC_GATE_PATH)
    for gate in range(1, 11):
        assert f"G{gate}" in text
    assert "authoritative_now" in text
    assert "planning_only" in text
    assert "historical_context_only" in text
    assert "route_elsewhere" in text


def test_readme_guidelines_and_schema_reference_logic_gate_profile() -> None:
    assert "ilc_mempalace_logic_gate_profile_v0.1.md" in _read(README_PATH)
    assert "ilc_mempalace_logic_gate_profile_v0.1.md" in _read(GUIDELINES_PATH)
    assert "ilc_mempalace_logic_gate_profile_v0.1.md" in _read(SCHEMA_PATH)


def test_retrieval_brief_renders_logic_gate_section(tmp_path: Path) -> None:
    brief = _load_module(BRIEF_SCRIPT, "mempalace_logic_gate_brief")
    repo_root = tmp_path / "repo"
    (repo_root / "docs" / "specs").mkdir(parents=True)
    (repo_root / "docs" / "specs" / "x.md").write_text("x", encoding="utf-8")
    doc = tmp_path / "prompt.md"
    doc.write_text("# Phase 607 Example\n\nRead `docs/specs/x.md` first.\n", encoding="utf-8")
    manifest = {"tiers": {"tier_a_canonical": {"include": ["docs/specs/x.md"]}}}
    rendered = brief.render_brief(doc, manifest, repo_root)
    assert "## Reviewer logic gates" in rendered
    assert "`G1`" in rendered
    assert "`G10`" in rendered
    assert "ilc_mempalace_logic_gate_profile_v0.1.md" in rendered


def test_window_607_612_doc_exists_and_preserves_boundary_discipline() -> None:
    text = _read(ACTIVE_WINDOW_PATH)
    required_sections = (
        "## 1. Window identity and scope",
        "## 2. Baseline and inheritance",
        "## 3. Track inventory",
        "## 8. CDL number assignments",
        "## 9. Candidate phase table",
        "## 10. Sensitivity classification",
        "## 14. Non-goals and explicitly deferred items",
        "## 15. Key canonical anchors for prompt drafting",
    )
    for section in required_sections:
        assert section in text
    for phase in range(607, 613):
        assert f"| {phase} |" in text
    assert "no payment implementation" in text
    assert "no wallet-authority opening" in text
    assert "no native escrow authorization" in text
    assert "public auditability is not identical to public identity exposure" in text
    assert "off-chain-first / later-chain direction" in text
    assert "current internal-ledger posture becoming the permanent final substrate" in text


def test_window_607_615_doc_is_retained_as_superseded_planning_lineage() -> None:
    text = _read(SUPERSEDED_WINDOW_PATH)
    assert "This is a superseded candidate grouping draft." in text
    assert "docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md" in text
    assert "Do not use it as the current active window guide" in text


def test_manifest_classifies_new_boundary_and_logic_gate_sources() -> None:
    manifest = json.loads(_read(MANIFEST_PATH))
    tier_a = manifest["tiers"]["tier_a_canonical"]["include"]
    tier_b = manifest["tiers"]["tier_b_planning"]["include"]
    tier_d = manifest["tiers"]["tier_d_historical"]["include"]
    assert "docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md" in tier_a
    assert "docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md" in tier_a
    assert "docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md" in tier_a
    assert "docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md" in tier_b
    assert "docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md" in tier_b
    assert "docs/specs/ilc_window_607_615_candidate_phase_grouping_v0.1.md" in tier_d
