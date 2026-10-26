from __future__ import annotations

import copy
import hashlib
import json
import struct
from pathlib import Path

import pytest

from tools.sim.sim_sufficiency_package_tensor_00 import (
    TENSOR_DESCRIPTOR_KEYS,
    FixtureValidationError,
    build_tensor_fixture,
    run_demonstrations,
    validate_tensor_fixture,
    verify_bsd3_license_text,
    verify_package_fixture,
    write_results,
)


# NumPy is a declared project dependency. The driver verifies the installed
# distribution's BSD-3-Clause license text before using numpy.gcd.


def test_demonstrations_match_independent_references():
    results = run_demonstrations()
    assert results["schema_version"] == "sufficiency_package_tensor_demo_v0"
    assert [item["type"] for item in results["demonstrations"]] == [
        "package_function",
        "tensor_numerical",
    ]
    assert all(item["match"] for item in results["demonstrations"])
    assert [item["reference_output"] for item in results["demonstrations"]] == [6, 10]
    assert [item["interpreter_output"] for item in results["demonstrations"]] == [6, 10]
    assert [item["handler_call_count"] for item in results["demonstrations"]] == [1, 1]


def test_package_license_and_exact_artifact_are_verified():
    fixture = verify_package_fixture()
    assert fixture["license"]["spdx"] == "BSD-3-Clause"
    assert fixture["license"]["verified"] is True
    assert len(fixture["artifact_sha256"]) == 64
    assert fixture["implementation_ref"].startswith(
        f"sha256:{fixture['artifact_sha256']}#numpy.gcd@"
    )


def test_incomplete_license_text_is_rejected():
    with pytest.raises(FixtureValidationError, match="package_license_not_verified"):
        verify_bsd3_license_text("BSD")


def test_tampered_package_artifact_rejects_before_invocation(tmp_path):
    fixture = verify_package_fixture()
    from numpy._core import _multiarray_umath

    original = Path(_multiarray_umath.__file__).read_bytes()
    tampered = tmp_path / "tampered_numpy_extension.bin"
    tampered.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    calls = 0
    with pytest.raises(FixtureValidationError, match="package_artifact_digest_mismatch"):
        verify_package_fixture(
            artifact_path=tampered,
            expected_sha256=fixture["artifact_sha256"],
        )
    assert calls == 0


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"expected_version": "0.invalid"}, "package_version_mismatch"),
        ({"operation_id": "numpy.add"}, "package_operation_identity_mismatch"),
        ({"expected_sha256": "0" * 64}, "package_expected_digest_mismatch"),
    ],
)
def test_package_labels_cannot_override_verified_identity(kwargs, error):
    with pytest.raises(FixtureValidationError, match=error):
        verify_package_fixture(**kwargs)


def test_arbitrary_file_cannot_be_labeled_as_numpy_implementation(tmp_path):
    fake = tmp_path / "not_numpy.bin"
    fake.write_bytes(b"not a NumPy extension")
    digest = hashlib.sha256(fake.read_bytes()).hexdigest()
    with pytest.raises(FixtureValidationError, match="package_artifact_digest_mismatch"):
        verify_package_fixture(artifact_path=fake, expected_sha256=digest)


def test_tensor_fixture_has_complete_phase_1622_body():
    descriptor, payload = build_tensor_fixture()
    assert set(descriptor) == TENSOR_DESCRIPTOR_KEYS
    assert descriptor["dtype"] == "int32"
    assert descriptor["shape"] == [2, 2]
    assert descriptor["strides_bytes"] == [8, 4]
    assert descriptor["payload_integrity"]["algorithm"] == "sha256"
    assert descriptor["payload_integrity"]["hashed_byte_length"] == len(payload)
    assert len(descriptor["payload_integrity"]["digest"]) == 64


def test_tampered_tensor_payload_is_rejected():
    descriptor, payload = build_tensor_fixture()
    tampered = payload[:-1] + bytes([payload[-1] ^ 1])
    calls = 0
    with pytest.raises(FixtureValidationError, match="tensor_payload_digest_mismatch"):
        validate_tensor_fixture(descriptor, tampered)
        calls += 1
    assert calls == 0


@pytest.mark.parametrize(
    ("mutate", "error"),
    [
        (lambda d: d.update({"dtype": "float32"}), "tensor_dtype_invalid"),
        (lambda d: d.update({"shape": [4]}), "tensor_strides_invalid"),
        (lambda d: d.update({"byte_order": "big"}), "tensor_byte_order_invalid"),
        (lambda d: d.update({"layout": "strided"}), "tensor_layout_invalid"),
        (lambda d: d.update({"major_order": "column_major"}), "tensor_major_order_invalid"),
        (lambda d: d.update({"strides_bytes": [4, 8]}), "tensor_strides_invalid"),
        (lambda d: d.update({"byte_length": 20}), "tensor_byte_length_invalid"),
        (lambda d: d.update({"view": {"offset": 0}}), "tensor_view_invalid"),
        (lambda d: d.update({"invented": True}), "tensor_descriptor_fields_invalid"),
        (
            lambda d: d["payload_integrity"].update({"algorithm": "sha384"}),
            "tensor_payload_integrity_profile_invalid",
        ),
        (
            lambda d: d["payload_integrity"].update({"hashed_byte_length": 1}),
            "tensor_hashed_byte_length_invalid",
        ),
        (
            lambda d: d["payload_integrity"].update({"digest": "0" * 64}),
            "tensor_payload_digest_mismatch",
        ),
    ],
)
def test_tensor_descriptor_mismatches_fail_closed(mutate, error):
    descriptor, payload = build_tensor_fixture()
    mutate(descriptor)
    with pytest.raises(FixtureValidationError, match=error):
        validate_tensor_fixture(descriptor, payload)


def test_tensor_payload_length_mismatch_fails_closed():
    descriptor, payload = build_tensor_fixture()
    with pytest.raises(FixtureValidationError, match="tensor_payload_length_mismatch"):
        validate_tensor_fixture(descriptor, payload[:-1])


def test_zero_sized_tensor_is_valid_under_phase_1622_contract():
    descriptor, _ = build_tensor_fixture()
    payload = b""
    descriptor.update(
        {
            "shape": [0, 2],
            "element_count": 0,
            "strides_bytes": [8, 4],
            "byte_length": 0,
        }
    )
    descriptor["payload_integrity"].update(
        {"digest": hashlib.sha256(payload).hexdigest(), "hashed_byte_length": 0}
    )
    validate_tensor_fixture(descriptor, payload)


def test_scalar_tensor_uses_empty_shape_and_one_element():
    descriptor, _ = build_tensor_fixture()
    payload = struct.pack("<i", 7)
    descriptor.update(
        {
            "shape": [],
            "element_count": 1,
            "strides_bytes": [],
            "byte_length": 4,
        }
    )
    descriptor["payload_integrity"].update(
        {"digest": hashlib.sha256(payload).hexdigest(), "hashed_byte_length": 4}
    )
    validate_tensor_fixture(descriptor, payload)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("shape", [1] * 9, "tensor_shape_invalid"),
        ("shape", [1025], "tensor_dimension_invalid"),
        ("shape", [True], "tensor_dimension_invalid"),
        ("strides_bytes", [8.0, 4.0], "tensor_strides_invalid"),
    ],
)
def test_tensor_profile_bounds_and_exact_integer_types(field, value, error):
    descriptor, payload = build_tensor_fixture()
    descriptor[field] = value
    with pytest.raises(FixtureValidationError, match=error):
        validate_tensor_fixture(descriptor, payload)


@pytest.mark.parametrize(
    "semantic_labels",
    [
        {"label": "x" * 1_025},
        {"a": {"b": {"c": {"d": {"e": "too deep"}}}}},
        {str(index): index for index in range(33)},
    ],
)
def test_tensor_semantic_labels_are_recursively_bounded(semantic_labels):
    descriptor, payload = build_tensor_fixture()
    descriptor["semantic_labels"] = semantic_labels
    with pytest.raises(FixtureValidationError, match="tensor_semantic_labels_invalid"):
        validate_tensor_fixture(descriptor, payload)


def test_receipt_binds_descriptor_and_payload_through_input_commitment():
    results = run_demonstrations()
    tensor = results["demonstrations"][1]
    assert tensor["pinned_payload_identity"].startswith("sha256:")
    assert len(tensor["receipt_input_commitment"]) == 64
    assert len(tensor["receipt_schedule_digest"]) == 64
    assert tensor["pinned_payload_identity"] != tensor["receipt_input_commitment"]


def test_atomic_output_is_deterministic_and_parseable(tmp_path):
    first = write_results(tmp_path)
    first_bytes = (tmp_path / "demo_results.json").read_bytes()
    second = write_results(tmp_path)
    second_bytes = (tmp_path / "demo_results.json").read_bytes()
    assert first == second
    assert first_bytes == second_bytes
    assert json.loads(first_bytes)["demonstrations"] == first["demonstrations"]
    assert "graph_delta=none" in (tmp_path / "demo_summary.md").read_text()
