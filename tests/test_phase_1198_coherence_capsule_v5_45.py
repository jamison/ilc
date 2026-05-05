from pathlib import Path


COHERENCE = Path("docs/specs/ilc_integration_coherence_report_1198_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.45.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
STATUS = Path("docs/phases/STATUS.md")


def test_phase_1198_coherence_report_exists_and_passes() -> None:
    content = COHERENCE.read_text(encoding="utf-8")
    assert "coherence_report_1198_verdict=pass" in content
    assert "canon_bundle_signing_repair_pass_phase_1197" in content


def test_capsule_v5_45_supersedes_v5_44() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_45_supersedes_v5_44" in content
    assert "docs/specs/ilc_antigravity_context_capsule_v5.44.md" in content


def test_capsule_records_window_1191_1199_phase_tokens() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    for token in (
        "window_1191_1199_sequence_lock_committed",
        "launch_roadmap_v1_0_published_phase_1192",
        "v0_2_signing_ceremony_deferred_pending_signing_authorization",
        "cdl_086_public_launch_packaging_blocker_opened_phase_1194",
        "tier3_runtime_linkage_scope_committed_phase_1195",
        "persistent_rate_limiter_scope_committed_phase_1196",
        "canon_bundle_signing_repair_pass_phase_1197",
    ):
        assert token in content


def test_capsule_records_phase_1197_production_validation_boundary() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "USE_TESTING_CANON_EXPORT_SNAPSHOT = True" in content
    assert "Production validation remains strict" in content
    assert "malformed declared v0.1 exports are still rejected" in content


def test_capsule_records_immutable_diagnostic_sha() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in content


def test_planning_index_points_to_capsule_v5_45() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1191-1199 is IN PROGRESS through Phase 1198" in content
    assert "Capsule v5.45" in content
    assert "ilc_antigravity_context_capsule_v5.45.md" in content


def test_status_records_phase_1198() -> None:
    content = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1198" in content
    assert "coherence_report_1198_verdict=pass" in content
    assert "capsule_v5_45_supersedes_v5_44" in content
