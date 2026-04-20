use lmdb_rkv::{Cursor, Environment, Database, DatabaseFlags, Transaction, WriteFlags};
use std::sync::Arc;
use bincode;

use crate::types::{
    CIDv1Root, EpochCheckpoint, EpochSeq, EpochSettlementRecord, ILCConsensusError,
    ValidatorSet, ILC_EPOCH_SIG_DST,
};

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct StoredCheckpoint {
    pub record: EpochSettlementRecord,
    pub agg_sig_bytes: Vec<u8>,
}

/// Singleton key in the epoch_records DB storing the latest committed epoch number as a raw u64.
/// Kept in-band but distinguishable from epoch record keys (which are 8-byte big-endian u64s
/// for epoch numbers 0..u64::MAX-1) by using a dedicated 1-byte sentinel key.
const CURRENT_EPOCH_SENTINEL: &[u8] = b"\xff";

/// EpochStore securely harbors the definitive Epoch boundaries natively aligned to the DAG-consensus.
/// Segregated cleanly from the ECU balance mutations.
pub struct EpochStore {
    env: Arc<Environment>,
    db: Database,
}

impl EpochStore {
    pub fn new(env: Arc<Environment>) -> Result<Self, ILCConsensusError> {
        let db = env
            .create_db(Some("epoch_records"), DatabaseFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("Failed to create epoch_records DB: {}", e)))?;
        Ok(Self { env, db })
    }

    /// Write an epoch record directly (used by node control plane when processing EpochSettlementTx).
    /// Enforces the same monotonicity constraint as EpochSettlementProtocol: returns InvalidEpoch
    /// if the epoch has already been committed. Schema mapped consistently natively as StoredCheckpoint.
    pub fn commit_epoch_record(&self, record: EpochSettlementRecord) -> Result<(), ILCConsensusError> {
        let mut txn = self.env.begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        let key_bytes = record.epoch.0.to_be_bytes();
        if txn.get(self.db, &key_bytes).is_ok() {
            return Err(ILCConsensusError::InvalidEpoch);
        }

        let stored = StoredCheckpoint {
            record,
            agg_sig_bytes: vec![],
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
            txn.put(self.db, &CURRENT_EPOCH_SENTINEL, &key_bytes, WriteFlags::empty())
                .map_err(|e| ILCConsensusError::Other(format!("LMDB sentinel Put error: {}", e)))?;
        }

        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;

        Ok(())
    }

    /// Returns every epoch number stored in this node's epoch_records DB.
    /// Used by the M-015 epoch sync protocol to compute what a peer is missing.
    pub fn list_committed_epochs(&self) -> Result<Vec<u64>, ILCConsensusError> {
        let txn = self.env.begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let mut cursor = txn.open_ro_cursor(self.db)
            .map_err(|e| ILCConsensusError::Other(format!("Cursor open error: {}", e)))?;
        let mut epochs = Vec::new();
        for item in cursor.iter() {
            let (k, _v) = item
                .map_err(|e| ILCConsensusError::Other(format!("Cursor iter error: {}", e)))?;
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
        let txn = self.env.begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let mut db_cursor = txn.open_ro_cursor(self.db)
            .map_err(|e| ILCConsensusError::Other(format!("Cursor open error: {}", e)))?;
        let mut records = Vec::new();
        for item in db_cursor.iter() {
            let (k, v) = item
                .map_err(|e| ILCConsensusError::Other(format!("Cursor iter error: {}", e)))?;
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

    pub fn get_checkpoint(&self, epoch: u64) -> Result<Option<StoredCheckpoint>, ILCConsensusError> {
        let txn = self.env.begin_ro_txn()
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
        let txn = self.env.begin_ro_txn()
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
        // SEC-009: BLS AggSig verification
        let msg = bincode::serialize(&checkpoint.record)
            .map_err(|e| ILCConsensusError::Other(format!("BLS msg serialize error: {}", e)))?;
        let sig = checkpoint.sigs.0.to_signature();
        let pub_keys: Vec<blst::min_pk::PublicKey> = validator_set.validators
            .iter()
            .map(|(_, vk)| vk.0.clone())
            .collect();
        let pk_refs: Vec<&blst::min_pk::PublicKey> = pub_keys.iter().collect();
        
        let blst_result = sig.fast_aggregate_verify(
            true,
            msg.as_slice(),
            ILC_EPOCH_SIG_DST,
            &pk_refs,
        );
        if blst_result != blst::BLST_ERROR::BLST_SUCCESS {
            return Err(ILCConsensusError::BLSVerificationFailed);
        }

        let mut txn = self.epoch_store.env.begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        // Monotonicity Check
        let current_key_bytes = checkpoint.record.epoch.0.to_be_bytes();
        
        if txn.get(self.epoch_store.db, &current_key_bytes).is_ok() {
            return Err(ILCConsensusError::InvalidEpoch); 
        }

        let sig_bytes = checkpoint.sigs.0.to_signature().compress().to_vec();
        let stored = StoredCheckpoint {
            record: checkpoint.record.clone(),
            agg_sig_bytes: sig_bytes,
        };

        // Store epoch record natively carrying aggregated signature bounds
        let val_bytes = bincode::serialize(&stored)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;

        txn.put(self.epoch_store.db, &current_key_bytes, &val_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        // Update sentinel atomically in the same transaction
        let mut update_sentinel = true;
        if let Ok(bytes) = txn.get(self.epoch_store.db, &CURRENT_EPOCH_SENTINEL) {
            let mut buf = [0u8; 8];
            buf.copy_from_slice(bytes);
            let current = u64::from_be_bytes(buf);
            if checkpoint.record.epoch.0 <= current {
                update_sentinel = false;
            }
        }
        if update_sentinel {
            txn.put(self.epoch_store.db, &CURRENT_EPOCH_SENTINEL, &current_key_bytes, WriteFlags::empty())
                .map_err(|e| ILCConsensusError::Other(format!("LMDB sentinel Put error: {}", e)))?;
        }

        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;
            
        Ok(checkpoint.record.state_root)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use lmdb_rkv::Environment;
    use crate::types::AggSig;
    use blst::min_pk::{AggregateSignature, SecretKey};
    use std::mem::size_of;

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Environment::new()
            .set_max_dbs(2)
            .open(dir.path())
            .unwrap();
        (Arc::new(env), dir)
    }

    fn generate_dummy_agg_sig() -> AggSig {
        let sk = SecretKey::key_gen(&[1; 32], &[]).unwrap();
        let sig = sk.sign(b"dummy", b"DST", &[]);
        let agg = AggregateSignature::aggregate(&[&sig], false).unwrap();
        AggSig(agg)
    }

    fn setup_validators() -> (ValidatorSet, Vec<SecretKey>) {
        let mut keys = Vec::new();
        let mut validators = Vec::new();
        for i in 1..=2u32 {
            let sk = SecretKey::key_gen(&[i as u8; 32], &[]).unwrap();
            let pk = sk.sk_to_pk();
            keys.push(sk);
            validators.push((crate::types::ValidatorID(i), crate::types::ValidatorKey(pk)));
        }
        (ValidatorSet::new(validators, 0).unwrap(), keys)
    }

    fn generate_valid_agg_sig(record: &EpochSettlementRecord, keys: &[SecretKey]) -> AggSig {
        let msg = bincode::serialize(record).unwrap();
        let sigs: Vec<_> = keys.iter()
            .map(|sk| sk.sign(&msg, crate::types::ILC_EPOCH_SIG_DST, &[]))
            .collect();
        let sig_refs: Vec<_> = sigs.iter().collect();
        let agg = AggregateSignature::aggregate(&sig_refs, false).unwrap();
        AggSig(agg)
    }

    fn commit_epoch(protocol: &EpochSettlementProtocol, epoch: u64, fill: u8, vset: &ValidatorSet, keys: &[SecretKey]) {
        let record = EpochSettlementRecord {
            epoch: EpochSeq(epoch),
            state_root: CIDv1Root::new([fill; 36]),
        };
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs: generate_valid_agg_sig(&record, keys),
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
        assert_eq!(records.len(), 64, "OOM guard must cap response at 64 records");
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
        let (vset, keys) = setup_validators();

        let epoch_record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
        };

        let checkpoint = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs: generate_valid_agg_sig(&epoch_record, &keys),
        };

        let result = protocol.process_epoch_checkpoint(checkpoint, &vset).unwrap();
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
        let (vset, keys) = setup_validators();

        let epoch_record = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
        };

        let checkpoint = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs: generate_valid_agg_sig(&epoch_record, &keys),
        };

        // Standard successfully commit Sequence 2
        assert!(protocol.process_epoch_checkpoint(checkpoint.clone(), &vset).is_ok());

        // Identical submission violates epoch structure
        let checkpoint_old = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs: generate_valid_agg_sig(&epoch_record, &keys),
        };
        assert_eq!(
            protocol.process_epoch_checkpoint(checkpoint_old, &vset).unwrap_err(),
            ILCConsensusError::InvalidEpoch
        );
    }

    #[test]
    fn test_forged_epoch_record_rejected() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        
        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
        };

        // Sign with ONLY the first key instead of all N keys
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs: generate_valid_agg_sig(&record, &keys[0..1]),
        };

        let err = protocol.process_epoch_checkpoint(checkpoint, &vset).unwrap_err();
        assert_eq!(err, ILCConsensusError::BLSVerificationFailed);
    }

    #[test]
    fn test_valid_checkpoint_accepted() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        
        let record = EpochSettlementRecord {
            epoch: EpochSeq(42),
            state_root: CIDv1Root::new([42u8; 36]),
        };

        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs: generate_valid_agg_sig(&record, &keys),
        };

        let res = protocol.process_epoch_checkpoint(checkpoint, &vset);
        assert!(res.is_ok());
    }

    #[test]
    fn test_epoch_checkpoint_agg_sig_stored_in_lmdb() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        
        let record = EpochSettlementRecord {
            epoch: EpochSeq(7),
            state_root: CIDv1Root::new([7u8; 36]),
        };

        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs: generate_valid_agg_sig(&record, &keys),
        };

        protocol.process_epoch_checkpoint(checkpoint, &vset).unwrap();

        let stored = store.get_checkpoint(7).unwrap().unwrap();
        assert_eq!(stored.agg_sig_bytes.len(), 96);
    }

    #[test]
    fn test_recovery_path_verifies_signature() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();
        
        let record = EpochSettlementRecord {
            epoch: EpochSeq(9),
            state_root: CIDv1Root::new([9u8; 36]),
        };

        let mut sig_bytes = generate_valid_agg_sig(&record, &keys).0.to_signature().compress().to_vec();
        // Corrupt signature
        sig_bytes[5] ^= 0xFF;

        let corrupted_stored = StoredCheckpoint {
            record: record.clone(),
            agg_sig_bytes: sig_bytes,
        };

        // Construct recovering checkpoint from stored
        let parsed_sig = blst::min_pk::Signature::from_bytes(&corrupted_stored.agg_sig_bytes);
        assert!(parsed_sig.is_ok());
        let agg_sig = blst::min_pk::AggregateSignature::from_signature(&parsed_sig.unwrap());
        
        let recovery_checkpoint = EpochCheckpoint {
            record: corrupted_stored.record,
            sigs: crate::types::AggSig(agg_sig),
        };

        let err = protocol.process_epoch_checkpoint(recovery_checkpoint, &vset).unwrap_err();
        assert_eq!(err, ILCConsensusError::BLSVerificationFailed);
    }
}
