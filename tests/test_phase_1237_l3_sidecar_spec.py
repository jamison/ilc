from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs/specs/ilc_l3_sidecar_infrastructure_spec_1237_v0.1.md"
EXPANSION_PLAN_PATH = (
    REPO_ROOT
    / "docs/specs/ilc_phase_1237_sidecar_query_runtime_expansion_plan_v0.1.md"
)
PROMPT_DIR = REPO_ROOT / "docs/antigravity_tasks"


REQUIRED_HEADINGS = (
    "## 1. Boundary definition",
    "## 2. Consumption interface",
    "## 3. Privacy constraints",
    "## 4. Visualisation posture",
    "## 5. Mutation prohibition",
    "## 6. Deployment model",
    "## 7. Future runtime phase inputs",
)


FIX_PROMPTS = (
    "antigravity_prompt__phase_1237_fix1_g8_sidecar_query_runtime_skeleton.md",
    "antigravity_prompt__phase_1237_fix2_g8_sidecar_ego_graph_query.md",
    "antigravity_prompt__phase_1237_fix3_g8_sidecar_centrality_metrics.md",
    "antigravity_prompt__phase_1237_fix4_g8_sidecar_convergence_trace.md",
    "antigravity_prompt__phase_1237_fix5_g8_sidecar_dispatcher_integration.md",
    "antigravity_prompt__phase_1237_fix6_g8_sidecar_canonical_export_bundle.md",
    "antigravity_prompt__phase_1237_fix7_g8_sidecar_local_smoke_harness.md",
)


def _spec_text() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def test_phase_1237_l3_sidecar_spec_file_exists() -> None:
    assert SPEC_PATH.exists()


def test_phase_1237_l3_sidecar_spec_contains_all_required_headings() -> None:
    text = _spec_text()
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_phase_1237_l3_sidecar_spec_contains_commit_token() -> None:
    assert "l3_sidecar_infrastructure_spec_committed_phase_1237" in _spec_text()


def test_phase_1237_l3_sidecar_spec_references_projection_runtime() -> None:
    assert "agent_graph_projection_runtime_1229.v0.1" in _spec_text()


def test_phase_1237_l3_sidecar_spec_prohibits_mutation_authority() -> None:
    text = _spec_text()
    assert "no mutation authority" in text
    assert "no write path" in text


def test_phase_1237_l3_sidecar_spec_contains_pending_fix1_token() -> None:
    assert "l3_sidecar_runtime_implementation_pending_fix1_authorization" in _spec_text()


def test_phase_1237_l3_sidecar_spec_excludes_protocol_participation() -> None:
    text = _spec_text()
    assert "does not participate in the ILC protocol" in text
    assert "not a consensus participant" in text


def test_phase_1237_expansion_plan_exists_and_is_tokenized() -> None:
    assert EXPANSION_PLAN_PATH.exists()
    text = EXPANSION_PLAN_PATH.read_text(encoding="utf-8")
    assert "phase_1237_sidecar_query_runtime_expansion_plan_committed" in text


def test_phase_1237_all_fix_prompts_exist() -> None:
    missing = [name for name in FIX_PROMPTS if not (PROMPT_DIR / name).exists()]
    assert missing == []
