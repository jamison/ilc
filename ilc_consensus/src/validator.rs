use crate::types::{ILCConsensusError, ValidatorID, ValidatorKey, ValidatorSet, ValidatorSig};
use blst::min_pk::SecretKey;
use getrandom::getrandom;

pub fn validator_dst(network_id: &str) -> Vec<u8> {
    format!("ILC_FAST_PATH_V1:{}", network_id).into_bytes()
}

/// Returns the intersection-safe BFT quorum threshold: the minimum number of
/// validator signatures required to commit an epoch checkpoint.
///
/// Phase 1590-Fix1: dynamic validator admission invalidated the older
/// `2f + 1` shortcut for intermediate set sizes such as N=5 and N=6. Two
/// size-3 quorums at N=5 can intersect only at the Byzantine validator. The
/// production rule is therefore `N - f`, where `f = floor((N - 1) / 3)`,
/// which guarantees any two quorums intersect in at least f+1 validators.
///
/// Verified values:
///   N=1 → 1, N=2 → 2, N=3 → 3, N=4 → 3, N=5 → 4, N=6 → 5,
///   N=7 → 5, N=8 → 6, N=9 → 7, N=10 → 7
pub fn quorum_threshold(n: usize) -> usize {
    n.saturating_sub(n.saturating_sub(1) / 3)
}

/// Minimum stake required for validator admission (1,000 ECU = 1,000,000,000 micro-ECU).
pub const MIN_STAKE_MICRO_ECU: u64 = 1_000_000_000;

impl ValidatorSet {
    fn rebuild_with(
        validators: Vec<(ValidatorID, ValidatorKey)>,
    ) -> Result<Self, ILCConsensusError> {
        let f = validators.len().saturating_sub(1) / 3;
        // BUG-001: f=0 on N>1 means a single validator can commit transfers.
        // This is mathematically valid under N>3F but operationally dangerous.
        // Emit a visible warning so operators are not silently exposed to the cliff.
        if f == 0 && validators.len() > 1 {
            eprintln!(
                "[sec_warn] rebuild_with: N={} produces f=0 — fault tolerance is zero; \
                 a single validator can finalize transfers. \
                 Token: sec_warn_bft_fault_tolerance_zero",
                validators.len()
            );
        }
        ValidatorSet::new(validators, f)
    }

    /// Applies strict centralization BFT detection limiting boundaries to guarantees of Safety under byzantine assumptions.
    /// Rejects if any single node controls >= 1/3 of the total system stake exactly as required by the Phase 694 model.
    pub fn check_concentration_limit(
        stakes: &[(ValidatorID, u64)],
    ) -> Result<(), ILCConsensusError> {
        let total_stake: u128 = stakes
            .iter()
            .map(|(_, s)| *s as u128)
            .fold(0u128, |acc, s| acc.saturating_add(s));

        // BUG-006: detect pathological saturation before division.
        if total_stake == u128::MAX {
            return Err(ILCConsensusError::Other(
                "stake overflow: total_stake saturated at u128::MAX".to_string(),
            ));
        }

        // BUG-002: use multiplication instead of floor division to avoid the
        // off-by-one where stake == total_stake/3 (exactly 1/3) incorrectly passes.
        // Reject if stake * 3 >= total_stake (i.e., stake >= 1/3 of total).
        for &(_, stake) in stakes {
            if (stake as u128).saturating_mul(3) >= total_stake {
                return Err(ILCConsensusError::Other(
                    "concentration limit exceeded".to_string(),
                ));
            }
        }
        Ok(())
    }

    /// CDL-017 hook: validator admission
    pub fn admit_validator(
        &mut self,
        id: ValidatorID,
        key: ValidatorKey,
        stake_micro_ecu: u64,
    ) -> Result<(), ILCConsensusError> {
        if stake_micro_ecu < MIN_STAKE_MICRO_ECU {
            return Err(ILCConsensusError::Other(format!(
                "insufficient stake: {} micro-ECU provided, minimum is {}",
                stake_micro_ecu, MIN_STAKE_MICRO_ECU
            )));
        }
        if self.validators.contains_key(&id) {
            return Err(ILCConsensusError::Other(format!(
                "validator {} already present",
                id.0
            )));
        }
        if self
            .validators
            .values()
            .any(|existing_key| *existing_key == key)
        {
            return Err(ILCConsensusError::Other(
                "validator key already present".to_string(),
            ));
        }

        let mut entries: Vec<(ValidatorID, ValidatorKey)> = self
            .validators
            .iter()
            .map(|(&eid, k)| (eid, k.clone()))
            .collect();
        entries.push((id, key));
        let rebuilt = ValidatorSet::rebuild_with(entries)?;
        *self = rebuilt;
        Ok(())
    }

    /// CDL-017 hook: validator ejection
    pub fn eject_validator(&mut self, id: ValidatorID) -> Result<(), ILCConsensusError> {
        let original_len = self.validators.len();
        let validators: Vec<(ValidatorID, ValidatorKey)> = self
            .validators
            .iter()
            .filter(|(&existing_id, _)| existing_id != id)
            .map(|(&eid, k)| (eid, k.clone()))
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
    getrandom(&mut ikm)
        .map_err(|e| ILCConsensusError::Other(format!("OS entropy failure: {}", e)))?;

    let sk = SecretKey::key_gen(&ikm, &[])
        .map_err(|_| ILCConsensusError::Other("BLS KeyGen failed".to_string()))?;
    let vk = ValidatorKey(sk.sk_to_pk());
    Ok((sk, vk))
}

pub fn sign_message(sk: &SecretKey, msg: &[u8], network_id: &str) -> ValidatorSig {
    let dst = validator_dst(network_id);
    ValidatorSig(sk.sign(msg, &dst, &[]))
}

pub fn verify_signature(
    vk: &ValidatorKey,
    msg: &[u8],
    sig: &ValidatorSig,
    network_id: &str,
) -> Result<(), ILCConsensusError> {
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
        assert_eq!(
            verify_signature(&vk_spoof, msg, &sig_valid, "testnet_abc"),
            Err(ILCConsensusError::InvalidSignature)
        );
    }

    #[test]
    fn test_concentration_limit_detected() {
        let stakes = vec![
            (ValidatorID(1), 20),
            (ValidatorID(2), 20),
            (ValidatorID(3), 20),
            (ValidatorID(4), 40), // 40*3=120 >= 100 → rejected
        ];
        assert_eq!(
            ValidatorSet::check_concentration_limit(&stakes),
            Err(ILCConsensusError::Other(
                "concentration limit exceeded".to_string()
            ))
        );

        let valid_stakes = vec![
            (ValidatorID(1), 25),
            (ValidatorID(2), 25),
            (ValidatorID(3), 25),
            (ValidatorID(4), 25), // 25*3=75 < 100 → accepted
        ];
        assert!(ValidatorSet::check_concentration_limit(&valid_stakes).is_ok());
    }

    #[test]
    fn test_concentration_limit_exact_one_third_rejected() {
        // BUG-002: with floor division, stake=33 on total=99 would pass (33 > 33 is false).
        // The multiplication approach correctly catches stake * 3 >= total (33*3=99 >= 99).
        let stakes_exact_third = vec![
            (ValidatorID(1), 33),
            (ValidatorID(2), 33),
            (ValidatorID(3), 33),
        ]; // total=99, each stake is exactly 1/3
        assert_eq!(
            ValidatorSet::check_concentration_limit(&stakes_exact_third),
            Err(ILCConsensusError::Other(
                "concentration limit exceeded".to_string()
            )),
            "stake exactly equal to 1/3 of total must be rejected"
        );

        // One unit below 1/3 of total=99 (stake=32) must pass.
        let stakes_below_third = vec![
            (ValidatorID(1), 32),
            (ValidatorID(2), 32),
            (ValidatorID(3), 35),
        ]; // total=99; 32*3=96 < 99, 35*3=105 >= 99
           // Validator 3 holds 35/99 > 1/3, so should be rejected.
        assert_eq!(
            ValidatorSet::check_concentration_limit(&stakes_below_third),
            Err(ILCConsensusError::Other(
                "concentration limit exceeded".to_string()
            )),
        );

        // Validator with stake 32 of total 99: 32*3=96 < 99, strictly under 1/3.
        let stakes_all_under = vec![
            (ValidatorID(1), 32),
            (ValidatorID(2), 32),
            (ValidatorID(3), 32),
            (ValidatorID(4), 3),
        ]; // total=99; max stake 32, 32*3=96 < 99
        assert!(ValidatorSet::check_concentration_limit(&stakes_all_under).is_ok());
    }

    #[test]
    fn test_concentration_limit_large_stakes_rejected() {
        // BUG-006: verify the check behaves correctly at u64::MAX stake values.
        // Three validators each at u64::MAX: total = 3 * u64::MAX, which does NOT
        // saturate u128 (saturation requires ~2^64 validators — impossible in practice).
        // Each holds exactly 1/3 of total, so all three trigger "concentration limit
        // exceeded" via the multiplication path (stake*3 == total_stake >= total_stake).
        // The u128::MAX saturation guard is a defensive check for pathological input
        // that cannot be reached with u64 stake values.
        let stakes = vec![
            (ValidatorID(1), u64::MAX),
            (ValidatorID(2), u64::MAX),
            (ValidatorID(3), u64::MAX),
        ];
        assert_eq!(
            ValidatorSet::check_concentration_limit(&stakes),
            Err(ILCConsensusError::Other(
                "concentration limit exceeded".to_string()
            )),
            "each validator holding exactly 1/3 of total must be rejected"
        );
    }

    #[test]
    fn test_eject_to_f_zero_warns_but_succeeds() {
        // BUG-001: ejecting from N=4 (f=1) to N=3 (f=0) silently drops fault tolerance.
        // The fix emits a visible warning token but does not fail — f=0 is still
        // mathematically valid under N>3F.  This test confirms the mutation succeeds
        // and f is correctly set to 0.
        let mut set = make_validator_set(4);
        assert_eq!(set.f, 1);
        set.eject_validator(ValidatorID(4)).unwrap();
        assert_eq!(set.validators.len(), 3);
        assert_eq!(set.f, 0, "f must be 0 after ejecting from N=4 to N=3");
    }

    #[test]
    fn test_admit_validator_adds_validator_and_recomputes_f() {
        let mut set = make_validator_set(3);
        let (_, key) = generate_validator_key().unwrap();

        set.admit_validator(ValidatorID(4), key, MIN_STAKE_MICRO_ECU)
            .unwrap();

        assert_eq!(set.validators.len(), 4);
        assert_eq!(set.f, 1);
        assert!(set.validators.contains_key(&ValidatorID(4)));
    }

    #[test]
    fn test_admit_validator_rejects_duplicate_id() {
        let mut set = make_validator_set(3);
        let (_, key) = generate_validator_key().unwrap();

        let err = set
            .admit_validator(ValidatorID(1), key, MIN_STAKE_MICRO_ECU)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("validator 1 already present".to_string())
        );
    }

    #[test]
    fn test_admit_validator_rejects_duplicate_key() {
        let mut set = make_validator_set(3);
        let duplicate_key = set.validators.values().next().unwrap().clone();

        let err = set
            .admit_validator(ValidatorID(4), duplicate_key, MIN_STAKE_MICRO_ECU)
            .unwrap_err();
        assert_eq!(
            err,
            ILCConsensusError::Other("validator key already present".to_string())
        );
    }

    #[test]
    fn test_admit_validator_rejects_insufficient_stake() {
        let mut set = make_validator_set(3);
        let (_, key) = generate_validator_key().unwrap();

        let err = set
            .admit_validator(ValidatorID(4), key, MIN_STAKE_MICRO_ECU - 1)
            .unwrap_err();
        assert!(
            format!("{:?}", err).contains("insufficient stake"),
            "stake below minimum must be rejected, got: {:?}",
            err
        );
    }

    #[test]
    fn test_eject_validator_removes_validator_and_recomputes_f() {
        let mut set = make_validator_set(4);

        set.eject_validator(ValidatorID(4)).unwrap();

        assert_eq!(set.validators.len(), 3);
        assert_eq!(set.f, 0);
        assert!(!set.validators.contains_key(&ValidatorID(4)));
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
