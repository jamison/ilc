use bincode;
use lmdb_rkv::{Database, DatabaseFlags, Environment, Transaction, WriteFlags};
use std::collections::HashSet;
use std::sync::Arc;

use crate::types::{
    AgentID, AttributionBatch, ECUBalance, EpochSeq, ILCConsensusError, TransferCertificate,
};

const BACKWARD_ATTRIBUTION_BATCH_ROOT_KEY_PREFIX: &[u8] = b"backward_attr_root:";
const AGENT_REPUTATION_ROOT_KEY_PREFIX: &[u8] = b"agent_reputation_root:";
const ATTRIBUTION_EPOCH_COMMIT_KEY_PREFIX: &[u8] = b"attribution_epoch_commit:";

pub struct BalanceStore {
    env: Arc<Environment>,
    db: Database,
}

#[derive(Debug, Clone)]
pub struct BalanceChange {
    pub from_agent: AgentID,
    pub to_agent: AgentID,
    pub amount: u64,
}

impl BalanceStore {
    pub fn new(env: Arc<Environment>) -> Result<Self, ILCConsensusError> {
        let db = env
            .create_db(Some("ecu_balances"), DatabaseFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("Failed to create DB: {}", e)))?;
        Ok(Self { env, db })
    }

    pub fn get_balance(&self, agent_id: &AgentID) -> Result<ECUBalance, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;

        match txn.get(self.db, &agent_id.0) {
            Ok(bytes) => {
                let balance: ECUBalance = bincode::deserialize(bytes)
                    .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?;
                Ok(balance)
            }
            Err(lmdb_rkv::Error::NotFound) => {
                // If not found, they have 0 balance at version 0, epoch 0.
                Ok(ECUBalance {
                    agent: *agent_id,
                    amount_micro_ecu: 0,
                    epoch: EpochSeq(0),
                    version: 0,
                })
            }
            Err(e) => Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
    }

    pub fn get_backward_attribution_batch_root(
        &self,
        epoch: EpochSeq,
    ) -> Result<Option<[u8; 32]>, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let key = backward_attribution_batch_root_key(epoch);
        match txn.get(self.db, &key) {
            Ok(bytes) => {
                if bytes.len() != 32 {
                    return Err(ILCConsensusError::Other(
                        "stored backward attribution batch root has invalid length".to_string(),
                    ));
                }
                let mut root = [0u8; 32];
                root.copy_from_slice(bytes);
                Ok(Some(root))
            }
            Err(lmdb_rkv::Error::NotFound) => Ok(None),
            Err(e) => Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
    }

    pub fn get_agent_reputation_root(
        &self,
        epoch: EpochSeq,
    ) -> Result<Option<[u8; 32]>, ILCConsensusError> {
        let txn = self
            .env
            .begin_ro_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin txn: {}", e)))?;
        let key = agent_reputation_root_key(epoch);
        match txn.get(self.db, &key) {
            Ok(bytes) => {
                if bytes.len() != 32 {
                    return Err(ILCConsensusError::Other(
                        "stored agent reputation root has invalid length".to_string(),
                    ));
                }
                let mut root = [0u8; 32];
                root.copy_from_slice(bytes);
                Ok(Some(root))
            }
            Err(lmdb_rkv::Error::NotFound) => Ok(None),
            Err(e) => Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
    }

    pub fn store_backward_attribution_batch_root(
        &self,
        epoch: EpochSeq,
        root: [u8; 32],
    ) -> Result<(), ILCConsensusError> {
        let mut txn = self
            .env
            .begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;
        let key = backward_attribution_batch_root_key(epoch);
        match txn.get(self.db, &key) {
            Ok(existing) => {
                if existing == root {
                    drop(txn);
                    return Ok(());
                }
                return Err(ILCConsensusError::Other(
                    "backward_attribution_batch_root_conflict_phase_1594".to_string(),
                ));
            }
            Err(lmdb_rkv::Error::NotFound) => {}
            Err(e) => return Err(ILCConsensusError::Other(format!("LMDB get error: {}", e))),
        }
        txn.put(self.db, &key, &root.to_vec(), WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;
        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;
        Ok(())
    }

    /// Primary execution boundary for the Byzantine Consistent Broadcast fast-path.
    /// Locks on `cert.transfer.object_ref` to enforce SafetyNoDualCert.
    /// Note: Assumes `cert` signatures have already been aggregated and checked
    /// by the fast-path network logic (handled in M-004).
    pub fn apply_transfer(
        &self,
        cert: TransferCertificate,
    ) -> Result<BalanceChange, ILCConsensusError> {
        // Enforce anti-inflation logic preventing single-address overwrite bugs
        if cert.transfer.object_ref.agent == cert.transfer.to {
            return Err(ILCConsensusError::SelfTransfer);
        }

        // Zero-amount transfers are prohibited: they burn a version slot without moving value,
        // enabling a targeted DoS that exhausts an agent's ObjectRef version space.
        if cert.transfer.amount_micro_ecu == 0 {
            return Err(ILCConsensusError::Other(
                "zero-amount transfer prohibited".to_string(),
            ));
        }

        let mut txn = self
            .env
            .begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        let sender_id = &cert.transfer.object_ref.agent;
        let recipient_id = &cert.transfer.to;
        let amount = cert.transfer.amount_micro_ecu;
        let version_attempt = cert.transfer.object_ref.version;

        // 1. Fetch current sender balance object
        let mut sender_bal = match txn.get(self.db, &sender_id.0) {
            Ok(bytes) => bincode::deserialize::<ECUBalance>(bytes)
                .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?,
            Err(lmdb_rkv::Error::NotFound) => return Err(ILCConsensusError::BalanceInsufficient),
            Err(e) => return Err(ILCConsensusError::Other(format!("DB Error: {}", e))),
        };

        // 2. ATOMIC LOCK CHECK: The attempted version must match the current state version precisely.
        // Any deviation triggers a ConflictingTransfer intercept.
        if sender_bal.version != version_attempt {
            return Err(ILCConsensusError::ConflictingTransfer);
        }

        // 3. Balance verification
        if sender_bal.amount_micro_ecu < amount {
            return Err(ILCConsensusError::BalanceInsufficient);
        }
        if cert.epoch < sender_bal.epoch {
            return Err(ILCConsensusError::InvalidEpoch);
        }

        // 4. Fetch recipient balance object
        let mut recipient_bal = match txn.get(self.db, &recipient_id.0) {
            Ok(bytes) => bincode::deserialize::<ECUBalance>(bytes)
                .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?,
            Err(lmdb_rkv::Error::NotFound) => ECUBalance {
                agent: *recipient_id,
                amount_micro_ecu: 0,
                epoch: cert.epoch,
                version: 0,
            },
            Err(e) => return Err(ILCConsensusError::Other(format!("DB Error: {}", e))),
        };

        // 5. Apply transitions
        sender_bal.amount_micro_ecu = sender_bal
            .amount_micro_ecu
            .checked_sub(amount)
            .ok_or(ILCConsensusError::BalanceInsufficient)?;
        sender_bal.version = sender_bal
            .version
            .checked_add(1)
            .ok_or(ILCConsensusError::Other(
                "ObjectRef version overflow".to_string(),
            ))?;
        sender_bal.epoch = cert.epoch;

        recipient_bal.amount_micro_ecu = recipient_bal
            .amount_micro_ecu
            .checked_add(amount)
            .ok_or(ILCConsensusError::Other("ECU amount overflow".to_string()))?;
        if cert.epoch > recipient_bal.epoch {
            recipient_bal.epoch = cert.epoch;
        }
        // Notice: Recipient version does not increment here because the transfer lock is purely on the sender's owned-object.

        // 6. Write back safely bound within the single `txn`
        let s_bytes = bincode::serialize(&sender_bal)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;
        let r_bytes = bincode::serialize(&recipient_bal)
            .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;

        txn.put(self.db, &sender_id.0, &s_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;
        txn.put(self.db, &recipient_id.0, &r_bytes, WriteFlags::empty())
            .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        // 7. Commit
        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;

        Ok(BalanceChange {
            from_agent: *sender_id,
            to_agent: *recipient_id,
            amount,
        })
    }

    /// Epoch-boundary global reconciliation where identical attribution rules are universally applied.
    pub fn apply_attribution(&self, batch: AttributionBatch) -> Result<(), ILCConsensusError> {
        // Reject batches with duplicate AgentIDs. The current loop would otherwise
        // sum duplicate entries, but each batch must contain one canonical row per
        // recipient AgentID to keep attribution evidence unambiguous.
        let mut seen = HashSet::new();
        for (agent_id, _) in &batch.attributions {
            if !seen.insert(agent_id.0) {
                return Err(ILCConsensusError::Other(format!(
                    "duplicate AgentID in AttributionBatch: {:?}",
                    agent_id
                )));
            }
        }

        let mut txn = self
            .env
            .begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        let epoch_commit_key = attribution_epoch_commit_key(batch.epoch);
        match txn.get(self.db, &epoch_commit_key) {
            Ok(_) => return Err(ILCConsensusError::InvalidEpoch),
            Err(lmdb_rkv::Error::NotFound) => {}
            Err(e) => return Err(ILCConsensusError::Other(format!("DB Error: {}", e))),
        }

        for (agent_id, amount) in batch.attributions {
            let (mut agent_bal, is_new) = match txn.get(self.db, &agent_id.0) {
                Ok(bytes) => (
                    bincode::deserialize::<ECUBalance>(bytes).map_err(|e| {
                        ILCConsensusError::Other(format!("Deserialize error: {}", e))
                    })?,
                    false,
                ),
                Err(lmdb_rkv::Error::NotFound) => (
                    ECUBalance {
                        agent: agent_id,
                        amount_micro_ecu: 0,
                        epoch: batch.epoch,
                        version: 0,
                    },
                    true,
                ),
                Err(e) => return Err(ILCConsensusError::Other(format!("DB Error: {}", e))),
            };

            // Replay guard: reject older-epoch attribution for existing agents.
            // Same-epoch attribution is valid when an agent first received a transfer in
            // that epoch. Replay of an attribution batch for the same epoch is prevented
            // above by the epoch commit marker, before any per-agent mutation occurs.
            // New agents are exempt: they have no prior epoch record and their initial
            // epoch field is set to batch.epoch as part of construction above.
            if !is_new && batch.epoch.0 < agent_bal.epoch.0 {
                return Err(ILCConsensusError::InvalidEpoch);
            }

            agent_bal.amount_micro_ecu = agent_bal
                .amount_micro_ecu
                .checked_add(amount)
                .ok_or(ILCConsensusError::Other("ECU amount overflow".to_string()))?;
            agent_bal.epoch = batch.epoch;

            let arr = bincode::serialize(&agent_bal)
                .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;
            txn.put(self.db, &agent_id.0, &arr, WriteFlags::empty())
                .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;
        }

        if let Some(root) = batch.backward_attribution_batch_root {
            let key = backward_attribution_batch_root_key(batch.epoch);
            let root_bytes = root.to_vec();
            txn.put(self.db, &key, &root_bytes, WriteFlags::empty())
                .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;
        }
        if let Some(root) = batch.agent_reputation_root {
            let key = agent_reputation_root_key(batch.epoch);
            let root_bytes = root.to_vec();
            txn.put(self.db, &key, &root_bytes, WriteFlags::empty())
                .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;
        }
        txn.put(
            self.db,
            &epoch_commit_key,
            b"committed_attribution_epoch_v1",
            WriteFlags::empty(),
        )
        .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;

        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;

        Ok(())
    }
}

fn backward_attribution_batch_root_key(epoch: EpochSeq) -> Vec<u8> {
    let mut key = Vec::with_capacity(
        BACKWARD_ATTRIBUTION_BATCH_ROOT_KEY_PREFIX.len() + std::mem::size_of::<u64>(),
    );
    key.extend_from_slice(BACKWARD_ATTRIBUTION_BATCH_ROOT_KEY_PREFIX);
    key.extend_from_slice(&epoch.0.to_be_bytes());
    key
}

fn agent_reputation_root_key(epoch: EpochSeq) -> Vec<u8> {
    let mut key =
        Vec::with_capacity(AGENT_REPUTATION_ROOT_KEY_PREFIX.len() + std::mem::size_of::<u64>());
    key.extend_from_slice(AGENT_REPUTATION_ROOT_KEY_PREFIX);
    key.extend_from_slice(&epoch.0.to_be_bytes());
    key
}

fn attribution_epoch_commit_key(epoch: EpochSeq) -> Vec<u8> {
    let mut key =
        Vec::with_capacity(ATTRIBUTION_EPOCH_COMMIT_KEY_PREFIX.len() + std::mem::size_of::<u64>());
    key.extend_from_slice(ATTRIBUTION_EPOCH_COMMIT_KEY_PREFIX);
    key.extend_from_slice(&epoch.0.to_be_bytes());
    key
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{AgentSig, ECUTransfer, ObjectRef};
    use blst::min_pk::SecretKey;
    use tempfile::tempdir;

    fn dummy_agent_sig() -> AgentSig {
        let ikm = [42u8; 32];
        let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
        AgentSig(sk.sign(b"dummy", crate::types::AGENT_TRANSFER_DST, &[]))
    }

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Environment::new().set_max_dbs(1).open(dir.path()).unwrap();
        (Arc::new(env), dir)
    }

    #[test]
    fn test_apply_transfer_atomicity_and_conflicts() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();

        let agent1 = AgentID([1; 48]);
        let agent2 = AgentID([2; 48]);

        // Inject initial attribution
        let batch = AttributionBatch {
            epoch: EpochSeq(1),
            attributions: vec![(agent1, 1_000_000)], // 1 ECU
            backward_attribution_batch_root: None,
            agent_reputation_root: None,
        };
        store.apply_attribution(batch).unwrap();

        // Valid transfer
        let cert1 = TransferCertificate {
            transfer: ECUTransfer {
                object_ref: ObjectRef {
                    agent: agent1,
                    version: 0,
                },
                to: agent2,
                amount_micro_ecu: 400_000,
                transfer_class: crate::types::TransferClass::Contribution,
                sender_sig: dummy_agent_sig(),
            },
            sigs: Vec::new(),
            epoch: EpochSeq(1),
        };

        store.apply_transfer(cert1.clone()).unwrap();

        let bal1 = store.get_balance(&agent1).unwrap();
        assert_eq!(bal1.amount_micro_ecu, 600_000);
        assert_eq!(bal1.version, 1);

        // Try applying same transfer again (Replay violation)
        let res = store.apply_transfer(cert1);
        assert_eq!(res.unwrap_err(), ILCConsensusError::ConflictingTransfer);

        // Try conflicting transfer with identical valid struct but wrong nonce
        let cert2 = TransferCertificate {
            transfer: ECUTransfer {
                object_ref: ObjectRef {
                    agent: agent1,
                    version: 0,
                }, // Using outdated version 0
                to: agent2,
                amount_micro_ecu: 100_000,
                transfer_class: crate::types::TransferClass::Contribution,
                sender_sig: dummy_agent_sig(),
            },
            sigs: Vec::new(),
            epoch: EpochSeq(1),
        };
        let res2 = store.apply_transfer(cert2);
        assert_eq!(res2.unwrap_err(), ILCConsensusError::ConflictingTransfer);
    }

    #[test]
    fn test_apply_transfer_uses_certificate_epoch_for_mutated_balances() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();

        let agent1 = AgentID([3; 48]);
        let agent2 = AgentID([4; 48]);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent1, 1_000_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let cert = TransferCertificate {
            transfer: ECUTransfer {
                object_ref: ObjectRef {
                    agent: agent1,
                    version: 0,
                },
                to: agent2,
                amount_micro_ecu: 400_000,
                transfer_class: crate::types::TransferClass::Contribution,
                sender_sig: dummy_agent_sig(),
            },
            sigs: Vec::new(),
            epoch: EpochSeq(2),
        };

        store.apply_transfer(cert).unwrap();

        assert_eq!(store.get_balance(&agent1).unwrap().epoch, EpochSeq(2));
        assert_eq!(store.get_balance(&agent2).unwrap().epoch, EpochSeq(2));
    }

    #[test]
    fn test_apply_attribution_allows_same_epoch_after_transfer() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();

        let agent1 = AgentID([21; 48]);
        let agent2 = AgentID([22; 48]);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent1, 1_000_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let cert = TransferCertificate {
            transfer: ECUTransfer {
                object_ref: ObjectRef {
                    agent: agent1,
                    version: 0,
                },
                to: agent2,
                amount_micro_ecu: 400_000,
                transfer_class: crate::types::TransferClass::Contribution,
                sender_sig: dummy_agent_sig(),
            },
            sigs: Vec::new(),
            epoch: EpochSeq(2),
        };
        store.apply_transfer(cert).unwrap();

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(2),
                attributions: vec![(agent2, 200_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let bal = store.get_balance(&agent2).unwrap();
        assert_eq!(bal.amount_micro_ecu, 600_000);
        assert_eq!(bal.epoch, EpochSeq(2));
    }

    #[test]
    fn test_apply_transfer_rejects_stale_certificate_epoch() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();

        let agent1 = AgentID([5; 48]);
        let agent2 = AgentID([6; 48]);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(5),
                attributions: vec![(agent1, 1_000_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let cert = TransferCertificate {
            transfer: ECUTransfer {
                object_ref: ObjectRef {
                    agent: agent1,
                    version: 0,
                },
                to: agent2,
                amount_micro_ecu: 400_000,
                transfer_class: crate::types::TransferClass::Contribution,
                sender_sig: dummy_agent_sig(),
            },
            sigs: Vec::new(),
            epoch: EpochSeq(4),
        };

        assert_eq!(
            store.apply_transfer(cert).unwrap_err(),
            ILCConsensusError::InvalidEpoch
        );
    }

    // SEC-FIX-02: apply_attribution same-epoch replay must not double-mint
    #[test]
    fn test_apply_attribution_same_epoch_replay_rejected() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent = AgentID([7; 48]);

        let batch = AttributionBatch {
            epoch: EpochSeq(5),
            attributions: vec![(agent, 500_000)],
            backward_attribution_batch_root: None,
            agent_reputation_root: None,
        };
        // First application: succeeds and sets epoch=5 for this agent.
        store.apply_attribution(batch.clone()).unwrap();
        let bal = store.get_balance(&agent).unwrap();
        assert_eq!(bal.amount_micro_ecu, 500_000);

        // Replay of same epoch: must be rejected (would double-mint without <=).
        let err = store.apply_attribution(batch).unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::InvalidEpoch,
            "same-epoch replay must return InvalidEpoch to prevent double-minting"
        );

        // Balance unchanged after rejected replay.
        let bal_after = store.get_balance(&agent).unwrap();
        assert_eq!(
            bal_after.amount_micro_ecu, 500_000,
            "balance must not change after replay"
        );
    }

    #[test]
    fn test_apply_attribution_same_epoch_disjoint_agent_rejected() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent1 = AgentID([17; 48]);
        let agent2 = AgentID([18; 48]);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(21),
                attributions: vec![(agent1, 500_000)],
                backward_attribution_batch_root: Some([1u8; 32]),
                agent_reputation_root: Some([2u8; 32]),
            })
            .unwrap();

        let err = store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(21),
                attributions: vec![(agent2, 700_000)],
                backward_attribution_batch_root: Some([3u8; 32]),
                agent_reputation_root: Some([4u8; 32]),
            })
            .unwrap_err();

        assert_eq!(err, ILCConsensusError::InvalidEpoch);
        assert_eq!(store.get_balance(&agent2).unwrap().amount_micro_ecu, 0);
        assert_eq!(
            store
                .get_backward_attribution_batch_root(EpochSeq(21))
                .unwrap(),
            Some([1u8; 32])
        );
        assert_eq!(
            store.get_agent_reputation_root(EpochSeq(21)).unwrap(),
            Some([2u8; 32])
        );
    }

    #[test]
    fn test_apply_attribution_root_bearing_batch_after_rootless_epoch_rejected() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent1 = AgentID([19; 48]);
        let agent2 = AgentID([20; 48]);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(22),
                attributions: vec![(agent1, 500_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let err = store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(22),
                attributions: vec![(agent2, 700_000)],
                backward_attribution_batch_root: Some([5u8; 32]),
                agent_reputation_root: Some([6u8; 32]),
            })
            .unwrap_err();

        assert_eq!(err, ILCConsensusError::InvalidEpoch);
        assert_eq!(store.get_balance(&agent2).unwrap().amount_micro_ecu, 0);
        assert_eq!(
            store
                .get_backward_attribution_batch_root(EpochSeq(22))
                .unwrap(),
            None
        );
        assert_eq!(store.get_agent_reputation_root(EpochSeq(22)).unwrap(), None);
    }

    // SEC-FIX-02: new agents in epoch 0 must be attributable on first call
    #[test]
    fn test_apply_attribution_new_agent_first_call_succeeds() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent = AgentID([8; 48]);

        // New agent, epoch 0 — must succeed even though initialization sets epoch=0.
        let batch = AttributionBatch {
            epoch: EpochSeq(0),
            attributions: vec![(agent, 100_000)],
            backward_attribution_batch_root: None,
            agent_reputation_root: None,
        };
        store.apply_attribution(batch).unwrap();
        let bal = store.get_balance(&agent).unwrap();
        assert_eq!(bal.amount_micro_ecu, 100_000);
    }

    // SEC-FIX-02: old-epoch batch must still be rejected
    #[test]
    fn test_apply_attribution_old_epoch_rejected() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent = AgentID([9; 48]);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(10),
                attributions: vec![(agent, 200_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let err = store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(9),
                attributions: vec![(agent, 999_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::InvalidEpoch,
            "older-epoch batch must be rejected"
        );
    }

    #[test]
    fn test_apply_attribution_stores_backward_attribution_batch_root() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent = AgentID([10; 48]);
        let root = [42u8; 32];

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(11),
                attributions: vec![(agent, 321_000)],
                backward_attribution_batch_root: Some(root),
                agent_reputation_root: None,
            })
            .unwrap();

        assert_eq!(
            store
                .get_backward_attribution_batch_root(EpochSeq(11))
                .unwrap(),
            Some(root)
        );
        assert_eq!(
            store
                .get_backward_attribution_batch_root(EpochSeq(12))
                .unwrap(),
            None
        );
    }

    #[test]
    fn test_apply_attribution_stores_agent_reputation_root() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();
        let agent = AgentID([11; 48]);
        let root = [77u8; 32];

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(13),
                attributions: vec![(agent, 654_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: Some(root),
            })
            .unwrap();

        assert_eq!(
            store.get_agent_reputation_root(EpochSeq(13)).unwrap(),
            Some(root)
        );
        assert_eq!(store.get_agent_reputation_root(EpochSeq(14)).unwrap(), None);
    }
}
