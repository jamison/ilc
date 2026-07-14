from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
GATE = ROOT / "docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md"
HANDOFF = ROOT / "docs/specs/ilc_window_1565_1575_handoff_1575c_v0.1.md"
SOURCE_EXPORT = ROOT / "out/block6_public_rc_gate_001_1575c/final_source_export_1575c.json"
MIRROR_MANIFEST = ROOT / "out/block6_public_rc_gate_001_1575c/public_mirror_manifest_1575c.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_artifact_has_required_sections() -> None:
    text = _read(GATE)
    for section in range(1, 11):
        assert f"## {section}." in text
    assert "GO PUBLIC-RC-GATE-001" in text
    assert "post_rc_v05_behavioral_graph_carry_forward_locked_phase_1575c" in text


def test_status_tokens_emitted() -> None:
    text = _read(STATUS)
    for token in [
        "genesis_v05_public_rc_envelope_consumed_phase_1575c",
        "public_rc_gate_001_authorized",
        "window_1565_closed_phase_1575c",
        "window_1565_closure_gate_verdict=pass",
        "public_rc_live_phase_1575c",
        "public_repository_push_authorized_phase_1575c",
        "post_rc_v05_behavioral_graph_carry_forward_locked_phase_1575c",
        "sanitized_public_mirror_regenerated_phase_1575c",
    ]:
        assert token in text


def test_genesis_v04_source_and_v05_signature_boundary() -> None:
    genesis_v04 = ROOT / "out/genesis_core_star_map_v0.4.json"
    verification = ROOT / "out/genesis_public_rc_signing_envelope_v0.5.verification.json"
    assert genesis_v04.exists()
    data = json.loads(genesis_v04.read_text(encoding="utf-8"))
    assert not ({"signature", "signatures", "cose_sign1", "signed_at"} & set(data))
    verification_data = json.loads(verification.read_text(encoding="utf-8"))
    assert verification_data["verification_result"] == "signature_verified"
    assert (
        verification_data["signature_payload_sha256"]
        == "57a6b9640686df7f21dcb39d8f102c19d8c75e553ce182e1529ac01060b4db01"
    )


def test_final_source_export_manifest_is_clean() -> None:
    data = json.loads(SOURCE_EXPORT.read_text(encoding="utf-8"))
    counts = data["counts"]
    included = {record["path"] for record in data["included_files"]}
    excluded = {record["path"] for record in data["excluded_files"]}
    assert data["result"] == "pass"
    assert counts["included_files"] == 435
    assert counts["excluded_files"] == 39
    assert counts["blocked_ambiguities"] == 0
    assert data["marker_scan"]["result"] == "pass"
    assert data["dependency_scan"]["result"] == "pass"
    assert included.isdisjoint(excluded)


def test_public_mirror_manifest_is_clean_and_no_push() -> None:
    data = json.loads(MIRROR_MANIFEST.read_text(encoding="utf-8"))
    assert data["pipeline_version"] == "generate_public_mirror_1573n.v0.2"
    assert data["filtered_public_head_sha"] == "0730d639eee684737ff087e7ef8e7b9046495461"
    assert data["canonical_hash"] == (
        "sha256:4df9c0bc1db05872fc96e3fc3e4616b6618ffaa18cedfc9c01bb1d00366740dd"
    )
    assert data["denylist_scan_result"] == "pass"
    assert data["public_rc_exclude_scan_result"] == "pass"
    assert data["no_push"] is True


def test_phase_1564_selftest_chain_guard_is_present() -> None:
    text = _read(ROOT / "tests/test_phase_1564_window_1556_1564_closure_gate.py")
    assert "ILC_PHASE_1564_GATE_SELFTEST" in text
    assert "ILC_PHASE_1564_GATE_SELFTEST" in _read(GATE)


def test_no_activation_guards_cleared_in_runtime_source() -> None:
    cleared: list[str] = []
    for path in (ROOT / "ilc_core").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"NOT_ACTIVATED\s*=\s*False", text):
            cleared.append(str(path.relative_to(ROOT)))
    assert cleared == []


def test_six_economic_guards_still_true() -> None:
    from ilc_core.economics.productive_ecu_expansion_bounty_runtime import (
        PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED,
    )
    from ilc_core.epoch.ejected_stake_distribution_production_path import (
        EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
    )
    from ilc_core.epoch.epoch_emission_production_path import (
        PRODUCTION_EMISSION_NOT_ACTIVATED,
    )
    from ilc_core.epoch.treasury_validator_reward_production_path import (
        TREASURY_DISTRIBUTION_NOT_ACTIVATED,
    )
    from ilc_core.ledger.conversion_candidate_runtime import (
        CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED,
    )
    from ilc_core.validator.validator_admission_ejection_production_path import (
        VALIDATOR_ADMISSION_NOT_ACTIVATED,
    )

    assert CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED is True
    assert EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED is True
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is True
    assert PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED is True
    assert TREASURY_DISTRIBUTION_NOT_ACTIVATED is True
    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True


def test_handoff_records_public_rc_live_and_post_rc_routing() -> None:
    text = _read(HANDOFF)
    assert "window_1565_closure_gate_verdict=pass" in text
    assert "public_rc_live_phase_1575c" in text
    assert "Post-RC v0.5 workstream" in text


def test_no_dev_test_signing_profile_is_accepted() -> None:
    text = _read(GATE)
    assert "ed25519_cose_sign1_dev_test_only" not in text
    assert "ML-DSA-65" in text
