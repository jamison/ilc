from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.rc.package_profiles import PROFILE_OPENCLAW_SKILL_CLAIMABLE, profile_manifest
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest
from ilc_core.sidecars.value_path_activation_boundary_preflight import (
    ECU_MINTING_NOT_AUTHORIZED_TOKEN,
    ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
    PHASE_1316_NEXT_TOKEN,
    PREFLIGHT_REF_PREFIX,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1315_TOKEN,
    VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION,
    VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN,
    ValuePathActivationBoundaryPreflightError,
    build_value_path_activation_boundary_preflight_packet,
    export_value_path_activation_boundary_preflight_json,
    validate_value_path_activation_boundary_preflight_packet,
    value_path_activation_boundary_preflight_manifest,
    value_path_activation_boundary_preflight_ref,
    value_path_activation_boundary_preflight_required_tokens,
)
from ilc_core.sidecars.wallet_action_semantics_preflight import (
    WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/value_path_activation_boundary_preflight.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
PACKAGE_PROFILES_PATH = ROOT / "ilc_core/rc/package_profiles.py"
LIFECYCLE_PATH = ROOT / "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py"
GUARDRAIL_PATH = ROOT / "tools/check_sensitive_runtime_coding_taboos.py"
SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_ecu_minting_ilc_settlement_boundary_preflight_1315_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1315_ecu_minting_ilc_settlement_boundary_preflight_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
NETWORK_PLAN_PATH = (
    ROOT / "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md"
)
ARCHITECTURE_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"
REGISTRY_SPEC_PATH = ROOT / "docs/specs/ilc_graph_native_sidecar_registry_manifest_1307_v0.1.md"

REQUIRED_TOKENS = [
    VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION,
    ECU_MINTING_NOT_AUTHORIZED_TOKEN,
    ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
    VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN,
    PHASE_1316_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1315_TOKEN,
]


def _packet() -> dict:
    return build_value_path_activation_boundary_preflight_packet(current_epoch=1315)


def test_phase_1315_value_path_boundary_packet_is_deterministic() -> None:
    packet = _packet()
    exported_once = export_value_path_activation_boundary_preflight_json(packet)
    exported_twice = export_value_path_activation_boundary_preflight_json(packet)

    assert value_path_activation_boundary_preflight_required_tokens() == REQUIRED_TOKENS
    assert packet["version"] == VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION
    assert packet["tokens"] == REQUIRED_TOKENS
    assert packet["local_only"] is True
    assert packet["preflight_only"] is True
    assert packet["readiness_verdict"] == "preflight_recorded_value_path_activation_blocked"
    assert packet["next_phase"] == PHASE_1316_NEXT_TOKEN
    assert packet["permitted_local_read_substrates"] == [
        "ecu_active_layer_read",
        "ecu_ilc_lifecycle_status",
        "wallet_status",
        "wallet_history",
        "wallet_export",
        "ledger_summary",
        "offline_claimability_receipt_verifier",
        "wallet_action_semantics_preflight",
    ]
    boundary = packet["ledger_truth_boundary"]
    assert boundary["boundary_token"] == VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN
    assert boundary["ledger_truth_boundary_token"] == (
        WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN
    )
    assert boundary["ecu_mint_instruction_constructed"] is False
    assert boundary["ilc_settlement_instruction_constructed"] is False
    assert boundary["withdrawal_runtime_constructed"] is False
    assert boundary["ledger_mutation_emitted"] is False
    assert boundary["wallet_provider_role"] == "adapter_or_sidecar_not_truth_source"
    assert all(value is False for value in packet["authorization_flags"].values())
    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        json.loads(exported_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert value_path_activation_boundary_preflight_ref(packet).startswith(
        f"{PREFLIGHT_REF_PREFIX}:"
    )


def test_phase_1315_value_path_activation_flags_fail_closed() -> None:
    cases = [
        ("ecu_mint_authorized", ECU_MINTING_NOT_AUTHORIZED_TOKEN),
        ("ecu_creation_enabled", ECU_MINTING_NOT_AUTHORIZED_TOKEN),
        ("ecu_supply_policy_authorized", ECU_MINTING_NOT_AUTHORIZED_TOKEN),
        ("ilc_settlement_authorized", ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN),
        ("ilc_transfer_enabled", ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN),
        ("ilc_settlement_root_authorized", ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN),
        ("withdrawal_runtime_enabled", ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN),
        ("withdrawal_endpoint_enabled", ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN),
        ("wallet_write_authorized", "value_path_activation_authority_forbidden_phase_1315"),
        ("wallet_signing_authorized", "value_path_activation_authority_forbidden_phase_1315"),
        ("wallet_ledger_write_authorized", "value_path_activation_authority_forbidden_phase_1315"),
        ("public_claimability_activated", "value_path_activation_authority_forbidden_phase_1315"),
        ("public_claim_endpoint_enabled", "value_path_activation_authority_forbidden_phase_1315"),
        ("public_verifier_service_enabled", "value_path_activation_authority_forbidden_phase_1315"),
        ("external_chain_bridge_enabled", "value_path_activation_authority_forbidden_phase_1315"),
        ("release_artifact_authorized", "value_path_activation_authority_forbidden_phase_1315"),
        ("release_key_material_authorized", "value_path_activation_authority_forbidden_phase_1315"),
        ("cdl088_opened", "value_path_activation_authority_forbidden_phase_1315"),
    ]
    for field, token in cases:
        with pytest.raises(ValuePathActivationBoundaryPreflightError) as exc:
            build_value_path_activation_boundary_preflight_packet(
                current_epoch=1315,
                **{field: True},
            )
        assert exc.value.token == token


def test_phase_1315_validation_rejects_mutated_boundaries_and_hash_drift() -> None:
    packet = _packet()

    mutated = copy.deepcopy(packet)
    mutated["authorization_flags"]["ecu_mint_authorized"] = True
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as mint_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert mint_exc.value.token == ECU_MINTING_NOT_AUTHORIZED_TOKEN

    mutated = copy.deepcopy(packet)
    mutated["authorization_flags"]["ilc_settlement_authorized"] = True
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as settle_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert settle_exc.value.token == ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN

    mutated = copy.deepcopy(packet)
    mutated["permitted_local_read_substrates"].append("ecu_mint")
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as substrates_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert substrates_exc.value.token == (
        "value_path_activation_boundary_permitted_substrates_invalid_phase_1315"
    )

    mutated = copy.deepcopy(packet)
    mutated["prohibited_value_path_actions"].remove("ilc_settlement_execution")
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as actions_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert actions_exc.value.token == (
        "value_path_activation_boundary_prohibited_actions_invalid_phase_1315"
    )

    mutated = copy.deepcopy(packet)
    mutated["ledger_truth_boundary"]["ledger_mutation_emitted"] = True
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as boundary_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert boundary_exc.value.token == (
        "value_path_activation_boundary_ledger_truth_invalid_phase_1315"
    )

    mutated = copy.deepcopy(packet)
    mutated["required_before_value_path_activation"].append("optional_activation")
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as req_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert req_exc.value.token == (
        "value_path_activation_boundary_requirements_invalid_phase_1315"
    )

    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["phase_1315_scope"] = "settlement_enabled"
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as source_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert source_exc.value.token == (
        "value_path_activation_boundary_source_evidence_invalid_phase_1315"
    )

    mutated = copy.deepcopy(packet)
    mutated["candidate_sha256"] = "0" * 64
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as hash_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert hash_exc.value.token == (
        "value_path_activation_boundary_candidate_hash_mismatch_phase_1315"
    )


def test_phase_1315_rejects_non_json_float_cycle_and_invalid_text_inputs() -> None:
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as epoch_exc:
        build_value_path_activation_boundary_preflight_packet(current_epoch=1.0)  # type: ignore[arg-type]
    assert epoch_exc.value.token == "value_path_activation_boundary_current_epoch_invalid_phase_1315"

    packet = _packet()
    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["float"] = 1.0
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as float_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert float_exc.value.token == (
        "value_path_activation_boundary_float_values_forbidden_phase_1315"
    )

    cyclic: dict = {}
    cyclic["self"] = cyclic
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as cycle_exc:
        validate_value_path_activation_boundary_preflight_packet(cyclic)
    assert cycle_exc.value.token == (
        "value_path_activation_boundary_payload_cycle_forbidden_phase_1315"
    )

    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["bad"] = " leading"
    with pytest.raises(ValuePathActivationBoundaryPreflightError) as text_exc:
        validate_value_path_activation_boundary_preflight_packet(mutated)
    assert text_exc.value.token == "value_path_activation_boundary_text_invalid_phase_1315"


def test_phase_1315_registry_and_package_profiles_record_value_path_boundary() -> None:
    manifest = value_path_activation_boundary_preflight_manifest()
    registry = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in registry["sidecars"]}
    value_path = sidecars["value_path_activation_boundary_preflight"]
    claimable = {
        profile["profile_id"]: profile for profile in registry["profiles"]
    }["openclaw_claimable_local_bridge"]
    integrity = registry["package_profile_integrity"][
        "value_path_activation_boundary_preflight_manifest"
    ]
    package = profile_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)

    assert manifest["contract_version"] == VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION
    assert manifest["preflight_only"] is True
    assert manifest["ecu_mint_authorized"] is False
    assert manifest["ilc_settlement_authorized"] is False
    assert manifest["withdrawal_runtime_enabled"] is False
    assert manifest["wallet_write_authorized"] is False
    assert value_path["authority_gate"] == (
        "phase_1315_preflight_only_value_path_activation_blocked"
    )
    assert value_path["public_serving_enabled"] is False
    for token in REQUIRED_TOKENS[1:]:
        assert token in value_path["required_capabilities"]
    assert "value_path_activation_boundary_preflight" in claimable["required_sidecars"]
    assert "value_path_activation_boundary_preflight_sidecar" in package["components"]
    assert integrity == manifest


def test_phase_1315_lifecycle_settlement_runtime_remains_existing_but_not_activated() -> None:
    runtime_methods = {
        name
        for name, value in EcuIlcLifecycleRuntime.__dict__.items()
        if callable(value) and not name.startswith("_")
    }
    assert "commit_settled_epoch" in runtime_methods

    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "commit_settled_epoch(" not in source
    assert "put_wallet(" not in source
    assert "put_wallet_history(" not in source

    lifecycle_source = LIFECYCLE_PATH.read_text(encoding="utf-8")
    assert "def commit_settled_epoch" in lifecycle_source
    assert "claimability_state\": \"deferred\"" in lifecycle_source


def test_phase_1315_source_has_no_network_server_clock_or_public_rc_exclude_surface() -> None:
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
    assert "ilc_core/sidecars/value_path_activation_boundary_preflight.py" in (
        GUARDRAIL_PATH.read_text(encoding="utf-8")
    )


def test_phase_1315_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
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
            REGISTRY_SPEC_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for non_claim in (
        "no ECU minting",
        "no ILC settlement",
        "no withdrawal runtime",
        "no wallet-facing withdrawal request",
        "no wallet-facing transfer request",
        "no wallet-facing spend request",
        "no wallet-provider signing request",
        "no wallet-provider ledger-write request",
        "no public claim endpoint",
        "no public claimability activation",
        "no value-path activation",
        "wallet-provider agnostic but not ledger-truth agnostic",
        "Phase 1316 is sensitive and requires explicit `GO Phase 1316`",
    ):
        assert non_claim in corpus
