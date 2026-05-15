from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
CDL = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"

# Ordered phase prompts for Window 1343-1368.
# The superseded Phase 1347a draft is excluded — it has a tombstone banner and
# is not an executable prompt.
PHASE_PROMPTS = (
    "antigravity_prompt__phase_1343_g8_window_1343_1368_sequence_lock_capsule_v5_56.md",
    "antigravity_prompt__phase_1344_g8_issuance_stack_scoping.md",
    "antigravity_prompt__phase_1345_g8_production_epoch_emission_engine.md",
    "antigravity_prompt__phase_1346_g8_cdl_028_fee_burn_split_runtime.md",
    "antigravity_prompt__phase_1347_g8_cdl_029_80_15_5_allocation_distributor.md",
    "antigravity_prompt__phase_1348_g8_cdl_047_treasury_governance_runtime.md",
    "antigravity_prompt__phase_1349_g8_cdl_054_validator_reward_pool_routing.md",
    "antigravity_prompt__phase_1350_g8_cdl_083_ejected_stake_treasury_distribution.md",
    "antigravity_prompt__phase_1351_g8_cdl_030_ecu_price_clamp_runtime.md",
    "antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md",
    "antigravity_prompt__phase_1352_g8_issuance_economics_integration_gate.md",
    "antigravity_prompt__phase_1353_g8_cdl_017_validator_admission_ejection_sec_004_wiring.md",
    "antigravity_prompt__phase_1354_g8_cdl_068_topology_shuffle_vrf_runtime.md",
    "antigravity_prompt__phase_1355_g8_cdl_v6_genesis_intervention_enforcement.md",
    "antigravity_prompt__phase_1356_g8_cdl_013_governance_weight_live_integration.md",
    "antigravity_prompt__phase_1357_g8_reputation_py_h11_float_kill_decimal_rewrite.md",
    "antigravity_prompt__phase_1358_g8_ilc_core_ilc_consensus_production_bridge.md",
    "antigravity_prompt__phase_1359_g8_high_001_two_layer_defense.md",
    "antigravity_prompt__phase_1360_g8_multi_operator_mysticeti_testnet.md",
    "antigravity_prompt__phase_1360_g8_four_validator_epoch_finalization_fix1.md",
    "antigravity_prompt__phase_1361_g8_cdl_043_044_adaptive_pruning_completion.md",
    "antigravity_prompt__phase_1362_g8_blocking_authority_vehicle_opening.md",
    "antigravity_prompt__phase_1363_g8_blocking_authority_deliberation_prelock.md",
    "antigravity_prompt__phase_1364_g8_blocking_authority_ratification_cdl_057_activation.md",
    "antigravity_prompt__phase_1365_g8_capsule_v5_57_coherence_report.md",
    "antigravity_prompt__phase_1366_g8_soft_rc_readiness_gate.md",
    "antigravity_prompt__phase_1367_g8_pre_gate_fix_pass.md",
    "antigravity_prompt__phase_1368_g8_window_1343_1368_closure_handoff.md",
)

# Prompts that are NON-SENSITIVE — no additional GO token needed beyond prompt approval.
NON_SENSITIVE_PROMPTS = {
    "antigravity_prompt__phase_1344_g8_issuance_stack_scoping.md",
    "antigravity_prompt__phase_1360_g8_four_validator_epoch_finalization_fix1.md",
    "antigravity_prompt__phase_1365_g8_capsule_v5_57_coherence_report.md",
}

# CDL mutation phases require extra env-var authority in addition to the human GO token.
CDL_MUTATION_PHASES = {
    "antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md": "1351a",
    "antigravity_prompt__phase_1362_g8_blocking_authority_vehicle_opening.md": "1362",
    "antigravity_prompt__phase_1363_g8_blocking_authority_deliberation_prelock.md": "1363",
    "antigravity_prompt__phase_1364_g8_blocking_authority_ratification_cdl_057_activation.md": "1364",
}

# Issuance economics runtimes (Phases 1345–1351) must record a NOT_ACTIVATED token.
ISSUANCE_RUNTIME_PROMPTS = {
    "antigravity_prompt__phase_1345_g8_production_epoch_emission_engine.md",
    "antigravity_prompt__phase_1346_g8_cdl_028_fee_burn_split_runtime.md",
    "antigravity_prompt__phase_1347_g8_cdl_029_80_15_5_allocation_distributor.md",
    "antigravity_prompt__phase_1348_g8_cdl_047_treasury_governance_runtime.md",
    "antigravity_prompt__phase_1349_g8_cdl_054_validator_reward_pool_routing.md",
    "antigravity_prompt__phase_1350_g8_cdl_083_ejected_stake_treasury_distribution.md",
    "antigravity_prompt__phase_1351_g8_cdl_030_ecu_price_clamp_runtime.md",
}

# Phase 1351a was drafted before the MemPalace and graph_delta walkthrough requirements
# were standardized for this window. It has already been committed and executed.
# Exempt it from those specific checks only.
SCHEMA_EXEMPT_PROMPTS = {
    "antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md",
}
# Back-compat alias used in discovery section test
MEMPALACE_EXEMPT_PROMPTS = SCHEMA_EXEMPT_PROMPTS

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
    tokens = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        # Handle OR-alternatives like "token_a | token_b" — flatten to individual tokens
        for part in line.split("|"):
            part = part.strip()
            if part:
                tokens.append(part)
    return tokens


def test_window_1343_1368_sequence_lock_covers_all_phases() -> None:
    text = _text(SEQUENCE_LOCK)

    for phase in range(1343, 1369):
        assert f"| {phase} |" in text, f"Phase {phase} missing from sequence lock"

    assert "Phase 1351a" in text or "| 1351a |" in text, "Phase 1351a missing from sequence lock"

    for token in (
        "window_1343_1368_sequence_lock_committed",
        "window_1343_1368_sequence_lock_verdict=pass",
        "context_capsule_v5_56_window_1343_sequence_lock_phase_1343.v0.1",
        "capsule_v5_56_supersedes_v5_55",
        "phase_1344_issuance_stack_scoping_next",
        "window_1343_1368_no_public_activation_or_value_path_authority",
        "soft_rc_gate_routed_phase_1366",
        "public_rc_remains_blocked_after_phase_1343",
        "cdl_053_vehicle_collision_recorded_phase_1343",
    ):
        assert token in text, f"Required token missing from sequence lock: {token}"


def test_window_1343_1368_sequence_lock_records_cdl_mutation_requirements() -> None:
    text = _text(SEQUENCE_LOCK)

    for phase_num in ("1362", "1363", "1364"):
        assert f"ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE={phase_num}" in text, (
            f"CDL mutation env var missing from sequence lock for Phase {phase_num}"
        )

    assert "1351a" in text
    assert "ILC_CDL_MUTATION_AUTHORIZED=1" in text


def test_window_1343_1368_all_prompts_exist() -> None:
    for prompt_name in PHASE_PROMPTS:
        path = PROMPT_DIR / prompt_name
        assert path.exists(), f"Prompt file missing: {prompt_name}"


def test_window_1343_1368_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        errors = validate(PROMPT_DIR / prompt_name)
        assert not errors, f"{prompt_name} failed schema validation: {errors}"


def test_window_1343_1368_prompt_drafts_include_discovery_sections() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)

        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text, f"{prompt_name} missing discovery section: {section}"

        if prompt_name not in SCHEMA_EXEMPT_PROMPTS:
            assert "MemPalace" in text, f"{prompt_name} missing MemPalace reference"
            assert "graph_delta" in text, f"{prompt_name} missing graph_delta"
        assert "No ellipses in walkthrough" in text, f"{prompt_name} missing ellipsis rule"
        assert "## Non-authorization floor" in text, f"{prompt_name} missing Non-authorization floor"


def test_window_1343_1368_prompt_drafts_have_required_tokens() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        tokens = _required_tokens(text)

        assert tokens, f"{prompt_name} has no Required Tokens"
        assert any(
            token.endswith(".v0.1") or "_phase_" in token or token.endswith("_next")
            for token in tokens
        ), f"{prompt_name} required tokens lack a versioned or phase-scoped token"
        assert all(" " not in token for token in tokens), (
            f"{prompt_name} required tokens contain whitespace"
        )


def test_window_1343_1368_sensitive_prompts_have_go_gates() -> None:
    for prompt_name in PHASE_PROMPTS:
        if prompt_name in NON_SENSITIVE_PROMPTS:
            continue

        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]

        assert "**SENSITIVE**" in text or "SENSITIVE" in text, (
            f"{prompt_name} does not declare SENSITIVE"
        )
        assert f"GO Phase {phase}" in text, (
            f"{prompt_name} missing GO gate for phase {phase}"
        )


def test_window_1343_1368_non_sensitive_prompts_are_correctly_classified() -> None:
    for prompt_name in NON_SENSITIVE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        assert "NON-SENSITIVE" in text, (
            f"{prompt_name} expected to be NON-SENSITIVE but classification is missing"
        )


def test_window_1343_1368_cdl_mutation_prompts_require_env_authority() -> None:
    for prompt_name, phase_num in CDL_MUTATION_PHASES.items():
        text = _text(PROMPT_DIR / prompt_name)

        assert f"ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE={phase_num}" in text, (
            f"{prompt_name} missing CDL mutation env-var requirement"
        )
        assert "two-commit" in text.lower() or "separate commit" in text.lower(), (
            f"{prompt_name} missing two-commit pattern requirement"
        )


def test_window_1343_1368_issuance_runtime_prompts_forbid_production_activation() -> None:
    for prompt_name in ISSUANCE_RUNTIME_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)

        assert "not_activated" in text.lower() or "NOT_ACTIVATED" in text, (
            f"{prompt_name} missing production NOT_ACTIVATED guard token"
        )
        # Each runtime uses slightly different prohibition language; check for any form.
        text_lower = text.lower()
        assert (
            "must not activate" in text_lower
            or "must not activate production" in text_lower
            or "not activate production" in text_lower
            or "not activated" in text_lower
        ), f"{prompt_name} missing explicit activation prohibition"


def test_window_1343_1368_phase_1352_gate_references_full_stack() -> None:
    text = _text(
        PROMPT_DIR / "antigravity_prompt__phase_1352_g8_issuance_economics_integration_gate.md"
    )

    for cdl in ("CDL-025", "CDL-026", "CDL-027", "CDL-028", "CDL-029",
                "CDL-030", "CDL-031", "CDL-047", "CDL-054", "CDL-083"):
        assert cdl in text, f"Phase 1352 gate missing reference to {cdl}"

    assert "double-entry" in text or "double_entry" in text, (
        "Phase 1352 missing double-entry ledger invariant reference"
    )
    assert "issuance_economics_integration_gate" in text, (
        "Phase 1352 missing gate token"
    )
    assert "issuance_economics_integration_gate_pass" in text, (
        "Phase 1352 missing pass verdict token"
    )
    assert "issuance_economics_integration_gate_blocked" in text, (
        "Phase 1352 missing blocked verdict token"
    )


def test_window_1343_1368_phase_1366_is_soft_rc_gate() -> None:
    text = _text(
        PROMPT_DIR / "antigravity_prompt__phase_1366_g8_soft_rc_readiness_gate.md"
    )

    assert "soft_rc" in text.lower() or "soft-RC" in text or "soft RC" in text, (
        "Phase 1366 missing soft-RC reference"
    )
    assert "GO Phase 1366" in text, "Phase 1366 missing GO gate"
    assert "production_distribution_not_activated" in text.lower() or "not activated" in text.lower(), (
        "Phase 1366 missing production activation guard"
    )


def test_window_1343_1368_phase_1368_is_closure_handoff() -> None:
    text = _text(
        PROMPT_DIR / "antigravity_prompt__phase_1368_g8_window_1343_1368_closure_handoff.md"
    )

    assert "closure" in text.lower(), "Phase 1368 missing closure reference"
    assert "Window 1343" in text or "window_1343_1368" in text, (
        "Phase 1368 missing window reference"
    )
    assert "GO Phase 1368" in text, "Phase 1368 missing GO gate"


def test_window_1343_1368_tombstoned_phase_1347a_is_superseded() -> None:
    path = PROMPT_DIR / "antigravity_prompt__phase_1347a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md"
    assert path.exists(), "Phase 1347a tombstone file missing"

    text = path.read_text(encoding="utf-8")
    assert "SUPERSEDED" in text, "Phase 1347a tombstone banner missing"
    assert "1351a" in text or "phase_1351a" in text, (
        "Phase 1347a tombstone does not point to superseding Phase 1351a prompt"
    )


def test_window_1343_1368_planning_index_registers_window() -> None:
    text = _text(PLANNING_INDEX)

    for phrase in (
        "Window 1343-1368 is OPEN",
        "Phase 1351a",
        "cdl_029_amendment_phase_1351a",
        # Phase 1352 gate result token will be present after Phase 1352 executes.
        # For now, verify the Phase 1352 integration gate is mentioned as next planned phase.
        "Phase 1352",
    ):
        assert phrase in text, f"PLANNING_INDEX missing phrase: {phrase!r}"


def test_window_1343_1368_forward_plan_records_ecl_ilc_layer_distinction() -> None:
    text = _text(FORWARD_PLAN)

    for phrase in (
        # Heading uses "ECU / ILC" with spaces (see line 666)
        "ECU / ILC Layer Distinction",
        "Mode-2 Refutation Adjudication and Settlement",
        "Window 1391-1398",
        "Window 1399",
    ):
        assert phrase in text, (
            f"Forward plan missing required section/phrase: {phrase!r}"
        )


def test_window_1343_1368_phase_1351a_references_cdl_083_not_cdl_v7_for_attribution() -> None:
    text = _text(
        PROMPT_DIR
        / "antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md"
    )

    assert "CDL-083" in text, "Phase 1351a must reference CDL-083 Q4"
    assert "caller-filtered" in text, "Phase 1351a must specify caller-filtered recipients"
    assert "performer pool" in text, "Phase 1351a must specify performer pool fallback"
    assert "sub-quantum residual" in text, "Phase 1351a must scope to sub-quantum residuals only"
    assert "genesis_overhead_cap_blocked" in text, (
        "Phase 1351a must reference genesis_overhead_cap_blocked parameter"
    )
    # CDL-V7 must not be the primary attribution interface — CDL-083 Q4 supersedes it
    # for dust routing purposes. The prompt may still mention CDL-V7 for context, but
    # the known-token table must clarify the distinction.
    assert "CDL-083 Q4" in text or "upheld-refutation recipients" in text, (
        "Phase 1351a must reference CDL-083 Q4 upheld-refutation recipients"
    )
