"""Phase 1153 — Genesis Canonical Lineage Contract planning spec."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_spec_exists_with_phase_token() -> None:
    text = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "genesis_canonical_lineage_contract_planning_spec_committed_phase_1153" in text
    assert ROOT_HASH in text


def test_spec_defines_network_id_and_gossip_domain() -> None:
    text = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "network_id = H(\"ILC_NETWORK_ID_V1\"" in text
    assert "genesis_domain = H(\"ILC_GENESIS_GOSSIP_DOMAIN_V1\"" in text


def test_spec_requires_node_zero_inclusion_chain() -> None:
    text = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "artifact:genesis_intent_attestation_init_authority_map" in text
    assert "Node 0 appears in the node manifest" in text
    assert "release artifact lineage references" in text


def test_spec_keeps_release_key_genesis_bound_not_independent() -> None:
    text = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "not an independent root" in text
    assert "Phase 1153 does not create or authorize the release key" in text


def test_spec_covers_rolling_ecu_and_transition_policy() -> None:
    text = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "Rolling ECU Legitimacy Windows" in text
    assert "prior_envelope_hash" in text
    assert "public_rc_envelope_hash_transition_policy_required" in text


def test_spec_has_non_goals_against_adr_cdl_runtime_and_legal_claims() -> None:
    text = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "open or ratify a CDL" in text
    assert "authorize runtime enforcement" in text
    assert "make license, trademark, or legal recommendations" in text
