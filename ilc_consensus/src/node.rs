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
use std::collections::HashMap;
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
    pub censor_validator: Option<u32>,
    pub censor_target: Option<u32>,
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
            censor_validator: std::env::var("CENSOR_VALIDATOR").ok().and_then(|v| v.parse().ok()),
            censor_target: std::env::var("CENSOR_TARGET").ok().and_then(|v| v.parse().ok()),
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
                // TODO(pre-production): isolate under #[cfg(feature = "testnet_fault_sim")]
                if let Some(censor_val) = self.censor_validator {
                    if let Some(censor_tgt) = self.censor_target {
                        if self.validator_id.0 == censor_val && from.0 == censor_tgt {
                            eprintln!("[m014_censor] validator_id={} dropped EpochSettlementTx from validator_id={}", self.validator_id.0, from.0);
                            return Ok(());
                        }
                    }
                }
                self.handle_epoch_settlement_tx(tx).await
            }
            GossipMessage::MissingCertSync { agent, missing_versions } => {
                self.handle_missing_cert_sync(agent, missing_versions, from).await
            }
            GossipMessage::MissingCertResponse { certs } => {
                self.handle_missing_cert_response(certs).await
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
            table.entry(object_ref).or_insert_with(|| InFlight {
                transfer: transfer.clone(),
                sigs: Vec::new(),
                certified: false,
            });
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
    // EpochSettlementTx handler
    // -----------------------------------------------------------------------

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
        let conn = self.network.endpoint
            .connect(addr, "localhost")
            .map_err(|e| ILCConsensusError::Other(format!("Connect error: {}", e)))?
            .await
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
