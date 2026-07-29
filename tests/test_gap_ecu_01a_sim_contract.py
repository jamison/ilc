from pathlib import Path


SPEC = Path("docs/specs/ilc_backward_attribution_sim_contract_GAP_ECU_01a_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_gap_ecu_01a_sim_contract_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")


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


def test_gap_ecu_01a_contract_defines_five_adversarial_scenarios():
    text = SPEC.read_text(encoding="utf-8")
    expected = [
        "Scenario 1: Self-Referential Dependency Loops",
        "Scenario 2: Citation Rings",
        "Scenario 3: Dense Early-Node Capture",
        "Scenario 4: Sybil Reuse Amplification",
        "Scenario 5: Stale-Founder Dominance",
    ]
    for scenario in expected:
        assert scenario in text
    scenario_section = _section_between(text, "## 5. Adversarial Scenario Corpus", "## 6. No-Double-Counting Check Contract")
    assert scenario_section.count("Detection method") == 5
    assert scenario_section.count("FAIL condition") == 5


def test_gap_ecu_01a_contract_has_specific_attack_thresholds_and_bounds():
    text = SPEC.read_text(encoding="utf-8")
    assert 'citation_ring_amplification <= "2.0"' in text
    assert 'early_node_share_epoch_50 <= "0.35"' in text
    assert 'sybil_amplification_factor <= "3.0"' in text
    assert 'stale_founder_ratio <= "1.5"' in text
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
    assert "Decimal strings" in text or "Decimal-string" in text


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
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    token = "backward_attribution_sim_contract_committed_GAP_ECU_01a"
    assert token in status
    assert token in walkthrough
    assert "pending human review before GAP-ECU-01b" in status
