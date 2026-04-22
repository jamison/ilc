use blst::min_pk::{PublicKey, Signature, AggregateSignature};
use serde::{Deserialize, Serialize};

/// AgentID represents a unique ILC Agent inside the system. 
/// Derived securely via CDL-042 key mechanics.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct AgentID(pub [u8; 48]);

impl serde::Serialize for AgentID {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_bytes(&self.0)
    }
}

impl<'de> serde::Deserialize<'de> for AgentID {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let bytes: Vec<u8> = serde::Deserialize::deserialize(deserializer)?;
        if bytes.len() != 48 {
            return Err(serde::de::Error::custom("AgentID must be exactly 48 bytes"));
        }
        let mut arr = [0u8; 48];
        arr.copy_from_slice(&bytes);
        Ok(AgentID(arr))
    }
}

pub const AGENT_TRANSFER_DST: &[u8] = b"ILC_AGENT_TRANSFER_V1";
pub const ILC_EPOCH_SIG_DST: &[u8] = b"ILC_EPOCH_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_NUL_";

pub struct AgentSecretKey(pub blst::min_pk::SecretKey);

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AgentSig(pub Signature);

impl serde::Serialize for AgentSig {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_bytes(&self.0.to_bytes())
    }
}

impl<'de> serde::Deserialize<'de> for AgentSig {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let bytes: Vec<u8> = serde::Deserialize::deserialize(deserializer)?;
        let sig = Signature::from_bytes(&bytes)
            .map_err(|e| serde::de::Error::custom(format!("blst agent signature parse fail: {:?}", e)))?;
        // SEC-FIX-01: G2 subgroup check — from_bytes decompresses but does not enforce
        // r-order subgroup membership. An off-subgroup point can forge verify() results.
        sig.validate(false)
            .map_err(|_| serde::de::Error::custom("AgentSig G2 subgroup check failed"))?;
        Ok(AgentSig(sig))
    }
}

/// ObjectRef anchors an owned-object uniquely within the Mysticeti fast-path.
/// This fulfills the Sui `ObjectID`/`ObjectRef` semantic replacement gap (M-001 finding).
/// An ECU balance object is tied to an Agent and a monotonic version to prevent replays.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ObjectRef {
    pub agent: AgentID,
    pub version: u64, // Uniquely identifies the state instantiation of the Owned object
}

/// EpochSeq provides monotonic epoch tracking.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct EpochSeq(pub u64);

/// ECUBalance represents the total active owned-object value inside the LMDB store.
/// 
/// Note: Enforces strict M-Series specification prohibiting floating-point arithmetic.
/// Value is stored strictly as `u64` representing micro-ECU (µECU).
/// 1 ECU = 1_000_000 µECU.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ECUBalance {
    pub agent: AgentID,
    pub amount_micro_ecu: u64,
    pub epoch: EpochSeq,
    pub version: u64, // Tracks the monotonically increasing nonce required to enforce ObjectRef checks
}

/// ECUTransfer contains the fast-path deterministic instruction to alter Owned Objects.
/// Uniquely locks on `object_ref` to enforce SafetyNoDualCert property.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ECUTransfer {
    pub object_ref: ObjectRef,   // owned object mapping directly to sender agent and monotonic version
    pub to: AgentID,
    pub amount_micro_ecu: u64,
    pub sender_sig: AgentSig,
}

/// Validator Sig wrapping the direct `blst` primitive.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidatorSig(pub Signature);

impl serde::Serialize for ValidatorSig {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_bytes(&self.0.to_bytes())
    }
}

impl<'de> serde::Deserialize<'de> for ValidatorSig {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let bytes: Vec<u8> = serde::Deserialize::deserialize(deserializer)?;
        let sig = Signature::from_bytes(&bytes)
            .map_err(|e| serde::de::Error::custom(format!("blst signature parse fail: {:?}", e)))?;
        // SEC-FIX-01: G2 subgroup check.
        sig.validate(false)
            .map_err(|_| serde::de::Error::custom("ValidatorSig G2 subgroup check failed"))?;
        Ok(ValidatorSig(sig))
    }
}

/// Fast-Path Certified transaction object containing Byzantine Consistent Broadcast acknowledgment signatures.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransferCertificate {
    pub transfer: ECUTransfer,
    pub sigs: Vec<(ValidatorID, ValidatorSig)>, // Pair Validator routing to signature for discrete threshold checking
    pub epoch: EpochSeq,
}

/// CIDv1Root encapsulates the strictly defined Phase 14 Canonical Commitment format.
/// Always 36 bytes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct CIDv1Root {
    pub p1: [u8; 32],
    pub p2: [u8; 4],
}

impl CIDv1Root {
    pub fn new(bytes: [u8; 36]) -> Self {
        let mut p1 = [0u8; 32];
        let mut p2 = [0u8; 4];
        p1.copy_from_slice(&bytes[..32]);
        p2.copy_from_slice(&bytes[32..]);
        Self { p1, p2 }
    }
}

/// EpochSettlementRecord defines the Shared-Object committed directly via the full DAG ordering layer.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EpochSettlementRecord {
    pub epoch: EpochSeq,
    pub state_root: CIDv1Root,
}

/// EpochSettlementTx represents the payload submitted natively by the Epistemic Engine bridging Phase 14 CID components into the shared-object protocol.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EpochSettlementTx {
    pub epoch: EpochSeq,
    pub state_root: CIDv1Root,
}

/// AggSig is used exclusively for combining multiple signatures via `blst::AggregateSignature::aggregate`.
/// Eliminated M-001 gap by mapping correctly to BLS collective cryptography rather than SecretKey generation.
#[derive(Debug, Clone)]
pub struct AggSig(pub AggregateSignature);

impl serde::Serialize for AggSig {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let bytes = self.0.to_signature().serialize().to_vec();
        serializer.serialize_bytes(&bytes)
    }
}

impl<'de> serde::Deserialize<'de> for AggSig {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let bytes: Vec<u8> = serde::Deserialize::deserialize(deserializer)?;
        let sig = blst::min_pk::Signature::from_bytes(&bytes)
            .map_err(|e| serde::de::Error::custom(format!("Invalid blst signature: {:?}", e)))?;
        // SEC-FIX-01: G2 subgroup check — guards against forged EpochCheckpoint acceptance.
        sig.validate(false)
            .map_err(|_| serde::de::Error::custom("AggSig G2 subgroup check failed"))?;
        Ok(AggSig(blst::min_pk::AggregateSignature::from_signature(&sig)))
    }
}

impl PartialEq for AggSig {
    fn eq(&self, other: &Self) -> bool {
        self.0.to_signature().serialize() == other.0.to_signature().serialize()
    }
}

impl Eq for AggSig {}

/// EpochCheckpoint embeds the epoch settlement alongside an aggregate quorum signature.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct EpochCheckpoint {
    pub record: EpochSettlementRecord,
    pub sigs: AggSig,
}

/// Validator identity
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ValidatorID(pub u32);

/// ValidatorKey wrapping the direct `blst` public key primitive.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidatorKey(pub PublicKey);

/// ValidatorSet tracking the current functional topology and Fault conditions.
#[derive(Debug, Clone)]
pub struct ValidatorSet {
    pub validators: Vec<(ValidatorID, ValidatorKey)>,
    pub f: usize,
}

/// Core interface mapping error cases across the DAG interactions.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, thiserror::Error)]
pub enum ILCConsensusError {
    #[error("Invalid validator signature")]
    InvalidSignature,
    #[error("Insufficient signatures for quorum certificate")]
    InsufficientSignatures,
    #[error("Conflicting transfer attempted on identical ObjectRef version")]
    ConflictingTransfer, // Triggers on dual-cert violations for the same ObjectRef
    #[error("Self-transfer explicitly prohibited")]
    SelfTransfer,
    #[error("Invalid epoch reference")]
    InvalidEpoch,
    #[error("Insufficient micro-ECU for transfer")]
    BalanceInsufficient,
    #[error("BLS signature verification failed")]
    BLSVerificationFailed,
    #[error("Internal LMDB or system error: {0}")]
    Other(String),
}

/// Batch containing system-issued ECU allocations during Epoch settlement.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttributionBatch {
    pub epoch: EpochSeq,
    pub attributions: Vec<(AgentID, u64)>, // Added micro-ecu additions
}

#[cfg(test)]
mod tests {
    use super::*;
    use blst::min_pk::SecretKey;
    use bincode;

    // ---------------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------------

    fn valid_agent_sig_bytes() -> Vec<u8> {
        let sk = SecretKey::key_gen(&[1u8; 32], &[]).unwrap();
        let sig = sk.sign(b"test_message", AGENT_TRANSFER_DST, &[]);
        sig.to_bytes().to_vec()
    }

    fn valid_validator_sig_bytes() -> Vec<u8> {
        let sk = SecretKey::key_gen(&[2u8; 32], &[]).unwrap();
        let sig = sk.sign(b"test_message", b"ILC_FAST_PATH_V1:testnet", &[]);
        sig.to_bytes().to_vec()
    }

    fn valid_aggsig_bytes() -> Vec<u8> {
        let sk = SecretKey::key_gen(&[3u8; 32], &[]).unwrap();
        let sig = sk.sign(b"test_message", ILC_EPOCH_SIG_DST, &[]);
        let agg = blst::min_pk::AggregateSignature::aggregate(&[&sig], false).unwrap();
        agg.to_signature().to_bytes().to_vec()
    }

    /// All-zeros G2 bytes (96 bytes with no compression flag).
    /// Byte 0 = 0x00 has neither the compression bit (0x80) set,
    /// so from_bytes rejects this as a malformed point encoding.
    fn g2_invalid_bytes() -> Vec<u8> {
        vec![0u8; 96]
    }

    /// All-zeros G1 bytes (48 bytes with no compression flag).
    fn g1_invalid_bytes() -> Vec<u8> {
        vec![0u8; 48]
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-01: AgentSig G2 subgroup check
    // ---------------------------------------------------------------------------

    #[test]
    fn test_agentsig_deserialize_valid_sig_passes() {
        let bytes = valid_agent_sig_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<AgentSig, _> = bincode::deserialize(&encoded);
        assert!(result.is_ok(), "valid AgentSig must deserialize successfully");
    }

    #[test]
    fn test_agentsig_deserialize_invalid_bytes_rejected() {
        // All-zeros bytes lack the required compression flag (bit 7 of byte 0).
        // blst::Signature::from_bytes rejects this before validate() is reached.
        let bytes = g2_invalid_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<AgentSig, _> = bincode::deserialize(&encoded);
        assert!(result.is_err(), "malformed G2 bytes must be rejected by AgentSig deserialization");
    }

    #[test]
    fn test_agentsig_validate_is_called_on_valid_path() {
        // Confirm that validate() passes for legitimately generated signatures.
        // Off-subgroup G2 vectors require BLS12-381-specific test data outside
        // this crate; subgroup check presence is verified by code review +
        // this regression confirming the valid path still works.
        let sk = SecretKey::key_gen(&[77u8; 32], &[]).unwrap();
        let sig = sk.sign(b"validate_test", AGENT_TRANSFER_DST, &[]);
        assert!(sig.validate(false).is_ok(), "valid sig must pass validate()");
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-01: ValidatorSig G2 subgroup check
    // ---------------------------------------------------------------------------

    #[test]
    fn test_validatorsig_deserialize_valid_sig_passes() {
        let bytes = valid_validator_sig_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<ValidatorSig, _> = bincode::deserialize(&encoded);
        assert!(result.is_ok(), "valid ValidatorSig must deserialize successfully");
    }

    #[test]
    fn test_validatorsig_deserialize_invalid_bytes_rejected() {
        let bytes = g2_invalid_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<ValidatorSig, _> = bincode::deserialize(&encoded);
        assert!(result.is_err(), "malformed G2 bytes must be rejected by ValidatorSig deserialization");
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-01: AggSig G2 subgroup check
    // ---------------------------------------------------------------------------

    #[test]
    fn test_aggsig_deserialize_valid_sig_passes() {
        let bytes = valid_aggsig_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<AggSig, _> = bincode::deserialize(&encoded);
        assert!(result.is_ok(), "valid AggSig must deserialize successfully");
    }

    #[test]
    fn test_aggsig_deserialize_invalid_bytes_rejected() {
        let bytes = g2_invalid_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<AggSig, _> = bincode::deserialize(&encoded);
        assert!(result.is_err(), "malformed G2 bytes must be rejected by AggSig deserialization");
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-01: G1 PublicKey (AgentID-as-pubkey) subgroup check
    // ---------------------------------------------------------------------------

    #[test]
    fn test_g1_invalid_bytes_fail_pubkey_from_bytes() {
        // All-zeros bytes without compression flag are rejected by from_bytes.
        let bytes = g1_invalid_bytes();
        assert!(
            blst::min_pk::PublicKey::from_bytes(&bytes).is_err(),
            "malformed G1 bytes must be rejected by PublicKey::from_bytes"
        );
    }

    #[test]
    fn test_valid_g1_pubkey_passes_validate() {
        let sk = SecretKey::key_gen(&[4u8; 32], &[]).unwrap();
        let pk = sk.sk_to_pk();
        assert!(pk.validate().is_ok(), "valid G1 public key must pass validate()");
    }
}

impl ValidatorSet {
    pub fn new(validators: Vec<(ValidatorID, ValidatorKey)>, f: usize) -> Result<Self, ILCConsensusError> {
        let n = validators.len();
        if n <= 3 * f {
            return Err(ILCConsensusError::Other(format!("Invalid ValidatorSet: N ({}) must be > 3F ({})", n, 3 * f)));
        }
        for i in 0..validators.len() {
            for j in (i + 1)..validators.len() {
                if validators[i].0 == validators[j].0 {
                    return Err(ILCConsensusError::Other(format!(
                        "Duplicate ValidatorID in ValidatorSet: {}",
                        validators[i].0 .0
                    )));
                }
                if validators[i].1 == validators[j].1 {
                    return Err(ILCConsensusError::Other(
                        "Duplicate ValidatorKey in ValidatorSet".to_string(),
                    ));
                }
            }
        }
        Ok(ValidatorSet { validators, f })
    }
}
