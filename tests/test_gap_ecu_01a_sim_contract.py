import json
from pathlib import Path


SPEC = Path("docs/specs/ilc_backward_attribution_sim_contract_GAP_ECU_01a_v0.1.md")
PROMPT_01B = Path("docs/antigravity_tasks/antigravity_prompt__phase_1595c_g10_gap_ecu_01b_sim_execution.md")
WALKTHROUGH = Path("docs/phases/phase_gap_ecu_01a_sim_contract_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
LEDGER = Path("docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json")


def _section_between(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def test_gap_ecu_01a_contract_addresses_all_nine_parameter_surfaces():
    text = SPEC.read_text(encoding="utf-8")
    section = _section_between(text, "## 4. Parameter Grid", "## 5. Adversarial Scenario Corpus")
    expected = [
        "Triggering events",
        "Eligible upstream artifacts",
        "Typed path semantics",
        "Provenance-distance score",
        "Decay rule",
        "Bidirectional coefficients",
        "Depth and dominance bounds",
        "Refutation interaction",
        "Audit surface",
    ]
    for surface in expected:
        assert surface in section
    assert section.count("| ") >= 10


def test_gap_ecu_01a_contract_defines_six_adversarial_scenarios():
    text = SPEC.read_text(encoding="utf-8")
    expected = [
        "Scenario 1: Self-Referential Dependency Loops",
        "Scenario 2: Citation Rings",
        "Scenario 3: Dense Early-Node Capture",
        "Scenario 4: Sybil Reuse Amplification",
        "Scenario 5: Stale-Founder Dominance",
        "Scenario 6: Novelty-Gate Bypass / Thin-Node Inflation",
    ]
    for scenario in expected:
        assert scenario in text
    scenario_section = _section_between(text, "## 5. Adversarial Scenario Corpus", "## 6. No-Double-Counting Check Contract")
    assert scenario_section.count("Detection method") == 6
    assert scenario_section.count("FAIL condition") == 6


def test_gap_ecu_01a_contract_has_specific_attack_thresholds_and_bounds():
    text = SPEC.read_text(encoding="utf-8")
    assert 'citation_ring_amplification <= "2.0"' in text
    assert 'early_node_share_epoch_50 <= "0.35"' in text
    assert 'sybil_amplification_factor <= "3.0"' in text
    assert 'stale_founder_ratio <= "1.5"' in text
    assert 'thin_node_amplification_factor <= "2.0"' in text
    assert "novelty_filtered_or_discounted_count >= 1" in text
    assert "`MAX_TRAVERSAL_NODES`" in text
    assert "`MAX_TRAVERSAL_EDGES`" in text


def test_gap_ecu_01a_contract_preserves_cdl083_cdl084_no_double_pay():
    text = SPEC.read_text(encoding="utf-8")
    assert "## 6. No-Double-Counting Check Contract" in text
    assert "### 6.1 CDL-083 REFUTATION" in text
    assert "### 6.2 CDL-084 Explicit-Chain PROVENANCE" in text
    assert 'duplicate_refutation_credit == "0"' in text
    assert "same downstream/upstream/event triple is paid by both CDL-084 and backward attribution" in text
    assert "cdl084_explicit_chain_already_settled" in text
    assert "`settle_attribution_batch()` processing `AttributionEvent` objects" in text


def test_gap_ecu_01a_contract_requires_machine_verifiable_evidence():
    text = SPEC.read_text(encoding="utf-8")
    evidence_section = _section_between(text, "## 7. GAP-ECU-01b Evidence Requirements", "## 8. Viability Verdict Criteria")
    for field in [
        "schema_version",
        "contract_sha256",
        "parameter_grid_sha256",
        "scenario_results",
        "no_double_count_results",
        "candidate_region_results",
        "recommended_regions",
        "deterministic_replay_sha256",
    ]:
        assert field in evidence_section
    assert "exactly the six scenario ids from Section 5" in evidence_section
    assert "Decimal strings" in text or "Decimal-string" in text


def test_gap_ecu_01a_contract_defines_gini_population_and_advisory_threshold():
    text = SPEC.read_text(encoding="utf-8")
    evidence_section = _section_between(text, "## 7. GAP-ECU-01b Evidence Requirements", "## 8. Viability Verdict Criteria")
    assert "Gini coefficient over agent-level backward attribution credit shares" in evidence_section or (
        "the Gini coefficient over agent-level backward attribution credit" in evidence_section
    )
    assert "Agents with zero backward" in evidence_section
    assert "remain in the population" in evidence_section
    assert 'gini > "0.80"' in evidence_section
    assert "advisory dominance flag" in evidence_section


def test_gap_ecu_01a_human_review_gate_and_non_claims_are_recorded():
    text = SPEC.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert "GAP-ECU-01b must not execute until the human reviews and approves this contract" in text
    assert "GAP-ECU-01b is blocked until the human reviews and approves this contract" in walkthrough
    assert "This phase does not:" in text
    assert "run a simulation" in text
    assert "open, prelock, ratify, or mutate a CDL" in text
    assert "change `ilc_core/`, Rust consensus, bridge code, guards, or validator code" in text


def test_gap_ecu_01a_status_and_walkthrough_tokens():
    status = STATUS.read_text(encoding="utf-8")
    block = status.split("### Phase GAP-ECU-01a", 1)[1].split("\n### ", 1)[0]
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    token = "backward_attribution_sim_contract_committed_GAP_ECU_01a"
    assert token in block
    assert token in walkthrough
    assert "pending human review before GAP-ECU-01b" in block


def test_gap_ecu_01a_fix2_hardens_gap_ecu_01b_prompt_against_stale_scenario_count():
    prompt = PROMPT_01B.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "run all 6 adversarial scenarios" in prompt
    assert "SIM contract has exactly 6 adversarial scenarios" in prompt
    assert "thin_node_amplification_factor" in prompt
    assert "Gini coefficient over agent-level backward attribution credit shares" in prompt
    assert "gap_ecu_01a_fix2_gini_novelty_contract_hardened" in status


def test_gap_ecu_01a_fix2_ledger_records_amended_contract_and_prompt_hardening():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_path = {entry.get("repo_path"): entry for entry in data.get("annotations", [])}
    assert "six adversarial scenarios" in by_path[
        "docs/specs/ilc_backward_attribution_sim_contract_GAP_ECU_01a_v0.1.md"
    ]["manual_read_summary"]
    assert "gini evidence semantics" in by_path[
        "docs/specs/ilc_backward_attribution_sim_contract_GAP_ECU_01a_v0.1.md"
    ]["manual_read_summary"]
    assert by_path[
        "docs/phases/phase_gap_ecu_01a_fix2_gini_novelty_contract_hardening_walkthrough.md"
    ]["node_kind"] == "phase_walkthrough"
    assert by_path[
        "docs/antigravity_tasks/antigravity_prompt__phase_1595c_g10_gap_ecu_01b_sim_execution.md"
    ]["node_kind"] == "phase_prompt"
