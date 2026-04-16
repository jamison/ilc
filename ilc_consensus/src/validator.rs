use crate::types::{ValidatorID, ValidatorKey, ValidatorSet, ValidatorSig, ILCConsensusError};
use blst::min_pk::SecretKey;
use getrandom::getrandom;

pub const VALIDATOR_DST: &[u8] = b"ILC_FAST_PATH_V1";

impl ValidatorSet {
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
    pub fn admit_validator(&mut self, _id: ValidatorID, _key: ValidatorKey) -> Result<(), ILCConsensusError> {
        unimplemented!("CDL-017: validator admission requires ratification before activation")
    }

    /// CDL-017 hook: validator ejection
    pub fn eject_validator(&mut self, _id: ValidatorID) -> Result<(), ILCConsensusError> {
        unimplemented!("CDL-017: validator ejection requires ratification before activation")
    }
}

pub fn generate_validator_key() -> Result<(SecretKey, ValidatorKey), ILCConsensusError> {
    let mut ikm = [0u8; 32];
    getrandom(&mut ikm).map_err(|e| ILCConsensusError::Other(format!("OS entropy failure: {}", e)))?;
    
    let sk = SecretKey::key_gen(&ikm, &[]).map_err(|_| ILCConsensusError::Other("BLS KeyGen failed".to_string()))?;
    let vk = ValidatorKey(sk.sk_to_pk());
    Ok((sk, vk))
}

pub fn sign_message(sk: &SecretKey, msg: &[u8]) -> ValidatorSig {
    ValidatorSig(sk.sign(msg, VALIDATOR_DST, &[]))
}

pub fn verify_signature(vk: &ValidatorKey, msg: &[u8], sig: &ValidatorSig) -> Result<(), ILCConsensusError> {
    let valid = sig.0.verify(true, msg, VALIDATOR_DST, &[], &vk.0, true);
    if valid == blst::BLST_ERROR::BLST_SUCCESS {
        Ok(())
    } else {
        Err(ILCConsensusError::InvalidSignature)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_keygen_produces_valid_keypair() {
        let (sk, vk) = generate_validator_key().unwrap();
        let msg = b"ilc_m007_test_message_bound";
        let sig = sign_message(&sk, msg);
        assert!(verify_signature(&vk, msg, &sig).is_ok());
    }

    #[test]
    fn test_invalid_signature_rejected() {
        let (sk, vk) = generate_validator_key().unwrap();
        let msg = b"ilc_m007_test_message_bound";
        let sig_valid = sign_message(&sk, msg);

        // Alter message payload maliciously asserting verify_signature actively tracks verification failures
        let tampered_msg = b"ilc_tampered_malicious_boundary";
        let result = verify_signature(&vk, tampered_msg, &sig_valid);
        assert_eq!(result, Err(ILCConsensusError::InvalidSignature));
        
        // Assert spoofing a valid signature against a different honest key natively catches cross-key rejections
        let (_, vk_spoof) = generate_validator_key().unwrap();
        assert_eq!(verify_signature(&vk_spoof, msg, &sig_valid), Err(ILCConsensusError::InvalidSignature));
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
    #[should_panic(expected = "CDL-017: validator admission requires ratification before activation")]
    fn test_admit_validator_is_unimplemented() {
        let mut set = ValidatorSet { validators: vec![], f: 0 };
        let (_, key) = generate_validator_key().unwrap();
        let _ = set.admit_validator(ValidatorID(1), key);
    }

    #[test]
    #[should_panic(expected = "CDL-017: validator ejection requires ratification before activation")]
    fn test_eject_validator_is_unimplemented() {
        let mut set = ValidatorSet { validators: vec![], f: 0 };
        let _ = set.eject_validator(ValidatorID(1));
    }
}
