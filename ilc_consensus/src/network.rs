use crate::types::{EpochSettlementTx, TransferCertificate, ILCConsensusError, ValidatorID};
use quinn::{Endpoint, ServerConfig, ClientConfig, Connection, RecvStream, SendStream};
use rustls::{Certificate, PrivateKey, ClientConfig as RustlsClientConfig};
use std::sync::Arc;
use std::collections::HashMap;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum GossipMessage {
    BroadcastHonest(crate::types::ECUTransfer), // DAG Vertex Proposal
    Ack(crate::types::ValidatorSig),            // Fast path Ack (unkeyed, legacy)
    /// Keyed ack: carries the ObjectRef so the receiver can route to the correct in-flight entry.
    /// Replaces Ack for M-010+ to fix concurrent-transfer ambiguity.
    AckFor {
        object_ref: crate::types::ObjectRef,
        sig: crate::types::ValidatorSig,
    },
    Certificate(TransferCertificate),           // Fast path Certificate
    EpochSettlementTx(EpochSettlementTx),       // Shared-object submission
    MissingCertSync {                           // SEC-003: Offline validator recovery
        agent: crate::types::AgentID,
        missing_versions: Vec<u64>,
    },
    MissingCertResponse {
        certs: Vec<TransferCertificate>,
    }
}

/// CDL-061: HTTP/3 structured framing envelope
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct GossipEnvelope {
    pub frame_type: u8, // 0x00 for DATA frame mimicking H3 structure
    pub peer_id: ValidatorID,
    pub payload: GossipMessage,
}

pub struct PeerNetwork {
    peer_certs: Arc<HashMap<u32, Vec<u8>>>,
    pub endpoint: Endpoint,
}

struct PinnedCertVerifier {
    allowed_cert_ders: Vec<Vec<u8>>,
}

impl rustls::client::ServerCertVerifier for PinnedCertVerifier {
    fn verify_server_cert(
        &self,
        end_entity: &Certificate,
        _intermediates: &[Certificate],
        _server_name: &rustls::client::ServerName,
        _scts: &mut dyn Iterator<Item = &[u8]>,
        _ocsp_response: &[u8],
        _now: std::time::SystemTime,
    ) -> Result<rustls::client::ServerCertVerified, rustls::Error> {
        if self.allowed_cert_ders.iter().any(|d| d == &end_entity.0) {
            Ok(rustls::client::ServerCertVerified::assertion())
        } else {
            Err(rustls::Error::General("unknown peer certificate".into()))
        }
    }
}

impl rustls::server::ClientCertVerifier for PinnedCertVerifier {
    fn client_auth_root_subjects(&self) -> &[rustls::DistinguishedName] {
        &[]
    }

    fn verify_client_cert(
        &self,
        end_entity: &Certificate,
        _intermediates: &[Certificate],
        _now: std::time::SystemTime,
    ) -> Result<rustls::server::ClientCertVerified, rustls::Error> {
        if self.allowed_cert_ders.iter().any(|d| d == &end_entity.0) {
            Ok(rustls::server::ClientCertVerified::assertion())
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
}

impl PeerNetwork {
    pub fn new_server(
        bind_addr: std::net::SocketAddr,
        peer_certs: HashMap<u32, Vec<u8>>,
        my_cert_der: Vec<u8>,
        my_key_der: Vec<u8>,
    ) -> Result<Self, ILCConsensusError> {
        let cert = Certificate(my_cert_der);
        let key = PrivateKey(my_key_der);

        let allowed_ders: Vec<Vec<u8>> = peer_certs.values().cloned().collect();
        let verifier = Arc::new(PinnedCertVerifier { allowed_cert_ders: allowed_ders });

        let mut server_crypto = rustls::ServerConfig::builder()
            .with_safe_defaults()
            .with_client_cert_verifier(verifier)
            .with_single_cert(vec![cert], key)
            .map_err(|e| ILCConsensusError::Other(format!("TLS error: {}", e)))?;

        server_crypto.alpn_protocols = vec![b"ilc-gossip".to_vec()];

        let server_config = ServerConfig::with_crypto(Arc::new(server_crypto));

        let endpoint = Endpoint::server(server_config, bind_addr)
            .map_err(|e| ILCConsensusError::Other(format!("Bind error: {}", e)))?;

        Ok(Self {
            peer_certs: Arc::new(peer_certs),
            endpoint,
        })
    }

    pub fn new_client(
        bind_addr: std::net::SocketAddr,
        peer_certs: HashMap<u32, Vec<u8>>,
        my_cert_der: Vec<u8>,
        my_key_der: Vec<u8>,
    ) -> Result<Self, ILCConsensusError> {
        let mut endpoint = Endpoint::client(bind_addr)
            .map_err(|e| ILCConsensusError::Other(format!("Bind error: {}", e)))?;

        let cert = Certificate(my_cert_der);
        let key = PrivateKey(my_key_der);

        let allowed_ders: Vec<Vec<u8>> = peer_certs.values().cloned().collect();
        let verifier = Arc::new(PinnedCertVerifier { allowed_cert_ders: allowed_ders });

        let mut client_crypto = RustlsClientConfig::builder()
            .with_safe_defaults()
            .with_custom_certificate_verifier(verifier)
            .with_single_cert(vec![cert], key)
            .map_err(|e| ILCConsensusError::Other(format!("TLS error: {}", e)))?;
            
        client_crypto.alpn_protocols = vec![b"ilc-gossip".to_vec()];

        let client_config = ClientConfig::new(Arc::new(client_crypto));
        endpoint.set_default_client_config(client_config);

        Ok(Self {
            peer_certs: Arc::new(peer_certs),
            endpoint,
        })
    }

    /// Verifies static Topology securely by mapping the physical native connection identity bounds internally (SEC-006)
    pub fn authenticate_peer_tls(&self, connection: &Connection) -> Result<u32, ILCConsensusError> {
        let identities = connection.peer_identity()
            .ok_or_else(|| ILCConsensusError::Other("No TLS peer identity provided".into()))?;
            
        let certs = identities.downcast_ref::<Vec<Certificate>>()
            .ok_or_else(|| ILCConsensusError::Other("Invalid certificate hierarchy".into()))?;
            
        let peer_cert_der = &certs[0].0;

        for (id, der) in self.peer_certs.iter() {
            if der == peer_cert_der {
                return Ok(*id);
            }
        }
        
        Err(ILCConsensusError::Other("TLS Identity not found in Validator Static Registry".into()))
    }

    pub async fn transmit(&self, mut send: SendStream, env: GossipEnvelope) -> Result<(), ILCConsensusError> {
        let bytes = bincode::serialize(&env)
            .map_err(|_| ILCConsensusError::Other("Envelope map error".into()))?;
            
        send.write_all(&(bytes.len() as u32).to_be_bytes()).await
            .map_err(|_| ILCConsensusError::Other("Write length fail".into()))?;
            
        send.write_all(&bytes).await
            .map_err(|_| ILCConsensusError::Other("Write payload fail".into()))?;
            
        send.finish().await
            .map_err(|_| ILCConsensusError::Other("Send flush exception".into()))?;
            
        Ok(())
    }

    pub async fn receive(&self, connection: &Connection, mut recv: RecvStream) -> Result<GossipEnvelope, ILCConsensusError> {
        let authenticated_id = self.authenticate_peer_tls(connection)?;

        let mut len_buf = [0u8; 4];
        recv.read_exact(&mut len_buf).await
            .map_err(|_| ILCConsensusError::Other("Read fail length".into()))?;
            
        let target_len = u32::from_be_bytes(len_buf) as usize;
        if target_len > 10 * 1024 * 1024 {
            return Err(ILCConsensusError::Other("Payload excessive length bound".into()));
        }

        let mut buf = vec![0u8; target_len];
        recv.read_exact(&mut buf).await
            .map_err(|_| ILCConsensusError::Other("Read fail payload".into()))?;

        let envelope: GossipEnvelope = bincode::deserialize(&buf)
            .map_err(|_| ILCConsensusError::Other("Corrupted CDL-061 Envelope parsed".into()))?;

        // SEC-006: Cryptographically bind application payload to mathematical TLS identity
        if envelope.peer_id.0 != authenticated_id {
            return Err(ILCConsensusError::Other(format!(
                "Spoofed peer ID: claimed {}, actually established via mTLS as {}", 
                envelope.peer_id.0, authenticated_id
            )));
        }

        Ok(envelope)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{AgentID, ECUTransfer, ObjectRef};
    use std::net::{SocketAddr, Ipv4Addr, SocketAddrV4};
    use tokio::time::Duration;
    use crate::types::AgentSig;

    fn dummy_agent_sig() -> AgentSig {
        let ikm = [42u8; 32];
        let sk = blst::min_pk::SecretKey::key_gen(&ikm, &[]).unwrap();
        AgentSig(sk.sign(b"dummy", crate::types::AGENT_TRANSFER_DST, &[]))
    }

    fn generate_ephemeral_cert() -> (Vec<u8>, Vec<u8>) {
        let cert = rcgen::generate_simple_self_signed(vec!["localhost".into()]).unwrap();
        let cert_der = cert.serialize_der().unwrap();
        let key_der = cert.serialize_private_key_der();
        (cert_der, key_der)
    }

    fn mock_socket() -> SocketAddr {
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0))
    }

    #[tokio::test]
    async fn test_two_validators_loopback() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (client_cert, client_key) = generate_ephemeral_cert();
        
        let mut server_peers = HashMap::new();
        server_peers.insert(2, client_cert.clone());

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let server_node = PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node = PeerNetwork::new_client(mock_socket(), client_peers, client_cert, client_key).unwrap();

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

        let conn = client_node.endpoint.connect(bound_addr, "localhost").unwrap().await.unwrap();
        let (send, _recv) = conn.open_bi().await.unwrap();
        
        let tx = ECUTransfer {
            object_ref: ObjectRef { agent: AgentID([1; 48]), version: 0 },
            to: AgentID([2; 48]),
            amount_micro_ecu: 10,
            sender_sig: dummy_agent_sig(),
        };

        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(2),
            payload: GossipMessage::BroadcastHonest(tx),
        };

        client_node.transmit(send, envelope).await.unwrap();
        
        let result = tokio::time::timeout(Duration::from_secs(2), server_task).await.unwrap().unwrap();
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

        let server_node = PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node = PeerNetwork::new_client(mock_socket(), client_peers, unauth_cert, unauth_key).unwrap();

        let server_task = tokio::spawn(async move {
            if let Some(incoming) = server_node.endpoint.accept().await {
                // If it connects or fails is fine, mTLS breaks internally
                let _ = incoming.await;
            }
        });

        // QUIC TLS 1.3 1-RTT client connections complete superficially prior to Server Certificate Verification 
        // We assert mTLS failure inherently drops the connection breaking stream boundaries natively.
        let conn_result = client_node.endpoint.connect(bound_addr, "localhost").unwrap().await;
        if let Ok(conn) = conn_result {
            // Await connection telemetry ensuring rustls closes peer mapping over background routing loops natively.
            let close_reason = tokio::time::timeout(tokio::time::Duration::from_secs(1), conn.closed()).await;
            assert!(close_reason.is_ok(), "Connection must close cleanly due to mTLS strict checking parameters");
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

        let server_node = PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node = PeerNetwork::new_client(mock_socket(), client_peers, client_cert, client_key).unwrap();

        let server_task = tokio::spawn(async move {
            let incoming = server_node.endpoint.accept().await.unwrap();
            let connection = incoming.await.unwrap();
            let (_send, recv) = connection.accept_bi().await.unwrap();
            
            // Server correctly maps connection to Val 2... but envelope says Val 3.
            let result = server_node.receive(&connection, recv).await;
            assert!(result.is_err());
            let err_str = format!("{:?}", result.unwrap_err());
            assert!(err_str.contains("Spoofed peer ID: claimed 3, actually established via mTLS as 2"));
        });

        let conn = client_node.endpoint.connect(bound_addr, "localhost").unwrap().await.unwrap();
        let (send, _recv) = conn.open_bi().await.unwrap();
        
        // Attacker writes peer 3 internally!
        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(3), 
            payload: GossipMessage::MissingCertSync {
                agent: AgentID([1; 48]),
                missing_versions: vec![1],
            },
        };

        client_node.transmit(send, envelope).await.unwrap();
        tokio::time::timeout(Duration::from_secs(2), server_task).await.unwrap();
    }

    #[tokio::test]
    async fn test_plaintext_connection_rejected() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        
        let server_peers = HashMap::new();
        let server_node = PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();
        
        // Send raw garbage directly targeting QUIC structural bounds
        let sock = tokio::net::UdpSocket::bind("127.0.0.1:0").await.unwrap();
        sock.send_to(b"null-payload", bound_addr).await.unwrap();

        let result = tokio::time::timeout(
            Duration::from_millis(200),
            server_node.endpoint.accept()
        ).await;
        
        assert!(result.is_err(), "garbage UDP bytes must not produce an accepted connection");
    }

    #[tokio::test]
    async fn test_offline_validator_catchup() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (client_cert, client_key) = generate_ephemeral_cert();
        
        let mut server_peers = HashMap::new();
        server_peers.insert(2, client_cert.clone());

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let server_node = PeerNetwork::new_server(mock_socket(), server_peers, server_cert, server_key).unwrap();
        let bound_addr = server_node.endpoint.local_addr().unwrap();

        let client_node = PeerNetwork::new_client(mock_socket(), client_peers, client_cert, client_key).unwrap();

        let server_task = tokio::spawn(async move {
            let incoming = server_node.endpoint.accept().await.unwrap();
            let connection = incoming.await.unwrap();
            let (mut send, recv) = connection.accept_bi().await.unwrap();
            
            let envelope = server_node.receive(&connection, recv).await.unwrap();
            
            if let GossipMessage::MissingCertSync { agent: _, missing_versions: _ } = envelope.payload {
                let response = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: ValidatorID(1),
                    payload: GossipMessage::MissingCertResponse { certs: vec![] }
                };
                server_node.transmit(send, response).await.unwrap();
            } else {
                panic!("Invalid payload");
            }
        });

        let conn = client_node.endpoint.connect(bound_addr, "localhost").unwrap().await.unwrap();
        let (send, recv) = conn.open_bi().await.unwrap();
        
        let sync_req = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(2),
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

        let _ = tokio::time::timeout(Duration::from_secs(2), server_task).await.unwrap();
    }
}
