import hashlib
import os
from pathlib import Path

import pytest


SELFTEST_MODE = os.environ.get("ILC_PHASE_1224_GATE_SELFTEST") == "1"

SEQ_LOCK = Path("docs/specs/ilc_phase_1218_1224_sequence_lock_v0.1.md")
CEREMONY = Path("docs/specs/ilc_truth_primitive_permanence_ceremony_materials_1219_v0.1.md")
RATIFICATION = Path("docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md")
CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SIGNING_WALKTHROUGH = Path("docs/phases/phase_1221_v0_2_signing_ceremony_walkthrough.md")
FETCH_SPEC = Path("docs/specs/ilc_reciprocal_fetch_admission_model_spec_1222_v0.1.md")
PROJECTION_SPEC = Path("docs/specs/ilc_agent_graph_projection_interface_spec_1222_v0.1.md")
REPORT = Path("docs/specs/ilc_integration_coherence_report_1223_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.48.md")
HANDOFF = Path("docs/specs/ilc_window_1218_1224_handoff_1224_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1224_window_1218_1224_closure_gate_walkthrough.md")
DIAGNOSTIC = Path("out/genesis_compile_coverage_diagnostic_v0.1.json")

EXPECTED_DIAGNOSTIC_SHA = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
GENESIS_V0_1_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1224_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_exists_and_token_present() -> None:
    text = _read(SEQ_LOCK)
    assert "window_1218_1224_sequence_lock_committed" in text


def test_cat2_phase_1219_ceremony_materials_exist() -> None:
    assert CEREMONY.exists()
    assert "truth_primitive_permanence_ceremony_materials_committed_phase_1219" in _read(CEREMONY)


def test_cat3_permanence_has_exactly_one_final_routing_token() -> None:
    status = _read(Path("docs/phases/STATUS.md"))
    attested = "truth_primitive_permanence_genesis_attested_phase_1219" in status
    blocked = "truth_primitive_permanence_ratification_blocked_phase_1219" in status
    assert attested is True
    assert blocked is False


def test_cat4_attested_ratification_event_has_authority_and_dissent() -> None:
    text = _read(RATIFICATION)
    assert "Attestation statement" in text
    assert "Genesis authority" in text
    assert "Dissent" in text
    assert "No dissent recorded." in text


def test_cat5_no_blocker_path_needed_when_attested() -> None:
    text = _read(RATIFICATION)
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in text
    assert "truth_primitive_permanence_ratification_blocked_phase_1219" not in text


def test_cat6_cdl_086_status_ratified_or_deferred() -> None:
    register = _read(CDL_REGISTER)
    assert "cdl_086_ratified_phase_1220" in register
    assert "| CDL-086 |" in register
    assert "| ratified |" in register


def test_cat7_v0_2_signing_routed() -> None:
    text = _read(SIGNING_WALKTHROUGH)
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text


def test_cat8_fetch_spec_exists() -> None:
    assert FETCH_SPEC.exists()


def test_cat9_fetch_spec_contains_token_and_reframing() -> None:
    text = _read(FETCH_SPEC)
    assert "reciprocal_fetch_admission_model_spec_committed_phase_1222" in text
    assert "fetch_distribution_architecture_reframed_phase_1222" in text
    assert "Non-Selected Candidate" in text


def test_cat8b_projection_interface_spec_exists() -> None:
    assert PROJECTION_SPEC.exists()


def test_cat9b_projection_interface_spec_contains_committed_token() -> None:
    text = _read(PROJECTION_SPEC)
    assert "agent_graph_projection_interface_spec_committed_phase_1222" in text


def test_cat9c_projection_interface_defers_l3_sidecar_to_window_1225_plus() -> None:
    text = _read(PROJECTION_SPEC)
    assert "l3_sidecar_infrastructure_spec_required_window_1225_plus" in text
    assert "Deferred to Window 1225+" in text


def test_cat10_coherence_report_exists() -> None:
    assert REPORT.exists()
    assert "coherence_report_1223_verdict=pass" in _read(REPORT)


def test_cat11_capsule_v5_48_exists_and_token_present() -> None:
    assert CAPSULE.exists()
    assert "capsule_v5_48_supersedes_v5_47" in _read(CAPSULE)


def test_cat12_signed_genesis_v0_1_hash_unchanged_in_sequence_lock() -> None:
    assert GENESIS_V0_1_HASH in _read(SEQ_LOCK)


def test_cat13_immutable_diagnostic_sha_matches_committed_value() -> None:
    digest = hashlib.sha256(DIAGNOSTIC.read_bytes()).hexdigest()
    assert digest == EXPECTED_DIAGNOSTIC_SHA


def test_cat14_rate_limit_boundary_recorded() -> None:
    handoff = _read(HANDOFF)
    capsule = _read(CAPSULE)
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in handoff + capsule


def test_cat15_ratification_event_contains_explicit_dissent_field() -> None:
    text = _read(RATIFICATION)
    assert "Dissent" in text
    assert "No dissent recorded." in text


def test_cat16_ratification_event_contains_explicit_genesis_authority_attestation() -> None:
    text = _read(RATIFICATION)
    assert "Attestation statement" in text
    assert "Genesis authority" in text


def test_closure_handoff_and_walkthrough_tokens_present() -> None:
    handoff = _read(HANDOFF)
    walkthrough = _read(WALKTHROUGH)
    assert "window_1218_1224_closed_phase_1224" in handoff
    assert "window_1218_1224_closure_gate_verdict=pass" in handoff
    assert "**Status:** complete" in walkthrough
    assert "window_1218_1224_closed_phase_1224" in walkthrough
