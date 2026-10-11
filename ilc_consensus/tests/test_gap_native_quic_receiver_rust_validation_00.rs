// SPDX-License-Identifier: AGPL-3.0-only

use ilc_consensus::native_submit_validate::{
    canonical_preimage_bytes_from_value, payload_sha256_hex, validate_native_submit_envelope,
    verify_native_submit_bytes,
};
use serde_json::Value;
use std::fs;
use std::path::Path;

fn parity_vectors() -> Value {
    let path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../out/gap_native_quic_receiver_parity_vectors_00/parity_vectors.json");
    serde_json::from_str(&fs::read_to_string(path).expect("parity vectors readable"))
        .expect("parity vectors JSON valid")
}

fn json_bytes(value: &Value) -> Vec<u8> {
    serde_json::to_vec(value).expect("fixture serializable")
}

#[test]
fn canonical_preimage_matches_python_sort_keys_vectors() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_1"].as_array().expect("set 1 array");
    assert_eq!(entries.len(), 5);
    for entry in entries {
        let observed =
            canonical_preimage_bytes_from_value(&entry["input"]).expect("canonical bytes produced");
        assert_eq!(
            hex_encode(&observed),
            entry["expected_output"].as_str().unwrap()
        );
    }
}

#[test]
fn payload_sha256_matches_python_vectors() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_2"].as_array().expect("set 2 array");
    assert_eq!(entries.len(), 5);
    for entry in entries {
        let observed =
            payload_sha256_hex(&json_bytes(&entry["input"])).expect("payload hash produced");
        assert_eq!(observed, entry["expected_output"].as_str().unwrap());
    }
}

#[test]
fn bls_verify_matches_python_vectors() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_3"].as_array().expect("set 3 array");
    assert_eq!(entries.len(), 10);
    for entry in entries {
        let input = &entry["input"];
        let message = hex_decode(input["message_bytes_hex"].as_str().unwrap());
        let observed = verify_native_submit_bytes(
            input["public_key_hex"].as_str().unwrap(),
            &message,
            input["signature_hex"].as_str().unwrap(),
            input["network_id"].as_str().unwrap(),
        );
        assert_eq!(
            observed,
            entry["expected_output"]["expected_verify_result"]
                .as_bool()
                .unwrap()
        );
    }
}

#[test]
fn full_signed_parity_envelopes_validate() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_1"].as_array().expect("set 1 array");
    for entry in entries {
        let validated = validate_native_submit_envelope(&json_bytes(&entry["input"]))
            .expect("signed envelope validates");
        assert_eq!(
            validated.agent_id,
            entry["input"]["agent_id"].as_str().unwrap()
        );
        assert_eq!(
            validated.primitive,
            entry["input"]["primitive"].as_str().unwrap()
        );
        assert_eq!(
            hex_encode(&validated.canonical_preimage_bytes),
            entry["expected_output"].as_str().unwrap()
        );
    }
}

#[test]
fn adversarial_direct_validation_returns_bls_failure_token() {
    let vectors = parity_vectors();
    let mut envelope = vectors["vector_set_1"][0]["input"].clone();
    envelope["sig"]["signature_hex"] = Value::String("00".repeat(96));
    let token = validate_native_submit_envelope(&json_bytes(&envelope)).unwrap_err();
    assert_eq!(token, "native_submit_sig_bls_verification_failed_CDL_118");
}

#[test]
fn key_ref_agent_id_mismatch_returns_cdl_118_token() {
    let vectors = parity_vectors();
    let mut envelope = vectors["vector_set_1"][0]["input"].clone();
    let different_agent_id = vectors["vector_set_1"][1]["input"]["agent_id"]
        .as_str()
        .expect("second vector has agent_id")
        .to_string();
    assert_ne!(
        different_agent_id,
        envelope["agent_id"]
            .as_str()
            .expect("first vector has agent_id")
    );

    envelope["sig"]["key_ref"] = Value::String(different_agent_id);
    let token = validate_native_submit_envelope(&json_bytes(&envelope)).unwrap_err();
    assert_eq!(token, "native_submit_sig_key_ref_agent_id_mismatch_CDL_118");
}

#[test]
fn network_id_non_space_whitespace_rejected_like_python_backend() {
    let vectors = parity_vectors();
    let entry = &vectors["vector_set_3"]
        .as_array()
        .expect("set 3 array")
        .first()
        .expect("set 3 has at least one valid BLS vector");
    let input = &entry["input"];
    let message = hex_decode(input["message_bytes_hex"].as_str().unwrap());

    let observed = verify_native_submit_bytes(
        input["public_key_hex"].as_str().unwrap(),
        &message,
        input["signature_hex"].as_str().unwrap(),
        "\tilc-public-rc-01-testnet-harness\t",
    );

    assert!(
        !observed,
        "Python _require_non_empty_network_id rejects tab whitespace before strip(\" \")"
    );
}

#[test]
fn null_sig_matches_python_unsigned_placeholder_token() {
    let vectors = parity_vectors();
    let mut envelope = vectors["vector_set_1"][0]["input"].clone();
    envelope["sig"] = Value::Null;
    let token = validate_native_submit_envelope(&json_bytes(&envelope)).unwrap_err();
    assert_eq!(token, "native_submit_sig_unsigned_placeholder_rejected");
}

#[test]
fn non_integer_payload_number_is_rejected_before_signature_checks() {
    let vectors = parity_vectors();
    let mut envelope = vectors["vector_set_1"][0]["input"].clone();
    envelope["payload"]["content"]["non_integer"] = serde_json::json!(0.5);
    let token = validate_native_submit_envelope(&json_bytes(&envelope)).unwrap_err();
    assert_eq!(token, "payload_non_integer_number_rejected");
}

#[test]
fn validation_module_remains_storage_free() {
    let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("src/native_submit_validate.rs");
    let source = fs::read_to_string(path).expect("module source readable");
    for forbidden in [
        "lmdb",
        "Environment",
        "Database",
        "File::create",
        "write_all",
    ] {
        assert!(
            !source.contains(forbidden),
            "validation module must not contain storage primitive {forbidden}"
        );
    }
}

fn hex_encode(bytes: &[u8]) -> String {
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push_str(&format!("{byte:02x}"));
    }
    out
}

fn hex_decode(value: &str) -> Vec<u8> {
    assert_eq!(value.len() % 2, 0);
    let mut out = Vec::with_capacity(value.len() / 2);
    let bytes = value.as_bytes();
    for index in (0..bytes.len()).step_by(2) {
        out.push((hex_nibble(bytes[index]) << 4) | hex_nibble(bytes[index + 1]));
    }
    out
}

fn hex_nibble(byte: u8) -> u8 {
    match byte {
        b'0'..=b'9' => byte - b'0',
        b'a'..=b'f' => byte - b'a' + 10,
        _ => panic!("invalid hex"),
    }
}
