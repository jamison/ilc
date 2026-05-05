from pathlib import Path


COHERENCE = Path("docs/specs/ilc_integration_coherence_report_1207_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.46.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
STATUS = Path("docs/phases/STATUS.md")


def test_phase_1207_coherence_report_exists_and_passes() -> None:
    content = COHERENCE.read_text(encoding="utf-8")
    assert "coherence_report_1207_verdict=pass" in content
    assert "cdl_086_prelock_committed_phase_1204" in content
    assert "truth_primitive_permanence_governance_routed_phase_1206" in content


def test_capsule_v5_46_supersedes_v5_45() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_46_supersedes_v5_45" in content
    assert "docs/specs/ilc_antigravity_context_capsule_v5.45.md" in content


def test_capsule_records_runtime_versions_and_deferred_tokens() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    for token in (
        "tier3_runtime_linkage_runtime_1201.v0.1",
        "persistent_fetch_rate_limiter_runtime_1202.v0.1",
        "edge_mint_phi_bound_enforcement_not_yet_implemented",
        "v0_2_signing_ceremony_deferred_pending_signing_authorization",
        "truth_primitive_permanence_ratification_packet_required_window_1209",
    ):
        assert token in content


def test_capsule_records_immutable_diagnostic_sha() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in content


def test_planning_index_points_to_capsule_v5_46() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1200-1208 is IN PROGRESS through Phase 1207" in content
    assert "Capsule v5.46" in content
    assert "ilc_antigravity_context_capsule_v5.46.md" in content


def test_status_records_phase_1207() -> None:
    content = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1207" in content
    assert "coherence_report_1207_verdict=pass" in content
    assert "capsule_v5_46_supersedes_v5_45" in content
