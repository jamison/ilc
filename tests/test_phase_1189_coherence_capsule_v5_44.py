from pathlib import Path


COHERENCE = Path("docs/specs/ilc_integration_coherence_report_1189_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.44.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_coherence_report_exists() -> None:
    assert COHERENCE.exists()


def test_capsule_v5_44_supersedes() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_44_supersedes_v5_43" in content


def test_capsule_records_cdl_085_ratified() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "cdl_085_ratified_phase_1185" in content
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content


def test_capsule_records_three_slice_completion() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "sim_spectral_05_runtime_binding_slice_pass" in content
    assert "sim_spectral_05_economic_flow_slice_pass" in content
    assert "sim_spectral_05_gossip_slice_pass" in content
    assert "sim_spectral_05_three_slice_observer_framework_complete" in content


def test_planning_index_points_to_capsule_v5_44() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Capsule v5.44" in content
    assert "ilc_antigravity_context_capsule_v5.44.md" in content
