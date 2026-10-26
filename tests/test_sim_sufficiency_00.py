from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "sim" / "sim_sufficiency_00.py"
SPEC = importlib.util.spec_from_file_location("sim_sufficiency_00", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load sim_sufficiency_00 module")
sim = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sim
SPEC.loader.exec_module(sim)


def records():
    return copy.deepcopy(sim.build_results())


def by_id(items, example_id):
    return next(item for item in items if item["example_id"] == example_id)


def all_errors(items):
    return sim.validate_examples(items) + sim.check_mathematical_invariants(items)


def assert_rejected(items, fragment):
    errors = all_errors(items)
    assert errors
    assert any(fragment in error for error in errors), errors


def test_reference_records_pass_both_layers():
    items = records()
    assert sim.validate_examples(items) == []
    assert sim.check_mathematical_invariants(items) == []


def test_exhaustive_counts_are_fixture_derived():
    items = records()
    assert by_id(items, "E1")["exhaustive_check_receipt"]["actual_check_count"] == 625
    assert by_id(items, "E2b")["exhaustive_check_receipt"]["actual_check_count"] == 125


def test_none_receipt_is_rejected():
    items = records()
    by_id(items, "E2a")["witness_receipt"] = None
    assert_rejected(items, "witness_receipt must be an object")


def test_none_in_each_required_receipt_field_is_rejected():
    exhaustive_fields = (
        "domain_size",
        "action_count",
        "expected_check_count",
        "actual_check_count",
        "coverage_complete",
        "all_checked",
        "checker_id",
        "checker_version",
    )
    for field in exhaustive_fields:
        items = records()
        by_id(items, "E1")["exhaustive_check_receipt"][field] = None
        assert all_errors(items), field
    witness_fields = (
        "state_a",
        "state_b",
        "action",
        "separation_reason",
        "retained_a",
        "retained_b",
        "behavior_a",
        "behavior_b",
        "checker_id",
        "checker_version",
    )
    for field in witness_fields:
        items = records()
        by_id(items, "E2a")["witness_receipt"][field] = None
        assert all_errors(items), field


def test_empty_string_receipt_is_rejected():
    items = records()
    by_id(items, "E1")["exhaustive_check_receipt"] = ""
    assert_rejected(items, "exhaustive_check_receipt must be an object")


def test_invalid_count_types_and_bounds_are_rejected():
    for field in (
        "domain_size",
        "action_count",
        "expected_check_count",
        "actual_check_count",
    ):
        for invalid in (True, "625", 0, -1):
            items = records()
            by_id(items, "E1")["exhaustive_check_receipt"][field] = invalid
            assert_rejected(items, f"{field} must be a positive integer")


def test_empty_checker_identity_or_version_is_rejected():
    for example_id, receipt_name in (
        ("E1", "exhaustive_check_receipt"),
        ("E2a", "witness_receipt"),
    ):
        for field in ("checker_id", "checker_version"):
            items = records()
            by_id(items, example_id)[receipt_name][field] = ""
            assert_rejected(items, f"{field} must be a nonempty string")


def test_state_outside_declared_domain_is_rejected():
    items = records()
    by_id(items, "E2a")["witness_receipt"]["state_b"] = [9, 9]
    assert_rejected(items, "witness state outside declared domain")


def test_action_outside_declared_domain_is_rejected():
    items = records()
    by_id(items, "E3")["witness_receipt"]["action"] = 9
    assert_rejected(items, "witness action outside declared domain")


def test_receipt_values_inconsistent_with_recomputation_are_rejected():
    items = records()
    by_id(items, "E2a")["witness_receipt"]["behavior_b"] = {"admitted": True}
    assert_rejected(items, "behavior_b does not match recomputation")


def test_retained_value_inconsistent_with_recomputation_is_rejected():
    items = records()
    by_id(items, "E2a")["witness_receipt"]["retained_b"] = 4
    assert_rejected(items, "retained_b does not match recomputation")


def test_correct_witness_attached_to_wrong_example_is_rejected():
    items = records()
    by_id(items, "E3")["witness_receipt"] = copy.deepcopy(
        by_id(items, "E2a")["witness_receipt"]
    )
    assert_rejected(items, "behavior_b does not match recomputation")


def test_e1_cannot_claim_e2b_check_count():
    items = records()
    receipt = by_id(items, "E1")["exhaustive_check_receipt"]
    receipt["expected_check_count"] = 125
    receipt["actual_check_count"] = 125
    assert_rejected(items, "expected_check_count does not match recomputation")


def test_e5_cannot_carry_e2a_witness():
    items = records()
    by_id(items, "E5")["witness_receipt"] = copy.deepcopy(
        by_id(items, "E2a")["witness_receipt"]
    )
    assert_rejected(items, "witness state outside declared domain")


def test_e5_unsupported_symbolic_assumptions_are_rejected():
    items = records()
    by_id(items, "E5")["verification_method_limit"] = (
        "real-exponential softmax is monotone"
    )
    assert_rejected(items, "unsupported symbolic assumptions")


def test_missing_claim_verdict_is_rejected():
    items = records()
    del by_id(items, "E1")["claim_verdict"]
    assert_rejected(items, "missing or null claim_verdict")


def test_wrong_evidence_type_is_rejected():
    items = records()
    by_id(items, "E1")["evidence_type"] = "sampled_testing"
    assert_rejected(items, "evidence_type differs from anchored expectation")


def test_duplicate_example_id_is_rejected():
    items = records()
    items[-1]["example_id"] = "E1"
    assert_rejected(items, "duplicate example_id")


def test_unexpected_example_id_is_rejected():
    items = records()
    items[-1]["example_id"] = "E6"
    assert_rejected(items, "unexpected example_id")


def test_schema_validator_does_not_claim_mathematical_verification():
    items = records()
    by_id(items, "E2a")["witness_receipt"]["behavior_b"] = {
        "admitted": True,
        "output": 99,
        "successor_retained": 0,
        "effects": [],
    }
    assert sim.validate_examples(items) == []
    assert any(
        "behavior_b does not match recomputation" in error
        for error in sim.check_mathematical_invariants(items)
    )


def test_symbolic_e5_fixture_is_checked_without_float_evaluation():
    items = records()
    e5 = by_id(items, "E5")
    assert e5["witness_receipt"]["behavior_a"]["attention_output"] == "tanh(1)"
    assert e5["witness_receipt"]["behavior_b"]["attention_output"] == "-tanh(1)"
    assert e5["witness_receipt"]["behavior_a"]["numerator_terms"] == [
        {"coefficient": 1, "exponent": 1},
        {"coefficient": -1, "exponent": -1},
    ]
    assert sim.check_mathematical_invariants(items) == []


def test_source_fixture_hash_is_pinned():
    assert sim.verify_source_fixture() == []


def test_results_contain_no_binary_floats():
    def walk(value):
        assert not isinstance(value, float)
        if isinstance(value, dict):
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(records())


def test_valid_math_never_becomes_authorized_reuse_in_research_fixture():
    items = records()
    for example_id in ("E1", "E2b"):
        item = by_id(items, example_id)
        assert item["claim_verdict"] == "valid"
        assert item["aggregate_decision"] == "unresolved_pending_evidence"
        assert item["capsule_assessments"]["current_observer_permission"] == "unresolved"


def test_atomic_generation_and_cli_verification(tmp_path):
    generation = subprocess.run(
        ["python", str(MODULE_PATH), "--generate", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert generation.returncode == 0, generation.stderr
    result_path = tmp_path / "sim_results.json"
    document_path = tmp_path / "sim_doc.md"
    assert result_path.is_file()
    assert document_path.is_file()
    assert len(json.loads(result_path.read_text())) == 6
    verification = subprocess.run(
        ["python", str(MODULE_PATH), "--verify", str(result_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert verification.returncode == 0, verification.stdout + verification.stderr
    assert "OK: all 6 records pass" in verification.stdout


def test_selected_runner_failure_propagates_without_fallback(tmp_path):
    fallback_marker = tmp_path / "fallback-ran"
    selected_runner = tmp_path / "selected-runner.sh"
    alternative_runner = tmp_path / "alternative-runner.sh"
    selected_runner.write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "EXPECTED: mandatory runner failure"\nexit 23\n'
    )
    alternative_runner.write_text(
        f"#!/usr/bin/env bash\ntouch {fallback_marker!s}\nexit 0\n"
    )
    selected_runner.chmod(0o700)
    alternative_runner.chmod(0o700)
    command = (
        f"{selected_runner!s} 2>&1 | tail -20"
    )
    result = subprocess.run(
        ["bash", "-o", "pipefail", "-c", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 23
    assert result.stdout.strip() == "EXPECTED: mandatory runner failure"
    assert not fallback_marker.exists()


def test_every_mathematical_claim_field_is_required():
    for field in sim.MATHEMATICAL_CLAIM_KEYS:
        items = records()
        del by_id(items, "E1")["sufficiency_claim"]["mathematical_claim"][field]
        assert all_errors(items), field


def test_every_mathematical_claim_field_rejects_wrong_value():
    for field in sim.MATHEMATICAL_CLAIM_KEYS:
        items = records()
        by_id(items, "E1")["sufficiency_claim"]["mathematical_claim"][field] = (
            "fixture:wrong-value"
        )
        assert all_errors(items), field


def test_every_eligibility_field_is_required():
    for field in sim.ELIGIBILITY_KEYS:
        items = records()
        del by_id(items, "E1")["sufficiency_claim"]["eligibility_assessment"][field]
        assert all_errors(items), field


def test_every_eligibility_field_rejects_wrong_value():
    for field in sim.ELIGIBILITY_KEYS:
        items = records()
        by_id(items, "E1")["sufficiency_claim"]["eligibility_assessment"][field] = (
            "fixture:wrong-value"
        )
        assert all_errors(items), field


def test_e5_requires_formal_derivation_and_bound_premises():
    items = records()
    item = by_id(items, "E5")
    claim = item["sufficiency_claim"]["mathematical_claim"]
    assert claim["verification_method"] == "formal_derivation"
    assert claim["assumption_refs"]
    claim["verification_method"] = "bounded_model_check"
    assert all_errors(items)


@pytest.mark.parametrize(
    ("target_path", "extra_key"),
    [
        (("sufficiency_claim", "mathematical_claim"), "unknown_claim_field"),
        (("sufficiency_claim", "eligibility_assessment"), "unknown_eligibility_field"),
        (
            ("sufficiency_claim", "mathematical_claim", "evidence_commitment"),
            "unknown_commitment_field",
        ),
        (("exhaustive_check_receipt",), "unknown_receipt_field"),
    ],
)
def test_unknown_schema_fields_are_rejected(target_path, extra_key):
    items = records()
    target = by_id(items, "E1")
    for part in target_path:
        target = target[part]
    target[extra_key] = "not allowed"
    assert all_errors(items)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("hash_algorithm", "sha512"),
        ("digest", "a" * 63 + "Z"),
        ("media_type", "application/json"),
        ("byte_length", True),
        ("evidence_ref", "fixture:receipt:E2a"),
    ],
)
def test_each_commitment_field_is_bound(field, invalid):
    items = records()
    commitment = by_id(items, "E1")["sufficiency_claim"]["mathematical_claim"][
        "evidence_commitment"
    ]
    commitment[field] = invalid
    assert all_errors(items)


def test_mutated_receipt_with_unchanged_commitment_is_rejected():
    items = records()
    by_id(items, "E2a")["witness_receipt"]["behavior_b"]["output"] = 2
    assert_rejected(items, "commitment digest does not match submitted receipt")


def test_mathematically_false_receipt_with_matching_commitment_is_rejected():
    items = records()
    item = by_id(items, "E2a")
    item["witness_receipt"]["behavior_b"]["output"] = 2
    raw = json.dumps(
        item["witness_receipt"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    commitment = item["sufficiency_claim"]["mathematical_claim"]["evidence_commitment"]
    commitment["digest"] = hashlib.sha256(raw).hexdigest()
    commitment["byte_length"] = len(raw)
    assert_rejected(items, "submitted receipt differs from independent recomputation")


@pytest.mark.parametrize("invalid", [True, 0.0])
def test_retained_exact_integer_type_is_enforced(invalid):
    items = records()
    by_id(items, "E2a")["witness_receipt"]["retained_a"] = invalid
    assert all_errors(items)


def test_nested_behavior_boolean_type_is_enforced():
    items = records()
    by_id(items, "E2a")["witness_receipt"]["behavior_a"]["admitted"] = 1
    assert all_errors(items)


@pytest.mark.parametrize(
    "payload",
    [
        '[{"value":NaN}]',
        '[{"value":Infinity}]',
        '[{"value":1.0}]',
        '[{"a":1,"a":2}]',
        '[{"value":9007199254740993}]',
    ],
)
def test_strict_json_tokens_are_rejected(tmp_path, payload):
    path = tmp_path / "invalid.json"
    path.write_text(payload, encoding="utf-8")
    parsed, error = sim._load_results_json(path)
    assert parsed is None
    assert error is not None


def test_json_structural_bounds_are_rejected(tmp_path):
    cases = {
        "deep.json": "[" * 20 + "0" + "]" * 20,
        "long_key.json": '[{"' + "k" * (sim._MAX_STRING_LEN + 1) + '":0}]',
        "long_array.json": "[" + ",".join("0" for _ in range(1001)) + "]",
    }
    for name, payload in cases.items():
        path = tmp_path / name
        path.write_text(payload, encoding="utf-8")
        parsed, error = sim._load_results_json(path)
        assert parsed is None, name
        assert error is not None, name


def test_json_file_and_encoding_guards(tmp_path):
    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b"[" + b"0" * sim._MAX_RESULTS_BYTES + b"]")
    invalid_utf8 = tmp_path / "invalid_utf8.json"
    invalid_utf8.write_bytes(b"[\xff\xfe]")
    non_array = tmp_path / "non_array.json"
    non_array.write_text("{}", encoding="utf-8")
    for path in (oversized, invalid_utf8, non_array):
        parsed, error = sim._load_results_json(path)
        assert parsed is None
        assert error is not None


def test_source_fixture_missing_and_tampered_paths(tmp_path, monkeypatch):
    missing = tmp_path / "missing.py.bak"
    monkeypatch.setattr(sim, "SOURCE_FIXTURE_PATH", missing)
    assert any("unable to read" in error for error in sim.verify_source_fixture())
    tampered = tmp_path / "tampered.py.bak"
    tampered.write_bytes(b"tampered")
    monkeypatch.setattr(sim, "SOURCE_FIXTURE_PATH", tampered)
    assert any("hash mismatch" in error for error in sim.verify_source_fixture())


def test_non_container_guards_and_unsupported_e5_state():
    assert sim.validate_examples(None) == ["results must be an array"]
    assert sim.validate_examples("string") == ["results must be an array"]
    assert sim.check_mathematical_invariants(None) == ["results must be an array"]
    assert sim._record_errors("not_a_dict", 0) == ["record[0]: must be an object"]
    with pytest.raises(ValueError, match="unsupported E5 fixture state"):
        sim._e5_behavior((99, 99), "evaluate_attention")


def test_e5_claim_method_and_premises_are_exact():
    e5 = by_id(records(), "E5")
    claim = e5["sufficiency_claim"]["mathematical_claim"]
    assert e5["verification_method"] == "symbolic_argument"
    assert claim["verification_method"] == "formal_derivation"
    assert claim["assumption_refs"] == sim.E5_ASSUMPTION_REFS


def test_independent_finite_oracle_without_sim_behavior_helpers():
    states = tuple((left, right) for left in range(5) for right in range(5))
    actions = tuple(range(5))

    e1_checks = 0
    for state_a in states:
        for state_b in states:
            if sum(state_a) % 5 != sum(state_b) % 5:
                continue
            for action in actions:
                e1_checks += 1
                behavior_a = (
                    True,
                    sum(state_a) % 5,
                    (sum(state_a) + 3 * action) % 5,
                    (),
                )
                behavior_b = (
                    True,
                    sum(state_b) % 5,
                    (sum(state_b) + 3 * action) % 5,
                    (),
                )
                assert behavior_a == behavior_b
    assert e1_checks == 625

    e2b_checks = 0
    for state_a in states:
        rep_a = (sum(state_a) % 5, state_a[0])
        for state_b in states:
            rep_b = (sum(state_b) % 5, state_b[0])
            if rep_a != rep_b:
                continue
            assert state_a == state_b
            for action in actions:
                e2b_checks += 1
                behavior_a = (
                    True,
                    state_a[0],
                    ((sum(state_a) + 3 * action) % 5, (state_a[0] + action) % 5),
                    (),
                )
                behavior_b = (
                    True,
                    state_b[0],
                    ((sum(state_b) + 3 * action) % 5, (state_b[0] + action) % 5),
                    (),
                )
                assert behavior_a == behavior_b
    assert e2b_checks == 125

    state_a, state_b = (0, 0), (1, 4)
    assert sum(state_a) % 5 == sum(state_b) % 5 == 0
    assert state_a[0] != state_b[0]
    assert (state_a[0] == 0) is True
    assert (state_b[0] == 0) is False

    assert ((-1) * (-1), 1 * 1) == (1, 1)
    assert -(-1) != -(1)

    keys_a, keys_b = (1, -1), (-1, 1)
    assert sum(keys_a) == sum(keys_b) == 0
    assert sum(key * key for key in keys_a) == 2
    assert sum(key * key for key in keys_b) == 2
    numerator_a = ((1, 1), (-1, -1))
    numerator_b = ((1, -1), (-1, 1))
    denominator_a = ((1, 1), (1, -1))
    denominator_b = ((1, -1), (1, 1))
    assert numerator_b == tuple((coefficient, -exponent) for coefficient, exponent in numerator_a)
    assert sorted(denominator_a) == sorted(denominator_b)
    assert sim.E5_ASSUMPTION_REFS == [
        "fixture:assumption:attention_q1_scale1_values_1_neg1_real_exp_softmax",
        "fixture:assumption:tanh_is_odd",
        "fixture:assumption:tanh_of_1_positive",
    ]
