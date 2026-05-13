import hashlib
import json

import pytest

from ilc_core.sidecars.confidential_coordination_sealed_sender import (
    CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
    ConfidentialCoordinationSealedSenderError,
    build_local_delivery_projection,
    build_sealed_delivery_projection,
    build_sealed_local_delivery_intent,
    build_sealed_local_delivery_receipt,
    build_sealed_payload_class_ref,
    canonical_ccss_003_json,
    ccss_003_required_tokens,
    ccss_003_sealed_sender_local_delivery_manifest,
    export_ccss_003_record_json,
    validate_ccss_003_manifest,
    validate_ccss_003_record,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


def _ref(prefix: str, material: str) -> str:
    return f"{prefix}:{hashlib.sha256(material.encode()).hexdigest()}"


def _sample_bundle() -> tuple[dict, dict, dict, dict]:
    payload_class = build_sealed_payload_class_ref(sealed_payload_size_class_bytes=2108)
    intent = build_sealed_local_delivery_intent(
        private_shard_ref=_ref("private_shard", "phase-1326-shard"),
        capability_ref=_ref("capability", "phase-1326-capability"),
        sealed_payload_class_ref=payload_class["sealed_payload_class_ref"],
        sealed_payload_digest_ref=_ref("sealed_payload_digest", "sealed-payload-bytes"),
        relay_instruction_ref=_ref("relay_instruction", "h015-route-seam"),
        opaque_channel_ref=_ref("opaque_channel", "opaque-channel"),
        local_delivery_token_ref=_ref("local_delivery_token", "local-token"),
        delivery_epoch=1326,
        delivery_sequence=1,
        sealed_payload_size_bytes=2108,
    )
    receipt = build_sealed_local_delivery_receipt(
        private_shard_ref=intent["private_shard_ref"],
        delivery_intent_ref=intent["sealed_delivery_intent_ref"],
        sealed_payload_class_ref=payload_class["sealed_payload_class_ref"],
        local_delivery_token_ref=intent["local_delivery_token_ref"],
        local_recipient_adapter_ref=_ref("local_recipient_adapter", "local-adapter"),
        delivery_epoch=1326,
        delivery_sequence=2,
    )
    projection = build_sealed_delivery_projection(
        private_shard_ref=intent["private_shard_ref"],
        delivery_intent_ref=intent["sealed_delivery_intent_ref"],
        sealed_payload_class_ref=payload_class["sealed_payload_class_ref"],
        delivery_state="sealed_delivered_local",
        projection_epoch=1326,
    )
    return payload_class, intent, receipt, projection


def test_manifest_declares_required_tokens_and_non_authority_flags() -> None:
    manifest = ccss_003_sealed_sender_local_delivery_manifest()

    assert manifest["contract_version"] == CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION
    assert manifest["tokens"] == ccss_003_required_tokens()
    assert manifest["sealed_sender_fixed_size_payload_boundary_recorded"] is True
    assert manifest["h013_h015_dependency_seams_recorded"] is True
    assert manifest["sealed_payload_size_classes"] == [2108, 4156]
    assert manifest["plaintext_size_classes"] == [2048, 4096]
    assert manifest["public_p2p_enabled"] is False
    assert manifest["public_relay_serving_enabled"] is False
    assert manifest["public_confidential_messaging_claimed"] is False
    validate_ccss_003_manifest(manifest)


def test_records_are_hash_bound_and_export_deterministically() -> None:
    payload_class, intent, receipt, projection = _sample_bundle()

    for record in (payload_class, intent, receipt, projection):
        validated = validate_ccss_003_record(record)
        assert validated == record
        exported = export_ccss_003_record_json(record)
        assert exported == json.dumps(validated, allow_nan=False, separators=(",", ":"), sort_keys=True)


def test_fixed_size_payload_boundary_rejects_variable_size_payload() -> None:
    with pytest.raises(ConfidentialCoordinationSealedSenderError) as exc:
        build_sealed_payload_class_ref(sealed_payload_size_class_bytes=4095)

    assert exc.value.token == "ccss_003_size_class_invalid_phase_1326"


def test_missing_sealed_marker_is_rejected() -> None:
    payload_class, *_ = _sample_bundle()
    mutated = dict(payload_class)
    mutated["sealed_marker"] = "not_sealed"

    with pytest.raises(ConfidentialCoordinationSealedSenderError) as exc:
        validate_ccss_003_record(mutated)

    assert exc.value.token == "ccss_003_sealed_marker_invalid_phase_1326"


def test_projection_rejects_route_metadata_and_plaintext_leakage() -> None:
    *_, projection = _sample_bundle()
    route_leak = dict(projection)
    route_leak["projection_scope"] = "route_history_visible"
    with pytest.raises(ConfidentialCoordinationSealedSenderError) as route_exc:
        validate_ccss_003_record(route_leak)
    assert route_exc.value.token == "ccss_003_private_value_forbidden_phase_1326"

    plaintext_leak = dict(projection)
    plaintext_leak["plaintext_payload"] = "hidden text"
    with pytest.raises(ConfidentialCoordinationSealedSenderError):
        validate_ccss_003_record(plaintext_leak)


def test_local_delivery_projection_states_are_fail_closed() -> None:
    payload_class, intent, *_ = _sample_bundle()

    pending = build_local_delivery_projection(intent_record=intent, projection_epoch=1326)
    assert pending["delivery_state"] == "sealed_pending_local"

    delivered = build_local_delivery_projection(
        intent_record=intent,
        projection_epoch=1326,
        mark_delivered=True,
    )
    assert delivered["delivery_state"] == "sealed_delivered_local"

    replay = build_local_delivery_projection(
        intent_record=intent,
        projection_epoch=1326,
        replayed_delivery_token_refs=(intent["local_delivery_token_ref"],),
    )
    assert replay["delivery_state"] == "rejected_replay"

    public_transport = build_local_delivery_projection(
        intent_record=intent,
        projection_epoch=1326,
        public_p2p_enabled=True,
    )
    assert public_transport["delivery_state"] == "blocked_public_transport"

    bad_size = dict(intent)
    bad_size["sealed_payload_size_bytes"] = 9999
    size_rejection = build_local_delivery_projection(intent_record=bad_size, projection_epoch=1326)
    assert size_rejection["delivery_state"] == "rejected_size_class"
    assert size_rejection["sealed_payload_class_ref"] != payload_class["sealed_payload_class_ref"]


def test_public_relay_config_and_unbounded_queue_are_forbidden() -> None:
    payload_class, intent, *_ = _sample_bundle()

    flags = dict(intent["authorization_flags"])
    flags["public_relay_serving_enabled"] = True
    mutated = dict(intent)
    mutated["authorization_flags"] = flags
    with pytest.raises(ConfidentialCoordinationSealedSenderError) as flag_exc:
        validate_ccss_003_record(mutated)
    assert flag_exc.value.token == "public_p2p_not_activated_by_ccss_phase_1326"

    with pytest.raises(ConfidentialCoordinationSealedSenderError) as queue_exc:
        build_sealed_local_delivery_intent(
            private_shard_ref=intent["private_shard_ref"],
            capability_ref=intent["capability_ref"],
            sealed_payload_class_ref=payload_class["sealed_payload_class_ref"],
            sealed_payload_digest_ref=intent["sealed_payload_digest_ref"],
            relay_instruction_ref=intent["relay_instruction_ref"],
            opaque_channel_ref=intent["opaque_channel_ref"],
            local_delivery_token_ref=_ref("local_delivery_token", "new-token"),
            delivery_epoch=1326,
            delivery_sequence=3,
            sealed_payload_size_bytes=2108,
            delivery_queue_bound=0,
        )
    assert queue_exc.value.token == "ccss_003_delivery_queue_bound_invalid_phase_1326"


def test_protocol_time_and_sequence_are_positive() -> None:
    payload_class, intent, *_ = _sample_bundle()

    with pytest.raises(ConfidentialCoordinationSealedSenderError) as epoch_exc:
        build_sealed_local_delivery_intent(
            private_shard_ref=intent["private_shard_ref"],
            capability_ref=intent["capability_ref"],
            sealed_payload_class_ref=payload_class["sealed_payload_class_ref"],
            sealed_payload_digest_ref=intent["sealed_payload_digest_ref"],
            relay_instruction_ref=intent["relay_instruction_ref"],
            opaque_channel_ref=intent["opaque_channel_ref"],
            local_delivery_token_ref=_ref("local_delivery_token", "epoch-zero"),
            delivery_epoch=0,
            delivery_sequence=1,
            sealed_payload_size_bytes=2108,
        )
    assert exc_token(epoch_exc) == "ccss_003_delivery_epoch_invalid_phase_1326"

    with pytest.raises(ConfidentialCoordinationSealedSenderError) as sequence_exc:
        build_sealed_local_delivery_receipt(
            private_shard_ref=intent["private_shard_ref"],
            delivery_intent_ref=intent["sealed_delivery_intent_ref"],
            sealed_payload_class_ref=payload_class["sealed_payload_class_ref"],
            local_delivery_token_ref=intent["local_delivery_token_ref"],
            local_recipient_adapter_ref=_ref("local_recipient_adapter", "adapter"),
            delivery_epoch=1326,
            delivery_sequence=0,
        )
    assert exc_token(sequence_exc) == "ccss_003_delivery_sequence_invalid_phase_1326"


def test_canonical_json_rejects_unsafe_payloads_before_serialization(monkeypatch: pytest.MonkeyPatch) -> None:
    cyclic: dict[str, object] = {}
    cyclic["self"] = cyclic
    with pytest.raises(ConfidentialCoordinationSealedSenderError) as cycle_exc:
        canonical_ccss_003_json(cyclic)
    assert cycle_exc.value.token == "ccss_003_payload_cycle_forbidden_phase_1326"

    for payload in ({"float": 1.5}, {"tuple": ("x",)}, {"text": "ok\tno"}):
        with pytest.raises(ConfidentialCoordinationSealedSenderError):
            canonical_ccss_003_json(payload)

    oversized = {f"k{i}": "x" * 4096 for i in range(2500)}

    def _fail_dumps(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("json.dumps should not be reached for oversized payload")

    monkeypatch.setattr(json, "dumps", _fail_dumps)
    with pytest.raises(ConfidentialCoordinationSealedSenderError) as size_exc:
        canonical_ccss_003_json(oversized)
    assert size_exc.value.token == "ccss_003_payload_size_exceeded_phase_1326"


def test_registry_manifest_includes_ccss_003_without_public_authority() -> None:
    manifest = build_sidecar_registry_manifest()
    sidecars = {item["sidecar_id"]: item for item in manifest["sidecars"]}
    assert "confidential_coordination_sealed_sender_local_delivery" in sidecars
    assert sidecars["confidential_coordination_sealed_sender_local_delivery"]["public_serving_enabled"] is False

    confidential_profile = next(
        profile
        for profile in manifest["profiles"]
        if profile["profile_id"] == "confidential_coordination_local_preview"
    )
    assert "confidential_coordination_sealed_sender_local_delivery" in confidential_profile["required_sidecars"]
    ccss = manifest["package_profile_integrity"]["confidential_coordination_sealed_sender_manifest"]
    assert ccss["contract_version"] == CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION
    assert ccss["public_p2p_enabled"] is False


def test_required_tokens_exist_in_prompt_and_docs() -> None:
    corpus = "\n".join(
        [
            open(
                "docs/antigravity_tasks/antigravity_prompt__phase_1326_g8_ccss_003_sealed_sender_local_delivery_boundary.md",
                encoding="utf-8",
            ).read(),
            "\n".join(ccss_003_required_tokens()),
        ]
    )
    for token in ccss_003_required_tokens():
        assert token in corpus


def exc_token(exc_info: pytest.ExceptionInfo[ConfidentialCoordinationSealedSenderError]) -> str:
    return exc_info.value.token
