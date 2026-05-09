from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path(
    "docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1279_release_manifest_allowlist_prepublication_preflight_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ALLOWLIST_PROCEDURE_PATH = Path(
    "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md"
)
ATLAS_G_006_PATH = Path("docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md")

REQUIRED_TOKENS = (
    "release_manifest_allowlist_publication_preflight_phase_1279.v0.1",
    "public_repository_publication_not_authorized_phase_1279",
    "release_artifact_production_not_authorized_phase_1279",
    "v0_2_signing_not_authorized_phase_1279",
)

BOUNDARY_TOKENS = (
    "source_allowlist_export_not_executed_phase_1279",
    "release_keys_not_generated_phase_1279",
    "release_envelope_not_produced_phase_1279",
    "genesis_atlas_mutation_not_authorized_phase_1279",
    "public_rc_remains_blocked_after_phase_1279",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl087_row() -> str:
    rows = [
        line
        for line in _read(CDL_REGISTER_PATH).splitlines()
        if line.startswith("| CDL-087 |")
    ]
    assert len(rows) == 1
    return rows[0]


def test_phase_1279_required_tokens_are_recorded_everywhere() -> None:
    texts = (
        _read(SPEC_PATH),
        _read(WALKTHROUGH_PATH),
        _read(STATUS_PATH),
        _read(PLANNING_INDEX_PATH),
        _read(ROADMAP_PATH),
        _read(SEQUENCE_LOCK_PATH),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text


def test_phase_1279_records_publication_and_release_non_authority() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        for token in BOUNDARY_TOKENS:
            assert token in text

        for forbidden_authority in (
            "public repository publication",
            "public package publication",
            "public release artifact production",
            "release-key generation",
            "release envelope production",
            "Genesis Atlas mutation",
            "v0.2 signing",
            "public RC claim",
            "CDL-088 opening",
        ):
            assert forbidden_authority in text


def test_phase_1279_binds_prior_manifest_allowlist_and_graph_evidence() -> None:
    spec = _read(SPEC_PATH)
    allowlist = _read(ALLOWLIST_PROCEDURE_PATH)
    atlas = _read(ATLAS_G_006_PATH)

    assert "release_artifact_manifest_schema_committed_phase_1213" in spec
    assert "distribution_channel_integrity_checklist_committed_phase_1213" in spec
    assert "allowlist_export_procedure_defined_phase_1255" in spec
    assert "atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1" in spec
    assert "cdl087_ratified_phase_1278_fix1" in spec

    assert "denylist overrides allowlist" in allowlist
    assert "public_repository_publication_not_authorized_phase_1255" in allowlist
    assert "public_release_artifact_not_authorized_phase_1271" in atlas
    assert "no_genesis_atlas_mutation_phase_1271" in atlas


def test_phase_1279_keeps_cdl087_ratified_without_new_cdl_mutation() -> None:
    row = _cdl087_row()
    spec = _read(SPEC_PATH)

    assert "| ratified |" in row
    assert "cdl087_ratified_phase_1278_fix1" in row
    assert "CDL mutation" in spec
    assert "CDL-088 opening" in spec
    assert "release_manifest_allowlist_publication_preflight_phase_1279.v0.1" not in row


def test_phase_1279_updates_frontier_and_next_phase() -> None:
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)
    status = _read(STATUS_PATH)
    sequence_lock = _read(SEQUENCE_LOCK_PATH)

    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in planning
    assert "window_1281_plus_sequence_lock_required_before_next_phase_assignment" in planning
    assert "Window frontier | Window 1273-1280 CLOSED / PASS through Phase 1280" in roadmap
    assert "## 25. Phase 1279 Release Manifest Allowlist Prepublication Addendum" in roadmap
    assert "## Phase 1279" in status
    assert "Phase 1280 - Window 1273-1280 coherence, blocker classification, and closure gate" in status
    assert "## 7. Phase 1279 Prepublication Addendum" in sequence_lock


def test_phase_1279_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md -> release/publication",
        "graph_delta=support_tests_added:tests/test_phase_1279_release_manifest_allowlist_prepublication_preflight.py -> validation",
        "graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier",
        "graph_delta=support_only:docs/phases/phase_1279_release_manifest_allowlist_prepublication_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status
