from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime
from ilc_core.rc.package_profiles import PROFILE_OPENCLAW_SKILL_CLAIMABLE, profile_manifest
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest
from ilc_core.sidecars.wallet_action_semantics_preflight import (
    PHASE_1315_NEXT_TOKEN,
    PREFLIGHT_REF_PREFIX,
    PUBLIC_CLAIMABILITY_USER_ACTION_BOUNDARY_RECORDED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1314_TOKEN,
    WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
    WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN,
    WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
    WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
    WalletActionSemanticsPreflightError,
    build_wallet_action_semantics_preflight_packet,
    export_wallet_action_semantics_preflight_json,
    validate_wallet_action_semantics_preflight_packet,
    wallet_action_semantics_preflight_manifest,
    wallet_action_semantics_preflight_ref,
    wallet_action_semantics_preflight_required_tokens,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/wallet_action_semantics_preflight.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
PUBLIC_WALLET_PATH = ROOT / "ilc_core/protocol/public_wallet_runtime.py"
PACKAGE_PROFILES_PATH = ROOT / "ilc_core/rc/package_profiles.py"
GUARDRAIL_PATH = ROOT / "tools/check_sensitive_runtime_coding_taboos.py"
SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1314_wallet_withdrawal_transfer_spend_semantics_preflight_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
NETWORK_PLAN_PATH = (
    ROOT / "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md"
)
ARCHITECTURE_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"

REQUIRED_TOKENS = [
    WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
    WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
    WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
    PUBLIC_CLAIMABILITY_USER_ACTION_BOUNDARY_RECORDED_TOKEN,
    PHASE_1315_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1314_TOKEN,
]


def _packet() -> dict:
    return build_wallet_action_semantics_preflight_packet(current_epoch=1314)


def test_phase_1314_wallet_action_preflight_packet_is_deterministic() -> None:
    packet = _packet()
    exported_once = export_wallet_action_semantics_preflight_json(packet)
    exported_twice = export_wallet_action_semantics_preflight_json(packet)

    assert wallet_action_semantics_preflight_required_tokens() == REQUIRED_TOKENS
    assert packet["version"] == WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION
    assert packet["tokens"] == REQUIRED_TOKENS
    assert packet["local_only"] is True
    assert packet["preflight_only"] is True
    assert packet["readiness_verdict"] == "preflight_recorded_wallet_actions_blocked"
    assert packet["next_phase"] == PHASE_1315_NEXT_TOKEN
    assert packet["permitted_wallet_query_operations"] == [
        "wallet_status",
        "wallet_history",
        "wallet_export",
        "ledger_summary",
    ]
    assert packet["user_action_boundary"]["signature_payload_constructed"] is False
    assert packet["user_action_boundary"]["ledger_mutation_emitted"] is False
    assert (
        packet["user_action_boundary"]["ledger_truth_boundary_token"]
        == WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN
    )
    assert packet["user_action_boundary"]["wallet_provider_role"] == (
        "adapter_or_sidecar_not_truth_source"
    )
    assert all(value is False for value in packet["authorization_flags"].values())
    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        json.loads(exported_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert wallet_action_semantics_preflight_ref(packet).startswith(
        f"{PREFLIGHT_REF_PREFIX}:"
    )


def test_phase_1314_wallet_activation_flags_fail_closed() -> None:
    cases = [
        ("wallet_withdrawal_enabled", WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN),
        ("wallet_transfer_enabled", WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN),
        ("wallet_spend_enabled", WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN),
        ("wallet_signing_authorized", WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN),
        ("wallet_ledger_write_authorized", WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN),
        ("public_claimability_activated", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("public_claim_endpoint_enabled", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("withdrawal_endpoint_enabled", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("transfer_endpoint_enabled", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("spend_endpoint_enabled", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("external_chain_bridge_enabled", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("withdrawal_runtime_enabled", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("ecu_mint_authorized", "wallet_action_semantics_activation_forbidden_phase_1314"),
        ("ilc_settlement_authorized", "wallet_action_semantics_activation_forbidden_phase_1314"),
    ]
    for field, token in cases:
        with pytest.raises(WalletActionSemanticsPreflightError) as exc:
            build_wallet_action_semantics_preflight_packet(current_epoch=1314, **{field: True})
        assert exc.value.token == token


def test_phase_1314_validation_rejects_mutated_actions_and_hash_drift() -> None:
    packet = _packet()

    mutated = copy.deepcopy(packet)
    mutated["authorization_flags"]["wallet_spend_enabled"] = True
    with pytest.raises(WalletActionSemanticsPreflightError) as exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert exc.value.token == WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN

    mutated = copy.deepcopy(packet)
    mutated["authorization_flags"]["wallet_signing_authorized"] = True
    with pytest.raises(WalletActionSemanticsPreflightError) as sign_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert sign_exc.value.token == WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN

    mutated = copy.deepcopy(packet)
    mutated["permitted_wallet_query_operations"].append("wallet_withdraw")
    with pytest.raises(WalletActionSemanticsPreflightError) as ops_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert ops_exc.value.token == (
        "wallet_action_semantics_permitted_operations_invalid_phase_1314"
    )

    mutated = copy.deepcopy(packet)
    mutated["prohibited_user_value_actions"].remove("spend_request")
    with pytest.raises(WalletActionSemanticsPreflightError) as actions_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert actions_exc.value.token == (
        "wallet_action_semantics_prohibited_actions_invalid_phase_1314"
    )

    mutated = copy.deepcopy(packet)
    mutated["user_action_boundary"]["signature_payload_constructed"] = True
    with pytest.raises(WalletActionSemanticsPreflightError) as boundary_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert boundary_exc.value.token == "wallet_action_semantics_user_boundary_invalid_phase_1314"

    mutated = copy.deepcopy(packet)
    mutated["required_before_wallet_action_activation"].append("optional_activation")
    with pytest.raises(WalletActionSemanticsPreflightError) as req_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert req_exc.value.token == "wallet_action_semantics_requirements_invalid_phase_1314"

    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["phase_617_public_wallet_surface"] = "write_enabled"
    with pytest.raises(WalletActionSemanticsPreflightError) as source_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert source_exc.value.token == "wallet_action_semantics_source_evidence_invalid_phase_1314"

    mutated = copy.deepcopy(packet)
    mutated["candidate_sha256"] = "0" * 64
    with pytest.raises(WalletActionSemanticsPreflightError) as hash_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert hash_exc.value.token == (
        "wallet_action_semantics_candidate_hash_mismatch_phase_1314"
    )


def test_phase_1314_rejects_non_json_float_cycle_and_invalid_text_inputs() -> None:
    with pytest.raises(WalletActionSemanticsPreflightError) as epoch_exc:
        build_wallet_action_semantics_preflight_packet(current_epoch=1.0)  # type: ignore[arg-type]
    assert epoch_exc.value.token == "wallet_action_semantics_current_epoch_invalid_phase_1314"

    packet = _packet()
    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["float"] = 1.0
    with pytest.raises(WalletActionSemanticsPreflightError) as float_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert float_exc.value.token == "wallet_action_semantics_float_values_forbidden_phase_1314"

    cyclic: dict = {}
    cyclic["self"] = cyclic
    with pytest.raises(WalletActionSemanticsPreflightError) as cycle_exc:
        validate_wallet_action_semantics_preflight_packet(cyclic)
    assert cycle_exc.value.token == "wallet_action_semantics_payload_cycle_forbidden_phase_1314"

    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["bad"] = " leading"
    with pytest.raises(WalletActionSemanticsPreflightError) as text_exc:
        validate_wallet_action_semantics_preflight_packet(mutated)
    assert text_exc.value.token == "wallet_action_semantics_text_invalid_phase_1314"


def test_phase_1314_registry_and_package_profiles_record_wallet_action_boundary() -> None:
    manifest = wallet_action_semantics_preflight_manifest()
    registry = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in registry["sidecars"]}
    wallet_actions = sidecars["wallet_action_semantics_preflight"]
    claimable = {
        profile["profile_id"]: profile for profile in registry["profiles"]
    }["openclaw_claimable_local_bridge"]
    integrity = registry["package_profile_integrity"][
        "wallet_action_semantics_preflight_manifest"
    ]
    package = profile_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)

    assert manifest["contract_version"] == WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION
    assert manifest["preflight_only"] is True
    assert manifest["wallet_withdrawal_enabled"] is False
    assert manifest["wallet_transfer_enabled"] is False
    assert manifest["wallet_spend_enabled"] is False
    assert manifest["wallet_signing_authorized"] is False
    assert manifest["wallet_ledger_write_authorized"] is False
    assert wallet_actions["authority_gate"] == "phase_1314_preflight_only_wallet_actions_blocked"
    assert wallet_actions["public_serving_enabled"] is False
    for token in REQUIRED_TOKENS[1:]:
        assert token in wallet_actions["required_capabilities"]
    assert "wallet_action_semantics_preflight" in claimable["required_sidecars"]
    assert "wallet_action_semantics_preflight_sidecar" in package["components"]
    assert integrity == manifest


def test_phase_1314_public_wallet_runtime_remains_read_only() -> None:
    runtime_methods = {
        name
        for name, value in PublicWalletRuntime.__dict__.items()
        if callable(value) and not name.startswith("_")
    }
    assert runtime_methods == {
        "wallet_status",
        "wallet_history",
        "wallet_export",
        "ledger_summary",
    }

    source = PUBLIC_WALLET_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "def wallet_withdraw",
        "def wallet_transfer",
        "def wallet_spend",
        "def sign",
        "def ledger_write",
    ):
        assert forbidden not in source


def test_phase_1314_source_has_no_network_server_or_clock_surface() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_roots = {
        "aiohttp",
        "datetime",
        "fastapi",
        "http",
        "random",
        "requests",
        "socket",
        "time",
        "urllib",
        "uvicorn",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_roots

    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "PUBLIC_RC_EXCLUDE" not in source
    assert "ilc_core/sidecars/wallet_action_semantics_preflight.py" in (
        GUARDRAIL_PATH.read_text(encoding="utf-8")
    )


def test_phase_1314_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MODULE_PATH,
            REGISTRY_PATH,
            PACKAGE_PROFILES_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            NETWORK_PLAN_PATH,
            ARCHITECTURE_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    assert WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN in corpus
    for non_claim in (
        "no wallet-facing withdrawal request",
        "no wallet-facing transfer request",
        "no wallet-facing spend request",
        "no wallet-provider signing request",
        "no wallet-provider ledger-write request",
        "no public claim endpoint",
        "no ECU minting",
        "no ILC settlement",
        "wallet-provider agnostic but not ledger-truth agnostic",
        "optional sidecar recipe",
        "Phase 1315 is sensitive and requires explicit `GO Phase 1315`",
    ):
        assert non_claim in corpus
