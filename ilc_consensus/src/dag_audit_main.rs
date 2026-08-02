/// ilc_dag_audit - Phase 805 Tier-1 public auditability verifier.
///
/// Usage:
///   ilc_dag_audit verify-epoch-chain --lmdb-path <dir> --genesis <genesis.json> [--verbose]
///
/// This binary verifies that an exported epoch_records LMDB contains a gap-free
/// epoch chain whose aggregate BLS signatures verify against the validator keys
/// declared in genesis. It intentionally has no testnet/structural-only pass
/// mode: empty or invalid aggregate signatures always fail.
use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};
use std::sync::Arc;

use blst::min_pk::{PublicKey, Signature};
use lmdb_rkv::{Cursor, Environment, EnvironmentFlags, Transaction};
use serde::Serialize;
use serde_json::Value;

use ilc_consensus::epoch_settlement::StoredCheckpoint;
use ilc_consensus::types::{CIDv1Root, ValidatorID, ILC_EPOCH_SIG_DST};

const SCHEMA_VERSION: &str = "ilc_dag_audit_v1";
const SENTINEL: &[u8] = b"\xff";
const HIGH_002_NOTE: &str = "HIGH-002 FIXED (Phase 842), hardened by Phase 1590-Fix1: EpochCheckpoint carries a signers subset. process_epoch_checkpoint accepts intersection-safe quorum_threshold(N) = N - floor((N-1)/3) signatures. At N=4: threshold=3. One offline validator no longer stalls epoch-close.";

#[derive(Debug)]
enum AuditError {
    Usage(String),
    Io(String),
}

impl AuditError {
    fn exit_code(&self) -> i32 {
        match self {
            AuditError::Usage(_) => 2,
            AuditError::Io(_) => 3,
        }
    }

    fn message(&self) -> &str {
        match self {
            AuditError::Usage(msg) | AuditError::Io(msg) => msg,
        }
    }
}

#[derive(Debug)]
struct Args {
    lmdb_path: PathBuf,
    genesis_path: PathBuf,
    verbose: bool,
}

#[derive(Serialize)]
struct GenesisAnchor {
    network_id: String,
    genesis_epoch: u64,
    validator_count: usize,
    genesis_network_note: String,
}

#[derive(Serialize)]
struct EpochResult {
    epoch: u64,
    state_root_hex: String,
    agg_sig_hex: String,
    bls_verified: bool,
    bls_error: Option<String>,
}

#[derive(Serialize)]
struct AuditReport {
    schema_version: &'static str,
    genesis_anchor: GenesisAnchor,
    epoch_results: Vec<EpochResult>,
    chain_complete: bool,
    sentinel_consistent: bool,
    all_sigs_verified: bool,
    high_002_note: &'static str,
    verdict: String,
}

struct GenesisContext {
    anchor: GenesisAnchor,
    public_keys: Vec<PublicKey>,
}

fn main() {
    match real_main() {
        Ok(exit_code) => std::process::exit(exit_code),
        Err(err) => {
            eprintln!("[dag_audit] {}", err.message());
            std::process::exit(err.exit_code());
        }
    }
}

fn real_main() -> Result<i32, AuditError> {
    let args = parse_args(&std::env::args().collect::<Vec<_>>())?;
    let report = verify_epoch_chain(&args)?;
    let exit_code = if report.verdict == "dag_audit_tier1_pass" {
        0
    } else {
        1
    };
    let json = serde_json::to_string_pretty(&report)
        .map_err(|e| AuditError::Io(format!("JSON serialize error: {}", e)))?;
    println!("{}", json);
    Ok(exit_code)
}

fn parse_args(raw: &[String]) -> Result<Args, AuditError> {
    if raw.len() < 2 || raw[1] != "verify-epoch-chain" {
        return Err(AuditError::Usage(usage()));
    }

    let mut lmdb_path: Option<PathBuf> = None;
    let mut genesis_path: Option<PathBuf> = None;
    let mut verbose = false;
    let mut i = 2;

    while i < raw.len() {
        match raw[i].as_str() {
            "--lmdb-path" => {
                i += 1;
                let value = raw.get(i).ok_or_else(|| AuditError::Usage(usage()))?;
                lmdb_path = Some(PathBuf::from(value));
            }
            "--genesis" => {
                i += 1;
                let value = raw.get(i).ok_or_else(|| AuditError::Usage(usage()))?;
                genesis_path = Some(PathBuf::from(value));
            }
            "--verbose" => {
                verbose = true;
            }
            _ => return Err(AuditError::Usage(usage())),
        }
        i += 1;
    }

    Ok(Args {
        lmdb_path: lmdb_path.ok_or_else(|| AuditError::Usage(usage()))?,
        genesis_path: genesis_path.ok_or_else(|| AuditError::Usage(usage()))?,
        verbose,
    })
}

fn usage() -> String {
    "Usage: ilc_dag_audit verify-epoch-chain --lmdb-path <dir> --genesis <genesis.json> [--verbose]"
        .to_string()
}

fn verify_epoch_chain(args: &Args) -> Result<AuditReport, AuditError> {
    let genesis = load_genesis(&args.genesis_path)?;
    if args.verbose {
        eprintln!(
            "[dag_audit] genesis network_id={} epoch={} validators={}",
            genesis.anchor.network_id, genesis.anchor.genesis_epoch, genesis.anchor.validator_count
        );
    }

    let (records, sentinel_epoch) = read_epoch_records(&args.lmdb_path, args.verbose)?;
    let max_committed = records.keys().copied().max().unwrap_or(0);
    let chain_complete = if records.is_empty() {
        false
    } else {
        let expected: Vec<u64> = (1..=max_committed).collect();
        let actual: Vec<u64> = records.keys().copied().collect();
        expected == actual
    };
    let sentinel_consistent = sentinel_epoch == Some(max_committed);

    // Build a ValidatorID → PublicKey map. Genesis validators are 0-indexed in the array;
    // ValidatorIDs are 1-indexed (ValidatorID(1) = genesis.validators[0]).
    let pk_by_id: HashMap<ValidatorID, &PublicKey> = genesis
        .public_keys
        .iter()
        .enumerate()
        .map(|(idx, pk)| (ValidatorID((idx + 1) as u32), pk))
        .collect();
    let mut epoch_results = Vec::with_capacity(records.len());
    for (epoch_num, stored) in &records {
        let result = verify_stored_checkpoint(*epoch_num, stored, &pk_by_id);
        if args.verbose {
            eprintln!(
                "[dag_audit] epoch={} bls_verified={} error={}",
                result.epoch,
                result.bls_verified,
                result.bls_error.as_deref().unwrap_or("none")
            );
        }
        epoch_results.push(result);
    }

    let all_sigs_verified =
        !epoch_results.is_empty() && epoch_results.iter().all(|entry| entry.bls_verified);

    let verdict = if records.is_empty() {
        "dag_audit_fail_no_epochs"
    } else if !chain_complete {
        "dag_audit_fail_chain_gap"
    } else if !sentinel_consistent {
        "dag_audit_fail_sentinel_mismatch"
    } else if !all_sigs_verified {
        "dag_audit_fail_bls_invalid"
    } else {
        "dag_audit_tier1_pass"
    };

    Ok(AuditReport {
        schema_version: SCHEMA_VERSION,
        genesis_anchor: genesis.anchor,
        epoch_results,
        chain_complete,
        sentinel_consistent,
        all_sigs_verified,
        high_002_note: HIGH_002_NOTE,
        verdict: verdict.to_string(),
    })
}

fn load_genesis(path: &Path) -> Result<GenesisContext, AuditError> {
    let text = std::fs::read_to_string(path).map_err(|e| {
        AuditError::Io(format!(
            "Cannot read genesis file {}: {}",
            path.display(),
            e
        ))
    })?;
    let genesis: Value = serde_json::from_str(&text)
        .map_err(|e| AuditError::Io(format!("Invalid genesis JSON: {}", e)))?;

    let network_id = genesis["network_id"]
        .as_str()
        .unwrap_or("unknown")
        .to_string();
    let genesis_epoch = genesis["epoch"].as_u64().unwrap_or(0);
    let genesis_network_note = genesis["note"].as_str().unwrap_or("").to_string();
    let validators = genesis["validators"].as_array().ok_or_else(|| {
        AuditError::Io("genesis validators array is missing or invalid".to_string())
    })?;

    let mut public_keys = Vec::with_capacity(validators.len());
    for (idx, validator) in validators.iter().enumerate() {
        let key_hex = validator
            .get("consensus_key_hex")
            .or_else(|| validator.get("validator_key"))
            .and_then(Value::as_str)
            .ok_or_else(|| {
                AuditError::Io(format!(
                    "validator index {} missing consensus_key_hex or validator_key",
                    idx
                ))
            })?;
        let key_bytes = hex_decode_exact(key_hex, 48).map_err(|e| {
            AuditError::Io(format!("validator index {} public key hex: {}", idx, e))
        })?;
        let public_key = PublicKey::from_bytes(&key_bytes).map_err(|_| {
            AuditError::Io(format!(
                "validator index {} public key is not a valid BLS12-381 G1 point",
                idx
            ))
        })?;
        public_key.validate().map_err(|_| {
            AuditError::Io(format!(
                "validator index {} public key failed G1 subgroup check",
                idx
            ))
        })?;
        public_keys.push(public_key);
    }

    Ok(GenesisContext {
        anchor: GenesisAnchor {
            network_id,
            genesis_epoch,
            validator_count: public_keys.len(),
            genesis_network_note,
        },
        public_keys,
    })
}

fn read_epoch_records(
    lmdb_path: &Path,
    verbose: bool,
) -> Result<(BTreeMap<u64, StoredCheckpoint>, Option<u64>), AuditError> {
    let env = Environment::new()
        .set_flags(EnvironmentFlags::READ_ONLY | EnvironmentFlags::NO_LOCK)
        .set_max_dbs(4)
        .open(lmdb_path)
        .map_err(|e| {
            AuditError::Io(format!(
                "Cannot open LMDB at {}: {}",
                lmdb_path.display(),
                e
            ))
        })?;
    let env = Arc::new(env);
    let db = env
        .open_db(Some("epoch_records"))
        .map_err(|e| AuditError::Io(format!("Cannot open epoch_records DB: {}", e)))?;
    let txn = env
        .begin_ro_txn()
        .map_err(|e| AuditError::Io(format!("Cannot begin read txn: {}", e)))?;
    let mut cursor = txn
        .open_ro_cursor(db)
        .map_err(|e| AuditError::Io(format!("Cannot open cursor: {}", e)))?;

    let mut records = BTreeMap::new();
    let mut sentinel_epoch: Option<u64> = None;

    for item in cursor.iter() {
        let (key, value) = item.map_err(|e| AuditError::Io(format!("Cursor iter error: {}", e)))?;
        if key == SENTINEL {
            if value.len() != 8 {
                return Err(AuditError::Io(format!(
                    "Invalid sentinel length: expected 8, got {}",
                    value.len()
                )));
            }
            let mut buf = [0u8; 8];
            buf.copy_from_slice(value);
            sentinel_epoch = Some(u64::from_be_bytes(buf));
            if verbose {
                eprintln!(
                    "[dag_audit] sentinel_current_epoch={}",
                    sentinel_epoch.unwrap_or(0)
                );
            }
            continue;
        }
        if key.len() != 8 {
            return Err(AuditError::Io(format!(
                "Unexpected epoch_records key length: {}",
                key.len()
            )));
        }
        let mut buf = [0u8; 8];
        buf.copy_from_slice(key);
        let epoch_num = u64::from_be_bytes(buf);
        let stored: StoredCheckpoint = bincode::deserialize(value).map_err(|e| {
            AuditError::Io(format!(
                "StoredCheckpoint deserialize error at epoch {}: {}",
                epoch_num, e
            ))
        })?;
        records.insert(epoch_num, stored);
    }

    Ok((records, sentinel_epoch))
}

fn verify_stored_checkpoint(
    epoch_num: u64,
    stored: &StoredCheckpoint,
    pk_by_id: &HashMap<ValidatorID, &PublicKey>,
) -> EpochResult {
    let mut result = EpochResult {
        epoch: stored.record.epoch.0,
        state_root_hex: cid_hex(&stored.record.state_root),
        agg_sig_hex: bytes_to_hex(&stored.agg_sig_bytes),
        bls_verified: false,
        bls_error: None,
    };

    if stored.record.epoch.0 != epoch_num {
        result.bls_error = Some("epoch_key_record_mismatch".to_string());
        return result;
    }
    if stored.agg_sig_bytes.is_empty() {
        result.bls_error = Some("empty_sig_testnet_fault_sim_path".to_string());
        return result;
    }
    if stored.signers.is_empty() {
        result.bls_error = Some("signers_empty_cannot_verify_subset".to_string());
        return result;
    }

    // Resolve the signing subset's public keys in signer order.
    let mut subset_keys: Vec<&PublicKey> = Vec::with_capacity(stored.signers.len());
    for &signer_id in &stored.signers {
        match pk_by_id.get(&signer_id) {
            Some(pk) => subset_keys.push(pk),
            None => {
                result.bls_error = Some(format!("signer_validator_{}_not_in_genesis", signer_id.0));
                return result;
            }
        }
    }

    let msg = match bincode::serialize(&stored.record) {
        Ok(msg) => msg,
        Err(e) => {
            result.bls_error = Some(format!("record_serialize_error: {}", e));
            return result;
        }
    };
    let sig = match Signature::from_bytes(&stored.agg_sig_bytes) {
        Ok(sig) => sig,
        Err(_) => {
            result.bls_error = Some("signature_parse_failed".to_string());
            return result;
        }
    };
    if sig.validate(true).is_err() {
        result.bls_error = Some("signature_validate_failed".to_string());
        return result;
    }

    let verify_result = sig.fast_aggregate_verify(true, &msg, ILC_EPOCH_SIG_DST, &subset_keys);
    if verify_result == blst::BLST_ERROR::BLST_SUCCESS {
        result.bls_verified = true;
    } else {
        result.bls_error = Some(format!("fast_aggregate_verify_failed:{:?}", verify_result));
    }
    result
}

fn bytes_to_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

fn cid_hex(root: &CIDv1Root) -> String {
    let mut bytes = [0u8; 36];
    bytes[..32].copy_from_slice(&root.p1);
    bytes[32..].copy_from_slice(&root.p2);
    bytes_to_hex(&bytes)
}

fn hex_decode_exact(hex: &str, expected_len: usize) -> Result<Vec<u8>, String> {
    if hex.len() != expected_len * 2 {
        return Err(format!(
            "expected {} hex chars ({} bytes), got {}",
            expected_len * 2,
            expected_len,
            hex.len()
        ));
    }
    (0..hex.len())
        .step_by(2)
        .map(|i| {
            u8::from_str_radix(&hex[i..i + 2], 16)
                .map_err(|_| format!("invalid hex at offset {}", i))
        })
        .collect::<Result<Vec<u8>, _>>()
}

#[cfg(test)]
mod tests {
    use super::*;
    use blst::min_pk::{AggregateSignature, SecretKey};
    use ilc_consensus::epoch_settlement::{
        EpochSettlementProtocol, EpochStore, MIN_EPOCH_DURATION_MS,
    };
    use ilc_consensus::types::{
        AggSig, CIDv1Root, EpochCheckpoint, EpochSeq, EpochSettlementRecord, ValidatorID,
        ValidatorKey, ValidatorSet,
    };

    #[test]
    fn dag_audit_write_fixture_from_env() {
        let Some(root) = std::env::var_os("ILC_DAG_AUDIT_FIXTURE_DIR") else {
            return;
        };
        write_fixture(Path::new(&root)).expect("fixture generation must succeed");
    }

    fn write_fixture(root: &Path) -> Result<(), Box<dyn std::error::Error>> {
        std::fs::create_dir_all(root)?;
        let lmdb_path = root.join("lmdb");
        std::fs::create_dir_all(&lmdb_path)?;
        let env = Environment::new()
            .set_max_dbs(4)
            .open(lmdb_path.as_path())?;
        let env = Arc::new(env);
        let store = Arc::new(EpochStore::new(Arc::clone(&env))?);
        let protocol = EpochSettlementProtocol::new(Arc::clone(&store));

        let keys = vec![
            SecretKey::key_gen(&[1u8; 32], &[])
                .map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "keygen failed"))?,
            SecretKey::key_gen(&[2u8; 32], &[])
                .map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "keygen failed"))?,
        ];
        let validators = keys
            .iter()
            .enumerate()
            .map(|(idx, sk)| (ValidatorID((idx + 1) as u32), ValidatorKey(sk.sk_to_pk())))
            .collect::<Vec<_>>();
        let validator_set = ValidatorSet::new(validators, 0)?;

        let all_ids: Vec<ValidatorID> = keys
            .iter()
            .enumerate()
            .map(|(idx, _)| ValidatorID((idx + 1) as u32))
            .collect();
        for epoch in 1..=3u64 {
            let record = EpochSettlementRecord {
                epoch: EpochSeq(epoch),
                state_root: CIDv1Root::new([epoch as u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [epoch as u8; 32],
                not_before_unix_ms: 1_000_000u64.saturating_add(
                    epoch
                        .saturating_sub(1)
                        .saturating_mul(MIN_EPOCH_DURATION_MS),
                ),
            };
            let checkpoint = EpochCheckpoint {
                record: record.clone(),
                sigs: aggregate_sig(&record, &keys)?,
                signers: all_ids.clone(),
            };
            protocol.process_epoch_checkpoint(checkpoint, &validator_set)?;
        }
        env.sync(true)?;
        drop(protocol);
        drop(store);
        drop(env);

        let validators_json = keys
            .iter()
            .enumerate()
            .map(|(idx, sk)| {
                let key_hex = bytes_to_hex(&sk.sk_to_pk().compress());
                serde_json::json!({
                    "validator_id": idx + 1,
                    "consensus_key_hex": key_hex,
                    "validator_key": key_hex,
                    "stake_micro_ecu": 1_000_000u64
                })
            })
            .collect::<Vec<_>>();
        let genesis = serde_json::json!({
            "network_id": "dag-audit-fixture",
            "epoch": 0,
            "validators": validators_json,
            "note": "phase 805 dag audit fixture"
        });
        std::fs::write(
            root.join("genesis.json"),
            serde_json::to_string_pretty(&genesis)?,
        )?;
        Ok(())
    }

    fn aggregate_sig(
        record: &EpochSettlementRecord,
        keys: &[SecretKey],
    ) -> Result<AggSig, Box<dyn std::error::Error>> {
        let msg = bincode::serialize(record)?;
        let sigs = keys
            .iter()
            .map(|sk| sk.sign(&msg, ILC_EPOCH_SIG_DST, &[]))
            .collect::<Vec<_>>();
        let sig_refs = sigs.iter().collect::<Vec<_>>();
        let aggregate = AggregateSignature::aggregate(&sig_refs, false).map_err(|_| {
            std::io::Error::new(std::io::ErrorKind::Other, "aggregate signature failed")
        })?;
        Ok(AggSig(aggregate))
    }
}
