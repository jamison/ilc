from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.genesis import (
    APPEND_ONLY_INVOCATION_LOG_TOKEN,
    CDL_V6_EXTRAORDINARY_PATH_NOT_ORDINARY_GOVERNANCE_TOKEN,
    CDL_V6_GENESIS_INTERVENTION_RUNTIME_TOKEN,
    CDL_V6_GOV_B_TO_GOV_A_TOKEN,
    EPOCH_CEILING,
    EPOCH_CEILING_ENFORCER_TOKEN,
    GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN,
    GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN,
    GENESIS_INTERVENTION_NOT_FIRED_IN_TESTS_TOKEN,
    GENESIS_INTERVENTION_RUNTIME_VERSION,
    INTERVENTION_BRAKE_FIRE_COUNT,
    MAX_LIFETIME_INVOCATIONS,
    MAX_SUSPENSION_EPOCHS,
    PHASE_597_BOOTSTRAP_SUSPENSIVE_GUARDRAIL_BOUNDS_TOKEN,
    SIGNED_AUDIT_RECORD_REQUIRED_TOKEN,
    GenesisInterventionRequest,
    read_genesis_intervention_counter,
    record_genesis_intervention_guardrail_invocation,
    require_genesis_intervention_execution_authorization,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/genesis/genesis_intervention_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1355_g8_cdl_v6_genesis_intervention_enforcement.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1355_cdl_v6_genesis_intervention_enforcement_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT
    / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _request(proposal_id: str, *, epoch: int = 12) -> GenesisInterventionRequest:
    return GenesisInterventionRequest(
        proposal_id=proposal_id,
        proposal_content_hash=f"sha256:{proposal_id}",
        trigger_type="canonical_genesis_lineage_severance",
        invocation_epoch=epoch,
        expected_sunset_epoch=epoch + MAX_SUSPENSION_EPOCHS,
        ratified_artifact_or_lineage_boundary=(
            "docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1"
        ),
        cdl_v4_review_pointer="cdl_v4_review_required_after_phase_1355_guardrail",
        requested_by="phase_1355_test_operator",
        justification="test guardrail audit record only",
        signed_audit_record_ref="signed-audit-record-ref:phase-1355-test-only",
    )


def _audit_records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _imports_module(path: Path, module_name: str) -> bool:
    tree = ast.parse(_read(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == module_name for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module == module_name:
            return True
    return False


def test_phase_1355_counter_states_zero_one_two_accepted_three_rejected(
    tmp_path: Path,
) -> None:
    counter_path = tmp_path / "counter.json"
    audit_log_path = tmp_path / "audit.ndjson"

    for index in range(MAX_LIFETIME_INVOCATIONS):
        audit = record_genesis_intervention_guardrail_invocation(
            request=_request(f"proposal-{index}"),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp=f"2026-05-15T00:00:0{index}+00:00",
        )
        assert audit.accepted is True
        assert audit.counter_before == index
        assert audit.counter_after == index + 1
        assert audit.execution_authorized is False
        assert audit.brake_fired is False

    state = read_genesis_intervention_counter(counter_path)
    assert state.lifetime_invocations == MAX_LIFETIME_INVOCATIONS

    with pytest.raises(
        ValueError,
        match="genesis_intervention_max_invocations_exceeded",
    ):
        record_genesis_intervention_guardrail_invocation(
            request=_request("proposal-3"),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-05-15T00:00:04+00:00",
        )

    records = _audit_records(audit_log_path)
    assert len(records) == 4
    assert records[-1]["accepted"] is False
    assert records[-1]["outcome_token"] == "genesis_intervention_max_invocations_exceeded"
    assert read_genesis_intervention_counter(counter_path).lifetime_invocations == 3


def test_phase_1355_epoch_ceiling_and_one_epoch_sunset_are_enforced(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="genesis_intervention_epoch_ceiling_exceeded"):
        record_genesis_intervention_guardrail_invocation(
            request=_request("epoch-over-ceiling", epoch=EPOCH_CEILING + 1),
            counter_path=tmp_path / "counter.json",
            audit_log_path=tmp_path / "audit.ndjson",
            diagnostic_timestamp="2026-05-15T00:01:00+00:00",
        )

    bad_sunset = GenesisInterventionRequest(
        **{
            **_request("bad-sunset").__dict__,
            "expected_sunset_epoch": 20,
        }
    )
    with pytest.raises(
        ValueError,
        match="genesis_intervention_sunset_must_be_one_epoch_phase_1355",
    ):
        record_genesis_intervention_guardrail_invocation(
            request=bad_sunset,
            counter_path=tmp_path / "counter.json",
            audit_log_path=tmp_path / "audit.ndjson",
            diagnostic_timestamp="2026-05-15T00:02:00+00:00",
        )


def test_phase_1355_per_proposal_limit_and_trigger_scope_are_enforced(
    tmp_path: Path,
) -> None:
    counter_path = tmp_path / "counter.json"
    audit_log_path = tmp_path / "audit.ndjson"

    record_genesis_intervention_guardrail_invocation(
        request=_request("same-proposal"),
        counter_path=counter_path,
        audit_log_path=audit_log_path,
        diagnostic_timestamp="2026-05-15T00:03:00+00:00",
    )

    with pytest.raises(
        ValueError,
        match="genesis_intervention_proposal_invocation_limit_exceeded",
    ):
        record_genesis_intervention_guardrail_invocation(
            request=_request("same-proposal"),
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-05-15T00:04:00+00:00",
        )

    bad_trigger = GenesisInterventionRequest(
        **{
            **_request("bad-trigger").__dict__,
            "trigger_type": "ordinary_feature_release",
        }
    )
    with pytest.raises(
        ValueError,
        match="genesis_intervention_trigger_out_of_scope_phase_1355",
    ):
        record_genesis_intervention_guardrail_invocation(
            request=bad_trigger,
            counter_path=counter_path,
            audit_log_path=audit_log_path,
            diagnostic_timestamp="2026-05-15T00:05:00+00:00",
        )


def test_phase_1355_audit_log_appends_and_counter_write_is_atomic(tmp_path: Path) -> None:
    counter_path = tmp_path / "counter.json"
    audit_log_path = tmp_path / "audit.ndjson"
    first = record_genesis_intervention_guardrail_invocation(
        request=_request("append-one"),
        counter_path=counter_path,
        audit_log_path=audit_log_path,
        diagnostic_timestamp="2026-05-15T00:06:00+00:00",
    )
    second = record_genesis_intervention_guardrail_invocation(
        request=_request("append-two"),
        counter_path=counter_path,
        audit_log_path=audit_log_path,
        diagnostic_timestamp="2026-05-15T00:07:00+00:00",
    )

    records = _audit_records(audit_log_path)
    assert [record["proposal_id"] for record in records] == ["append-one", "append-two"]
    assert first.append_only_log_token == APPEND_ONLY_INVOCATION_LOG_TOKEN
    assert second.counter_after == 2
    assert read_genesis_intervention_counter(counter_path).lifetime_invocations == 2

    source = _read(RUNTIME)
    assert "tempfile.mkstemp" in source
    assert "os.replace" in source
    assert 'path.open("a", encoding="utf-8")' in source
    assert ".truncate(" not in source


def test_phase_1355_audit_json_is_canonical_and_contains_required_tokens(
    tmp_path: Path,
) -> None:
    audit_log_path = tmp_path / "audit.ndjson"
    audit = record_genesis_intervention_guardrail_invocation(
        request=_request("canonical-json"),
        counter_path=tmp_path / "counter.json",
        audit_log_path=audit_log_path,
        diagnostic_timestamp="2026-05-15T00:08:00+00:00",
    )
    raw_line = audit_log_path.read_text(encoding="utf-8").strip()
    parsed = json.loads(raw_line)

    assert raw_line == json.dumps(
        parsed,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert audit.runtime_version == GENESIS_INTERVENTION_RUNTIME_VERSION
    assert parsed["counter_token"] == GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN
    assert parsed["epoch_ceiling_token"] == EPOCH_CEILING_ENFORCER_TOKEN
    assert parsed["hardening_token"] == CDL_V6_GOV_B_TO_GOV_A_TOKEN
    assert parsed["phase_597_bounds_token"] == (
        PHASE_597_BOOTSTRAP_SUSPENSIVE_GUARDRAIL_BOUNDS_TOKEN
    )
    assert parsed["cdl_v6_extraordinary_boundary_token"] == (
        CDL_V6_EXTRAORDINARY_PATH_NOT_ORDINARY_GOVERNANCE_TOKEN
    )
    assert parsed["execution_not_authorized_token"] == (
        GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN
    )
    assert parsed["signed_audit_record_ref"] == (
        "signed-audit-record-ref:phase-1355-test-only"
    )
    assert parsed["signed_audit_record_required_token"] == (
        SIGNED_AUDIT_RECORD_REQUIRED_TOKEN
    )


def test_phase_1355_brake_execution_remains_not_authorized() -> None:
    assert INTERVENTION_BRAKE_FIRE_COUNT == 0
    assert GENESIS_INTERVENTION_NOT_FIRED_IN_TESTS_TOKEN == (
        "genesis_intervention_not_fired_in_tests_phase_1355"
    )
    with pytest.raises(
        ValueError,
        match=GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN,
    ):
        require_genesis_intervention_execution_authorization()


def test_phase_1355_docs_record_tokens_and_scope_correction() -> None:
    tokens = (
        CDL_V6_GENESIS_INTERVENTION_RUNTIME_TOKEN,
        GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN,
        APPEND_ONLY_INVOCATION_LOG_TOKEN,
        EPOCH_CEILING_ENFORCER_TOKEN,
        CDL_V6_GOV_B_TO_GOV_A_TOKEN,
        GENESIS_INTERVENTION_NOT_FIRED_IN_TESTS_TOKEN,
        PHASE_597_BOOTSTRAP_SUSPENSIVE_GUARDRAIL_BOUNDS_TOKEN,
        CDL_V6_EXTRAORDINARY_PATH_NOT_ORDINARY_GOVERNANCE_TOKEN,
        GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN,
        SIGNED_AUDIT_RECORD_REQUIRED_TOKEN,
    )
    for path in (RUNTIME, PROMPT, WALKTHROUGH, STATUS, INDEX, FORWARD_PLAN):
        text = _read(path)
        for token in tokens:
            assert token in text
    assert "forward-plan hardening shorthand" in _read(PROMPT)
    assert "Phase 597" in _read(WALKTHROUGH)


def test_phase_1355_runtime_has_no_random_float_or_assert_enforcement() -> None:
    source = _read(RUNTIME)
    tree = ast.parse(source)
    assert not _imports_module(RUNTIME, "random")
    assert "float(" not in source
    assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))
