import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_privacy_preserving_proximity_hydration_rehearsal_1545p_fix11_v0.1.md"
FIXTURE = ROOT / "out/privacy_preserving_proximity_hydration_rehearsal_1545p_fix11.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix11_privacy_preserving_proximity_hydration_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix11_tokens_and_not_live_zkp_boundary() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix11_privacy_preserving_proximity_hydration_committed",
        "proximity_witness_not_live_zkp_recorded_phase_1545p_fix11",
        "merkle_laplacian_hydration_commitment_boundary_recorded_phase_1545p_fix11",
        "public_sidecar_serving_not_activated_phase_1545p_fix11",
        "public_p2p_not_activated_phase_1545p_fix11",
        "genesis_manifest_not_mutated_phase_1545p_fix11",
        "public_path_remains_blocked_phase_1545p_fix11",
    ]:
        assert token in text

    assert "not a live ZKP" in text
    assert "not an anonymity system" in text
    assert "not an unlinkability guarantee" in text
    assert "no formal zero-knowledge circuit, verifier, proof system, or public proof service" in text


def test_data_flow_disclosure_budget_and_rejection_tokens() -> None:
    text = read(SPEC)

    for phrase in [
        "Private upstream path set",
        "Committed rule identifier",
        "committed_subgraph_id",
        "disclosure budget",
        "Router verification",
        "private_path_disclosure_forbidden",
        "identity_material_disclosure_forbidden",
        "live_zkp_claim_without_verifier",
        "proximity_witness_bounds_missing",
    ]:
        assert phrase in text


def test_router_and_sidecar_boundaries_are_explicit() -> None:
    text = read(SPEC)

    assert "Router" in text
    assert "Learn full upstream path sets" in text
    assert "infer public identity from witness" in text
    assert "Public-serve witnesses" in text
    assert "claim Signal-equivalent anonymity" in text
    assert "Treat proximity as type authority, Genesis authority, economic authority, or public onboarding authority." in text


def test_toy_fixture_is_non_secret_and_non_activating() -> None:
    payload = json.loads(read(FIXTURE))

    assert payload["proximity_witness_kind"] == "structural_commitment_rehearsal_not_live_zkp"
    assert payload["authorization_flags"]["formal_zkp_verifier_active"] is False
    assert payload["authorization_flags"]["public_sidecar_serving_enabled"] is False
    assert payload["authorization_flags"]["public_p2p_enabled"] is False
    assert payload["disclosure_budget"]["path_disclosure"] == "none"
    assert payload["disclosure_budget"]["identity_disclosure"] == "none"
    assert "private_path_disclosure_forbidden" in payload["rejection_tokens"]
    assert "toy graph only" in payload["privacy_statement"]


def test_non_claims_and_frontier_docs_record_fix11() -> None:
    text = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    for phrase in [
        "live ZKP routing",
        "anonymity",
        "unlinkability",
        "public sidecar serving",
        "public P2P activation",
        "public confidential coordination serving",
        "Genesis manifest mutation",
        "ECU minting",
        "public RC activation",
    ]:
        assert phrase in text

    assert "phase_1545p_fix11_privacy_preserving_proximity_hydration_committed" in walkthrough
    assert "Phase 1545p-Fix11" in status
    assert "Phase 1545p-Fix11" in planning
    assert "⬅ CURRENT" in planning.split("Phase 1545p-Fix11", 1)[1].splitlines()[0]
