from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"
GUIDANCE = ROOT / "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"

PHASE_PROMPTS = (
    "antigravity_prompt__phase_1330_g8_window_1330_1342_sequence_lock.md",
    "antigravity_prompt__phase_1331_g8_context_capsule_v5_55_release_candidate_freeze.md",
    "antigravity_prompt__phase_1332_g8_final_deterministic_code_security_audit.md",
    "antigravity_prompt__phase_1333_g8_source_allowlist_export_execution_gate.md",
    "antigravity_prompt__phase_1334_g8_release_artifact_production_gate.md",
    "antigravity_prompt__phase_1335_g8_release_keys_envelopes_generation_gate.md",
    "antigravity_prompt__phase_1336_g8_public_claimability_api_activation_or_carry_forward_gate.md",
    "antigravity_prompt__phase_1337_g8_public_path_sidecar_activation_or_exclusion_gate.md",
    "antigravity_prompt__phase_1338_g8_wallet_ecu_ilc_activation_or_carry_forward_gate.md",
    "antigravity_prompt__phase_1339_g8_atlas_g_mutation_regeneration_finalization.md",
    "antigravity_prompt__phase_1340_g8_v0_2_signing_ceremony_gate.md",
    "antigravity_prompt__phase_1341_g8_public_rc_publication_claim_gate.md",
    "antigravity_prompt__phase_1342_g8_window_1330_1342_closure_handoff.md",
)

UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

HIGH_AUTHORITY_PHRASES = {
    "antigravity_prompt__phase_1335_g8_release_keys_envelopes_generation_gate.md": (
        "GO Phase 1335: authorize release key/envelope generation"
    ),
    "antigravity_prompt__phase_1340_g8_v0_2_signing_ceremony_gate.md": (
        "GO Phase 1340: authorize v0.2 signing ceremony"
    ),
    "antigravity_prompt__phase_1341_g8_public_rc_publication_claim_gate.md": (
        "GO Phase 1341: authorize public RC publication/claim"
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


def test_window_1330_1342_guidance_is_planning_only_and_routes_all_phases() -> None:
    text = _text(GUIDANCE)

    for token in (
        "window_1330_1342_candidate_phase_grouping_drafted_after_phase_1329",
        "window_1330_1342_not_open_until_sequence_lock",
        "phase_1330_window_1330_1342_sequence_lock_required",
        "final_rc_signing_gate_public_rc_still_blocked_by_default",
        "source_allowlist_export_execution_gate_routed_phase_1333",
        "release_artifact_production_gate_routed_phase_1334",
        "release_key_envelope_generation_gate_routed_phase_1335",
        "public_claimability_api_gate_or_carry_forward_phase_1336",
        "public_path_sidecar_confidential_coordination_gate_or_exclusion_phase_1337",
        "wallet_ecu_ilc_activation_gate_or_carry_forward_phase_1338",
        "atlas_g_tail_routed_phase_1339_1340_before_signing",
        "public_rc_publication_claim_gate_routed_phase_1341",
        "window_1330_1342_prompt_drafts_registered",
    ):
        assert token in text

    for phase in range(1330, 1343):
        assert f"| {phase} |" in text

    for phrase in (
        "Planning-only candidate guidance. Not a sequence lock.",
        "does not open Window 1330-1342",
        "Phase 1330 sequence lock is required",
        "Identity Bootstrap Stop Guard",
        "CDL-069 commitment mismatch",
        "GO Phase 1335: authorize release key/envelope generation",
        "GO Phase 1340: authorize v0.2 signing ceremony",
        "GO Phase 1341: authorize public RC publication/claim",
    ):
        assert phrase in text


def test_window_1330_1342_prompt_drafts_match_phase_prompt_schema() -> None:
    for prompt_name in PHASE_PROMPTS:
        validate(PROMPT_DIR / prompt_name)


def test_window_1330_1342_prompt_drafts_include_discovery_and_walkthrough_controls() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)

        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            assert section in text, prompt_name

        assert "MemPalace" in text, prompt_name
        assert "No ellipses in walkthrough" in text, prompt_name
        assert "graph_delta" in text, prompt_name
        assert "## Non-authorization floor" in text, prompt_name


def test_window_1330_1342_prompt_drafts_have_required_tokens() -> None:
    for prompt_name in PHASE_PROMPTS:
        tokens = _required_tokens(_text(PROMPT_DIR / prompt_name))

        assert tokens, prompt_name
        assert any(
            token.endswith((".v0.1", "_next"))
            or token.startswith(("window_1330_1342", "phase_1342"))
            for token in tokens
        ), prompt_name
        assert any("public_rc" in token for token in tokens), prompt_name
        assert all(" " not in token for token in tokens), prompt_name


def test_window_1330_1342_sensitive_prompts_preserve_go_gates() -> None:
    for prompt_name in PHASE_PROMPTS:
        text = _text(PROMPT_DIR / prompt_name)
        phase = prompt_name.split("__phase_", maxsplit=1)[1].split("_", maxsplit=1)[0]

        if phase == "1331":
            assert "NON-SENSITIVE after Phase 1330 lock" in text
            assert "GO Phase 1331" in text
            continue

        assert "**SENSITIVE**" in text, prompt_name
        assert f"GO Phase {phase}" in text, prompt_name


def test_window_1330_1342_high_authority_prompts_require_stronger_phrases() -> None:
    guidance = _text(GUIDANCE)
    for prompt_name, phrase in HIGH_AUTHORITY_PHRASES.items():
        text = _text(PROMPT_DIR / prompt_name)

        assert phrase in guidance
        assert phrase in text
        assert "Ordinary queue position is not enough" in text


def test_planning_index_registers_window_1330_1342_as_draft_only() -> None:
    text = _text(PLANNING_INDEX)

    for phrase in (
        "Window 1330-1342 draft package (planning-only)",
        "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md",
        "antigravity_prompt__phase_1330_g8_window_1330_1342_sequence_lock.md",
        "do not open Window 1330-1342",
        "Phase 1330 requires a future explicit `GO Phase 1330`",
    ):
        assert phrase in text
