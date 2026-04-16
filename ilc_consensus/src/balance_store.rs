use lmdb_rkv::{Environment, Database, DatabaseFlags, Transaction, WriteFlags};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use bincode;

use crate::types::{AgentID, ECUBalance, TransferCertificate, ILCConsensusError, AttributionBatch, EpochSeq};

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
        let txn = self.env.begin_ro_txn()
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

    /// Primary execution boundary for the Byzantine Consistent Broadcast fast-path.
    /// Locks on `cert.transfer.object_ref` to enforce SafetyNoDualCert.
    /// Note: Assumes `cert` signatures have already been aggregated and checked
    /// by the fast-path network logic (handled in M-004).
    pub fn apply_transfer(&self, cert: TransferCertificate) -> Result<BalanceChange, ILCConsensusError> {
        // Enforce anti-inflation logic preventing single-address overwrite bugs
        if cert.transfer.object_ref.agent == cert.transfer.to {
            return Err(ILCConsensusError::SelfTransfer);
        }

        let mut txn = self.env.begin_rw_txn()
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

        // 4. Fetch recipient balance object
        let mut recipient_bal = match txn.get(self.db, &recipient_id.0) {
            Ok(bytes) => bincode::deserialize::<ECUBalance>(bytes)
                .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?,
            Err(lmdb_rkv::Error::NotFound) => ECUBalance {
                agent: *recipient_id,
                amount_micro_ecu: 0,
                epoch: sender_bal.epoch, 
                version: 0,
            },
            Err(e) => return Err(ILCConsensusError::Other(format!("DB Error: {}", e))),
        };

        // 5. Apply transitions
        sender_bal.amount_micro_ecu = sender_bal.amount_micro_ecu
            .checked_sub(amount)
            .ok_or(ILCConsensusError::BalanceInsufficient)?;
        sender_bal.version += 1; // Explicit monotonic progression protecting against replay and dual-certs

        recipient_bal.amount_micro_ecu = recipient_bal.amount_micro_ecu
            .checked_add(amount)
            .ok_or(ILCConsensusError::Other("ECU amount overflow".to_string()))?;
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
        let mut txn = self.env.begin_rw_txn()
            .map_err(|e| ILCConsensusError::Other(format!("Failed to begin RW txn: {}", e)))?;

        for (agent_id, amount) in batch.attributions {
            let mut agent_bal = match txn.get(self.db, &agent_id.0) {
                Ok(bytes) => bincode::deserialize::<ECUBalance>(bytes)
                    .map_err(|e| ILCConsensusError::Other(format!("Deserialize error: {}", e)))?,
                Err(lmdb_rkv::Error::NotFound) => ECUBalance {
                    agent: agent_id,
                    amount_micro_ecu: 0,
                    epoch: batch.epoch,
                    version: 0,
                },
                Err(e) => return Err(ILCConsensusError::Other(format!("DB Error: {}", e))),
            };

            if batch.epoch.0 < agent_bal.epoch.0 {
                return Err(ILCConsensusError::InvalidEpoch);
            }
            
            agent_bal.amount_micro_ecu = agent_bal.amount_micro_ecu
                .checked_add(amount)
                .ok_or(ILCConsensusError::Other("ECU amount overflow".to_string()))?;
            agent_bal.epoch = batch.epoch;

            let arr = bincode::serialize(&agent_bal)
                .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;
            txn.put(self.db, &agent_id.0, &arr, WriteFlags::empty())
                .map_err(|e| ILCConsensusError::Other(format!("LMDB Put error: {}", e)))?;
        }

        txn.commit()
            .map_err(|e| ILCConsensusError::Other(format!("Txn Commit error: {}", e)))?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use lmdb_rkv::{EnvironmentBuilder};
    use crate::types::{ECUTransfer, ObjectRef};

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = EnvironmentBuilder::new()
            .set_max_dbs(1)
            .open(dir.path())
            .unwrap();
        (Arc::new(env), dir)
    }

    #[test]
    fn test_apply_transfer_atomicity_and_conflicts() {
        let (env, _dir) = setup_env();
        let store = BalanceStore::new(env).unwrap();

        let agent1 = AgentID([1; 32]);
        let agent2 = AgentID([2; 32]);

        // Inject initial attribution
        let batch = AttributionBatch {
            epoch: EpochSeq(1),
            attributions: vec![(agent1, 1_000_000)], // 1 ECU
        };
        store.apply_attribution(batch).unwrap();

        // Valid transfer
        let cert1 = TransferCertificate {
            transfer: ECUTransfer {
                object_ref: ObjectRef { agent: agent1, version: 0 },
                to: agent2,
                amount_micro_ecu: 400_000,
            },
            sigs: Vec::new(),
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
                object_ref: ObjectRef { agent: agent1, version: 0 }, // Using outdated version 0
                to: agent2,
                amount_micro_ecu: 100_000,
            },
            sigs: Vec::new(),
        };
        let res2 = store.apply_transfer(cert2);
        assert_eq!(res2.unwrap_err(), ILCConsensusError::ConflictingTransfer);
    }
}
