from __future__ import annotations

import json
from pathlib import Path

from ilc_core.bundle.type_registry import (
    ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED,
    TypeRegistryCache,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_genesis_common_registry_node_candidate_audit_1545p_fix7_v0.1.md"
ADDENDUM = ROOT / "docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.3_candidate_addendum.md"
QUEUE = ROOT / "out/genesis_common_registry_node_candidates_1545p_fix7.json"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.3_candidate.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix7_genesis_common_registry_node_candidate_audit_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def queue() -> dict[str, object]:
    return json.loads(read(QUEUE))


def candidate_ids() -> set[str]:
    data = queue()
    candidates = data["candidates"]
    assert isinstance(candidates, list)
    return {str(candidate["candidate_id"]) for candidate in candidates}


def test_fix7_tokens_and_successor_target_are_recorded() -> None:
    text = read(SPEC)
    for token in (
        "phase_1545p_fix7_genesis_common_registry_node_candidate_audit_committed",
        "sidecar_registry_candidate_nodes_audited_phase_1545p_fix7",
        "sidecar_install_registry_activation_boundary_recorded_phase_1545p_fix7",
        "common_namespace_candidate_queue_committed_phase_1545p_fix7",
        "public_rc_drift_reconciliation_anchor_consumed_phase_1545p_fix7",
        "post_1447_manifest_relevance_candidates_consumed_phase_1545p_fix7",
        "genesis_successor_target_v04_candidate_required_phase_1545p_fix7",
        "adr_0035_type_registry_remains_not_activated_phase_1545p_fix7",
        "genesis_manifest_not_mutated_phase_1545p_fix7",
        "public_path_remains_blocked_phase_1545p_fix7",
    ):
        assert token in text
    assert "genesis_successor_target_v03_clean_confirmed_phase_1545p_fix7" not in text
    assert "successor_target=v0.4_candidate_required" in text


def test_support_only_candidate_queue_shape_and_canonical_dump() -> None:
    data = queue()
    assert data["artifact_status"] == "support_only_candidate_queue"
    assert data["authority_status"] == "not_authority_bearing"
    assert data["genesis_manifest_mutation"] is False
    assert data["successor_target"] == "v0.4_candidate_required"
    assert data["successor_target_token"] == "genesis_successor_target_v04_candidate_required_phase_1545p_fix7"
    assert data["type_registry_guard"] == "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED=True"

    # The support queue must remain deterministic for later tooling.
    assert json.dumps(data, sort_keys=True, indent=2) + "\n" == read(QUEUE)


def test_required_candidate_families_are_present() -> None:
    required = {
        "adr:0009_protocol_native_bundle_distribution",
        "adr:0035_type_definition_authority",
        "cdl:096_werner_global_tier_authority",
        "registry:sidecar",
        "registry:sidecar_recipe",
        "recipe:confidential-contact",
        "namespace:sidecar_id",
        "namespace:recipe_id",
        "namespace:agent_id",
        "namespace:external_identifier",
        "namespace:content_address",
        "registry:node_type",
        "registry:hyperedge_type",
        "registry:content_type",
        "registry:parameter",
        "registry:validator_endpoint",
        "registry:agent_endpoint",
        "transport:direct",
        "transport:tor_onion",
        "transport:ccss_local_private_contact",
        "economic:emission_production_path",
        "economic:validator_admission_ejection",
        "economic:treasury_validator_reward",
        "economic:ejected_stake_distribution",
        "economic:productive_ecu_expansion_bounty",
        "economic:adaptive_fee_burn",
        "economic:peer_funded_bounty",
    }
    assert required <= candidate_ids()


def test_no_candidate_claims_authority_or_activation() -> None:
    data = queue()
    candidates = data["candidates"]
    assert isinstance(candidates, list)
    for candidate in candidates:
        assert candidate["authority_status"] == "not_authority_bearing"
        assert candidate["disposition"] == "candidate_queue_only"
        assert candidate["classification"] in {
            "must_include_genesis_node",
            "candidate_common_node",
            "sidecar_recipe_node",
            "support_only",
            "exclude_private_process",
        }
        assert candidate["legacy_classification"] in {
            "genesis_core_candidate",
            "post_genesis_registry_candidate",
            "sidecar_local_only_candidate",
            "reject_or_defer",
        }


def test_type_registry_remains_default_off_and_non_authority_bearing() -> None:
    assert ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED is True
    state = TypeRegistryCache().startup_state()
    assert state.activated is False
    assert state.guard is True
    assert dict(state.definitions) == {}


def test_signed_v03_star_map_was_not_mutated() -> None:
    data = json.loads(read(STAR_MAP))
    assert len(data["nodes"]) == 54
    assert len(data["edges"]) == 77


def test_decision_log_records_sidecar_boundary_and_v04_target() -> None:
    text = read(ADDENDUM)
    assert "`GND-0036`" in text
    assert "Successor target is `v0.4_candidate_required`" in text
    assert "Separate local sidecar install, registry acceptance, and public/protocol activation" in text
    assert "sidecar_install_registry_activation_boundary_recorded_phase_1545p_fix7" in text


def test_frontier_docs_record_fix7_and_non_claims() -> None:
    for path in (WALKTHROUGH, STATUS, PLANNING_INDEX):
        text = read(path)
        assert "phase_1545p_fix7_genesis_common_registry_node_candidate_audit_committed" in text
        assert "genesis_successor_target_v04_candidate_required_phase_1545p_fix7" in text
        assert "public_path_remains_blocked_phase_1545p_fix7" in text
    assert "local install is not registry acceptance" in read(WALKTHROUGH)
