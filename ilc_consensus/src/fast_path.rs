use crate::types::{TransferCertificate, ILCConsensusError, ValidatorSet};
use crate::balance_store::{BalanceStore, BalanceChange};
use std::sync::Arc;
use std::collections::HashSet;
pub struct FastPathProtocol {
    validator_set: Arc<ValidatorSet>,
    balance_store: Arc<BalanceStore>,
    network_id: String,
}

impl FastPathProtocol {
    pub fn new(validator_set: Arc<ValidatorSet>, balance_store: Arc<BalanceStore>, network_id: String) -> Self {
        Self { validator_set, balance_store, network_id }
    }

    /// Primary Byzantine Consistent Broadcast gateway. 
    /// Verifies quorum boundaries directly against BLS cryptographic parameters.
    pub fn execute_certificate(&self, cert: TransferCertificate) -> Result<BalanceChange, ILCConsensusError> {
        // SEC-001: Verify sender authorization FIRST, before quorum check
        let sender_msg = bincode::serialize(&(&cert.transfer.object_ref, &cert.transfer.to, &cert.transfer.amount_micro_ecu))
            .map_err(|e| ILCConsensusError::Other(format!("Sender msg serialization failed: {}", e)))?;

        let sender_pubkey = blst::min_pk::PublicKey::from_bytes(&cert.transfer.object_ref.agent.0)
            .map_err(|_| ILCConsensusError::InvalidSignature)?;

        let verify_result = cert.transfer.sender_sig.0.verify(
            true, &sender_msg, crate::types::AGENT_TRANSFER_DST, &[], &sender_pubkey, true
        );
        if verify_result != blst::BLST_ERROR::BLST_SUCCESS {
            return Err(ILCConsensusError::InvalidSignature);
        }

        let required_votes = 2 * self.validator_set.f + 1;
        
        // 1. O(1) Quorum enforcement
        if cert.sigs.len() < required_votes {
            return Err(ILCConsensusError::InsufficientSignatures);
        }

        let mut seen_validators = HashSet::new();

        let msg = bincode::serialize(&cert.transfer)
            .map_err(|e| ILCConsensusError::Other(format!("Transfer serialization failed: {}", e)))?;
        // Domain separation tag dynamically parameterizing network authentication structures (SEC-002)
        let dst = crate::validator::validator_dst(&self.network_id); 
            
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
            let err = sig.0.verify(true, &msg, &dst, &[], &pub_key.0, true);
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
    use crate::types::{AgentID, ECUTransfer, ObjectRef, ValidatorID, ValidatorKey, ValidatorSig, AttributionBatch, EpochSeq, AgentSig};
    use blst::min_pk::SecretKey;

    fn generate_agent_keypair(seed: u8) -> (SecretKey, AgentID) {
        let ikm = [seed; 32];
        let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
        let pk = sk.sk_to_pk();
        (sk, AgentID(pk.to_bytes()))
    }
    use tempfile::tempdir;
    use lmdb_rkv::Environment;

    fn generate_keypair(seed: u8) -> (SecretKey, ValidatorKey) {
        let ikm = [seed; 32];
        let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
        let pk = sk.sk_to_pk();
        (sk, ValidatorKey(pk))
    }

    fn setup_env() -> (Arc<lmdb_rkv::Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Environment::new()
            .set_max_dbs(1)
            .open(dir.path())
            .unwrap();
        (Arc::new(env), dir)
    }

    #[test]
    fn test_fast_path_quorum_verification() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

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
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef { agent: agent1, version: 0 },
            to: agent2,
            amount_micro_ecu: 100_000,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let sender_msg = bincode::serialize(&(&transfer.object_ref, &transfer.to, &transfer.amount_micro_ecu)).unwrap();
        transfer.sender_sig = AgentSig(sk_agent1.sign(&sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = crate::validator::validator_dst("testnet");

        let sig1 = ValidatorSig(sk1.sign(&msg, &dst, &[]));
        let sig2 = ValidatorSig(sk2.sign(&msg, &dst, &[]));
        let sig3 = ValidatorSig(sk3.sign(&msg, &dst, &[]));

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
        let invalid_sig = ValidatorSig(sk3.sign(invalid_msg, &dst, &[]));
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

    #[test]
    fn test_byzantine_equivocation_safety() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);
        let (_, agent3) = generate_agent_keypair(33);

        store.apply_attribution(AttributionBatch {
            epoch: EpochSeq(1),
            attributions: vec![(agent1, 1_000_000)],
        }).unwrap();

        // N=4, F=1. Required=2f+1=3
        let (sk1, vk1) = generate_keypair(1); // Honest
        let (sk2, vk2) = generate_keypair(2); // Honest 
        let (sk3, vk3) = generate_keypair(3); // Honest
        let (sk4, vk4) = generate_keypair(4); // Byzantine

        let validators = vec![
            (ValidatorID(1), vk1),
            (ValidatorID(2), vk2),
            (ValidatorID(3), vk3),
            (ValidatorID(4), vk4),
        ];

        let val_set = Arc::new(ValidatorSet::new(validators, 1).unwrap());
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        // Two conflicting transfers originating from the same object version
        let mut transfer_alpha = ECUTransfer {
            object_ref: ObjectRef { agent: agent1, version: 0 },
            to: agent2,
            amount_micro_ecu: 400_000,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let alpha_sender_msg = bincode::serialize(&(&transfer_alpha.object_ref, &transfer_alpha.to, &transfer_alpha.amount_micro_ecu)).unwrap();
        transfer_alpha.sender_sig = AgentSig(sk_agent1.sign(&alpha_sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let mut transfer_beta = ECUTransfer {
            object_ref: ObjectRef { agent: agent1, version: 0 },
            to: agent3,
            amount_micro_ecu: 400_000,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let beta_sender_msg = bincode::serialize(&(&transfer_beta.object_ref, &transfer_beta.to, &transfer_beta.amount_micro_ecu)).unwrap();
        transfer_beta.sender_sig = AgentSig(sk_agent1.sign(&beta_sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg_alpha = bincode::serialize(&transfer_alpha).unwrap();
        let msg_beta = bincode::serialize(&transfer_beta).unwrap();
        let dst = crate::validator::validator_dst("testnet");

        // Validator 1, 2 see Alpha
        let sig1_alpha = ValidatorSig(sk1.sign(&msg_alpha, &dst, &[]));
        let sig2_alpha = ValidatorSig(sk2.sign(&msg_alpha, &dst, &[]));

        // Validator 3 sees Beta
        let sig3_beta = ValidatorSig(sk3.sign(&msg_beta, &dst, &[]));

        // Validator 4 (Byzantine) equivocates and signs both!
        let sig4_alpha = ValidatorSig(sk4.sign(&msg_alpha, &dst, &[]));
        let sig4_beta = ValidatorSig(sk4.sign(&msg_beta, &dst, &[]));

        // Alpha forms a valid cert (V1, V2, V4)
        let cert_alpha = TransferCertificate {
            transfer: transfer_alpha.clone(),
            sigs: vec![
                (ValidatorID(1), sig1_alpha),
                (ValidatorID(2), sig2_alpha),
                (ValidatorID(4), sig4_alpha), // Byzantine component
            ],
        };

        // For Beta to form a cert across the threshold (which theoretically shouldn't happen 
        // due to honest-node locking), we simulate a worst-case where another node maliciously 
        // or accidentally signs the conflicting transfer to verify our safety bounds.
        let sig2_beta = ValidatorSig(sk2.sign(&msg_beta, &dst, &[]));
        let cert_beta = TransferCertificate {
            transfer: transfer_beta.clone(),
            sigs: vec![
                (ValidatorID(3), sig3_beta),
                (ValidatorID(2), sig2_beta),
                (ValidatorID(4), sig4_beta), // Byzantine component explicitly equivocating
            ],
        };

        // Alpha commits to state safely
        assert!(fast_path.execute_certificate(cert_alpha).is_ok());

        // Beta crashes hard against the native Semantic firewall despite carrying 3 valid BLS signatures
        assert_eq!(
            fast_path.execute_certificate(cert_beta).unwrap_err(), 
            ILCConsensusError::ConflictingTransfer
        );
    }

    #[test]
    fn test_unsigned_transfer_rejected() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());
        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

        let (_, vk1) = generate_keypair(1);
        let val_set = Arc::new(ValidatorSet::new(vec![(ValidatorID(1), vk1)], 0).unwrap());
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef { agent: agent1, version: 0 },
            to: agent2,
            amount_micro_ecu: 100_000,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let bad_msg = b"tampered";
        transfer.sender_sig = AgentSig(sk_agent1.sign(bad_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let cert = TransferCertificate { transfer, sigs: vec![] };
        assert_eq!(fast_path.execute_certificate(cert).unwrap_err(), ILCConsensusError::InvalidSignature);
    }

    #[test]
    fn test_sender_sig_verified_before_quorum() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());
        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

        let (sk_val1, vk1) = generate_keypair(1);
        let val_set = Arc::new(ValidatorSet::new(vec![(ValidatorID(1), vk1)], 0).unwrap());
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef { agent: agent1, version: 0 },
            to: agent2,
            amount_micro_ecu: 100_000,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let bad_msg = b"tampered";
        transfer.sender_sig = AgentSig(sk_agent1.sign(bad_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = crate::validator::validator_dst("testnet");
        let sig1 = ValidatorSig(sk_val1.sign(&msg, &dst, &[]));

        let cert = TransferCertificate { transfer, sigs: vec![(ValidatorID(1), sig1)] };
        assert_eq!(fast_path.execute_certificate(cert).unwrap_err(), ILCConsensusError::InvalidSignature);
    }
}
