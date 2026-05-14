import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs/specs/ilc_wallet_ecu_ilc_activation_or_carry_forward_gate_1338_v0.1.json"
REPORT_MD_PATH = ROOT / "docs/specs/ilc_wallet_ecu_ilc_activation_or_carry_forward_gate_1338_v0.1.md"
WALKTHROUGH_PATH = ROOT / "docs/phases/phase_1338_wallet_ecu_ilc_activation_or_carry_forward_gate_walkthrough.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
WINDOW_PLAN_PATH = ROOT / "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN_PATH = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)


REQUIRED_TOKENS = {
    "wallet_ecu_ilc_activation_or_carry_forward_gate_phase_1338.v0.1",
    "wallet_provider_adapter_boundary_preserved_phase_1338",
    "ecu_minting_requires_explicit_authority_phase_1338",
    "ilc_settlement_requires_explicit_authority_phase_1338",
    "phase_1339_atlas_g_mutation_regeneration_finalization_next",
    "public_rc_remains_blocked_after_phase_1338",
}

EXPECTED_SUBPATHS = {
    "wallet_facing_withdrawal_request",
    "wallet_facing_transfer_request",
    "wallet_facing_spend_request",
    "wallet_provider_signing_request",
    "wallet_provider_ledger_write",
    "wallet_write",
    "withdrawal_runtime",
    "ecu_minting",
    "ecu_creation",
    "ecu_supply_policy_mutation",
    "ilc_settlement",
    "ilc_transfer",
    "settlement_root_publication",
    "public_claim_endpoint_dependency",
    "value_path_activation",
}

EXPECTED_BLOCKERS = {
    "explicit_value_path_activation_authority_missing",
    "public_claimability_api_not_activated",
    "replay_nullifier_duplicate_claim_policy_not_activated",
    "cdl_088_not_opened_or_ratified",
    "wallet_provider_signing_payload_contract_missing",
    "wallet_ledger_write_authority_and_replay_policy_missing",
    "ecu_mint_policy_and_supply_invariant_missing",
    "ilc_settlement_authority_replay_policy_missing",
    "settlement_root_namespace_binding_contract_missing",
    "withdrawal_runtime_contract_missing",
    "atlas_g_signing_publication_preconditions_not_closed",
    "public_rc_publication_claim_not_authorized",
}


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text())


def test_phase_1338_report_records_carry_forward_verdict() -> None:
    report = _report()

    assert report["schema_version"] == "wallet_ecu_ilc_activation_or_carry_forward_gate_phase_1338.v0.1"
    assert report["result"] == "carry_forward_no_activation"
    assert report["wallet_ecu_ilc_activation_or_carry_forward_gate_verdict"] == (
        "wallet_ecu_ilc_activation_or_carry_forward_gate_verdict=carry_forward_no_activation"
    )
    assert set(report["required_tokens"]) == REQUIRED_TOKENS
    assert report["next_phase"] == "phase_1339_atlas_g_mutation_regeneration_finalization_next"
    assert report["public_rc_remains_blocked"] is True
    assert report["authority_decision"]["gate_execution_authorized_by_go_phase_1338"] is True
    assert report["authority_decision"]["explicit_value_path_activation_authority_present"] is False
    assert report["authority_decision"]["wallet_provider_adapter_boundary_preserved"] is True


def test_phase_1338_manifest_hash_is_stable() -> None:
    report = _report()
    stored = report["manifest_hash"]
    report["manifest_hash"] = ""
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

    assert hashlib.sha256(canonical).hexdigest() == stored


def test_phase_1338_carries_forward_all_value_subpaths() -> None:
    rows = {row["subpath"]: row for row in _report()["subpath_decision_table"]}

    assert set(rows) == EXPECTED_SUBPATHS
    for subpath, row in rows.items():
        assert row["status"] == "carry_forward_no_activation", subpath
        assert row["authorized"] is False, subpath

    assert rows["ecu_minting"]["reason"] == "ecu_minting_requires_explicit_authority_phase_1338"
    assert rows["ilc_settlement"]["reason"] == "ilc_settlement_requires_explicit_authority_phase_1338"
    assert rows["wallet_facing_withdrawal_request"]["reason"] == (
        "wallet_provider_adapter_boundary_preserved_phase_1338"
    )


def test_phase_1338_non_authorization_floor_is_all_false() -> None:
    non_auth = _report()["non_authorization_floor"]

    for key, value in non_auth.items():
        assert value is False, key


def test_phase_1338_records_expected_blockers() -> None:
    report = _report()
    blockers = {item["blocker_id"]: item for item in report["blockers"]}

    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(item["status"] == "open" for item in blockers.values())
    assert blockers["explicit_value_path_activation_authority_missing"]["carry_forward_route"] == (
        "wallet_ecu_ilc_full_activation_deferred_window_1357_plus"
    )
    assert blockers["cdl_088_not_opened_or_ratified"]["carry_forward_route"] == (
        "phase_1349_to_1351_cdl_088_open_deliberate_ratify"
    )


def test_phase_1338_records_exact_numeric_safety_boundary() -> None:
    checks = _report()["exact_numeric_safety_checks"]

    assert checks["runtime_code_changed"] is False
    assert checks["float_economics_introduced_by_phase_1338"] is False
    assert checks["non_finite_decimal_allowed_by_exact_numeric_boundary"] is False
    assert any("rejects bool, float" in item for item in checks["source_evidence"])


def test_phase_1338_reports_and_frontier_docs_carry_tokens() -> None:
    combined = "\n".join(
        path.read_text()
        for path in (
            REPORT_PATH,
            REPORT_MD_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            WINDOW_PLAN_PATH,
            FORWARD_PLAN_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in combined

    assert "phase_1338_status=complete_carry_forward_no_activation" in combined
    assert "wallet_ecu_ilc_activation_or_carry_forward_gate_verdict=carry_forward_no_activation" in combined
    assert "phase_1339_atlas_g_mutation_regeneration_finalization_next" in combined
    assert "wallet_ecu_ilc_full_activation_deferred_window_1357_plus" in combined
