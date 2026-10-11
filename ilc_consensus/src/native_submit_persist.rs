// SPDX-License-Identifier: AGPL-3.0-only

use crate::native_submit_validate::ValidatedEnvelope;
use lmdb_rkv::{Database, DatabaseFlags, Environment, Transaction, WriteFlags};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};
use std::path::Path;
use std::sync::Arc;

const CDL_075_VERSION_TAG: &str = "cdl_075.v0.1";
const TRUTH_PRIMITIVE_GRAPH_STORE_VERSION: &str = "truth_primitive_graph_store_880.v0.1";
const REPLAY_KEY_PREFIX: &str = "native_submit_replay:v1:";
const DEFAULT_MAP_SIZE_BYTES: usize = 256 * 1024 * 1024;
const CODEC_DAG_CBOR: u64 = 0x71;
const CIDV1_VERSION: u64 = 1;
const MH_SHA2_256: u64 = 0x12;
const SHA2_256_LEN: u64 = 32;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WriteReceipt {
    pub node_id: Option<String>,
    pub nodes_written: u64,
    pub edges_written: u64,
    pub native_submit_replay_written: u64,
    pub primitive: String,
    pub version: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct EdgeSpec {
    edge_type: String,
    source: String,
    target: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct GraphContract {
    primitive: String,
    creates_node: bool,
    node_primitive_type: Option<String>,
    edges: Vec<EdgeSpec>,
    uncertainty_declared: Option<String>,
}

pub fn node_record_from_validated(validated: &ValidatedEnvelope) -> Result<Value, String> {
    let contract = graph_contract_from_validated(validated)?;
    if !contract.creates_node {
        return Err("native_submit_persistence_node_record_invalid_primitive".to_string());
    }
    let mut record = Map::new();
    record.insert(
        "agent_id".to_string(),
        Value::String(validated.agent_id.clone()),
    );
    record.insert(
        "cdl_version".to_string(),
        Value::String(CDL_075_VERSION_TAG.to_string()),
    );
    record.insert("epoch".to_string(), Value::Number(validated.epoch.into()));
    record.insert("payload".to_string(), validated.payload.clone());
    record.insert(
        "primitive".to_string(),
        Value::String(validated.primitive.clone()),
    );
    record.insert(
        "primitive_type".to_string(),
        Value::String(
            contract.node_primitive_type.ok_or_else(|| {
                "native_submit_persistence_node_primitive_type_missing".to_string()
            })?,
        ),
    );
    if let Some(uncertainty) = contract.uncertainty_declared {
        record.insert(
            "uncertainty_declared".to_string(),
            Value::String(uncertainty),
        );
    }
    record.insert("v".to_string(), Value::Number(validated.version.into()));
    record.insert("native_submit_sig".to_string(), validated.sig.clone());
    Ok(Value::Object(record))
}

pub fn node_id_from_record(record: &Value) -> Result<String, String> {
    let dag_bytes = encode_dag_cbor(record)?;
    let digest = Sha256::digest(&dag_bytes);
    let mut multihash = Vec::with_capacity(34);
    encode_uvarint(MH_SHA2_256, &mut multihash);
    encode_uvarint(SHA2_256_LEN, &mut multihash);
    multihash.extend_from_slice(&digest);

    let mut cid = Vec::with_capacity(36);
    encode_uvarint(CIDV1_VERSION, &mut cid);
    encode_uvarint(CODEC_DAG_CBOR, &mut cid);
    cid.extend_from_slice(&multihash);
    Ok(base32_lower_no_pad(&cid))
}

pub fn replay_key(agent_id: &str, epoch: i64, payload_sha256: &str) -> String {
    let triple = format!("{agent_id}:{epoch}:{payload_sha256}");
    let digest = Sha256::digest(triple.as_bytes());
    format!("{REPLAY_KEY_PREFIX}{}", hex_lower(&digest))
}

pub fn replay_payload(validated: &ValidatedEnvelope) -> Value {
    let mut payload = Map::new();
    payload.insert(
        "agent_id".to_string(),
        Value::String(validated.agent_id.clone()),
    );
    payload.insert("epoch".to_string(), Value::Number(validated.epoch.into()));
    payload.insert(
        "kind".to_string(),
        Value::String("native_submit_replay".to_string()),
    );
    payload.insert(
        "payload_sha256".to_string(),
        Value::String(validated.payload_sha256.clone()),
    );
    Value::Object(payload)
}

pub fn write_submission_to_lmdb(
    db_path: &str,
    validated: &ValidatedEnvelope,
) -> Result<WriteReceipt, String> {
    let store = RustTruthPrimitiveGraphStore::open(db_path)?;
    store.write_submission(validated)
}

fn graph_contract_from_validated(validated: &ValidatedEnvelope) -> Result<GraphContract, String> {
    let payload = validated
        .payload
        .as_object()
        .ok_or_else(|| "payload_missing".to_string())?;
    let uncertainty_declared = validated.uncertainty_declared.clone();
    match validated.primitive.as_str() {
        "assert.truth" => {
            require_object(payload, "content")?;
            let primitive_type =
                require_allowed_primitive_type(require_str(payload, "primitive_type")?)?;
            require_epistemic_type(require_str(payload, "epistemic_type")?)?;
            let parents = require_array(payload, "parent_node_ids")?;
            if parents.len() > 64 {
                return Err("parent_node_ids_count_exceeded".to_string());
            }
            let mut edges = vec![EdgeSpec {
                edge_type: "asserted_by".to_string(),
                source: "new_node_id".to_string(),
                target: "agent_id".to_string(),
            }];
            for parent in parents {
                if !parent.as_str().is_some_and(|value| !value.is_empty()) {
                    return Err("parent_node_ids_invalid_entry".to_string());
                }
                edges.push(EdgeSpec {
                    edge_type: "extends".to_string(),
                    source: "new_node_id".to_string(),
                    target: "parent_node_id".to_string(),
                });
            }
            Ok(GraphContract {
                primitive: validated.primitive.clone(),
                creates_node: true,
                node_primitive_type: Some(primitive_type.to_string()),
                edges,
                uncertainty_declared,
            })
        }
        "validate.claim" => {
            require_str(payload, "target_node_id")?;
            require_decimal_confidence(payload.get("confidence"))?;
            let evidence_summary = require_str(payload, "evidence_summary")?;
            if evidence_summary.as_bytes().len() > 1024 {
                return Err("evidence_summary_too_long".to_string());
            }
            Ok(GraphContract {
                primitive: validated.primitive.clone(),
                creates_node: false,
                node_primitive_type: None,
                edges: vec![EdgeSpec {
                    edge_type: "validated_by".to_string(),
                    source: "target_node_id".to_string(),
                    target: "agent_id".to_string(),
                }],
                uncertainty_declared,
            })
        }
        "contradict.assert" => {
            let node_a_id = require_str(payload, "node_a_id")?;
            let node_b_id = require_str(payload, "node_b_id")?;
            if node_a_id == node_b_id {
                return Err("contradict_assert_same_node".to_string());
            }
            require_contradiction_scope(require_str(payload, "contradiction_scope")?)?;
            let rationale = require_str(payload, "rationale")?;
            if rationale.as_bytes().len() > 2048 {
                return Err("rationale_too_long".to_string());
            }
            Ok(GraphContract {
                primitive: validated.primitive.clone(),
                creates_node: false,
                node_primitive_type: None,
                edges: vec![EdgeSpec {
                    edge_type: "contradicts".to_string(),
                    source: "node_a_id".to_string(),
                    target: "node_b_id".to_string(),
                }],
                uncertainty_declared,
            })
        }
        "link.claim" => {
            let source_node_id = require_str(payload, "source_node_id")?;
            let target_node_id = require_str(payload, "target_node_id")?;
            if source_node_id == target_node_id {
                return Err("link_claim_same_node".to_string());
            }
            let link_type = require_link_type(require_str(payload, "link_type")?)?;
            let link_rationale = require_str(payload, "link_rationale")?;
            if link_rationale.as_bytes().len() > 1024 {
                return Err("link_rationale_too_long".to_string());
            }
            Ok(GraphContract {
                primitive: validated.primitive.clone(),
                creates_node: false,
                node_primitive_type: None,
                edges: vec![EdgeSpec {
                    edge_type: link_type.to_string(),
                    source: "source_node_id".to_string(),
                    target: "target_node_id".to_string(),
                }],
                uncertainty_declared,
            })
        }
        "refute.claim" => {
            require_str(payload, "target_node_id")?;
            let criterion = require_object(payload, "refutation_criterion")?;
            require_refutation_criterion(criterion)?;
            let evidence_ids = require_array(payload, "evidence_node_ids")?;
            if evidence_ids.len() > 64 {
                return Err("evidence_node_ids_count_exceeded".to_string());
            }
            let mut edges = vec![EdgeSpec {
                edge_type: "refuted_by".to_string(),
                source: "target_node_id".to_string(),
                target: "agent_id".to_string(),
            }];
            for evidence in evidence_ids {
                if !evidence.as_str().is_some_and(|value| !value.is_empty()) {
                    return Err("evidence_node_ids_invalid_entry".to_string());
                }
                edges.push(EdgeSpec {
                    edge_type: "supported_by".to_string(),
                    source: "refutation_context".to_string(),
                    target: "evidence_node_id".to_string(),
                });
            }
            Ok(GraphContract {
                primitive: validated.primitive.clone(),
                creates_node: false,
                node_primitive_type: None,
                edges,
                uncertainty_declared,
            })
        }
        "revise.assert" => {
            require_str(payload, "source_node_id")?;
            let revised_content = require_object(payload, "revised_content")?;
            let primitive_type =
                require_allowed_primitive_type(require_str(revised_content, "primitive_type")?)?;
            let revision_rationale = require_str(payload, "revision_rationale")?;
            if revision_rationale.as_bytes().len() > 2048 {
                return Err("revision_rationale_too_long".to_string());
            }
            Ok(GraphContract {
                primitive: validated.primitive.clone(),
                creates_node: true,
                node_primitive_type: Some(primitive_type.to_string()),
                edges: vec![
                    EdgeSpec {
                        edge_type: "asserted_by".to_string(),
                        source: "new_node_id".to_string(),
                        target: "agent_id".to_string(),
                    },
                    EdgeSpec {
                        edge_type: "revision_of".to_string(),
                        source: "new_node_id".to_string(),
                        target: "source_node_id".to_string(),
                    },
                    EdgeSpec {
                        edge_type: "revised_by".to_string(),
                        source: "source_node_id".to_string(),
                        target: "new_node_id".to_string(),
                    },
                ],
                uncertainty_declared,
            })
        }
        _ => Err("primitive_unknown".to_string()),
    }
}

pub struct RustTruthPrimitiveGraphStore {
    env: Arc<Environment>,
    nodes: Database,
    edges: Database,
    native_submit_replay: Database,
}

impl RustTruthPrimitiveGraphStore {
    pub fn open(path: impl AsRef<Path>) -> Result<Self, String> {
        std::fs::create_dir_all(path.as_ref())
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
        let env = Environment::new()
            .set_max_dbs(16)
            .set_map_size(DEFAULT_MAP_SIZE_BYTES)
            .open(path.as_ref())
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
        let nodes = env
            .create_db(Some("nodes"), DatabaseFlags::empty())
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
        let edges = env
            .create_db(Some("edges"), DatabaseFlags::empty())
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
        let native_submit_replay = env
            .create_db(Some("native_submit_replay"), DatabaseFlags::empty())
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
        Ok(Self {
            env: Arc::new(env),
            nodes,
            edges,
            native_submit_replay,
        })
    }

    pub fn write_submission(&self, validated: &ValidatedEnvelope) -> Result<WriteReceipt, String> {
        let contract = graph_contract_from_validated(validated)?;
        let replay_key = replay_key(
            &validated.agent_id,
            validated.epoch,
            &validated.payload_sha256,
        );
        let replay_payload = replay_payload(validated);

        let (node_id, node_record) = if contract.creates_node {
            let record = node_record_from_validated(validated)?;
            let node_id = node_id_from_record(&record)?;
            (Some(node_id), Some(record))
        } else {
            (None, None)
        };
        let edge_records = resolve_edges(validated, &contract, node_id.as_deref())?;

        let mut txn = self
            .env
            .begin_rw_txn()
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;

        match txn.get(self.native_submit_replay, &replay_key) {
            Ok(_) => return Err("native_submit_sig_replay_rejected_CDL_118".to_string()),
            Err(lmdb_rkv::Error::NotFound) => {}
            Err(_) => return Err("native_submit_lmdb_write_failed".to_string()),
        }

        txn.put(
            self.native_submit_replay,
            &replay_key,
            &canonical_json_bytes(&replay_payload)?,
            WriteFlags::empty(),
        )
        .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;

        let mut nodes_written = 0_u64;
        if let (Some(id), Some(record)) = (&node_id, &node_record) {
            match txn.get(self.nodes, id) {
                Ok(_) => {}
                Err(lmdb_rkv::Error::NotFound) => {
                    txn.put(
                        self.nodes,
                        id,
                        &canonical_json_bytes(record)?,
                        WriteFlags::empty(),
                    )
                    .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
                    nodes_written = 1;
                }
                Err(_) => return Err("native_submit_lmdb_write_failed".to_string()),
            }
        }

        let mut edges_written = 0_u64;
        for (edge_key, edge_value) in edge_records {
            match txn.get(self.edges, &edge_key) {
                Ok(_) => {}
                Err(lmdb_rkv::Error::NotFound) => {
                    txn.put(
                        self.edges,
                        &edge_key,
                        &canonical_json_bytes(&edge_value)?,
                        WriteFlags::empty(),
                    )
                    .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;
                    edges_written += 1;
                }
                Err(_) => return Err("native_submit_lmdb_write_failed".to_string()),
            }
        }
        txn.commit()
            .map_err(|_| "native_submit_lmdb_write_failed".to_string())?;

        Ok(WriteReceipt {
            node_id,
            nodes_written,
            edges_written,
            native_submit_replay_written: 1,
            primitive: validated.primitive.clone(),
            version: TRUTH_PRIMITIVE_GRAPH_STORE_VERSION.to_string(),
        })
    }
}

fn resolve_edges(
    validated: &ValidatedEnvelope,
    contract: &GraphContract,
    node_id: Option<&str>,
) -> Result<Vec<(String, Value)>, String> {
    let payload = validated
        .payload
        .as_object()
        .ok_or_else(|| "payload_missing".to_string())?;
    let mut parent_index = 0_usize;
    let mut evidence_index = 0_usize;
    let mut records = Vec::with_capacity(contract.edges.len());
    for edge in &contract.edges {
        let source = resolve_label(
            &edge.source,
            &validated.agent_id,
            node_id,
            payload,
            &mut parent_index,
            &mut evidence_index,
        )?;
        let target = resolve_label(
            &edge.target,
            &validated.agent_id,
            node_id,
            payload,
            &mut parent_index,
            &mut evidence_index,
        )?;
        let (Some(source), Some(target)) = (source, target) else {
            continue;
        };
        let mut record = Map::new();
        record.insert(
            "agent_id".to_string(),
            Value::String(validated.agent_id.clone()),
        );
        record.insert(
            "edge_type".to_string(),
            Value::String(edge.edge_type.clone()),
        );
        record.insert("epoch".to_string(), Value::Number(validated.epoch.into()));
        record.insert("native_submit_sig".to_string(), validated.sig.clone());
        record.insert("payload".to_string(), validated.payload.clone());
        record.insert(
            "primitive".to_string(),
            Value::String(validated.primitive.clone()),
        );
        record.insert("source".to_string(), Value::String(source.clone()));
        record.insert("target".to_string(), Value::String(target.clone()));
        record.insert("v".to_string(), Value::Number(validated.version.into()));
        if let Some(uncertainty) = &contract.uncertainty_declared {
            record.insert(
                "uncertainty_declared".to_string(),
                Value::String(uncertainty.clone()),
            );
        }
        records.push((
            format!("{source}:{}:{target}", edge.edge_type),
            Value::Object(record),
        ));
    }
    Ok(records)
}

fn resolve_label(
    label: &str,
    agent_id: &str,
    node_id: Option<&str>,
    payload: &Map<String, Value>,
    parent_index: &mut usize,
    evidence_index: &mut usize,
) -> Result<Option<String>, String> {
    match label {
        "new_node_id" => Ok(node_id.map(ToString::to_string)),
        "agent_id" => Ok(Some(agent_id.to_string())),
        "target_node_id" | "node_a_id" | "node_b_id" | "source_node_id" => payload
            .get(label)
            .and_then(Value::as_str)
            .map(ToString::to_string)
            .map(Some)
            .ok_or_else(|| "edge_label_resolution_failed".to_string()),
        "parent_node_id" => {
            let out = payload
                .get("parent_node_ids")
                .and_then(Value::as_array)
                .and_then(|items| items.get(*parent_index))
                .and_then(Value::as_str)
                .map(ToString::to_string);
            *parent_index += 1;
            Ok(out)
        }
        "refutation_context" => payload
            .get("target_node_id")
            .and_then(Value::as_str)
            .map(ToString::to_string)
            .map(Some)
            .ok_or_else(|| "edge_label_resolution_failed".to_string()),
        "evidence_node_id" => {
            let out = payload
                .get("evidence_node_ids")
                .and_then(Value::as_array)
                .and_then(|items| items.get(*evidence_index))
                .and_then(Value::as_str)
                .map(ToString::to_string);
            *evidence_index += 1;
            Ok(out)
        }
        _ => Err("edge_label_unknown".to_string()),
    }
}

pub fn canonical_json_bytes(value: &Value) -> Result<Vec<u8>, String> {
    Ok(canonical_json(value)?.into_bytes())
}

fn canonical_json(value: &Value) -> Result<String, String> {
    match value {
        Value::Null | Value::Bool(_) | Value::Number(_) | Value::String(_) => {
            serde_json::to_string(value).map_err(|_| "native_submit_json_encode_failed".to_string())
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
                        .map_err(|_| "native_submit_json_encode_failed".to_string())?,
                );
                out.push(':');
                out.push_str(&canonical_json(child)?);
            }
            out.push('}');
            Ok(out)
        }
    }
}

fn require_str<'a>(object: &'a Map<String, Value>, key: &str) -> Result<&'a str, String> {
    object
        .get(key)
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| format!("field_invalid_{key}"))
}

fn require_object<'a>(
    object: &'a Map<String, Value>,
    key: &str,
) -> Result<&'a Map<String, Value>, String> {
    object
        .get(key)
        .and_then(Value::as_object)
        .ok_or_else(|| format!("field_invalid_{key}"))
}

fn require_array<'a>(object: &'a Map<String, Value>, key: &str) -> Result<&'a Vec<Value>, String> {
    object
        .get(key)
        .and_then(Value::as_array)
        .ok_or_else(|| format!("field_invalid_{key}"))
}

fn require_allowed_primitive_type(value: &str) -> Result<&str, String> {
    match value {
        "citation"
        | "execution_descriptor"
        | "governance_proposal"
        | "knowledge_claim"
        | "observation"
        | "genesis_authority_assertion"
        | "epoch_record" => Ok(value),
        _ => Err("primitive_type_not_allowed".to_string()),
    }
}

fn require_epistemic_type(value: &str) -> Result<(), String> {
    match value {
        "objective" | "subjective" | "normative" | "creative_speculative" => Ok(()),
        _ => Err("field_value_invalid_epistemic_type".to_string()),
    }
}

fn require_contradiction_scope(value: &str) -> Result<(), String> {
    match value {
        "logical" | "empirical" | "definitional" => Ok(()),
        _ => Err("field_value_invalid_contradiction_scope".to_string()),
    }
}

fn require_link_type(value: &str) -> Result<&str, String> {
    match value {
        "cites" | "elaborates" | "contrasts" | "instantiates" | "generalizes" => Ok(value),
        _ => Err("field_value_invalid_link_type".to_string()),
    }
}

fn require_refutation_criterion(criterion: &Map<String, Value>) -> Result<(), String> {
    if criterion.get("has_falsifiable_test") != Some(&Value::Bool(true)) {
        return Err("refute_claim_has_falsifiable_test_required".to_string());
    }
    for field in ["claim", "evidence_type", "scope_boundary", "claim_form"] {
        if !criterion.contains_key(field) {
            return Err("MALFORMED_REFUTATION_CRITERION".to_string());
        }
    }
    match criterion.get("evidence_type").and_then(Value::as_str) {
        Some("empirical" | "logical" | "counter_example") => {}
        _ => return Err("MALFORMED_REFUTATION_CRITERION".to_string()),
    }
    match normalize_claim_form(criterion.get("claim_form"))?.as_str() {
        "singular" | "bounded_existential" | "falsifiable_positive" => {}
        _ => return Err("MALFORMED_REFUTATION_CRITERION".to_string()),
    }
    match criterion.get("is_inadmissible_counterexample") {
        Some(Value::Bool(true)) => return Err("MALFORMED_REFUTATION_CRITERION".to_string()),
        Some(Value::Bool(false)) | None => {}
        Some(_) => return Err("MALFORMED_REFUTATION_CRITERION".to_string()),
    }
    let default_agreement = Value::String("1.0".to_string());
    let default_threshold = Value::String("0.85".to_string());
    let agreement_score = criterion
        .get("agreement_score")
        .unwrap_or(&default_agreement);
    let reproducibility_threshold = criterion
        .get("reproducibility_threshold")
        .unwrap_or(&default_threshold);
    if !decimal_value_in_closed_unit_interval(agreement_score)
        || !decimal_value_in_closed_unit_interval(reproducibility_threshold)
    {
        return Err("MALFORMED_REFUTATION_CRITERION".to_string());
    }
    if compare_decimal_values(agreement_score, reproducibility_threshold)
        .ok_or_else(|| "MALFORMED_REFUTATION_CRITERION".to_string())?
        .is_lt()
    {
        return Err("MALFORMED_REFUTATION_CRITERION".to_string());
    }
    Ok(())
}

fn normalize_claim_form(value: Option<&Value>) -> Result<String, String> {
    let Some(Value::String(raw)) = value else {
        return Err("MALFORMED_REFUTATION_CRITERION".to_string());
    };
    let normalized = raw.trim().to_ascii_lowercase().replace('-', "_");
    if normalized.is_empty() {
        return Err("MALFORMED_REFUTATION_CRITERION".to_string());
    }
    Ok(normalized)
}

fn require_decimal_confidence(value: Option<&Value>) -> Result<(), String> {
    let Some(Value::String(raw)) = value else {
        return Err("field_invalid_confidence".to_string());
    };
    if !decimal_string_in_open_closed_unit_interval(raw) {
        return Err("field_out_of_range_confidence".to_string());
    }
    Ok(())
}

fn decimal_value_in_closed_unit_interval(value: &Value) -> bool {
    match value {
        Value::String(raw) => decimal_string_in_closed_unit_interval(raw),
        Value::Number(number) if number.is_i64() || number.is_u64() => {
            number.as_i64().is_some_and(|n| n == 0 || n == 1)
                || number.as_u64().is_some_and(|n| n == 0 || n == 1)
        }
        _ => false,
    }
}

fn decimal_string_in_open_closed_unit_interval(raw: &str) -> bool {
    decimal_string_parts(raw)
        .is_some_and(|parts| parts.nonzero_seen && decimal_parts_less_than_or_equal_one(&parts))
}

fn decimal_string_in_closed_unit_interval(raw: &str) -> bool {
    decimal_string_parts(raw).is_some_and(|parts| decimal_parts_less_than_or_equal_one(&parts))
}

#[derive(Debug)]
struct DecimalParts<'a> {
    integer_digits: &'a str,
    fractional_digits: &'a str,
    nonzero_seen: bool,
}

fn decimal_string_parts(raw: &str) -> Option<DecimalParts<'_>> {
    if raw.is_empty()
        || raw.starts_with('-')
        || raw.starts_with('+')
        || raw.contains(['e', 'E'])
        || raw == "."
    {
        return None;
    }
    let mut dot_seen = false;
    let mut digit_seen = false;
    let mut nonzero_seen = false;
    for byte in raw.bytes() {
        match byte {
            b'0'..=b'9' => {
                digit_seen = true;
                nonzero_seen |= byte != b'0';
            }
            b'.' if !dot_seen => dot_seen = true,
            _ => return None,
        }
    }
    if !digit_seen {
        return None;
    }

    let (integer_part, fractional_part) = raw.split_once('.').unwrap_or((raw, ""));
    Some(DecimalParts {
        integer_digits: integer_part.trim_start_matches('0'),
        fractional_digits: fractional_part,
        nonzero_seen,
    })
}

fn decimal_parts_less_than_or_equal_one(parts: &DecimalParts<'_>) -> bool {
    match parts.integer_digits {
        "" => true,
        "1" => parts.fractional_digits.bytes().all(|byte| byte == b'0'),
        _ => false,
    }
}

fn compare_decimal_values(left: &Value, right: &Value) -> Option<std::cmp::Ordering> {
    let left = decimal_value_to_scaled_int(left)?;
    let right = decimal_value_to_scaled_int(right)?;
    let scale = left.1.max(right.1);
    let left_scaled = left.0.checked_mul(10_u128.checked_pow(scale - left.1)?)?;
    let right_scaled = right.0.checked_mul(10_u128.checked_pow(scale - right.1)?)?;
    Some(left_scaled.cmp(&right_scaled))
}

fn decimal_value_to_scaled_int(value: &Value) -> Option<(u128, u32)> {
    match value {
        Value::String(raw) => decimal_string_to_scaled_int(raw),
        Value::Number(number) if number.is_i64() || number.is_u64() => {
            if let Some(n) = number.as_i64() {
                u128::try_from(n).ok().map(|n| (n, 0))
            } else {
                number.as_u64().map(|n| (u128::from(n), 0))
            }
        }
        _ => None,
    }
}

fn decimal_string_to_scaled_int(raw: &str) -> Option<(u128, u32)> {
    let parts = decimal_string_parts(raw)?;
    if !decimal_parts_less_than_or_equal_one(&parts) {
        return None;
    }
    let mut digits = String::new();
    digits.push_str(if parts.integer_digits.is_empty() {
        "0"
    } else {
        parts.integer_digits
    });
    digits.push_str(parts.fractional_digits);
    let scale = u32::try_from(parts.fractional_digits.len()).ok()?;
    let value = digits.parse::<u128>().ok()?;
    Some((value, scale))
}

pub fn encode_dag_cbor(value: &Value) -> Result<Vec<u8>, String> {
    let mut out = Vec::new();
    encode_dag_cbor_value(value, &mut out)?;
    Ok(out)
}

fn encode_dag_cbor_value(value: &Value, out: &mut Vec<u8>) -> Result<(), String> {
    match value {
        Value::Null => out.push(0xf6),
        Value::Bool(false) => out.push(0xf4),
        Value::Bool(true) => out.push(0xf5),
        Value::Number(number) => {
            let Some(n) = number.as_i64() else {
                return Err("dag_cbor_number_not_integer".to_string());
            };
            if n >= 0 {
                encode_type_and_len(0, n as u64, out)?;
            } else {
                encode_type_and_len(1, (-1_i128 - i128::from(n)) as u64, out)?;
            }
        }
        Value::String(text) => encode_text(text, out)?,
        Value::Array(items) => {
            encode_type_and_len(4, items.len() as u64, out)?;
            for item in items {
                encode_dag_cbor_value(item, out)?;
            }
        }
        Value::Object(object) => {
            let mut keys = Vec::with_capacity(object.len());
            for key in object.keys() {
                let mut encoded_key = Vec::new();
                encode_text(key, &mut encoded_key)?;
                keys.push((encoded_key, key));
            }
            keys.sort_by(|left, right| {
                left.0
                    .len()
                    .cmp(&right.0.len())
                    .then_with(|| left.0.cmp(&right.0))
            });
            encode_type_and_len(5, keys.len() as u64, out)?;
            for (encoded_key, key) in keys {
                out.extend_from_slice(&encoded_key);
                encode_dag_cbor_value(&object[key], out)?;
            }
        }
    }
    Ok(())
}

fn encode_text(text: &str, out: &mut Vec<u8>) -> Result<(), String> {
    let bytes = text.as_bytes();
    encode_type_and_len(3, bytes.len() as u64, out)?;
    out.extend_from_slice(bytes);
    Ok(())
}

fn encode_type_and_len(major: u8, n: u64, out: &mut Vec<u8>) -> Result<(), String> {
    let head = major << 5;
    if n <= 23 {
        out.push(head | n as u8);
    } else if n <= 0xff {
        out.push(head | 24);
        out.push(n as u8);
    } else if n <= 0xffff {
        out.push(head | 25);
        out.extend_from_slice(&(n as u16).to_be_bytes());
    } else if n <= 0xffff_ffff {
        out.push(head | 26);
        out.extend_from_slice(&(n as u32).to_be_bytes());
    } else {
        out.push(head | 27);
        out.extend_from_slice(&n.to_be_bytes());
    }
    Ok(())
}

fn encode_uvarint(mut value: u64, out: &mut Vec<u8>) {
    while value >= 0x80 {
        out.push((value as u8) | 0x80);
        value >>= 7;
    }
    out.push(value as u8);
}

fn base32_lower_no_pad(bytes: &[u8]) -> String {
    const ALPHABET: &[u8; 32] = b"abcdefghijklmnopqrstuvwxyz234567";
    let mut out = String::with_capacity(1 + (bytes.len() * 8).div_ceil(5));
    out.push('b');
    let mut buffer: u16 = 0;
    let mut bits: u8 = 0;
    for byte in bytes {
        buffer = (buffer << 8) | u16::from(*byte);
        bits += 8;
        while bits >= 5 {
            let index = ((buffer >> (bits - 5)) & 0x1f) as usize;
            out.push(ALPHABET[index] as char);
            bits -= 5;
        }
    }
    if bits > 0 {
        let index = ((buffer << (5 - bits)) & 0x1f) as usize;
        out.push(ALPHABET[index] as char);
    }
    out
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}
