from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1303_g8_window_1303_1316_sequence_lock.md",
    "antigravity_prompt__phase_1304_g8_context_capsule_v5_53_frontier_refresh.md",
    "antigravity_prompt__phase_1305_g8_offline_claimability_receipt_verifier_sidecar_library.md",
    "antigravity_prompt__phase_1306_g8_proof_binding_canonical_hash_negative_path_tests.md",
    "antigravity_prompt__phase_1307_g8_graph_native_sidecar_registry_manifest_profile_hardening.md",
    "antigravity_prompt__phase_1308_g8_public_rc_exclude_helper_pruning_replacement_plan.md",
    "antigravity_prompt__phase_1309_g8_transport_principal_admission_sidecar_lifecycle_hardening.md",
    "antigravity_prompt__phase_1310_g8_revocation_replay_admission_ban_tests.md",
    "antigravity_prompt__phase_1311_g8_local_graph_memory_projection_sidecar_public_safe_projection.md",
    "antigravity_prompt__phase_1312_g8_projection_privacy_field_filtering_tests.md",
    "antigravity_prompt__phase_1313_g8_public_fetch_p2p_activation_candidate_default_off.md",
    "antigravity_prompt__phase_1314_g8_wallet_withdrawal_transfer_spend_semantics_preflight.md",
    "antigravity_prompt__phase_1315_g8_ecu_minting_ilc_settlement_boundary_preflight.md",
    "antigravity_prompt__phase_1316_g8_window_1303_1316_closure_implementation_audit.md",
)

SENSITIVE_PROMPTS = tuple(name for name in PHASE_PROMPTS if "phase_1304" not in name)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_tokens(text: str) -> list[str]:
    marker = "## Required Tokens"
    assert marker in text
    after_marker = text.split(marker, maxsplit=1)[1]
    block = after_marker.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_window_1303_1316_guidance_is_planning_only_and_routes_all_phases() -> None:
    text = _text(GUIDANCE)

    for token in (
        "window_1303_1316_candidate_phase_grouping_drafted_after_phase_1302",
        "window_1303_1316_not_open_until_sequence_lock",
        "phase_1303_window_1303_1316_sequence_lock_required",
        "window_1303_1316_implementation_hardening_public_rc_blocked",
        "rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate",
        "graph_native_sidecar_essential_suite_routed_window_1303_1316",
        "public_rc_exclude_helper_stripping_planning_phase_1308",
        "confidential_coordination_local_preview_prereqs_routed_phase_1307_1311_1312",
    ):
        assert token in text

    for phase in range(1303, 1317):
        assert f"| {phase} |" in text

    for phrase in (
        "does not open",
        "does not activate public claimability",
        "Phase 1308 is the first explicit stripping-planning point",
        "Phase 1313 cannot become a real public P2P/fetch activation",
        "OpenClaw/NemoClaw remain hosts or consumers",
        "public confidential messaging",
    ):
        assert phrase in text


def test_window_1303_1316_guidance_matches_forward_plan_core_assignments() -> None:
    guidance = _text(GUIDANCE)
    forward_plan = _text(FORWARD_PLAN)

    for phrase in (
        "Offline/local claimability and receipt verifier sidecar/library",
        "Proof-binding, canonical hash, and negative-path tests",
        "Graph-native sidecar registry/manifest plus claimability package profile hardening",
        "Helper pruning/replacement plan with `PUBLIC_RC_EXCLUDE` enforcement",
        "TransportPrincipal admission sidecar lifecycle implementation hardening",
        "Projection privacy and field-filtering tests",
        "Public fetch/P2P readiness candidate, default off with no activation",
        "Wallet-facing withdrawal, transfer, and spend request semantics preflight",
        "ECU minting and ILC settlement boundary preflight",
    ):
        assert phrase in guidance
        assert phrase in forward_plan


def test_window_1303_1316_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        prompt_path = PROMPT_DIR / prompt_name
        assert validate(prompt_path) == []


def test_window_1303_1316_prompt_drafts_have_token_audit_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "## §0 — Canon checks and token audit" in text
        assert 'rg -n "<token>"' in text
        assert "MemPalace" in text
        assert "No ellipses in walkthrough" in text
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text


def test_window_1303_1316_prompt_drafts_have_single_non_authorization_floor() -> None:
    required_phrases = (
        "Public RC claim or public launch claim",
        "Source export, source publication, package publication, release artifact production",
        "Public claimability/API activation or public verifier service",
        "Public P2P, public fetch serving, public sidecar/projection serving",
        "Helper promotion, marker removal, or public export stripping",
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


def test_window_1303_1316_required_token_blocks_are_non_empty() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))
        assert tokens
        assert all(" " not in token for token in tokens)


def test_window_1303_1316_sensitive_prompts_require_explicit_go() -> None:
    for prompt_name in SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]
        assert "**SENSITIVE**" in text
        assert f"GO Phase {phase}" in text


def test_window_1303_1316_prompts_reference_candidate_guidance_and_lock() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "ilc_window_1303_1316_candidate_phase_grouping_v0.1.md" in text
        assert "ilc_phase_1303_1316_sequence_lock_v0.1.md" in text


def test_phase_1308_prompt_records_disposition_without_export_execution() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1308_g8_public_rc_exclude_helper_pruning_replacement_plan.md"
    )

    for phrase in (
        "replace_before_export",
        "strip_from_export",
        "defer_public_rc",
        "helper_stripping_not_executed_phase_1308",
        "source_allowlist_export_not_executed_phase_1308",
        "does not execute source export",
        "Default to `defer_public_rc`",
    ):
        assert phrase in text


def test_phase_1313_prompt_preserves_rust_gate_and_default_off_boundary() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1313_g8_public_fetch_p2p_activation_candidate_default_off.md"
    )

    for phrase in (
        "rust_public_p2p_substrate_gate_status_recorded_phase_1313",
        "public_p2p_default_off_phase_1313",
        "public_fetch_serving_default_off_phase_1313",
        "If there is no explicit Rust public-P2P substrate ADR/integration gate",
        "Do not infer public transport authority",
        "Public P2P activation in Phase 1313",
        "Public fetch serving in Phase 1313",
        "must remain readiness-only",
    ):
        assert phrase in text

    assert "unless explicitly authorized" not in text
    assert "default off unless explicit authority" not in text


def test_planning_index_references_window_1303_1316_guidance_and_lock() -> None:
    text = _text(PLANNING_INDEX)

    assert "ilc_phase_1303_1316_sequence_lock_v0.1.md" in text
    assert "ilc_window_1303_1316_candidate_phase_grouping_v0.1.md" in text
    assert "window_1303_1316_candidate_phase_grouping_drafted_after_phase_1302" in text
    assert "window_1303_1316_candidate_phase_grouping_consumed_by_phase_1303_sequence_lock" in text
    assert "window_1303_1316_sequence_lock_committed" in text
    assert "phase_1303_window_1303_1316_sequence_lock_required" in text
