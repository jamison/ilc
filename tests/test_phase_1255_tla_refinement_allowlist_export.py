from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_tla_refinement_notes_map_current_specs_to_rust_without_stale_overclaim():
    notes = read_repo("docs/research/ilc_tla_plus_rust_refinement_notes_v0.1.md")

    required = [
        "tla_refinement_notes_pre_rc_closed_phase_1255",
        "phase_1255_tla_allowlist_export_complete",
        "ilc_dag_censorship_bounds.tla",
        "ilc_ecu_fast_path_bcast.tla",
        "ilc_partition_heal.tla",
        "MaxRound=5",
        "MaxRound=12",
        "memory-bound",
        "EpochCheckpoint.signers",
        "quorum_threshold",
        "fast_aggregate_verify",
        "handle_ack_for",
        "BalanceStore::apply_transfer",
        "MissingEpochSync",
    ]
    for token in required:
        assert token in notes

    stale = "verifies an aggregate signature against the full current validator-set key list"
    assert stale not in notes


def test_allowlist_export_procedure_preserves_publication_boundary_and_exclusions():
    procedure = read_repo(
        "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md"
    )

    required = [
        "allowlist_export_procedure_defined_phase_1255",
        "public_repository_publication_not_authorized_phase_1255",
        "phase_1255_tla_allowlist_export_complete",
        "allowlist_export_procedure_defined_required_before_public_repo_publication",
        "counsel_license_instrument_selection_required_before_public_rc",
        "counsel_cla_text_approved_required_before_external_contributors",
        "counsel_trademark_policy_published_required_before_public_launch",
        "us_provisional_patent_application_filed_required_before_public_repo_publication",
        "docs/research/patent_pending/",
        "Z_Past_Chats/",
        "docs/antigravity_tasks/",
        "docs/phases/",
        "denylist overrides allowlist",
        "clean public genesis commit",
        "no git history rewrite",
    ]
    for token in required:
        assert token in procedure

    non_authorized = [
        "public repository publication",
        "public release artifact distribution",
        "public RC announcement",
        "external contributor onboarding",
        "release-key generation",
        "v0.2 signing",
    ]
    for token in non_authorized:
        assert token in procedure


def test_tla_forward_plan_records_phase_1255_closure_and_maxround_boundary():
    plan = read_repo("docs/specs/ilc_tla_plus_formal_verification_forward_planning_v0.1.md")

    assert "tla_refinement_notes_pre_rc_closed_phase_1255" in plan
    assert "Phase 1255" in plan
    assert "MaxRound=12" in plan
    assert "memory-bound" in plan
    assert "All three gate specs pass cleanly under" not in plan
    assert "already MaxRound=12 and the evidence is recorded" not in plan


def test_phase_1255_frontier_docs_are_updated_without_publication_claim():
    status = read_repo("docs/phases/STATUS.md")
    index = read_repo("docs/PLANNING_INDEX.md")
    roadmap = read_repo("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")

    required = [
        "Phase 1255",
        "tla_refinement_notes_pre_rc_closed_phase_1255",
        "allowlist_export_procedure_defined_phase_1255",
        "public_repository_publication_not_authorized_phase_1255",
        "phase_1255_tla_allowlist_export_complete",
    ]
    for token in required:
        assert token in status
        assert token in index

    assert "Phase 1256" in status
    assert "SENSITIVE" in status
    assert "public_repository_publication_not_authorized_phase_1255" in roadmap
    assert "tla_refinement_notes_pre_rc_closed_phase_1255" in roadmap
