from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

HANDOFF = "docs/specs/ilc_window_1317_1329_handoff_1329_v0.1.md"
PROMPT = "docs/antigravity_tasks/antigravity_prompt__phase_1329_g8_window_1317_1329_closure_gate.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
FORWARD_PLAN = "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
CCSS_PLAN = "docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md"
WALKTHROUGH = "docs/phases/phase_1329_window_1317_1329_closure_gate_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1317_1329_closed_phase_1329",
    "window_1317_1329_closure_gate_verdict=pass_or_blocked_with_carry_forward",
    "phase_1329_window_1317_1329_closure_complete",
    "window_1330_plus_sequence_lock_required_before_next_phase_assignment",
    "release_dry_run_ccss_atlas_g_blockers_classified_phase_1329",
    "public_rc_remains_blocked_after_phase_1329",
)

PHASE_EVIDENCE = (
    "ilc_phase_1317_1329_sequence_lock_v0.1.md",
    "ilc_antigravity_context_capsule_v5.54.md",
    "ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.md",
    "ilc_release_artifact_manifest_instance_rehearsal_1320_v0.1.md",
    "ilc_release_key_envelope_procedure_rehearsal_1321_v0.1.md",
    "ilc_three_machine_seven_agent_private_deployment_rehearsal_1322_v0.1.md",
    "ilc_phase_1322_fix1_vps_git_workflow_restore_v0.1.md",
    "ilc_openclaw_nemoclaw_claimable_profile_full_dry_run_1323_v0.1.md",
    "ilc_phase_1323_fix2_openclaw_vps_install_skill_discovery_v0.1.md",
    "ilc_layered_license_posture_1323_fix3_v0.1.md",
    "ilc_ccss_001_private_gated_shard_sidecar_contract_1324_v0.1.md",
    "ilc_phase_1324_fix2_sidecar_harness_cross_module_hardening_v0.1.md",
    "ilc_ccss_002_capability_membership_grant_revocation_boundary_1325_v0.1.md",
    "ilc_phase_1325_fix1_ccss_002_access_audit_hardening_v0.1.md",
    "ilc_phase_1325_fix2_ccss_002_branch_and_integer_hardening_v0.1.md",
    "ilc_ccss_003_sealed_sender_local_delivery_boundary_1326_v0.1.md",
    "ilc_ccss_004_gossip_jitter_cover_policy_tests_1327_v0.1.md",
    "ilc_ccss_005_private_openclaw_nemoclaw_droplet_dry_run_1328_v0.1.md",
)

LEDGER_NAMES = (
    "release_dry_run_ledger",
    "private_deployment_ledger",
    "ccss_ledger",
    "atlas_g_ledger",
    "economics_ledger",
    "publication_ledger",
)

BLOCKER_PHRASES = (
    "source allowlist export execution",
    "clean materialized public tree production",
    "release artifact production",
    "release-key generation",
    "release envelope production",
    "public claimability/API",
    "public P2P",
    "public sidecar/projection serving",
    "public confidential coordination serving",
    "ATLAS-G-007",
    "ATLAS-G-010",
    "wallet-facing",
    "ECU minting",
    "ILC settlement",
    "CDL-069 commitment",
    "Genesis-rooted agent birth attestation",
    "counsel review",
)

NON_AUTHORIZATION_PHRASES = (
    "public RC claim",
    "source allowlist export execution",
    "source publication",
    "public repository publication",
    "public package publication",
    "release artifact production",
    "release-key generation",
    "release envelope production",
    "release signing material",
    "OpenClaw skill publication",
    "ClawHub listing",
    "public installability claim",
    "public claimability activation",
    "public verifier service",
    "public claim endpoint",
    "non-loopback bind",
    "public P2P",
    "public fetch serving",
    "public sidecar/projection serving",
    "public confidential messaging",
    "public confidential coordination serving",
    "CDL-088 opening",
    "Genesis Atlas mutation",
    "ATLAS-G-007",
    "v0.2 signing",
    "identity artifact creation",
    "identity_seed_commitment",
    "dummy Agent Birth artifact",
    "wallet-facing withdrawal request",
    "ECU minting",
    "ILC settlement",
    "value-path activation",
)

GRAPH_DELTAS = (
    "graph_delta=support_only:docs/specs/ilc_window_1317_1329_handoff_1329_v0.1.md -> planning/frontier",
    "graph_delta=support_tests_added:tests/test_phase_1329_window_1317_1329_closure_gate.py -> validation",
    "graph_delta=support_only:docs/phases/phase_1329_window_1317_1329_closure_gate_walkthrough.md -> planning/frontier",
    "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
    "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.54.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md -> planning/frontier",
    "graph_delta=support_only:docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md -> graph-native-sidecars/confidential-coordination",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1329_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(HANDOFF)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1329_closes_window_and_requires_next_sequence_lock() -> None:
    for path in (HANDOFF, PLANNING, CAPSULE, ROADMAP, STATUS, WALKTHROUGH):
        text = read(path)
        assert "Window 1317-1329 is CLOSED / PASS with carry-forward through Phase 1329" in text
        assert "window_1330_plus_sequence_lock_required_before_next_phase_assignment" in text


def test_phase_1329_handoff_classifies_all_phase_evidence() -> None:
    text = read(HANDOFF)

    for phase in range(1317, 1329):
        assert f"| {phase} |" in text

    for evidence in PHASE_EVIDENCE:
        assert evidence in text

    assert "| 1326 Fix1 | closed |" in text
    assert "9d8f665e phase 1326 fix1 harden sealed sender ref collection" in text


def test_phase_1329_ledgers_and_blockers_are_explicit() -> None:
    handoff = read(HANDOFF)
    walkthrough = read(WALKTHROUGH)

    for ledger in LEDGER_NAMES:
        assert ledger in handoff
        assert ledger in walkthrough

    for text in (handoff, walkthrough, read(PLANNING), read(CAPSULE), read(ROADMAP)):
        for phrase in BLOCKER_PHRASES:
            assert phrase in text

    for classification in ("closed", "open", "carried_forward", "blocked_by_authority"):
        assert classification in handoff


def test_phase_1329_preserves_ccss_atlas_split_and_public_serving_block() -> None:
    for path in (HANDOFF, FORWARD_PLAN, CCSS_PLAN, WALKTHROUGH):
        text = read(path)
        assert "CCSS is complete enough as private/local evidence" in text
        assert "not a first-RC blocker by default" in text
        assert "ATLAS-G-007 through ATLAS-G-010" in text
        assert "public confidential coordination serving" in text


def test_phase_1329_records_identity_and_license_carry_forward() -> None:
    text = read(HANDOFF) + read(CAPSULE) + read(ROADMAP) + read(PLANNING)

    assert 'identity_seed_commitment = sha384("ilc-seed-commit-v1:" || identity_seed)' in text
    assert "sha384(identity_seed)" in text
    assert "Genesis-rooted agent birth attestation" in text
    assert "Layered license posture is implemented provisionally" in text
    assert "counsel review" in text


def test_phase_1329_records_no_activation_boundary() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS):
        compact = " ".join(read(path).split())
        for phrase in NON_AUTHORIZATION_PHRASES:
            assert phrase in compact


def test_phase_1329_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    handoff = read(HANDOFF)

    assert "window_1317_1329_closed_phase_1329" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL mutation" in handoff
    assert "CDL-088 opening" in handoff


def test_phase_1329_graph_delta_is_recorded() -> None:
    for text in (read(HANDOFF), read(WALKTHROUGH), read(STATUS)):
        for graph_delta in GRAPH_DELTAS:
            assert graph_delta in text
