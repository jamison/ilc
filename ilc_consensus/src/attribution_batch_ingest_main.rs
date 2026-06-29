/// attribution_batch_ingest_main.rs — Phase 1568-Fix2b-3.
///
/// Applies accepted-work ECU attributions to the Rust consensus balance store.
/// This is the narrow bridge from Python rehearsal claim artifacts into
/// `BalanceStore.apply_attribution()`. It does not perform claim review,
/// jury finality, CDL-048 conversion, ILC allocation, or epoch checkpoint
/// signing. Those remain separate production-path steps.
use std::collections::HashSet;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;

use ilc_consensus::balance_store::BalanceStore;
use ilc_consensus::types::{AgentID, AttributionBatch, EpochSeq};
use lmdb_rkv::Environment;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug)]
struct CliArgs {
    lmdb_path: Option<PathBuf>,
    input_file: PathBuf,
    dry_run: bool,
}

#[derive(Debug, Deserialize)]
struct JsonAttributionBatch {
    epoch: u64,
    attributions: Vec<JsonAttribution>,
}

#[derive(Debug, Deserialize)]
struct JsonAttribution {
    agent_id_hex: String,
    amount_micro_ecu: u64,
}

#[derive(Debug, Serialize)]
struct IngestReport {
    marker: &'static str,
    dry_run: bool,
    epoch: u64,
    attribution_count: usize,
    total_micro_ecu: u64,
    input_sha256: String,
    balances: Vec<BalanceReport>,
}

#[derive(Debug, Serialize)]
struct BalanceReport {
    agent_id_hex: String,
    amount_micro_ecu: u64,
    epoch: u64,
    version: u64,
}

fn main() {
    match run() {
        Ok(report) => {
            println!(
                "{}",
                serde_json::to_string(&report).expect("serialize ingest report")
            );
        }
        Err(err) => {
            eprintln!("{err}");
            std::process::exit(1);
        }
    }
}

fn run() -> Result<IngestReport, String> {
    let args = parse_args(&std::env::args().collect::<Vec<_>>())?;
    let input_bytes =
        fs::read(&args.input_file).map_err(|err| format!("input_file_read_failed: {err}"))?;
    let input_sha256 = hex_encode(&Sha256::digest(&input_bytes));
    let json_batch: JsonAttributionBatch =
        serde_json::from_slice(&input_bytes).map_err(|err| format!("input_json_invalid: {err}"))?;
    let batch = to_attribution_batch(json_batch)?;
    let total_micro_ecu = checked_total(&batch)?;

    if args.dry_run {
        return Ok(IngestReport {
            marker: "attribution_batch_ingest_ok",
            dry_run: true,
            epoch: batch.epoch.0,
            attribution_count: batch.attributions.len(),
            total_micro_ecu,
            input_sha256,
            balances: vec![],
        });
    }

    let Some(lmdb_path) = args.lmdb_path else {
        return Err("--lmdb is required unless --dry-run is set".to_string());
    };
    fs::create_dir_all(&lmdb_path).map_err(|err| format!("lmdb_dir_create_failed: {err}"))?;
    let env = Arc::new(
        Environment::new()
            .set_max_dbs(1)
            .open(&lmdb_path)
            .map_err(|err| format!("lmdb_open_failed: {err}"))?,
    );
    let store =
        BalanceStore::new(env).map_err(|err| format!("balance_store_open_failed: {err}"))?;
    let balance_agents: Vec<AgentID> = batch
        .attributions
        .iter()
        .map(|(agent_id, _)| *agent_id)
        .collect();
    store
        .apply_attribution(batch)
        .map_err(|err| format!("balance_store_apply_attribution_failed: {err}"))?;
    let mut balances = Vec::new();
    for agent_id in balance_agents {
        let balance = store
            .get_balance(&agent_id)
            .map_err(|err| format!("balance_store_get_balance_failed: {err}"))?;
        balances.push(BalanceReport {
            agent_id_hex: hex_encode(&agent_id.0),
            amount_micro_ecu: balance.amount_micro_ecu,
            epoch: balance.epoch.0,
            version: balance.version,
        });
    }
    Ok(IngestReport {
        marker: "attribution_batch_ingest_ok",
        dry_run: false,
        epoch: balances.first().map(|item| item.epoch).unwrap_or(0),
        attribution_count: balances.len(),
        total_micro_ecu,
        input_sha256,
        balances,
    })
}

fn parse_args(args: &[String]) -> Result<CliArgs, String> {
    let mut idx = 1;
    let mut lmdb_path: Option<PathBuf> = None;
    let mut input_file: Option<PathBuf> = None;
    let mut dry_run = false;
    while idx < args.len() {
        match args[idx].as_str() {
            "--lmdb" => {
                idx += 1;
                let Some(value) = args.get(idx) else {
                    return Err("--lmdb requires a value".to_string());
                };
                lmdb_path = Some(PathBuf::from(value));
            }
            "--input-file" => {
                idx += 1;
                let Some(value) = args.get(idx) else {
                    return Err("--input-file requires a value".to_string());
                };
                input_file = Some(PathBuf::from(value));
            }
            "--dry-run" => {
                dry_run = true;
            }
            "--help" | "-h" => {
                return Err(usage());
            }
            other => {
                return Err(format!("unknown argument: {other}"));
            }
        }
        idx += 1;
    }
    let Some(input_file) = input_file else {
        return Err("--input-file is required".to_string());
    };
    Ok(CliArgs {
        lmdb_path,
        input_file,
        dry_run,
    })
}

fn usage() -> String {
    "Usage: attribution_batch_ingest --input-file <json> [--lmdb <path>] [--dry-run]".to_string()
}

fn to_attribution_batch(json_batch: JsonAttributionBatch) -> Result<AttributionBatch, String> {
    if json_batch.attributions.is_empty() {
        return Err("attributions_must_not_be_empty".to_string());
    }
    let mut seen = HashSet::new();
    let mut attributions = Vec::with_capacity(json_batch.attributions.len());
    for item in json_batch.attributions {
        let agent_id = parse_agent_id_hex(&item.agent_id_hex)?;
        if item.amount_micro_ecu == 0 {
            return Err("amount_micro_ecu_must_be_positive".to_string());
        }
        if !seen.insert(agent_id) {
            return Err(format!(
                "duplicate_agent_id_in_attribution_batch: {}",
                hex_encode(&agent_id.0)
            ));
        }
        attributions.push((agent_id, item.amount_micro_ecu));
    }
    attributions.sort_by_key(|(agent_id, _)| agent_id.0);
    Ok(AttributionBatch {
        epoch: EpochSeq(json_batch.epoch),
        attributions,
    })
}

fn checked_total(batch: &AttributionBatch) -> Result<u64, String> {
    let mut total = 0u64;
    for (_, amount) in &batch.attributions {
        total = total
            .checked_add(*amount)
            .ok_or_else(|| "total_micro_ecu_overflow".to_string())?;
    }
    Ok(total)
}

fn parse_agent_id_hex(value: &str) -> Result<AgentID, String> {
    let normalized = value.trim();
    if normalized.len() != 96 {
        return Err("agent_id_hex_must_be_96_lower_hex".to_string());
    }
    if !normalized
        .as_bytes()
        .iter()
        .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
    {
        return Err("agent_id_hex_must_be_96_lower_hex".to_string());
    }
    let mut bytes = [0u8; 48];
    for (index, pair) in normalized.as_bytes().chunks_exact(2).enumerate() {
        let pair_str = std::str::from_utf8(pair).map_err(|_| "agent_id_hex_invalid_utf8")?;
        bytes[index] = u8::from_str_radix(pair_str, 16)
            .map_err(|_| "agent_id_hex_must_be_96_lower_hex".to_string())?;
    }
    Ok(AgentID(bytes))
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

#[cfg(test)]
mod tests {
    use super::*;

    fn agent_hex(byte: &str) -> String {
        byte.repeat(48)
    }

    #[test]
    fn converts_json_batch_to_sorted_attribution_batch() {
        let batch = to_attribution_batch(JsonAttributionBatch {
            epoch: 7,
            attributions: vec![
                JsonAttribution {
                    agent_id_hex: agent_hex("02"),
                    amount_micro_ecu: 2,
                },
                JsonAttribution {
                    agent_id_hex: agent_hex("01"),
                    amount_micro_ecu: 1,
                },
            ],
        })
        .unwrap();
        assert_eq!(batch.epoch.0, 7);
        assert_eq!(batch.attributions[0].0 .0, [1u8; 48]);
        assert_eq!(batch.attributions[1].0 .0, [2u8; 48]);
        assert_eq!(checked_total(&batch).unwrap(), 3);
    }

    #[test]
    fn rejects_duplicate_agent_ids_before_store_write() {
        let err = to_attribution_batch(JsonAttributionBatch {
            epoch: 7,
            attributions: vec![
                JsonAttribution {
                    agent_id_hex: agent_hex("02"),
                    amount_micro_ecu: 2,
                },
                JsonAttribution {
                    agent_id_hex: agent_hex("02"),
                    amount_micro_ecu: 1,
                },
            ],
        })
        .unwrap_err();
        assert!(err.starts_with("duplicate_agent_id_in_attribution_batch"));
    }

    #[test]
    fn rejects_malformed_agent_id_hex() {
        let err = parse_agent_id_hex(&"0".repeat(95)).unwrap_err();
        assert_eq!(err, "agent_id_hex_must_be_96_lower_hex");
        let err = parse_agent_id_hex(&"AA".repeat(48)).unwrap_err();
        assert_eq!(err, "agent_id_hex_must_be_96_lower_hex");
    }
}
