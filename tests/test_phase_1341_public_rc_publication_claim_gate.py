from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ilc_core.rc import public_rc_publication_claim_gate as gate


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _canonical_hash(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()


def test_phase_1341_report_blocks_publication_with_findings() -> None:
    report = _load_json("docs/specs/ilc_public_rc_publication_claim_gate_1341_v0.1.json")

    assert report["schema_version"] == gate.PHASE_1341_VERSION
    assert report["required_tokens"] == gate.phase_1341_required_tokens()
    assert report["gate_result"] == "blocked_with_findings"
    assert report["public_rc_publication_claim_gate_verdict"] == (
        "public_rc_publication_claim_gate_verdict=blocked_with_findings"
    )
    assert report["authority_decision"]["explicit_authority_present"] is True
    assert report["public_rc_remains_blocked"] is True
    assert report["next_phase"] == "phase_1342_window_1330_1342_closure_next"


def test_phase_1341_report_records_expected_open_blockers() -> None:
    report = _load_json("docs/specs/ilc_public_rc_publication_claim_gate_1341_v0.1.json")
    blocker_ids = {blocker["blocker_id"] for blocker in report["blockers"]}

    assert "publication_target_or_tag_not_selected" in blocker_ids
    assert "counsel_publication_clearance_missing" in blocker_ids
    assert "release_artifact_not_release_signed" in blocker_ids
    assert "public_claimability_api_not_activated" in blocker_ids
    assert "public_path_p2p_sidecar_serving_not_activated" in blocker_ids
    assert "wallet_ecu_ilc_value_path_not_activated" in blocker_ids


def test_phase_1341_positive_evidence_is_scoped_not_published() -> None:
    report = _load_json("docs/specs/ilc_public_rc_publication_claim_gate_1341_v0.1.json")
    claim_status = {claim["claim_id"]: claim["status"] for claim in report["claim_matrix"]}

    assert claim_status["clean_materialized_source_tree_exists"] == "closed"
    assert claim_status["unsigned_release_artifact_exists"] == "closed"
    assert claim_status["release_key_envelope_metadata_exists"] == "closed"
    assert claim_status["genesis_atlas_v0_2_root_envelope_signed"] == "closed"
    assert claim_status["public_rc_publication_claim"] == "blocked"
    assert report["publication_action"]["publication_performed"] is False
    assert report["publication_action"]["public_repository_push_performed"] is False
    assert report["publication_action"]["public_package_upload_performed"] is False


def test_phase_1341_non_authorization_floor_remains_closed() -> None:
    report = _load_json("docs/specs/ilc_public_rc_publication_claim_gate_1341_v0.1.json")
    floor = report["non_authorization_floor"]

    assert floor["public_rc_publication_claim_authority_present"] is True
    assert floor["public_rc_publication_claim_performed"] is False
    assert floor["public_repository_publication_performed"] is False
    assert floor["source_publication_performed"] is False
    assert floor["release_signing_authorized_or_performed"] is False
    assert floor["counsel_approval_authorized_or_recorded"] is False
    assert floor["wallet_ecu_ilc_activation_authorized"] is False


def test_phase_1341_manifest_hash_and_validator() -> None:
    report = _load_json("docs/specs/ilc_public_rc_publication_claim_gate_1341_v0.1.json")
    hash_payload = dict(report)
    hash_payload["manifest_hash"] = "sha256:" + "0" * 64

    assert report["manifest_hash"] == _canonical_hash(hash_payload)
    assert gate.validate_public_rc_publication_claim_gate(report)["gate_result"] == (
        "blocked_with_findings"
    )
