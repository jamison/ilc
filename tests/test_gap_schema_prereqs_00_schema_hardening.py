from __future__ import annotations

from dataclasses import fields

import pytest

from ilc_core.epistemic.jury_assignment_runtime import JuryAssignmentQuote
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_graph_store import (
    node_record_from_submission,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    validate_truth_primitive_submission,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


def _assert_truth_submission(**overrides: object) -> dict[str, object]:
    submission: dict[str, object] = {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": "a" * 96,
        "epoch": 1,
        "payload": {
            "content": {"text": "bounded uncertainty claim"},
            "primitive_type": "knowledge_claim",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }
    submission.update(overrides)
    return submission


def _validate_claim_submission(**overrides: object) -> dict[str, object]:
    submission: dict[str, object] = {
        "v": 1,
        "primitive": "validate.claim",
        "agent_id": "b" * 96,
        "epoch": 2,
        "payload": {
            "target_node_id": "bafy-target",
            "confidence": "0.9",
            "evidence_summary": "observed twice",
        },
        "sig": "UNSIGNED",
    }
    submission.update(overrides)
    return submission


def test_uncertainty_declared_passes_through_validation_result() -> None:
    result = validate_truth_primitive_submission(
        _assert_truth_submission(uncertainty_declared="0.85")
    )
    assert result.uncertainty_declared == "0.85"


def test_uncertainty_declared_rejects_non_string_non_null() -> None:
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(
            _assert_truth_submission(uncertainty_declared={"score": "0.85"})
        )
    assert exc_info.value.token == "uncertainty_declared_invalid"


def test_uncertainty_declared_rejects_oversized_utf8_string() -> None:
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(
            _assert_truth_submission(uncertainty_declared="x" * 513)
        )
    assert exc_info.value.token == "uncertainty_declared_too_long"


def test_uncertainty_declared_is_persisted_on_node_record_when_present() -> None:
    envelope = _assert_truth_submission(uncertainty_declared="bounded-low")
    result = validate_truth_primitive_submission(envelope)
    record = node_record_from_submission(envelope, result)
    assert record["uncertainty_declared"] == "bounded-low"


def test_uncertainty_declared_is_persisted_on_edge_record_when_present(tmp_path) -> None:
    envelope = _validate_claim_submission(uncertainty_declared="audit confidence caveat")
    result = validate_truth_primitive_submission(envelope)
    store = TruthPrimitiveGraphStore(tmp_path / "truth_graph")
    try:
        receipt = write_truth_primitive_result(store, envelope, result)
        assert receipt["edges_written"] == 1
        edge = store.iter_edges()[0]
    finally:
        store.close()
    assert edge["uncertainty_declared"] == "audit confidence caveat"


def test_lineage_independence_score_field_reserved_with_default_none() -> None:
    quote_fields = {field.name: field for field in fields(JuryAssignmentQuote)}
    assert "lineage_independence_score" in quote_fields
    assert quote_fields["lineage_independence_score"].default is None
