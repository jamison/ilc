use crate::epoch_settlement::StoredCheckpoint;
use crate::types::{
    AgentID, CIDv1Root, EpochCheckpoint, EpochSettlementTx, ILCConsensusError, TransferCertificate,
    ValidatorSig,
};
use bincode::Options;
use quinn::{ClientConfig, Connection, Endpoint, RecvStream, SendStream, ServerConfig};
use rustls::client::danger::ServerCertVerified;
use rustls::pki_types::ServerName;
use rustls::pki_types::{CertificateDer, PrivateKeyDer, UnixTime};
use rustls::server::danger::ClientCertVerified;
use std::collections::HashMap;
use std::sync::Arc;

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum GossipMessage {
    BroadcastHonest(crate::types::ECUTransfer), // DAG Vertex Proposal
    /// testnet_only: Window 775-782 Layer-2 submission indirection wrapper.
    /// Carries an unchanged transfer plus the remaining validator relay route.
    RelaySubmit {
        transfer: crate::types::ECUTransfer,
        remaining_route: Vec<AgentID>,
    },
    Ack(crate::types::ValidatorSig), // Fast path Ack (unkeyed, legacy)
    /// Keyed ack: carries the ObjectRef so the receiver can route to the correct in-flight entry.
    /// Replaces Ack for M-010+ to fix concurrent-transfer ambiguity.
    AckFor {
        object_ref: crate::types::ObjectRef,
        sig: crate::types::ValidatorSig,
    },
    Certificate(TransferCertificate),     // Fast path Certificate
    EpochSettlementTx(EpochSettlementTx), // Shared-object submission
    MissingCertSync {
        // SEC-003: Offline validator recovery
        agent: crate::types::AgentID,
        missing_versions: Vec<u64>,
    },
    MissingCertResponse {
        certs: Vec<TransferCertificate>,
    },
    /// M-015: epoch-settlement recovery sync (cursor protocol, O(1) wire size).
    ///
    /// Requester sends its latest_contiguous_epoch — the highest epoch N such that
    /// all epochs 1..=N are committed locally. Responder returns any records with
    /// epoch > latest_contiguous_epoch, capped at 64 per response (OOM guard).
    ///
    /// Replaces the original known_epochs: Vec<u64> design (O(N) wire size that would
    /// hit the 10MB frame ceiling at ~1.3M epochs, breaking sync liveness permanently).
    /// SEC-008: cursor approach eliminates the O(N) growth path.
    MissingEpochSync {
        latest_contiguous_epoch: u64,
    },
    MissingEpochResponse {
        records: Vec<StoredCheckpoint>,
    },
    /// Phase 1586: authenticated gRPC ingress is converted to a validator-owned
    /// epoch proposal. This is not a checkpoint and carries no external BLS authority.
    EpochProposal(EpochProposal),
    /// Phase 1586: validator signature over the EpochSettlementRecord derived
    /// from an EpochProposal. Originator aggregates quorum acks into an internal
    /// EpochCheckpoint before committing.
    EpochProposalAck(EpochProposalAck),
    EpochCheckpointMsg(EpochCheckpoint),
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, PartialEq, Eq)]
pub struct EpochProposal {
    pub submitter_agent_id: Vec<u8>,
    pub epoch_number: u64,
    pub state_root: CIDv1Root,
    pub spectral_hash: [u8; 32],
    pub epoch_data_hash: Vec<u8>,
    pub settlement_record_bytes: Vec<u8>,
    pub idempotency_key: String,
    pub not_before_unix_ms: u64,
    pub network_id: String,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct EpochProposalAck {
    pub idempotency_key: String,
    pub epoch_number: u64,
    pub proposal_commitment_sha256: Vec<u8>,
    pub proposal_sig: ValidatorSig,
    pub sig: ValidatorSig,
}

/// CDL-061: HTTP/3 structured framing envelope
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct GossipEnvelope {
    pub frame_type: u8, // 0x00 for DATA frame mimicking H3 structure
    pub peer_id: AgentID,
    pub payload: GossipMessage,
}

pub struct PeerNetwork {
    peer_certs: Arc<HashMap<u32, Vec<u8>>>,
    peer_agent_ids: Arc<HashMap<u32, AgentID>>,
    pub endpoint: Endpoint,
}

#[derive(Debug)]
struct PinnedCertVerifier {
    allowed_cert_ders: Vec<Vec<u8>>,
}

impl rustls::client::danger::ServerCertVerifier for PinnedCertVerifier {
    fn verify_server_cert(
        &self,
        end_entity: &CertificateDer<'_>,
        _intermediates: &[CertificateDer<'_>],
        _server_name: &ServerName<'_>,
        _ocsp_response: &[u8],
        _now: UnixTime,
    ) -> Result<ServerCertVerified, rustls::Error> {
        if self
            .allowed_cert_ders
            .iter()
            .any(|d| d.as_slice() == end_entity.as_ref())
        {
            Ok(ServerCertVerified::assertion())
        } else {
            Err(rustls::Error::General("unknown peer certificate".into()))
        }
    }

    fn verify_tls12_signature(
        &self,
        _message: &[u8],
        _cert: &CertificateDer<'_>,
        _dss: &rustls::DigitallySignedStruct,
    ) -> Result<rustls::client::danger::HandshakeSignatureValid, rustls::Error> {
        Err(rustls::Error::General("TLS 1.2 not supported".into()))
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &rustls::DigitallySignedStruct,
    ) -> Result<rustls::client::danger::HandshakeSignatureValid, rustls::Error> {
        rustls::crypto::verify_tls13_signature(
            message,
            cert,
            dss,
            &rustls::crypto::ring::default_provider().signature_verification_algorithms,
        )
    }

    fn supported_verify_schemes(&self) -> Vec<rustls::SignatureScheme> {
        rustls::crypto::ring::default_provider()
            .signature_verification_algorithms
            .supported_schemes()
    }
}

impl rustls::server::danger::ClientCertVerifier for PinnedCertVerifier {
    fn root_hint_subjects(&self) -> &[rustls::DistinguishedName] {
        &[]
    }

    fn verify_client_cert(
        &self,
        end_entity: &CertificateDer<'_>,
        _intermediates: &[CertificateDer<'_>],
        _now: UnixTime,
    ) -> Result<ClientCertVerified, rustls::Error> {
        if self
            .allowed_cert_ders
            .iter()
            .any(|d| d.as_slice() == end_entity.as_ref())
        {
            Ok(ClientCertVerified::assertion())
        } else {
            Err(rustls::Error::General("unknown client certificate".into()))
        }
    }

    fn offer_client_auth(&self) -> bool {
        true
    }
    fn client_auth_mandatory(&self) -> bool {
        true
    }

    fn verify_tls12_signature(
        &self,
        _message: &[u8],
        _cert: &CertificateDer<'_>,
        _dss: &rustls::DigitallySignedStruct,
    ) -> Result<rustls::client::danger::HandshakeSignatureValid, rustls::Error> {
        Err(rustls::Error::General("TLS 1.2 not supported".into()))
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &rustls::DigitallySignedStruct,
    ) -> Result<rustls::client::danger::HandshakeSignatureValid, rustls::Error> {
        rustls::crypto::verify_tls13_signature(
            message,
            cert,
            dss,
            &rustls::crypto::ring::default_provider().signature_verification_algorithms,
        )
    }

    fn supported_verify_schemes(&self) -> Vec<rustls::SignatureScheme> {
        rustls::crypto::ring::default_provider()
            .signature_verification_algorithms
            .supported_schemes()
    }
}

/// SEC-FIX-03: per-operation I/O timeout on all blocking network awaits.
/// A slow or malicious peer that trickles bytes or fills the QUIC flow control
/// window can hold async tasks indefinitely without these guards.
pub const IO_TIMEOUT_MS: u64 = 1500;
pub const MAX_GOSSIP_PAYLOAD_BYTES: usize = 10 * 1024 * 1024;

impl PeerNetwork {
    pub fn new_server(
        bind_addr: std::net::SocketAddr,
        peer_certs: HashMap<u32, Vec<u8>>,
        my_cert_der: Vec<u8>,
        my_key_der: Vec<u8>,
    ) -> Result<Self, ILCConsensusError> {
        rustls::crypto::ring::default_provider()
            .install_default()
            .ok();

        // Clone raw bytes before they are consumed by the server config; needed
        // to also build the outbound (client) config on the same endpoint.
        let my_cert_der_clone = my_cert_der.clone();
        let my_key_der_clone = my_key_der.clone();

        let cert = CertificateDer::from(my_cert_der);
        let key = PrivateKeyDer::Pkcs8(my_key_der.into());

        let allowed_ders: Vec<Vec<u8>> = peer_certs.values().cloned().collect();
        let allowed_ders_for_client = allowed_ders.clone();
        let verifier = Arc::new(PinnedCertVerifier {
            allowed_cert_ders: allowed_ders,
        });

        let mut server_crypto = rustls::ServerConfig::builder()
            .with_client_cert_verifier(verifier)
            .with_single_cert(vec![cert], key)
            .map_err(|e| ILCConsensusError::Other(format!("TLS error: {}", e)))?;

        server_crypto.alpn_protocols = vec![b"ilc-gossip".to_vec()];

        // `server_crypto` is a rustls 0.23 ServerConfig. quinn uses QuicServerConfig.
        let quic_server_crypto =
            quinn::crypto::rustls::QuicServerConfig::try_from(server_crypto)
                .map_err(|_| ILCConsensusError::Other("Quic crypto config failed".into()))?;

        let server_config = ServerConfig::with_crypto(Arc::new(quic_server_crypto));

        let mut endpoint = Endpoint::server(server_config, bind_addr)
            .map_err(|e| ILCConsensusError::Other(format!("Bind error: {}", e)))?;

        // Set client config so this endpoint can also open outbound connections to peers
        // (required for validator-to-validator gossip and epoch sync).
        {
            let cert = CertificateDer::from(my_cert_der_clone);
            let key = PrivateKeyDer::Pkcs8(my_key_der_clone.into());
            let client_verifier = Arc::new(PinnedCertVerifier {
                allowed_cert_ders: allowed_ders_for_client,
            });
            // SNI is intentionally not used as the validator identity authority
            // here. This closed validator-set transport authenticates peers by
            // exact DER certificate pinning plus the genesis validator_id ->
            // AgentID metadata map; DNS/SNI names are operator routing hints.
            let mut client_crypto = rustls::ClientConfig::builder()
                .dangerous()
                .with_custom_certificate_verifier(client_verifier)
                .with_client_auth_cert(vec![cert], key)
                .map_err(|e| ILCConsensusError::Other(format!("TLS client error: {}", e)))?;
            client_crypto.alpn_protocols = vec![b"ilc-gossip".to_vec()];
            let quic_client_crypto =
                quinn::crypto::rustls::QuicClientConfig::try_from(client_crypto).map_err(|_| {
                    ILCConsensusError::Other("Quic client crypto config failed".into())
                })?;
            endpoint.set_default_client_config(ClientConfig::new(Arc::new(quic_client_crypto)));
        }

        Ok(Self {
            peer_certs: Arc::new(peer_certs),
            peer_agent_ids: Arc::new(HashMap::new()),
            endpoint,
        })
    }

    pub fn new_client(
        bind_addr: std::net::SocketAddr,
        peer_certs: HashMap<u32, Vec<u8>>,
        my_cert_der: Vec<u8>,
        my_key_der: Vec<u8>,
    ) -> Result<Self, ILCConsensusError> {
        rustls::crypto::ring::default_provider()
            .install_default()
            .ok();
        let mut endpoint = Endpoint::client(bind_addr)
            .map_err(|e| ILCConsensusError::Other(format!("Bind error: {}", e)))?;

        let cert = CertificateDer::from(my_cert_der);
        let key = PrivateKeyDer::Pkcs8(my_key_der.into());

        let allowed_ders: Vec<Vec<u8>> = peer_certs.values().cloned().collect();
        let verifier = Arc::new(PinnedCertVerifier {
            allowed_cert_ders: allowed_ders,
        });

        let mut client_crypto = rustls::ClientConfig::builder()
            .dangerous()
            .with_custom_certificate_verifier(verifier)
            .with_client_auth_cert(vec![cert], key)
            .map_err(|e| ILCConsensusError::Other(format!("TLS error: {}", e)))?;

        client_crypto.alpn_protocols = vec![b"ilc-gossip".to_vec()];

        let quic_client_crypto =
            quinn::crypto::rustls::QuicClientConfig::try_from(client_crypto)
                .map_err(|_| ILCConsensusError::Other("Quic crypto config failed".into()))?;

        let client_config = ClientConfig::new(Arc::new(quic_client_crypto));
        endpoint.set_default_client_config(client_config);

        Ok(Self {
            peer_certs: Arc::new(peer_certs),
            peer_agent_ids: Arc::new(HashMap::new()),
            endpoint,
        })
    }

    pub fn with_peer_agent_ids(mut self, peer_agent_ids: HashMap<u32, AgentID>) -> Self {
        self.peer_agent_ids = Arc::new(peer_agent_ids);
        self
    }

    /// Verifies static Topology securely by mapping the physical native connection identity bounds internally (SEC-006)
    pub fn authenticate_peer_tls(
        &self,
        connection: &Connection,
    ) -> Result<AgentID, ILCConsensusError> {
        let identities = connection
            .peer_identity()
            .ok_or_else(|| ILCConsensusError::Other("No TLS peer identity provided".into()))?;

        let certs = identities
            .downcast_ref::<Vec<CertificateDer<'static>>>()
            .ok_or_else(|| ILCConsensusError::Other("Invalid certificate hierarchy".into()))?;

        // MEDIUM-005 fix: check for empty cert chain before indexing.
        let peer_cert_der = certs
            .first()
            .ok_or_else(|| ILCConsensusError::Other("Empty TLS cert chain".into()))?
            .as_ref();

        for (id, der) in self.peer_certs.iter() {
            if der == peer_cert_der {
                if let Some(agent_id) = self.peer_agent_ids.get(id).copied() {
                    return Ok(agent_id);
                }
                #[cfg(test)]
                {
                    return Ok(crate::types::test_agent_id(*id));
                }
                #[cfg(not(test))]
                {
                    return Err(ILCConsensusError::Other(format!(
                        "TLS validator_id={} missing genesis AgentID metadata",
                        id
                    )));
                }
            }
        }

        Err(ILCConsensusError::Other(
            "TLS Identity not found in Validator Static Registry".into(),
        ))
    }

    pub async fn transmit(
        &self,
        mut send: SendStream,
        env: GossipEnvelope,
    ) -> Result<(), ILCConsensusError> {
        let bytes = bincode::DefaultOptions::new()
            .with_fixint_encoding()
            .serialize(&env)
            .map_err(|_| ILCConsensusError::Other("Envelope map error".into()))?;

        let timeout = tokio::time::Duration::from_millis(IO_TIMEOUT_MS);

        tokio::time::timeout(timeout, send.write_all(&(bytes.len() as u32).to_be_bytes()))
            .await
            .map_err(|_| ILCConsensusError::Other("Transmit: length write timed out".into()))?
            .map_err(|_| ILCConsensusError::Other("Write length fail".into()))?;

        tokio::time::timeout(timeout, send.write_all(&bytes))
            .await
            .map_err(|_| ILCConsensusError::Other("Transmit: payload write timed out".into()))?
            .map_err(|_| ILCConsensusError::Other("Write payload fail".into()))?;

        // finish() is synchronous — marks the stream end without blocking.
        send.finish()
            .map_err(|_| ILCConsensusError::Other("Send flush exception".into()))?;

        Ok(())
    }

    pub async fn receive(
        &self,
        connection: &Connection,
        mut recv: RecvStream,
    ) -> Result<GossipEnvelope, ILCConsensusError> {
        let authenticated_id = self.authenticate_peer_tls(connection)?;

        let timeout = tokio::time::Duration::from_millis(IO_TIMEOUT_MS);

        let mut len_buf = [0u8; 4];
        tokio::time::timeout(timeout, recv.read_exact(&mut len_buf))
            .await
            .map_err(|_| ILCConsensusError::Other("Receive: length read timed out".into()))?
            .map_err(|_| ILCConsensusError::Other("Read fail length".into()))?;

        let target_len = u32::from_be_bytes(len_buf) as usize;
        if target_len > MAX_GOSSIP_PAYLOAD_BYTES {
            return Err(ILCConsensusError::Other(
                "Payload excessive length bound".into(),
            ));
        }

        let mut buf = vec![0u8; target_len];
        tokio::time::timeout(timeout, recv.read_exact(&mut buf))
            .await
            .map_err(|_| ILCConsensusError::Other("Receive: payload read timed out".into()))?
            .map_err(|_| ILCConsensusError::Other("Read fail payload".into()))?;

        let envelope = deserialize_gossip_envelope_bytes(&buf)?;

        // SEC-006: Cryptographically bind application payload to mathematical TLS identity
        if envelope.peer_id != authenticated_id {
            return Err(ILCConsensusError::Other(format!(
                "Spoofed peer ID: claimed {}, actually established via mTLS as {}",
                envelope.peer_id, authenticated_id
            )));
        }

        Ok(envelope)
    }
}

fn deserialize_gossip_envelope_bytes(buf: &[u8]) -> Result<GossipEnvelope, ILCConsensusError> {
    let fixed_options = bincode::DefaultOptions::new()
        .with_fixint_encoding()
        .allow_trailing_bytes()
        .with_limit(MAX_GOSSIP_PAYLOAD_BYTES as u64);
    fixed_options.deserialize(buf).or_else(|fixed_err| {
        let legacy_options = bincode::DefaultOptions::new()
            .allow_trailing_bytes()
            .with_limit(MAX_GOSSIP_PAYLOAD_BYTES as u64);
        legacy_options.deserialize(buf).map_err(|legacy_err| {
            ILCConsensusError::Other(format!(
                "Corrupted CDL-061 Envelope parsed: fixed_bincode={}; legacy_bincode={}",
                fixed_err, legacy_err
            ))
        })
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::AgentSig;
    use crate::types::{
        AgentID, AggSig, CIDv1Root, ECUTransfer, EpochCheckpoint, EpochSeq, EpochSettlementRecord,
        ObjectRef, ILC_EPOCH_SIG_DST,
    };
    use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
    use tokio::time::Duration;

    fn dummy_agent_sig() -> AgentSig {
        let ikm = [42u8; 32];
        let sk = blst::min_pk::SecretKey::key_gen(&ikm, &[]).unwrap();
        AgentSig(sk.sign(b"dummy", crate::types::AGENT_TRANSFER_DST, &[]))
    }

    fn generate_ephemeral_cert() -> (Vec<u8>, Vec<u8>) {
        let rcgen::CertifiedKey { cert, key_pair } =
            rcgen::generate_simple_self_signed(vec!["localhost".into()]).unwrap();
        let cert_der = cert.der().to_vec();
        let key_der = key_pair.serialize_der();
        (cert_der, key_der)
    }

    fn mock_socket() -> SocketAddr {
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0))
    }

    #[test]
    fn test_epoch_checkpoint_envelope_bincode_round_trip() {
        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([7u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [7u8; 32],
            not_before_unix_ms: 0,
        };
        let msg_bytes = bincode::serialize(&record).unwrap();
        let sk_1 = blst::min_pk::SecretKey::key_gen(&[1u8; 32], &[]).unwrap();
        let sk_2 = blst::min_pk::SecretKey::key_gen(&[2u8; 32], &[]).unwrap();
        let sig_1 = sk_1.sign(&msg_bytes, ILC_EPOCH_SIG_DST, &[]);
        let sig_2 = sk_2.sign(&msg_bytes, ILC_EPOCH_SIG_DST, &[]);
        let sig_refs = vec![&sig_1, &sig_2];
        let agg = blst::min_pk::AggregateSignature::aggregate(&sig_refs, false).unwrap();
        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: crate::types::test_agent_id(2),
            payload: GossipMessage::EpochCheckpointMsg(EpochCheckpoint {
                record,
                sigs: AggSig(agg),
                signers: vec![
                    crate::types::test_agent_id(1),
                    crate::types::test_agent_id(2),
                ],
            }),
        };

        let bytes = bincode::DefaultOptions::new()
            .with_fixint_encoding()
            .serialize(&envelope)
            .unwrap();
        let decoded: GossipEnvelope = bincode::DefaultOptions::new()
            .with_fixint_encoding()
            .allow_trailing_bytes()
            .with_limit(MAX_GOSSIP_PAYLOAD_BYTES as u64)
            .deserialize(&bytes)
            .unwrap();

        assert_eq!(decoded.peer_id, crate::types::test_agent_id(2));
        match decoded.payload {
            GossipMessage::EpochCheckpointMsg(checkpoint) => {
                assert_eq!(checkpoint.record.epoch, EpochSeq(1));
                assert_eq!(
                    checkpoint.signers,
                    vec![
                        crate::types::test_agent_id(1),
                        crate::types::test_agent_id(2)
                    ]
                );
            }
            other => panic!("unexpected payload: {:?}", other),
        }
    }

    #[test]
    fn test_legacy_bincode_fallback_decodes_under_size_limit() {
        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: crate::types::test_agent_id(2),
            payload: GossipMessage::MissingEpochSync {
                latest_contiguous_epoch: 7,
            },
        };
        let legacy_bytes = bincode::serialize(&envelope).unwrap();

        let decoded = deserialize_gossip_envelope_bytes(&legacy_bytes).unwrap();

        assert_eq!(decoded.peer_id, envelope.peer_id);
        match decoded.payload {
            GossipMessage::MissingEpochSync {
                latest_contiguous_epoch,
            } => assert_eq!(latest_contiguous_epoch, 7),
            other => panic!("unexpected payload: {:?}", other),
        }
    }

    #[tokio::test]
    async fn test_two_validators_loopback() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (client_cert, client_key) = generate_ephemeral_cert();

        let mut server_peers = HashMap::new();
        server_peers.insert(2, client_cert.clone());

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let server_node =
            PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node =
            PeerNetwork::new_client(mock_socket(), client_peers, client_cert, client_key).unwrap();

        let server_task = tokio::spawn(async move {
            let incoming = server_node.endpoint.accept().await.unwrap();
            let connection = incoming.await.unwrap();
            let (_send, recv) = connection.accept_bi().await.unwrap();

            let envelope = server_node.receive(&connection, recv).await.unwrap();

            assert_eq!(envelope.frame_type, 0x00);
            match envelope.payload {
                GossipMessage::BroadcastHonest(_) => Ok(()),
                _ => Err("Invalid Payload"),
            }
        });

        let conn = client_node
            .endpoint
            .connect(bound_addr, "localhost")
            .unwrap()
            .await
            .unwrap();
        let (send, _recv) = conn.open_bi().await.unwrap();

        let tx = ECUTransfer {
            object_ref: ObjectRef {
                agent: AgentID([1; 48]),
                version: 0,
            },
            to: AgentID([2; 48]),
            amount_micro_ecu: 10,
            transfer_class: crate::types::TransferClass::Contribution,
            sender_sig: dummy_agent_sig(),
        };

        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: crate::types::test_agent_id(2),
            payload: GossipMessage::BroadcastHonest(tx),
        };

        client_node.transmit(send, envelope).await.unwrap();

        let result = tokio::time::timeout(Duration::from_secs(2), server_task)
            .await
            .unwrap()
            .unwrap();
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_unknown_peer_rejected() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (unauth_cert, unauth_key) = generate_ephemeral_cert(); // Validator 3

        let mut server_peers = HashMap::new();
        // Server expects Val 2, not Val 3!
        server_peers.insert(2, vec![1, 2, 3]);

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let server_node =
            PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node =
            PeerNetwork::new_client(mock_socket(), client_peers, unauth_cert, unauth_key).unwrap();

        let server_task = tokio::spawn(async move {
            if let Some(incoming) = server_node.endpoint.accept().await {
                // If it connects or fails is fine, mTLS breaks internally
                let _ = incoming.await;
            }
        });

        // QUIC TLS 1.3 1-RTT client connections complete superficially prior to Server Certificate Verification
        // We assert mTLS failure inherently drops the connection breaking stream boundaries natively.
        let conn_result = client_node
            .endpoint
            .connect(bound_addr, "localhost")
            .unwrap()
            .await;
        if let Ok(conn) = conn_result {
            // Await connection telemetry ensuring rustls closes peer mapping over background routing loops natively.
            let close_reason =
                tokio::time::timeout(tokio::time::Duration::from_secs(1), conn.closed()).await;
            assert!(
                close_reason.is_ok(),
                "Connection must close cleanly due to mTLS strict checking parameters"
            );
        } else {
            assert!(conn_result.is_err());
        }

        server_task.abort();
    }

    #[tokio::test]
    async fn test_spoofed_peer_id_rejected() {
        // Val 2 attacks server, authenticates correctly as Val 2 natively on TLS... but declares themselves as Val 3 on bincode!
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (client_cert, client_key) = generate_ephemeral_cert(); // Actually Val 2

        let mut server_peers = HashMap::new();
        server_peers.insert(2, client_cert.clone());
        server_peers.insert(3, vec![9, 9, 9]); // Some other node

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let server_node =
            PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node =
            PeerNetwork::new_client(mock_socket(), client_peers, client_cert, client_key).unwrap();

        let server_task = tokio::spawn(async move {
            let incoming = server_node.endpoint.accept().await.unwrap();
            let connection = incoming.await.unwrap();
            let (_send, recv) = connection.accept_bi().await.unwrap();

            // Server correctly maps connection to Val 2... but envelope says Val 3.
            let result = server_node.receive(&connection, recv).await;
            assert!(result.is_err());
            let err_str = format!("{:?}", result.unwrap_err());
            assert!(
                err_str.contains("Spoofed peer ID: claimed 3, actually established via mTLS as 2")
            );
        });

        let conn = client_node
            .endpoint
            .connect(bound_addr, "localhost")
            .unwrap()
            .await
            .unwrap();
        let (send, _recv) = conn.open_bi().await.unwrap();

        // Attacker writes peer 3 internally!
        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: crate::types::test_agent_id(3),
            payload: GossipMessage::MissingCertSync {
                agent: AgentID([1; 48]),
                missing_versions: vec![1],
            },
        };

        client_node.transmit(send, envelope).await.unwrap();
        let _ = tokio::time::timeout(Duration::from_secs(2), server_task)
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_plaintext_connection_rejected() {
        let (server_cert, server_key) = generate_ephemeral_cert();

        let server_peers = HashMap::new();
        let server_node =
            PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        // Send raw garbage directly targeting QUIC structural bounds
        let sock = tokio::net::UdpSocket::bind("127.0.0.1:0").await.unwrap();
        sock.send_to(b"null-payload", bound_addr).await.unwrap();

        let result =
            tokio::time::timeout(Duration::from_millis(200), server_node.endpoint.accept()).await;

        assert!(
            result.is_err(),
            "garbage UDP bytes must not produce an accepted connection"
        );
    }

    #[tokio::test]
    async fn test_offline_validator_catchup() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (client_cert, client_key) = generate_ephemeral_cert();

        let mut server_peers = HashMap::new();
        server_peers.insert(2, client_cert.clone());

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let server_node =
            PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node =
            PeerNetwork::new_client(mock_socket(), client_peers, client_cert, client_key).unwrap();

        let server_task = tokio::spawn(async move {
            let incoming = server_node.endpoint.accept().await.unwrap();
            let connection = incoming.await.unwrap();
            let (send, recv) = connection.accept_bi().await.unwrap();

            let envelope = server_node.receive(&connection, recv).await.unwrap();

            if let GossipMessage::MissingCertSync {
                agent: _,
                missing_versions: _,
            } = envelope.payload
            {
                let response = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: crate::types::test_agent_id(1),
                    payload: GossipMessage::MissingCertResponse { certs: vec![] },
                };
                server_node.transmit(send, response).await.unwrap();
                tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
            } else {
                panic!("Invalid payload");
            }
        });

        let conn = client_node
            .endpoint
            .connect(bound_addr, "localhost")
            .unwrap()
            .await
            .unwrap();
        let (send, recv) = conn.open_bi().await.unwrap();

        let sync_req = GossipEnvelope {
            frame_type: 0x00,
            peer_id: crate::types::test_agent_id(2),
            payload: GossipMessage::MissingCertSync {
                agent: AgentID([1; 48]),
                missing_versions: vec![5, 6, 7],
            },
        };

        client_node.transmit(send, sync_req).await.unwrap();

        let response_env = client_node.receive(&conn, recv).await.unwrap();
        match response_env.payload {
            GossipMessage::MissingCertResponse { .. } => assert!(true),
            _ => panic!("Expected MissingCertResponse"),
        }

        let _ = tokio::time::timeout(Duration::from_secs(2), server_task)
            .await
            .unwrap();
    }
}
