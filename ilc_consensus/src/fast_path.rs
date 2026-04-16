use crate::types::{TransferCertificate, ILCConsensusError, ValidatorSet};
use crate::balance_store::{BalanceStore, BalanceChange};
use std::sync::Arc;
use std::collections::HashSet;

pub struct FastPathProtocol {
    validator_set: Arc<ValidatorSet>,
    balance_store: Arc<BalanceStore>,
}

impl FastPathProtocol {
    pub fn new(validator_set: Arc<ValidatorSet>, balance_store: Arc<BalanceStore>) -> Self {
        Self { validator_set, balance_store }
    }

    /// Primary Byzantine Consistent Broadcast gateway. 
    /// Verifies quorum boundaries directly against BLS cryptographic parameters.
    pub fn execute_certificate(&self, cert: TransferCertificate) -> Result<BalanceChange, ILCConsensusError> {
        let required_votes = 2 * self.validator_set.f + 1;
        
        // 1. O(1) Quorum enforcement
        if cert.sigs.len() < required_votes {
            return Err(ILCConsensusError::InsufficientSignatures);
        }

        let mut seen_validators = HashSet::new();

        let msg = bincode::serialize(&cert.transfer)
            .map_err(|e| ILCConsensusError::Other(format!("Transfer serialization failed: {}", e)))?;
            
        // Domain separation tag binding the signature directly to ILC's Fast Path mechanism
        let dst = b"ILC_FAST_PATH_V1"; 

        // 2. Cryptographic constraint loop
        for (val_id, sig) in &cert.sigs {
            if !seen_validators.insert(val_id.0) {
                return Err(ILCConsensusError::InvalidSignature); // Stops Sybil duplication of signatures within the set
            }

            // O(N) internal router mapping ID -> PublicKey. (Could be optimized with HashMap)
            let pub_key = self.validator_set.validators.iter()
                .find(|(id, _)| id == val_id)
                .map(|(_, key)| key)
                .ok_or(ILCConsensusError::InvalidSignature)?;

            // Direct BLS point verification
            // true = hash_to_curve (standard for variable length messages)
            // msg = payload hash target
            // dst = Domain separation tag
            // aug = augmentation (none here)
            // pk = PublicKey
            // true = pairing optimization flag
            let err = sig.0.verify(true, &msg, dst, &[], &pub_key.0, true);
            if err != blst::BLST_ERROR::BLST_SUCCESS {
                return Err(ILCConsensusError::InvalidSignature);
            }
        }

        // 3. Delegate validated entity to safe LMDB atomic barrier
        self.balance_store.apply_transfer(cert)
    }
}
