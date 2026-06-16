from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_homoiconic_test_registry_guidance_uses_current_fix_order() -> None:
    guidance = read(
        "docs/specs/ilc_homoiconic_test_registry_implementation_guidance_v0.1.md"
    )
    planning = read("docs/PLANNING_INDEX.md")
    combined = guidance + "\n" + planning

    assert "Phase 1545p-Fix35: registry-mode pytest sidecar scaffold" in combined
    assert "Phase 1545p-Fix36: canonical evidence envelope rehearsal" in combined
    assert "Phase 1545p-Fix37: graph-hydrated workspace mode" in combined
    assert "Phase 1545p-Fix38: graph-derived test frontier report" in combined
    assert "Fix35 canonical evidence envelope rehearsal" not in combined
    assert "Fix36 graph-derived test frontier report" not in combined


def test_fix32_contract_no_longer_skips_sidecar_phase() -> None:
    contract = read("docs/specs/ilc_homoiconic_test_registry_contract_1545p_fix32_v0.1.md")

    assert "## 9. Fix35 Registry-Mode Sidecar Contract" in contract
    assert "## 10. Fix36 Evidence Envelope Contract" in contract
    assert "## 11. Fix37 Graph-Hydrated Workspace Contract" in contract
    assert "## 12. Fix38 Frontier Report Contract" in contract
    assert contract.count("AST alone must not define the") == 1


def test_block6_guidance_records_topology_hard_stop_and_scope_boundary() -> None:
    block6 = read("docs/specs/ilc_window_1565_1575_block6_candidate_phase_grouping_v0.1.md")

    assert "Phase 1568 may not begin unless Phase 1567 records a PASS" in block6
    assert "A failed or ambiguous topology check is a Block 6 stop condition" in block6
    assert "This section assumes the Fix18 core-only v0.4 target" in block6
    assert "Block 6 guidance must be patched before Phase 1573" in block6


def test_forward_planning_reconciliation_locks_blocker_boundaries() -> None:
    reconciliation = read(
        "docs/specs/ilc_forward_planning_reconciliation_after_fix35_1545p_v0.1.md"
    )
    planning = read("docs/PLANNING_INDEX.md")

    assert "block6_critical_path_reaffirmed_after_fix35" in reconciliation
    assert "Fix31 scope decision" in reconciliation
    assert "It does not block `GO Phase 1565`" in reconciliation
    assert "B10-B12 fallback edge reclassification" in reconciliation
    assert "does not block Fix18 core-only v0.4 signing" in reconciliation
    assert "publication_refresh_required_before_public_rc_gate_phase_1545p_fix35" in planning
