"""Phase 1522p closure-gate checks.

PUBLIC_RC_EXCLUDE: phase_1522p_private_closure_gate_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window closure assertion. Not a public RC artifact.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _selftest_mode() -> bool:
    return os.environ.get("ILC_PHASE_1522P_GATE_SELFTEST") == "1"


def _row_for(register: str, obligation_id: str) -> str:
    row_prefix = f"| {obligation_id} |"
    return next(line for line in register.splitlines() if line.startswith(row_prefix))


def test_required_window_tokens_are_present() -> None:
    if _selftest_mode():
        return

    corpus = "\n".join(
        [
            _read("docs/specs/ilc_phase_1515p_1522p_sequence_lock_v0.1.md"),
            _read("docs/specs/ilc_open_obligation_register_v0.1.md"),
            _read("docs/specs/ilc_window_1515p_coherence_report_1521p_v0.1.md"),
            _read("docs/specs/ilc_antigravity_context_capsule_v5.66p_private_1515p.md"),
            _read("docs/phases/STATUS.md"),
        ]
    )

    required_tokens = [
        "window_1515p_sequence_lock_committed",
        "obl_register_stale_routing_patched_phase_1515p",
        "adr_0009_layer0_layer1_encoding_integration_phase_1516p",
        "adr_0009_layer2_layer3_encoding_integration_phase_1517p",
        "adr_0009_four_layer_bundle_chain_complete_phase_1517p",
        "adr_0009_bundle_verifier_implemented_phase_1518p",
        "adr_0009_canonical_test_vectors_committed_phase_1518p",
        "adr_0009_source_export_rehearsal_profile_integration_phase_1519p",
        "adr_0009_promoted_to_accepted_phase_1520p",
        "adr_0009_not_public_distribution_guards_cleared_phase_1520p",
        "obl_026_closed_phase_1520p",
        "window_1515p_coherence_complete_phase_1521p",
        "context_capsule_v5_66p_private_1515p_committed",
    ]
    for token in required_tokens:
        assert token in corpus


def test_adr_0009_is_accepted_and_guards_are_cleared() -> None:
    if _selftest_mode():
        return

    adr = _read("docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md")
    assert "**Status:** Accepted" in adr
    assert "**Ratified:** Phase 1520p - 2026-06-06" in adr

    guard_files = {
        "ilc_core/bundle/layer0_protocol_bundle.py": "ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION = False",
        "ilc_core/bundle/layer1_genesis_bundle.py": "ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION = False",
        "ilc_core/bundle/layer2_epoch_snapshot.py": "ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION = False",
        "ilc_core/bundle/layer3_wire_binding.py": "ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION = False",
    }
    for path, expected in guard_files.items():
        text = _read(path)
        assert expected in text
        assert "guard cleared Phase 1520p - ADR-0009 accepted" in text


def test_obligation_register_records_closure_and_block_routing() -> None:
    if _selftest_mode():
        return

    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    assert "| OBL-002 |" in register
    assert "| permanent-invariant |" in register
    assert "allowlist export" in _row_for(register, "OBL-002")

    obl_026 = _row_for(register, "OBL-026")
    assert "| closed |" in obl_026
    assert "Phase 1520p" in obl_026
    assert "obl_026_closed_phase_1520p" in obl_026

    expected_routes = {
        "OBL-020": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-021": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-022": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-023": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
        "OBL-024": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
        "OBL-025": "Block 3 ADR-0035 homoiconic type-system lane, phase/window TBD by later sequence lock",
        "OBL-027": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-028": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
        "OBL-029": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
    }
    for obligation_id, route in expected_routes.items():
        row = _row_for(register, obligation_id)
        assert "| open |" in row
        assert route in row


def test_closure_handoff_records_pass_verdict_and_public_path_block() -> None:
    if _selftest_mode():
        return

    handoff = _read("docs/specs/ilc_window_1515p_1522p_handoff_1522p_v0.1.md")

    required_tokens = [
        "window_1515p_closed_phase_1522p",
        "window_1515p_closure_gate_committed_phase_1522p",
        "window_1515p_closure_gate_verdict=pass",
        "public_path_remains_blocked_phase_1522p",
        "go_window_1523p_required_next",
    ]
    for token in required_tokens:
        assert token in handoff

    assert "Block 2 ADR-0009 is complete" in handoff
    assert "Window 1523p is not opened by this handoff" in handoff
    assert "CDL-096 remains eligible but unopened" in handoff
    assert "public repository publication" in handoff
    assert "public source export" in handoff
    assert "raw repository publication" in handoff


def test_capsule_and_walkthroughs_exist() -> None:
    if _selftest_mode():
        return

    required_paths = [
        "docs/specs/ilc_antigravity_context_capsule_v5.66p_private_1515p.md",
        "docs/phases/phase_1515p_window_1515p_1522p_sequence_lock_walkthrough.md",
        "docs/phases/phase_1516p_adr_0009_layer0_layer1_encoding_integration_walkthrough.md",
        "docs/phases/phase_1517p_adr_0009_layer2_layer3_encoding_integration_walkthrough.md",
        "docs/phases/phase_1518p_adr_0009_bundle_verifier_test_vectors_walkthrough.md",
        "docs/phases/phase_1519p_adr_0009_source_export_rehearsal_integration_walkthrough.md",
        "docs/phases/phase_1520p_adr_0009_promotion_walkthrough.md",
        "docs/phases/phase_1521p_window_1515p_coherence_capsule_walkthrough.md",
        "docs/phases/phase_1522p_window_1515p_1522p_closure_gate_walkthrough.md",
    ]
    for path in required_paths:
        assert (ROOT / path).exists()


def test_planning_frontier_records_closed_window_and_next_go() -> None:
    if _selftest_mode():
        return

    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")
    sequence_lock = _read("docs/specs/ilc_phase_1515p_1522p_sequence_lock_v0.1.md")

    assert "docs/specs/ilc_window_1515p_1522p_handoff_1522p_v0.1.md" in planning_index
    assert "Window 1515p-1522p CLOSED" in planning_index
    assert "GO Window 1523p" in planning_index
    # HISTORICAL_SNAPSHOT: exact current-marker cardinality is not a live invariant.
    assert planning_index.count("⬅ CURRENT") >= 1

    assert "Phase 1522p - Window 1515p-1522p Closure Gate" in status
    assert "window_1515p_closed_phase_1522p" in status
    assert "window: 1515p-1522p" in agents
    assert "window_1515p_1522p: CLOSED" in agents
    assert "go_window_1523p_required_next" in agents
    assert "**Status:** CLOSED - Phase 1522p closure gate complete" in sequence_lock


def test_non_authorization_floor_is_preserved() -> None:
    if _selftest_mode():
        return

    handoff = _read("docs/specs/ilc_window_1515p_1522p_handoff_1522p_v0.1.md")
    walkthrough = _read(
        "docs/phases/phase_1522p_window_1515p_1522p_closure_gate_walkthrough.md"
    )

    non_authorized_terms = [
        "CDL mutation",
        "ADR mutation",
        "CDL-096 opening",
        "epoch transition",
        "public RC",
        "public source export",
        "public repository publication",
        "public package publication",
        "public bundle serving",
        "public P2P activation",
        "ECU minting",
        "ILC settlement",
        "wallet write",
        "treasury write",
        "CCSS public activation",
        "clearing any non-ADR-0009 guard",
        "raw repository publication",
    ]
    for term in non_authorized_terms:
        assert term in handoff

    assert "graph_delta=load_bearing_artifact_added:docs/specs/ilc_window_1515p_1522p_handoff_1522p_v0.1.md" in walkthrough
