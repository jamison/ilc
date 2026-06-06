import pytest

from ilc_core.bundle.layer0_protocol_bundle import (
    ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION,
    generate_layer0_protocol_bundle,
    verify_layer0_protocol_bundle,
)


def test_layer0_protocol_bundle_generation_is_deterministic() -> None:
    bundle_a = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[
            {"type_name": "Node", "required": ["node_id", "type"]},
            {"type_name": "Edge", "required": ["source", "target"]},
        ],
        parameters={"truth_primitives": 7},
    )
    bundle_b = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[
            {"type_name": "Edge", "required": ["source", "target"]},
            {"type_name": "Node", "required": ["node_id", "type"]},
        ],
        parameters={"truth_primitives": 7},
    )

    assert ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION is False
    assert bundle_a.sha256 == bundle_b.sha256
    assert verify_layer0_protocol_bundle(bundle_a) is True
    assert bundle_a.public_rc_exclude is True


def test_layer0_protocol_bundle_rejects_float_inputs() -> None:
    with pytest.raises(ValueError, match="layer0_protocol_bundle_float_not_allowed"):
        generate_layer0_protocol_bundle(
            bundle_id="layer0-fixture",
            version="v0.1-private",
            schemas=[{"type_name": "Node", "weight": 3.14}],
            parameters={"truth_primitives": 7},
        )


def test_layer0_protocol_bundle_freezes_nested_containers() -> None:
    bundle = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id"]}],
        parameters={"truth_primitives": 7},
    )

    with pytest.raises(TypeError):
        bundle.schemas[0]["type_name"] = "Mutated"  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.parameters["truth_primitives"] = 8  # type: ignore[index]
