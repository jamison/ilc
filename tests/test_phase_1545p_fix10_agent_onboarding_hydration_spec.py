from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_agent_onboarding_organic_graph_hydration_spec_1545p_fix10_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix10_agent_onboarding_organic_graph_hydration_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix10_tokens_and_current_canon_are_recorded() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix10_agent_onboarding_hydration_spec_committed",
        "invitation_edge_hydration_boundary_recorded_phase_1545p_fix10",
        "organic_graph_hydration_support_only_phase_1545p_fix10",
        "invitation_attribution_not_minting_recorded_phase_1545p_fix10",
        "public_p2p_not_activated_phase_1545p_fix10",
        "genesis_manifest_not_mutated_phase_1545p_fix10",
        "public_path_remains_blocked_phase_1545p_fix10",
    ]:
        assert token in text

    assert "ADR-0009 is Accepted after Phase 1520p" in text
    assert "public operator onboarding" in text
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in text
    assert "Agent INIT is permissionless and zero public epistemic weight until attested." in text


def test_lifecycle_distinguishes_seed_bundle_hydration_support_and_authority() -> None:
    text = read(SPEC)

    for phrase in [
        "receiving a seed",
        "verifying a bundle",
        "hydrating local graph context",
        "creating a local support node",
        "creating an authority-bearing protocol node",
    ]:
        assert phrase in text

    assert "Seed receipt is not identity authority." in text
    assert "Bundle verification is integrity verification, not onboarding authority." in text
    assert "Local graph hydration is support context, not canonical graph admission." in text


def test_invitation_attribution_is_not_economics_or_public_serving() -> None:
    text = read(SPEC)

    assert "Invitation alone does not mint ECU or ILC." in text
    assert "Invitation alone does not admit a validator." in text
    assert "Invitation alone does not activate public serving." in text
    assert "Invitation alone does not create public claimability or public epistemic weight." in text
    assert "Invitation alone does not create wallet, treasury, settlement, fee, reward, or payout authority." in text


def test_fragment_rejection_and_sidecar_boundaries_are_fail_closed() -> None:
    text = read(SPEC)

    for rejection in [
        "hydration_fragment_missing_source_evidence",
        "hydration_fragment_unknown_authority_class",
        "hydration_fragment_type_authority_not_activated",
        "hydration_fragment_public_path_claim_rejected",
        "hydration_fragment_bounds_missing",
        "hydration_fragment_not_replayable",
    ]:
        assert rejection in text

    assert "No public confidential coordination serving" in text
    assert "No public projection endpoint" in text
    assert "No public peer discovery, no public P2P routing, no sidecar registry activation." in text


def test_non_authorizations_and_frontier_docs_record_fix10() -> None:
    text = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    for phrase in [
        "public P2P activation",
        "non-loopback sidecar serving",
        "public RC activation",
        "Genesis manifest mutation",
        "type-registry activation",
        "sidecar registry activation",
    ]:
        assert phrase in text

    assert "phase_1545p_fix10_agent_onboarding_hydration_spec_committed" in walkthrough
    assert "Phase 1545p-Fix10" in status
    assert "Phase 1545p-Fix10" in planning
    fix10_line = planning.split("Phase 1545p-Fix10", 1)[1].splitlines()[0]
    assert "⬅ CURRENT" in fix10_line or "Superseded as current frontier" in fix10_line
