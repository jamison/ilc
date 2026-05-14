import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs/specs/ilc_public_path_sidecar_activation_or_exclusion_gate_1337_v0.1.json"
REPORT_MD_PATH = ROOT / "docs/specs/ilc_public_path_sidecar_activation_or_exclusion_gate_1337_v0.1.md"
WALKTHROUGH_PATH = ROOT / "docs/phases/phase_1337_public_path_sidecar_activation_or_exclusion_gate_walkthrough.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
WINDOW_PLAN_PATH = ROOT / "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN_PATH = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)


REQUIRED_TOKENS = {
    "public_path_sidecar_activation_or_exclusion_gate_phase_1337.v0.1",
    "transport_principal_public_path_requires_explicit_authority_phase_1337",
    "public_sidecar_projection_serving_requires_explicit_authority_phase_1337",
    "public_confidential_coordination_serving_requires_explicit_authority_phase_1337",
    "phase_1338_wallet_ecu_ilc_activation_gate_next",
    "public_rc_remains_blocked_after_phase_1337",
}

EXPECTED_BLOCKERS = {
    "explicit_public_path_authority_missing",
    "rust_public_p2p_substrate_gate_not_satisfied",
    "transport_principal_public_path_not_authorized",
    "public_bind_listener_peer_discovery_not_authorized",
    "public_sidecar_projection_serving_not_authorized",
    "public_confidential_coordination_serving_not_selected",
    "atlas_g_signing_publication_preconditions_not_closed",
    "source_publication_release_public_rc_claim_not_authorized",
}

EXPECTED_SURFACES = {
    "transport_principal_public_path",
    "public_p2p",
    "public_fetch_serving",
    "public_sidecar_projection_serving",
    "public_confidential_coordination_serving",
    "public_listener",
    "peer_discovery",
    "non_loopback_bind",
}


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text())


def test_phase_1337_report_records_exclusion_verdict() -> None:
    report = _report()

    assert report["schema_version"] == "public_path_sidecar_activation_or_exclusion_gate_phase_1337.v0.1"
    assert report["result"] == "excluded_from_first_rc"
    assert report["public_path_sidecar_activation_or_exclusion_gate_verdict"] == (
        "public_path_sidecar_activation_or_exclusion_gate_verdict=excluded_from_first_rc"
    )
    assert set(report["required_tokens"]) == REQUIRED_TOKENS
    assert report["next_phase"] == "phase_1338_wallet_ecu_ilc_activation_gate_next"
    assert report["public_rc_remains_blocked"] is True
    assert report["authority_decision"]["gate_execution_authorized_by_go_phase_1337"] is True
    assert report["authority_decision"]["explicit_public_path_activation_authority_present"] is False


def test_phase_1337_manifest_hash_is_stable() -> None:
    report = _report()
    stored = report["manifest_hash"]
    report["manifest_hash"] = ""
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

    assert hashlib.sha256(canonical).hexdigest() == stored


def test_phase_1337_excludes_all_public_path_surfaces() -> None:
    report = _report()
    rows = {row["surface"]: row for row in report["public_path_decision_table"]}

    assert set(rows) == EXPECTED_SURFACES
    for surface, row in rows.items():
        assert row["status"] == "excluded_from_first_rc", surface
        assert row["public_serving_enabled"] is False, surface

    assert rows["transport_principal_public_path"]["reason"] == (
        "transport_principal_public_path_requires_explicit_authority_phase_1337"
    )
    assert rows["public_sidecar_projection_serving"]["reason"] == (
        "public_sidecar_projection_serving_requires_explicit_authority_phase_1337"
    )
    assert rows["public_confidential_coordination_serving"]["reason"] == (
        "public_confidential_coordination_serving_requires_explicit_authority_phase_1337"
    )


def test_phase_1337_non_authorization_floor_is_all_false() -> None:
    non_auth = _report()["non_authorization_floor"]

    for key, value in non_auth.items():
        assert value is False, key


def test_phase_1337_records_expected_blockers() -> None:
    report = _report()
    blockers = {item["blocker_id"]: item for item in report["blockers"]}

    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(item["status"] == "open" for item in blockers.values())
    assert blockers["rust_public_p2p_substrate_gate_not_satisfied"]["carry_forward_route"] == (
        "public_p2p_sidecar_serving_deferred_window_1357_plus_pending_rust_p2p_adr"
    )
    assert blockers["public_confidential_coordination_serving_not_selected"]["carry_forward_route"] == (
        "post_claimability_or_dedicated_ccss_public_serving_window_if_selected"
    )


def test_phase_1337_reports_and_frontier_docs_carry_tokens() -> None:
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

    assert "phase_1337_status=complete_excluded_from_first_rc" in combined
    assert "public_path_sidecar_activation_or_exclusion_gate_verdict=excluded_from_first_rc" in combined
    assert "phase_1338_wallet_ecu_ilc_activation_gate_next" in combined
    assert "public_p2p_sidecar_serving_deferred_window_1357_plus_pending_rust_p2p_adr" in combined
