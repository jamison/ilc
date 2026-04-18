"""
tests/test_phase_M016_workload_d_results.py

M-016 Workload D: Replayability and State Extraction

Tests are anchored to literal tokens from the actual run artefacts:
  - docs/research/ilc_mysticeti_workload_d_results_M016_v0.1.md
  - docs/research/ilc_m016_state_extraction_report.json
  - ilc_consensus/src/state_extractor_main.rs
  - tools/testbed/ilc_loopback_m016_runner.sh
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
RESULTS_DOC = REPO_ROOT / "docs/research/ilc_mysticeti_workload_d_results_M016_v0.1.md"
STATE_REPORT = REPO_ROOT / "docs/research/ilc_m016_state_extraction_report.json"
EXTRACTOR_SRC = REPO_ROOT / "ilc_consensus/src/state_extractor_main.rs"
RUNNER = REPO_ROOT / "tools/testbed/ilc_loopback_m016_runner.sh"
CARGO_TOML = REPO_ROOT / "ilc_consensus/Cargo.toml"


# ── 1. Results doc exists ──────────────────────────────────────────────────────

def test_results_doc_exists():
    assert RESULTS_DOC.exists(), f"Results doc not found: {RESULTS_DOC}"


# ── 2. Verdict token present in results doc ────────────────────────────────────

def test_results_doc_verdict_pass():
    text = RESULTS_DOC.read_text()
    assert "run_m016_workload_d_verdict=pass" in text, \
        "Verdict token run_m016_workload_d_verdict=pass not found in results doc"


# ── 3. All three Phase 690 Workload D pass criteria answered PASS ──────────────

def test_results_doc_three_criteria_pass():
    text = RESULTS_DOC.read_text()
    # Criterion 1
    assert "chain_complete=true" in text, \
        "chain_complete=true not found (criterion 1: full chain reconstructible)"
    # Criterion 2
    assert "sentinel_consistent=true" in text, \
        "sentinel_consistent=true not found (criterion 2: any epoch retrievable)"
    # Criterion 3
    assert "genesis_anchor" in text, \
        "genesis_anchor not found (criterion 3: genesis lineage anchor verifiable)"


# ── 4. State extraction report exists and has correct structure ────────────────

def test_state_report_exists_and_parseable():
    assert STATE_REPORT.exists(), f"State report not found: {STATE_REPORT}"
    with open(STATE_REPORT) as f:
        report = json.load(f)
    assert "epoch_chain" in report
    assert "genesis_anchor" in report
    assert "sentinel_current_epoch" in report
    assert "chain_complete" in report
    assert "sentinel_consistent" in report
    assert "verdict" in report


# ── 5. Chain is gap-free 1-5 in the JSON report ────────────────────────────────

def test_state_report_chain_complete_1_to_5():
    with open(STATE_REPORT) as f:
        report = json.load(f)
    epochs = [e["epoch"] for e in report["epoch_chain"]]
    assert epochs == list(range(1, 6)), \
        f"Epoch chain is not complete 1-5: {epochs}"
    assert report["chain_complete"] is True
    assert report["sentinel_consistent"] is True
    assert report["sentinel_current_epoch"] == 5


# ── 6. Genesis anchor matches expected testnet values ─────────────────────────

def test_state_report_genesis_anchor():
    with open(STATE_REPORT) as f:
        report = json.load(f)
    anchor = report["genesis_anchor"]
    assert anchor["network_id"] == "ilc-mysticeti-testnet-m009", \
        f"Unexpected network_id: {anchor['network_id']}"
    assert anchor["genesis_epoch"] == 0, \
        f"Unexpected genesis_epoch: {anchor['genesis_epoch']}"
    assert anchor["validator_count"] == 4, \
        f"Unexpected validator_count: {anchor['validator_count']}"


# ── 7. state_extractor binary is declared in Cargo.toml ──────────────────────

def test_state_extractor_in_cargo_toml():
    text = CARGO_TOML.read_text()
    assert 'name = "state_extractor"' in text, \
        "state_extractor not declared as [[bin]] in Cargo.toml"
    assert 'path = "src/state_extractor_main.rs"' in text, \
        "state_extractor_main.rs path not in Cargo.toml"


# ── 8. Extractor opens LMDB read-only (NO_LOCK + READ_ONLY flags) ─────────────

def test_state_extractor_uses_read_only_no_lock():
    text = EXTRACTOR_SRC.read_text()
    assert "READ_ONLY" in text, \
        "state_extractor must open LMDB with READ_ONLY flag"
    assert "NO_LOCK" in text, \
        "state_extractor must open LMDB with NO_LOCK flag (no live process required)"


# ── 9. Runner emits offline extraction token ───────────────────────────────────

def test_runner_emits_offline_extraction_token():
    text = RUNNER.read_text()
    assert "m016_offline_extraction_start" in text, \
        "Runner must emit m016_offline_extraction_start token"


# ── 10. Runner exits nonzero on failed prerequisite ───────────────────────────

def test_runner_exits_nonzero_on_failure():
    text = RUNNER.read_text()
    assert "exit 1" in text, \
        "Runner must exit 1 on failed prerequisite or extraction verification"


# ── 11. Row-7 replayability cited in results doc ──────────────────────────────

def test_results_doc_cites_row7():
    text = RESULTS_DOC.read_text()
    assert "row-7" in text.lower() or "Row-7" in text, \
        "Results doc must reference row-7 replayability connection"


# ── 12. Report verdict field matches pass ─────────────────────────────────────

def test_state_report_verdict_field():
    with open(STATE_REPORT) as f:
        report = json.load(f)
    assert report["verdict"] == "workload_d_replayability_pass", \
        f"Expected workload_d_replayability_pass, got: {report['verdict']}"
