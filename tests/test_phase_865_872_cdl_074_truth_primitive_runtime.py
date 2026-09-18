"""CDL-074 truth primitive submission runtime tests — Phases 865–869.

Covers Evidence items 1–10 from the CDL-074 evidence checklist:
  1  Module exists
  2  CDL_074_DEPENDENCY token present
  3  AGENT_ISSUABLE_PRIMITIVES contains all six
  4  validate_truth_primitive_submission present
  5  commit.epoch rejected with commit_epoch_agent_submission_rejected
  6  All six primitives validated (payload + graph-output contract)
  7  refute.claim integrates CDL-052 has_falsifiable_test enforcement
  8  Graph-output contract consistent with CDL-073 schema section
  9  node_submission_runtime.py (CDL-052) unchanged — coexistence confirmed
 10  Historical hardening: CDL-034, CDL-052, CDL-073 guard tests pass
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from ilc_core.epistemic.truth_primitive_submission_runtime import (
    AGENT_ISSUABLE_PRIMITIVES,
    CDL_052_DEPENDENCY,
    CDL_073_DEPENDENCY,
    CDL_074_DEPENDENCY,
    TRUTH_PRIMITIVE_RUNTIME_VERSION,
    EdgeSpec,
    TruthPrimitiveResult,
    validate_truth_primitive_submission,
)
from ilc_core.epistemic.node_submission_runtime import (
    EPISTEMIC_RUNTIME_PART1_VERSION,
    CDL_052_DEPENDENCY as NODE_CDL_052_DEPENDENCY,
)
from ilc_core.node.node_schema_core_runtime_360 import (
    ALLOWED_PRIMITIVE_TYPES,
    SYSTEM_PRIMITIVE_TYPES,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError

_SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "docs" / "specs" / "ilc_layer_0_bundle_schema_section_v0.1.json"
)

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def schema() -> dict:
    with _SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _outer(primitive: str, payload: dict, *, epoch: int = 1) -> dict:
    """Build a minimal valid CDL-073 outer envelope."""
    return {
        "v": 1,
        "primitive": primitive,
        "agent_id": "a" * 96,
        "epoch": epoch,
        "payload": payload,
        "sig": "fakesig",
    }


def _assert_truth_payload(**overrides) -> dict:
    base = {
        "content": {"text": "sample claim"},
        "primitive_type": "knowledge_claim",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    }
    base.update(overrides)
    return base


def _validate_claim_payload(**overrides) -> dict:
    base = {
        "target_node_id": "cid_" + "a" * 59,
        "confidence": "0.9",
        "evidence_summary": "Verified against three independent sources.",
    }
    base.update(overrides)
    return base


def _contradict_assert_payload(**overrides) -> dict:
    base = {
        "node_a_id": "cid_" + "a" * 59,
        "node_b_id": "cid_" + "b" * 59,
        "contradiction_scope": "logical",
        "rationale": "These two claims cannot both be true simultaneously.",
    }
    base.update(overrides)
    return base


def _link_claim_payload(**overrides) -> dict:
    base = {
        "source_node_id": "cid_" + "a" * 59,
        "target_node_id": "cid_" + "b" * 59,
        "link_type": "cites",
        "link_rationale": "Source node cites this evidence directly.",
    }
    base.update(overrides)
    return base


def _refutation_criterion(**overrides) -> dict:
    base = {
        "claim": "X causes Y under conditions Z",
        "evidence_type": "empirical",
        "scope_boundary": "bounded",
        "claim_form": "bounded_existential",
        "has_falsifiable_test": True,
    }
    base.update(overrides)
    return base


def _refute_claim_payload(**overrides) -> dict:
    base = {
        "target_node_id": "cid_" + "a" * 59,
        "refutation_criterion": _refutation_criterion(),
        "evidence_node_ids": [],
    }
    base.update(overrides)
    return base


def _revise_assert_payload(**overrides) -> dict:
    base = {
        "source_node_id": "cid_" + "a" * 59,
        "revised_content": {
            "primitive_type": "knowledge_claim",
            "text": "Revised claim text with correction applied.",
        },
        "revision_rationale": "Original contained an empirical error; corrected per new evidence.",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Evidence 1 — module exists
# ---------------------------------------------------------------------------

def test_truth_primitive_runtime_module_exists():
    """CDL-074 Evidence 1: runtime module is importable."""
    mod = importlib.import_module(
        "ilc_core.epistemic.truth_primitive_submission_runtime"
    )
    assert mod is not None


# ---------------------------------------------------------------------------
# Evidence 2 — dependency tokens
# ---------------------------------------------------------------------------

def test_cdl_074_dependency_token():
    assert CDL_074_DEPENDENCY == "cdl_074_truth_primitive_runtime_ratified.v0.1"


def test_cdl_073_dependency_token():
    assert CDL_073_DEPENDENCY == "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"


def test_cdl_052_dependency_token():
    assert CDL_052_DEPENDENCY == "cdl_052_ratified_466.v0.1"


def test_version_token_contains_868():
    assert "868" in TRUTH_PRIMITIVE_RUNTIME_VERSION


# ---------------------------------------------------------------------------
# Evidence 3 — AGENT_ISSUABLE_PRIMITIVES contains all six
# ---------------------------------------------------------------------------

def test_agent_issuable_primitives_complete():
    expected = {
        "assert.truth", "validate.claim", "contradict.assert",
        "refute.claim", "revise.assert", "link.claim",
    }
    assert AGENT_ISSUABLE_PRIMITIVES == expected


def test_commit_epoch_not_in_agent_issuable_primitives():
    assert "commit.epoch" not in AGENT_ISSUABLE_PRIMITIVES


# ---------------------------------------------------------------------------
# Evidence 4 — validate_truth_primitive_submission present and callable
# ---------------------------------------------------------------------------

def test_validate_truth_primitive_submission_is_callable():
    assert callable(validate_truth_primitive_submission)


# ---------------------------------------------------------------------------
# Evidence 5 — commit.epoch rejected
# ---------------------------------------------------------------------------

def test_commit_epoch_agent_submission_rejected():
    """CDL-074 Evidence 5: commit.epoch raises with correct token."""
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(
            _outer("commit.epoch", {"epoch_id": 1})
        )
    assert exc_info.value.token == "commit_epoch_agent_submission_rejected"


def test_commit_epoch_rejection_message_is_informative():
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(
            _outer("commit.epoch", {})
        )
    assert "consensus-layer only" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Outer envelope validation
# ---------------------------------------------------------------------------

def test_wrong_protocol_version_rejected():
    envelope = _outer("assert.truth", _assert_truth_payload())
    envelope["v"] = 2
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(envelope)
    assert "protocol_version_invalid" in exc_info.value.token


def test_unknown_primitive_rejected():
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(
            _outer("invent.claim", {})
        )
    assert "primitive_unknown" in exc_info.value.token


def test_missing_agent_id_rejected():
    envelope = _outer("assert.truth", _assert_truth_payload())
    del envelope["agent_id"]
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(envelope)
    assert "agent_id_missing" in exc_info.value.token


@pytest.mark.parametrize(
    "bad_agent_id",
    [
        "a" * 95,
        "a" * 97,
        "a" * 64,
        "A" * 96,
        "agent-test-874",
        b"a" * 96,
    ],
)
def test_noncanonical_agent_id_rejected(bad_agent_id):
    envelope = _outer("assert.truth", _assert_truth_payload())
    envelope["agent_id"] = bad_agent_id
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(envelope)
    assert "agent_id_invalid" in exc_info.value.token


def test_negative_epoch_rejected():
    envelope = _outer("assert.truth", _assert_truth_payload(), epoch=-1)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(envelope)
    assert "epoch_invalid" in exc_info.value.token


def test_non_dict_submission_rejected():
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission("not a dict")
    assert "submission_must_be_dict" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 6 — assert.truth (Phase 865)
# ---------------------------------------------------------------------------

def test_assert_truth_valid_returns_result():
    result = validate_truth_primitive_submission(
        _outer("assert.truth", _assert_truth_payload())
    )
    assert isinstance(result, TruthPrimitiveResult)
    assert result.primitive == "assert.truth"
    assert result.creates_node is True
    assert result.node_primitive_type == "knowledge_claim"


def test_assert_truth_produces_asserted_by_edge():
    result = validate_truth_primitive_submission(
        _outer("assert.truth", _assert_truth_payload())
    )
    edge_types = {e.edge_type for e in result.edges}
    assert "asserted_by" in edge_types


def test_assert_truth_extends_edge_per_parent():
    parents = ["cid_" + "a" * 59, "cid_" + "b" * 59]
    payload = _assert_truth_payload(parent_node_ids=parents)
    result = validate_truth_primitive_submission(_outer("assert.truth", payload))
    extends_edges = [e for e in result.edges if e.edge_type == "extends"]
    assert len(extends_edges) == 2


def test_assert_truth_no_parents_no_extends_edge():
    result = validate_truth_primitive_submission(
        _outer("assert.truth", _assert_truth_payload(parent_node_ids=[]))
    )
    extends_edges = [e for e in result.edges if e.edge_type == "extends"]
    assert len(extends_edges) == 0


def test_assert_truth_invalid_epistemic_type_rejected():
    payload = _assert_truth_payload(epistemic_type="speculative")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("assert.truth", payload))
    assert "epistemic_type" in exc_info.value.token


def test_assert_truth_unknown_primitive_type_rejected():
    payload = _assert_truth_payload(primitive_type="invented_type")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("assert.truth", payload))
    assert "primitive_type_not_allowed" in exc_info.value.token


def test_assert_truth_system_primitive_type_allowed():
    """genesis_authority_assertion is in SYSTEM_PRIMITIVE_TYPES and must be allowed."""
    payload = _assert_truth_payload(primitive_type="genesis_authority_assertion")
    result = validate_truth_primitive_submission(_outer("assert.truth", payload))
    assert result.node_primitive_type == "genesis_authority_assertion"


def test_assert_truth_missing_content_rejected():
    payload = _assert_truth_payload()
    del payload["content"]
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("assert.truth", payload))
    assert "content" in exc_info.value.token


def test_assert_truth_missing_parent_node_ids_rejected():
    payload = _assert_truth_payload()
    del payload["parent_node_ids"]
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("assert.truth", payload))
    assert "parent_node_ids" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 6 — validate.claim (Phase 865)
# ---------------------------------------------------------------------------

def test_validate_claim_valid_returns_result():
    result = validate_truth_primitive_submission(
        _outer("validate.claim", _validate_claim_payload())
    )
    assert result.primitive == "validate.claim"
    assert result.creates_node is False
    assert result.node_primitive_type is None


def test_validate_claim_produces_validated_by_edge():
    result = validate_truth_primitive_submission(
        _outer("validate.claim", _validate_claim_payload())
    )
    assert any(e.edge_type == "validated_by" for e in result.edges)


def test_validate_claim_validated_by_edge_semantics():
    result = validate_truth_primitive_submission(
        _outer("validate.claim", _validate_claim_payload())
    )
    edge = next(e for e in result.edges if e.edge_type == "validated_by")
    assert edge.source == "target_node_id"
    assert edge.target == "agent_id"


def test_validate_claim_confidence_zero_rejected():
    payload = _validate_claim_payload(confidence="0")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("validate.claim", payload))
    assert "confidence" in exc_info.value.token


def test_validate_claim_confidence_above_one_rejected():
    payload = _validate_claim_payload(confidence="1.1")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("validate.claim", payload))
    assert "confidence" in exc_info.value.token


def test_validate_claim_confidence_not_string_rejected():
    payload = _validate_claim_payload(confidence=0.9)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("validate.claim", payload))
    assert "confidence" in exc_info.value.token


def test_validate_claim_evidence_summary_too_long_rejected():
    payload = _validate_claim_payload(evidence_summary="x" * 1025)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("validate.claim", payload))
    assert "evidence_summary_too_long" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 6 — contradict.assert (Phase 866)
# ---------------------------------------------------------------------------

def test_contradict_assert_valid_returns_result():
    result = validate_truth_primitive_submission(
        _outer("contradict.assert", _contradict_assert_payload())
    )
    assert result.primitive == "contradict.assert"
    assert result.creates_node is False


def test_contradict_assert_produces_contradicts_edge():
    result = validate_truth_primitive_submission(
        _outer("contradict.assert", _contradict_assert_payload())
    )
    assert any(e.edge_type == "contradicts" for e in result.edges)


def test_contradict_assert_same_node_rejected():
    cid = "cid_" + "a" * 59
    payload = _contradict_assert_payload(node_a_id=cid, node_b_id=cid)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("contradict.assert", payload))
    assert "contradict_assert_same_node" in exc_info.value.token


def test_contradict_assert_invalid_scope_rejected():
    payload = _contradict_assert_payload(contradiction_scope="philosophical")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("contradict.assert", payload))
    assert "contradiction_scope" in exc_info.value.token


def test_contradict_assert_rationale_too_long_rejected():
    payload = _contradict_assert_payload(rationale="r" * 2049)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("contradict.assert", payload))
    assert "rationale_too_long" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 6 — link.claim (Phase 866)
# ---------------------------------------------------------------------------

def test_link_claim_valid_returns_result():
    result = validate_truth_primitive_submission(
        _outer("link.claim", _link_claim_payload())
    )
    assert result.primitive == "link.claim"
    assert result.creates_node is False


def test_link_claim_edge_type_matches_link_type():
    for link_type in ("cites", "elaborates", "contrasts", "instantiates", "generalizes"):
        payload = _link_claim_payload(link_type=link_type)
        result = validate_truth_primitive_submission(_outer("link.claim", payload))
        assert any(e.edge_type == link_type for e in result.edges), (
            f"expected edge type {link_type!r}"
        )


def test_link_claim_same_node_rejected():
    cid = "cid_" + "a" * 59
    payload = _link_claim_payload(source_node_id=cid, target_node_id=cid)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("link.claim", payload))
    assert "link_claim_same_node" in exc_info.value.token


def test_link_claim_invalid_link_type_rejected():
    payload = _link_claim_payload(link_type="supports")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("link.claim", payload))
    assert "link_type" in exc_info.value.token


def test_link_claim_rationale_too_long_rejected():
    payload = _link_claim_payload(link_rationale="x" * 1025)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("link.claim", payload))
    assert "link_rationale_too_long" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 6 + 7 — refute.claim (Phase 867)
# ---------------------------------------------------------------------------

def test_refute_claim_valid_returns_result():
    result = validate_truth_primitive_submission(
        _outer("refute.claim", _refute_claim_payload())
    )
    assert result.primitive == "refute.claim"
    assert result.creates_node is False


def test_refute_claim_produces_refuted_by_edge():
    result = validate_truth_primitive_submission(
        _outer("refute.claim", _refute_claim_payload())
    )
    assert any(e.edge_type == "refuted_by" for e in result.edges)


def test_refute_claim_supported_by_edge_per_evidence():
    evidence = ["cid_" + "a" * 59, "cid_" + "b" * 59]
    payload = _refute_claim_payload(evidence_node_ids=evidence)
    result = validate_truth_primitive_submission(_outer("refute.claim", payload))
    supported = [e for e in result.edges if e.edge_type == "supported_by"]
    assert len(supported) == 2


def test_refute_claim_has_falsifiable_test_false_rejected():
    """CDL-074 Evidence 7: has_falsifiable_test=False rejected (CDL-052)."""
    criterion = _refutation_criterion(has_falsifiable_test=False)
    payload = _refute_claim_payload(refutation_criterion=criterion)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("refute.claim", payload))
    assert "falsifiable" in exc_info.value.token.lower() or "falsifiable" in str(exc_info.value).lower()


def test_refute_claim_missing_criterion_rejected():
    payload = _refute_claim_payload()
    del payload["refutation_criterion"]
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("refute.claim", payload))
    assert "refutation_criterion" in exc_info.value.token


def test_refute_claim_criterion_missing_required_field_rejected():
    criterion = _refutation_criterion()
    del criterion["claim"]
    payload = _refute_claim_payload(refutation_criterion=criterion)
    with pytest.raises(EpistemicSubmissionError):
        validate_truth_primitive_submission(_outer("refute.claim", payload))


# ---------------------------------------------------------------------------
# Evidence 6 — revise.assert (Phase 868)
# ---------------------------------------------------------------------------

def test_revise_assert_valid_returns_result():
    result = validate_truth_primitive_submission(
        _outer("revise.assert", _revise_assert_payload())
    )
    assert result.primitive == "revise.assert"
    assert result.creates_node is True
    assert result.node_primitive_type == "knowledge_claim"


def test_revise_assert_produces_three_edges():
    result = validate_truth_primitive_submission(
        _outer("revise.assert", _revise_assert_payload())
    )
    edge_types = {e.edge_type for e in result.edges}
    assert edge_types == {"asserted_by", "revision_of", "revised_by"}


def test_revise_assert_revision_of_edge_semantics():
    result = validate_truth_primitive_submission(
        _outer("revise.assert", _revise_assert_payload())
    )
    edge = next(e for e in result.edges if e.edge_type == "revision_of")
    assert edge.source == "new_node_id"
    assert edge.target == "source_node_id"


def test_revise_assert_revised_by_edge_semantics():
    result = validate_truth_primitive_submission(
        _outer("revise.assert", _revise_assert_payload())
    )
    edge = next(e for e in result.edges if e.edge_type == "revised_by")
    assert edge.source == "source_node_id"
    assert edge.target == "new_node_id"


def test_revise_assert_unknown_revised_primitive_type_rejected():
    payload = _revise_assert_payload(
        revised_content={"primitive_type": "invented_type", "text": "x"}
    )
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("revise.assert", payload))
    assert "primitive_type" in exc_info.value.token


def test_revise_assert_missing_revised_content_rejected():
    payload = _revise_assert_payload()
    del payload["revised_content"]
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("revise.assert", payload))
    assert "revised_content" in exc_info.value.token


def test_revise_assert_rationale_too_long_rejected():
    payload = _revise_assert_payload(revision_rationale="r" * 2049)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(_outer("revise.assert", payload))
    assert "revision_rationale_too_long" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 8 — graph-output contract consistent with CDL-073 schema section
# ---------------------------------------------------------------------------

def test_assert_truth_graph_output_matches_schema(schema):
    """assert.truth creates a node — consistent with CDL-073 schema."""
    prim = schema["primitives"]["assert.truth"]
    assert prim["graph_output"]["creates_node"] is True
    result = validate_truth_primitive_submission(
        _outer("assert.truth", _assert_truth_payload())
    )
    assert result.creates_node is True


def test_validate_claim_graph_output_matches_schema(schema):
    prim = schema["primitives"]["validate.claim"]
    assert prim["graph_output"]["creates_node"] is False
    result = validate_truth_primitive_submission(
        _outer("validate.claim", _validate_claim_payload())
    )
    assert result.creates_node is False


def test_contradict_assert_graph_output_matches_schema(schema):
    prim = schema["primitives"]["contradict.assert"]
    assert prim["graph_output"]["creates_node"] is False
    result = validate_truth_primitive_submission(
        _outer("contradict.assert", _contradict_assert_payload())
    )
    assert result.creates_node is False


def test_refute_claim_graph_output_matches_schema(schema):
    prim = schema["primitives"]["refute.claim"]
    assert prim["graph_output"]["creates_node"] is False
    result = validate_truth_primitive_submission(
        _outer("refute.claim", _refute_claim_payload())
    )
    assert result.creates_node is False


def test_revise_assert_graph_output_matches_schema(schema):
    prim = schema["primitives"]["revise.assert"]
    assert prim["graph_output"]["creates_node"] is True
    result = validate_truth_primitive_submission(
        _outer("revise.assert", _revise_assert_payload())
    )
    assert result.creates_node is True


def test_link_claim_graph_output_matches_schema(schema):
    prim = schema["primitives"]["link.claim"]
    assert prim["graph_output"]["creates_node"] is False
    result = validate_truth_primitive_submission(
        _outer("link.claim", _link_claim_payload())
    )
    assert result.creates_node is False


# ---------------------------------------------------------------------------
# Evidence 9 — CDL-052 node_submission_runtime coexistence
# ---------------------------------------------------------------------------

def test_cdl_052_node_submission_runtime_version_unchanged():
    """CDL-074 Evidence 9: CDL-052 runtime version constant is unchanged."""
    assert EPISTEMIC_RUNTIME_PART1_VERSION == "epistemic_node_submission_runtime_477.v0.1"


def test_cdl_052_dependency_consistent():
    assert NODE_CDL_052_DEPENDENCY == CDL_052_DEPENDENCY


def test_both_runtimes_importable_without_collision():
    """Both runtimes live in ilc_core/epistemic/ without import collision."""
    import ilc_core.epistemic.node_submission_runtime as m1
    import ilc_core.epistemic.truth_primitive_submission_runtime as m2
    assert m1 is not m2
    assert hasattr(m1, "validate_epistemic_node_submission")
    assert hasattr(m2, "validate_truth_primitive_submission")


# ---------------------------------------------------------------------------
# Evidence 10 — historical hardening (CDL-034, CDL-073)
# ---------------------------------------------------------------------------

def test_allowed_primitive_types_still_contains_cdl_034_set():
    """CDL-034 ALLOWED_PRIMITIVE_TYPES unchanged by CDL-074."""
    expected_min = {
        "citation", "execution_descriptor", "governance_proposal",
        "knowledge_claim", "observation",
    }
    assert expected_min.issubset(set(ALLOWED_PRIMITIVE_TYPES))


def test_system_primitive_types_disjoint_from_allowed_unchanged():
    """SYSTEM_PRIMITIVE_TYPES still disjoint from ALLOWED_PRIMITIVE_TYPES."""
    assert not (SYSTEM_PRIMITIVE_TYPES & set(ALLOWED_PRIMITIVE_TYPES))


def test_cdl_073_schema_section_still_present():
    """CDL-073 Layer 0 bundle schema section artifact unchanged."""
    assert _SCHEMA_PATH.exists()
    with _SCHEMA_PATH.open("r", encoding="utf-8") as f:
        s = json.load(f)
    assert s["_meta"]["token"] == "hb_003_layer_0_bundle_schema_section"
    assert s["_meta"]["cdl_dependency"] == "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"


def test_cdl_074_does_not_extend_allowed_primitive_types():
    """ALLOWED_PRIMITIVE_TYPES must not include truth primitive verbs."""
    truth_verbs = {
        "assert.truth", "validate.claim", "contradict.assert",
        "refute.claim", "revise.assert", "link.claim", "commit.epoch",
    }
    assert not (truth_verbs & set(ALLOWED_PRIMITIVE_TYPES))
