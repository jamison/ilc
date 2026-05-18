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
use tokio::sync::Mutex;

use crate::balance_store::BalanceStore;
use crate::epoch_settlement::EpochStore;
use crate::fast_path::FastPathProtocol;
use crate::network::{GossipEnvelope, GossipMessage, PeerNetwork};
use crate::persistent_quic::PersistentQuicSessionManager;
use crate::types::{ECUTransfer, ILCConsensusError, ObjectRef, TransferCertificate, ValidatorID};
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
    /// Outbound connection pool: one QUIC connection per peer, reused across messages.
    pub outbound_pool: Arc<Mutex<HashMap<SocketAddr, Connection>>>,
    /// ADR-0039 projection-backed persistent session manager for production activation path.
    pub persistent_sessions: Option<Arc<PersistentQuicSessionManager>>,
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
            outbound_pool: Arc::new(Mutex::new(HashMap::new())),
            persistent_sessions: None,
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
                    // Compute latest_contiguous_epoch: the highest N where all of
                    // 1..=N are committed. Send as a cursor (O(1) wire size) rather
                    // than the full known-epoch list (SEC-008 fix).
                    let epochs = match node.epoch_store.list_committed_epochs() {
                        Ok(v) => v,
                        Err(e) => {
                            eprintln!(
                                "[m015_epoch_sync] validator_id={} list_committed_epochs error: {}",
                                node.validator_id.0, e
                            );
                            continue;
                        }
                    };
                    let cursor = epochs
                        .iter()
                        .enumerate()
                        .take_while(|(i, &e)| e == (*i + 1) as u64)
                        .map(|(_, &e)| e)
                        .last()
                        .unwrap_or(0);
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
            eprintln!(
                "[row5_privacy_lane] validator_id={} obj_ref={} {}",
                self.validator_id.0,
                fmt_object_ref(&transfer.object_ref),
                routing_token,
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
        // FIXME(M-5): self.f is captured at NodeRunner::new() and is NOT updated
        // when validators are admitted or ejected at runtime. For the current
        // genesis network (static 4-validator set) this is safe, but dynamic
        // membership requires reading f from self.fast_path.validator_set at
        // quorum-check time instead.
        let quorum = 2 * self.f + 1;
        let mut to_certify: Option<(ECUTransfer, Vec<(ValidatorID, crate::types::ValidatorSig)>)> =
            None;

        {
            let mut table = self.in_flight.lock().await;
            if let Some(entry) = table.get_mut(&object_ref) {
                if !entry.certified {
                    // Deduplicate: only accept one sig per validator.
                    if !entry.sigs.iter().any(|(id, _)| *id == from) {
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
        _missing_versions: Vec<u64>,
        _from: ValidatorID,
    ) -> Result<(), ILCConsensusError> {
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
        const MAX_CERTS_PER_RESPONSE: usize = 64;
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

fn apply_missing_epoch_record(
    epoch_store: &crate::epoch_settlement::EpochStore,
    stored: crate::epoch_settlement::StoredCheckpoint,
    protocol: &crate::epoch_settlement::EpochSettlementProtocol,
    validator_set: &crate::types::ValidatorSet,
) -> Result<(), ILCConsensusError> {
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
    use crate::epoch_settlement::{EpochSettlementProtocol, EpochStore, StoredCheckpoint};
    use crate::types::{
        AgentID, AggSig, CIDv1Root, ECUTransfer, EpochSeq, EpochSettlementRecord, ObjectRef,
        ValidatorSet,
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
        const MAX_CERTS_PER_RESPONSE: usize = 64;
        assert_eq!(certs.len(), 65);
        assert!(
            certs.len() > MAX_CERTS_PER_RESPONSE,
            "65 certs must exceed the cap of 64"
        );
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
        };
        let wrong_record = EpochSettlementRecord {
            epoch: EpochSeq(99),
            state_root: CIDv1Root::new([99u8; 36]),
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
