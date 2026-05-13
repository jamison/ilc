from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1317_g8_window_1317_1329_sequence_lock.md",
    "antigravity_prompt__phase_1318_g8_context_capsule_v5_54_frontier_refresh.md",
    "antigravity_prompt__phase_1319_g8_deterministic_source_allowlist_export_rehearsal.md",
    "antigravity_prompt__phase_1320_g8_release_artifact_manifest_instance_rehearsal.md",
    "antigravity_prompt__phase_1321_g8_release_key_envelope_procedure_rehearsal.md",
    "antigravity_prompt__phase_1322_g8_three_machine_seven_agent_private_deployment_rehearsal.md",
    "antigravity_prompt__phase_1323_g8_openclaw_nemoclaw_claimable_profile_full_dry_run.md",
    "antigravity_prompt__phase_1324_g8_ccss_001_private_gated_shard_sidecar_contract.md",
    "antigravity_prompt__phase_1325_g8_ccss_002_capability_membership_grant_revocation_boundary.md",
    "antigravity_prompt__phase_1326_g8_ccss_003_sealed_sender_local_delivery_boundary.md",
    "antigravity_prompt__phase_1327_g8_ccss_004_gossip_jitter_cover_policy_tests.md",
    "antigravity_prompt__phase_1328_g8_ccss_005_private_openclaw_nemoclaw_droplet_dry_run.md",
    "antigravity_prompt__phase_1329_g8_window_1317_1329_closure_gate.md",
)

SENSITIVE_PROMPTS = tuple(name for name in PHASE_PROMPTS if "phase_1318" not in name)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

PHASE_SPECIFIC_HARDENING_PHRASES = {
    "antigravity_prompt__phase_1317_g8_window_1317_1329_sequence_lock.md": (
        "phase-by-phase authority table",
        "stop-condition table",
        "CCSS phases 1324-1328 are not a substitute for ATLAS-G-007 through ATLAS-G-010",
        "Sequence-lock artifact exists and names Phase 1317 as the only executed phase.",
    ),
    "antigravity_prompt__phase_1318_g8_context_capsule_v5_54_frontier_refresh.md": (
        "compact but explicit delta from v5.53",
        "blocker table for source materialization",
        "Phase 1319 is next after Phase 1318, but it remains sensitive",
        "Capsule v5.54 exists and supersedes v5.53 only after Phase 1317 is confirmed.",
    ),
    "antigravity_prompt__phase_1319_g8_deterministic_source_allowlist_export_rehearsal.md": (
        "stable relative POSIX paths",
        "symlink escapes",
        "Marker scanning must operate on exported file bytes",
        "re-run and produce byte-identical manifest output",
        "`candidate_roots`",
        "`dependency_scan`",
        "Manifest records included files, excluded files, hashes, scanners, limitations, and non-claims.",
    ),
    "antigravity_prompt__phase_1320_g8_release_artifact_manifest_instance_rehearsal.md": (
        "source_tree_rehearsal_input",
        "dummy placeholder",
        "tarballs, wheels, release bundles, container images",
        "Release manifest rehearsal instance exists and is clearly dry-run-only.",
    ),
    "antigravity_prompt__phase_1321_g8_release_key_envelope_procedure_rehearsal.md": (
        "DRY_RUN_KEY_ID_DO_NOT_USE",
        "two-person or explicit-human-authority checkpoint",
        "HSM interface, cloud KMS API",
        "Procedure uses only fake identifiers and no generated cryptographic material.",
    ),
    "antigravity_prompt__phase_1322_g8_three_machine_seven_agent_private_deployment_rehearsal.md": (
        "executed_live_private_droplet",
        "inbound ports",
        "teardown instructions",
        "identity_artifact_creation_stop_guard_phase_1322",
        "stop and do not proceed until the CDL-069 commitment-formula mismatch is resolved",
        "Machine role: coordinator, verifier/projection, harness-adapter, or local-only substitute.",
        "Public exposure column is `none` for every executed role.",
    ),
    "antigravity_prompt__phase_1323_g8_openclaw_nemoclaw_claimable_profile_full_dry_run.md": (
        "profile requirements are satisfied by checked-in code",
        "wallet-provider signing request",
        "harness invocation through an adapter/sidecar boundary",
        "discover the current OpenClaw skill format",
        "Surface 1: CLI-first thin skill",
        "Surface 2: Python import bridge",
        "no seed/mnemonic/key material in LLM chat",
        "OpenClaw skill is already published, listed, installable",
        "Exact claimable profile name and package-profile version are recorded.",
        "Identity-seed UX is recorded as a public-bootstrap blocker",
    ),
    "antigravity_prompt__phase_1324_g8_ccss_001_private_gated_shard_sidecar_contract.md": (
        "shard identifiers as opaque references",
        "encrypted coordination-node envelope",
        "private-to-public promotion evidence shape",
        "`EncryptedCoordinationNodeEnvelope`",
        "`DisclosureDenial`",
        "`PrivateShardRef` is opaque and excludes AgentID, wallet ID, IP address, participant name, and harness identity.",
    ),
    "antigravity_prompt__phase_1325_g8_ccss_002_capability_membership_grant_revocation_boundary.md": (
        "capability reference, membership proof reference",
        "Unknown, expired, revoked, malformed, replayed, or cross-shard capabilities",
        "optional ZK interface must be a seam only",
        "`zk_deferred`",
        "Revocation wins over grant evidence.",
    ),
    "antigravity_prompt__phase_1326_g8_ccss_003_sealed_sender_local_delivery_boundary.md": (
        "envelope-routing seam",
        "allowed size classes",
        "variable-size leakage",
        "`blocked_public_transport`",
        "Allowed size classes and maximum payload bounds are explicit.",
    ),
    "antigravity_prompt__phase_1327_g8_ccss_004_gossip_jitter_cover_policy_tests.md": (
        "announce/pull as private/local coordination behavior only",
        "timing correlation, batch-size correlation",
        "claims stronger than the evidence demonstrates",
        "Harness identity leakage through adapter metadata.",
        "`not_tested_carry_forward`",
        "Runtime/security-sensitive paths do not use predictable PRNG for jitter.",
    ),
    "antigravity_prompt__phase_1328_g8_ccss_005_private_openclaw_nemoclaw_droplet_dry_run.md": (
        "real droplets, local loopback, or was blocked by unavailable infrastructure",
        "inbound firewall posture",
        "sidecar versions, profile names",
        "`harness_adapter_calls`",
        "`confidential_coordination_checks`",
        "Report declares one execution mode: real private droplets, local loopback, private overlay simulation, or blocked.",
    ),
    "antigravity_prompt__phase_1329_g8_window_1317_1329_closure_gate.md": (
        "phase-by-phase closure table",
        "release dry-run blockers, source materialization blockers, CCSS blockers",
        "artifact accidentally claims public RC",
        "`release_dry_run_ledger`",
        "`blocked_by_authority`",
        "Every Phase 1317-1328 walkthrough and STATUS entry is direct-read and classified.",
    ),
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1317_1329_guidance_is_planning_only_and_routes_all_phases() -> None:
    text = _text(GUIDANCE)

    for token in (
        "window_1317_1329_candidate_phase_grouping_drafted_after_phase_1316",
        "window_1317_1329_not_open_until_sequence_lock",
        "phase_1317_window_1317_1329_sequence_lock_required",
        "window_1317_1329_release_dry_run_public_rc_blocked",
        "deterministic_source_allowlist_export_rehearsal_required_phase_1319",
        "openclaw_skill_format_discovery_required_phase_1323",
        "identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323",
        "openclaw_skill_not_published_or_installable_phase_1323",
        "genesis_rooted_agent_birth_attestation_blocker_phase_1323",
        "ccss_tail_routed_phase_1324_1328_without_atlas_g_compression",
        "atlas_g_tail_carried_forward_not_hidden_inside_ccss_phase_1317_1329",
        "window_1317_1329_prompt_drafts_registered",
    ):
        assert token in text

    for phase in range(1317, 1330):
        assert f"| {phase} |" in text

    for phrase in (
        "does not open",
        "Phase 1319 is the first materialization rehearsal",
        "zero exported files contain `PUBLIC_RC_EXCLUDE`",
        "OpenClaw and NemoClaw remain harness/deployment targets",
        "CLI-first OpenClaw skill surface",
        "non-custodial",
        "ATLAS-G-007 through ATLAS-G-010 remain required before signing",
        "public confidential coordination serving",
    ):
        assert phrase in text


def test_window_1317_1329_guidance_matches_forward_plan_assignments() -> None:
    guidance = _text(GUIDANCE)
    forward_plan = _text(FORWARD_PLAN)

    for phrase in (
        "Deterministic source allowlist export rehearsal",
        "Release artifact manifest instance rehearsal",
        "Release key/envelope procedure rehearsal",
        "Three-machine/seven-agent private deployment rehearsal",
        "OpenClaw/NemoClaw claimable profile full dry run",
        "CCSS-001 private/gated shard sidecar contract",
        "CCSS-002 capability, membership, grant, revocation",
        "CCSS-003 sealed sender local delivery sidecar boundary",
        "CCSS-004 gossip announce/pull, jitter",
        "CCSS-005 private OpenClaw/NemoClaw confidential coordination droplet dry run",
    ):
        assert phrase in guidance
        assert phrase in forward_plan


def test_forward_plan_records_resolved_ccss_atlas_g_split() -> None:
    forward_plan = _text(FORWARD_PLAN)

    for phrase in (
        "Resolved by the Phase 1317 sequence lock",
        "ccss_tail_routed_without_atlas_g_compression_phase_1317",
        "atlas_g_tail_carried_forward_not_hidden_inside_ccss_phase_1317_1329",
        "Phases 1324-1328 are the current CCSS-001 through CCSS-005 private/local lane.",
        "They are not Atlas-G tail phases and must not execute ATLAS-G-007 through",
        "ATLAS-G-010 as hidden scope.",
        "ATLAS-G-010 v0.2 signing ceremony gate",
        "Phase 1340 explicit signing gate; no signing by default.",
        "openclaw_skill_format_discovery_required_phase_1323",
        "cli_first_skill_surface_recorded_phase_1323",
        "python_import_bridge_surface_recorded_phase_1323",
        "identity_seed_ux_public_bootstrap_blocker_phase_1323",
        "identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323",
        "openclaw_skill_not_published_or_installable_phase_1323",
        "genesis_rooted_agent_birth_attestation_blocker_phase_1323",
        "no seed/mnemonic/private-key disclosure to LLM chat",
    ):
        assert phrase in forward_plan

    assert (
        "If a future sequence lock chooses to prioritize Atlas-G tail before CCSS"
        not in forward_plan
    )


def test_window_1317_1329_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        assert validate(PROMPT_DIR / prompt_name) == []


def test_window_1317_1329_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text


def test_window_1317_1329_prompt_drafts_have_non_authorization_floor() -> None:
    required_phrases = (
        "Public RC claim or public launch claim",
        "Source export execution, source publication, package publication",
        "Release artifact production, real release keys, release envelopes, or signing",
        "Public claimability/API activation or public verifier service",
        "Public P2P, public fetch serving, public sidecar/projection serving",
        "Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088 opening",
        "Wallet-facing withdrawal, transfer, or spend request activation",
        "Public confidential messaging or public confidential coordination serving",
    )

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert text.count("## Non-authorization floor") == 1
        assert text.count("## Deliverables") == 1
        for phrase in required_phrases:
            assert phrase in text


def test_window_1317_1329_prompt_drafts_have_distinct_phase_specific_hardening() -> None:
    line_counts = []

    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## Phase-specific hardening requirements" in text
        assert "## Phase-specific acceptance checklist" in text
        for phrase in PHASE_SPECIFIC_HARDENING_PHRASES[prompt_name]:
            assert phrase in text
        line_counts.append(len(text.splitlines()))

    assert max(line_counts) - min(line_counts) >= 40


def test_window_1317_1329_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1317_1329_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1317_1329_prompts_reference_guidance_and_current_handoff() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "ilc_window_1317_1329_candidate_phase_grouping_v0.1.md" in text
        assert "ilc_window_1303_1316_handoff_1316_v0.1.md" in text
        assert "ilc_antigravity_context_capsule_v5.53.md" in text


def test_phase_1319_prompt_preserves_materialization_rehearsal_boundaries() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1319_g8_deterministic_source_allowlist_export_rehearsal.md"
    )

    for phrase in (
        "zero exported files contain `PUBLIC_RC_EXCLUDE`",
        "zero exported files import or depend on stripped helper modules",
        "legacy-untagged review results",
        "source_export_rehearsal_no_publication_phase_1319",
        "not public source export",
        "must fail closed",
    ):
        assert phrase in text


def test_phase_1324_1328_prompts_preserve_ccss_private_local_boundary() -> None:
    for prompt_name in PHASE_PROMPTS[7:12]:
        text = _text(PROMPT_DIR / prompt_name)
        assert "Confidential Coordination Sidecar Suite" in text
        assert "private/local" in text
        assert "no public P2P" in text or "public P2P" in text
        assert "public confidential coordination serving" in text


def test_planning_index_references_window_1317_1329_sequence_lock_and_guidance() -> None:
    text = _text(PLANNING_INDEX)

    assert "ilc_phase_1317_1329_sequence_lock_v0.1.md" in text
    assert "ilc_window_1317_1329_candidate_phase_grouping_v0.1.md" in text
    assert "window_1317_1329_candidate_phase_grouping_drafted_after_phase_1316" in text
    assert "window_1317_1329_not_open_until_sequence_lock" in text
    assert "phase_1317_window_1317_1329_sequence_lock_required" in text
    assert "window_1317_1329_candidate_phase_grouping_consumed_by_phase_1317_sequence_lock" in text
    assert "window_1317_1329_sequence_lock_committed" in text
    assert "phase_1318_context_capsule_v5_54_refresh_next" in text
    assert "context_capsule_v5_54_frontier_refresh_phase_1318.v0.1" in text
    assert "deterministic_source_allowlist_export_rehearsal_phase_1319.v0.1" in text
    assert "phase_1320_release_artifact_manifest_instance_rehearsal_next" in text
    assert "release_artifact_manifest_instance_rehearsal_phase_1320.v0.1" in text
    assert "phase_1321_release_key_envelope_rehearsal_next" in text
    assert "release_key_envelope_procedure_rehearsal_phase_1321.v0.1" in text
    assert "release_key_generation_not_authorized_phase_1321" in text
    assert "signing_procedure_rehearsed_no_real_signing_phase_1321" in text
    assert "phase_1322_private_deployment_rehearsal_next" in text
    assert "three_machine_seven_agent_private_deployment_rehearsal_phase_1322.v0.1" in text
    assert (
        "essential_graph_native_sidecar_suite_private_deployment_rehearsed_phase_1322"
        in text
    )
    assert "private_wiring_only_no_public_serving_phase_1322" in text
    assert "identity_artifact_creation_stop_guard_phase_1322" in text
    assert "phase_1323_openclaw_nemoclaw_claimable_profile_dry_run_next" in text
    assert "openclaw_skill_format_discovery_required_phase_1323" in text
    assert "cli_first_skill_surface_recorded_phase_1323" in text
    assert "python_import_bridge_surface_recorded_phase_1323" in text
    assert "identity_seed_ux_public_bootstrap_blocker_phase_1323" in text
    assert "identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323" in text
    assert "openclaw_skill_not_published_or_installable_phase_1323" in text
    assert "genesis_rooted_agent_birth_attestation_blocker_phase_1323" in text
    assert "phase_1322_fix1_restore_vps_git_workflow.v0.1" in text
    assert "remote_rsync_tree_provenance_blocker_resolved_phase_1322_fix1" in text
    assert "sync_repo_git_workflow_restored_phase_1322_fix1" in text
    assert "phase_1323_remote_sync_precondition_cleared_phase_1322_fix1" in text
    assert "openclaw_nemoclaw_claimable_profile_full_dry_run_phase_1323.v0.1" in text
    assert "claimable_profile_dry_run_public_claimability_still_gated_phase_1323" in text
    assert "graph_native_sidecar_suite_profile_integrity_rehearsed_phase_1323" in text
    assert "phase_1323_fix2_openclaw_vps_install_skill_discovery.v0.1" in text
    assert "openclaw_cli_installed_on_private_vps_phase_1323_fix2" in text
    assert "local_ilc_skill_draft_discovered_by_openclaw_phase_1323_fix2" in text
    assert "openclaw_gateway_not_started_phase_1323_fix2" in text
    assert "clawhub_publication_not_authorized_phase_1323_fix2" in text
    assert "ilc_runtime_not_modified_phase_1323_fix2" in text
    assert "public_rc_remains_blocked_after_phase_1323_fix2" in text
    assert "phase_1324_ccss_private_gated_shard_contract_next_after_fix2" in text
    assert "phase_1324_ccss_private_gated_shard_contract_next" in text
    assert "public_rc_remains_blocked_after_phase_1323" in text
    assert "ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1" in text
    assert "encrypted_coordination_node_envelope_contract_recorded_phase_1324" in text
    assert "shard_header_projection_contract_recorded_phase_1324" in text
    assert "private_to_public_promotion_evidence_shape_recorded_phase_1324" in text
    assert "ccss_public_serving_not_enabled_phase_1324" in text
    assert "phase_1325_ccss_capability_membership_boundary_next" in text
    assert "public_rc_remains_blocked_after_phase_1324" in text
    assert "ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1" in text
    assert "private_shard_access_control_boundary_recorded_phase_1325" in text
    assert "membership_plaintext_disclosure_forbidden_phase_1325" in text
    assert "optional_zk_interface_boundary_recorded_phase_1325" in text
    assert "phase_1326_ccss_sealed_sender_boundary_next" in text
    assert "public_rc_remains_blocked_after_phase_1325" in text
    assert "Window 1317-1329 is OPEN through Phase 1325" in text
