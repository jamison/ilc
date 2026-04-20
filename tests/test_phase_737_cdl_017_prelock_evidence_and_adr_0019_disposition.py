from __future__ import annotations

import subprocess
from pathlib import Path


EVIDENCE_PATH = Path("docs/research/ilc_validator_agent_design_evidence_v0.1.md")
DISPOSITION_PATH = Path(
    "docs/specs/ilc_adr_0019_graph_native_governance_boundary_disposition_note_v0.1.md"
)
ADR_PATH = Path("docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prelock_evidence_artifact_exists() -> None:
    assert EVIDENCE_PATH.exists()


def test_existing_phase_710_sections_and_tokens_remain_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert "## 1. Baseline and accepted premises" in text
    assert "## 2. Q1-Q6 resolved answers" in text
    assert "## 3. Rejected alternatives" in text
    assert "## 4. CDL-017 prelock mapping" in text
    assert "## 5. Deferred items and later-window routing" in text
    assert "validator_agent_design_evidence_complete" in text
    assert "q1_q6_answers_recorded_for_cdl_017_prelock" in text
    assert "cdl_017_prelock_only_not_ratified_here" in text
    assert "validation_pools_deferred_beyond_cdl_017_core" in text


def test_new_section_6_heading_present_with_exact_text() -> None:
    text = _read(EVIDENCE_PATH)
    assert "## 6. Q1–Q6 answers — 2026-04-19 pre-window conversation" in text


def test_new_section_7_heading_present_with_exact_text() -> None:
    text = _read(EVIDENCE_PATH)
    assert "## 7. CDL-017 prelock checklist satisfaction" in text


def test_phase_737_tokens_present_and_completion_token_is_exclusive() -> None:
    text = _read(EVIDENCE_PATH)
    assert "q3_q5_q6_settled_2026_04_19_recorded_in_prelock_evidence" in text
    assert "cdl_017_prelock_evidence_artifact_updated_phase_737" in text
    assert "sim_validator_01_results_cited_in_prelock_evidence" in text
    assert "sim_topology_01_results_cited_in_prelock_evidence" in text
    assert "cdl_017_prelock_codex_side_complete" in text
    assert "cdl_017_prelock_codex_side_advanced_with_carry_forward" not in text


def test_section_6_records_q3_q5_q6_and_q1_drafting_note() -> None:
    text = _read(EVIDENCE_PATH)
    assert "Q3: topology shuffle authorization is a new CDL, not a CDL-039 amendment." in text
    assert "Q5: epoch-hash v1 remains the production v1 posture for topology shuffle" in text
    assert "Q6: the metric definition remains `validator_cluster_id`" in text
    assert "the derivation relationship is assertable to the governance mechanism during admission — it is not required to be publicly inferrable from either key alone" in text
    assert "epoch-hash v1 with mandatory VRF at `vrf_upgrade_threshold_validator_count 10`" in text


def test_section_7_checklist_cites_full_pass_sim_results() -> None:
    text = _read(EVIDENCE_PATH)
    assert "Phase 734 SIM-VALIDATOR-01 (`sim_validator_01_verdict=pass`" in text
    assert "Phase 736 CDL-068 opening (`cdl_068_opens_phase_736`" in text
    assert "Phase 735 SIM-TOPOLOGY-01 (`sim_topology_01_verdict=pass`" in text
    assert "`distinct_cluster_floor_recommendation 4`" in text
    assert "`max_cluster_share_ceiling_recommendation 33`" in text


def test_adr_0019_disposition_note_exists_with_required_headings() -> None:
    text = _read(DISPOSITION_PATH)
    assert "## 1. Disposition verdict" in text
    assert "## 2. Scope-limiting amendment" in text
    assert "## 3. Consistency with live CDLs and ADMs" in text
    assert "## 4. Activation trigger for revisiting" in text


def test_adr_0019_disposition_note_contains_required_tokens_and_scope_language() -> None:
    text = _read(DISPOSITION_PATH)
    assert "adr_0019_disposition_complete_phase_737" in text
    assert "adr_0019_verdict_accepted_with_scope_amendment" in text
    assert "Verdict: `Accepted with scope-limiting amendment`" in text
    assert "graph-native compilation of governance constants is the long-horizon" in text
    assert "no production governance constant may be moved to graph-native form without a" in text
    assert "the kernel boundary section of ADR-0019 is sound as written and is not" in text
    assert "Acceptance of ADR-0019 means the boundary direction is sound. It does not" in text


def test_adr_file_status_reads_accepted_not_proposed() -> None:
    text = _read(ADR_PATH)
    assert "**Status:** Accepted" in text
    assert "**Status:** Proposed" not in text


def test_decision_log_remains_clean_and_adr_diff_is_only_status_change() -> None:
    result_log = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_log.returncode == 0

    result_adr = subprocess.run(
        ["git", "diff", "--", str(ADR_PATH)],
        capture_output=True,
        check=True,
        text=True,
    )
    diff_text = result_adr.stdout
    changed_lines = [
        line
        for line in diff_text.splitlines()
        if line.startswith("+") or line.startswith("-")
    ]
    assert "-**Status:** Proposed" in diff_text
    assert "+**Status:** Accepted" in diff_text
    assert all("Date:" not in line for line in changed_lines)
    assert all("Dependencies:" not in line for line in changed_lines)
