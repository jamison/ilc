from pathlib import Path


REPORT = Path("docs/specs/ilc_integration_coherence_report_1223_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.48.md")
WALKTHROUGH = Path("docs/phases/phase_1223_coherence_capsule_v5_48_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING = Path("docs/PLANNING_INDEX.md")


def test_coherence_report_exists() -> None:
    assert REPORT.exists()
    text = REPORT.read_text(encoding="utf-8")
    assert "coherence_report_1223_verdict=pass" in text


def test_capsule_v5_48_exists() -> None:
    assert CAPSULE.exists()


def test_capsule_contains_token() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_48_supersedes_v5_47" in text
    assert "coherence_report_1223_verdict=pass" in text


def test_capsule_records_permanence_status() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in text
    assert "commit_epoch_causal_frontier_mapping_spec_required" in text


def test_capsule_records_cdl_086_and_signing_status() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "cdl_086_ratified_phase_1220" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "public-launch acts still separately blocked" in text


def test_capsule_records_fetch_reframing_direction() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "reciprocal_fetch_admission_model_spec_committed_phase_1222" in text
    assert "fetch_distribution_architecture_reframed_phase_1222" in text
    assert "non-selected research candidate" in text
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in text


def test_capsule_records_committed_sha_and_dirty_worktree_note() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in text
    assert "3eb15f5c4c15d6b24191f1403912bfa88df17e47c4a6328a6bdff3905a63bd4d" in text
    assert "dirty generated copy" in text


def test_walkthrough_status_and_planning_updated() -> None:
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING.read_text(encoding="utf-8")
    assert "**Status:** complete" in walkthrough
    assert "capsule_v5_48_supersedes_v5_47" in walkthrough
    assert "## Phase 1223" in status
    assert "coherence_report_1223_verdict=pass" in status
    assert "Capsule v5.48" in planning
