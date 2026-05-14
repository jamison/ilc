import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.json"
REPORT_MD_PATH = ROOT / "docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.md"
WALKTHROUGH_PATH = (
    ROOT / "docs/phases/phase_1336_public_claimability_api_activation_or_carry_forward_gate_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
WINDOW_PLAN_PATH = ROOT / "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN_PATH = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)


REQUIRED_TOKENS = {
    "public_claimability_api_activation_or_carry_forward_gate_phase_1336.v0.1",
    "public_claimability_requires_explicit_authority_phase_1336",
    "claimability_replay_nullifier_policy_checked_phase_1336",
    "wallet_value_actions_still_separate_gate_phase_1336",
    "phase_1337_public_path_sidecar_activation_or_exclusion_gate_next",
    "public_rc_remains_blocked_after_phase_1336",
}


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text())


def test_phase_1336_report_records_no_claim_carry_forward() -> None:
    report = _report()

    assert report["schema_version"] == "public_claimability_api_activation_or_carry_forward_gate_phase_1336.v0.1"
    assert report["result"] == "no_claim_carry_forward"
    assert (
        report["public_claimability_api_activation_or_carry_forward_gate_verdict"]
        == "public_claimability_api_activation_or_carry_forward_gate_verdict=no_claim_carry_forward"
    )
    assert set(report["required_tokens"]) == REQUIRED_TOKENS
    assert report["next_phase"] == "phase_1337_public_path_sidecar_activation_or_exclusion_gate_next"
    assert report["public_rc_remains_blocked"] is True


def test_phase_1336_manifest_hash_is_stable() -> None:
    report = _report()
    stored = report["manifest_hash"]
    report["manifest_hash"] = ""
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

    assert hashlib.sha256(canonical).hexdigest() == stored


def test_phase_1336_does_not_activate_public_surfaces_or_wallet_value_paths() -> None:
    report = _report()

    assert report["authority_decision"]["gate_execution_authorized_by_go_phase_1336"] is True
    assert report["authority_decision"]["explicit_public_claimability_activation_authority_present"] is False

    for row in report["endpoint_public_path_table"]:
        assert row["status"] == "not_activated"
        assert row["public_route_added"] is False
        assert row["non_loopback_bind_created"] is False

    assert report["local_substrate_status"]["public_api_enabled"] is False
    assert report["local_substrate_status"]["public_claimability_activated"] is False
    assert report["local_substrate_status"]["public_verifier_service_enabled"] is False
    assert report["local_substrate_status"]["public_claim_endpoint_enabled"] is False

    non_auth = report["non_authorization_floor"]
    for key, value in non_auth.items():
        assert value is False, key

    value_status = report["wallet_value_actions_status"]
    for key, value in value_status.items():
        if key == "token":
            continue
        assert value is False, key


def test_phase_1336_records_required_blockers_and_routes() -> None:
    report = _report()
    blockers = {item["blocker_id"]: item for item in report["blockers"]}

    expected = {
        "explicit_public_claimability_authority_missing",
        "replay_nullifier_policy_not_activated",
        "duplicate_claim_registry_not_activated",
        "cdl_088_not_opened_or_ratified",
        "genesis_rooted_agent_birth_attestation_unspecified",
        "identity_bootstrap_adr_cdl_not_ratified",
        "legacy_v1_public_fastapi_routes_not_cleaned",
        "public_verifier_api_counsel_clearance_missing",
    }

    assert set(blockers) == expected
    assert all(item["status"] == "open" for item in blockers.values())
    assert blockers["replay_nullifier_policy_not_activated"]["carry_forward_route"] == (
        "phase_1352_replay_nullifier_duplicate_claim_policy"
    )
    assert blockers["cdl_088_not_opened_or_ratified"]["carry_forward_route"] == (
        "phase_1349_to_1351_cdl_088_open_deliberate_ratify"
    )
    assert blockers["genesis_rooted_agent_birth_attestation_unspecified"]["carry_forward_route"] == (
        "phase_1345_agent_birth_attestation_adr"
    )


def test_phase_1336_reports_and_frontier_docs_carry_tokens() -> None:
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

    assert "phase_1336_status=complete_no_claim_carry_forward" in combined
    assert "phase_1337_public_path_sidecar_activation_or_exclusion_gate_next" in combined
    assert "public_claimability_api_activation_or_carry_forward_gate_verdict=no_claim_carry_forward" in combined
    assert "public_claimability_api_revised_gate_routed_window_1343_plus" in combined
