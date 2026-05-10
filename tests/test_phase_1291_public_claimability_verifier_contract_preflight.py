from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1291_g8_public_claimability_verifier_contract_preflight.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1291_public_claimability_verifier_contract_preflight_walkthrough.md"
SWEEPER = "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
PROOF_BINDING = "ilc_core/ledger/claimability_proof_binding_runtime.py"

REQUIRED_TOKENS = (
    "public_claimability_verifier_contract_preflight_phase_1291.v0.1",
    "public_claimability_activation_not_authorized_by_default_phase_1291",
    "claimability_verifier_public_api_not_enabled_phase_1291",
    "wallet_withdrawal_transfer_spend_still_blocked_phase_1291",
    "public_rc_remains_blocked_after_phase_1291",
)

EXTRA_TOKENS = (
    "public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled",
    "claimability_contract_no_runtime_helper_added_phase_1291",
    "phase_1292_verifier_negative_path_corpus_package_boundary_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1291_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in EXTRA_TOKENS:
        assert token in read(SPEC)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1291_contract_boundary_defines_future_envelopes_only() -> None:
    spec = read(SPEC)

    assert "ClaimabilityVerifierInput" in spec
    assert "ClaimabilityVerifierDecision" in spec
    for phrase in (
        "settled_runtime_root",
        "wallet_state_root",
        "latest_balance_receipt_ref",
        "history_digest",
        "claimability_proof_ref",
        "conversion_receipt_sha256",
        "conversion_key_sha256",
        "conversion_lot_id",
        "conversion_deadline_epoch",
        "transport_principal_ref",
    ):
        assert phrase in spec

    assert "does not implement them" in spec
    assert "No new runtime helper is introduced" in spec
    assert "claimability_contract_no_runtime_helper_added_phase_1291" in spec


def test_phase_1291_keeps_all_activation_flags_false() -> None:
    spec = read(SPEC)

    for phrase in (
        "public_claimability_activated",
        "non_loopback_claimability_api_enabled",
        "wallet_withdrawal_enabled",
        "wallet_transfer_enabled",
        "wallet_spend_enabled",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
        "Must remain `false`",
    ):
        assert phrase in spec

    for denial in (
        "Any activation flag is `true`",
        "public or non-loopback claimability API",
        "Python float",
        "non-finite Decimal",
        "non-string keys",
        "cycles",
        "excessive depth",
        "replay/nullifier",
        "field-level public-safe disclosure schema",
        "PUBLIC_RC_EXCLUDE",
    ):
        assert denial in spec


def test_phase_1291_does_not_add_public_claimability_surface() -> None:
    spec = read(SPEC)
    walkthrough = read(WALKTHROUGH)

    for text in (spec, walkthrough):
        for phrase in (
            "no HTTP route",
            "FastAPI route",
            "socket listener",
            "non-loopback bind",
            "wildcard bind",
            "public host bind",
            "peer discovery",
            "claim endpoint",
            "withdrawal endpoint",
            "transfer endpoint",
            "spend endpoint",
            "ECU mint endpoint",
            "ILC settlement endpoint",
        ):
            assert phrase in text

    assert "public verifier service" in spec
    assert "public claimability API activation" in spec


def test_phase_1291_existing_helpers_remain_public_rc_excluded() -> None:
    sweeper_header = read(SWEEPER).splitlines()[:4]
    proof_header = read(PROOF_BINDING).splitlines()[:4]
    spec = read(SPEC)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in "\n".join(
        sweeper_header
    )
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in "\n".join(
        proof_header
    )
    assert "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py" in spec
    assert "ilc_core/ledger/claimability_proof_binding_runtime.py" in spec


def test_phase_1291_public_safe_disclosure_remains_open() -> None:
    spec = read(SPEC)

    assert "does not declare the full Phase 1275 proof-binding payload public-safe" in spec
    assert "Public-safe field projection remains open" in spec
    assert "Correctness and public disclosure are separate gates" in spec


def test_phase_1291_updates_frontier_without_breaking_phase_1290_history() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1289-1302 is OPEN through Phase 1291" in planning
    assert "Window 1289-1302 is open through Phase 1291" in capsule
    assert "Window 1289-1302 OPEN through Phase 1291" in roadmap
    assert "Phase 1292 is sensitive" in planning
    assert "Phase 1292 is sensitive" in capsule

    assert "Window 1289-1302 is OPEN through Phase 1290" in planning
    assert "Window 1289-1302 is open through Phase 1290" in capsule


def test_phase_1291_prompt_references_active_1289_1302_window() -> None:
    prompt = read(PROMPT)

    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt


def test_phase_1291_carry_forward_blocks_public_rc_and_routes_1292() -> None:
    spec = read(SPEC)
    status = read(STATUS)
    capsule = read(CAPSULE)

    for phrase in (
        "Public RC remains blocked after Phase 1291",
        "Phase 1292 verifier negative-path corpus",
        "public-safe disclosure schema",
        "TransportPrincipal public-path activation authority",
        "wallet withdrawal",
        "wallet transfer",
        "wallet spend",
        "ECU minting",
        "ILC settlement",
        "CDL-088",
    ):
        assert phrase in spec or phrase in status

    assert "phase_1292_verifier_negative_path_corpus_package_boundary_next" in status
    assert "phase_1292_verifier_negative_path_corpus_package_boundary_next" in capsule


def test_phase_1291_walkthrough_records_discovery_graph_delta_and_verification() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for phrase in (
        "Section 0a Known-token audit",
        "Section 0b Concept-discovery search",
        "Section 0c Contradiction and non-claim search",
        "Section 0d Source expansion",
        "Public-Surface Denial Checks",
        "Graph Delta",
        "Verification",
    ):
        assert phrase in walkthrough

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md -> ecu/ilc/public_rc",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1291_g8_public_claimability_verifier_contract_preflight.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1291_public_claimability_verifier_contract_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1291_public_claimability_verifier_contract_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
