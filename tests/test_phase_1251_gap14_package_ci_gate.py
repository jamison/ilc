import json
from pathlib import Path

import pytest

from ilc_core.rc.package_profile_ci_gate import (
    GAP14_PACKAGE_CI_GATE_VERSION,
    PACKAGE_PROFILE_AUDIT_FILE_SUFFIXES,
    PHASE_1250_FIX1_CARRY_FORWARD_ROUTES,
    PHASE_1250_FIX1_CONSUMED_FINDINGS,
    PHASE_1251_GAP14_PACKAGE_CI_PROFILE_AUDIT_COMPLETE_TOKEN,
    PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN,
    SELECTED_GAP14_PROFILE_IDS,
    build_package_profile_ci_audit,
    export_package_profile_ci_audit_json,
    render_package_profile_ci_audit_markdown,
    validate_package_profile_ci_audit,
)
from ilc_core.rc.package_profiles import (
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
)


ARTIFACT_JSON = Path("docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json")
ARTIFACT_MD = Path("docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md")


def test_phase_1251_required_tokens_are_exported() -> None:
    audit = build_package_profile_ci_audit()

    assert audit["version"] == GAP14_PACKAGE_CI_GATE_VERSION
    assert audit["public_package_size_audit_token"] == PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN
    assert audit["required_tokens"] == [
        GAP14_PACKAGE_CI_GATE_VERSION,
        PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN,
        PHASE_1251_GAP14_PACKAGE_CI_PROFILE_AUDIT_COMPLETE_TOKEN,
    ]


def test_phase_1251_selected_profiles_pass_gate_without_public_p2p_claims() -> None:
    audit = validate_package_profile_ci_audit()

    assert audit["audit_status"] == "pass"
    assert tuple(audit["selected_profile_ids"]) == SELECTED_GAP14_PROFILE_IDS
    local = audit["profiles"][PROFILE_OPENCLAW_SKILL_LOCAL]
    claimable = audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE]
    assert local["profile_status"] == "pass"
    assert claimable["profile_status"] == "pass"
    assert local["claim_status"] == {
        "package_publication": False,
        "public_claimability_declared": False,
        "public_claimability_runtime_activated": False,
        "public_p2p_declared": False,
        "public_rc_claimed": False,
        "public_repository_publication": False,
    }
    assert claimable["claim_status"]["public_claimability_declared"] is True
    assert claimable["claim_status"]["public_claimability_runtime_activated"] is False
    assert claimable["claim_status"]["public_p2p_declared"] is False
    assert claimable["claim_status"]["public_rc_claimed"] is False


def test_phase_1251_boundary_surfaces_reuse_import_inventory_and_measurement_only_surfaces() -> None:
    audit = build_package_profile_ci_audit()
    claimable = audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE]
    surfaces = claimable["surface_measurements"]

    for surface_id in ("ilc_logic", "ilc_cli", "ilc_harness_adapters"):
        assert surfaces[surface_id]["boundary_contract"]["status"] == "pass"
        assert surfaces[surface_id]["boundary_contract"]["violation_count"] == 0
    assert surfaces["local_sidecar"]["boundary_contract"]["status"] == "measurement_only"
    assert surfaces["public_claimability"]["boundary_contract"]["status"] == "measurement_only"


def test_phase_1251_package_size_measurements_are_non_empty_and_full_digest() -> None:
    audit = build_package_profile_ci_audit()
    assert PACKAGE_PROFILE_AUDIT_FILE_SUFFIXES == (".json", ".py")
    for profile_id in audit["selected_profile_ids"]:
        measurement = audit["profiles"][profile_id]["profile_unique_measurement"]
        assert measurement["file_count"] > 0
        assert measurement["total_bytes"] > 0
        assert measurement["total_lines"] > 0
        for surface in audit["profiles"][profile_id]["surface_measurements"].values():
            assert surface["file_count"] > 0
            assert surface["total_bytes"] > 0
            for file_record in surface["files"]:
                assert len(file_record["sha256"]) == 64
                int(file_record["sha256"], 16)
                assert file_record["bytes"] > 0
                assert file_record["lines"] > 0


def test_phase_1251_protocol_schema_json_is_counted_as_package_content() -> None:
    audit = build_package_profile_ci_audit()
    logic_files = {
        record["path"]
        for record in audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE][
            "surface_measurements"
        ]["ilc_logic"]["files"]
    }

    assert "ilc_core/protocol/schemas/ilc_protocol_wire_format_v0.1.json" in logic_files


def test_phase_1251_canonical_json_artifact_matches_builder() -> None:
    expected = export_package_profile_ci_audit_json(build_package_profile_ci_audit())

    assert json.loads(expected) == build_package_profile_ci_audit()
    assert expected == json.dumps(
        build_package_profile_ci_audit(),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert ARTIFACT_JSON.read_text(encoding="utf-8").strip() == expected


def test_phase_1251_markdown_artifact_records_tokens_and_non_claims() -> None:
    markdown = render_package_profile_ci_audit_markdown(build_package_profile_ci_audit())
    artifact = ARTIFACT_MD.read_text(encoding="utf-8")

    assert artifact == markdown + "\n"
    assert GAP14_PACKAGE_CI_GATE_VERSION in artifact
    assert PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN in artifact
    assert PHASE_1251_GAP14_PACKAGE_CI_PROFILE_AUDIT_COMPLETE_TOKEN in artifact
    assert "No public RC claim was made." in artifact
    assert "No public claimability runtime was activated." in artifact
    assert "No public P2P exposure was introduced." in artifact


def test_phase_1251_fix1_non_package_findings_remain_routed() -> None:
    audit = build_package_profile_ci_audit()

    assert tuple(audit["fix1_finding_scope"]["consumed_findings"]) == (
        *PHASE_1250_FIX1_CONSUMED_FINDINGS,
    )
    routes = audit["fix1_finding_scope"]["non_package_findings_remain_routed"]
    assert set(routes) == set(PHASE_1250_FIX1_CARRY_FORWARD_ROUTES)
    assert routes["phase_1252"]["token"] == (
        "phase_1252_digest_truncation_security_binding_classification_recorded"
    )
    assert routes["phase_1253"]["token"] == (
        "phase_1253_transport_digest_and_rust_m5_disposition_recorded"
    )
    assert routes["phase_1254"]["token"] == (
        "phase_1254_legacy_graph_delta_gap_disposition_recorded"
    )


def test_phase_1251_unknown_profile_fails_closed() -> None:
    with pytest.raises(ValueError, match="public_rc_package_profile_unknown"):
        build_package_profile_ci_audit(("unknown_profile",))
