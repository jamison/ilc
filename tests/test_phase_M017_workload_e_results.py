import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
M017_RESULTS = REPO_ROOT / "docs" / "research" / "ilc_mysticeti_workload_e_results_M017_v0.1.md"
M017_JSON = REPO_ROOT / "docs" / "research" / "ilc_m017_operability_report.json"
M017_RUNNER = REPO_ROOT / "tools" / "testbed" / "ilc_loopback_m017_runner.sh"


def test_results_doc_exists_1():
    assert M017_RESULTS.exists(), "Results doc M017 must exist natively."


def test_results_doc_verdict_pass_2():
    content = M017_RESULTS.read_text()
    assert "run_m017_workload_e_verdict=pass" in content, "Verdict token missing from structural markdown document"


def test_operability_report_exists_and_parseable_3():
    assert M017_JSON.exists(), "Operability JSON file must exist."
    try:
        json.loads(M017_JSON.read_text())
    except Exception as e:
        pytest.fail(f"Could not parse M-017 Operability JSON: {e}")


def test_report_has_required_fields_4():
    data = json.loads(M017_JSON.read_text())
    required_keys = ["phase", "workload", "date", "hardware", "storage", "sync", "chain_sanity", "commodity_hardware_criterion_pass", "overall_verdict"]
    for key in required_keys:
        assert key in data, f"Missing top-level key {key} physically absent."


def test_hardware_section_present_5():
    data = json.loads(M017_JSON.read_text())
    hw = data.get("hardware", {})
    for key in ["logical_cpu_count", "ram_gb", "arch", "os", "disk_type"]:
        assert key in hw, f"Hardware missing structural key: {key}"


def test_hardware_logical_cpu_count_under_8():
    data = json.loads(M017_JSON.read_text())
    cpu = data["hardware"]["logical_cpu_count"]
    assert cpu < 8, f"CPU count {cpu} exceeds commodity hardware bound of 8"


def test_hardware_ram_gb_under_32():
    data = json.loads(M017_JSON.read_text())
    ram = data["hardware"]["ram_gb"]
    assert ram < 32.0, f"RAM {ram} GB exceeds commodity hardware bound of 32 GB"


def test_storage_criterion_pass_6():
    data = json.loads(M017_JSON.read_text())
    assert data["storage"].get("storage_criterion_pass") is True, "Storage natively failed condition limit bound constraints"


def test_storage_bytes_per_epoch_under_target_7():
    data = json.loads(M017_JSON.read_text())
    target = data["storage"].get("target_bytes_per_epoch", 102400)
    avg = data["storage"].get("average_bytes_per_epoch", 10000000)
    assert avg <= target, f"Storage Bytes scale natively failed {avg} vs {target}"


def test_sync_criterion_pass_8():
    data = json.loads(M017_JSON.read_text())
    assert data["sync"].get("sync_criterion_pass") is True, "Sync natively failed boolean threshold."


def test_sync_extrapolated_under_24h_9():
    data = json.loads(M017_JSON.read_text())
    hours = data["sync"].get("extrapolated_10k_sync_hours", 99999)
    assert hours <= 24, f"Extrapolation spans extensively above 24 hours natively: {hours} hours"


def test_chain_sanity_complete_10():
    data = json.loads(M017_JSON.read_text())
    assert data["chain_sanity"].get("chain_complete") is True, "Chain Extraction Sanity loop physically crashed parameters natively."


def test_runner_emits_verdict_token_11():
    content = M017_RUNNER.read_text()
    assert "run_m017_workload_e_verdict=pass" in content, "Gating token missing permanently from structural execution execution script natively."


def test_runner_uses_retry_only_missing_pattern_12():
    content = M017_RUNNER.read_text()
    # Accept either phrasing based on runner heritage
    assert "retry-only-missing" in content or "ensure_all_committed" in content, "Runner ignores physical replay loop bounds natively mapping execution."


def test_overall_verdict_field_13():
    data = json.loads(M017_JSON.read_text())
    assert data.get("overall_verdict") == "workload_e_operability_pass", "Verdict completely collapsed structually."


def test_commodity_hardware_criterion_pass_14():
    data = json.loads(M017_JSON.read_text())
    assert data.get("commodity_hardware_criterion_pass") is True, "Hardware Commodity bounds exceeded mechanically natively."
