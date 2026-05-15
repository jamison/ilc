use crate::balance_store::{BalanceChange, BalanceStore};
use crate::types::{EpochSeq, ILCConsensusError, TransferCertificate, ValidatorSet};
use std::collections::{BTreeMap, HashSet};
use std::sync::{Arc, RwLock};

pub const SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_PHASE_1353: &str =
    "sec_004_transfer_certificate_epoch_binding_phase_1353";
pub const VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_PHASE_1353: &str =
    "validator_set_rotation_wired_fast_path_phase_1353";

pub struct FastPathProtocol {
    /// Current validator set view, kept for existing epoch-settlement / harness compatibility.
    pub validator_set: Arc<RwLock<ValidatorSet>>,
    /// SEC-004: historical validator-set snapshots keyed by the epoch they become active.
    epoch_sets: Arc<RwLock<BTreeMap<EpochSeq, ValidatorSet>>>,
    balance_store: Arc<BalanceStore>,
    network_id: String,
}

impl FastPathProtocol {
    pub fn new(
        validator_set: ValidatorSet,
        balance_store: Arc<BalanceStore>,
        network_id: String,
    ) -> Self {
        let mut epoch_sets = BTreeMap::new();
        epoch_sets.insert(EpochSeq(0), validator_set.clone());
        Self {
            validator_set: Arc::new(RwLock::new(validator_set)),
            epoch_sets: Arc::new(RwLock::new(epoch_sets)),
            balance_store,
            network_id,
        }
    }

    /// SEC-004: Record the validator set that becomes active at `active_from_epoch`
    /// and update the current-set compatibility view.
    ///
    /// Monotonicity guard: if `active_from_epoch` is less than or equal to the
    /// latest recorded activation epoch, the call is a no-op (logged).  This
    /// prevents a stale or replayed governance action from overwriting a newer set.
    ///
    /// Phase 1353 binds this callable rotation surface to CDL-017 admission/ejection
    /// decisions. Production validator admission remains behind a separate operator
    /// human gate; this method records deterministic epoch-bound rotations once a
    /// caller supplies an authorized `ValidatorSet`.
    pub fn rotate_validator_set(&self, active_from_epoch: EpochSeq, new_set: ValidatorSet) {
        let mut sets = self.epoch_sets.write().unwrap();
        if let Some((&latest_epoch, _)) = sets.iter().next_back() {
            if active_from_epoch <= latest_epoch {
                eprintln!(
                    "[sec_004] rotate_validator_set: active_from_epoch={} <= latest={} — skipping stale rotation",
                    active_from_epoch.0, latest_epoch.0
                );
                return;
            }
        }
        sets.insert(active_from_epoch, new_set.clone());
        // BUG-003: update validator_set while still holding the epoch_sets write lock
        // to eliminate the staleness window between the two stores.  Lock ordering is
        // always epoch_sets → validator_set; no other path acquires validator_set write
        // while reading epoch_sets, so this order is consistent and deadlock-free.
        *self.validator_set.write().unwrap() = new_set;
        // epoch_sets write lock releases here when `sets` drops.
    }

    /// Primary Byzantine Consistent Broadcast gateway.
    /// Verifies quorum boundaries directly against BLS cryptographic parameters.
    pub fn execute_certificate(
        &self,
        cert: TransferCertificate,
    ) -> Result<BalanceChange, ILCConsensusError> {
        // SEC-001: Verify sender authorization FIRST, before quorum check
        let sender_msg = bincode::serialize(&(
            &cert.transfer.object_ref,
            &cert.transfer.to,
            &cert.transfer.amount_micro_ecu,
            &cert.transfer.transfer_class,
        ))
        .map_err(|e| ILCConsensusError::Other(format!("Sender msg serialization failed: {}", e)))?;

        let sender_pubkey = blst::min_pk::PublicKey::from_bytes(&cert.transfer.object_ref.agent.0)
            .map_err(|_| ILCConsensusError::InvalidSignature)?;
        // SEC-FIX-01: G1 subgroup check — from_bytes skips cofactor membership; validate enforces it.
        sender_pubkey
            .validate()
            .map_err(|_| ILCConsensusError::InvalidSignature)?;

        let verify_result = cert.transfer.sender_sig.0.verify(
            true,
            &sender_msg,
            crate::types::AGENT_TRANSFER_DST,
            &[],
            &sender_pubkey,
            true,
        );
        if verify_result != blst::BLST_ERROR::BLST_SUCCESS {
            return Err(ILCConsensusError::InvalidSignature);
        }

        // SEC-004: resolve the historical ValidatorSet active when this cert was assembled.
        // The largest active_from_epoch <= cert.epoch is the governing set.
        let sets = self.epoch_sets.read().unwrap();
        let vs = sets
            .range(..=cert.epoch)
            .next_back()
            .map(|(_, vs)| vs)
            .ok_or(ILCConsensusError::InvalidEpoch)?;

        let required_votes = 2 * vs.f + 1;

        // 1. O(1) Quorum enforcement
        if cert.sigs.len() < required_votes {
            return Err(ILCConsensusError::InsufficientSignatures);
        }

        let mut seen_validators = HashSet::new();

        let msg = bincode::serialize(&cert.transfer).map_err(|e| {
            ILCConsensusError::Other(format!("Transfer serialization failed: {}", e))
        })?;
        // Domain separation tag dynamically parameterizing network authentication structures (SEC-002)
        let dst = crate::validator::validator_dst(&self.network_id);

        // 2. Cryptographic constraint loop
        for (val_id, sig) in &cert.sigs {
            if !seen_validators.insert(val_id.0) {
                return Err(ILCConsensusError::InvalidSignature); // Stops Sybil duplication of signatures within the set
            }

            // SEC-004: validator not in the cert's historical set → InvalidSignature.
            // O(1) HashMap lookup replaces the prior O(n) linear scan.
            let pub_key = vs
                .validators
                .get(val_id)
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
    use crate::types::{
        AgentID, AgentSig, AttributionBatch, ECUTransfer, EpochSeq, ObjectRef, TransferClass,
        ValidatorID, ValidatorKey, ValidatorSig,
    };
    use blst::min_pk::SecretKey;

    fn generate_agent_keypair(seed: u8) -> (SecretKey, AgentID) {
        let ikm = [seed; 32];
        let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
        let pk = sk.sk_to_pk();
        (sk, AgentID(pk.to_bytes()))
    }
    use lmdb_rkv::Environment;
    use tempfile::tempdir;

    fn generate_keypair(seed: u8) -> (SecretKey, ValidatorKey) {
        let ikm = [seed; 32];
        let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
        let pk = sk.sk_to_pk();
        (sk, ValidatorKey(pk))
    }

    fn setup_env() -> (Arc<lmdb_rkv::Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Environment::new().set_max_dbs(1).open(dir.path()).unwrap();
        (Arc::new(env), dir)
    }

    #[test]
    fn test_phase_1353_sec_004_binding_tokens_present() {
        assert_eq!(
            SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_PHASE_1353,
            "sec_004_transfer_certificate_epoch_binding_phase_1353"
        );
        assert_eq!(
            VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_PHASE_1353,
            "validator_set_rotation_wired_fast_path_phase_1353"
        );
    }

    #[test]
    fn test_fast_path_quorum_verification() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent1, 1_000_000)],
            })
            .unwrap();

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

        let val_set = ValidatorSet::new(validators, 1).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef {
                agent: agent1,
                version: 0,
            },
            to: agent2,
            amount_micro_ecu: 100_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let sender_msg = bincode::serialize(&(
            &transfer.object_ref,
            &transfer.to,
            &transfer.amount_micro_ecu,
            &transfer.transfer_class,
        ))
        .unwrap();
        transfer.sender_sig =
            AgentSig(sk_agent1.sign(&sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = crate::validator::validator_dst("testnet");

        let sig1 = ValidatorSig(sk1.sign(&msg, &dst, &[]));
        let sig2 = ValidatorSig(sk2.sign(&msg, &dst, &[]));
        let sig3 = ValidatorSig(sk3.sign(&msg, &dst, &[]));

        // b. cert with fewer than 2f+1 sigs
        let cert_insufficient = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()),
                (ValidatorID(2), sig2.clone()),
            ],
            epoch: EpochSeq(1),
        };
        assert_eq!(
            fast_path
                .execute_certificate(cert_insufficient)
                .unwrap_err(),
            ILCConsensusError::InsufficientSignatures
        );

        // c. cert with duplicate validator ID
        let cert_duplicate = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()),
                (ValidatorID(2), sig2.clone()),
                (ValidatorID(1), sig1.clone()), // Duplicate!
            ],
            epoch: EpochSeq(1),
        };
        assert_eq!(
            fast_path.execute_certificate(cert_duplicate).unwrap_err(),
            ILCConsensusError::InvalidSignature
        );

        // d. cert with invalid signature
        let invalid_msg = b"tampered_payload";
        let invalid_sig = ValidatorSig(sk3.sign(invalid_msg, &dst, &[]));
        let cert_invalid = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()),
                (ValidatorID(2), sig2.clone()),
                (ValidatorID(3), invalid_sig),
            ],
            epoch: EpochSeq(1),
        };
        assert_eq!(
            fast_path.execute_certificate(cert_invalid).unwrap_err(),
            ILCConsensusError::InvalidSignature
        );

        // a. valid cert
        let cert_valid = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (ValidatorID(1), sig1.clone()),
                (ValidatorID(2), sig2.clone()),
                (ValidatorID(3), sig3.clone()),
            ],
            epoch: EpochSeq(1),
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

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent1, 1_000_000)],
            })
            .unwrap();

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

        let val_set = ValidatorSet::new(validators, 1).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        // Two conflicting transfers originating from the same object version
        let mut transfer_alpha = ECUTransfer {
            object_ref: ObjectRef {
                agent: agent1,
                version: 0,
            },
            to: agent2,
            amount_micro_ecu: 400_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let alpha_sender_msg = bincode::serialize(&(
            &transfer_alpha.object_ref,
            &transfer_alpha.to,
            &transfer_alpha.amount_micro_ecu,
            &transfer_alpha.transfer_class,
        ))
        .unwrap();
        transfer_alpha.sender_sig =
            AgentSig(sk_agent1.sign(&alpha_sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let mut transfer_beta = ECUTransfer {
            object_ref: ObjectRef {
                agent: agent1,
                version: 0,
            },
            to: agent3,
            amount_micro_ecu: 400_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let beta_sender_msg = bincode::serialize(&(
            &transfer_beta.object_ref,
            &transfer_beta.to,
            &transfer_beta.amount_micro_ecu,
            &transfer_beta.transfer_class,
        ))
        .unwrap();
        transfer_beta.sender_sig =
            AgentSig(sk_agent1.sign(&beta_sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

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
            epoch: EpochSeq(1),
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
            epoch: EpochSeq(1),
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
        let val_set = ValidatorSet::new(vec![(ValidatorID(1), vk1)], 0).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef {
                agent: agent1,
                version: 0,
            },
            to: agent2,
            amount_micro_ecu: 100_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let bad_msg = b"tampered";
        transfer.sender_sig =
            AgentSig(sk_agent1.sign(bad_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let cert = TransferCertificate {
            transfer,
            sigs: vec![],
            epoch: EpochSeq(1),
        };
        assert_eq!(
            fast_path.execute_certificate(cert).unwrap_err(),
            ILCConsensusError::InvalidSignature
        );
    }

    #[test]
    fn test_sender_sig_verified_before_quorum() {
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());
        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

        let (sk_val1, vk1) = generate_keypair(1);
        let val_set = ValidatorSet::new(vec![(ValidatorID(1), vk1)], 0).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef {
                agent: agent1,
                version: 0,
            },
            to: agent2,
            amount_micro_ecu: 100_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let bad_msg = b"tampered";
        transfer.sender_sig =
            AgentSig(sk_agent1.sign(bad_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = crate::validator::validator_dst("testnet");
        let sig1 = ValidatorSig(sk_val1.sign(&msg, &dst, &[]));

        let cert = TransferCertificate {
            transfer,
            sigs: vec![(ValidatorID(1), sig1)],
            epoch: EpochSeq(1),
        };
        assert_eq!(
            fast_path.execute_certificate(cert).unwrap_err(),
            ILCConsensusError::InvalidSignature
        );
    }

    #[test]
    fn test_ejected_validator_sig_rejected_after_epoch_boundary() {
        // SEC-004: Historical ValidatorSet resolution.
        // V3 is in the epoch-1 set but ejected at epoch 2.
        // A cert stamped with epoch=1 bearing V3's sig must remain valid after
        // the epoch-2 rotation. A cert stamped with epoch=2 bearing V3's sig
        // must be rejected against the post-ejection set.
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent1, 1_000_000)],
            })
            .unwrap();

        // Epoch 1 set: N=4, F=1. Required=3. Validator 3 will be ejected at epoch 2.
        let (sk1, vk1) = generate_keypair(1);
        let (sk2, vk2) = generate_keypair(2);
        let (sk3, vk3) = generate_keypair(3); // will be ejected
        let (_sk4, vk4) = generate_keypair(4);

        let validators_full = vec![
            (ValidatorID(1), vk1.clone()),
            (ValidatorID(2), vk2.clone()),
            (ValidatorID(3), vk3),
            (ValidatorID(4), vk4.clone()),
        ];
        let val_set = ValidatorSet::new(validators_full, 1).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let dst = crate::validator::validator_dst("testnet");

        let make_transfer = |version: u64| -> ECUTransfer {
            let mut transfer = ECUTransfer {
                object_ref: ObjectRef {
                    agent: agent1,
                    version,
                },
                to: agent2,
                amount_micro_ecu: 100_000,
                transfer_class: TransferClass::Contribution,
                sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
            };
            let sender_msg = bincode::serialize(&(
                &transfer.object_ref,
                &transfer.to,
                &transfer.amount_micro_ecu,
                &transfer.transfer_class,
            ))
            .unwrap();
            transfer.sender_sig =
                AgentSig(sk_agent1.sign(&sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));
            transfer
        };

        // Case 1: epoch-1 cert with V3 is accepted before rotation.
        let transfer_epoch1_pre = make_transfer(0);
        let msg_epoch1_pre = bincode::serialize(&transfer_epoch1_pre).unwrap();
        let cert_epoch1_pre = TransferCertificate {
            transfer: transfer_epoch1_pre,
            sigs: vec![
                (
                    ValidatorID(1),
                    ValidatorSig(sk1.sign(&msg_epoch1_pre, &dst, &[])),
                ),
                (
                    ValidatorID(2),
                    ValidatorSig(sk2.sign(&msg_epoch1_pre, &dst, &[])),
                ),
                (
                    ValidatorID(3),
                    ValidatorSig(sk3.sign(&msg_epoch1_pre, &dst, &[])),
                ),
            ],
            epoch: EpochSeq(1),
        };
        assert!(
            fast_path.execute_certificate(cert_epoch1_pre).is_ok(),
            "epoch-1 cert with V3 sig must be accepted before the ejection boundary"
        );

        // Rotate at epoch 2: V3 is ejected. Post-ejection: N=3, F=0, quorum=1.
        let validators_post = vec![
            (ValidatorID(1), vk1),
            (ValidatorID(2), vk2),
            (ValidatorID(4), vk4),
        ];
        fast_path.rotate_validator_set(EpochSeq(2), ValidatorSet::new(validators_post, 0).unwrap());

        // Case 2: epoch-1 cert with V3 remains valid after rotation because the
        // historically active epoch-1 set still contains V3.
        let transfer_epoch1_post = make_transfer(1);
        let msg_epoch1_post = bincode::serialize(&transfer_epoch1_post).unwrap();
        let cert_epoch1_post = TransferCertificate {
            transfer: transfer_epoch1_post,
            sigs: vec![
                (
                    ValidatorID(1),
                    ValidatorSig(sk1.sign(&msg_epoch1_post, &dst, &[])),
                ),
                (
                    ValidatorID(2),
                    ValidatorSig(sk2.sign(&msg_epoch1_post, &dst, &[])),
                ),
                (
                    ValidatorID(3),
                    ValidatorSig(sk3.sign(&msg_epoch1_post, &dst, &[])),
                ),
            ],
            epoch: EpochSeq(1),
        };
        assert!(
            fast_path.execute_certificate(cert_epoch1_post).is_ok(),
            "epoch-1 cert with V3 sig must remain accepted after the epoch-2 rotation"
        );

        // Case 3: epoch-2 cert with V3 must be rejected against the post-ejection set.
        let transfer_epoch2_bad = make_transfer(2);
        let msg_epoch2_bad = bincode::serialize(&transfer_epoch2_bad).unwrap();
        let cert_epoch2_with_v3 = TransferCertificate {
            transfer: transfer_epoch2_bad,
            sigs: vec![
                (
                    ValidatorID(1),
                    ValidatorSig(sk1.sign(&msg_epoch2_bad, &dst, &[])),
                ),
                (
                    ValidatorID(2),
                    ValidatorSig(sk2.sign(&msg_epoch2_bad, &dst, &[])),
                ),
                (
                    ValidatorID(3),
                    ValidatorSig(sk3.sign(&msg_epoch2_bad, &dst, &[])),
                ),
            ],
            epoch: EpochSeq(2),
        };
        assert_eq!(
            fast_path
                .execute_certificate(cert_epoch2_with_v3)
                .unwrap_err(),
            ILCConsensusError::InvalidSignature,
            "epoch-2 cert with ejected V3 sig must be rejected"
        );

        // Case 4: epoch-2 cert with only still-active validators is accepted.
        let transfer_epoch2_good = make_transfer(2);
        let msg_epoch2_good = bincode::serialize(&transfer_epoch2_good).unwrap();
        let cert_epoch2_valid = TransferCertificate {
            transfer: transfer_epoch2_good,
            sigs: vec![(
                ValidatorID(1),
                ValidatorSig(sk1.sign(&msg_epoch2_good, &dst, &[])),
            )],
            epoch: EpochSeq(2),
        };
        assert!(
            fast_path.execute_certificate(cert_epoch2_valid).is_ok(),
            "epoch-2 cert with a valid post-ejection quorum must be accepted"
        );
    }

    #[test]
    fn test_epoch_zero_cert_resolves_to_genesis_set() {
        // SEC-004: epoch_sets is seeded with (EpochSeq(0), genesis_set).
        // A cert stamped epoch=0 must resolve to the genesis set via
        // range(..=EpochSeq(0)).next_back().
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (sk_agent1, agent1) = generate_agent_keypair(11);
        let (_, agent2) = generate_agent_keypair(22);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(0),
                attributions: vec![(agent1, 1_000_000)],
            })
            .unwrap();

        let (sk1, vk1) = generate_keypair(1);
        let val_set = ValidatorSet::new(vec![(ValidatorID(1), vk1)], 0).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef {
                agent: agent1,
                version: 0,
            },
            to: agent2,
            amount_micro_ecu: 100_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(sk_agent1.sign(b"dummy", &[], &[])),
        };
        let sender_msg = bincode::serialize(&(
            &transfer.object_ref,
            &transfer.to,
            &transfer.amount_micro_ecu,
            &transfer.transfer_class,
        ))
        .unwrap();
        transfer.sender_sig =
            AgentSig(sk_agent1.sign(&sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = crate::validator::validator_dst("testnet");
        let sig1 = ValidatorSig(sk1.sign(&msg, &dst, &[]));

        // epoch=0 cert resolves to genesis set (EpochSeq(0) entry).
        let cert = TransferCertificate {
            transfer,
            sigs: vec![(ValidatorID(1), sig1)],
            epoch: EpochSeq(0),
        };
        assert!(
            fast_path.execute_certificate(cert).is_ok(),
            "epoch-0 cert must resolve to genesis set"
        );
    }

    #[test]
    fn test_quorum_floor_enforced_after_ejection() {
        // BUG-004: the SEC-004 acceptance test (Case 4) passes with quorum=1 because
        // ejecting V3 from N=4 produces N=3, f=0.  That is a safety cliff rather than
        // a meaningful quorum proof.  This test uses a richer N=7→N=6 rotation so
        // f drops from 2 to 1 and quorum drops from 5 to 3, then verifies that a
        // cert with only 2 sigs is still rejected.
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (sk_agent, agent) = generate_agent_keypair(55);
        let (_, agent2) = generate_agent_keypair(66);

        store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent, 1_000_000)],
            })
            .unwrap();

        // Build N=7, f=2 genesis set.
        let keypairs: Vec<(blst::min_pk::SecretKey, ValidatorKey)> =
            (1u8..=7).map(|s| generate_keypair(s)).collect();
        let validators: Vec<(ValidatorID, ValidatorKey)> = keypairs
            .iter()
            .enumerate()
            .map(|(i, (_, vk))| (ValidatorID((i + 1) as u32), vk.clone()))
            .collect();
        let val_set = ValidatorSet::new(validators, 2).unwrap();
        let fast_path = FastPathProtocol::new(val_set, store, "testnet".to_string());

        // Rotate at epoch 2: eject validator 7 → N=6, f=1, quorum=3.
        let validators_post: Vec<(ValidatorID, ValidatorKey)> = keypairs[..6]
            .iter()
            .enumerate()
            .map(|(i, (_, vk))| (ValidatorID((i + 1) as u32), vk.clone()))
            .collect();
        fast_path.rotate_validator_set(EpochSeq(2), ValidatorSet::new(validators_post, 1).unwrap());

        let mut transfer = ECUTransfer {
            object_ref: ObjectRef { agent, version: 0 },
            to: agent2,
            amount_micro_ecu: 100_000,
            transfer_class: TransferClass::Contribution,
            sender_sig: AgentSig(keypairs[0].0.sign(b"dummy", &[], &[])),
        };
        let sender_msg = bincode::serialize(&(
            &transfer.object_ref,
            &transfer.to,
            &transfer.amount_micro_ecu,
            &transfer.transfer_class,
        ))
        .unwrap();
        transfer.sender_sig =
            AgentSig(sk_agent.sign(&sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));

        let msg = bincode::serialize(&transfer).unwrap();
        let dst = crate::validator::validator_dst("testnet");

        // 2-sig cert against epoch-2 quorum=3 must be rejected.
        let cert_under_quorum = TransferCertificate {
            transfer: transfer.clone(),
            sigs: vec![
                (
                    ValidatorID(1),
                    ValidatorSig(keypairs[0].0.sign(&msg, &dst, &[])),
                ),
                (
                    ValidatorID(2),
                    ValidatorSig(keypairs[1].0.sign(&msg, &dst, &[])),
                ),
            ],
            epoch: EpochSeq(2),
        };
        assert_eq!(
            fast_path
                .execute_certificate(cert_under_quorum)
                .unwrap_err(),
            ILCConsensusError::InsufficientSignatures,
            "2-sig cert must be rejected when epoch-2 quorum is 3"
        );

        // 3-sig cert (meets quorum=3) must pass.
        let cert_at_quorum = TransferCertificate {
            transfer,
            sigs: vec![
                (
                    ValidatorID(1),
                    ValidatorSig(keypairs[0].0.sign(&msg, &dst, &[])),
                ),
                (
                    ValidatorID(2),
                    ValidatorSig(keypairs[1].0.sign(&msg, &dst, &[])),
                ),
                (
                    ValidatorID(3),
                    ValidatorSig(keypairs[2].0.sign(&msg, &dst, &[])),
                ),
            ],
            epoch: EpochSeq(2),
        };
        assert!(
            fast_path.execute_certificate(cert_at_quorum).is_ok(),
            "3-sig cert must be accepted when epoch-2 quorum is 3"
        );
    }

    #[test]
    fn test_rotate_validator_set_monotonicity_guard_rejects_stale() {
        // SEC-004: rotate_validator_set must ignore calls where active_from_epoch
        // is less than or equal to the latest recorded epoch.  This prevents a stale
        // or replayed governance action from overwriting a newer set.
        let (env, _dir) = setup_env();
        let store = Arc::new(BalanceStore::new(env).unwrap());

        let (_, vk1) = generate_keypair(1);
        let (_, vk2) = generate_keypair(2);
        let val_set_genesis = ValidatorSet::new(vec![(ValidatorID(1), vk1.clone())], 0).unwrap();
        let fast_path = FastPathProtocol::new(val_set_genesis, store, "testnet".to_string());

        // Advance to epoch 5.
        let val_set_epoch5 = ValidatorSet::new(
            vec![(ValidatorID(1), vk1.clone()), (ValidatorID(2), vk2.clone())],
            0,
        )
        .unwrap();
        fast_path.rotate_validator_set(EpochSeq(5), val_set_epoch5);

        // Stale call: epoch 3 < epoch 5 — must not overwrite.
        let val_set_stale = ValidatorSet::new(vec![(ValidatorID(2), vk2)], 0).unwrap();
        fast_path.rotate_validator_set(EpochSeq(3), val_set_stale);

        // Verify epoch_sets still has only genesis (0) and epoch 5 — not the stale epoch 3.
        let sets = fast_path.epoch_sets.read().unwrap();
        assert!(
            !sets.contains_key(&EpochSeq(3)),
            "stale epoch-3 must not be inserted"
        );
        assert!(
            sets.contains_key(&EpochSeq(5)),
            "epoch-5 must still be present"
        );
        assert_eq!(
            sets.len(),
            2,
            "epoch_sets must have exactly genesis + epoch-5"
        );
    }
}
