from pathlib import Path


RECIPROCAL_SPEC = Path("docs/specs/ilc_reciprocal_fetch_admission_model_spec_1222_v0.1.md")
PROJECTION_SPEC = Path("docs/specs/ilc_agent_graph_projection_interface_spec_1222_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1222_reciprocal_fetch_admission_model_spec_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")


def test_spec_files_exist() -> None:
    assert RECIPROCAL_SPEC.exists()
    assert PROJECTION_SPEC.exists()
    assert WALKTHROUGH.exists()


def test_spec_contains_required_tokens() -> None:
    text = RECIPROCAL_SPEC.read_text(encoding="utf-8")
    projection = PROJECTION_SPEC.read_text(encoding="utf-8")
    assert "reciprocal_fetch_admission_model_spec_committed_phase_1222" in text
    assert "reciprocal_fetch_admission_model_required" in text
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in text
    assert "agent_graph_projection_interface_spec_committed_phase_1222" in projection


def test_reciprocal_spec_contains_all_required_sections() -> None:
    text = RECIPROCAL_SPEC.read_text(encoding="utf-8")
    required = [
        "## 1. Problem Statement",
        "## 2. Model Parameters",
        "## 3. Interaction With Existing CDLs / ADRs",
        "## 4. Constitutional Routing",
        "## 5. Static Limiter Supersession Boundary",
    ]
    for section in required:
        assert section in text


def test_reciprocal_spec_is_design_only_and_decimal_safe() -> None:
    text = RECIPROCAL_SPEC.read_text(encoding="utf-8")
    assert "DESIGN SPEC ONLY" in text
    assert "No float constants" in text
    assert "Decimal" in text
    assert "math.exp" in text
    assert "does not:" in text
    assert "mutate `ilc_core/`" in text


def test_graph_projection_spec_prioritizes_agent_native_exports() -> None:
    text = PROJECTION_SPEC.read_text(encoding="utf-8")
    for phrase in [
        "authority_graph",
        "claim_composition_graph",
        "provenance_graph",
        "runtime_binding_graph",
        "economic_flow_graph",
        "branchial_convergence_graph",
        "repo_hypergraph",
        "deterministic JSON and NDJSON",
        "No unbounded graph dump by default",
        "l3_sidecar_infrastructure_spec_required_window_1225_plus",
    ]:
        assert phrase in text


def test_phase_1222_status_recorded() -> None:
    status = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1222" in status
    assert "reciprocal_fetch_admission_model_spec_committed_phase_1222" in status
    assert "agent_graph_projection_interface_spec_committed_phase_1222" in status
