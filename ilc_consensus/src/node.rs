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
use crate::types::{
    ECUTransfer, ILCConsensusError, ObjectRef, TransferCertificate, ValidatorID,
};
use crate::validator::sign_message;

// ---------------------------------------------------------------------------
// In-flight transfer state (quorum accumulation)
// ---------------------------------------------------------------------------

struct InFlight {
    transfer: ECUTransfer,
    sigs: Vec<(ValidatorID, crate::types::ValidatorSig)>,
    /// Whether we have already assembled and broadcast a Certificate for this transfer.
    certified: bool,
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
            #[cfg(feature = "testnet_fault_sim")]
            censor_validator: std::env::var("CENSOR_VALIDATOR").ok().and_then(|v| v.parse().ok()),
            #[cfg(feature = "testnet_fault_sim")]
            censor_target: std::env::var("CENSOR_TARGET").ok().and_then(|v| v.parse().ok()),
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

    /// Main accept loop: accept inbound QUIC connections and dispatch each in its own task.
    /// Requires Arc<Self> so each spawned task can hold a reference independently.
    pub async fn run(self: Arc<Self>) -> Result<(), ILCConsensusError> {
        eprintln!(
            "[m010_node] validator_id={} running on {}",
            self.validator_id.0,
            self.network.endpoint.local_addr()
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
                    let msg = GossipMessage::MissingEpochSync { latest_contiguous_epoch: cursor };
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

        loop {
            let incoming = self.network.endpoint.accept().await
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
                let (_, recv) = match connection.accept_bi().await {
                    Ok(s) => s,
                    Err(e) => {
                        eprintln!("[m010_node] stream accept error: {}", e);
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
            GossipMessage::Certificate(cert) => {
                self.handle_certificate(cert).await
            }
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
            GossipMessage::MissingCertSync { agent, missing_versions } => {
                self.handle_missing_cert_sync(agent, missing_versions, from).await
            }
            GossipMessage::MissingCertResponse { certs } => {
                self.handle_missing_cert_response(certs).await
            }
            GossipMessage::MissingEpochSync { latest_contiguous_epoch } => {
                self.handle_missing_epoch_sync(latest_contiguous_epoch, from).await
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
        let sender_msg = bincode::serialize(&(
            &transfer.object_ref,
            &transfer.to,
            &transfer.amount_micro_ecu,
        ))
        .map_err(|e| ILCConsensusError::Other(format!("Sender msg serialize: {}", e)))?;

        let sender_pubkey = blst::min_pk::PublicKey::from_bytes(&transfer.object_ref.agent.0)
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
            eprintln!(
                "[m010_node] validator_id={} rejected transfer from peer={}: invalid sender_sig",
                self.validator_id.0, from.0
            );
            return Ok(()); // drop silently; do not propagate invalid transfers
        }

        // Record in in_flight table if not already present.
        let object_ref = transfer.object_ref;
        {
            let mut table = self.in_flight.lock().await;
            if let Some(existing) = table.get(&object_ref) {
                // If it already exists, verify the payload matches. If not, it's equivocation!
                if existing.transfer.to != transfer.to || existing.transfer.amount_micro_ecu != transfer.amount_micro_ecu {
                    eprintln!(
                        "[m010_node] validator_id={} duplicate certificate ignored (ConflictingTransfer / Equivocation Detected)",
                        self.validator_id.0
                    );
                    return Ok(());
                }
            } else {
                table.insert(object_ref, InFlight {
                    transfer: transfer.clone(),
                    sigs: Vec::new(),
                    certified: false,
                });
            }
        }

        // Sign the transfer with our validator key and send AckFor back to originator.
        // AckFor carries the object_ref so the recipient can key the ack unambiguously.
        let transfer_msg = bincode::serialize(&transfer)
            .map_err(|e| ILCConsensusError::Other(format!("Transfer serialize: {}", e)))?;
        let sig = sign_message(&self.validator_sk, &transfer_msg, &self.network_id);

        eprintln!(
            "[m010_node] validator_id={} acking transfer obj_ref={:?} to peer={}",
            self.validator_id.0, object_ref, from.0
        );

        self.send_to_peer(
            from,
            GossipMessage::AckFor { object_ref, sig },
        ).await
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
        let quorum = 2 * self.f + 1;
        let mut to_certify: Option<(ECUTransfer, Vec<(ValidatorID, crate::types::ValidatorSig)>)> = None;

        {
            let mut table = self.in_flight.lock().await;
            if let Some(entry) = table.get_mut(&object_ref) {
                if !entry.certified {
                    // Deduplicate: only accept one sig per validator.
                    if !entry.sigs.iter().any(|(id, _)| *id == from) {
                        entry.sigs.push((from, sig));
                        eprintln!(
                            "[m010_node] validator_id={} ack from peer={} for obj_ref={:?} sigs={}/{}",
                            self.validator_id.0, from.0, object_ref, entry.sigs.len(), quorum
                        );
                        if entry.sigs.len() >= quorum {
                            entry.certified = true;
                            to_certify = Some((entry.transfer.clone(), entry.sigs.clone()));
                        }
                    }
                }
            } else {
                eprintln!(
                    "[m010_node] validator_id={} AckFor for unknown obj_ref={:?} from peer={}",
                    self.validator_id.0, object_ref, from.0
                );
            }
        }

        if let Some((transfer, sigs)) = to_certify {
            let cert = TransferCertificate { transfer, sigs };
            eprintln!(
                "[m010_node] validator_id={} assembled certificate for obj_ref={:?} — broadcasting",
                self.validator_id.0, object_ref
            );
            self.broadcast_certificate(cert.clone()).await?;
            self.execute_and_log(cert).await?;
        }

        Ok(())
    }

    // -----------------------------------------------------------------------
    // Certificate handler
    // -----------------------------------------------------------------------

    async fn handle_certificate(&self, cert: TransferCertificate) -> Result<(), ILCConsensusError> {
        eprintln!(
            "[m010_node] validator_id={} received Certificate for obj_ref={:?}",
            self.validator_id.0, cert.transfer.object_ref
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
        for cert in certs {
            eprintln!(
                "[m010_node] validator_id={} MissingCertResponse: replaying certificate obj_ref={:?}",
                self.validator_id.0, cert.transfer.object_ref
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
        self.send_to_peer(from, GossipMessage::MissingEpochResponse { records }).await
    }

    async fn handle_epoch_checkpoint_msg(
        &self,
        checkpoint: crate::types::EpochCheckpoint,
    ) -> Result<(), ILCConsensusError> {
        let validator_set = &self.fast_path.validator_set;
        let protocol = crate::epoch_settlement::EpochSettlementProtocol::new(self.epoch_store.clone());
        let epoch = checkpoint.record.epoch.0;

        match protocol.process_epoch_checkpoint(checkpoint, validator_set) {
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
                eprintln!("[m018_node] validator_id={} checkpoint validation failed: {:?}", self.validator_id.0, e);
                Err(e)
            }
        }
    }

    async fn handle_missing_epoch_response(
        &self,
        records: Vec<crate::epoch_settlement::StoredCheckpoint>,
    ) -> Result<(), ILCConsensusError> {
        let protocol = crate::epoch_settlement::EpochSettlementProtocol::new(self.epoch_store.clone());
        let validator_set = &self.fast_path.validator_set;
        
        for stored in records {
            let epoch = stored.record.epoch.0;
            
            // Reconstruct EpochCheckpoint natively
            let parsed_sig = blst::min_pk::Signature::from_bytes(&stored.agg_sig_bytes)
                .map_err(|_| ILCConsensusError::BLSVerificationFailed)?;
            let agg_sig = blst::min_pk::AggregateSignature::from_signature(&parsed_sig);
            
            let checkpoint = crate::types::EpochCheckpoint {
                record: stored.record,
                sigs: crate::types::AggSig(agg_sig),
            };

            match protocol.process_epoch_checkpoint(checkpoint, validator_set) {
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

    async fn broadcast_certificate(&self, cert: TransferCertificate) -> Result<(), ILCConsensusError> {
        for (peer_id, addr) in &self.peer_addrs {
            #[cfg(feature = "testnet_fault_sim")]
            if self.partition_block_peers.contains(&peer_id.0) {
                eprintln!(
                    "[m015_partition_drop] validator_id={} target={} kind=broadcast_certificate",
                    self.validator_id.0, peer_id.0
                );
                continue;
            }
            let env = GossipEnvelope {
                frame_type: 0x00,
                peer_id: self.validator_id,
                payload: GossipMessage::Certificate(cert.clone()),
            };
            if let Err(e) = self.send_envelope_to_addr(*addr, env).await {
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
        let addr = self.peer_addrs.iter()
            .find(|(id, _)| *id == peer_id)
            .map(|(_, addr)| *addr)
            .ok_or_else(|| ILCConsensusError::Other(format!("Unknown peer {}", peer_id.0)))?;

        let env = GossipEnvelope {
            frame_type: 0x00,
            peer_id: self.validator_id,
            payload: msg,
        };
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
        let conn_future = self.network.endpoint
            .connect(addr, "localhost")
            .map_err(|e| ILCConsensusError::Other(format!("Connect error: {}", e)))?;
        // 3-second connect timeout prevents the background sync loop from stalling
        // on peers that are unreachable (e.g. testnet_client port that is not listening).
        let conn = tokio::time::timeout(
            tokio::time::Duration::from_secs(3),
            conn_future,
        )
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
        let (send, _recv) = conn.open_bi().await
            .map_err(|e| ILCConsensusError::Other(format!("Open stream error: {}", e)))?;
        self.network.transmit(send, env).await
    }
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
    use crate::types::{AgentID, ECUTransfer, ObjectRef};
    use crate::validator::validator_dst;

    fn dummy_transfer() -> ECUTransfer {
        let ikm = [1u8; 32];
        let agent_sk = blst::min_pk::SecretKey::key_gen(&ikm, &[]).unwrap();
        let agent_id = AgentID(agent_sk.sk_to_pk().to_bytes());
        let object_ref = ObjectRef { agent: agent_id, version: 0 };
        let sender_msg = bincode::serialize(&(&object_ref, &AgentID([2; 48]), &100u64)).unwrap();
        let sig = crate::types::AgentSig(agent_sk.sign(&sender_msg, crate::types::AGENT_TRANSFER_DST, &[]));
        ECUTransfer {
            object_ref,
            to: AgentID([2; 48]),
            amount_micro_ecu: 100,
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

    #[test]
    fn test_dummy_transfer_has_valid_sender_sig() {
        let transfer = dummy_transfer();
        let sender_msg = bincode::serialize(&(
            &transfer.object_ref,
            &transfer.to,
            &transfer.amount_micro_ecu,
        )).unwrap();
        let pubkey = blst::min_pk::PublicKey::from_bytes(&transfer.object_ref.agent.0).unwrap();
        let result = transfer.sender_sig.0.verify(
            true, &sender_msg, crate::types::AGENT_TRANSFER_DST, &[], &pubkey, true,
        );
        assert_eq!(result, blst::BLST_ERROR::BLST_SUCCESS);
    }
}
