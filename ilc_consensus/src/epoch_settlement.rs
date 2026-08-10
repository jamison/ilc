use bincode;
use lmdb_rkv::{Cursor, Database, DatabaseFlags, Environment, Transaction, WriteFlags};
use std::collections::HashSet;
use std::sync::Arc;

use crate::types::{
    CIDv1Root, EpochCheckpoint, EpochSettlementRecord, ILCConsensusError, ValidatorID,
    ValidatorSet, ILC_EPOCH_SIG_DST,
};
use crate::validator::quorum_threshold;

pub const MAX_SIGNERS_PER_CHECKPOINT: usize = 1000;

/// Minimum wall-clock duration between epoch commits on mainnet (30 days in ms).
pub const MIN_EPOCH_DURATION_MS: u64 = 2_592_000_000;
/// Tolerance window for accepting checkpoints with future not_before_unix_ms (5 minutes).
pub const CLOCK_SKEW_TOLERANCE_MS: u64 = 300_000;

#[cfg(test)]
pub const TEST_MIN_EPOCH_DURATION_MS: u64 = 10_000;
#[cfg(test)]
pub const TEST_EPOCH_NOT_BEFORE_BASE_MS: u64 = 1_000_000;

#[cfg(test)]
fn effective_min_epoch_duration_ms() -> u64 {
    TEST_MIN_EPOCH_DURATION_MS
}

#[cfg(not(test))]
fn effective_min_epoch_duration_ms() -> u64 {
    MIN_EPOCH_DURATION_MS
}

fn min_epoch_duration_ms_override_or_default(override_ms: Option<u64>) -> u64 {
    override_ms.unwrap_or_else(effective_min_epoch_duration_ms)
}

#[cfg(test)]
pub fn test_epoch_not_before_unix_ms(epoch: u64) -> u64 {
    TEST_EPOCH_NOT_BEFORE_BASE_MS.saturating_add(
        epoch
            .saturating_sub(1)
            .saturating_mul(effective_min_epoch_duration_ms()),
    )
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct StoredCheckpoint {
    pub record: EpochSettlementRecord,
    pub agg_sig_bytes: Vec<u8>,
    /// Signing subset stored alongside the aggregate so the recovery path can
    /// reconstruct a valid EpochCheckpoint without re-gossiping the signers.
    pub signers: Vec<ValidatorID>,
}

/// Singleton key in the epoch_records DB storing the latest committed epoch number as a raw u64.
/// Kept in-band but distinguishable from epoch record keys (which are 8-byte big-endian u64s
/// for epoch numbers 0..u64::MAX-1) by using a dedicated 1-byte sentinel key.
const CURRENT_EPOCH_SENTINEL: &[u8] = b"\xff";
const EPOCH_PROPOSAL_SEEN_PREFIX: &[u8] = b"seen_epoch_proposal:";

/// EpochStore securely harbors the definitive Epoch boundaries natively aligned to the DAG-consensus.
/// Segregated cleanly from the ECU balance mutations.
pub struct EpochStore {
    env: Arc<Environment>,
    db: Database,
    min_epoch_duration_ms_override: Option<u64>,
}

fn epoch_proposal_seen_key(idempotency_key: &str) -> Vec<u8> {
    let mut key = Vec::with_capacity(EPOCH_PROPOSAL_SEEN_PREFIX.len() + idempotency_key.len());
    key.extend_from_slice(EPOCH_PROPOSAL_SEEN_PREFIX);
    key.extend_from_slice(idempotency_key.as_bytes());
    key
}

impl EpochStore {
    pub fn new(env: Arc<Environment>) -> Result<Self, ILCConsensusError> {
        Self::new_with_min_epoch_duration_ms(env, None)
    }

    pub fn new_with_min_epoch_duration_ms(
        env: Arc<Environment>,
        min_epoch_duration_ms_override: Option<u64>,
    ) -> Result<Self, ILCConsensusError> {
        let db = env
            .create_db(Some("epoch_records"), DatabaseFlags::empty())
            .map_err(|e| {
                ILCConsensusError::Other(format!("Failed to create epoch_records DB: {}", e))
            })?;
        Ok(Self {
            env,
            db,
            min_epoch_duration_ms_override,
        })
    }

    fn effective_min_epoch_duration_ms(&self) -> u64 {
        min_epoch_duration_ms_override_or_default(self.min_epoch_duration_ms_override)
    }

    pub fn has_seen_epoch_proposal(
        &self,
        idempotency_key: &str,
    ) -> Result<bool, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RO txn: {}", e)))?;
        match txn.get(self.db, &epoch_proposal_seen_key(idempotency_key)) {
            Ok(_) => Ok(true),
            Err(lmdb_rkv::Error::NotFound) => Ok(false),
            Err(e) => Err(ILCConsensusError::Other(format!(
                "Epoch proposal idempotency read error: {}",
                e
            ))),
        }
    }

    pub fn mark_seen_epoch_proposal(&self, idempotency_key: &str) -> Result<(), ILCConsensusError> {
        let mut txn = self
            .env
            .begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;
        txn.put(
            self.db,
            &epoch_proposal_seen_key(idempotency_key),
            &1u64.to_be_bytes(),
            WriteFlags::empty(),
        )
        .map_err(|e| {
            ILCConsensusError::Other(format!("Epoch proposal idempotency Put error: {}", e))
        })?;
        txn.commit().map_err(|e| {
            ILCConsensusError::Other(format!("Epoch proposal idempotency Commit error: {}", e))
        })
    }

    /// Write an epoch record directly — called only by `handle_epoch_settlement_tx` which is
    /// gated to `testnet_fault_sim` builds (CRIT-001). Records committed via this path carry
    /// `agg_sig_bytes: vec![]` (no BLS verification). Production epoch commits go through
    /// `process_epoch_checkpoint` which performs full BLS AggSig verification before writing.
    /// Enforces the same monotonicity constraint as EpochSettlementProtocol: returns InvalidEpoch
    /// if the epoch has already been committed.
    // MEDIUM-001 fix: gate the function itself (not just its caller) to testnet_fault_sim.
    // This makes the compile-time invariant explicit: commit_epoch_record (BLS-bypass path)
    // cannot be called from production code because the symbol does not exist outside the
    // testnet_fault_sim feature. The caller (handle_epoch_settlement_tx) is already gated;
    // this adds defense-in-depth at the function level.
    #[cfg(feature = "testnet_fault_sim")]
    pub fn commit_epoch_record(
        &self,
        record: EpochSettlementRecord,
    ) -> Result<(), ILCConsensusError> {
        let mut txn = self
            .env
            .begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        let key_bytes = record.epoch.0.to_be_bytes();
        if txn.get(self.db, &key_bytes).is_ok() {
            return Err(ILCConsensusError::InvalidEpoch);
        }

        let stored = StoredCheckpoint {
            record,
            agg_sig_bytes: vec![],
            signers: vec![], // testnet_fault_sim path: no BLS sig, no signers
        };

        let val_bytes = bincode::serialize(&stored)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;

        txn.put(self.db, &key_bytes, &val_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        let mut update_sentinel = true;
        if let Ok(bytes) = txn.get(self.db, &CURRENT_EPOCH_SENTINEL) {
            let mut buf = [0u8; 8];
            buf.copy_from_slice(bytes);
            let current = u64::from_be_bytes(buf);
            if stored.record.epoch.0 <= current {
                update_sentinel = false;
            }
        }
        if update_sentinel {
            txn.put(
                self.db,
                &CURRENT_EPOCH_SENTINEL,
                &key_bytes,
                WriteFlags::empty(),
            )
            .map_err(|e| ILCConsensusError::Other(format!("LMDB sentinel Put error: {}", e)))?;
        }

        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;

        Ok(())
    }

    /// Returns every epoch number stored in this node's epoch_records DB.
    /// Used by the M-015 epoch sync protocol to compute what a peer is missing.
    pub fn list_committed_epochs(&self) -> Result<Vec<u64>, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let mut cursor = txn
            .open_ro_cursor(self.db)
            .map_err(|e| ILCConsensusError::Other(format!("Cursor open error: {}", e)))?;
        let mut epochs = Vec::new();
        for item in cursor.iter() {
            let (k, _v) =
                item.map_err(|e| ILCConsensusError::Other(format!("Cursor iter error: {}", e)))?;
            if k.len() == 8 {
                // 8-byte big-endian u64 = epoch key; 1-byte sentinel (\xff) is skipped.
                let mut buf = [0u8; 8];
                buf.copy_from_slice(k);
                epochs.push(u64::from_be_bytes(buf));
            }
        }
        Ok(epochs)
    }

    /// Returns records with epoch > `cursor`, capped at 64 per call (OOM guard).
    ///
    /// Used to answer a MissingEpochSync request. The cursor is the peer's
    /// `latest_contiguous_epoch` — the highest N such that epochs 1..=N are all
    /// committed on the peer. Any epoch beyond that is a candidate to send back.
    ///
    /// This is the SEC-008 cursor approach: O(1) request wire size vs the prior
    /// O(N) `get_epochs_not_in` which required sending all known epochs over the
    /// wire and would have hit the 10 MB frame ceiling at ~1.3 M epochs.
    pub fn get_epochs_after(
        &self,
        cursor: u64,
    ) -> Result<Vec<StoredCheckpoint>, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let mut db_cursor = txn
            .open_ro_cursor(self.db)
            .map_err(|e| ILCConsensusError::Other(format!("Cursor open error: {}", e)))?;
        let mut records = Vec::new();
        for item in db_cursor.iter() {
            let (k, v) =
                item.map_err(|e| ILCConsensusError::Other(format!("Cursor iter error: {}", e)))?;
            if k.len() != 8 {
                continue; // Skip the 1-byte sentinel key.
            }
            let mut buf = [0u8; 8];
            buf.copy_from_slice(k);
            let epoch_num = u64::from_be_bytes(buf);
            if epoch_num <= cursor {
                continue; // Peer already has this epoch.
            }
            let record: StoredCheckpoint = bincode::deserialize(v)
                .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?;
            records.push(record);
            if records.len() >= 64 {
                break; // OOM guard: cap per-response at 64 records.
            }
        }
        Ok(records)
    }

    pub fn get_checkpoint(
        &self,
        epoch: u64,
    ) -> Result<Option<StoredCheckpoint>, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let key_bytes = epoch.to_be_bytes();
        match txn.get(self.db, &key_bytes) {
            Ok(bytes) => {
                let record: StoredCheckpoint = bincode::deserialize(bytes)
                    .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?;
                Ok(Some(record))
            }
            Err(lmdb_rkv::Error::NotFound) => Ok(None),
            Err(e) => Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
    }

    /// Fetches the latest canonical Epoch via O(1) singleton sentinel key lookup.
    /// The sentinel is updated atomically alongside each epoch record commit.
    pub fn get_current_epoch(&self) -> Result<u64, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;

        match txn.get(self.db, &CURRENT_EPOCH_SENTINEL) {
            Ok(bytes) => {
                let mut buf = [0u8; 8];
                buf.copy_from_slice(bytes);
                Ok(u64::from_be_bytes(buf))
            }
            Err(lmdb_rkv::Error::NotFound) => Ok(0), // No epoch committed yet; genesis stub
            Err(e) => Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
    }
}

/// The Shared-Object equivalent to the BCB FastPath.
pub struct EpochSettlementProtocol {
    epoch_store: Arc<EpochStore>,
}

impl EpochSettlementProtocol {
    pub fn new(epoch_store: Arc<EpochStore>) -> Self {
        Self { epoch_store }
    }

    /// Executed via the ApplicationInterface trait boundary upon DAG commitment.
    /// Strictly protects Monotonicity property.
    pub fn process_epoch_checkpoint(
        &self,
        checkpoint: EpochCheckpoint,
        validator_set: &ValidatorSet,
    ) -> Result<CIDv1Root, ILCConsensusError> {
        // SEC-009: BLS AggSig verification — HIGH-002 fix.
        //
        // Accept any signing subset of size >= quorum_threshold(N). The checkpoint
        // names exactly which validators signed (`checkpoint.signers`). We verify:
        //   1. The signing subset is large enough (>= quorum_threshold).
        //   2. No duplicate signer IDs (prevents inflation of the apparent quorum size).
        //   3. All signers are members of the active validator set.
        //   4. The aggregate sig verifies against exactly the signing subset's public keys.
        //
        // Safety is preserved: `fast_aggregate_verify` checks the aggregate equals the
        // product of the individual signatures for the named keys — a forged sig still
        // fails. Claiming more signers than actually signed also fails: a subset aggregate
        // cannot verify against a larger superset of public keys.
        let n = validator_set.validators.len();
        let threshold = quorum_threshold(n);

        if checkpoint.signers.len() < threshold {
            return Err(ILCConsensusError::InsufficientSignatures);
        }
        if checkpoint.signers.len() > MAX_SIGNERS_PER_CHECKPOINT
            || checkpoint.signers.len() > validator_set.validators.len()
        {
            return Err(ILCConsensusError::InvalidSignature);
        }

        // Duplicate signer check.
        let mut seen: HashSet<ValidatorID> = HashSet::with_capacity(checkpoint.signers.len());
        for &signer_id in &checkpoint.signers {
            if !seen.insert(signer_id) {
                return Err(ILCConsensusError::Other(format!(
                    "duplicate signer in checkpoint: validator {}",
                    signer_id.0
                )));
            }
        }

        // Resolve public keys for the signing subset only.
        let msg = bincode::serialize(&checkpoint.record)
            .map_err(|e| ILCConsensusError::Other(format!("BLS msg serialize error: {}", e)))?;
        let mut pub_keys: Vec<blst::min_pk::PublicKey> =
            Vec::with_capacity(checkpoint.signers.len());
        for &signer_id in &checkpoint.signers {
            let vk = validator_set.validators.get(&signer_id).ok_or_else(|| {
                ILCConsensusError::Other(format!(
                    "signer validator {} not in active validator set",
                    signer_id.0
                ))
            })?;
            pub_keys.push(vk.0.clone());
        }
        let pk_refs: Vec<&blst::min_pk::PublicKey> = pub_keys.iter().collect();

        let sig = checkpoint.sigs.0.to_signature();
        let blst_result =
            sig.fast_aggregate_verify(true, msg.as_slice(), ILC_EPOCH_SIG_DST, &pk_refs);
        if blst_result != blst::BLST_ERROR::BLST_SUCCESS {
            return Err(ILCConsensusError::BLSVerificationFailed);
        }

        // SEC-FIX-03: Epoch timing enforcement.
        // Reject checkpoints claiming to be valid far in the future (clock skew guard).
        // Phase 1588: this guard is unconditional; no genesis/runtime flag can bypass it.
        let now_ms = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);
        if checkpoint.record.not_before_unix_ms > now_ms.saturating_add(CLOCK_SKEW_TOLERANCE_MS) {
            return Err(ILCConsensusError::Other(
                "epoch_checkpoint_not_before_too_far_future".to_string(),
            ));
        }

        let mut txn = self
            .epoch_store
            .env
            .begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        // SEC-FIX-02: Strict sequential monotonicity — read sentinel inside the write
        // transaction (TOCTOU-safe) and enforce epoch == current_epoch + 1.
        //
        // The prior guard only checked for duplicates (is_ok()), which allowed an
        // attacker with a valid BLS-signed checkpoint for epoch N+K (K>1) to jump the
        // sentinel forward, permanently fragmenting the epoch chain and breaking
        // get_epoch_chain() at the first gap.
        //
        // Note: commit_epoch_record (testnet_fault_sim path) intentionally does NOT
        // enforce +1 — it is used for direct test injection without ordering constraints.
        let current_epoch = match txn.get(self.epoch_store.db, &CURRENT_EPOCH_SENTINEL) {
            Ok(bytes) => {
                let mut buf = [0u8; 8];
                buf.copy_from_slice(bytes);
                u64::from_be_bytes(buf)
            }
            Err(lmdb_rkv::Error::NotFound) => 0, // No epoch committed yet; genesis stub.
            Err(e) => {
                return Err(ILCConsensusError::Other(format!(
                    "Sentinel read error: {}",
                    e
                )))
            }
        };
        let next_epoch = current_epoch
            .checked_add(1)
            .ok_or(ILCConsensusError::InvalidEpoch)?; // u64::MAX sentinel — unreachable in practice
        if checkpoint.record.epoch.0 != next_epoch {
            return Err(ILCConsensusError::InvalidEpoch);
        }

        // SEC-FIX-03: Minimum epoch duration enforcement.
        // If this is not the first epoch, verify the checkpoint's
        // not_before_unix_ms is at least MIN_EPOCH_DURATION_MS after the previous epoch's value.
        if current_epoch > 0 {
            // Read the previous epoch's not_before_unix_ms from LMDB.
            let prev_key = current_epoch.to_be_bytes();
            match txn.get(self.epoch_store.db, &prev_key) {
                Ok(bytes) => {
                    let prev_stored: StoredCheckpoint =
                        bincode::deserialize(bytes).map_err(|e| {
                            ILCConsensusError::Other(format!("Prev epoch deserialize error: {}", e))
                        })?;
                    let prev_not_before = prev_stored.record.not_before_unix_ms;
                    if checkpoint.record.not_before_unix_ms
                        < prev_not_before
                            .saturating_add(self.epoch_store.effective_min_epoch_duration_ms())
                    {
                        return Err(ILCConsensusError::Other(
                            "epoch_checkpoint_min_duration_not_elapsed".to_string(),
                        ));
                    }
                }
                Err(lmdb_rkv::Error::NotFound) => {
                    // Previous epoch not found — should not happen after +1 guard, but treat as non-fatal.
                }
                Err(e) => {
                    return Err(ILCConsensusError::Other(format!(
                        "Prev epoch read error: {}",
                        e
                    )));
                }
            }
        }

        // Duplicate check (kept for defence-in-depth; should never fire after the +1 guard).
        let current_key_bytes = checkpoint.record.epoch.0.to_be_bytes();
        if txn.get(self.epoch_store.db, &current_key_bytes).is_ok() {
            return Err(ILCConsensusError::InvalidEpoch);
        }

        let sig_bytes = checkpoint.sigs.0.to_signature().compress().to_vec();
        let stored = StoredCheckpoint {
            record: checkpoint.record.clone(),
            agg_sig_bytes: sig_bytes,
            signers: checkpoint.signers.clone(),
        };

        // Store epoch record natively carrying aggregated signature bounds
        let val_bytes = bincode::serialize(&stored)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;

        txn.put(
            self.epoch_store.db,
            &current_key_bytes,
            &val_bytes,
            WriteFlags::empty(),
        )
        .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        // Sentinel always updated: monotonicity guard above guarantees
        // checkpoint.record.epoch == current_epoch + 1.
        txn.put(
            self.epoch_store.db,
            &CURRENT_EPOCH_SENTINEL,
            &current_key_bytes,
            WriteFlags::empty(),
        )
        .map_err(|e| ILCConsensusError::Other(format!("LMDB sentinel Put error: {}", e)))?;

        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;

        Ok(checkpoint.record.state_root)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::AggSig;
    use crate::types::EpochSeq;
    use crate::validator::quorum_threshold;
    use blst::min_pk::{AggregateSignature, SecretKey};
    use lmdb_rkv::Environment;
    use std::mem::size_of;
    use tempfile::tempdir;

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Environment::new().set_max_dbs(2).open(dir.path()).unwrap();
        (Arc::new(env), dir)
    }

    fn deterministic_ikm(seed: u32) -> [u8; 32] {
        let mut ikm = [0u8; 32];
        ikm[0..4].copy_from_slice(&seed.to_be_bytes());
        ikm
    }

    /// Returns a 2-validator set (f=0). IDs are ValidatorID(1) and ValidatorID(2).
    fn setup_validators() -> (ValidatorSet, Vec<(ValidatorID, SecretKey)>) {
        let mut entries = Vec::new();
        let mut validators = Vec::new();
        for i in 1..=2u32 {
            let sk = SecretKey::key_gen(&deterministic_ikm(i), &[]).unwrap();
            let pk = sk.sk_to_pk();
            let id = ValidatorID(i);
            entries.push((id, sk));
            validators.push((id, crate::types::ValidatorKey(pk)));
        }
        (ValidatorSet::new(validators, 0).unwrap(), entries)
    }

    /// Returns an N-validator set. IDs are ValidatorID(1)..ValidatorID(n).
    fn setup_n_validators(n: u32) -> (ValidatorSet, Vec<(ValidatorID, SecretKey)>) {
        let f = (n as usize).saturating_sub(1) / 3;
        let mut entries = Vec::new();
        let mut validators = Vec::new();
        for i in 1..=n {
            let sk = SecretKey::key_gen(&deterministic_ikm(i), &[]).unwrap();
            let pk = sk.sk_to_pk();
            let id = ValidatorID(i);
            entries.push((id, sk));
            validators.push((id, crate::types::ValidatorKey(pk)));
        }
        (ValidatorSet::new(validators, f).unwrap(), entries)
    }

    /// Aggregate signatures for the given subset of (ValidatorID, SecretKey) pairs.
    /// Returns the aggregate sig and the signer ID list.
    fn agg_sig_for_subset(
        record: &EpochSettlementRecord,
        subset: &[(ValidatorID, SecretKey)],
    ) -> (AggSig, Vec<ValidatorID>) {
        let msg = bincode::serialize(record).unwrap();
        let sigs: Vec<_> = subset
            .iter()
            .map(|(_, sk)| sk.sign(&msg, crate::types::ILC_EPOCH_SIG_DST, &[]))
            .collect();
        let sig_refs: Vec<_> = sigs.iter().collect();
        let agg = AggregateSignature::aggregate(&sig_refs, false).unwrap();
        let signers: Vec<ValidatorID> = subset.iter().map(|(id, _)| *id).collect();
        (AggSig(agg), signers)
    }

    /// Convenience: aggregate all validators in the set (sorted by ID).
    fn agg_sig_all(
        record: &EpochSettlementRecord,
        entries: &[(ValidatorID, SecretKey)],
    ) -> (AggSig, Vec<ValidatorID>) {
        let mut sorted = entries.to_vec();
        sorted.sort_by_key(|(id, _)| id.0);
        agg_sig_for_subset(record, &sorted)
    }

    fn commit_epoch(
        protocol: &EpochSettlementProtocol,
        epoch: u64,
        fill: u8,
        vset: &ValidatorSet,
        entries: &[(ValidatorID, SecretKey)],
    ) {
        let record = EpochSettlementRecord {
            epoch: EpochSeq(epoch),
            state_root: CIDv1Root::new([fill; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [fill; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(epoch),
        };
        let (sigs, signers) = agg_sig_all(&record, entries);
        let checkpoint = EpochCheckpoint {
            record,
            sigs,
            signers,
        };
        protocol.process_epoch_checkpoint(checkpoint, vset).unwrap();
    }

    #[test]
    fn test_get_epochs_after_cursor_zero_returns_all() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        commit_epoch(&protocol, 1, 0x01, &vset, &keys);
        commit_epoch(&protocol, 2, 0x02, &vset, &keys);
        commit_epoch(&protocol, 3, 0x03, &vset, &keys);

        let records = store.get_epochs_after(0).unwrap();
        assert_eq!(records.len(), 3);
        assert_eq!(records[0].record.epoch, EpochSeq(1));
        assert_eq!(records[2].record.epoch, EpochSeq(3));
    }

    #[test]
    fn test_get_epochs_after_cursor_mid_returns_tail() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        commit_epoch(&protocol, 1, 0x01, &vset, &keys);
        commit_epoch(&protocol, 2, 0x02, &vset, &keys);
        commit_epoch(&protocol, 3, 0x03, &vset, &keys);
        commit_epoch(&protocol, 4, 0x04, &vset, &keys);
        commit_epoch(&protocol, 5, 0x05, &vset, &keys);

        // Peer has epochs 1-3 contiguous; should receive 4 and 5.
        let records = store.get_epochs_after(3).unwrap();
        assert_eq!(records.len(), 2);
        assert_eq!(records[0].record.epoch, EpochSeq(4));
        assert_eq!(records[1].record.epoch, EpochSeq(5));
    }

    #[test]
    fn test_get_epochs_after_cursor_at_max_returns_empty() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        commit_epoch(&protocol, 1, 0x01, &vset, &keys);
        commit_epoch(&protocol, 2, 0x02, &vset, &keys);

        // Peer is fully caught up — nothing to send.
        let records = store.get_epochs_after(2).unwrap();
        assert!(records.is_empty());
    }

    #[test]
    fn test_get_epochs_after_empty_store_returns_empty() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());

        let records = store.get_epochs_after(0).unwrap();
        assert!(records.is_empty());
    }

    #[test]
    fn test_get_epochs_after_cap_at_64() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        // Commit 70 epochs — response should be capped at 64.
        for i in 1u64..=70 {
            commit_epoch(&protocol, i, i as u8, &vset, &keys);
        }

        let records = store.get_epochs_after(0).unwrap();
        assert_eq!(
            records.len(),
            64,
            "OOM guard must cap response at 64 records"
        );
        assert_eq!(records[0].record.epoch, EpochSeq(1));
        assert_eq!(records[63].record.epoch, EpochSeq(64));
    }

    #[test]
    fn test_cid_root_is_36_bytes() {
        assert_eq!(size_of::<CIDv1Root>(), 36);
        let sample = CIDv1Root::new([0u8; 36]);
        assert_eq!(sample.p1.len() + sample.p2.len(), 36);
    }

    #[test]
    fn test_epoch_settlement_commit() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        let epoch_record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&epoch_record, &entries);
        let checkpoint = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs,
            signers,
        };

        let result = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap();
        assert_eq!(result.p1, [1u8; 32]);
        assert_eq!(result.p2, [1u8; 4]);

        // Verify via Retrievable route
        let stored = store.get_checkpoint(1).unwrap().unwrap().record;
        assert_eq!(stored.state_root.p1, [1u8; 32]);
        assert_eq!(stored.state_root.p2, [1u8; 4]);
        assert_eq!(stored.epoch, EpochSeq(1));
    }

    #[test]
    fn test_epoch_monotonicity() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        let epoch_record = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [2u8; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(2),
        };
        let (sigs, signers) = agg_sig_all(&epoch_record, &entries);
        let checkpoint = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs,
            signers,
        };

        // Must commit epoch 1 first (strict +1 sequential enforcement, SEC-FIX-02).
        commit_epoch(&protocol, 1, 0x01, &vset, &entries);

        // Standard successfully commit Sequence 2
        assert!(protocol
            .process_epoch_checkpoint(checkpoint.clone(), &vset)
            .is_ok());

        // Identical submission violates epoch structure
        let (sigs2, signers2) = agg_sig_all(&epoch_record, &entries);
        let checkpoint_old = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs: sigs2,
            signers: signers2,
        };
        assert_eq!(
            protocol
                .process_epoch_checkpoint(checkpoint_old, &vset)
                .unwrap_err(),
            ILCConsensusError::InvalidEpoch
        );
    }

    #[test]
    fn test_forged_epoch_record_rejected() {
        // A checkpoint that claims all validators signed but whose aggregate is
        // actually from only one key must fail fast_aggregate_verify.
        // (N=2, quorum_threshold=1, but we claim 2 signers → aggregate mismatch.)
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };

        // Aggregate only the first signer's key, but claim both validators signed.
        let (forged_sigs, _) = agg_sig_for_subset(&record, &entries[0..1]);
        let all_signers: Vec<ValidatorID> = entries.iter().map(|(id, _)| *id).collect();
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs: forged_sigs,
            signers: all_signers, // claims 2 signers, aggregate only covers 1
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(err, ILCConsensusError::BLSVerificationFailed);
    }

    #[test]
    fn test_valid_checkpoint_accepted() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        // SEC-FIX-02: must start from epoch 1.
        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };

        let res = protocol.process_epoch_checkpoint(checkpoint, &vset);
        assert!(res.is_ok());
    }

    #[test]
    fn test_epoch_checkpoint_agg_sig_stored_in_lmdb() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        // SEC-FIX-02: must start from epoch 1.
        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers: signers.clone(),
        };

        protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap();

        let stored = store.get_checkpoint(1).unwrap().unwrap();
        assert_eq!(stored.agg_sig_bytes.len(), 96);
        assert_eq!(stored.signers, signers);
    }

    #[test]
    fn test_recovery_path_verifies_signature() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        // SEC-FIX-02: must use epoch 1 so the monotonicity gate passes and the
        // corrupt signature reaches fast_aggregate_verify (BLSVerificationFailed path).
        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };

        // Build a valid-format signature, but signed over a DIFFERENT record (epoch 99).
        // This ensures from_bytes succeeds (valid G2 point) but fast_aggregate_verify
        // fails (wrong message). Avoids fragile byte-corruption that may reject at
        // from_bytes depending on the specific compressed point bytes produced.
        let wrong_record = EpochSettlementRecord {
            epoch: EpochSeq(99),
            state_root: CIDv1Root::new([99u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [99u8; 32],
            not_before_unix_ms: 0,
        };
        let (wrong_agg, _) = agg_sig_all(&wrong_record, &entries);
        let wrong_sig_bytes = wrong_agg.0.to_signature().compress().to_vec();

        let all_signers: Vec<ValidatorID> = entries.iter().map(|(id, _)| *id).collect();
        let corrupted_stored = StoredCheckpoint {
            record: record.clone(),
            agg_sig_bytes: wrong_sig_bytes,
            signers: all_signers.clone(),
        };

        // Construct recovering checkpoint from stored (sig is valid-format but wrong message).
        let parsed_sig = blst::min_pk::Signature::from_bytes(&corrupted_stored.agg_sig_bytes);
        assert!(
            parsed_sig.is_ok(),
            "wrong-message sig must parse as a valid G2 point"
        );
        let agg_sig = blst::min_pk::AggregateSignature::from_signature(&parsed_sig.unwrap());

        let recovery_checkpoint = EpochCheckpoint {
            record: corrupted_stored.record,
            sigs: crate::types::AggSig(agg_sig),
            signers: all_signers,
        };

        let err = protocol
            .process_epoch_checkpoint(recovery_checkpoint, &vset)
            .unwrap_err();
        assert_eq!(err, ILCConsensusError::BLSVerificationFailed);
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-02: epoch monotonicity — strict sequential enforcement tests
    // ---------------------------------------------------------------------------

    #[test]
    fn test_process_checkpoint_skip_epoch_rejected() {
        // A valid BLS checkpoint for epoch 5 when current=0 must be rejected.
        // Prior guard only checked for duplicates; +1 enforcement blocks this.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        let record = EpochSettlementRecord {
            epoch: EpochSeq(5),
            state_root: CIDv1Root::new([5u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [5u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::InvalidEpoch,
            "epoch skip from 0 to 5 must be rejected"
        );
    }

    #[test]
    fn test_process_checkpoint_sequential_epochs_accepted() {
        // Epochs 1→2→3 committed in order must all succeed.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        for epoch in 1u64..=3 {
            let record = EpochSettlementRecord {
                epoch: EpochSeq(epoch),
                state_root: CIDv1Root::new([epoch as u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [epoch as u8; 32],
                not_before_unix_ms: test_epoch_not_before_unix_ms(epoch),
            };
            let (sigs, signers) = agg_sig_all(&record, &entries);
            let checkpoint = EpochCheckpoint {
                record: record.clone(),
                sigs,
                signers,
            };
            protocol
                .process_epoch_checkpoint(checkpoint, &vset)
                .unwrap_or_else(|e| panic!("epoch {} should be accepted: {:?}", epoch, e));
        }

        assert_eq!(store.get_current_epoch().unwrap(), 3);
    }

    #[test]
    fn test_process_checkpoint_past_epoch_rejected() {
        // After committing epoch 3, submitting epoch 2 again must return InvalidEpoch.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        commit_epoch(&protocol, 1, 0x01, &vset, &entries);
        commit_epoch(&protocol, 2, 0x02, &vset, &entries);
        commit_epoch(&protocol, 3, 0x03, &vset, &entries);

        // Now submit epoch 2 again (past epoch).
        let record = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [2u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };
        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::InvalidEpoch,
            "past epoch must be rejected after current sentinel has advanced"
        );
    }

    #[test]
    fn test_process_checkpoint_future_skip_rejected_after_established_chain() {
        // After committing 1→2→3, submitting epoch 10 must be rejected.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        commit_epoch(&protocol, 1, 0x01, &vset, &entries);
        commit_epoch(&protocol, 2, 0x02, &vset, &entries);
        commit_epoch(&protocol, 3, 0x03, &vset, &entries);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(10),
            state_root: CIDv1Root::new([10u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [10u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };
        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::InvalidEpoch,
            "epoch jump from 3 to 10 must be rejected by +1 monotonicity guard"
        );
    }

    // ---------------------------------------------------------------------------
    // HIGH-002 fix: quorum threshold tests
    // ---------------------------------------------------------------------------

    #[test]
    fn test_quorum_threshold_correctness() {
        // Phase 1590-Fix1: quorum_threshold(N) = N - floor((N-1)/3).
        assert_eq!(quorum_threshold(1), 1, "N=1: f=0, threshold=1");
        assert_eq!(quorum_threshold(2), 2, "N=2: f=0, threshold=2");
        assert_eq!(quorum_threshold(3), 3, "N=3: f=0, threshold=3");
        assert_eq!(quorum_threshold(4), 3, "N=4: f=1, threshold=3");
        assert_eq!(quorum_threshold(5), 4, "N=5: f=1, threshold=4");
        assert_eq!(quorum_threshold(6), 5, "N=6: f=1, threshold=5");
        assert_eq!(quorum_threshold(7), 5, "N=7: f=2, threshold=5");
        assert_eq!(quorum_threshold(8), 6, "N=8: f=2, threshold=6");
        assert_eq!(quorum_threshold(9), 7, "N=9: f=2, threshold=7");
        assert_eq!(quorum_threshold(10), 7, "N=10: f=3, threshold=7");
    }

    #[test]
    fn test_quorum_threshold_intersection_safety_for_intermediate_sizes() {
        for n in [5usize, 6usize] {
            let f = (n - 1) / 3;
            let threshold = quorum_threshold(n);
            let min_intersection = threshold.saturating_mul(2).saturating_sub(n);
            assert!(
                min_intersection > f,
                "N={} threshold={} must force quorum intersection > f={} to prevent Byzantine-only overlap",
                n,
                threshold,
                f
            );
        }
    }

    #[test]
    fn test_three_of_four_signers_commits_epoch() {
        // N=4, f=1: quorum_threshold=3. Three validators signing must be sufficient.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_n_validators(4);
        assert_eq!(vset.f, 1);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        // Use only the first 3 validators (IDs 1, 2, 3) — validator 4 is "offline".
        let (sigs, signers) = agg_sig_for_subset(&record, &entries[0..3]);
        assert_eq!(signers.len(), 3);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };

        let result = protocol.process_epoch_checkpoint(checkpoint, &vset);
        assert!(
            result.is_ok(),
            "3-of-4 quorum must commit epoch: {:?}",
            result
        );
    }

    #[test]
    fn test_two_of_four_signers_rejected() {
        // N=4, f=1: quorum_threshold=3. Two validators signing is insufficient.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_n_validators(4);
        assert_eq!(vset.f, 1);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_for_subset(&record, &entries[0..2]);
        assert_eq!(signers.len(), 2);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::InsufficientSignatures,
            "2-of-4 must be rejected (threshold=3)"
        );
    }

    #[test]
    fn test_duplicate_signer_rejected() {
        // Listing the same validator twice in signers must be rejected.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_n_validators(4);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, _) = agg_sig_for_subset(&record, &entries[0..3]);
        // Claim 3 signers but with a duplicate — validators 1, 1, 2 instead of 1, 2, 3.
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers: vec![ValidatorID(1), ValidatorID(1), ValidatorID(2)],
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        match err {
            ILCConsensusError::Other(msg) => {
                assert!(
                    msg.contains("duplicate signer"),
                    "error must mention duplicate signer: {msg}"
                );
            }
            other => panic!("expected Other(duplicate signer), got {:?}", other),
        }
    }

    #[test]
    fn test_unknown_signer_rejected() {
        // A signer not in the active validator set must be rejected.
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_n_validators(4);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, _) = agg_sig_for_subset(&record, &entries[0..3]);
        // Claim signers include validator 99 which is not in the active set.
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers: vec![ValidatorID(1), ValidatorID(2), ValidatorID(99)],
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        match err {
            ILCConsensusError::Other(msg) => {
                assert!(
                    msg.contains("not in active validator set"),
                    "error must mention active validator set: {msg}"
                );
            }
            other => panic!(
                "expected Other(not in active validator set), got {:?}",
                other
            ),
        }
    }

    #[test]
    fn test_signer_list_larger_than_validator_set_rejected_before_resolution() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_n_validators(4);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, mut signers) = agg_sig_for_subset(&record, &entries[0..3]);
        signers.push(ValidatorID(99));
        signers.push(ValidatorID(100));
        let checkpoint = EpochCheckpoint {
            record,
            sigs,
            signers,
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(err, ILCConsensusError::InvalidSignature);
    }

    #[test]
    fn test_signer_list_above_max_cap_rejected_before_duplicate_or_bls_resolution() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let validator_count = (MAX_SIGNERS_PER_CHECKPOINT + 1) as u32;
        let (vset, entries) = setup_n_validators(validator_count);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_for_subset(&record, &entries[0..3]);
        let oversized_signers: Vec<ValidatorID> = (1..=validator_count).map(ValidatorID).collect();
        assert_eq!(oversized_signers.len(), MAX_SIGNERS_PER_CHECKPOINT + 1);
        assert!(oversized_signers.len() <= vset.validators.len());
        assert_eq!(
            signers,
            vec![ValidatorID(1), ValidatorID(2), ValidatorID(3)]
        );
        let checkpoint = EpochCheckpoint {
            record,
            sigs,
            signers: oversized_signers,
        };

        let err = protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap_err();
        assert_eq!(err, ILCConsensusError::InvalidSignature);
    }

    #[test]
    fn test_epoch_timing_rejected_on_mainnet_if_too_soon() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        // Commit epoch 1 with a deterministic past lower-bound timestamp.
        let record1 = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(1),
        };
        let (sigs1, signers1) = agg_sig_all(&record1, &entries);
        protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record: record1,
                    sigs: sigs1,
                    signers: signers1,
                },
                &vset,
            )
            .unwrap();

        // Epoch 2 with not_before_unix_ms only 1ms after epoch 1 — must be rejected
        let record2 = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [2u8; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(1) + 1,
        };
        let (sigs2, signers2) = agg_sig_all(&record2, &entries);
        let err = protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record: record2,
                    sigs: sigs2,
                    signers: signers2,
                },
                &vset,
            )
            .unwrap_err();
        assert!(
            format!("{:?}", err).contains("min_duration_not_elapsed"),
            "expected min_duration rejection, got: {:?}",
            err
        );
    }

    #[test]
    fn test_epoch_timing_accepted_on_mainnet_after_min_duration() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        // Commit epoch 1
        let record1 = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(1),
        };
        let (sigs1, signers1) = agg_sig_all(&record1, &entries);
        protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record: record1,
                    sigs: sigs1,
                    signers: signers1,
                },
                &vset,
            )
            .unwrap();

        // Epoch 2 with not_before_unix_ms >= test minimum duration after epoch 1 — accepted.
        let record2 = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [2u8; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(2),
        };
        let (sigs2, signers2) = agg_sig_all(&record2, &entries);
        protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record: record2,
                    sigs: sigs2,
                    signers: signers2,
                },
                &vset,
            )
            .unwrap();
    }

    #[test]
    fn test_epoch_timing_enforced_unconditionally_for_back_to_back_epochs() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        commit_epoch(&protocol, 1, 0x01, &vset, &entries);

        let record = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [2u8; 32],
            not_before_unix_ms: test_epoch_not_before_unix_ms(1),
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let err = protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record,
                    sigs,
                    signers,
                },
                &vset,
            )
            .unwrap_err();
        assert!(
            format!("{:?}", err).contains("min_duration_not_elapsed"),
            "back-to-back epochs must be rejected without a testnet bypass: {:?}",
            err
        );
    }

    #[test]
    fn test_testnet_epoch_duration_override_allows_back_to_back_checkpoint_soak() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new_with_min_epoch_duration_ms(env, Some(0)).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, entries) = setup_validators();

        let record1 = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs1, signers1) = agg_sig_all(&record1, &entries);
        protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record: record1,
                    sigs: sigs1,
                    signers: signers1,
                },
                &vset,
            )
            .unwrap();

        let record = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [2u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);

        protocol
            .process_epoch_checkpoint(
                EpochCheckpoint {
                    record,
                    sigs,
                    signers,
                },
                &vset,
            )
            .unwrap();
    }
}
