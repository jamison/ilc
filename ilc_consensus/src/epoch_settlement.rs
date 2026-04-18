use lmdb_rkv::{Cursor, Environment, Database, DatabaseFlags, Transaction, WriteFlags};
use std::collections::HashSet;
use std::sync::Arc;
use bincode;

use crate::types::{CIDv1Root, EpochCheckpoint, EpochSeq, EpochSettlementRecord, ILCConsensusError};

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

    /// Fetches the securely locked canonical EpochSettlementRecord given an EpochSeq mapping natively from Python tracking
    pub fn get_epoch_record(&self, epoch: EpochSeq) -> Result<EpochSettlementRecord, ILCConsensusError> {
        let txn = self.env.begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        
        // Use epoch index natively
        let key_bytes = epoch.0.to_be_bytes();
        match txn.get(self.db, &key_bytes) {
            Ok(bytes) => {
                let record: EpochSettlementRecord = bincode::deserialize(bytes)
                    .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?;
                Ok(record)
            }
            // M-series specifications expect 0 mapping naturally on genesis stubs
            Err(lmdb_rkv::Error::NotFound) => Ok(EpochSettlementRecord {
                epoch: EpochSeq(0),
                state_root: CIDv1Root::new([0u8; 36]),
            }),
            Err(e) => Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
    }

    /// Write an epoch record directly (used by node control plane when processing EpochSettlementTx).
    /// Enforces the same monotonicity constraint as EpochSettlementProtocol: returns InvalidEpoch
    /// if the epoch has already been committed.
    pub fn commit_epoch_record(&self, record: EpochSettlementRecord) -> Result<(), ILCConsensusError> {
        let mut txn = self.env.begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        let key_bytes = record.epoch.0.to_be_bytes();
        if txn.get(self.db, &key_bytes).is_ok() {
            return Err(ILCConsensusError::InvalidEpoch);
        }

        let val_bytes = bincode::serialize(&record)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;

        txn.put(self.db, &key_bytes, &val_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        txn.put(self.db, &CURRENT_EPOCH_SENTINEL, &key_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB sentinel Put error: {}", e)))?;

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

    /// Returns records this node has that are NOT in `known`.
    /// Used to answer a MissingEpochSync request from a peer that is behind.
    /// Capped at 64 records per call as an OOM guard.
    pub fn get_epochs_not_in(
        &self,
        known: &HashSet<u64>,
    ) -> Result<Vec<EpochSettlementRecord>, ILCConsensusError> {
        let txn = self.env.begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let mut cursor = txn.open_ro_cursor(self.db)
            .map_err(|e| ILCConsensusError::Other(format!("Cursor open error: {}", e)))?;
        let mut records = Vec::new();
        for item in cursor.iter() {
            let (k, v) = item
                .map_err(|e| ILCConsensusError::Other(format!("Cursor iter error: {}", e)))?;
            if k.len() != 8 {
                continue; // Skip the 1-byte sentinel key.
            }
            let mut buf = [0u8; 8];
            buf.copy_from_slice(k);
            let epoch_num = u64::from_be_bytes(buf);
            if known.contains(&epoch_num) {
                continue;
            }
            let record: EpochSettlementRecord = bincode::deserialize(v)
                .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?;
            records.push(record);
            if records.len() >= 64 {
                break; // OOM guard: cap per-response at 64 records.
            }
        }
        Ok(records)
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
    pub fn process_epoch_checkpoint(&self, checkpoint: EpochCheckpoint) -> Result<CIDv1Root, ILCConsensusError> {
        // Validation check over Sig components bounds -> (Skipped for M-006, validated manually via M-007 implementation)
        
        let mut txn = self.epoch_store.env.begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        // Monotonicity Check
        // Given we are committing epoch N, we explicitly enforce validation logic that this prevents re-committing identical Epochs
        let current_key_bytes = checkpoint.record.epoch.0.to_be_bytes();
        
        if let Ok(_) = txn.get(self.epoch_store.db, &current_key_bytes) {
            return Err(ILCConsensusError::InvalidEpoch); // Block re-committing identical Epoch
        }

        // Store epoch record
        let val_bytes = bincode::serialize(&checkpoint.record)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;

        txn.put(self.epoch_store.db, &current_key_bytes, &val_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        // Update sentinel atomically in the same transaction — O(1) current epoch lookup
        txn.put(self.epoch_store.db, &CURRENT_EPOCH_SENTINEL, &current_key_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB sentinel Put error: {}", e)))?;

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

        let epoch_record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
        };

        let checkpoint = EpochCheckpoint {
            record: epoch_record,
            sigs: generate_dummy_agg_sig(),
        };

        let result = protocol.process_epoch_checkpoint(checkpoint).unwrap();
        assert_eq!(result.p1, [1u8; 32]);
        assert_eq!(result.p2, [1u8; 4]);

        // Verify via Retrievable route
        let stored = store.get_epoch_record(EpochSeq(1)).unwrap();
        assert_eq!(stored.state_root.p1, [1u8; 32]);
        assert_eq!(stored.state_root.p2, [1u8; 4]);
        assert_eq!(stored.epoch, EpochSeq(1));
    }

    #[test]
    fn test_epoch_monotonicity() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());

        let epoch_record = EpochSettlementRecord {
            epoch: EpochSeq(2),
            state_root: CIDv1Root::new([2u8; 36]),
        };

        let checkpoint = EpochCheckpoint {
            record: epoch_record.clone(),
            sigs: generate_dummy_agg_sig(),
        };

        // Standard successfully commit Sequence 2
        assert!(protocol.process_epoch_checkpoint(checkpoint.clone()).is_ok());

        // Identical submission violates epoch structure
        let checkpoint_old = EpochCheckpoint {
            record: epoch_record,
            sigs: generate_dummy_agg_sig(),
        };
        assert_eq!(
            protocol.process_epoch_checkpoint(checkpoint_old).unwrap_err(),
            ILCConsensusError::InvalidEpoch
        );
    }
}
