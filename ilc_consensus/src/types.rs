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
        Ok(ValidatorSig(sig))
    }
}

/// Fast-Path Certified transaction object containing Byzantine Consistent Broadcast acknowledgment signatures.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransferCertificate {
    pub transfer: ECUTransfer,
    pub sigs: Vec<(ValidatorID, ValidatorSig)>, // Pair Validator routing to signature for discrete threshold checking
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
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpochSettlementRecord {
    pub epoch: EpochSeq,
    pub state_root: CIDv1Root,
}

/// EpochSettlementTx represents the payload submitted natively by the Epistemic Engine bridging Phase 14 CID components into the shared-object protocol.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpochSettlementTx {
    pub epoch: EpochSeq,
    pub state_root: CIDv1Root,
}

/// AggSig is used exclusively for combining multiple signatures via `blst::AggregateSignature::aggregate`.
/// Eliminated M-001 gap by mapping correctly to BLS collective cryptography rather than SecretKey generation.
#[derive(Debug, Clone)]
pub struct AggSig(pub AggregateSignature);

impl PartialEq for AggSig {
    fn eq(&self, other: &Self) -> bool {
        self.0.to_signature().serialize() == other.0.to_signature().serialize()
    }
}

impl Eq for AggSig {}

/// EpochCheckpoint embeds the epoch settlement alongside an aggregate quorum signature.
#[derive(Debug, Clone)]
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
    #[error("Internal LMDB or system error: {0}")]
    Other(String),
}

/// Batch containing system-issued ECU allocations during Epoch settlement.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttributionBatch {
    pub epoch: EpochSeq,
    pub attributions: Vec<(AgentID, u64)>, // Added micro-ecu additions
}

impl ValidatorSet {
    pub fn new(validators: Vec<(ValidatorID, ValidatorKey)>, f: usize) -> Result<Self, ILCConsensusError> {
        let n = validators.len();
        if n <= 3 * f {
            return Err(ILCConsensusError::Other(format!("Invalid ValidatorSet: N ({}) must be > 3F ({})", n, 3 * f)));
        }
        Ok(ValidatorSet { validators, f })
    }
}
