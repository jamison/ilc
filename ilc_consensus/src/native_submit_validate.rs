// SPDX-License-Identifier: AGPL-3.0-only

use blst::min_pk::{PublicKey, Signature};
use serde_json::Value;
use sha2::{Digest, Sha256};

const PROTOCOL_VERSION: i64 = 1;
const DST_PREFIX: &str = "ILC_NATIVE_TRUTH_SUBMIT_V1:";
const SIG_SCHEMA_VERSION: &str = "native_submit_sig.v0.1";
const SIG_VERIFIER_PROFILE: &str = "native_submit_sig_profile.v0.1";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidatedEnvelope {
    pub version: i64,
    pub agent_id: String,
    pub epoch: i64,
    pub primitive: String,
    pub payload: Value,
    pub uncertainty_declared: Option<String>,
    pub sig: Value,
    pub payload_sha256: String,
    pub canonical_preimage_bytes: Vec<u8>,
}

pub fn validate_native_submit_envelope(json_bytes: &[u8]) -> Result<ValidatedEnvelope, String> {
    let envelope: Value =
        serde_json::from_slice(json_bytes).map_err(|_| "native_submit_invalid_json".to_string())?;
    let object = envelope
        .as_object()
        .ok_or_else(|| "submission_must_be_dict".to_string())?;

    let version = object
        .get("v")
        .and_then(Value::as_i64)
        .ok_or_else(|| "protocol_version_invalid".to_string())?;
    if version != PROTOCOL_VERSION {
        return Err("protocol_version_invalid".to_string());
    }

    let primitive = object
        .get("primitive")
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| "primitive_missing".to_string())?;
    if primitive == "commit.epoch" {
        return Err("commit_epoch_agent_submission_rejected".to_string());
    }
    if !is_agent_issuable_primitive(primitive) {
        return Err("primitive_unknown".to_string());
    }

    let agent_value = object.get("agent_id");
    if agent_value.is_none() || agent_value == Some(&Value::String(String::new())) {
        return Err("agent_id_missing".to_string());
    }
    let agent_id = agent_value
        .and_then(Value::as_str)
        .ok_or_else(|| "agent_id_invalid".to_string())?;
    if !is_lower_hex_exact(agent_id, 48) {
        return Err("agent_id_invalid".to_string());
    }

    let epoch = object
        .get("epoch")
        .and_then(Value::as_i64)
        .filter(|value| *value >= 0)
        .ok_or_else(|| "epoch_invalid".to_string())?;

    let payload = object
        .get("payload")
        .filter(|value| value.is_object())
        .ok_or_else(|| "payload_missing".to_string())?;
    if contains_non_integer_number(payload) {
        return Err("payload_non_integer_number_rejected".to_string());
    }

    let uncertainty_declared = match object.get("uncertainty_declared") {
        Some(Value::String(value)) => {
            if value.as_bytes().len() > 512 {
                return Err("uncertainty_declared_too_long".to_string());
            }
            Some(value.clone())
        }
        Some(Value::Null) | None => None,
        Some(_) => return Err("uncertainty_declared_invalid".to_string()),
    };

    let sig = object.get("sig");
    if sig.is_none()
        || sig == Some(&Value::Null)
        || sig == Some(&Value::String("UNSIGNED".to_string()))
    {
        return Err("native_submit_sig_unsigned_placeholder_rejected".to_string());
    }
    let sig_object = sig
        .and_then(Value::as_object)
        .ok_or_else(|| "native_submit_sig_not_object_IMPL_00".to_string())?;

    if sig_object.get("schema_version").and_then(Value::as_str) != Some(SIG_SCHEMA_VERSION) {
        return Err("native_submit_sig_schema_version_invalid_IMPL_00".to_string());
    }
    if sig_object.get("verifier_profile").and_then(Value::as_str) != Some(SIG_VERIFIER_PROFILE) {
        return Err("native_submit_sig_verifier_profile_invalid_IMPL_00".to_string());
    }

    let dst = sig_object
        .get("dst")
        .and_then(Value::as_str)
        .filter(|value| value.starts_with(DST_PREFIX))
        .ok_or_else(|| "native_submit_sig_dst_invalid_IMPL_00".to_string())?;
    let network_id = &dst[DST_PREFIX.len()..];

    let payload_sha256 = sig_object
        .get("payload_sha256")
        .and_then(Value::as_str)
        .ok_or_else(|| "native_submit_sig_payload_sha256_format_invalid_IMPL_00".to_string())?;
    if !is_lower_hex_exact(payload_sha256, 32) {
        return Err("native_submit_sig_payload_sha256_format_invalid_IMPL_00".to_string());
    }

    let signature_hex = sig_object
        .get("signature_hex")
        .and_then(Value::as_str)
        .ok_or_else(|| "native_submit_sig_signature_hex_invalid_IMPL_00".to_string())?;
    if signature_hex.is_empty()
        || signature_hex.len() % 2 != 0
        || !signature_hex
            .bytes()
            .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
    {
        return Err("native_submit_sig_signature_hex_invalid_IMPL_00".to_string());
    }
    if signature_hex.len() != 192 {
        return Err("native_submit_sig_signature_hex_length_invalid_CDL_118".to_string());
    }

    let key_ref = sig_object
        .get("key_ref")
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| "native_submit_sig_key_ref_missing_IMPL_00".to_string())?;

    let canonical_preimage_bytes = canonical_preimage_bytes_from_value(&envelope)?;
    let expected_sha256 = sha256_hex(&canonical_preimage_bytes);
    if payload_sha256 != expected_sha256 {
        return Err("native_submit_sig_payload_sha256_mismatch_IMPL_00".to_string());
    }

    if key_ref != agent_id {
        return Err("native_submit_sig_key_ref_agent_id_mismatch_CDL_118".to_string());
    }

    if !verify_native_submit_bytes(
        agent_id,
        &canonical_preimage_bytes,
        signature_hex,
        network_id,
    ) {
        return Err("native_submit_sig_bls_verification_failed_CDL_118".to_string());
    }

    Ok(ValidatedEnvelope {
        version,
        agent_id: agent_id.to_string(),
        epoch,
        primitive: primitive.to_string(),
        payload: payload.clone(),
        uncertainty_declared,
        sig: sig
            .expect("sig is present after unsigned-placeholder rejection")
            .clone(),
        payload_sha256: payload_sha256.to_string(),
        canonical_preimage_bytes,
    })
}

pub fn canonical_preimage_bytes(json_bytes: &[u8]) -> Result<Vec<u8>, String> {
    let envelope: Value =
        serde_json::from_slice(json_bytes).map_err(|_| "native_submit_invalid_json".to_string())?;
    canonical_preimage_bytes_from_value(&envelope)
}

pub fn canonical_preimage_bytes_from_value(envelope: &Value) -> Result<Vec<u8>, String> {
    let object = envelope
        .as_object()
        .ok_or_else(|| "submission_must_be_dict".to_string())?;
    let mut entries = Vec::with_capacity(object.len().saturating_sub(1));
    for (key, value) in object {
        if key != "sig" {
            entries.push((key.as_str(), value));
        }
    }
    entries.sort_by(|left, right| left.0.cmp(right.0));

    let mut out = String::from("{");
    for (index, (key, value)) in entries.iter().enumerate() {
        if index > 0 {
            out.push(',');
        }
        out.push_str(
            &serde_json::to_string(key)
                .map_err(|_| "native_submit_canonical_json_failed".to_string())?,
        );
        out.push(':');
        out.push_str(&canonical_json(value)?);
    }
    out.push('}');
    Ok(out.into_bytes())
}

pub fn payload_sha256_hex(json_bytes: &[u8]) -> Result<String, String> {
    Ok(sha256_hex(&canonical_preimage_bytes(json_bytes)?))
}

pub fn verify_native_submit_bytes(
    public_key_hex: &str,
    message_bytes: &[u8],
    signature_hex: &str,
    network_id: &str,
) -> bool {
    if message_bytes.is_empty() {
        return false;
    }
    let clean_network_id = match normalize_network_id(network_id) {
        Some(value) => value,
        None => return false,
    };
    let public_key_bytes = match hex_decode_exact(public_key_hex, 48) {
        Ok(value) => value,
        Err(_) => return false,
    };
    let signature_bytes = match hex_decode_exact(signature_hex, 96) {
        Ok(value) => value,
        Err(_) => return false,
    };
    let public_key = match PublicKey::from_bytes(&public_key_bytes) {
        Ok(value) => value,
        Err(_) => return false,
    };
    if public_key.validate().is_err() {
        return false;
    }
    let signature = match Signature::from_bytes(&signature_bytes) {
        Ok(value) => value,
        Err(_) => return false,
    };
    if signature.validate(true).is_err() {
        return false;
    }
    let dst = format!("{DST_PREFIX}{clean_network_id}");
    signature.verify(true, message_bytes, dst.as_bytes(), &[], &public_key, true)
        == blst::BLST_ERROR::BLST_SUCCESS
}

fn canonical_json(value: &Value) -> Result<String, String> {
    match value {
        Value::Null | Value::Bool(_) | Value::Number(_) | Value::String(_) => {
            serde_json::to_string(value)
                .map_err(|_| "native_submit_canonical_json_failed".to_string())
        }
        Value::Array(items) => {
            let mut out = String::from("[");
            for (index, item) in items.iter().enumerate() {
                if index > 0 {
                    out.push(',');
                }
                out.push_str(&canonical_json(item)?);
            }
            out.push(']');
            Ok(out)
        }
        Value::Object(object) => {
            let mut entries: Vec<_> = object.iter().collect();
            entries.sort_by(|left, right| left.0.cmp(right.0));
            let mut out = String::from("{");
            for (index, (key, child)) in entries.iter().enumerate() {
                if index > 0 {
                    out.push(',');
                }
                out.push_str(
                    &serde_json::to_string(key)
                        .map_err(|_| "native_submit_canonical_json_failed".to_string())?,
                );
                out.push(':');
                out.push_str(&canonical_json(child)?);
            }
            out.push('}');
            Ok(out)
        }
    }
}

fn is_agent_issuable_primitive(value: &str) -> bool {
    matches!(
        value,
        "assert.truth"
            | "validate.claim"
            | "contradict.assert"
            | "link.claim"
            | "refute.claim"
            | "revise.assert"
    )
}

fn is_lower_hex_exact(value: &str, expected_bytes: usize) -> bool {
    value.len() == expected_bytes * 2
        && value
            .bytes()
            .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
}

fn contains_non_integer_number(value: &Value) -> bool {
    match value {
        Value::Number(number) => !(number.is_i64() || number.is_u64()),
        Value::Array(items) => items.iter().any(contains_non_integer_number),
        Value::Object(object) => object.values().any(contains_non_integer_number),
        _ => false,
    }
}

fn hex_decode_exact(value: &str, expected_bytes: usize) -> Result<Vec<u8>, String> {
    if !is_lower_hex_exact(value, expected_bytes) {
        return Err("hex_invalid".to_string());
    }
    let mut out = Vec::with_capacity(expected_bytes);
    let bytes = value.as_bytes();
    for index in (0..bytes.len()).step_by(2) {
        let hi = hex_nibble(bytes[index])?;
        let lo = hex_nibble(bytes[index + 1])?;
        out.push((hi << 4) | lo);
    }
    Ok(out)
}

fn hex_nibble(byte: u8) -> Result<u8, String> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        _ => Err("hex_invalid".to_string()),
    }
}

fn normalize_network_id(value: &str) -> Option<&str> {
    let clean = value.trim_matches(' ');
    if clean.is_empty()
        || clean.contains(':')
        || !clean.is_ascii()
        || clean.bytes().any(|byte| !(0x21..=0x7e).contains(&byte))
    {
        None
    } else {
        Some(clean)
    }
}

fn sha256_hex(bytes: &[u8]) -> String {
    let digest = Sha256::digest(bytes);
    let mut out = String::with_capacity(64);
    for byte in digest {
        out.push_str(&format!("{byte:02x}"));
    }
    out
}
