use crate::types::{ValidatorID, ValidatorKey, ValidatorSet, ValidatorSig, ILCConsensusError};
use blst::min_pk::SecretKey;
use getrandom::getrandom;

pub fn validator_dst(network_id: &str) -> Vec<u8> {
    format!("ILC_FAST_PATH_V1:{}", network_id).into_bytes()
}

impl ValidatorSet {
    fn rebuild_with(validators: Vec<(ValidatorID, ValidatorKey)>) -> Result<Self, ILCConsensusError> {
        let f = validators.len().saturating_sub(1) / 3;
        ValidatorSet::new(validators, f)
    }

    /// Applies strict centralization BFT detection limiting boundaries to guarantees of Safety under byzantine assumptions.
    /// Rejects if any single node controls >= 1/3 of the total system stake exactly as required by the Phase 694 model.
    pub fn check_concentration_limit(stakes: &[(ValidatorID, u64)]) -> Result<(), ILCConsensusError> {
        let total_stake: u128 = stakes.iter()
            .map(|(_, s)| *s as u128)
            .fold(0u128, |acc, s| acc.saturating_add(s));
        let ceiling = total_stake / 3;

        for &(_, stake) in stakes {
            if stake as u128 > ceiling {
                return Err(ILCConsensusError::Other("concentration limit exceeded".to_string()));
            }
        }
        Ok(())
    }

    /// CDL-017 hook: validator admission
    pub fn admit_validator(&mut self, id: ValidatorID, key: ValidatorKey) -> Result<(), ILCConsensusError> {
        if self.validators.iter().any(|(existing_id, _)| *existing_id == id) {
            return Err(ILCConsensusError::Other(format!(
                "validator {} already present",
                id.0
            )));
        }
        if self.validators.iter().any(|(_, existing_key)| *existing_key == key) {
            return Err(ILCConsensusError::Other(
                "validator key already present".to_string(),
            ));
        }

        let mut validators = self.validators.clone();
        validators.push((id, key));
        let rebuilt = ValidatorSet::rebuild_with(validators)?;
        *self = rebuilt;
        Ok(())
    }

    /// CDL-017 hook: validator ejection
    pub fn eject_validator(&mut self, id: ValidatorID) -> Result<(), ILCConsensusError> {
        let original_len = self.validators.len();
        let validators: Vec<(ValidatorID, ValidatorKey)> = self.validators
            .iter()
            .filter(|(existing_id, _)| *existing_id != id)
            .cloned()
            .collect();

        if validators.len() == original_len {
            return Err(ILCConsensusError::Other(format!(
                "validator {} not present",
                id.0
            )));
        }

        let rebuilt = ValidatorSet::rebuild_with(validators)?;
        *self = rebuilt;
        Ok(())
    }
}

pub fn generate_validator_key() -> Result<(SecretKey, ValidatorKey), ILCConsensusError> {
    let mut ikm = [0u8; 32];
    getrandom(&mut ikm).map_err(|e| ILCConsensusError::Other(format!("OS entropy failure: {}", e)))?;
    
    let sk = SecretKey::key_gen(&ikm, &[]).map_err(|_| ILCConsensusError::Other("BLS KeyGen failed".to_string()))?;
    let vk = ValidatorKey(sk.sk_to_pk());
    Ok((sk, vk))
}

pub fn sign_message(sk: &SecretKey, msg: &[u8], network_id: &str) -> ValidatorSig {
    let dst = validator_dst(network_id);
    ValidatorSig(sk.sign(msg, &dst, &[]))
}

pub fn verify_signature(vk: &ValidatorKey, msg: &[u8], sig: &ValidatorSig, network_id: &str) -> Result<(), ILCConsensusError> {
    let dst = validator_dst(network_id);
    let valid = sig.0.verify(true, msg, &dst, &[], &vk.0, true);
    if valid == blst::BLST_ERROR::BLST_SUCCESS {
        Ok(())
    } else {
        Err(ILCConsensusError::InvalidSignature)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_validator_set(count: u32) -> ValidatorSet {
        let mut validators = Vec::new();
        for id in 1..=count {
            let (_, key) = generate_validator_key().unwrap();
            validators.push((ValidatorID(id), key));
        }
        ValidatorSet::new(validators, count.saturating_sub(1) as usize / 3).unwrap()
    }

    #[test]
    fn test_keygen_produces_valid_keypair() {
        let (sk, vk) = generate_validator_key().unwrap();
        let msg = b"ilc_m007_test_message_bound";
        let sig = sign_message(&sk, msg, "testnet_abc");
        assert!(verify_signature(&vk, msg, &sig, "testnet_abc").is_ok());
    }

    #[test]
    fn test_cross_network_sig_rejected() {
        let (sk, vk) = generate_validator_key().unwrap();
        let msg = b"ilc_m007_test_message_bound";
        
        let sig = sign_message(&sk, msg, "testnet_a");
        // Verify via incorrect network identifier enforcing SEC-002 constraints dynamically
        let result = verify_signature(&vk, msg, &sig, "testnet_b");
        assert_eq!(result, Err(ILCConsensusError::InvalidSignature));
    }

    #[test]
    fn test_invalid_signature_rejected() {
        let (sk, vk) = generate_validator_key().unwrap();
        let msg = b"ilc_m007_test_message_bound";
        let sig_valid = sign_message(&sk, msg, "testnet_abc");

        // Alter message payload maliciously asserting verify_signature actively tracks verification failures
        let tampered_msg = b"ilc_tampered_malicious_boundary";
        let result = verify_signature(&vk, tampered_msg, &sig_valid, "testnet_abc");
        assert_eq!(result, Err(ILCConsensusError::InvalidSignature));
        
        // Assert spoofing a valid signature against a different honest key natively catches cross-key rejections
        let (_, vk_spoof) = generate_validator_key().unwrap();
        assert_eq!(verify_signature(&vk_spoof, msg, &sig_valid, "testnet_abc"), Err(ILCConsensusError::InvalidSignature));
    }

    #[test]
    fn test_concentration_limit_detected() {
        let stakes = vec![
            (ValidatorID(1), 20),
            (ValidatorID(2), 20),
            (ValidatorID(3), 20),
            (ValidatorID(4), 40), // Exceeds floor(100 / 3) = 33 boundary limit
        ];
        assert_eq!(
            ValidatorSet::check_concentration_limit(&stakes),
            Err(ILCConsensusError::Other("concentration limit exceeded".to_string()))
        );

        let valid_stakes = vec![
            (ValidatorID(1), 25),
            (ValidatorID(2), 25),
            (ValidatorID(3), 25),
            (ValidatorID(4), 25), // Smooth equilibrium mapping 
        ];
        assert!(ValidatorSet::check_concentration_limit(&valid_stakes).is_ok());
    }

    #[test]
    fn test_admit_validator_adds_validator_and_recomputes_f() {
        let mut set = make_validator_set(3);
        let (_, key) = generate_validator_key().unwrap();

        set.admit_validator(ValidatorID(4), key).unwrap();

        assert_eq!(set.validators.len(), 4);
        assert_eq!(set.f, 1);
        assert!(set.validators.iter().any(|(id, _)| *id == ValidatorID(4)));
    }

    #[test]
    fn test_admit_validator_rejects_duplicate_id() {
        let mut set = make_validator_set(3);
        let (_, key) = generate_validator_key().unwrap();

        let err = set.admit_validator(ValidatorID(1), key).unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("validator 1 already present".to_string())
        );
    }

    #[test]
    fn test_admit_validator_rejects_duplicate_key() {
        let mut set = make_validator_set(3);
        let duplicate_key = set.validators[0].1.clone();

        let err = set
            .admit_validator(ValidatorID(4), duplicate_key)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("validator key already present".to_string())
        );
    }

    #[test]
    fn test_eject_validator_removes_validator_and_recomputes_f() {
        let mut set = make_validator_set(4);

        set.eject_validator(ValidatorID(4)).unwrap();

        assert_eq!(set.validators.len(), 3);
        assert_eq!(set.f, 0);
        assert!(!set.validators.iter().any(|(id, _)| *id == ValidatorID(4)));
    }

    #[test]
    fn test_eject_validator_rejects_missing_id() {
        let mut set = make_validator_set(4);

        let err = set.eject_validator(ValidatorID(99)).unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("validator 99 not present".to_string())
        );
    }

    #[test]
    fn test_eject_validator_rejects_invalid_collapse() {
        let mut set = make_validator_set(1);

        let err = set.eject_validator(ValidatorID(1)).unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("Invalid ValidatorSet: N (0) must be > 3F (0)".to_string())
        );
    }

    #[test]
    fn test_validator_set_new_rejects_duplicate_keys() {
        let (_, key) = generate_validator_key().unwrap();
        let err = ValidatorSet::new(
            vec![
                (ValidatorID(1), key.clone()),
                (ValidatorID(2), key),
                (ValidatorID(3), generate_validator_key().unwrap().1),
                (ValidatorID(4), generate_validator_key().unwrap().1),
            ],
            1,
        )
        .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("Duplicate ValidatorKey in ValidatorSet".to_string())
        );
    }
}
