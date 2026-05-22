from __future__ import annotations

import hashlib
from pathlib import Path

import ilc_core.identity.agent_id_runtime as agent_id_runtime
from ilc_core.identity.agent_id_runtime import derive_agent_id, derive_agent_id_v2


ROOT = Path(__file__).resolve().parents[1]
BLOCKED_REPORT = ROOT / "docs/specs/ilc_phase_1431_rehearsal_identity_ceremony_blocked_v0.1.md"
MANIFEST = ROOT / "docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1431_blocked_report_records_required_tokens() -> None:
    text = _read(BLOCKED_REPORT)

    required_tokens = [
        "phase_1431_rehearsal_identity_ceremony_failed_closed",
        "finding_9_domain_separator_fixed_phase_1431",
        "finding_9_domain_separator_disposition_phase_1431",
        "finding_9_no_unratified_cdl_069_derivation_change_phase_1431",
        "human_public_identity_bundle_missing_phase_1431",
        "seven_agent_keypairs_not_generated_phase_1431",
        "identity_ceremony_public_manifest_not_committed_phase_1431",
        "keypairs_not_in_repo_phase_1431",
        "no_live_ecu_phase_1431",
        "no_graph_writes_phase_1431",
        "no_public_serving_phase_1431",
        "rehearsal_identity_ceremony_not_production_rc_phase_1431",
        "phase_1431_rerun_required_with_human_public_identity_bundle",
    ]

    for token in required_tokens:
        assert token in text


def test_finding_9_disposition_preserves_ratified_v2_known_vector() -> None:
    seed = b"\x00" * 32
    expected = hashlib.sha384(b"ilc-agent-id-v1:" + seed).hexdigest()

    assert agent_id_runtime._AGENT_ID_DOMAIN_V2 == b"ilc-agent-id-v1:"  # noqa: SLF001
    assert derive_agent_id_v2(seed) == expected


def test_legacy_and_v2_identity_paths_remain_unambiguous() -> None:
    same_32_bytes = bytes(range(32))

    legacy_id = derive_agent_id(same_32_bytes)
    v2_id = derive_agent_id_v2(same_32_bytes)

    assert legacy_id != v2_id
    assert legacy_id.startswith("agent-")
    assert len(legacy_id) == 70
    assert not v2_id.startswith("agent-")
    assert len(v2_id) == 96
    assert all(char in "0123456789abcdef" for char in v2_id)


def test_no_rehearsal_identity_manifest_or_completion_claim_created() -> None:
    text = _read(BLOCKED_REPORT)

    assert not MANIFEST.exists()
    assert "rehearsal_identity_ceremony_complete_phase_1431" not in text
    assert "seven_agent_keypairs_generated_phase_1431" not in text


def test_status_and_planning_route_phase_1431_to_rerun() -> None:
    status = _read(STATUS)
    planning = _read(PLANNING_INDEX)

    for text in (status, planning):
        assert "phase_1431_rehearsal_identity_ceremony_failed_closed" in text
        assert "phase_1431_rerun_required_with_human_public_identity_bundle" in text
        assert "Phase 1431" in text
