from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
ARCH_GATE = ROOT / "docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md"
SIDECAR_ARCH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"
CCSS_ARCH = ROOT / "docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md"
EXPORT_PROCEDURE = ROOT / "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md"
RELEASE_MANIFEST = ROOT / "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md"
RUNWAY = ROOT / "docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md"
GUIDANCE = ROOT / "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
PHASE_1299_PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1299_g8_release_allowlist_artifact_genesis_readiness_preflight.md"
)
PHASE_1302_PROMPT = (
    ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1302_g8_window_1289_1302_closure_gate.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_forward_packaging_plan_records_recovered_windows_and_non_authority() -> None:
    text = read(PLAN)

    for token in (
        "forward_phase_windows_1303_1342_packaging_and_signing_plan_recorded",
        "public_rc_exclude_helper_stripping_routed_to_phase_1308_1319_1333",
        "source_allowlist_export_materialization_must_fail_on_public_rc_exclude_markers",
        "public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution",
        "graph_native_sidecar_creation_routed_to_forward_windows_1303_1342",
        "essential_openclaw_rc_sidecars_truth_projection_claimability_bridge",
        "openclaw_nemoclaw_are_hosts_not_protocol_substrates",
        "sidecar_suite_public_serving_remains_blocked_until_explicit_authority",
        "confidential_coordination_sidecar_suite_forward_plan_recorded",
        "confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329",
        "confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only",
        "confidential_coordination_not_public_rc_blocker_without_explicit_selection",
    ):
        assert token in text

    for phase in range(1303, 1343):
        assert f"| {phase} |" in text

    for phrase in (
        "does not open",
        "execute source export",
        "publish a repository or package",
        "produce release artifacts",
        "sign v0.2",
        "authorize wallet/ECU/ILC economics",
    ):
        assert phrase in text


def test_forward_packaging_plan_assigns_helper_stripping_to_packaging_phases() -> None:
    text = read(PLAN)

    assert (
        "| 1308 | Helper pruning/replacement plan with `PUBLIC_RC_EXCLUDE` enforcement "
        "and truth-primitive sidecar boundary |"
    ) in text
    assert "| 1319 | Deterministic source allowlist export rehearsal |" in text
    assert "| 1333 | Source allowlist export execution gate |" in text

    for phrase in (
        "do not flip fail-closed helper flags from `False` to `True`",
        "replace_before_export",
        "strip_from_export",
        "defer_public_rc",
        "zero exported files contain `PUBLIC_RC_EXCLUDE`",
        "zero exported files import or depend on stripped helper modules",
        "reject the candidate export",
        "helper flags are flipped from false to true",
        "Source export must precede release artifact production",
    ):
        assert phrase in text


def test_forward_packaging_plan_keeps_phase_1313_readiness_only() -> None:
    text = read(PLAN)

    assert "Public fetch/P2P readiness candidate, default off with no activation" in text
    assert "Public fetch/P2P readiness without activation in this implementation-hardening window" in text
    assert "Public fetch/P2P activation candidate, default off unless authorized" not in text
    assert "default off unless authorized" not in text


def test_public_rc_packaging_architecture_gate_records_best_plan() -> None:
    text = read(ARCH_GATE)

    for phrase in (
        "public_rc_packaging_architecture_gate_recorded",
        "public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution",
        "public_rc_package_export_must_be_public_tree_clean_not_flag_flip",
        "release_artifact_packet_must_reference_clean_export_gate",
        "public_rc_exclude_absence_is_not_allowlist_clearance",
        "legacy_untagged_docs_default_review_required_before_public_export",
        "graph_native_sidecar_suite_must_package_as_clean_materialized_components",
        "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md",
        "must be produced from a clean materialized public source tree",
        "flipping internal fail-closed helper flags from false to true",
        "Absence of `PUBLIC_RC_EXCLUDE` is not allowlist clearance",
        "Phase 1308 performs helper pruning/replacement planning",
        "Phase 1319 performs deterministic source allowlist export rehearsal",
        "Phase 1333 performs the source allowlist export execution gate",
        "Release artifact production, release-key generation, release envelopes",
    ):
        assert phrase in text


def test_graph_native_sidecar_suite_architecture_records_harness_agnostic_plan() -> None:
    text = read(SIDECAR_ARCH)

    for phrase in (
        "ilc_graph_native_sidecar_suite_architecture_recorded",
        "ilc_graph_native_sidecar_suite_not_conventional_api_layer",
        "openclaw_nemoclaw_are_hosts_not_protocol_substrates",
        "essential_openclaw_rc_sidecars_truth_projection_claimability_bridge",
        "graph_native_sidecar_creation_routed_to_forward_windows_1303_1342",
        "sidecar_suite_public_serving_remains_blocked_until_explicit_authority",
        "Sidecar registry and manifest",
        "Truth primitive submission sidecar",
        "Local graph and memory projection sidecar",
        "Claimability and receipt verifier sidecar",
        "Confidential coordination profile",
        "OpenClaw/NemoClaw bridge sidecar",
        "private DigitalOcean OpenClaw droplet testing",
        "hosts or operators of the suite",
        "They are not protocol substrates",
        "Confidential Coordination Sidecar Suite",
        "1324-1329 implementation/dry-run lane",
        "sidecar public serving",
        "public confidential messaging",
        "public claimability API activation",
        "OpenClaw/NemoClaw as protocol substrate",
    ):
        assert phrase in text


def test_confidential_coordination_sidecar_suite_forward_plan_records_phase_routing() -> None:
    text = read(CCSS_ARCH)

    for token in (
        "confidential_coordination_sidecar_suite_forward_plan_recorded",
        "confidential_coordination_sidecar_suite_graph_native_not_signal_clone",
        "confidential_coordination_sidecar_suite_not_public_rc_blocker_by_default",
        "confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329",
        "confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only",
        "confidential_coordination_public_claim_requires_phase_1337_1341_authority",
    ):
        assert token in text

    for phrase in (
        "| 1297 | Completed related prerequisite: public-safe projection schema.",
        "| 1298 | Completed related prerequisite: bind/listener/peer-discovery authority preflight.",
        "| 1307 | Complete. Added `confidential_coordination_local_preview`",
        "| 1311 | Complete. Added local graph/memory projection records for private/gated shard headers",
        "| 1312 | Complete. Added privacy/filtering tests for confidential-coordination projections",
        "| 1324 | CCSS-001: implement or formally specify the private/gated shard sidecar contract",
        "| 1325 | CCSS-002: implement or formally specify capability, membership, grant, revocation",
        "| 1326 | CCSS-003: implement or formally specify sealed sender local delivery sidecar boundaries",
        "| 1327 | CCSS-004: implement or formally specify gossip announce/pull, jitter",
        "| 1328 | CCSS-005: run a private OpenClaw/NemoClaw or equivalent DigitalOcean droplet dry run",
        "| 1329 | Closure gate",
        "| 1337 | Public-path gate must explicitly activate or exclude",
        "| 1341 | Public RC publication/claim must not imply",
        "Anonymity guarantee is not a default claim",
        "OpenClaw, NemoClaw, and DigitalOcean droplets are harness/deployment targets",
        "public confidential messaging",
    ):
        assert phrase in text


def test_public_source_export_procedure_requires_marker_and_import_scans() -> None:
    text = read(EXPORT_PROCEDURE)

    for phrase in (
        "source_allowlist_export_materialization_must_fail_on_public_rc_exclude_markers",
        "PUBLIC_RC_EXCLUDE Helper Stripping Gate",
        "must not simply flip internal helper authorization flags from false to true",
        "contains `PUBLIC_RC_EXCLUDE`",
        "imports an excluded helper",
        "marker-scan and import-scan evidence",
        "Scan the materialized tree for `PUBLIC_RC_EXCLUDE` markers",
        "Scan exported imports for dependencies on excluded helper paths",
        "no import dependency on excluded helpers",
        "public_rc_package_export_must_be_public_tree_clean_not_flag_flip",
        "public_rc_exclude_absence_is_not_allowlist_clearance",
        "legacy_untagged_docs_default_review_required_before_public_export",
        "legacy_untagged_review",
        "`PUBLIC_RC_EXCLUDE` is a deny marker, not an allowlist signal",
        "Untagged legacy docs/research/planning files",
        "legacy-untagged scan",
        "ilc_public_rc_packaging_architecture_gate_v0.1.md",
    ):
        assert phrase in text


def test_release_manifest_and_runway_reference_packaging_architecture_gate() -> None:
    manifest = read(RELEASE_MANIFEST)
    runway = read(RUNWAY)

    for text in (manifest, runway):
        assert "ilc_public_rc_packaging_architecture_gate_v0.1.md" in text
        assert "public_rc_package_export_must_be_public_tree_clean_not_flag_flip" in text

    assert "ilc_graph_native_sidecar_suite_architecture_v0.1.md" in runway
    assert "ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md" in runway
    assert "essential_openclaw_rc_sidecars_truth_projection_claimability_bridge" in runway
    assert "openclaw_nemoclaw_are_hosts_not_protocol_substrates" in runway
    assert "sidecar_suite_public_serving_remains_blocked_until_explicit_authority" in runway
    assert "confidential_coordination_sidecar_suite_forward_plan_recorded" in runway
    assert "confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329" in runway
    assert "release_artifact_packet_must_reference_clean_export_gate" in manifest
    assert "legacy untagged-file review state" in manifest
    assert "legacy_untagged_docs_default_review_required_before_public_export" in manifest
    assert "deterministic dry-run materialization second" in runway
    assert "PUBLIC_RC_EXCLUDE` is a deny marker only" in runway


def test_current_window_prompts_carry_stripping_to_later_packaging_gates() -> None:
    prompt_1299 = read(PHASE_1299_PROMPT)
    prompt_1302 = read(PHASE_1302_PROMPT)
    guidance = read(GUIDANCE)

    assert (
        "public_rc_exclude_helper_stripping_deferred_to_package_materialization_after_phase_1299"
        in prompt_1299
    )
    assert "do not execute stripping in Phase" in prompt_1299
    assert "public_rc_exclude_helper_stripping_carried_forward_to_window_1303_plus" in prompt_1302
    assert "`PUBLIC_RC_EXCLUDE` helper replacement or stripping" in guidance


def test_roadmap_and_planning_index_reference_forward_packaging_plan() -> None:
    roadmap = read(ROADMAP)
    planning_index = read(PLANNING_INDEX)

    for text in (roadmap,):
        assert (
            "ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
            in text
            or "ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
            in text
        )
        assert "ilc_public_rc_packaging_architecture_gate_v0.1.md" in text
        assert "public_rc_exclude_helper_stripping_routed_to_phase_1308_1319_1333" in text
        assert "public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution" in text
        assert "legacy_untagged_docs_default_review_required_before_public_export" in text
        assert "ilc_graph_native_sidecar_suite_architecture_v0.1.md" in text
        assert "ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md" in text
        assert "ilc_graph_native_sidecar_suite_architecture_recorded" in text
        assert "graph_native_sidecar_creation_routed_to_forward_windows_1303_1342" in text
        assert "essential_openclaw_rc_sidecars_truth_projection_claimability_bridge" in text
        assert "openclaw_nemoclaw_are_hosts_not_protocol_substrates" in text
        assert "confidential_coordination_sidecar_suite_forward_plan_recorded" in text
        assert "confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329" in text
        assert "confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only" in text

    assert (
        "ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
        in planning_index
        or "ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
        in planning_index
    )

    assert "Phase 1308 is the implementation-hardening planning point" in roadmap
    assert "Phase 1307 through Phase 1314 are the implementation-hardening planning points" in roadmap
    assert "Phase 1324 through Phase 1328 are now the preferred planning lane" in roadmap
    assert "Confidential Coordination Sidecar Suite" in roadmap
    assert "Confidential coordination is not a first-public-RC blocker by default" in roadmap
    assert "successful private" in roadmap
    assert "DigitalOcean/OpenClaw tests do not authorize public sidecar serving" in roadmap
    assert "Phase 1319 is the deterministic source allowlist export rehearsal" in roadmap
    assert "Phase 1333 is the final source allowlist export execution gate" in roadmap
    assert "Release artifact packets must reference the clean export evidence" in roadmap
    assert "`PUBLIC_RC_EXCLUDE` is a deny marker, not allowlist clearance" in roadmap
