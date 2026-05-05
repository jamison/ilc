import ast
import hashlib
import os
from pathlib import Path

import pytest

from ilc_core.economics import epoch_attribution_settle_runtime as settle_rt
from ilc_core.network.d2d import http_fetch_transport_runtime as http_fetch


SELFTEST_MODE = os.environ.get("ILC_PHASE_1217_GATE_SELFTEST") == "1"

SEQ_LOCK = Path("docs/specs/ilc_phase_1209_1217_sequence_lock_v0.1.md")
SETTLE_RUNTIME = Path("ilc_core/economics/epoch_attribution_settle_runtime.py")
PERMANENCE_PACKET = Path("docs/specs/ilc_truth_primitive_permanence_ratification_packet_1211_v0.1.md")
HTTP_TRANSPORT = Path("ilc_core/network/d2d/http_fetch_transport_runtime.py")
WIRING_TEST = Path("tests/test_phase_1212_rate_limiter_wiring.py")
MANIFEST = Path("docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md")
CHECKLIST = Path("docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md")
PHASE_1214 = Path("docs/phases/phase_1214_cdl_086_ratification_walkthrough.md")
PHASE_1215 = Path("docs/phases/phase_1215_v0_2_signing_ceremony_walkthrough.md")
COHERENCE = Path("docs/specs/ilc_integration_coherence_report_1216_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.47.md")
HANDOFF = Path("docs/specs/ilc_window_1209_1217_handoff_1217_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
IMMUTABLE_DIAGNOSTIC = Path("out/genesis_compile_coverage_diagnostic_v0.1.json")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cat0_selftest_env_required():
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1217_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_exists_and_token_present():
    assert SEQ_LOCK.exists()
    assert "window_1209_1217_sequence_lock_committed" in _read(SEQ_LOCK)


def test_cat2_settle_runtime_version_contains_1210_v0_7():
    assert settle_rt.EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == (
        "epoch_attribution_settle_runtime_1210.v0.7"
    )


def test_cat3_settle_attribution_batch_accepts_epoch_node_mint_count():
    source = _read(SETTLE_RUNTIME)
    tree = ast.parse(source)
    fn = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "settle_attribution_batch"
    )
    assert "epoch_node_mint_count" in [arg.arg for arg in fn.args.args]


def test_cat4_truth_primitive_permanence_packet_exists():
    assert PERMANENCE_PACKET.exists()


def test_cat5_truth_primitive_permanence_packet_token_present():
    assert "truth_primitive_permanence_ratification_packet_committed_phase_1211" in _read(
        PERMANENCE_PACKET
    )


def test_cat6_rate_limiter_persistent_path_config_present():
    assert "persistent_limiter_path" in _read(HTTP_TRANSPORT)
    assert "Path | None" in _read(HTTP_TRANSPORT)


def test_cat7_rate_limiter_wiring_token_present():
    combined = _read(HTTP_TRANSPORT) + _read(WIRING_TEST)
    assert "persistent_rate_limiter_transport_wiring_committed_phase_1212" in combined


def test_cat8_cdl_086_ratification_prep_docs_exist():
    assert MANIFEST.exists()
    assert CHECKLIST.exists()


def test_cat9_cdl_086_status_ratified_or_deferred():
    status_text = _read(STATUS) + _read(PHASE_1214) + _read(HANDOFF)
    assert (
        "cdl_086_ratified_phase_1214" in status_text
        or "cdl_086_ratification_deferred_pending_counsel_disposition" in status_text
    )


def test_cat10_v0_2_signing_signed_or_deferred():
    status_text = _read(STATUS) + _read(PHASE_1215) + _read(HANDOFF)
    assert (
        "genesis_atlas_v0_2_signed_phase_1215" in status_text
        or "v0_2_signing_ceremony_deferred_pending_signing_authorization" in status_text
    )


def test_cat11_coherence_report_1216_exists():
    assert COHERENCE.exists()
    assert "coherence_report_1216_verdict=pass" in _read(COHERENCE)


def test_cat12_capsule_v5_47_exists_and_supersedes_v5_46():
    assert CAPSULE.exists()
    assert "capsule_v5_47_supersedes_v5_46" in _read(CAPSULE)


def test_cat13_signed_genesis_v0_1_hash_unchanged_in_sequence_lock():
    assert "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c" in _read(
        SEQ_LOCK
    )


def test_cat14_immutable_diagnostic_sha_matches_committed_value():
    assert (
        _sha256(IMMUTABLE_DIAGNOSTIC)
        == "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
    )


def test_cat15_handoff_records_rate_limiter_boundary():
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in _read(HANDOFF)


def test_cat16_handoff_carries_reciprocal_fetch_admission():
    assert "reciprocal_fetch_admission_model_required" in _read(HANDOFF)


def test_cat17_epoch_node_mint_count_zero_compat_tests_present():
    assert "edge_mint_phi_bound_enforcement_skipped_no_node_mints" in _read(
        Path("tests/test_phase_1210_phi_bound_enforcement.py")
    )


def test_cat18_no_float_literals_in_phi_bound_enforcement_function():
    source = _read(SETTLE_RUNTIME)
    tree = ast.parse(source)
    fn = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "settle_attribution_batch"
    )
    float_constants = [
        node.value
        for node in ast.walk(fn)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert float_constants == []


def test_cat19_handoff_closure_tokens_present():
    content = _read(HANDOFF)
    assert "window_1209_1217_closed_phase_1217" in content
    assert "window_1209_1217_closure_gate_verdict=pass" in content


def test_cat20_status_and_planning_closed():
    status = _read(STATUS)
    planning = _read(PLANNING_INDEX)
    assert "## Phase 1217" in status
    assert "window_1209_1217_closure_gate_verdict=pass" in status
    assert "Window 1209-1217 is CLOSED" in planning
