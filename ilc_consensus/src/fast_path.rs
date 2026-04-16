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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{AgentID, ECUTransfer, ObjectRef, ValidatorID, ValidatorKey, ValidatorSig};
    use crate::balance_store::{AttributionBatch, EpochSeq};
    use blst::min_pk::SecretKey;
    use tempfile::tempdir;
    use lmdb_rkv::EnvironmentBuilder;

    fn generate_keypair(seed: u8) -> (SecretKey, ValidatorKey) {
        let ikm = [seed; 32];
        let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
        let pk = sk.sk_to_pk();
        (sk, ValidatorKey(pk))
    }

    fn setup_env() -> (Arc<lmdb_rkv::Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = EnvironmentBuilder::new()
            .set_max_dbs(1)
            .open(dir.path())
            .unwrap();
        (Arc::new(env), dir)
    }

    #[test]
    fn test_fast_path_quorum_verification() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let agent1 = AgentID([1; 32]);
        let agent2 = AgentID([2; 32]);

        store.apply_attribution(AttributionBatch {
            epoch: EpochSeq(1),
            attributions: vec![(agent1, 1_000_000)],
        }).unwrap();

        // N=4, F=1. Required=2f+1=3
        let (sk1, vk1) = generate_keypair(1);
        let (sk2, vk2) = generate_keypair(2);
        let (sk3, vk3) = generate_keypair(3);
        let (_sk4, vk4) = generate_keypair(4);

        let validators = vec![
            (ValidatorID(1), vk1),
            (ValidatorID(2), vk2),
            (ValidatorID(3), vk3),
            (ValidatorID(4), vk4),
        ];

        let val_set = Arc::new(ValidatorSet::new(validators, 1).unwrap());
        let fast_path = FastPathProtocol::new(val_set, store);

        let transfer = ECUTransfer {
            object_ref: ObjectRef { agent: agent1, version: 0 },
            to: agent2,
            amount_micro_ecu: 100_000,
        };

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = b"ILC_FAST_PATH_V1";

        let sig1 = ValidatorSig(sk1.sign(&msg, dst, &[]));
        let sig2 = ValidatorSig(sk2.sign(&msg, dst, &[]));
        let sig3 = ValidatorSig(sk3.sign(&msg, dst, &[]));

        // b. cert with fewer than 2f+1 sigs
        let cert_insufficient = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![(ValidatorID(1), sig1.clone()), (ValidatorID(2), sig2.clone())],
        };
        assert_eq!(fast_path.execute_certificate(cert_insufficient).unwrap_err(), ILCConsensusError::InsufficientSignatures);

        // c. cert with duplicate validator ID
        let cert_duplicate = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()), 
                (ValidatorID(2), sig2.clone()), 
                (ValidatorID(1), sig1.clone()) // Duplicate!
            ],
        };
        assert_eq!(fast_path.execute_certificate(cert_duplicate).unwrap_err(), ILCConsensusError::InvalidSignature);

        // d. cert with invalid signature
        let invalid_msg = b"tampered_payload";
        let invalid_sig = ValidatorSig(sk3.sign(invalid_msg, dst, &[]));
        let cert_invalid = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()), 
                (ValidatorID(2), sig2.clone()), 
                (ValidatorID(3), invalid_sig)
            ],
        };
        assert_eq!(fast_path.execute_certificate(cert_invalid).unwrap_err(), ILCConsensusError::InvalidSignature);

        // a. valid cert
        let cert_valid = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()), 
                (ValidatorID(2), sig2.clone()), 
                (ValidatorID(3), sig3.clone())
            ],
        };
        assert!(fast_path.execute_certificate(cert_valid).is_ok());
    }
}
