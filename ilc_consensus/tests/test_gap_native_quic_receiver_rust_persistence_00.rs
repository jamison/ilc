// SPDX-License-Identifier: AGPL-3.0-only

use ilc_consensus::native_submit_persist::{
    canonical_json_bytes, node_id_from_record, node_record_from_validated, replay_key,
    replay_payload, write_submission_to_lmdb,
};
use ilc_consensus::native_submit_validate::{validate_native_submit_envelope, ValidatedEnvelope};
use lmdb_rkv::{Cursor, Environment, Transaction};
use serde_json::json;
use serde_json::Value;
use sha2::Digest;
use std::fs;
use std::io::Write;
use std::net::TcpListener;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};
use std::thread;
use std::time::{Duration, Instant};

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
fn no_float_payload_numbers_in_phase_7_vectors() {
    let vectors = parity_vectors();
    for set_name in [
        "vector_set_4",
        "vector_set_5",
        "vector_set_6",
        "vector_set_7",
    ] {
        assert!(
            !contains_non_integer_number(&vectors[set_name]),
            "{set_name} must not introduce non-integer JSON numbers without explicit float parity"
        );
    }
}

#[test]
fn replay_vectors_match_python_keys_and_payloads() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_4"].as_array().expect("set 4 array");
    assert_eq!(entries.len(), 6);
    let mut seen = std::collections::BTreeSet::new();
    for entry in entries {
        let validated = validate_native_submit_envelope(&json_bytes(&entry["input"]))
            .expect("vector envelope validates");
        let observed_key = replay_key(
            &validated.agent_id,
            validated.epoch,
            &validated.payload_sha256,
        );
        assert_eq!(
            observed_key,
            entry["expected_output"]["replay_key"].as_str().unwrap()
        );
        assert_eq!(
            replay_payload(&validated),
            entry["expected_output"]["replay_payload"]
        );
        let observed_is_replay = !seen.insert(observed_key);
        assert_eq!(
            observed_is_replay,
            entry["expected_output"]["is_replay"].as_bool().unwrap()
        );
    }
}

#[test]
fn node_records_match_python_vectors() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_5"].as_array().expect("set 5 array");
    assert_eq!(entries.len(), 5);
    for entry in entries {
        let validated = validate_native_submit_envelope(&json_bytes(&entry["input"]))
            .expect("vector envelope validates");
        let observed = node_record_from_validated(&validated).expect("node record generated");
        assert_eq!(observed, entry["expected_output"]);
    }
}

#[test]
fn uncertainty_declared_round_trips_from_signed_parity_envelope() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_5"].as_array().expect("set 5 array");
    let entry = entries
        .iter()
        .find(|entry| entry["input"].get("uncertainty_declared").is_some())
        .expect("at least one parity vector carries uncertainty_declared");
    let validated = validate_native_submit_envelope(&json_bytes(&entry["input"]))
        .expect("signed envelope validates");
    assert_eq!(
        validated.uncertainty_declared.as_deref(),
        entry["input"]["uncertainty_declared"].as_str()
    );
    let observed = node_record_from_validated(&validated).expect("node record generated");
    assert_eq!(observed, entry["expected_output"]);
    assert_eq!(
        observed["uncertainty_declared"].as_str(),
        entry["input"]["uncertainty_declared"].as_str()
    );
}

#[test]
fn cidv1_values_match_python_vectors() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_6"].as_array().expect("set 6 array");
    assert_eq!(entries.len(), 5);
    for entry in entries {
        let observed = node_id_from_record(&entry["input"]).expect("CIDv1 generated");
        assert_eq!(observed, entry["expected_output"].as_str().unwrap());
    }
}

#[test]
fn lmdb_batch_shape_matches_python_raw_hex_vectors() {
    let vectors = parity_vectors();
    let entries = vectors["vector_set_7"].as_array().expect("set 7 array");
    assert_eq!(entries.len(), 5);
    for entry in entries {
        let temp = tempfile::tempdir().expect("tempdir");
        let validated = validate_native_submit_envelope(&json_bytes(&entry["input"]))
            .expect("vector envelope validates");
        let receipt = write_submission_to_lmdb(temp.path().to_str().unwrap(), &validated)
            .expect("write succeeds");
        assert_eq!(serde_json::to_value(&receipt).unwrap(), entry["receipt"]);
        assert_eq!(
            raw_db_hex(temp.path(), "nodes"),
            vec![RawRow {
                key_hex: entry["expected_output"]["node_key"]
                    .as_str()
                    .unwrap()
                    .to_string(),
                value_hex: entry["expected_output"]["node_value"]
                    .as_str()
                    .unwrap()
                    .to_string(),
            }]
        );
        assert_eq!(
            raw_db_hex(temp.path(), "edges"),
            rows_from_vectors(
                entry["expected_output"]["edge_keys"].as_array().unwrap(),
                entry["expected_output"]["edge_values"].as_array().unwrap(),
            )
        );
        assert_eq!(
            raw_db_hex(temp.path(), "native_submit_replay"),
            vec![RawRow {
                key_hex: entry["expected_output"]["replay_key"]
                    .as_str()
                    .unwrap()
                    .to_string(),
                value_hex: entry["expected_output"]["replay_value"]
                    .as_str()
                    .unwrap()
                    .to_string(),
            }]
        );

        let replay_error = write_submission_to_lmdb(temp.path().to_str().unwrap(), &validated)
            .expect_err("second write rejects replay");
        assert_eq!(replay_error, "native_submit_sig_replay_rejected_CDL_118");
    }
}

#[test]
fn canonical_json_bytes_matches_python_lmdb_value_encoding() {
    let vectors = parity_vectors();
    let entry = &vectors["vector_set_7"].as_array().unwrap()[0];
    let expected_value_hex = entry["expected_output"]["node_value"].as_str().unwrap();
    let record = &vectors["vector_set_6"].as_array().unwrap()[0]["input"];
    assert_eq!(
        hex_encode(&canonical_json_bytes(record).unwrap()),
        expected_value_hex
    );
}

#[test]
fn full_receiver_local_loopback_accepts_signed_envelope() {
    let vectors = parity_vectors();
    let envelope = &vectors["vector_set_1"].as_array().unwrap()[0]["input"];
    let expected_node_id = vectors["vector_set_6"].as_array().unwrap()[0]["expected_output"]
        .as_str()
        .unwrap();
    let temp = tempfile::tempdir().expect("tempdir");
    let cert_path = temp.path().join("cert.pem");
    let key_path = temp.path().join("key.pem");
    write_self_signed_cert(&cert_path, &key_path);
    let graph_path = temp.path().join("graph.lmdb");
    let port = free_local_port();
    let endpoint = format!("127.0.0.1:{port}");

    let mut child = Command::new(env!("CARGO_BIN_EXE_ilc_native_submit_receiver_full"))
        .env("ILC_SUBMIT_RECEIVER_BIND_ADDR", &endpoint)
        .env("ILC_SUBMIT_RECEIVER_TLS_CERT", &cert_path)
        .env("ILC_SUBMIT_RECEIVER_TLS_KEY", &key_path)
        .env("ILC_TRUTH_GRAPH_STORE_PATH", &graph_path)
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .spawn()
        .expect("receiver starts");
    wait_for_receiver_ready(&endpoint, &cert_path);

    let output = run_client(&endpoint, &cert_path, envelope);
    child.kill().ok();
    child.wait().ok();

    assert!(
        output.status.success(),
        "client failed stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    let receipt: Value = serde_json::from_slice(&output.stdout).expect("receipt JSON");
    assert_eq!(receipt["ok"], true);
    assert_eq!(receipt["node_id"], expected_node_id);
    assert_eq!(receipt["receiver_profile"], "native_quic_full_rust");
    assert_eq!(receipt["graph_persistence"], "persisted");
}

#[test]
fn full_receiver_local_loopback_rejects_replay_unsigned_and_bad_sig() {
    let vectors = parity_vectors();
    let envelope = &vectors["vector_set_1"].as_array().unwrap()[0]["input"];
    let temp = tempfile::tempdir().expect("tempdir");
    let cert_path = temp.path().join("cert.pem");
    let key_path = temp.path().join("key.pem");
    write_self_signed_cert(&cert_path, &key_path);
    let graph_path = temp.path().join("graph.lmdb");
    let port = free_local_port();
    let endpoint = format!("127.0.0.1:{port}");

    let mut child = Command::new(env!("CARGO_BIN_EXE_ilc_native_submit_receiver_full"))
        .env("ILC_SUBMIT_RECEIVER_BIND_ADDR", &endpoint)
        .env("ILC_SUBMIT_RECEIVER_TLS_CERT", &cert_path)
        .env("ILC_SUBMIT_RECEIVER_TLS_KEY", &key_path)
        .env("ILC_TRUTH_GRAPH_STORE_PATH", &graph_path)
        .env("ILC_SUBMIT_RECEIVER_MAX_CONNECTIONS", "8")
        .env("ILC_SUBMIT_RECEIVER_MAX_IN_FLIGHT", "4")
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .spawn()
        .expect("receiver starts");
    wait_for_receiver_ready(&endpoint, &cert_path);

    let first = run_client(&endpoint, &cert_path, envelope);
    assert!(
        first.status.success(),
        "first signed submit failed stdout={} stderr={}",
        String::from_utf8_lossy(&first.stdout),
        String::from_utf8_lossy(&first.stderr)
    );

    let replay = run_client(&endpoint, &cert_path, envelope);
    assert_error_token(&replay, "native_submit_sig_replay_rejected_CDL_118");

    let mut unsigned = envelope.clone();
    unsigned["sig"] = Value::String("UNSIGNED".to_string());
    let unsigned_output = run_client(&endpoint, &cert_path, &unsigned);
    assert_error_token(
        &unsigned_output,
        "native_submit_sig_unsigned_placeholder_rejected",
    );

    let mut bad_sig = envelope.clone();
    bad_sig["sig"]["signature_hex"] = Value::String("00".repeat(96));
    let bad_sig_output = run_client(&endpoint, &cert_path, &bad_sig);
    assert_error_token(
        &bad_sig_output,
        "native_submit_sig_bls_verification_failed_CDL_118",
    );

    child.kill().ok();
    child.wait().ok();
}

#[test]
fn uncertainty_declared_is_preserved_in_node_records() {
    let validated = manual_validated_envelope(
        "assert.truth",
        json!({
            "content": {"claim": "uncertainty propagation check"},
            "epistemic_type": "objective",
            "parent_node_ids": [],
            "primitive_type": "observation",
        }),
    );
    let validated = ValidatedEnvelope {
        uncertainty_declared: Some("bounded by sensor calibration drift".to_string()),
        ..validated
    };
    let record = node_record_from_validated(&validated).expect("node record");
    assert_eq!(
        record["uncertainty_declared"],
        "bounded by sensor calibration drift"
    );
}

#[test]
fn refute_claim_popperian_criterion_is_enforced_before_write() {
    let mut invalid = manual_validated_envelope(
        "refute.claim",
        json!({
            "target_node_id": "bafyreibase",
            "refutation_criterion": {
                "evidence_type": "empirical",
                "scope_boundary": "bounded test",
                "claim_form": "singular",
                "has_falsifiable_test": true
            },
            "evidence_node_ids": ["bafyreibaseevidence"]
        }),
    );
    let temp = tempfile::tempdir().expect("tempdir");
    assert_eq!(
        write_submission_to_lmdb(temp.path().to_str().unwrap(), &invalid)
            .expect_err("missing claim rejected"),
        "MALFORMED_REFUTATION_CRITERION"
    );

    invalid.payload = json!({
        "target_node_id": "bafyreibase",
        "refutation_criterion": {
            "claim": "the measured output is reproducible",
            "evidence_type": "empirical",
            "scope_boundary": "bounded test",
            "claim_form": "singular",
            "has_falsifiable_test": true,
            "agreement_score": "0.84",
            "reproducibility_threshold": "0.85"
        },
        "evidence_node_ids": ["bafyreibaseevidence"]
    });
    assert_eq!(
        write_submission_to_lmdb(temp.path().to_str().unwrap(), &invalid)
            .expect_err("threshold failure rejected"),
        "MALFORMED_REFUTATION_CRITERION"
    );

    let valid = manual_validated_envelope(
        "refute.claim",
        json!({
            "target_node_id": "bafyreibase",
            "refutation_criterion": {
                "claim": "the measured output is reproducible",
                "evidence_type": "empirical",
                "scope_boundary": "bounded test",
                "claim_form": "singular",
                "has_falsifiable_test": true,
                "agreement_score": "0.90",
                "reproducibility_threshold": "0.85"
            },
            "evidence_node_ids": ["bafyreibaseevidence"]
        }),
    );
    let temp = tempfile::tempdir().expect("tempdir");
    let receipt = write_submission_to_lmdb(temp.path().to_str().unwrap(), &valid)
        .expect("valid refute.claim writes");
    assert_eq!(receipt.node_id, None);
    assert_eq!(receipt.nodes_written, 0);
    assert_eq!(receipt.edges_written, 2);
    assert_eq!(receipt.native_submit_replay_written, 1);
}

#[derive(Debug, PartialEq, Eq)]
struct RawRow {
    key_hex: String,
    value_hex: String,
}

fn raw_db_hex(path: &Path, db_name: &str) -> Vec<RawRow> {
    let env = Environment::new()
        .set_max_dbs(16)
        .open(path)
        .expect("open lmdb");
    let db = env.open_db(Some(db_name)).expect("open db");
    let txn = env.begin_ro_txn().expect("read txn");
    let mut cursor = txn.open_ro_cursor(db).expect("cursor");
    let mut rows = Vec::new();
    for item in cursor.iter() {
        let (key, value) = item.expect("row");
        rows.push(RawRow {
            key_hex: hex_encode(key),
            value_hex: hex_encode(value),
        });
    }
    rows
}

fn rows_from_vectors(keys: &[Value], values: &[Value]) -> Vec<RawRow> {
    keys.iter()
        .zip(values)
        .map(|(key, value)| RawRow {
            key_hex: key.as_str().unwrap().to_string(),
            value_hex: value.as_str().unwrap().to_string(),
        })
        .collect()
}

fn contains_non_integer_number(value: &Value) -> bool {
    match value {
        Value::Number(number) => !(number.is_i64() || number.is_u64()),
        Value::Array(items) => items.iter().any(contains_non_integer_number),
        Value::Object(object) => object.values().any(contains_non_integer_number),
        _ => false,
    }
}

fn run_client(endpoint: &str, cert_path: &Path, envelope: &Value) -> Output {
    let mut client = Command::new(env!("CARGO_BIN_EXE_ilc_native_submit_client"))
        .arg("--endpoint")
        .arg(endpoint)
        .arg("--expected-tls-fingerprint")
        .arg(cert_der_sha256(cert_path))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("client starts");
    client
        .stdin
        .as_mut()
        .unwrap()
        .write_all(&json_bytes(envelope))
        .expect("write envelope");
    client.wait_with_output().expect("client output")
}

fn assert_error_token(output: &Output, token: &str) {
    assert!(
        !output.status.success(),
        "expected {token} failure, got success stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    let payload: Value = serde_json::from_slice(&output.stdout).expect("error JSON");
    assert_eq!(payload["ok"], false);
    assert_eq!(payload["error"], token);
}

fn wait_for_receiver_ready(endpoint: &str, cert_path: &Path) {
    let deadline = Instant::now() + Duration::from_secs(5);
    let probe = serde_json::json!({"not":"a valid native submit envelope"});
    loop {
        let output = run_client(endpoint, cert_path, &probe);
        if !output.status.success()
            && serde_json::from_slice::<Value>(&output.stdout)
                .ok()
                .and_then(|payload| payload["error"].as_str().map(str::to_string))
                .as_deref()
                == Some("protocol_version_invalid")
        {
            return;
        }
        if Instant::now() >= deadline {
            panic!(
                "receiver did not become ready stdout={} stderr={}",
                String::from_utf8_lossy(&output.stdout),
                String::from_utf8_lossy(&output.stderr)
            );
        }
        thread::sleep(Duration::from_millis(100));
    }
}

fn free_local_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .expect("bind free port")
        .local_addr()
        .unwrap()
        .port()
}

fn manual_validated_envelope(primitive: &str, payload: Value) -> ValidatedEnvelope {
    ValidatedEnvelope {
        version: 1,
        agent_id: "a".repeat(96),
        epoch: 7,
        primitive: primitive.to_string(),
        payload,
        uncertainty_declared: None,
        sig: json!({
            "schema_version": "native_submit_sig.v0.1",
            "verifier_profile": "native_submit_sig_profile.v0.1",
            "dst": "ILC_NATIVE_TRUTH_SUBMIT_V1:ilc-public-rc-01-testnet-harness",
            "payload_sha256": "b".repeat(64),
            "key_ref": "a".repeat(96),
            "signature_hex": "c".repeat(192)
        }),
        payload_sha256: "b".repeat(64),
        canonical_preimage_bytes: Vec::new(),
    }
}

fn write_self_signed_cert(cert_path: &PathBuf, key_path: &PathBuf) {
    let rcgen::CertifiedKey { cert, key_pair } =
        rcgen::generate_simple_self_signed(vec!["localhost".into(), "127.0.0.1".into()])
            .expect("self signed cert");
    fs::write(cert_path, cert.pem()).expect("write cert");
    fs::write(key_path, key_pair.serialize_pem()).expect("write key");
}

fn cert_der_sha256(cert_path: &Path) -> String {
    let pem = fs::read_to_string(cert_path).expect("cert pem");
    let (item, _) = rustls_pemfile::read_one_from_slice(pem.as_bytes())
        .expect("read pem")
        .expect("cert item");
    match item {
        rustls_pemfile::Item::X509Certificate(cert) => {
            let digest = sha2::Sha256::digest(cert.as_ref());
            hex_encode(&digest)
        }
        _ => panic!("unexpected pem item"),
    }
}

fn hex_encode(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}
