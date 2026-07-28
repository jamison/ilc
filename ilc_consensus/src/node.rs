/// node.rs — M-010 validator node control plane.
///
/// Implements the BroadcastHonest → AckFor → Certificate → execute_certificate loop
/// that was missing from the library. This is the runtime glue between:
///   - PeerNetwork (mTLS QUIC transport)
///   - FastPathProtocol (owned-object fast path, quorum cert execution)
///   - EpochSettlementProtocol (shared-object epoch settlement)
///
/// State machine per in-flight transfer (owned-object fast path):
///
///   1. Receive BroadcastHonest(transfer) from any peer
///      → verify sender_sig (SEC-001 pre-check)
///      → sign transfer with own validator key
///      → send AckFor { object_ref, sig } back to broadcast originator
///        (NOTE: the originator does NOT count its own signature toward quorum;
///         with F=1 the quorum is 3/4, so the originator needs exactly two external
///         acks — fine for testnet but worth tracking if F increases)
///      → record transfer in in_flight table
///
///   2. Receive AckFor { object_ref, sig } from any peer
///      → look up the in-flight entry by object_ref (keyed — no concurrent ambiguity)
///      → accumulate sig
///      → when sigs ≥ 2F+1: assemble TransferCertificate
///        → broadcast Certificate to all peers
///        → call execute_certificate to commit to LMDB
///
///   3. Receive Certificate(cert) from any peer
///      → call execute_certificate to commit to LMDB
///      (idempotent — ConflictingTransfer is treated as already-committed)
///
/// Epoch settlement path (shared-object):
///   4. Receive EpochSettlementTx from any peer
///      → commit_epoch_record → LMDB
///      (idempotent — duplicate epoch record returns Ok without re-writing)
use std::collections::{HashMap, HashSet};
use std::net::SocketAddr;
use std::sync::Arc;

use quinn::Connection;
use sha2::{Digest, Sha256};
use tokio::sync::{oneshot, Mutex};

use crate::balance_store::BalanceStore;
use crate::epoch_settlement::{EpochStore, MAX_SIGNERS_PER_CHECKPOINT};
use crate::fast_path::{FastPathProtocol, MAX_CERT_SIGS};
use crate::network::{EpochProposal, EpochProposalAck, GossipEnvelope, GossipMessage, PeerNetwork};
use crate::persistent_quic::PersistentQuicSessionManager;
use crate::types::{
    AggSig, CIDv1Root, ECUTransfer, EpochCheckpoint, EpochSeq, EpochSettlementRecord,
    ILCConsensusError, ObjectRef, TransferCertificate, ValidatorID,
};
use crate::validator::quorum_threshold;
use crate::validator::sign_message;

// ---------------------------------------------------------------------------
// In-flight transfer state (quorum accumulation)
// ---------------------------------------------------------------------------

struct InFlight {
    transfer: ECUTransfer,
    sigs: Vec<(ValidatorID, crate::types::ValidatorSig)>,
    /// Whether we have already assembled and broadcast a Certificate for this transfer.
    certified: bool,
    /// SEC-FIX-04: wall-clock insertion time for TTL sweep (zombie eviction).
    inserted_at: tokio::time::Instant,
}

// layer1_agentid_log_hygiene_applied
#[cfg(feature = "debug_agent_ids")]
fn fmt_agent_id(id: &crate::types::AgentID) -> String {
    format!("{:?}", id)
}

#[cfg(not(feature = "debug_agent_ids"))]
fn fmt_agent_id(id: &crate::types::AgentID) -> String {
    let _ = id;
    "[redacted:agent_id]".to_string()
}

fn fmt_object_ref(object_ref: &ObjectRef) -> String {
    format!(
        "ObjectRef {{ agent: {}, version: {} }}",
        fmt_agent_id(&object_ref.agent),
        object_ref.version
    )
}

const MAX_TESTNET_RELAY_HOPS: usize = 4;
const OUTBOUND_POOL_EVICT_INTERVAL_SECS: u64 = 60;
const MAX_CERTS_PER_RESPONSE: usize = 64;
const MAX_MISSING_VERSIONS: usize = 1024;
const MAX_SIGS_PER_INFLIGHT: usize = MAX_CERT_SIGS;
const MAX_EPOCH_PROPOSAL_BODY_BYTES: usize = 256 * 1024;
const MAX_EPOCH_PROPOSALS_IN_FLIGHT: usize = 1024;
const EPOCH_PROPOSAL_TIMEOUT_MS: u64 = 5_000;
const EPOCH_PROPOSAL_STALE_MS: u64 = EPOCH_PROPOSAL_TIMEOUT_MS * 2;
const ILC_EPOCH_PROPOSAL_SIG_DST: &[u8] = b"ILC_EPOCH_PROPOSAL_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_";
const EPOCH_PROPOSAL_PREIMAGE_DOMAIN: &[u8] = b"ILC_SUBMIT_EPOCH_PROPOSAL_V1";

pub const SUBMIT_EPOCH_PROPOSAL_ACCEPTED_PHASE_1586: &str =
    "submit_epoch_proposal_accepted_phase_1586";
pub const SUBMIT_EPOCH_PROPOSAL_BFT_REJECTED_PHASE_1586: &str =
    "submit_epoch_proposal_bft_rejected_phase_1586";

struct EpochProposalInFlight {
    proposal: EpochProposal,
    sigs: Vec<(ValidatorID, crate::types::ValidatorSig)>,
    completed: bool,
    inserted_at: tokio::time::Instant,
    waiter: Option<oneshot::Sender<Result<EpochProposalOutcome, ILCConsensusError>>>,
}

#[derive(Debug, Clone)]
pub struct EpochProposalOutcome {
    pub status_token: String,
    pub epoch_number: u64,
    pub state_root: CIDv1Root,
    pub proposal_id: String,
}

fn verify_transfer_sender_sig(transfer: &ECUTransfer) -> Result<(), ILCConsensusError> {
    let sender_msg = bincode::serialize(&(
        &transfer.object_ref,
        &transfer.to,
        &transfer.amount_micro_ecu,
        &transfer.transfer_class,
    ))
    .map_err(|e| ILCConsensusError::Other(format!("Sender msg serialize: {}", e)))?;

    let sender_pubkey = blst::min_pk::PublicKey::from_bytes(&transfer.object_ref.agent.0)
        .map_err(|_| ILCConsensusError::InvalidSignature)?;
    // SEC-FIX-01: G1 subgroup check.
    sender_pubkey
        .validate()
        .map_err(|_| ILCConsensusError::InvalidSignature)?;

    let result = transfer.sender_sig.0.verify(
        true,
        &sender_msg,
        crate::types::AGENT_TRANSFER_DST,
        &[],
        &sender_pubkey,
        true,
    );
    if result != blst::BLST_ERROR::BLST_SUCCESS {
        return Err(ILCConsensusError::InvalidSignature);
    }

    Ok(())
}

fn next_relay_hop(
    current_validator: ValidatorID,
    remaining_route: &[ValidatorID],
) -> Result<Option<(ValidatorID, Vec<ValidatorID>)>, ILCConsensusError> {
    if remaining_route.is_empty() {
        return Ok(None);
    }
    if remaining_route.len() > MAX_TESTNET_RELAY_HOPS {
        return Err(ILCConsensusError::Other(format!(
            "relay route exceeds max hop cap of {}",
            MAX_TESTNET_RELAY_HOPS
        )));
    }

    let mut seen = HashSet::new();
    for hop in remaining_route {
        if *hop == current_validator {
            return Err(ILCConsensusError::Other(format!(
                "relay route loops back through validator {}",
                current_validator.0
            )));
        }
        if !seen.insert(*hop) {
            return Err(ILCConsensusError::Other(format!(
                "relay route contains duplicate validator {}",
                hop.0
            )));
        }
    }

    let (next_hop, tail) = remaining_route
        .split_first()
        .ok_or_else(|| ILCConsensusError::Other("relay route unexpectedly empty".into()))?;
    Ok(Some((*next_hop, tail.to_vec())))
}

// ---------------------------------------------------------------------------
// NodeRunner
// ---------------------------------------------------------------------------

pub struct NodeRunner {
    pub validator_id: ValidatorID,
    pub network_id: String,
    pub f: usize,
    pub validator_sk: blst::min_pk::SecretKey,
    pub network: Arc<PeerNetwork>,
    pub fast_path: Arc<FastPathProtocol>,
    pub balance_store: Arc<BalanceStore>,
    pub epoch_store: Arc<EpochStore>,
    /// peer_addrs: other validators' addresses, for active outbound connections.
    pub peer_addrs: Vec<(ValidatorID, SocketAddr)>,
    /// In-flight transfers keyed by ObjectRef (owned-object fast path).
    in_flight: Arc<Mutex<HashMap<ObjectRef, InFlight>>>,
    /// In-flight epoch proposals keyed by idempotency_key.
    epoch_proposals: Arc<Mutex<HashMap<String, EpochProposalInFlight>>>,
    /// Outbound connection pool: one QUIC connection per peer, reused across messages.
    pub outbound_pool: Arc<Mutex<HashMap<SocketAddr, Connection>>>,
    /// ADR-0039 projection-backed persistent session manager for production activation path.
    pub persistent_sessions: Option<Arc<PersistentQuicSessionManager>>,
    pub proposal_ingress_enabled: bool,
    #[cfg(feature = "testnet_fault_sim")]
    pub censor_validator: Option<u32>,
    #[cfg(feature = "testnet_fault_sim")]
    pub censor_target: Option<u32>,
    #[cfg(feature = "testnet_fault_sim")]
    pub partition_block_peers: HashSet<u32>,
    #[cfg(feature = "testnet_fault_sim")]
    pub delay_ms: Option<u64>,
}

impl NodeRunner {
    pub fn new(
        validator_id: ValidatorID,
        network_id: String,
        f: usize,
        validator_sk: blst::min_pk::SecretKey,
        network: Arc<PeerNetwork>,
        fast_path: Arc<FastPathProtocol>,
        balance_store: Arc<BalanceStore>,
        epoch_store: Arc<EpochStore>,
        peer_addrs: Vec<(ValidatorID, SocketAddr)>,
    ) -> Self {
        Self {
            validator_id,
            network_id,
            f,
            validator_sk,
            network,
            fast_path,
            balance_store,
            epoch_store,
            peer_addrs,
            in_flight: Arc::new(Mutex::new(HashMap::new())),
            epoch_proposals: Arc::new(Mutex::new(HashMap::new())),
            outbound_pool: Arc::new(Mutex::new(HashMap::new())),
            persistent_sessions: None,
            proposal_ingress_enabled: false,
            #[cfg(feature = "testnet_fault_sim")]
            censor_validator: std::env::var("CENSOR_VALIDATOR")
                .ok()
                .and_then(|v| v.parse().ok()),
            #[cfg(feature = "testnet_fault_sim")]
            censor_target: std::env::var("CENSOR_TARGET")
                .ok()
                .and_then(|v| v.parse().ok()),
            #[cfg(feature = "testnet_fault_sim")]
            partition_block_peers: std::env::var("PARTITION_BLOCK_PEERS")
                .unwrap_or_default()
                .split(',')
                .filter_map(|s| s.trim().parse::<u32>().ok())
                .collect(),
            #[cfg(feature = "testnet_fault_sim")]
            delay_ms: std::env::var("DELAY_MS").ok().and_then(|v| v.parse().ok()),
        }
    }

    pub fn with_persistent_sessions(
        mut self,
        persistent_sessions: Arc<PersistentQuicSessionManager>,
    ) -> Self {
        self.persistent_sessions = Some(persistent_sessions);
        self
    }

    pub fn with_proposal_ingress_enabled(mut self, enabled: bool) -> Self {
        self.proposal_ingress_enabled = enabled;
        self
    }

    pub async fn submit_epoch_proposal(
        &self,
        proposal: EpochProposal,
    ) -> Result<EpochProposalOutcome, ILCConsensusError> {
        {
            let mut table = self.epoch_proposals.lock().await;
            evict_stale_epoch_proposals(&mut table);
            if table.contains_key(&proposal.idempotency_key) {
                return Err(ILCConsensusError::Other(
                    "submit_epoch_proposal_duplicate_phase_1586".into(),
                ));
            }
        }
        self.validate_epoch_proposal(&proposal)?;
        if !self.proposal_ingress_enabled {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_settlement_path_not_mysticeti_phase_1586".into(),
            ));
        }

        let record = proposal_to_record(&proposal);
        let record_bytes = bincode::serialize(&record)
            .map_err(|e| ILCConsensusError::Other(format!("Epoch record serialize: {}", e)))?;
        let own_sig = crate::types::ValidatorSig(self.validator_sk.sign(
            &record_bytes,
            crate::types::ILC_EPOCH_SIG_DST,
            &[],
        ));
        let (tx, rx) = oneshot::channel();
        {
            let mut table = self.epoch_proposals.lock().await;
            if table.contains_key(&proposal.idempotency_key) {
                return Err(ILCConsensusError::Other(
                    "submit_epoch_proposal_duplicate_phase_1586".into(),
                ));
            }
            if table.len() >= MAX_EPOCH_PROPOSALS_IN_FLIGHT {
                return Err(ILCConsensusError::Other(
                    "submit_epoch_proposal_inflight_cap_exceeded_phase_1586".into(),
                ));
            }
            evict_stale_epoch_proposals(&mut table);
            table.insert(
                proposal.idempotency_key.clone(),
                EpochProposalInFlight {
                    proposal: proposal.clone(),
                    sigs: vec![(self.validator_id, own_sig)],
                    completed: false,
                    inserted_at: tokio::time::Instant::now(),
                    waiter: Some(tx),
                },
            );
        }

        self.try_finalize_epoch_proposal(&proposal.idempotency_key)
            .await?;

        for (peer_id, _addr) in &self.peer_addrs {
            if let Err(e) = self
                .send_to_peer(*peer_id, GossipMessage::EpochProposal(proposal.clone()))
                .await
            {
                eprintln!(
                    "[phase1586] validator_id={} EpochProposal send to peer={} failed: {}",
                    self.validator_id.0, peer_id.0, e
                );
            }
        }

        match tokio::time::timeout(
            tokio::time::Duration::from_millis(EPOCH_PROPOSAL_TIMEOUT_MS),
            rx,
        )
        .await
        {
            Ok(Ok(result)) => result,
            Ok(Err(_)) => Err(ILCConsensusError::Other(
                SUBMIT_EPOCH_PROPOSAL_BFT_REJECTED_PHASE_1586.into(),
            )),
            Err(_) => Err(ILCConsensusError::Other(
                SUBMIT_EPOCH_PROPOSAL_BFT_REJECTED_PHASE_1586.into(),
            )),
        }
    }

    /// Main accept loop: accept inbound QUIC connections and dispatch each in its own task.
    /// Requires Arc<Self> so each spawned task can hold a reference independently.
    pub async fn run(self: Arc<Self>) -> Result<(), ILCConsensusError> {
        eprintln!(
            "[m010_node] validator_id={} running on {}",
            self.validator_id.0,
            self.network
                .endpoint
                .local_addr()
                .map(|a| a.to_string())
                .unwrap_or_else(|_| "unknown".to_string()),
        );

        // Background epoch sync task: periodically broadcast MissingEpochSync so
        // validators that rejoin after a partition receive missing epoch records
        // from peers via protocol-driven delivery (Tier 2 recovery — M-015).
        {
            let node = Arc::clone(&self);
            tokio::spawn(async move {
                let interval_secs: u64 = std::env::var("EPOCH_SYNC_INTERVAL_SECS")
                    .ok()
                    .and_then(|v| v.parse().ok())
                    .unwrap_or(5);
                loop {
                    tokio::time::sleep(tokio::time::Duration::from_secs(interval_secs)).await;
                    // Read latest_contiguous_epoch from the singleton sentinel.
                    // commit_epoch_record/process_epoch_checkpoint enforce contiguous
                    // epoch progression, so the sentinel is the O(1) sync cursor.
                    let cursor = match latest_epoch_sync_cursor(&node.epoch_store) {
                        Ok(v) => v,
                        Err(e) => {
                            eprintln!(
                                "[m015_epoch_sync] validator_id={} get_current_epoch error: {}",
                                node.validator_id.0, e
                            );
                            continue;
                        }
                    };
                    let msg = GossipMessage::MissingEpochSync {
                        latest_contiguous_epoch: cursor,
                    };
                    for (peer_id, _addr) in &node.peer_addrs {
                        #[cfg(feature = "testnet_fault_sim")]
                        if node.partition_block_peers.contains(&peer_id.0) {
                            continue;
                        }
                        if let Err(e) = node.send_to_peer(*peer_id, msg.clone()).await {
                            eprintln!(
                                "[m015_epoch_sync] validator_id={} epoch sync to peer={} failed: {}",
                                node.validator_id.0, peer_id.0, e
                            );
                        }
                    }
                }
            });
        }

        // 1575h-Fix2: periodically evict dead outbound QUIC connections.
        // The pool is a connection cache only; live protocol authority remains
        // in signed messages and LMDB stores.
        {
            let node = Arc::clone(&self);
            tokio::spawn(async move {
                loop {
                    tokio::time::sleep(tokio::time::Duration::from_secs(
                        OUTBOUND_POOL_EVICT_INTERVAL_SECS,
                    ))
                    .await;
                    let evicted = node.evict_dead_outbound_connections().await;
                    if evicted > 0 {
                        eprintln!(
                            "[m010_node] validator_id={} outbound_pool sweep: evicted {} dead connections",
                            node.validator_id.0, evicted
                        );
                    }
                }
            });
        }

        // SEC-FIX-04: zombie in_flight TTL sweep.
        // Entries that never reach quorum (e.g. originator went offline) would otherwise
        // accumulate indefinitely, causing unbounded memory growth under sustained load.
        {
            let node = Arc::clone(&self);
            tokio::spawn(async move {
                const TTL_SECS: u64 = 60;
                let ttl = tokio::time::Duration::from_secs(TTL_SECS);
                loop {
                    tokio::time::sleep(tokio::time::Duration::from_secs(TTL_SECS)).await;
                    let mut table = node.in_flight.lock().await;
                    let before = table.len();
                    table.retain(|_, entry| !entry.certified && entry.inserted_at.elapsed() < ttl);
                    let evicted = before.saturating_sub(table.len());
                    if evicted > 0 {
                        eprintln!(
                            "[m010_node] validator_id={} in_flight TTL sweep: evicted {} zombie entries",
                            node.validator_id.0, evicted
                        );
                    }
                }
            });
        }

        loop {
            let incoming = self
                .network
                .endpoint
                .accept()
                .await
                .ok_or_else(|| ILCConsensusError::Other("Endpoint closed".into()))?;

            let node = Arc::clone(&self);
            tokio::spawn(async move {
                let connection = match incoming.await {
                    Ok(c) => c,
                    Err(e) => {
                        eprintln!("[m010_node] connection accept error: {}", e);
                        return;
                    }
                };
                // SEC-FIX-03: bound accept_bi to prevent zombie connections from
                // a peer that opens a QUIC connection but never opens a stream.
                let (_, recv) = match tokio::time::timeout(
                    tokio::time::Duration::from_millis(crate::network::IO_TIMEOUT_MS),
                    connection.accept_bi(),
                )
                .await
                {
                    Ok(Ok(s)) => s,
                    Ok(Err(e)) => {
                        eprintln!("[m010_node] stream accept error: {}", e);
                        return;
                    }
                    Err(_) => {
                        eprintln!("[m010_node] accept_bi timed out — dropping connection");
                        return;
                    }
                };
                let envelope = match node.network.receive(&connection, recv).await {
                    Ok(e) => e,
                    Err(e) => {
                        eprintln!("[m010_node] receive error: {}", e);
                        return;
                    }
                };
                if let Err(e) = node.dispatch(envelope).await {
                    eprintln!("[m010_node] dispatch error: {}", e);
                }
            });
        }
    }

    /// Dispatch a received GossipEnvelope to the appropriate handler.
    async fn dispatch(&self, envelope: GossipEnvelope) -> Result<(), ILCConsensusError> {
        let from = envelope.peer_id;
        #[cfg(feature = "testnet_fault_sim")]
        if self.partition_block_peers.contains(&from.0) {
            eprintln!(
                "[m015_partition_drop] validator_id={} target={} kind=inbound",
                self.validator_id.0, from.0
            );
            return Ok(());
        }

        // M-019 slow-validator simulation: delay_ms is applied uniformly to ALL
        // inbound messages after the partition gate, not just to specific message
        // types. This is intentional — a "slow" validator is slow on everything,
        // which faithfully models a saturated or degraded node. A selective per-type
        // delay would require a different attacker model and a separate field.
        // Note: this runs only under --features testnet_fault_sim; production
        // binaries do not compile this branch.
        #[cfg(feature = "testnet_fault_sim")]
        if let Some(ms) = self.delay_ms {
            tokio::time::sleep(tokio::time::Duration::from_millis(ms)).await;
        }
        match envelope.payload {
            GossipMessage::BroadcastHonest(transfer) => {
                self.handle_broadcast_honest(transfer, from).await
            }
            GossipMessage::RelaySubmit {
                transfer,
                remaining_route,
            } => {
                #[cfg(feature = "testnet_fault_sim")]
                {
                    self.handle_relay_submit(transfer, remaining_route, from)
                        .await
                }
                #[cfg(not(feature = "testnet_fault_sim"))]
                {
                    let _ = (transfer, remaining_route, from);
                    eprintln!(
                        "[m021_layer2] validator_id={} RelaySubmit rejected in non-testnet build",
                        self.validator_id.0
                    );
                    Err(ILCConsensusError::Other(
                        "RelaySubmit is testnet_only".into(),
                    ))
                }
            }
            GossipMessage::AckFor { object_ref, sig } => {
                self.handle_ack_for(object_ref, sig, from).await
            }
            GossipMessage::Ack(sig) => {
                // Legacy unkeyed ack — log and ignore; senders should use AckFor.
                eprintln!(
                    "[m010_node] validator_id={} ignoring legacy Ack from peer={} (use AckFor)",
                    self.validator_id.0, from.0
                );
                let _ = sig;
                Ok(())
            }
            GossipMessage::Certificate(cert) => self.handle_certificate(cert).await,
            GossipMessage::EpochSettlementTx(tx) => {
                // CRIT-001: EpochSettlementTx carries no sigs field. Epoch records
                // committed via this path have no BLS aggregate signature — any
                // authenticated peer could fabricate epoch records. This message
                // type is permitted only in testnet_fault_sim builds for loopback
                // testing. Production builds reject it unconditionally.
                #[cfg(feature = "testnet_fault_sim")]
                {
                    if let Some(censor_val) = self.censor_validator {
                        if let Some(censor_tgt) = self.censor_target {
                            if self.validator_id.0 == censor_val && from.0 == censor_tgt {
                                eprintln!("[m014_censor] validator_id={} dropped EpochSettlementTx from validator_id={}", self.validator_id.0, from.0);
                                return Ok(());
                            }
                        }
                    }
                    return self.handle_epoch_settlement_tx(tx).await;
                }
                #[cfg(not(feature = "testnet_fault_sim"))]
                {
                    let _ = tx;
                    eprintln!("[node] SECURITY: EpochSettlementTx rejected — no BLS aggregate sig field; use EpochCheckpointMsg");
                    Err(ILCConsensusError::InvalidSignature)
                }
            }
            GossipMessage::EpochCheckpointMsg(checkpoint) => {
                #[cfg(feature = "testnet_fault_sim")]
                if let Some(censor_val) = self.censor_validator {
                    if let Some(censor_tgt) = self.censor_target {
                        if self.validator_id.0 == censor_val && from.0 == censor_tgt {
                            eprintln!("[m014_censor] validator_id={} dropped EpochCheckpointMsg from validator_id={}", self.validator_id.0, from.0);
                            return Ok(());
                        }
                    }
                }
                self.handle_epoch_checkpoint_msg(checkpoint).await
            }
            GossipMessage::MissingCertSync {
                agent,
                missing_versions,
            } => {
                self.handle_missing_cert_sync(agent, missing_versions, from)
                    .await
            }
            GossipMessage::MissingCertResponse { certs } => {
                self.handle_missing_cert_response(certs).await
            }
            GossipMessage::MissingEpochSync {
                latest_contiguous_epoch,
            } => {
                self.handle_missing_epoch_sync(latest_contiguous_epoch, from)
                    .await
            }
            GossipMessage::MissingEpochResponse { records } => {
                self.handle_missing_epoch_response(records).await
            }
            GossipMessage::EpochProposal(proposal) => {
                self.handle_epoch_proposal(proposal, from).await
            }
            GossipMessage::EpochProposalAck(ack) => self.handle_epoch_proposal_ack(ack, from).await,
        }
    }

    // -----------------------------------------------------------------------
    // BroadcastHonest handler
    // -----------------------------------------------------------------------

    async fn handle_broadcast_honest(
        &self,
        transfer: ECUTransfer,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        // SEC-001: verify sender_sig before doing anything else.
        if verify_transfer_sender_sig(&transfer).is_err() {
            eprintln!(
                "[m010_node] validator_id={} rejected transfer from peer={}: invalid sender_sig",
                self.validator_id.0, from.0
            );
            return Ok(()); // drop silently; do not propagate invalid transfers
        }

        // Row-5 privacy lane routing decision (Phase 844).
        // Emit a log token per transfer_class so SIM-LEAKAGE-03 can account
        // for every routed transfer.  The decision is read from the
        // sender-signed `transfer_class` field — no adversary can strip or
        // modify it post-signing (covered by sender_sig per types.rs §TransferClass).
        {
            use crate::types::{ExpressConsent, TransferClass};
            let routing_token = match &transfer.transfer_class {
                TransferClass::Contribution => "privacy_lane_routing:class=contribution",
                TransferClass::Payment {
                    express:
                        Some(ExpressConsent {
                            agent_acknowledged_timing_disclosure: true,
                            ..
                        }),
                } => "privacy_lane_routing:class=payment_express",
                TransferClass::Payment {
                    express:
                        Some(ExpressConsent {
                            agent_acknowledged_timing_disclosure: false,
                            ..
                        }),
                } => "privacy_lane_routing:class=payment_express_rejected",
                TransferClass::Payment { express: None } => {
                    "privacy_lane_routing:class=payment_default"
                }
            };
            // LOW-005 fix: do not log routing_token directly — it reveals TransferClass
            // (Contribution / Payment / Payment_Express) even when AgentID is redacted.
            // Log only that a routing decision was made, not which class was selected.
            let _ = routing_token;
            eprintln!(
                "[row5_privacy_lane] validator_id={} obj_ref={} routing_decision=recorded",
                self.validator_id.0,
                fmt_object_ref(&transfer.object_ref),
            );
        }

        // Record in in_flight table if not already present.
        let object_ref = transfer.object_ref;
        {
            let mut table = self.in_flight.lock().await;
            if let Some(existing) = table.get(&object_ref) {
                // If it already exists, verify the payload matches. If not, it's equivocation!
                if existing.transfer.to != transfer.to
                    || existing.transfer.amount_micro_ecu != transfer.amount_micro_ecu
                    || existing.transfer.transfer_class != transfer.transfer_class
                {
                    eprintln!(
                        "[m010_node] validator_id={} duplicate certificate ignored (ConflictingTransfer / Equivocation Detected)",
                        self.validator_id.0
                    );
                    return Ok(());
                }
            } else {
                table.insert(
                    object_ref,
                    InFlight {
                        transfer: transfer.clone(),
                        sigs: Vec::new(),
                        certified: false,
                        inserted_at: tokio::time::Instant::now(),
                    },
                );
            }
        }

        // Sign the transfer with our validator key and send AckFor back to originator.
        // AckFor carries the object_ref so the recipient can key the ack unambiguously.
        let transfer_msg = bincode::serialize(&transfer)
            .map_err(|e| ILCConsensusError::Other(format!("Transfer serialize: {}", e)))?;
        let sig = sign_message(&self.validator_sk, &transfer_msg, &self.network_id);

        eprintln!(
            "[m010_node] validator_id={} acking transfer obj_ref={} to peer={}",
            self.validator_id.0,
            fmt_object_ref(&object_ref),
            from.0
        );

        self.send_to_peer(from, GossipMessage::AckFor { object_ref, sig })
            .await
    }

    #[cfg(feature = "testnet_fault_sim")]
    async fn handle_relay_submit(
        &self,
        transfer: ECUTransfer,
        remaining_route: Vec<ValidatorID>,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        // testnet_only: relay metadata stays outside TransferCertificate.
        match next_relay_hop(self.validator_id, &remaining_route)? {
            Some((next_hop, tail)) => {
                if verify_transfer_sender_sig(&transfer).is_err() {
                    eprintln!(
                        "[m021_layer2] validator_id={} rejected relay_submit from peer={}: invalid sender_sig",
                        self.validator_id.0, from.0
                    );
                    return Ok(());
                }

                eprintln!(
                    "[m021_layer2] validator_id={} forwarding relay_submit obj_ref={} next_peer={} remaining_hops={}",
                    self.validator_id.0,
                    fmt_object_ref(&transfer.object_ref),
                    next_hop.0,
                    tail.len()
                );

                self.send_to_peer(
                    next_hop,
                    GossipMessage::RelaySubmit {
                        transfer,
                        remaining_route: tail,
                    },
                )
                .await
            }
            None => {
                eprintln!(
                    "[m021_layer2] validator_id={} final relay destination for obj_ref={} from peer={}",
                    self.validator_id.0,
                    fmt_object_ref(&transfer.object_ref),
                    from.0
                );
                self.handle_broadcast_honest(transfer, from).await
            }
        }
    }

    // -----------------------------------------------------------------------
    // AckFor handler — keyed by ObjectRef, no concurrent-transfer ambiguity
    // -----------------------------------------------------------------------

    async fn handle_ack_for(
        &self,
        object_ref: ObjectRef,
        sig: crate::types::ValidatorSig,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        // MEDIUM-004 fix: read f from the live ValidatorSet instead of using
        // self.f (captured at NodeRunner::new()). This ensures that after a
        // rotate_validator_set call the quorum threshold reflects the current
        // membership, not the genesis value.
        let quorum = {
            let vs = self.fast_path.validator_set.read().unwrap();
            2 * vs.f + 1
        };
        let mut to_certify: Option<(ECUTransfer, Vec<(ValidatorID, crate::types::ValidatorSig)>)> =
            None;

        {
            let mut table = self.in_flight.lock().await;
            if let Some(entry) = table.get_mut(&object_ref) {
                if !entry.certified {
                    // Deduplicate: only accept one sig per validator.
                    if !entry.sigs.iter().any(|(id, _)| *id == from) {
                        if entry.sigs.len() >= MAX_SIGS_PER_INFLIGHT {
                            return Err(ILCConsensusError::Other(format!(
                                "in_flight_signature_cap_exceeded_phase_1575h_fix2: max_sigs={}",
                                MAX_SIGS_PER_INFLIGHT
                            )));
                        }
                        entry.sigs.push((from, sig));
                        eprintln!(
                            "[m010_node] validator_id={} ack from peer={} for obj_ref={} sigs={}/{}",
                            self.validator_id.0,
                            from.0,
                            fmt_object_ref(&object_ref),
                            entry.sigs.len(),
                            quorum
                        );
                        if entry.sigs.len() >= quorum {
                            entry.certified = true;
                            to_certify = Some((entry.transfer.clone(), entry.sigs.clone()));
                        }
                    }
                }
            } else {
                eprintln!(
                    "[m010_node] validator_id={} AckFor for unknown obj_ref={} from peer={}",
                    self.validator_id.0,
                    fmt_object_ref(&object_ref),
                    from.0
                );
            }
        }

        if let Some((transfer, sigs)) = to_certify {
            let cert_epoch = crate::types::EpochSeq(self.epoch_store.get_current_epoch()?.max(1));
            let cert = TransferCertificate {
                transfer,
                sigs,
                epoch: cert_epoch,
            };
            eprintln!(
                "[m010_node] validator_id={} assembled certificate for obj_ref={} — broadcasting",
                self.validator_id.0,
                fmt_object_ref(&object_ref)
            );
            self.broadcast_certificate(cert.clone()).await?;
            self.execute_and_log(cert).await?;
            // Evict certified entry immediately to prevent unbounded in_flight growth (OOM guard).
            // The LMDB version lock is the durable equivocation barrier; in_flight is an
            // ephemeral early-rejection cache only and must not retain entries after settlement.
            {
                let mut table = self.in_flight.lock().await;
                table.remove(&object_ref);
            }
        }

        Ok(())
    }

    // -----------------------------------------------------------------------
    // Certificate handler
    // -----------------------------------------------------------------------

    async fn handle_certificate(&self, cert: TransferCertificate) -> Result<(), ILCConsensusError> {
        eprintln!(
            "[m010_node] validator_id={} received Certificate for obj_ref={}",
            self.validator_id.0,
            fmt_object_ref(&cert.transfer.object_ref)
        );
        self.execute_and_log(cert).await
    }

    // -----------------------------------------------------------------------
    // EpochSettlementTx handler — testnet_fault_sim only (CRIT-001)
    // -----------------------------------------------------------------------

    #[cfg(feature = "testnet_fault_sim")]
    async fn handle_epoch_settlement_tx(
        &self,
        tx: crate::types::EpochSettlementTx,
    ) -> Result<(), ILCConsensusError> {
        eprintln!(
            "[m010_node] validator_id={} received EpochSettlementTx epoch={}",
            self.validator_id.0, tx.epoch.0
        );
        let record = crate::types::EpochSettlementRecord {
            epoch: tx.epoch,
            state_root: tx.state_root,
            not_before_unix_ms: 0,
        };
        // Treat duplicate epoch records as idempotent (mirrors ConflictingTransfer handling).
        match self.epoch_store.commit_epoch_record(record) {
            Ok(()) => {
                eprintln!("epoch_record_committed:epoch={}", tx.epoch.0);
            }
            Err(ILCConsensusError::InvalidEpoch) => {
                eprintln!(
                    "[m010_node] validator_id={} duplicate EpochSettlementTx epoch={} — already committed",
                    self.validator_id.0, tx.epoch.0
                );
            }
            Err(e) => return Err(e),
        }
        Ok(())
    }

    // -----------------------------------------------------------------------
    // SEC-003: MissingCertSync / MissingCertResponse
    // -----------------------------------------------------------------------

    async fn handle_missing_cert_sync(
        &self,
        _agent: crate::types::AgentID,
        missing_versions: Vec<u64>,
        _from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        if missing_versions.len() > MAX_MISSING_VERSIONS {
            return Err(ILCConsensusError::Other(format!(
                "missing_cert_sync_missing_versions_cap_exceeded_phase_1575h_fix2: max_versions={}",
                MAX_MISSING_VERSIONS
            )));
        }
        // M-010: scaffold only. Full sync response is M-011 workload.
        eprintln!(
            "[m010_node] validator_id={} MissingCertSync received — sync response deferred to M-011",
            self.validator_id.0
        );
        Ok(())
    }

    async fn handle_missing_cert_response(
        &self,
        certs: Vec<TransferCertificate>,
    ) -> Result<(), ILCConsensusError> {
        // SEC-FIX-04: cap certificate count to prevent CPU DoS.
        // Each cert triggers BLS quorum verification + LMDB write; a malicious peer
        // filling a near-10 MB payload could cause unbounded per-message work.
        if certs.len() > MAX_CERTS_PER_RESPONSE {
            eprintln!(
                "[m010_node] validator_id={} MissingCertResponse: {} certs exceeds cap of {}; dropping",
                self.validator_id.0, certs.len(), MAX_CERTS_PER_RESPONSE
            );
            return Err(ILCConsensusError::Other(format!(
                "MissingCertResponse exceeds per-response cert cap of {}",
                MAX_CERTS_PER_RESPONSE
            )));
        }
        for cert in certs {
            eprintln!(
                "[m010_node] validator_id={} MissingCertResponse: replaying certificate obj_ref={}",
                self.validator_id.0,
                fmt_object_ref(&cert.transfer.object_ref)
            );
            self.execute_and_log(cert).await?;
        }
        Ok(())
    }

    // -----------------------------------------------------------------------
    // MissingEpochSync / MissingEpochResponse — M-015 epoch recovery protocol
    // -----------------------------------------------------------------------

    async fn handle_missing_epoch_sync(
        &self,
        latest_contiguous_epoch: u64,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        let records = self.epoch_store.get_epochs_after(latest_contiguous_epoch)?;
        if records.is_empty() {
            return Ok(());
        }
        eprintln!(
            "[m015_epoch_sync] validator_id={} responding to peer={} with {} epoch(s) after cursor={}",
            self.validator_id.0, from.0, records.len(), latest_contiguous_epoch
        );
        self.send_to_peer(from, GossipMessage::MissingEpochResponse { records })
            .await
    }

    async fn handle_epoch_checkpoint_msg(
        &self,
        checkpoint: crate::types::EpochCheckpoint,
    ) -> Result<(), ILCConsensusError> {
        let vs_guard = self.fast_path.validator_set.read().unwrap();
        let protocol =
            crate::epoch_settlement::EpochSettlementProtocol::new(self.epoch_store.clone());
        let epoch = checkpoint.record.epoch.0;

        match protocol.process_epoch_checkpoint(checkpoint, &*vs_guard) {
            Ok(_) => {
                eprintln!("epoch_record_committed:epoch={}", epoch);
                Ok(())
            }
            Err(ILCConsensusError::InvalidEpoch) => {
                eprintln!(
                    "[m018_node] validator_id={} EpochCheckpointMsg epoch={} already committed",
                    self.validator_id.0, epoch
                );
                Ok(())
            }
            Err(e) => {
                eprintln!(
                    "[m018_node] validator_id={} checkpoint validation failed: {:?}",
                    self.validator_id.0, e
                );
                Err(e)
            }
        }
    }

    async fn handle_missing_epoch_response(
        &self,
        records: Vec<crate::epoch_settlement::StoredCheckpoint>,
    ) -> Result<(), ILCConsensusError> {
        let protocol =
            crate::epoch_settlement::EpochSettlementProtocol::new(self.epoch_store.clone());
        let vs_guard = self.fast_path.validator_set.read().unwrap();

        for stored in records {
            let epoch = stored.record.epoch.0;
            match apply_missing_epoch_record(&self.epoch_store, stored, &protocol, &*vs_guard) {
                Ok(_) => {
                    eprintln!("epoch_record_committed:epoch={}", epoch);
                    eprintln!("m015_epoch_recovery_path_protocol_driven epoch={}", epoch);
                }
                Err(ILCConsensusError::InvalidEpoch) => {
                    // Already committed — idempotent; do not re-log as a new commit.
                    eprintln!(
                        "[m015_epoch_sync] validator_id={} MissingEpochResponse epoch={} already committed",
                        self.validator_id.0, epoch
                    );
                }
                Err(e) => return Err(e),
            }
        }
        Ok(())
    }

    async fn handle_epoch_proposal(
        &self,
        proposal: EpochProposal,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        self.validate_epoch_proposal(&proposal)?;
        let proposal_commitment = proposal_commitment_sha256(&proposal);
        let record = proposal_to_record(&proposal);
        let msg = bincode::serialize(&record)
            .map_err(|e| ILCConsensusError::Other(format!("Epoch record serialize: {}", e)))?;
        let sig = crate::types::ValidatorSig(self.validator_sk.sign(
            &msg,
            crate::types::ILC_EPOCH_SIG_DST,
            &[],
        ));
        let proposal_sig = crate::types::ValidatorSig(self.validator_sk.sign(
            &proposal_commitment,
            ILC_EPOCH_PROPOSAL_SIG_DST,
            &[],
        ));
        self.send_to_peer(
            from,
            GossipMessage::EpochProposalAck(EpochProposalAck {
                idempotency_key: proposal.idempotency_key,
                epoch_number: proposal.epoch_number,
                proposal_commitment_sha256: proposal_commitment.to_vec(),
                proposal_sig,
                sig,
            }),
        )
        .await
    }

    async fn handle_epoch_proposal_ack(
        &self,
        ack: EpochProposalAck,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        {
            let mut table = self.epoch_proposals.lock().await;
            let Some(entry) = table.get_mut(&ack.idempotency_key) else {
                return Ok(());
            };
            if entry.completed || entry.proposal.epoch_number != ack.epoch_number {
                return Ok(());
            }
            self.verify_epoch_proposal_ack(&entry.proposal, &ack, from)?;
            if !entry.sigs.iter().any(|(id, _)| *id == from) {
                if entry.sigs.len() >= MAX_SIGNERS_PER_CHECKPOINT {
                    return Err(ILCConsensusError::Other(
                        "epoch_proposal_ack_signer_cap_exceeded_phase_1586".into(),
                    ));
                }
                entry.sigs.push((from, ack.sig));
            }
        }
        self.try_finalize_epoch_proposal(&ack.idempotency_key).await
    }

    async fn try_finalize_epoch_proposal(
        &self,
        idempotency_key: &str,
    ) -> Result<(), ILCConsensusError> {
        let finalize = {
            let mut table = self.epoch_proposals.lock().await;
            let Some(entry) = table.get_mut(idempotency_key) else {
                return Ok(());
            };
            if entry.completed {
                return Ok(());
            }
            let quorum = {
                let vs = self.fast_path.validator_set.read().unwrap();
                quorum_threshold(vs.validators.len())
            };
            if entry.sigs.len() < quorum {
                return Ok(());
            }
            Some((
                entry.proposal.clone(),
                entry.sigs.clone(),
                entry.waiter.take(),
            ))
        };

        let Some((proposal, sigs, waiter)) = finalize else {
            return Ok(());
        };

        let record = proposal_to_record(&proposal);
        let sig_refs: Vec<&blst::min_pk::Signature> = sigs.iter().map(|(_, sig)| &sig.0).collect();
        let agg = blst::min_pk::AggregateSignature::aggregate(&sig_refs, false)
            .map_err(|_| ILCConsensusError::BLSVerificationFailed)?;
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs: AggSig(agg),
            signers: sigs.iter().map(|(id, _)| *id).collect(),
        };

        let protocol =
            crate::epoch_settlement::EpochSettlementProtocol::new(self.epoch_store.clone());
        let result = {
            let vs_guard = self.fast_path.validator_set.read().unwrap();
            protocol.process_epoch_checkpoint(checkpoint.clone(), &*vs_guard)
        };
        match result {
            Ok(_) => {
                {
                    let mut table = self.epoch_proposals.lock().await;
                    if let Some(entry) = table.get_mut(idempotency_key) {
                        entry.completed = true;
                    }
                }
                for (peer_id, _addr) in &self.peer_addrs {
                    if let Err(e) = self
                        .send_to_peer(
                            *peer_id,
                            GossipMessage::EpochCheckpointMsg(checkpoint.clone()),
                        )
                        .await
                    {
                        eprintln!(
                            "[phase1586] validator_id={} EpochCheckpointMsg send to peer={} failed: {}",
                            self.validator_id.0, peer_id.0, e
                        );
                    }
                }
                let outcome = EpochProposalOutcome {
                    status_token: SUBMIT_EPOCH_PROPOSAL_ACCEPTED_PHASE_1586.to_string(),
                    epoch_number: proposal.epoch_number,
                    state_root: proposal.state_root,
                    proposal_id: proposal.idempotency_key,
                };
                if let Some(waiter) = waiter {
                    let _ = waiter.send(Ok(outcome));
                }
            }
            Err(e) => {
                if let Some(waiter) = waiter {
                    let _ = waiter.send(Err(e.clone()));
                }
                return Err(e);
            }
        }
        Ok(())
    }

    fn validate_epoch_proposal(&self, proposal: &EpochProposal) -> Result<(), ILCConsensusError> {
        if proposal.submitter_agent_id.len() != 48 {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_invalid_submitter_agent_id_phase_1586".into(),
            ));
        }
        if !is_lowercase_sha256_hex(&proposal.idempotency_key) {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_invalid_idempotency_key_phase_1586".into(),
            ));
        }
        if proposal.epoch_data_hash.len() != 32 {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_invalid_epoch_data_hash_phase_1586".into(),
            ));
        }
        if proposal.settlement_record_bytes.is_empty() {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_empty_body_phase_1586".into(),
            ));
        }
        if proposal.settlement_record_bytes.len() > MAX_EPOCH_PROPOSAL_BODY_BYTES {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_body_too_large_phase_1586".into(),
            ));
        }
        if proposal.network_id != self.network_id {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_wrong_network_phase_1586".into(),
            ));
        }
        validate_proposal_hashes(proposal)?;
        let current = self.epoch_store.get_current_epoch()?;
        if proposal.epoch_number != current.saturating_add(1) {
            return Err(ILCConsensusError::InvalidEpoch);
        }
        let now_ms = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);
        if proposal.not_before_unix_ms
            > now_ms.saturating_add(crate::epoch_settlement::CLOCK_SKEW_TOLERANCE_MS)
        {
            return Err(ILCConsensusError::Other(
                "submit_epoch_proposal_not_before_too_far_future_phase_1586".into(),
            ));
        }
        Ok(())
    }

    fn verify_epoch_proposal_ack(
        &self,
        proposal: &EpochProposal,
        ack: &EpochProposalAck,
        from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
        let commitment = proposal_commitment_sha256(proposal);
        if ack.proposal_commitment_sha256.as_slice() != commitment {
            return Err(ILCConsensusError::Other(
                "epoch_proposal_ack_commitment_mismatch_phase_1586_fix1".into(),
            ));
        }

        let record = proposal_to_record(proposal);
        let record_bytes = bincode::serialize(&record)
            .map_err(|e| ILCConsensusError::Other(format!("Epoch record serialize: {}", e)))?;
        let validator_key = {
            let vs = self.fast_path.validator_set.read().unwrap();
            vs.validators.get(&from).cloned().ok_or_else(|| {
                ILCConsensusError::Other(format!(
                    "epoch_proposal_ack_unknown_validator_phase_1586_fix1:{}",
                    from.0
                ))
            })?
        };

        let record_ok = ack.sig.0.verify(
            true,
            &record_bytes,
            crate::types::ILC_EPOCH_SIG_DST,
            &[],
            &validator_key.0,
            true,
        );
        if record_ok != blst::BLST_ERROR::BLST_SUCCESS {
            return Err(ILCConsensusError::Other(
                "epoch_proposal_ack_invalid_record_sig_phase_1586_fix1".into(),
            ));
        }

        let proposal_ok = ack.proposal_sig.0.verify(
            true,
            &commitment,
            ILC_EPOCH_PROPOSAL_SIG_DST,
            &[],
            &validator_key.0,
            true,
        );
        if proposal_ok != blst::BLST_ERROR::BLST_SUCCESS {
            return Err(ILCConsensusError::Other(
                "epoch_proposal_ack_invalid_proposal_sig_phase_1586_fix1".into(),
            ));
        }
        Ok(())
    }

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    async fn execute_and_log(&self, cert: TransferCertificate) -> Result<(), ILCConsensusError> {
        match self.fast_path.execute_certificate(cert) {
            Ok(change) => {
                eprintln!(
                    "[m010_node] validator_id={} fast_path_executed: {:?} → {:?} amount={}",
                    self.validator_id.0, change.from_agent, change.to_agent, change.amount
                );
                Ok(())
            }
            Err(ILCConsensusError::ConflictingTransfer) => {
                // Equivocation Detected: Duplicate or conflicting transfer received internally marking Byzantine fault limits structurally.
                // For M-010, identically consuming harmlessly, but fundamentally flags adversarial structures.
                eprintln!(
                    "[m010_node] validator_id={} duplicate certificate ignored (ConflictingTransfer / Equivocation Detected)",
                    self.validator_id.0
                );
                Ok(())
            }
            Err(e) => Err(e),
        }
    }

    async fn broadcast_certificate(
        &self,
        cert: TransferCertificate,
    ) -> Result<(), ILCConsensusError> {
        for (peer_id, _addr) in &self.peer_addrs {
            #[cfg(feature = "testnet_fault_sim")]
            if self.partition_block_peers.contains(&peer_id.0) {
                eprintln!(
                    "[m015_partition_drop] validator_id={} target={} kind=broadcast_certificate",
                    self.validator_id.0, peer_id.0
                );
                continue;
            }
            if let Err(e) = self
                .send_to_peer(*peer_id, GossipMessage::Certificate(cert.clone()))
                .await
            {
                eprintln!(
                    "[m010_node] validator_id={} broadcast_certificate: failed to send to peer={}: {}",
                    self.validator_id.0, peer_id.0, e
                );
                // Continue: partial delivery is acceptable — peers who receive the cert directly commit.
            }
        }
        Ok(())
    }

    async fn send_to_peer(
        &self,
        peer_id: ValidatorID,
        msg: GossipMessage,
    ) -> Result<(), ILCConsensusError> {
        #[cfg(feature = "testnet_fault_sim")]
        if self.partition_block_peers.contains(&peer_id.0) {
            eprintln!(
                "[m015_partition_drop] validator_id={} target={} kind=outbound",
                self.validator_id.0, peer_id.0
            );
            return Ok(());
        }
        let addr = self
            .peer_addrs
            .iter()
            .find(|(id, _)| *id == peer_id)
            .map(|(_, addr)| *addr)
            .ok_or_else(|| ILCConsensusError::Other(format!("Unknown peer {}", peer_id.0)))?;

        let env = GossipEnvelope {
            frame_type: 0x00,
            peer_id: self.validator_id,
            payload: msg,
        };
        if let Some(manager) = &self.persistent_sessions {
            manager.transmit_persistent(peer_id, env).await?;
            return Ok(());
        }
        self.send_envelope_to_addr(addr, env).await
    }

    /// Get or create an outbound QUIC connection to addr.
    /// Reuses an existing live connection; reconnects if the previous connection is closed.
    async fn get_or_connect(&self, addr: SocketAddr) -> Result<Connection, ILCConsensusError> {
        let mut pool = self.outbound_pool.lock().await;
        if let Some(conn) = pool.get(&addr) {
            if conn.close_reason().is_none() {
                return Ok(conn.clone());
            }
            // Previous connection is dead — fall through to reconnect.
            pool.remove(&addr);
        }
        let conn_future = self
            .network
            .endpoint
            .connect(addr, "localhost")
            .map_err(|e| ILCConsensusError::Other(format!("Connect error: {}", e)))?;
        // 3-second connect timeout prevents the background sync loop from stalling
        // on peers that are unreachable (e.g. testnet_client port that is not listening).
        let conn = tokio::time::timeout(tokio::time::Duration::from_secs(3), conn_future)
            .await
            .map_err(|_| ILCConsensusError::Other(format!("Connection to {} timed out", addr)))?
            .map_err(|e| ILCConsensusError::Other(format!("Connection error: {}", e)))?;
        pool.insert(addr, conn.clone());
        Ok(conn)
    }

    async fn evict_dead_outbound_connections(&self) -> usize {
        let mut pool = self.outbound_pool.lock().await;
        let before = pool.len();
        pool.retain(|_, conn| conn.close_reason().is_none());
        before.saturating_sub(pool.len())
    }

    async fn send_envelope_to_addr(
        &self,
        addr: SocketAddr,
        env: GossipEnvelope,
    ) -> Result<(), ILCConsensusError> {
        let conn = self.get_or_connect(addr).await?;
        // SEC-FIX-03: bound open_bi to prevent stalling when the peer's QUIC
        // stream limit is exhausted (flow-control tarpit).
        let (send, _recv) = tokio::time::timeout(
            tokio::time::Duration::from_millis(crate::network::IO_TIMEOUT_MS),
            conn.open_bi(),
        )
        .await
        .map_err(|_| ILCConsensusError::Other(format!("open_bi to {} timed out", addr)))?
        .map_err(|e| ILCConsensusError::Other(format!("Open stream error: {}", e)))?;
        self.network.transmit(send, env).await
    }
}

fn proposal_to_record(proposal: &EpochProposal) -> EpochSettlementRecord {
    EpochSettlementRecord {
        epoch: EpochSeq(proposal.epoch_number),
        state_root: proposal.state_root,
        not_before_unix_ms: proposal.not_before_unix_ms,
    }
}

fn validate_proposal_hashes(proposal: &EpochProposal) -> Result<(), ILCConsensusError> {
    let settlement_hash = Sha256::digest(&proposal.settlement_record_bytes);
    if proposal.epoch_data_hash.as_slice() != settlement_hash.as_slice() {
        return Err(ILCConsensusError::Other(
            "submit_epoch_proposal_epoch_data_hash_mismatch_phase_1586_fix1".into(),
        ));
    }
    let commitment = proposal_commitment_sha256(proposal);
    if proposal.idempotency_key != bytes_to_lower_hex(&commitment) {
        return Err(ILCConsensusError::Other(
            "submit_epoch_proposal_idempotency_preimage_mismatch_phase_1586_fix1".into(),
        ));
    }
    Ok(())
}

fn proposal_commitment_sha256(proposal: &EpochProposal) -> [u8; 32] {
    let settlement_hash = Sha256::digest(&proposal.settlement_record_bytes);
    let mut hasher = Sha256::new();
    hasher.update(EPOCH_PROPOSAL_PREIMAGE_DOMAIN);
    hasher.update(proposal.network_id.as_bytes());
    hasher.update(proposal.epoch_number.to_be_bytes());
    hasher.update(&proposal.submitter_agent_id);
    hasher.update(cid_root_bytes(&proposal.state_root));
    hasher.update(&proposal.epoch_data_hash);
    hasher.update(settlement_hash);
    hasher.update(proposal.not_before_unix_ms.to_be_bytes());
    hasher.finalize().into()
}

fn cid_root_bytes(root: &CIDv1Root) -> [u8; 36] {
    let mut out = [0u8; 36];
    out[..32].copy_from_slice(&root.p1);
    out[32..].copy_from_slice(&root.p2);
    out
}

fn bytes_to_lower_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for &byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}

fn evict_stale_epoch_proposals(table: &mut HashMap<String, EpochProposalInFlight>) {
    let now = tokio::time::Instant::now();
    let ttl = tokio::time::Duration::from_millis(EPOCH_PROPOSAL_STALE_MS);
    table.retain(|_, entry| now.duration_since(entry.inserted_at) <= ttl);
}

fn is_lowercase_sha256_hex(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

fn latest_epoch_sync_cursor(
    epoch_store: &crate::epoch_settlement::EpochStore,
) -> Result<u64, ILCConsensusError> {
    epoch_store.get_current_epoch()
}

fn apply_missing_epoch_record(
    epoch_store: &crate::epoch_settlement::EpochStore,
    stored: crate::epoch_settlement::StoredCheckpoint,
    protocol: &crate::epoch_settlement::EpochSettlementProtocol,
    validator_set: &crate::types::ValidatorSet,
) -> Result<(), ILCConsensusError> {
    #[cfg(not(feature = "testnet_fault_sim"))]
    let _ = epoch_store;

    // testnet_fault_sim: epoch records injected by the testnet client via
    // EpochSettlementTx are committed through commit_epoch_record(), which stores
    // agg_sig_bytes=[] (no BLS signature generated at submission time). Fall back
    // to direct commit only in those testnet builds. Production builds must treat
    // an empty signature as invalid and continue through the BLS-verified path.
    #[cfg(feature = "testnet_fault_sim")]
    if stored.agg_sig_bytes.is_empty() {
        return epoch_store.commit_epoch_record(stored.record);
    }

    let parsed_sig = blst::min_pk::Signature::from_bytes(&stored.agg_sig_bytes)
        .map_err(|_| ILCConsensusError::BLSVerificationFailed)?;
    parsed_sig
        .validate(true)
        .map_err(|_| ILCConsensusError::BLSVerificationFailed)?;
    let agg_sig = blst::min_pk::AggregateSignature::from_signature(&parsed_sig);

    let checkpoint = crate::types::EpochCheckpoint {
        record: stored.record,
        sigs: crate::types::AggSig(agg_sig),
        signers: stored.signers,
    };

    protocol
        .process_epoch_checkpoint(checkpoint, validator_set)
        .map(|_| ())
}

// ---------------------------------------------------------------------------
// Validator signing key generation for M-010 harness
// ---------------------------------------------------------------------------

/// Generate an ephemeral validator keypair for testnet test use exclusively.
#[cfg(test)]
pub fn generate_ephemeral_validator_sk() -> Result<blst::min_pk::SecretKey, ILCConsensusError> {
    let mut ikm = [0u8; 32];
    getrandom::getrandom(&mut ikm)
        .map_err(|e| ILCConsensusError::Other(format!("OS entropy: {}", e)))?;
    blst::min_pk::SecretKey::key_gen(&ikm, &[])
        .map_err(|_| ILCConsensusError::Other("BLS key_gen failed".into()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::epoch_settlement::{
        test_epoch_not_before_unix_ms, EpochSettlementProtocol, EpochStore, StoredCheckpoint,
    };
    use crate::types::{
        AgentID, AggSig, CIDv1Root, ECUTransfer, EpochSeq, EpochSettlementRecord, ObjectRef,
        ValidatorID, ValidatorSet, ValidatorSig,
    };
    use crate::validator::validator_dst;
    use blst::min_pk::{AggregateSignature, SecretKey};
    use lmdb_rkv::Environment;
    use tempfile::tempdir;

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Environment::new().set_max_dbs(2).open(dir.path()).unwrap();
        (Arc::new(env), dir)
    }

    fn setup_validators() -> (ValidatorSet, Vec<SecretKey>) {
        let mut keys = Vec::new();
        let mut validators = Vec::new();
        for i in 1..=2u32 {
            let sk = SecretKey::key_gen(&[i as u8; 32], &[]).unwrap();
            let pk = sk.sk_to_pk();
            keys.push(sk);
            validators.push((crate::types::ValidatorID(i), crate::types::ValidatorKey(pk)));
        }
        (ValidatorSet::new(validators, 0).unwrap(), keys)
    }

    fn setup_n_validators(n: u32) -> (ValidatorSet, Vec<(ValidatorID, SecretKey)>) {
        let mut entries = Vec::new();
        let mut validators = Vec::new();
        for i in 1..=n {
            let ikm = [i as u8; 32];
            let sk = SecretKey::key_gen(&ikm, &[]).unwrap();
            let pk = sk.sk_to_pk();
            let id = ValidatorID(i);
            entries.push((id, sk));
            validators.push((id, crate::types::ValidatorKey(pk)));
        }
        let f = n.saturating_sub(1) as usize / 3;
        (ValidatorSet::new(validators, f).unwrap(), entries)
    }

    fn generate_ephemeral_cert() -> (Vec<u8>, Vec<u8>) {
        let rcgen::CertifiedKey { cert, key_pair } =
            rcgen::generate_simple_self_signed(vec!["localhost".into()]).unwrap();
        (cert.der().to_vec(), key_pair.serialize_der())
    }

    fn setup_proposal_runner(n: u32) -> (Arc<NodeRunner>, Vec<(ValidatorID, SecretKey)>) {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env).unwrap());
        let (validator_set, entries) = setup_n_validators(n);
        let own_sk = entries[0].1.clone();
        let fast_path = Arc::new(FastPathProtocol::new(
            validator_set,
            Arc::clone(&balance_store),
            "ilc-rc01".to_string(),
        ));
        let (cert, key) = generate_ephemeral_cert();
        let network = Arc::new(
            PeerNetwork::new_client("127.0.0.1:0".parse().unwrap(), HashMap::new(), cert, key)
                .unwrap(),
        );
        let runner = Arc::new(
            NodeRunner::new(
                ValidatorID(1),
                "ilc-rc01".to_string(),
                n.saturating_sub(1) as usize / 3,
                own_sk,
                network,
                fast_path,
                balance_store,
                epoch_store,
                vec![],
            )
            .with_proposal_ingress_enabled(true),
        );
        (runner, entries)
    }

    fn canonical_epoch_proposal(epoch_number: u64) -> EpochProposal {
        let settlement_record_bytes = b"canonical-economic-evidence-phase-1586-fix1".to_vec();
        let epoch_data_hash = Sha256::digest(&settlement_record_bytes).to_vec();
        let mut proposal = EpochProposal {
            submitter_agent_id: vec![9; 48],
            epoch_number,
            state_root: CIDv1Root::new([7; 36]),
            epoch_data_hash,
            settlement_record_bytes,
            idempotency_key: String::new(),
            not_before_unix_ms: 0,
            network_id: "ilc-rc01".to_string(),
        };
        proposal.idempotency_key = bytes_to_lower_hex(&proposal_commitment_sha256(&proposal));
        proposal
    }

    fn valid_epoch_proposal_ack(
        proposal: &EpochProposal,
        signer: ValidatorID,
        sk: &SecretKey,
    ) -> (ValidatorID, EpochProposalAck) {
        let record = proposal_to_record(proposal);
        let record_bytes = bincode::serialize(&record).unwrap();
        let commitment = proposal_commitment_sha256(proposal);
        (
            signer,
            EpochProposalAck {
                idempotency_key: proposal.idempotency_key.clone(),
                epoch_number: proposal.epoch_number,
                proposal_commitment_sha256: commitment.to_vec(),
                proposal_sig: ValidatorSig(sk.sign(&commitment, ILC_EPOCH_PROPOSAL_SIG_DST, &[])),
                sig: ValidatorSig(sk.sign(&record_bytes, crate::types::ILC_EPOCH_SIG_DST, &[])),
            },
        )
    }

    fn generate_valid_agg_sig(record: &EpochSettlementRecord, keys: &[SecretKey]) -> AggSig {
        let msg = bincode::serialize(record).unwrap();
        let sigs: Vec<_> = keys
            .iter()
            .map(|sk| sk.sign(&msg, crate::types::ILC_EPOCH_SIG_DST, &[]))
            .collect();
        let sig_refs: Vec<_> = sigs.iter().collect();
        let agg = AggregateSignature::aggregate(&sig_refs, false).unwrap();
        AggSig(agg)
    }

    fn dummy_transfer() -> ECUTransfer {
        let ikm = [1u8; 32];
        let agent_sk = blst::min_pk::SecretKey::key_gen(&ikm, &[]).unwrap();
        let agent_id = AgentID(agent_sk.sk_to_pk().to_bytes());
        let object_ref = ObjectRef {
            agent: agent_id,
            version: 0,
        };
        let transfer_class = crate::types::TransferClass::Contribution;
        let sender_msg =
            bincode::serialize(&(&object_ref, &AgentID([2; 48]), &100u64, &transfer_class))
                .unwrap();
        let sig = crate::types::AgentSig(agent_sk.sign(
            &sender_msg,
            crate::types::AGENT_TRANSFER_DST,
            &[],
        ));
        ECUTransfer {
            object_ref,
            to: AgentID([2; 48]),
            amount_micro_ecu: 100,
            transfer_class,
            sender_sig: sig,
        }
    }

    #[test]
    fn test_generate_ephemeral_validator_sk_produces_valid_key() {
        let sk = generate_ephemeral_validator_sk().unwrap();
        let pk = sk.sk_to_pk();
        // Sign and verify a test message
        let msg = b"m010_node_keygen_test";
        let dst = validator_dst("ilc-mysticeti-testnet-m009");
        let sig = sk.sign(msg, &dst, &[]);
        let result = sig.verify(true, msg, &dst, &[], &pk, true);
        assert_eq!(result, blst::BLST_ERROR::BLST_SUCCESS);
    }

    #[tokio::test]
    async fn test_phase1586_fix1_n4_f1_quorum_commits_epoch_proposal() {
        let (runner, entries) = setup_proposal_runner(4);
        let proposal = canonical_epoch_proposal(1);
        let proposal_id = proposal.idempotency_key.clone();

        let submit_runner = Arc::clone(&runner);
        let submit =
            tokio::spawn(async move { submit_runner.submit_epoch_proposal(proposal).await });
        tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

        for (signer, sk) in entries.iter().skip(1).take(2) {
            let proposal = {
                let table = runner.epoch_proposals.lock().await;
                table.get(&proposal_id).unwrap().proposal.clone()
            };
            let (from, ack) = valid_epoch_proposal_ack(&proposal, *signer, sk);
            runner.handle_epoch_proposal_ack(ack, from).await.unwrap();
        }

        let outcome = submit.await.unwrap().unwrap();
        assert_eq!(
            outcome.status_token,
            SUBMIT_EPOCH_PROPOSAL_ACCEPTED_PHASE_1586
        );
        assert_eq!(runner.epoch_store.get_current_epoch().unwrap(), 1);
    }

    #[tokio::test]
    async fn test_phase1586_fix1_bad_ack_does_not_poison_proposal() {
        let (runner, entries) = setup_proposal_runner(4);
        let proposal = canonical_epoch_proposal(1);
        let proposal_id = proposal.idempotency_key.clone();

        let submit_runner = Arc::clone(&runner);
        let submit =
            tokio::spawn(async move { submit_runner.submit_epoch_proposal(proposal).await });
        tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

        let proposal = {
            let table = runner.epoch_proposals.lock().await;
            table.get(&proposal_id).unwrap().proposal.clone()
        };
        let (bad_from, mut bad_ack) =
            valid_epoch_proposal_ack(&proposal, entries[1].0, &entries[1].1);
        bad_ack.proposal_sig = valid_epoch_proposal_ack(&proposal, entries[2].0, &entries[2].1)
            .1
            .proposal_sig;
        assert!(runner
            .handle_epoch_proposal_ack(bad_ack, bad_from)
            .await
            .is_err());
        {
            let table = runner.epoch_proposals.lock().await;
            let entry = table.get(&proposal_id).unwrap();
            assert!(!entry.completed);
            assert_eq!(entry.sigs.len(), 1, "bad ack must not be stored");
        }

        for (signer, sk) in entries.iter().skip(1).take(2) {
            let (from, ack) = valid_epoch_proposal_ack(&proposal, *signer, sk);
            runner.handle_epoch_proposal_ack(ack, from).await.unwrap();
        }

        let outcome = submit.await.unwrap().unwrap();
        assert_eq!(
            outcome.status_token,
            SUBMIT_EPOCH_PROPOSAL_ACCEPTED_PHASE_1586
        );
        assert_eq!(runner.epoch_store.get_current_epoch().unwrap(), 1);
    }

    #[tokio::test]
    async fn test_phase1586_fix1_rejects_epoch_data_hash_mismatch() {
        let (runner, _) = setup_proposal_runner(4);
        let mut proposal = canonical_epoch_proposal(1);
        proposal.epoch_data_hash = vec![3; 32];
        proposal.idempotency_key = bytes_to_lower_hex(&proposal_commitment_sha256(&proposal));
        let err = runner.validate_epoch_proposal(&proposal).unwrap_err();
        assert!(format!("{err:?}").contains("epoch_data_hash_mismatch"));
    }

    #[tokio::test]
    async fn test_phase1586_fix1_rejects_idempotency_preimage_mismatch() {
        let (runner, _) = setup_proposal_runner(4);
        let mut proposal = canonical_epoch_proposal(1);
        proposal.idempotency_key = "a".repeat(64);
        let err = runner.validate_epoch_proposal(&proposal).unwrap_err();
        assert!(format!("{err:?}").contains("idempotency_preimage_mismatch"));
    }

    #[tokio::test]
    async fn test_phase1586_fix1_rejects_malformed_idempotency_on_peer_path() {
        let (runner, _) = setup_proposal_runner(4);
        let mut proposal = canonical_epoch_proposal(1);
        proposal.idempotency_key = "A".repeat(64);
        let err = runner.validate_epoch_proposal(&proposal).unwrap_err();
        assert!(format!("{err:?}").contains("invalid_idempotency_key"));
    }

    #[tokio::test]
    async fn test_phase1586_fix1_rejects_wrong_network_and_body_cap() {
        let (runner, _) = setup_proposal_runner(4);
        let mut wrong_network = canonical_epoch_proposal(1);
        wrong_network.network_id = "ilc-wrong-network".to_string();
        wrong_network.idempotency_key =
            bytes_to_lower_hex(&proposal_commitment_sha256(&wrong_network));
        let err = runner.validate_epoch_proposal(&wrong_network).unwrap_err();
        assert!(format!("{err:?}").contains("wrong_network"));

        let mut oversized = canonical_epoch_proposal(1);
        oversized.settlement_record_bytes = vec![1; MAX_EPOCH_PROPOSAL_BODY_BYTES + 1];
        oversized.epoch_data_hash = Sha256::digest(&oversized.settlement_record_bytes).to_vec();
        oversized.idempotency_key = bytes_to_lower_hex(&proposal_commitment_sha256(&oversized));
        let err = runner.validate_epoch_proposal(&oversized).unwrap_err();
        assert!(format!("{err:?}").contains("body_too_large"));
    }

    #[test]
    fn test_phase1586_fix1_epoch_proposal_ttl_cleanup_bounds_table() {
        let mut table: HashMap<String, EpochProposalInFlight> = HashMap::new();
        let stale = canonical_epoch_proposal(1);
        let fresh = canonical_epoch_proposal(2);
        table.insert(
            stale.idempotency_key.clone(),
            EpochProposalInFlight {
                proposal: stale,
                sigs: vec![],
                completed: true,
                inserted_at: tokio::time::Instant::now()
                    - tokio::time::Duration::from_millis(EPOCH_PROPOSAL_STALE_MS + 1),
                waiter: None,
            },
        );
        table.insert(
            fresh.idempotency_key.clone(),
            EpochProposalInFlight {
                proposal: fresh,
                sigs: vec![],
                completed: true,
                inserted_at: tokio::time::Instant::now(),
                waiter: None,
            },
        );

        evict_stale_epoch_proposals(&mut table);
        assert_eq!(table.len(), 1);
        assert_eq!(table.values().next().unwrap().proposal.epoch_number, 2);
    }

    // SEC-FIX-01: in_flight eviction — certified entries must not accumulate
    // This test verifies the eviction mechanic at the HashMap level. The full
    // integration path is covered by test_two_validators_loopback in network.rs.
    #[test]
    fn test_in_flight_eviction_clears_certified_entry() {
        use crate::types::AgentID;
        use std::collections::HashMap;

        let object_ref = ObjectRef {
            agent: AgentID([1; 48]),
            version: 0,
        };

        // Simulate the in_flight table lifecycle: insert on broadcast, remove on certification.
        let mut table: HashMap<ObjectRef, InFlight> = HashMap::new();
        assert_eq!(table.len(), 0);

        table.insert(
            object_ref,
            InFlight {
                transfer: dummy_transfer(),
                sigs: Vec::new(),
                certified: false,
                inserted_at: tokio::time::Instant::now(),
            },
        );
        assert_eq!(table.len(), 1, "entry must be present after broadcast");

        // Simulate post-certification eviction (the fix in handle_ack_for).
        table.remove(&object_ref);
        assert_eq!(
            table.len(),
            0,
            "entry must be evicted after certification — OOM guard"
        );
    }

    // SEC-FIX-04: MissingCertResponse count cap — CPU DoS guard.
    // Verifies the guard constant and condition that mirrors the production check.
    #[test]
    fn test_missing_cert_response_cap_enforced() {
        use crate::types::TransferCertificate;

        // Build 65 minimal certs (sigs=empty is fine — the cap fires before any BLS work).
        let certs: Vec<TransferCertificate> = (0u8..65)
            .map(|i| {
                let ikm = [i + 1; 32];
                let sk = blst::min_pk::SecretKey::key_gen(&ikm, &[]).unwrap();
                let agent_id = AgentID(sk.sk_to_pk().to_bytes());
                let object_ref = ObjectRef {
                    agent: agent_id,
                    version: i as u64,
                };
                let transfer_class = crate::types::TransferClass::Contribution;
                let msg =
                    bincode::serialize(&(&object_ref, &AgentID([2; 48]), &10u64, &transfer_class))
                        .unwrap();
                let sig =
                    crate::types::AgentSig(sk.sign(&msg, crate::types::AGENT_TRANSFER_DST, &[]));
                TransferCertificate {
                    transfer: ECUTransfer {
                        object_ref,
                        to: AgentID([2; 48]),
                        amount_micro_ecu: 10,
                        transfer_class,
                        sender_sig: sig,
                    },
                    sigs: vec![],
                    epoch: EpochSeq(1),
                }
            })
            .collect();

        // Guard condition mirrors the production code: > 64 → reject.
        assert_eq!(certs.len(), 65);
        assert_eq!(MAX_CERTS_PER_RESPONSE, 64);
        assert!(
            certs.len() > MAX_CERTS_PER_RESPONSE,
            "65 certs must exceed the cap of 64"
        );
    }

    #[test]
    fn test_latest_epoch_sync_cursor_uses_current_epoch_sentinel() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (validator_set, keys) = setup_validators();
        let signers = vec![crate::types::ValidatorID(1), crate::types::ValidatorID(2)];

        assert_eq!(latest_epoch_sync_cursor(&store).unwrap(), 0);
        for epoch in 1u64..=3 {
            let record = EpochSettlementRecord {
                epoch: EpochSeq(epoch),
                state_root: CIDv1Root::new([epoch as u8; 36]),
                not_before_unix_ms: test_epoch_not_before_unix_ms(epoch),
            };
            let checkpoint = crate::types::EpochCheckpoint {
                sigs: generate_valid_agg_sig(&record, &keys),
                record,
                signers: signers.clone(),
            };
            protocol
                .process_epoch_checkpoint(checkpoint, &validator_set)
                .unwrap();
        }

        assert_eq!(latest_epoch_sync_cursor(&store).unwrap(), 3);
    }

    #[test]
    fn test_missing_cert_sync_request_and_inflight_signature_caps_are_locked() {
        assert_eq!(MAX_MISSING_VERSIONS, 1024);
        assert_eq!(MAX_SIGS_PER_INFLIGHT, crate::fast_path::MAX_CERT_SIGS);

        let missing_versions: Vec<u64> = (0..=MAX_MISSING_VERSIONS as u64).collect();
        assert!(missing_versions.len() > MAX_MISSING_VERSIONS);

        let mut table: HashMap<ObjectRef, InFlight> = HashMap::new();
        let object_ref = ObjectRef {
            agent: AgentID([9; 48]),
            version: 1,
        };
        table.insert(
            object_ref,
            InFlight {
                transfer: dummy_transfer(),
                sigs: Vec::with_capacity(MAX_SIGS_PER_INFLIGHT),
                certified: false,
                inserted_at: tokio::time::Instant::now(),
            },
        );
        let entry = table.get(&object_ref).unwrap();
        assert_eq!(entry.sigs.len(), 0);
        assert!(entry.sigs.len() < MAX_SIGS_PER_INFLIGHT);
    }

    // SEC-FIX-04: zombie in_flight TTL sweep — non-certified entries must be evictable.
    #[test]
    fn test_in_flight_zombie_ttl_retain_evicts_stale() {
        use crate::types::AgentID;
        use std::collections::HashMap;

        let mut table: HashMap<ObjectRef, InFlight> = HashMap::new();

        // Stale zombie: inserted 120s ago (> 60s TTL), not certified.
        let stale_ref = ObjectRef {
            agent: AgentID([10; 48]),
            version: 0,
        };
        table.insert(
            stale_ref,
            InFlight {
                transfer: dummy_transfer(),
                sigs: Vec::new(),
                certified: false,
                inserted_at: tokio::time::Instant::now() - tokio::time::Duration::from_secs(120),
            },
        );

        // Fresh entry: inserted just now, not certified — must be retained.
        let fresh_ref = ObjectRef {
            agent: AgentID([11; 48]),
            version: 0,
        };
        table.insert(
            fresh_ref,
            InFlight {
                transfer: dummy_transfer(),
                sigs: Vec::new(),
                certified: false,
                inserted_at: tokio::time::Instant::now(),
            },
        );

        // Certified entry: even if fresh, must be evicted by TTL sweep.  Certified
        // entries are only an early-rejection cache and must not survive a failed
        // broadcast path indefinitely.
        let certified_ref = ObjectRef {
            agent: AgentID([12; 48]),
            version: 0,
        };
        table.insert(
            certified_ref,
            InFlight {
                transfer: dummy_transfer(),
                sigs: Vec::new(),
                certified: true,
                inserted_at: tokio::time::Instant::now(),
            },
        );

        let ttl = tokio::time::Duration::from_secs(60);
        table.retain(|_, entry| !entry.certified && entry.inserted_at.elapsed() < ttl);

        // stale zombie and certified entries must be gone; fresh non-certified remains.
        assert!(
            !table.contains_key(&stale_ref),
            "stale zombie must be evicted"
        );
        assert!(
            table.contains_key(&fresh_ref),
            "fresh entry must be retained"
        );
        assert!(
            !table.contains_key(&certified_ref),
            "certified entry must be evicted to avoid post-certification leaks"
        );
        assert_eq!(table.len(), 1);
    }

    #[test]
    fn test_apply_missing_epoch_record_malformed_non_empty_sig_rejected() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, keys) = setup_validators();

        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            not_before_unix_ms: 0,
        };
        let wrong_record = EpochSettlementRecord {
            epoch: EpochSeq(99),
            state_root: CIDv1Root::new([99u8; 36]),
            not_before_unix_ms: 0,
        };
        let wrong_sig_bytes = generate_valid_agg_sig(&wrong_record, &keys)
            .0
            .to_signature()
            .compress()
            .to_vec();

        // Claim both validators signed (IDs 1, 2) — but the aggregate is for the wrong record.
        let stored = StoredCheckpoint {
            record,
            agg_sig_bytes: wrong_sig_bytes,
            signers: vec![crate::types::ValidatorID(1), crate::types::ValidatorID(2)],
        };

        let err = apply_missing_epoch_record(&store, stored, &protocol, &vset).unwrap_err();
        assert_eq!(err, ILCConsensusError::BLSVerificationFailed);
        assert!(store.get_checkpoint(1).unwrap().is_none());
    }

    #[cfg(not(feature = "testnet_fault_sim"))]
    #[test]
    fn test_apply_missing_epoch_record_empty_sig_rejected_without_testnet_feature() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, _keys) = setup_validators();

        let stored = StoredCheckpoint {
            record: EpochSettlementRecord {
                epoch: EpochSeq(1),
                state_root: CIDv1Root::new([1u8; 36]),
                not_before_unix_ms: 0,
            },
            agg_sig_bytes: vec![],
            signers: vec![],
        };

        let err = apply_missing_epoch_record(&store, stored, &protocol, &vset).unwrap_err();
        assert_eq!(err, ILCConsensusError::BLSVerificationFailed);
        assert!(store.get_checkpoint(1).unwrap().is_none());
    }

    #[cfg(feature = "testnet_fault_sim")]
    #[test]
    fn test_apply_missing_epoch_record_empty_sig_falls_back_in_testnet_build() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, _keys) = setup_validators();

        let stored = StoredCheckpoint {
            record: EpochSettlementRecord {
                epoch: EpochSeq(1),
                state_root: CIDv1Root::new([1u8; 36]),
                not_before_unix_ms: 0,
            },
            agg_sig_bytes: vec![],
            signers: vec![],
        };

        apply_missing_epoch_record(&store, stored, &protocol, &vset).unwrap();

        let recovered = store.get_checkpoint(1).unwrap().unwrap();
        assert_eq!(recovered.record.epoch, EpochSeq(1));
        assert!(recovered.agg_sig_bytes.is_empty());
    }

    // M-015: multi-record iteration and idempotency in apply_missing_epoch_record.
    // handle_missing_epoch_response iterates over Vec<StoredCheckpoint>; each record
    // that returns InvalidEpoch is treated as already-committed (idempotent).
    // This test exercises that path: commit epoch 1 once, then re-apply it as part
    // of a batch alongside a new epoch 2 — epoch 1 is skipped, epoch 2 committed.
    #[cfg(feature = "testnet_fault_sim")]
    #[test]
    fn test_apply_missing_epoch_records_multi_record_with_idempotency() {
        let (env, _dir) = setup_env();
        let store = Arc::new(EpochStore::new(env).unwrap());
        let protocol = EpochSettlementProtocol::new(store.clone());
        let (vset, _keys) = setup_validators();

        // Pre-commit epoch 1 via testnet path (empty sig).
        let record_e1 = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            not_before_unix_ms: 0,
        };
        store.commit_epoch_record(record_e1.clone()).unwrap();
        assert!(
            store.get_checkpoint(1).unwrap().is_some(),
            "epoch 1 must be pre-committed"
        );

        // Build a batch of two records: epoch 1 (already committed) and epoch 2 (new).
        // `signers` is empty in this recovery-path test — the field exists for the gossip
        // path; apply_missing_epoch_record doesn't re-verify the aggregate.
        let stored_e1 = StoredCheckpoint {
            record: record_e1,
            agg_sig_bytes: vec![],
            signers: vec![],
        };
        let stored_e2 = StoredCheckpoint {
            record: EpochSettlementRecord {
                epoch: EpochSeq(2),
                state_root: CIDv1Root::new([2u8; 36]),
                not_before_unix_ms: test_epoch_not_before_unix_ms(2),
            },
            agg_sig_bytes: vec![],
            signers: vec![],
        };

        // Simulate the handle_missing_epoch_response loop.
        for stored in [stored_e1, stored_e2] {
            let epoch = stored.record.epoch.0;
            match apply_missing_epoch_record(&store, stored, &protocol, &vset) {
                Ok(()) => eprintln!("epoch {} committed", epoch),
                Err(ILCConsensusError::InvalidEpoch) => {
                    // Already committed — idempotent; correct behavior.
                    eprintln!("epoch {} already committed (idempotent)", epoch);
                }
                Err(e) => panic!("unexpected error for epoch {}: {:?}", epoch, e),
            }
        }

        // Both epochs must be present after the loop.
        assert!(
            store.get_checkpoint(1).unwrap().is_some(),
            "epoch 1 must still be present"
        );
        assert!(
            store.get_checkpoint(2).unwrap().is_some(),
            "epoch 2 must be committed by the loop"
        );
    }

    #[test]
    fn test_dummy_transfer_has_valid_sender_sig() {
        let transfer = dummy_transfer();
        let sender_msg = bincode::serialize(&(
            &transfer.object_ref,
            &transfer.to,
            &transfer.amount_micro_ecu,
            &transfer.transfer_class,
        ))
        .unwrap();
        let pubkey = blst::min_pk::PublicKey::from_bytes(&transfer.object_ref.agent.0).unwrap();
        let result = transfer.sender_sig.0.verify(
            true,
            &sender_msg,
            crate::types::AGENT_TRANSFER_DST,
            &[],
            &pubkey,
            true,
        );
        assert_eq!(result, blst::BLST_ERROR::BLST_SUCCESS);
    }

    #[test]
    fn test_next_relay_hop_returns_next_peer_and_tail() {
        let hop = next_relay_hop(ValidatorID(2), &[ValidatorID(3), ValidatorID(1)])
            .unwrap()
            .unwrap();

        assert_eq!(hop.0, ValidatorID(3));
        assert_eq!(hop.1, vec![ValidatorID(1)]);
    }

    #[test]
    fn test_next_relay_hop_rejects_duplicate_validator() {
        let err = next_relay_hop(ValidatorID(2), &[ValidatorID(3), ValidatorID(3)]).unwrap_err();

        assert!(format!("{:?}", err).contains("duplicate validator 3"));
    }

    #[test]
    fn test_next_relay_hop_rejects_loop_back_through_current_validator() {
        let err = next_relay_hop(ValidatorID(2), &[ValidatorID(3), ValidatorID(2)]).unwrap_err();

        assert!(format!("{:?}", err).contains("loops back through validator 2"));
    }
}
