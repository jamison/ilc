from __future__ import annotations

import pytest

from tools.testbed.phase1591_fix6_public_epoch_roll import (
    _extract_json_object,
    build_checkpoint_command,
    deterministic_state_root,
    parse_validator_spec,
    parse_validator_specs,
    redacted_endpoint_label,
)


def test_parse_validator_spec_accepts_public_endpoint_shape() -> None:
    endpoint = parse_validator_spec(
        "id=1,ssh=ilc-node-2,grpc=203.0.113.10:51265,quic=203.0.113.10:51255,db=db_1"
    )
    assert endpoint.validator_id == 1
    assert endpoint.ssh_host == "ilc-node-2"
    assert endpoint.grpc_target == "203.0.113.10:51265"
    assert endpoint.quic_target == "203.0.113.10:51255"
    assert endpoint.lmdb_path == "db_1"


def test_parse_validator_specs_rejects_duplicate_ids() -> None:
    spec = "id=1,ssh=ilc-node-2,grpc=203.0.113.10:51265,quic=203.0.113.10:51255,db=db_1"
    with pytest.raises(ValueError, match="phase1591_fix6_public_validator_set_invalid"):
        parse_validator_specs([spec, spec, spec, spec])


def test_parse_validator_spec_rejects_unsafe_lmdb_path() -> None:
    with pytest.raises(ValueError, match="phase1591_fix6_public_lmdb_path_invalid"):
        parse_validator_spec(
            "id=1,ssh=ilc-node-2,grpc=203.0.113.10:51265,quic=203.0.113.10:51255,db=../db_1"
        )


def test_deterministic_state_root_is_cidv1_hex_shaped_and_previous_root_bound() -> None:
    previous = "01711220" + "a" * 64
    root_a = deterministic_state_root(epoch=6, previous_state_root=previous, salt="same")
    root_b = deterministic_state_root(epoch=6, previous_state_root=previous, salt="same")
    root_c = deterministic_state_root(epoch=6, previous_state_root="01711220" + "b" * 64, salt="same")
    assert root_a == root_b
    assert root_a != root_c
    assert len(root_a) == 72
    assert root_a.startswith("01711220")
    assert root_a.islower()


def test_redacted_endpoint_label_omits_raw_hosts() -> None:
    endpoint = parse_validator_spec(
        "id=3,ssh=ilc-node-3,grpc=203.0.113.30:51263,quic=203.0.113.30:51253,db=db_3"
    )
    label = redacted_endpoint_label(endpoint)
    assert label["host_redacted"] is True
    assert label["grpc_port"] == 51263
    assert label["quic_port"] == 51253
    assert "203.0.113.30" not in repr(label)


def test_build_checkpoint_command_uses_distinct_injector_for_validator_one() -> None:
    endpoint = parse_validator_spec(
        "id=1,ssh=ilc-node-2,grpc=203.0.113.10:51265,quic=203.0.113.10:51255,db=db_1"
    )
    command = build_checkpoint_command(
        endpoint,
        epoch=6,
        state_root="01711220" + "c" * 64,
    )
    assert "--validator 203.0.113.10:51255" in command
    assert "--cert certs/validator_2_cert.pem" in command
    assert "--key certs/validator_2_key.pem" in command
    assert "--peer-cert certs/validator_1_cert.der" in command
    assert "--peer-id 2" in command


def test_build_checkpoint_command_uses_validator_one_injector_for_other_validators() -> None:
    endpoint = parse_validator_spec(
        "id=4,ssh=ilc-node-6,grpc=203.0.113.40:51264,quic=203.0.113.40:51254,db=db_4"
    )
    command = build_checkpoint_command(
        endpoint,
        epoch=6,
        state_root="01711220" + "d" * 64,
    )
    assert "--cert certs/validator_1_cert.pem" in command
    assert "--key certs/validator_1_key.pem" in command
    assert "--peer-cert certs/validator_4_cert.der" in command
    assert "--peer-id 1" in command


def test_extract_json_object_skips_state_extractor_logs() -> None:
    payload = _extract_json_object(
        "[m016] status line\n"
        '{"sentinel_current_epoch":6,"verdict":"workload_d_replayability_pass"}\n'
        "[m016] workload_d_replayability_pass\n"
    )
    assert payload == {
        "sentinel_current_epoch": 6,
        "verdict": "workload_d_replayability_pass",
    }
