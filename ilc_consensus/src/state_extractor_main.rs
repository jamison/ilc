/// state_extractor — M-016 Workload D: Replayability and State Extraction
///
/// Reads the epoch_records LMDB produced by validator_harness without
/// connecting to any live validator process.  Reconstructs the full
/// genesis-to-current epoch chain and emits a JSON report.
///
/// Usage:
///   state_extractor --lmdb-path <dir> --genesis <genesis.json>
///
/// The tool exits 0 if the epoch chain is complete (gap-free) and the
/// sentinel is consistent; exits 1 on any structural gap or integrity failure.
/// The genesis anchor (network_id, genesis_epoch, validator_count) is read
/// from genesis.json and included in the report for cross-reference; no
/// cryptographic linkage proof between genesis.json and the LMDB data is
/// performed — that requires a public query surface (M-018 gRPC scope).
use std::collections::BTreeMap;
use std::path::PathBuf;
use std::sync::Arc;

use lmdb_rkv::{Cursor, Environment, EnvironmentFlags, Transaction};
use serde::Serialize;
use serde_json::Value;

use ilc_consensus::types::{CIDv1Root, EpochSettlementRecord};

// ---------------------------------------------------------------------------
// Output structures
// ---------------------------------------------------------------------------

#[derive(Serialize)]
struct EpochEntry {
    epoch: u64,
    state_root_hex: String,
}

#[derive(Serialize)]
struct ChainReport {
    /// Extracted directly from genesis.json without operator involvement.
    genesis_anchor: GenesisAnchor,
    /// Ordered list of committed epoch records (epoch 1..N).
    epoch_chain: Vec<EpochEntry>,
    /// Epoch number stored in the LMDB sentinel key (\xff).
    sentinel_current_epoch: u64,
    /// True iff epoch_chain is a gap-free sequence 1..sentinel_current_epoch.
    chain_complete: bool,
    /// True iff sentinel_current_epoch == max committed epoch.
    sentinel_consistent: bool,
    verdict: String,
}

#[derive(Serialize)]
struct GenesisAnchor {
    network_id: String,
    genesis_epoch: u64,
    validator_count: usize,
    genesis_network_note: String,
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn bytes_to_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

fn cid_hex(root: &CIDv1Root) -> String {
    let mut bytes = [0u8; 36];
    bytes[..32].copy_from_slice(&root.p1);
    bytes[32..].copy_from_slice(&root.p2);
    bytes_to_hex(&bytes)
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let lmdb_path = parse_arg(&args, "--lmdb-path").unwrap_or_else(|| {
        eprintln!("Usage: state_extractor --lmdb-path <dir> --genesis <genesis.json>");
        std::process::exit(2);
    });
    let genesis_path = parse_arg(&args, "--genesis").unwrap_or_else(|| {
        eprintln!("Usage: state_extractor --lmdb-path <dir> --genesis <genesis.json>");
        std::process::exit(2);
    });

    // ── 1. Parse genesis anchor ────────────────────────────────────────────
    let genesis_text = std::fs::read_to_string(&genesis_path).unwrap_or_else(|e| {
        eprintln!("[m016] Cannot read genesis file {}: {}", genesis_path, e);
        std::process::exit(1);
    });
    let genesis: Value = serde_json::from_str(&genesis_text).unwrap_or_else(|e| {
        eprintln!("[m016] Invalid genesis JSON: {}", e);
        std::process::exit(1);
    });
    let network_id = genesis["network_id"].as_str().unwrap_or("unknown").to_string();
    let genesis_epoch = genesis["epoch"].as_u64().unwrap_or(0);
    let validator_count = genesis["validators"].as_array().map(|v| v.len()).unwrap_or(0);
    let genesis_note = genesis["note"].as_str().unwrap_or("").to_string();

    let genesis_anchor = GenesisAnchor {
        network_id: network_id.clone(),
        genesis_epoch,
        validator_count,
        genesis_network_note: genesis_note,
    };

    eprintln!("[m016] Genesis anchor: network_id={} epoch={} validators={}",
        network_id, genesis_epoch, validator_count);

    // ── 2. Open LMDB read-only ─────────────────────────────────────────────
    let env = Environment::new()
        .set_flags(EnvironmentFlags::READ_ONLY | EnvironmentFlags::NO_LOCK)
        .set_max_dbs(4)
        .open(PathBuf::from(&lmdb_path).as_path())
        .unwrap_or_else(|e| {
            eprintln!("[m016] Cannot open LMDB at {}: {}", lmdb_path, e);
            std::process::exit(1);
        });
    let env = Arc::new(env);

    let db = env
        .open_db(Some("epoch_records"))
        .unwrap_or_else(|e| {
            eprintln!("[m016] Cannot open epoch_records DB: {}", e);
            std::process::exit(1);
        });

    let txn = env.begin_ro_txn().unwrap_or_else(|e| {
        eprintln!("[m016] Cannot begin read txn: {}", e);
        std::process::exit(1);
    });

    // ── 3. Scan all keys ────────────────────────────────────────────────────
    let mut cursor = txn.open_ro_cursor(db).unwrap_or_else(|e| {
        eprintln!("[m016] Cannot open cursor: {}", e);
        std::process::exit(1);
    });

    // Collect: epoch_num → EpochSettlementRecord (skipping sentinel \xff key)
    let mut records: BTreeMap<u64, EpochSettlementRecord> = BTreeMap::new();
    let mut sentinel_epoch: u64 = 0;
    const SENTINEL: &[u8] = b"\xff";

    for item in cursor.iter() {
        let (k, v) = match item {
            Ok(pair) => pair,
            Err(e) => {
                eprintln!("[m016] Cursor iter error: {}", e);
                continue;
            }
        };

        if k == SENTINEL {
            // Sentinel key: value is 8-byte big-endian current epoch number.
            if v.len() == 8 {
                let mut buf = [0u8; 8];
                buf.copy_from_slice(v);
                sentinel_epoch = u64::from_be_bytes(buf);
                eprintln!("[m016] Sentinel current_epoch={}", sentinel_epoch);
            }
            continue;
        }

        if k.len() != 8 {
            eprintln!("[m016] Unexpected key length {}, skipping", k.len());
            continue;
        }

        let mut buf = [0u8; 8];
        buf.copy_from_slice(k);
        let epoch_num = u64::from_be_bytes(buf);

        let record: EpochSettlementRecord = match bincode::deserialize(v) {
            Ok(r) => r,
            Err(e) => {
                eprintln!("[m016] Deserialize error at epoch {}: {}", epoch_num, e);
                continue;
            }
        };

        eprintln!("[m016] epoch={} state_root={}", epoch_num, cid_hex(&record.state_root));
        records.insert(epoch_num, record);
    }

    // ── 4. Build ordered chain ──────────────────────────────────────────────
    let epoch_chain: Vec<EpochEntry> = records
        .values()
        .map(|r| EpochEntry {
            epoch: r.epoch.0,
            state_root_hex: cid_hex(&r.state_root),
        })
        .collect();

    // ── 5. Verify completeness ──────────────────────────────────────────────
    // Gap-free check: epochs must be consecutive starting from 1 (genesis is epoch 0).
    let max_committed = records.keys().copied().max().unwrap_or(0);
    let chain_complete = if records.is_empty() {
        false
    } else {
        let expected: Vec<u64> = (1..=max_committed).collect();
        let actual: Vec<u64> = records.keys().copied().collect();
        expected == actual
    };

    let sentinel_consistent = sentinel_epoch == max_committed;

    eprintln!(
        "[m016] chain_complete={} sentinel_consistent={} max_epoch={} sentinel={}",
        chain_complete, sentinel_consistent, max_committed, sentinel_epoch
    );

    // ── 6. Verdict ─────────────────────────────────────────────────────────
    let verdict = if chain_complete && sentinel_consistent && max_committed > 0 {
        "workload_d_replayability_pass"
    } else if max_committed == 0 {
        "workload_d_replayability_fail_no_epochs_found"
    } else if !chain_complete {
        "workload_d_replayability_fail_chain_gap"
    } else {
        "workload_d_replayability_fail_sentinel_mismatch"
    };

    let report = ChainReport {
        genesis_anchor,
        epoch_chain,
        sentinel_current_epoch: sentinel_epoch,
        chain_complete,
        sentinel_consistent,
        verdict: verdict.to_string(),
    };

    // Emit JSON report to stdout (pipe-friendly, auditable by any participant).
    println!("{}", serde_json::to_string_pretty(&report).unwrap());
    eprintln!("[m016] {}", verdict);

    if verdict == "workload_d_replayability_pass" {
        std::process::exit(0);
    } else {
        std::process::exit(1);
    }
}

// ---------------------------------------------------------------------------
// Argument parser
// ---------------------------------------------------------------------------

fn parse_arg(args: &[String], key: &str) -> Option<String> {
    args.windows(2)
        .find(|w| w[0] == key)
        .map(|w| w[1].clone())
}
