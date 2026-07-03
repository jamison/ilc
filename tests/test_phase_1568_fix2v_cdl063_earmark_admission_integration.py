from __future__ import annotations

import pytest

from ilc_core.epistemic.node_submission_runtime import (
    EpistemicSubmissionError,
    route_epistemic_mode,
    validate_epistemic_node_submission,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime


def _delivered_earmark_record() -> dict[str, object]:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("commissioner-agent", "10")

    proposed = runtime.earmark_propose(
        earmark_id="earmark:phase-1568-fix2v",
        commission_id="commission:phase-1568-fix2v",
        commissioning_agent_id="commissioner-agent",
        performing_agent_id="performer-agent",
        earmark_amount="2",
        proposal_epoch=10,
        task_description_hash="sha256:commission-task",
    )
    assert proposed["ok"] is True

    accepted = runtime.earmark_accept(
        earmark_id="earmark:phase-1568-fix2v",
        performing_agent_id="performer-agent",
        acceptance_epoch=11,
    )
    assert accepted["ok"] is True

    delivered = runtime.earmark_deliver(
        earmark_id="earmark:phase-1568-fix2v",
        performing_agent_id="performer-agent",
        contribution_id="cid:commissioned-contribution",
        delivery_epoch=12,
    )
    assert delivered["ok"] is True
    return delivered["data"]


def _expired_earmark_record() -> dict[str, object]:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("commissioner-agent", "10")

    proposed = runtime.earmark_propose(
        earmark_id="earmark:phase-1568-fix2v-expired",
        commission_id="commission:phase-1568-fix2v-expired",
        commissioning_agent_id="commissioner-agent",
        performing_agent_id="performer-agent",
        earmark_amount="2",
        proposal_epoch=10,
        task_description_hash="sha256:commission-task-expired",
    )
    assert proposed["ok"] is True

    boundary = runtime.process_epoch_boundary(commit_epoch=10 + 2880)
    assert boundary["ok"] is True

    status = runtime.earmark_status(earmark_id="earmark:phase-1568-fix2v-expired")
    assert status["ok"] is True
    assert status["data"]["state"] == "expired"
    return status["data"]


def _submission(*, refutation_criterion: dict[str, object]) -> dict[str, object]:
    return {
        "cid": "cid:commissioned-contribution",
        "agent_id": "performer-agent",
        "authored_envelope": {
            "refutation_criterion": refutation_criterion,
        },
        "protocol_envelope": {
            "cdl063_commission_earmark": _delivered_earmark_record(),
        },
        "transport_envelope": {},
    }


def test_cdl063_earmark_does_not_shortcut_invalid_popperian_claim() -> None:
    submission = _submission(
        refutation_criterion={
            "claim": "Commissioned work should be admitted because an earmark exists.",
            "evidence_type": "empirical",
            "scope_boundary": "phase_1568_fix2v",
            "claim_form": "normative",
            "has_falsifiable_test": True,
            "is_inadmissible_counterexample": False,
            "agreement_score": 1,
        }
    )

    with pytest.raises(EpistemicSubmissionError) as excinfo:
        validate_epistemic_node_submission(submission)

    assert excinfo.value.token == "MALFORMED_REFUTATION_CRITERION"


def test_cdl063_expired_earmark_does_not_shortcut_invalid_popperian_claim() -> None:
    submission = {
        "cid": "cid:commissioned-contribution",
        "agent_id": "performer-agent",
        "authored_envelope": {
            "refutation_criterion": {
                "claim": "Expired commission metadata should admit this claim.",
                "evidence_type": "empirical",
                "scope_boundary": "phase_1568_fix2v",
                "claim_form": "normative",
                "has_falsifiable_test": True,
                "is_inadmissible_counterexample": False,
                "agreement_score": 1,
            },
        },
        "protocol_envelope": {
            "cdl063_commission_earmark": _expired_earmark_record(),
        },
        "transport_envelope": {},
    }

    with pytest.raises(EpistemicSubmissionError) as excinfo:
        validate_epistemic_node_submission(submission)

    assert excinfo.value.token == "MALFORMED_REFUTATION_CRITERION"


def test_cdl063_earmark_preserves_valid_popperian_submission_route() -> None:
    submission = _submission(
        refutation_criterion={
            "claim": "The commissioned artifact reproduces fixture hash H in namespace N.",
            "evidence_type": "empirical",
            "scope_boundary": "phase_1568_fix2v",
            "claim_form": "falsifiable_positive",
            "has_falsifiable_test": True,
            "is_inadmissible_counterexample": False,
            "agreement_score": 1,
        }
    )

    validate_epistemic_node_submission(submission)
    assert route_epistemic_mode(submission) == "mode_2"


def test_cdl063_earmark_cannot_move_refutation_criterion_to_protocol_envelope() -> None:
    submission = {
        "cid": "cid:commissioned-contribution",
        "agent_id": "performer-agent",
        "authored_envelope": {},
        "protocol_envelope": {
            "cdl063_commission_earmark": _delivered_earmark_record(),
            "refutation_criterion": {
                "claim": "Protocol-side criterion should not bypass authorship rules.",
                "evidence_type": "empirical",
                "scope_boundary": "phase_1568_fix2v",
                "claim_form": "falsifiable_positive",
                "has_falsifiable_test": True,
                "is_inadmissible_counterexample": False,
                "agreement_score": 1,
            },
        },
        "transport_envelope": {},
    }

    with pytest.raises(EpistemicSubmissionError) as excinfo:
        validate_epistemic_node_submission(submission)

    assert excinfo.value.token == "AUTHORED_ENVELOPE_VIOLATION"
