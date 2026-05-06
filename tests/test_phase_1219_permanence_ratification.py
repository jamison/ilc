from pathlib import Path


MATERIALS = Path("docs/specs/ilc_truth_primitive_permanence_ceremony_materials_1219_v0.1.md")
EVENT = Path("docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1219_permanence_ratification_ceremony_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def _materials() -> str:
    return MATERIALS.read_text(encoding="utf-8")


def _event() -> str:
    return EVENT.read_text(encoding="utf-8")


def test_ceremony_materials_file_exists() -> None:
    assert MATERIALS.exists()


def test_ceremony_materials_contains_evidence_references() -> None:
    content = _materials()
    required = [
        "docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md",
        "CDL-073",
        "cdl_074_truth_primitive_runtime_ratified.v0.1",
        "cdl_075_truth_primitive_graph_persistence.v0.1",
        "cdl_052_ratified_466.v0.1",
        'TRUTH_PRIMITIVE_RUNTIME_VERSION = "truth_primitive_submission_runtime_868.v0.1"',
        'TRUTH_PRIMITIVE_GRAPH_STORE_VERSION = "truth_primitive_graph_store_880.v0.1"',
        "docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json",
        "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c",
        "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56",
    ]
    for item in required:
        assert item in content


def test_ceremony_materials_contains_primitive_set_and_exclusions() -> None:
    content = _materials()
    for primitive in [
        "assert.truth",
        "validate.claim",
        "contradict.assert",
        "refute.claim",
        "revise.assert",
        "link.claim",
        "commit.epoch",
    ]:
        assert primitive in content
    assert "`star.map` is explicitly excluded" in content
    assert "commit_epoch_agent_submission_rejected" in content
    assert "production emission runtime not ratified by this ceremony" in content
    assert "final production `commit.epoch` emission runtime" in content
    assert "commit_epoch_causal_frontier_mapping_spec_required" in content


def test_ceremony_materials_records_stage_b_boundary() -> None:
    content = _materials()
    assert "truth_primitive_permanence_ceremony_materials_committed_phase_1219" in content
    assert "truth_primitive_permanence_genesis_attestation_pending_phase_1219" in content
    assert "GO Phase 1219 ratification commit" in content
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in content
    assert "no wall-clock protocol time" in content
    assert "no\nfloat economics" in content


def test_ceremony_materials_has_attestation_and_dissent_fields() -> None:
    content = _materials()
    assert "Genesis authority identifier" in content
    assert "Optional Witness Attestations" in content
    assert "No dissent recorded in the repository materials as of Phase 1219 Stage A." in content


def test_ratification_event_records_genesis_attestation() -> None:
    assert EVENT.exists()
    content = _event()
    assert "GO Phase 1219 ratification commit" in content
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in content
    assert "docs/specs/ilc_truth_primitive_permanence_ceremony_materials_1219_v0.1.md" in content
    assert "Genesis Agent <ilcops@proton.me>" in content
    assert "Commit-anchored repository attestation" in content


def test_ratification_event_records_boundaries_and_no_dissent() -> None:
    content = _event()
    assert "`star.map` is excluded" in content
    assert "commit_epoch_agent_submission_rejected" in content
    assert "This event does not ratify a final production `commit.epoch` emission runtime." in content
    assert "No dissent recorded." in content
    assert "[]" in content
    assert "truth_primitive_permanence_ratification_blocked_phase_1219" not in content


def test_ratification_event_carries_commit_epoch_mapping_obligation() -> None:
    content = _event()
    assert "commit_epoch_causal_frontier_mapping_spec_required" in content
    assert "CDL-051 epoch-state/quorum records plus Genesis epoch-zero bootstrap" in content
    assert "no wall-clock protocol time" in content
    assert "no\nfloat economics" in content
    assert "causal-frontier semantics" in content


def test_ratification_event_contains_non_bypass_and_non_events() -> None:
    content = _event()
    assert "No public RC claim, public launch claim, release announcement" in content
    assert "This ratification event completes the truth-primitive permanence path only." in content
    for non_event in [
        "mutate the CDL register",
        "mutate runtime behavior",
        "sign Genesis Atlas v0.2",
        "authorize public repository publication",
        "authorize public RC or public launch claims",
    ]:
        assert non_event in content


def test_walkthrough_status_records_stage_b_complete() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "truth_primitive_permanence_ceremony_materials_committed_phase_1219" in content
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in content
    assert "commit_epoch_causal_frontier_mapping_spec_required" in content


def test_planning_index_and_status_record_stage_b_frontier() -> None:
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "Phase 1219 Stage B complete" in planning
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in planning
    assert "Phase 1219 Stage B" in status
    assert "truth_primitive_permanence_genesis_attested_phase_1219" in status
