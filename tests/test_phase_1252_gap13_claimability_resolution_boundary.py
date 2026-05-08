from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from ilc_core.ledger.canon_bundle_utils import derive_key_fingerprint, derive_key_id
from ilc_core.ledger.settlement_verification import hash_inputs
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime
from ilc_core.security.key_compromise_runtime import (
    TRIGGER_CUSTODY_LOSS,
    KeyCompromiseResponseRuntime,
)
from ilc_core.security.signer_lineage_runtime import SignerLineageRegistry


SPEC_PATH = Path("docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md")
LIFECYCLE_RUNTIME_PATH = Path("ilc_core/ledger/ecu_ilc_lifecycle_runtime.py")
PUBLIC_WALLET_RUNTIME_PATH = Path("ilc_core/protocol/public_wallet_runtime.py")

REQUIRED_TOKENS = (
    "gap13_claimability_resolution_boundary_phase_1252.v0.1",
    "public_claimability_runtime_not_activated_phase_1252",
    "epoch_commit_settlement_not_agent_manual_claim_default_phase_1252",
    "phase_1252_digest_truncation_security_binding_classification_recorded",
    "phase_1252_gap13_claimability_boundary_complete",
)

CANON_TOKENS = (
    "rc0_1_balance_visibility_does_not_imply_public_claimability",
    "ecu_accrual_reaches_ilc_balance_only_through_epoch_commit",
    "wallet_visibility_and_accounting_only",
    "no_public_claimability_or_spend_in_lifecycle_spec",
)

DIGEST_CANDIDATES = (
    "ilc_core/ledger/canon_bundle_key_registry.py:267",
    "ilc_core/ledger/canon_bundle_key_registry.py:636",
    "ilc_core/ledger/canon_bundle_key_registry_channel_signing.py:54",
    "ilc_core/ledger/canon_bundle_utils.py:23",
    "ilc_core/ledger/settlement_verification.py:56",
    "ilc_core/security/key_compromise_runtime.py:248",
    "ilc_core/security/key_compromise_runtime.py:261",
    "ilc_core/security/signer_lineage_runtime.py:350",
)

NETWORK_CARRY_FORWARD_CANDIDATES = (
    "ilc_core/network/d2d/gossip.py:181",
    "ilc_core/network/d2d/spectral_beacon.py:207",
    "ilc_core/network/star_map/star_map_route_index_runtime.py:120",
)


def _spec_text() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def _is_full_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _registry_with_lineage() -> SignerLineageRegistry:
    registry = SignerLineageRegistry()
    registry.register(
        lineage_id="lineage-alpha",
        canonical_root_key="root-001",
        authority_recovery_key="recovery-001",
        operational_signer_key="ops-001",
        authorizer_signer_id="root-001",
        reason_code="genesis_register",
        event_ts="2026-02-20T00:00:00Z",
    )
    return registry


def test_phase_1252_spec_contains_required_tokens_and_canon_lineage() -> None:
    text = _spec_text()

    for token in REQUIRED_TOKENS + CANON_TOKENS:
        assert token in text
    assert "RCGAP-1250-FIX1-003" in text
    assert "RCGAP-1250-FIX1-006" in text
    assert "GO Phase 1252" in text


def test_phase_1252_spec_locks_resolution_as_epoch_commit_not_agent_manual_claim() -> None:
    text = _spec_text()

    assert "Public claimability must be derived from settled runtime roots and epoch" in text
    assert "not from agent-specific manual claims" in text
    assert "4 issuance-epoch conversion deadline" in text
    assert "not an agent-authored manual entitlement claim" in text


def test_phase_1252_spec_records_non_activation_boundary_and_future_requirements() -> None:
    text = _spec_text()

    for phrase in (
        "does not activate public claimability",
        "does not implement a public claim endpoint",
        "does not implement a public",
        "withdrawal endpoint",
        "spend endpoint",
        "transfer endpoint",
        "public_claimability_runtime_not_activated_phase_1252",
    ):
        assert phrase in text

    for phrase in (
        "Full settled runtime root proof",
        "Replay and double-claim prevention",
        "Rust/chain settlement substrate selection",
        "TransportPrincipal",
        "Counsel/IP/allowlist",
    ):
        assert phrase in text


def test_phase_1252_digest_classification_records_every_fix1_candidate() -> None:
    text = _spec_text()

    for candidate in DIGEST_CANDIDATES:
        assert candidate in text
    for classification in (
        "Already-covered compatibility alias",
        "Storage/display-only",
        "Security/audit-binding evidence hash",
        "Security-binding incident identifier",
        "Security-binding recovery attestation",
        "Security-binding signer-lineage event identifier",
    ):
        assert classification in text


def test_phase_1252_carries_network_digest_candidates_to_transportprincipal() -> None:
    text = _spec_text()

    for candidate in NETWORK_CARRY_FORWARD_CANDIDATES:
        assert candidate in text
    assert "RCGAP-1250-FIX1-004" in text
    assert "phase_1253_transport_digest_and_rust_m5_disposition_recorded" in text
    assert "TransportPrincipal and public-P2P substrate" in text


def test_key_ids_remain_short_aliases_but_fingerprints_are_full_hashes() -> None:
    key = b"phase-1252-test-key"

    assert len(derive_key_id(key)) == 16
    assert _is_full_sha256(derive_key_fingerprint(key))


def test_settlement_verification_input_hash_is_full_canonical_sha256() -> None:
    epoch_record = {"distribution_status": "distributed", "summary": {"reward_total": "100"}}
    snapshot = StakeSnapshot(
        epoch_id="epoch-001",
        epoch_index=1,
        namespace_id="ns",
        stakes={"agent-a": Decimal("1"), "agent-b": Decimal("3")},
        total_stake=Decimal("4"),
        created_at="diagnostic-only",
    )
    before = {"agent-b": "0", "agent-a": "0"}
    after = {"agent-b": "75", "agent-a": "25"}

    first = hash_inputs(epoch_record, snapshot, before, after)
    second = hash_inputs(epoch_record, snapshot, dict(reversed(before.items())), dict(reversed(after.items())))

    assert _is_full_sha256(first)
    assert first == second


def test_security_lineage_and_compromise_ids_are_full_sha256() -> None:
    registry = _registry_with_lineage()

    assert _is_full_sha256(registry.transition_log[0].event_id)

    runtime = KeyCompromiseResponseRuntime(registry)
    incident = runtime.respond_to_compromise(
        lineage_id="lineage-alpha",
        compromised_signer_id="ops-001",
        trigger_class=TRIGGER_CUSTODY_LOSS,
        event_ts="2026-02-20T00:12:00Z",
        containment_authorizer_signer_id="root-001",
        replacement_signer_id="ops-002",
        recovery_ticket_id="ticket-001",
        recovery_authorizer_signer_id="recovery-001",
    )

    assert _is_full_sha256(incident.incident_id)
    assert incident.recovery_attestation is not None
    assert _is_full_sha256(incident.recovery_attestation)
    assert all(_is_full_sha256(record.event_id) for record in registry.transition_log)


def test_public_wallet_and_lifecycle_runtime_still_expose_deferred_claimability_only() -> None:
    lifecycle_source = LIFECYCLE_RUNTIME_PATH.read_text(encoding="utf-8")
    wallet_source = PUBLIC_WALLET_RUNTIME_PATH.read_text(encoding="utf-8")

    assert '"claimability_state": "deferred"' in lifecycle_source
    assert '"claimability_state": "deferred"' in wallet_source

    public_methods = {
        name
        for name in dir(PublicWalletRuntime)
        if not name.startswith("_") and callable(getattr(PublicWalletRuntime, name))
    }
    assert public_methods == {
        "ledger_summary",
        "wallet_export",
        "wallet_history",
        "wallet_status",
    }
    assert not any(
        forbidden in name
        for name in public_methods
        for forbidden in ("claim", "withdraw", "redeem", "spend", "transfer")
    )


def test_phase_1252_graph_delta_is_recorded() -> None:
    text = _spec_text()

    assert "graph_delta=load_bearing_spec_added:docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md -> ecu/ilc/public_rc" in text
    assert "graph_delta=load_bearing_code_changed:ilc_core/ledger/settlement_verification.py -> ecu/ilc/security" in text
    assert "graph_delta=load_bearing_code_changed:ilc_core/security/key_compromise_runtime.py -> security" in text
    assert "graph_delta=load_bearing_code_changed:ilc_core/security/signer_lineage_runtime.py -> security" in text
