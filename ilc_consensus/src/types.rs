use blst::min_pk::{AggregateSignature, PublicKey, Signature};
use serde::de::{Error as DeError, SeqAccess, Visitor};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;

fn deserialize_fixed_bytes<'de, D, const N: usize>(
    deserializer: D,
    type_name: &'static str,
) -> Result<[u8; N], D::Error>
where
    D: serde::Deserializer<'de>,
{
    struct FixedBytesVisitor<const N: usize> {
        type_name: &'static str,
    }

    impl<'de, const N: usize> Visitor<'de> for FixedBytesVisitor<N> {
        type Value = [u8; N];

        fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
            write!(
                formatter,
                "{} encoded as exactly {} bytes",
                self.type_name, N
            )
        }

        fn visit_bytes<E>(self, bytes: &[u8]) -> Result<Self::Value, E>
        where
            E: DeError,
        {
            if bytes.len() != N {
                return Err(E::custom(format!(
                    "{} must be exactly {} bytes, got {} bytes",
                    self.type_name,
                    N,
                    bytes.len()
                )));
            }
            let mut out = [0u8; N];
            out.copy_from_slice(bytes);
            Ok(out)
        }

        fn visit_borrowed_bytes<E>(self, bytes: &'de [u8]) -> Result<Self::Value, E>
        where
            E: DeError,
        {
            self.visit_bytes(bytes)
        }

        fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
        where
            A: SeqAccess<'de>,
        {
            let mut out = [0u8; N];
            for (idx, slot) in out.iter_mut().enumerate() {
                *slot = seq.next_element()?.ok_or_else(|| {
                    DeError::custom(format!(
                        "{} ended before byte {} of {}",
                        self.type_name, idx, N
                    ))
                })?;
            }
            if seq.next_element::<u8>()?.is_some() {
                return Err(DeError::custom(format!(
                    "{} exceeds fixed {} byte length",
                    self.type_name, N
                )));
            }
            Ok(out)
        }
    }

    deserializer.deserialize_bytes(FixedBytesVisitor::<N> { type_name })
}

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
        Ok(AgentID(deserialize_fixed_bytes::<D, 48>(
            deserializer,
            "AgentID",
        )?))
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
        let bytes = deserialize_fixed_bytes::<D, 96>(deserializer, "AgentSig")?;
        let sig = Signature::from_bytes(&bytes).map_err(|e| {
            serde::de::Error::custom(format!("blst agent signature parse fail: {:?}", e))
        })?;
        // SEC-FIX-01/SEC-AUDIT: G2 subgroup + infinity check. from_bytes
        // decompresses but does not enforce all cryptographic validity checks.
        sig.validate(true)
            .map_err(|_| serde::de::Error::custom("AgentSig G2 validity check failed"))?;
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

/// TransferClass distinguishes contribution transfers (work submitted to the epistemic graph)
/// from payment transfers (agent-to-agent bounty payouts, escrow releases).
///
/// Privacy routing rules:
/// - `Contribution`: mandatory privacy lane (k=30, jitter=3). No opt-out.
///   The anonymity set is collective — one opt-out shrinks the batch for all members.
/// - `Payment`: defaults to the same privacy lane. Agent may opt out to the express lane
///   (no jitter, immediate settlement) by supplying an explicit `ExpressConsent`.
///
/// `transfer_class` is covered by the agent's BLS sender signature to prevent
/// an adversary from stripping or modifying the class after signing.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum TransferClass {
    /// Contribution to the epistemic graph — privacy lane mandatory, no opt-out.
    Contribution,
    /// Peer-to-peer payment (bounty payout, escrow release, agent-to-agent).
    /// Defaults to privacy lane; agent may opt out to express lane with explicit consent.
    Payment { express: Option<ExpressConsent> },
}

/// ExpressConsent allows an agent to opt a `Payment` transfer out of the privacy lane
/// (jitter window) into the express lane (immediate settlement). Must be supplied
/// per-transfer and is epoch-scoped — it does not persist across epochs.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ExpressConsent {
    /// Must be `true` — agent explicitly acknowledges timing-disclosure risk.
    pub agent_acknowledged_timing_disclosure: bool,
    /// Epoch in which consent was given. Scoped per-epoch to prevent replay.
    pub consent_epoch: EpochSeq,
}

/// ECUTransfer contains the fast-path deterministic instruction to alter Owned Objects.
/// Uniquely locks on `object_ref` to enforce SafetyNoDualCert property.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ECUTransfer {
    pub object_ref: ObjectRef, // owned object mapping directly to sender agent and monotonic version
    pub to: AgentID,
    pub amount_micro_ecu: u64,
    /// Routing class — covered by `sender_sig` to prevent post-signing modification.
    pub transfer_class: TransferClass,
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
        let bytes = deserialize_fixed_bytes::<D, 96>(deserializer, "ValidatorSig")?;
        let sig = Signature::from_bytes(&bytes)
            .map_err(|e| serde::de::Error::custom(format!("blst signature parse fail: {:?}", e)))?;
        // SEC-FIX-01/SEC-AUDIT: G2 subgroup + infinity check.
        sig.validate(true)
            .map_err(|_| serde::de::Error::custom("ValidatorSig G2 validity check failed"))?;
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
    /// SHA-256 commitment to the full `SubmitEpochProposal` preimage. Phase
    /// 1586-Fix2 binds the aggregate epoch BLS signature to this field so the
    /// finalized record commits to submitter, network, epoch data hash, body
    /// hash, state root, and timing rather than only the compact epoch tuple.
    pub proposal_commitment_sha256: [u8; 32],
    /// Wall-clock lower bound (milliseconds since Unix epoch) after which this
    /// epoch is valid. Included in the BLS-signed message — prevents timestamp
    /// forgery by a colluding validator quorum.
    /// Phase 1588: timing enforcement is unconditional; no genesis field can bypass it.
    pub not_before_unix_ms: u64,
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
        let bytes = self.0.to_signature().to_bytes().to_vec();
        serializer.serialize_bytes(&bytes)
    }
}

impl<'de> serde::Deserialize<'de> for AggSig {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let bytes = deserialize_fixed_bytes::<D, 96>(deserializer, "AggSig")?;
        let sig = blst::min_pk::Signature::from_bytes(&bytes)
            .map_err(|e| serde::de::Error::custom(format!("Invalid blst signature: {:?}", e)))?;
        // SEC-FIX-01/SEC-AUDIT: G2 subgroup + infinity check — guards against
        // forged EpochCheckpoint acceptance and rejects identity points early.
        sig.validate(true)
            .map_err(|_| serde::de::Error::custom("AggSig G2 validity check failed"))?;
        Ok(AggSig(blst::min_pk::AggregateSignature::from_signature(
            &sig,
        )))
    }
}

impl PartialEq for AggSig {
    fn eq(&self, other: &Self) -> bool {
        self.0.to_signature().serialize() == other.0.to_signature().serialize()
    }
}

impl Eq for AggSig {}

/// EpochCheckpoint embeds the epoch settlement alongside an aggregate quorum signature.
///
/// HIGH-002 fix: `signers` names the subset of validators whose individual signatures
/// were aggregated into `sigs`. `process_epoch_checkpoint` verifies that:
///   - `signers.len() >= quorum_threshold(N)`
///   - all signers are in the active validator set (no unknown signers)
///   - no duplicate signer IDs are present
///   - the aggregate in `sigs` verifies against exactly the named signing subset
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct EpochCheckpoint {
    pub record: EpochSettlementRecord,
    /// Aggregate BLS signature over `record`, contributed by the validators in `signers`.
    pub sigs: AggSig,
    /// The subset of validators whose individual signatures were aggregated into `sigs`.
    pub signers: Vec<ValidatorID>,
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
    pub validators: HashMap<ValidatorID, ValidatorKey>,
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
    #[serde(default)]
    pub backward_attribution_batch_root: Option<[u8; 32]>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use bincode;
    use blst::min_pk::SecretKey;

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
    // SEC-FIX-01/SEC-AUDIT: AgentSig G2 validity check
    // ---------------------------------------------------------------------------

    #[test]
    fn test_agentsig_deserialize_valid_sig_passes() {
        let bytes = valid_agent_sig_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<AgentSig, _> = bincode::deserialize(&encoded);
        assert!(
            result.is_ok(),
            "valid AgentSig must deserialize successfully"
        );
    }

    #[test]
    fn test_agentsig_deserialize_invalid_bytes_rejected() {
        // All-zeros bytes lack the required compression flag (bit 7 of byte 0).
        // blst::Signature::from_bytes rejects this before validate() is reached.
        let bytes = g2_invalid_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<AgentSig, _> = bincode::deserialize(&encoded);
        assert!(
            result.is_err(),
            "malformed G2 bytes must be rejected by AgentSig deserialization"
        );
    }

    #[test]
    fn test_agentsig_validate_true_is_called_on_valid_path() {
        // Confirm that validate(true) passes for legitimately generated signatures.
        // Off-subgroup G2 vectors require BLS12-381-specific test data outside
        // this crate; subgroup check presence is verified by code review +
        // this regression confirming the valid path still works.
        let sk = SecretKey::key_gen(&[77u8; 32], &[]).unwrap();
        let sig = sk.sign(b"validate_test", AGENT_TRANSFER_DST, &[]);
        assert!(
            sig.validate(true).is_ok(),
            "valid sig must pass validate(true)"
        );
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-01/SEC-AUDIT: ValidatorSig G2 validity check
    // ---------------------------------------------------------------------------

    #[test]
    fn test_validatorsig_deserialize_valid_sig_passes() {
        let bytes = valid_validator_sig_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<ValidatorSig, _> = bincode::deserialize(&encoded);
        assert!(
            result.is_ok(),
            "valid ValidatorSig must deserialize successfully"
        );
    }

    #[test]
    fn test_validatorsig_deserialize_invalid_bytes_rejected() {
        let bytes = g2_invalid_bytes();
        let encoded = bincode::serialize(&bytes).unwrap();
        let result: Result<ValidatorSig, _> = bincode::deserialize(&encoded);
        assert!(
            result.is_err(),
            "malformed G2 bytes must be rejected by ValidatorSig deserialization"
        );
    }

    // ---------------------------------------------------------------------------
    // SEC-FIX-01/SEC-AUDIT: AggSig G2 validity check
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
        assert!(
            result.is_err(),
            "malformed G2 bytes must be rejected by AggSig deserialization"
        );
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
        assert!(
            pk.validate().is_ok(),
            "valid G1 public key must pass validate()"
        );
    }
}

impl ValidatorSet {
    pub fn new(
        validators: Vec<(ValidatorID, ValidatorKey)>,
        f: usize,
    ) -> Result<Self, ILCConsensusError> {
        let n = validators.len();
        if n <= 3 * f {
            return Err(ILCConsensusError::Other(format!(
                "Invalid ValidatorSet: N ({}) must be > 3F ({})",
                n,
                3 * f
            )));
        }
        // MEDIUM-006 fix: enforce that f equals the BFT-safe floor (n-1)/3.
        // ValidatorSet::new must not accept an undersafe f that would allow
        // a caller to create a set where NodeRunner quorum (2f+1) is below
        // the minimum required for Byzantine fault tolerance.
        let safe_f = n.saturating_sub(1) / 3;
        if f != safe_f {
            return Err(ILCConsensusError::Other(format!(
                "Invalid ValidatorSet: f ({}) must equal BFT floor (n-1)/3 = {} for N={}; \
                 use ValidatorSet::rebuild_with to compute f automatically",
                f, safe_f, n
            )));
        }
        let mut map: HashMap<ValidatorID, ValidatorKey> = HashMap::with_capacity(n);
        for (id, key) in validators {
            if map.contains_key(&id) {
                return Err(ILCConsensusError::Other(format!(
                    "Duplicate ValidatorID in ValidatorSet: {}",
                    id.0
                )));
            }
            // Duplicate key check: compare against all already-inserted values.
            if map.values().any(|v| v == &key) {
                return Err(ILCConsensusError::Other(
                    "Duplicate ValidatorKey in ValidatorSet".to_string(),
                ));
            }
            map.insert(id, key);
        }
        Ok(ValidatorSet { validators: map, f })
    }
}

#[cfg(test)]
mod fixed_deserialize_tests {
    use super::*;
    use bincode::Options;

    #[test]
    fn test_agent_id_deserialize_rejects_oversized_byte_vector_under_limit() {
        let payload = bincode::serialize(&vec![7u8; 49]).unwrap();
        let result: Result<AgentID, _> = bincode::DefaultOptions::new()
            .with_fixint_encoding()
            .allow_trailing_bytes()
            .with_limit(128)
            .deserialize(&payload);

        assert!(result.is_err());
    }

    #[test]
    fn test_agent_id_deserialize_obeys_bincode_read_limit() {
        let payload = bincode::serialize(&vec![7u8; 49]).unwrap();
        let result: Result<AgentID, _> = bincode::DefaultOptions::new()
            .with_fixint_encoding()
            .allow_trailing_bytes()
            .with_limit(16)
            .deserialize(&payload);

        assert!(result.is_err());
    }

    #[test]
    fn test_agent_id_deserialize_accepts_exact_fixed_bytes() {
        let payload = bincode::serialize(&vec![7u8; 48]).unwrap();
        let decoded: AgentID = bincode::DefaultOptions::new()
            .with_fixint_encoding()
            .allow_trailing_bytes()
            .with_limit(128)
            .deserialize(&payload)
            .unwrap();

        assert_eq!(decoded, AgentID([7u8; 48]));
    }
}
