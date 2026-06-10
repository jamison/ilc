from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.genesis.genesis_intervention_runtime import (
    EPOCH_CEILING,
    GENESIS_INTERVENTION_ACCEPTED_AUDIT_ONLY_TOKEN,
    GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN,
    GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN,
    MAX_LIFETIME_INVOCATIONS,
    MAX_SUSPENSION_EPOCHS,
    GenesisInterventionRequest,
    read_genesis_intervention_counter,
    record_genesis_intervention_guardrail_invocation,
    require_genesis_intervention_execution_authorization,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/specs/ilc_cdl_v6_enforcement_scaffold_audit_1548p_v0.1.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
RUNTIME = ROOT / "ilc_core/genesis/genesis_intervention_runtime.py"
STATUS = ROOT / "docs/phases/STATUS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def request(proposal_id: str, *, epoch: int = 12) -> GenesisInterventionRequest:
    return GenesisInterventionRequest(
        proposal_id=proposal_id,
        trigger_type="canonical_genesis_lineage_severance",
        invocation_epoch=epoch,
        expected_sunset_epoch=epoch + MAX_SUSPENSION_EPOCHS,
        ratified_artifact_or_lineage_boundary="phase_597_boundary",
        cdl_v4_review_pointer="cdl_v4_review_required",
        requested_by="phase_1548p_test",
        justification="audit-only test request",
        signed_audit_record_ref="signed-audit-record-ref:phase-1548p",
        proposal_content_hash=f"sha256:{proposal_id}",
    )


def audit_records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_phase_1548p_audit_doc_records_closure_without_invocation() -> None:
    text = read(AUDIT)

    for needle in (
        "obl_024_cdl_v6_enforcement_scaffold_audit_committed_phase_1548p",
        "obl_024_closed_phase_1548p",
        "cdl_v6_not_invoked_phase_1548p",
        "genesis_intervention_guard_retained_phase_1548p",
        "MAX_LIFETIME_INVOCATIONS = 3",
        "MAX_SUSPENSION_EPOCHS = 1",
        "EPOCH_CEILING = 60",
        "No runtime hardening was required in Phase 1548p.",
    ):
        assert needle in text

    assert "This audit does not invoke CDL-V6" in text


def test_phase_1548p_runtime_enforces_counter_audit_and_guard(tmp_path: Path) -> None:
    counter_path = tmp_path / "counter.json"
    audit_log_path = tmp_path / "audit.ndjson"

    for index in range(MAX_LIFETIME_INVOCATIONS):
        record = record_genesis_intervention_guardrail_invocation(
            request=request(f"proposal-{index}"),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp=f"2026-06-10T00:00:0{index}+00:00",
        )
        assert record.accepted is True
        assert record.outcome_token == GENESIS_INTERVENTION_ACCEPTED_AUDIT_ONLY_TOKEN
        assert record.execution_authorized is False
        assert record.brake_fired is False

    with pytest.raises(ValueError, match="genesis_intervention_max_invocations_exceeded"):
        record_genesis_intervention_guardrail_invocation(
            request=request("proposal-3"),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-06-10T00:00:04+00:00",
        )

    state = read_genesis_intervention_counter(counter_path)
    assert state.lifetime_invocations == 3

    records = audit_records(audit_log_path)
    assert len(records) == 4
    assert records[-1]["accepted"] is False
    assert records[-1]["counter_token"] == GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN
    assert records[-1]["outcome_token"] == "genesis_intervention_max_invocations_exceeded"

    with pytest.raises(ValueError, match=GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN):
        require_genesis_intervention_execution_authorization()


def test_phase_1548p_duplicate_proposal_bad_sunset_and_epoch_ceiling_reject(
    tmp_path: Path,
) -> None:
    counter_path = tmp_path / "counter.json"
    audit_log_path = tmp_path / "audit.ndjson"

    record_genesis_intervention_guardrail_invocation(
        request=request("same-proposal"),
        counter_path=counter_path,
        audit_log_path=audit_log_path,
        diagnostic_timestamp="2026-06-10T00:01:00+00:00",
    )

    with pytest.raises(
        ValueError,
        match="genesis_intervention_proposal_invocation_limit_exceeded",
    ):
        record_genesis_intervention_guardrail_invocation(
            request=request("same-proposal"),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-06-10T00:02:00+00:00",
        )

    bad_sunset = GenesisInterventionRequest(
        **{
            **request("bad-sunset").__dict__,
            "expected_sunset_epoch": 99,
        }
    )
    with pytest.raises(
        ValueError,
        match="genesis_intervention_sunset_must_be_one_epoch_phase_1355",
    ):
        record_genesis_intervention_guardrail_invocation(
            request=bad_sunset,
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-06-10T00:03:00+00:00",
        )

    with pytest.raises(ValueError, match="genesis_intervention_epoch_ceiling_exceeded"):
        record_genesis_intervention_guardrail_invocation(
            request=request("too-late", epoch=EPOCH_CEILING + 1),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-06-10T00:04:00+00:00",
        )


def test_phase_1548p_runtime_uses_canonical_json_atomic_counter_and_append_log() -> None:
    source = read(RUNTIME)

    assert "sort_keys=True" in source
    assert "allow_nan=False" in source
    assert "tempfile.mkstemp" in source
    assert "os.replace" in source
    assert "os.fsync" in source
    assert 'path.open("a", encoding="utf-8")' in source
    assert "execution_authorized=False" in source
    assert "brake_fired=False" in source
    assert "raise ValueError(GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN)" in source


def test_phase_1548p_obl_row_and_status_are_backfilled() -> None:
    register = read(REGISTER)
    row = next(line for line in register.splitlines() if line.startswith("| OBL-024 |"))
    assert "| closed |" in row
    assert "obl_024_closed_phase_1548p" in row
    assert "ilc_cdl_v6_enforcement_scaffold_audit_1548p_v0.1.md" in row
    assert "cdl_v6_not_invoked_phase_1548p" in row

    for obl in ("OBL-028", "OBL-029"):
        other = next(line for line in register.splitlines() if line.startswith(f"| {obl} |"))
        assert "closed_phase_1548p" not in other

    status = read(STATUS)
    assert "## Phase 1548p - OBL-024 CDL-V6 Enforcement Scaffold Audit" in status
    assert "obl_024_cdl_v6_enforcement_scaffold_audit_committed_phase_1548p" in status
    assert "No CDL-V6 invocation" in status
