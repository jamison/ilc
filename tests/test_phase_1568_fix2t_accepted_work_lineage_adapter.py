from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ilc_core.consensus.accepted_work_lineage_adapter import (
    AcceptedWorkLineageError,
    build_accepted_work_lineage_receipt,
    verify_accepted_work_lineage_receipt,
)
from ilc_core.consensus.attribution_batch_bridge import build_attribution_batch_from_claims
from tests.test_agent_loop_v1_runtime import _legacy_seed, _task
from tests.test_phase_1568_fix2l_rehearsal_economics_record import _accepted_submissions
from tools import agent_loop_v1
from tools.testbed import run_three_node_seven_agent_scenario as scenario_runner
from tools.testbed.rehearsal_economics import (
    build_rehearsal_economics_record,
    write_json,
)


def _artifacts() -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    submissions = _accepted_submissions()
    outsider = agent_loop_v1._build_outsider_submission(
        _task(),
        _legacy_seed("08"),
        "cluster-e",
        "ilc-node-6",
    )
    panel_payload = agent_loop_v1.evaluate_panel(
        task=_task(),
        submissions=submissions,
        outsider_submission=outsider,
    )
    claim_payload = agent_loop_v1.build_ecu_claim_batch(_task(), panel_payload)
    attribution_batch = build_attribution_batch_from_claims(claim_payload)
    economics_record = build_rehearsal_economics_record(
        namespace_id="phase1568-fix2t-test",
        accepted_submissions=submissions,
        ecu_claims=claim_payload["claims"],
        rehearsal_epoch=574,
    )
    return panel_payload, claim_payload, attribution_batch, economics_record


def _receipt() -> dict[str, object]:
    panel_payload, claim_payload, attribution_batch, economics_record = _artifacts()
    return build_accepted_work_lineage_receipt(
        panel_payload=panel_payload,
        claim_payload=claim_payload,
        attribution_batch=attribution_batch,
        conversion_resolution=economics_record["cdl048_conversion_resolution"],
        ilc_read_model_replay_record=economics_record,
    )


def test_fix2t_builds_receipt_binding_claims_batch_conversion_and_read_model() -> None:
    panel_payload, claim_payload, attribution_batch, economics_record = _artifacts()

    receipt = build_accepted_work_lineage_receipt(
        panel_payload=panel_payload,
        claim_payload=claim_payload,
        attribution_batch=attribution_batch,
        conversion_resolution=economics_record["cdl048_conversion_resolution"],
        ilc_read_model_replay_record=economics_record,
    )
    verification = verify_accepted_work_lineage_receipt(
        receipt,
        panel_payload=panel_payload,
        claim_payload=claim_payload,
        attribution_batch=attribution_batch,
        conversion_resolution=economics_record["cdl048_conversion_resolution"],
        ilc_read_model_replay_record=economics_record,
    )

    assert receipt["marker"] == "phase_1568_fix2t_accepted_work_lineage_receipt"
    assert receipt["accepted_work_ref"]["verdict_token"] == "panel_quorum_passed"
    assert receipt["attribution_batch_ref"]["total_micro_ecu"] == 5817378
    assert receipt["conversion_resolution_ref"]["resolution_status"] == "pending"
    assert receipt["ilc_read_model_replay_ref"]["settlement_root_hex"] == economics_record["settlement_root_hex"]
    assert receipt["new_attribution_schema_defined"] is False
    assert receipt["value_write_authorized"] is False
    assert receipt["wallet_write_authorized"] is False
    assert verification["ok"] is True
    assert verification["lineage_root"] == receipt["lineage_root"]


def test_fix2t_rejects_claim_payload_without_accepted_marker() -> None:
    panel_payload, claim_payload, attribution_batch, economics_record = _artifacts()
    claim_payload = dict(claim_payload)
    claim_payload.pop("marker")

    with pytest.raises(AcceptedWorkLineageError) as excinfo:
        build_accepted_work_lineage_receipt(
            panel_payload=panel_payload,
            claim_payload=claim_payload,
            attribution_batch=attribution_batch,
            conversion_resolution=economics_record["cdl048_conversion_resolution"],
            ilc_read_model_replay_record=economics_record,
        )

    assert excinfo.value.token == "agent_loop_claims_ok_required_phase_1568_fix2t"


def test_fix2t_rejects_tampered_attribution_batch() -> None:
    panel_payload, claim_payload, attribution_batch, economics_record = _artifacts()
    tampered = deepcopy(attribution_batch)
    tampered["total_micro_ecu"] = tampered["total_micro_ecu"] + 1

    with pytest.raises(AcceptedWorkLineageError) as excinfo:
        build_accepted_work_lineage_receipt(
            panel_payload=panel_payload,
            claim_payload=claim_payload,
            attribution_batch=tampered,
            conversion_resolution=economics_record["cdl048_conversion_resolution"],
            ilc_read_model_replay_record=economics_record,
        )

    assert excinfo.value.token == "attribution_batch_mismatch_phase_1568_fix2t"


def test_fix2t_rejects_value_write_authorization_and_attribution_fraction() -> None:
    panel_payload, claim_payload, attribution_batch, economics_record = _artifacts()
    resolution = deepcopy(economics_record["cdl048_conversion_resolution"])
    resolution["wallet_write_authorized"] = True

    with pytest.raises(AcceptedWorkLineageError) as excinfo:
        build_accepted_work_lineage_receipt(
            panel_payload=panel_payload,
            claim_payload=claim_payload,
            attribution_batch=attribution_batch,
            conversion_resolution=resolution,
            ilc_read_model_replay_record=economics_record,
        )

    assert excinfo.value.token == "accepted_work_lineage_write_authorization_forbidden"

    with_fraction = deepcopy(attribution_batch)
    with_fraction["attributions"][0]["attribution_fraction"] = "1.0"
    with pytest.raises(AcceptedWorkLineageError) as fraction_exc:
        build_accepted_work_lineage_receipt(
            panel_payload=panel_payload,
            claim_payload=claim_payload,
            attribution_batch=with_fraction,
            conversion_resolution=economics_record["cdl048_conversion_resolution"],
            ilc_read_model_replay_record=economics_record,
        )

    assert fraction_exc.value.token == "attribution_fraction_field_forbidden_phase_1568_fix2t"


def test_fix2t_scenario_runner_emits_lineage_artifacts(tmp_path: Path) -> None:
    panel_payload, claim_payload, _attribution_batch, economics_record = _artifacts()
    panel_dir = tmp_path / "panel"
    panel_dir.mkdir()
    write_json(panel_dir / "ecu_claims.json", claim_payload)

    receipt = scenario_runner._emit_accepted_work_lineage_receipt(
        output_root=tmp_path,
        panel_payload=panel_payload,
        rehearsal_economics_record=economics_record,
    )

    assert (tmp_path / "consensus_attribution_batch.json").exists()
    assert (tmp_path / "accepted_work_lineage_receipt.json").exists()
    assert json.loads((tmp_path / "accepted_work_lineage_receipt.json").read_text())[
        "lineage_root"
    ] == receipt["lineage_root"]


def test_fix2t_receipt_does_not_emit_attribution_fraction_schema() -> None:
    receipt_json = json.dumps(_receipt(), sort_keys=True)

    assert '"attribution_fraction"' not in receipt_json
    assert '"new_attribution_schema_defined": false' in receipt_json
