//! Phase 1386c persistent QUIC session proof.
//!
//! This module keeps validator connectivity authority outside hardcoded peer
//! lists. The only constructor for [`EndpointProjection`] rebuilds a read-only
//! projection from signed `QUIC_ENDPOINT` graph edges for one topology epoch.

use crate::network::{GossipEnvelope, PeerNetwork, IO_TIMEOUT_MS};
use crate::types::{ILCConsensusError, ValidatorID};
use quinn::Connection;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::path::Path;
use std::sync::Arc;
use tokio::sync::Mutex;

pub const PHASE_1386C_CONNECT_TIMEOUT_MS: u64 = 600;
pub const MAX_ENDPOINT_PROJECTION_BYTES: u64 = 1024 * 1024;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EndpointKind {
    Direct,
    Relay,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct QuicEndpointEdge {
    pub validator_id: ValidatorID,
    pub topology_epoch: u64,
    pub endpoint_kind: EndpointKind,
    pub addr: SocketAddr,
    pub server_name: String,
    pub protocol_version: String,
    pub signer_agent_id: String,
    pub signature_ref: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EndpointProjection {
    topology_epoch: u64,
    source_snapshot_hash: String,
    direct_endpoints: HashMap<u32, QuicEndpointEdge>,
    relay_endpoints: HashMap<u32, QuicEndpointEdge>,
}

impl EndpointProjection {
    pub fn rebuild_from_signed_edges(
        topology_epoch: u64,
        source_snapshot_hash: String,
        signed_edges: Vec<QuicEndpointEdge>,
    ) -> Result<Self, ILCConsensusError> {
        if source_snapshot_hash.trim().is_empty() {
            return Err(ILCConsensusError::Other(
                "endpoint projection source snapshot hash is empty".into(),
            ));
        }

        let mut direct_endpoints = HashMap::new();
        let mut relay_endpoints = HashMap::new();

        for edge in signed_edges {
            validate_signed_endpoint_edge(topology_epoch, &edge)?;
            let validator_key = edge.validator_id.0;
            match edge.endpoint_kind {
                EndpointKind::Direct => {
                    if direct_endpoints.insert(validator_key, edge).is_some() {
                        return Err(ILCConsensusError::Other(format!(
                            "duplicate direct endpoint for validator_id={}",
                            validator_key
                        )));
                    }
                }
                EndpointKind::Relay => {
                    if relay_endpoints.insert(validator_key, edge).is_some() {
                        return Err(ILCConsensusError::Other(format!(
                            "duplicate relay endpoint for validator_id={}",
                            validator_key
                        )));
                    }
                }
            }
        }

        Ok(Self {
            topology_epoch,
            source_snapshot_hash,
            direct_endpoints,
            relay_endpoints,
        })
    }

    pub fn topology_epoch(&self) -> u64 {
        self.topology_epoch
    }

    pub fn source_snapshot_hash(&self) -> &str {
        &self.source_snapshot_hash
    }

    pub fn direct_endpoint(&self, validator_id: ValidatorID) -> Option<&QuicEndpointEdge> {
        self.direct_endpoints.get(&validator_id.0)
    }

    pub fn relay_endpoint(&self, validator_id: ValidatorID) -> Option<&QuicEndpointEdge> {
        self.relay_endpoints.get(&validator_id.0)
    }

    pub fn validator_ids(&self) -> Vec<ValidatorID> {
        let mut ids: Vec<u32> = self
            .direct_endpoints
            .keys()
            .chain(self.relay_endpoints.keys())
            .copied()
            .collect();
        ids.sort_unstable();
        ids.dedup();
        ids.into_iter().map(ValidatorID).collect()
    }

    pub fn preferred_peer_addrs(&self) -> Vec<(ValidatorID, SocketAddr)> {
        let mut peers = Vec::new();
        for validator_id in self.validator_ids() {
            if let Some(edge) = self.direct_endpoint(validator_id) {
                peers.push((validator_id, edge.addr));
            } else if let Some(edge) = self.relay_endpoint(validator_id) {
                peers.push((validator_id, edge.addr));
            }
        }
        peers
    }
}

#[derive(Debug, Deserialize)]
struct EndpointProjectionDocument {
    topology_epoch: u64,
    source_snapshot_hash: String,
    signed_edges: Vec<QuicEndpointEdge>,
}

pub fn load_endpoint_projection_from_path(
    path: &Path,
) -> Result<EndpointProjection, ILCConsensusError> {
    let metadata = std::fs::metadata(path).map_err(|e| {
        ILCConsensusError::Other(format!("endpoint projection metadata error: {}", e))
    })?;
    if metadata.len() > MAX_ENDPOINT_PROJECTION_BYTES {
        return Err(ILCConsensusError::Other(format!(
            "endpoint projection exceeds {} byte bound",
            MAX_ENDPOINT_PROJECTION_BYTES
        )));
    }
    let raw = std::fs::read_to_string(path)
        .map_err(|e| ILCConsensusError::Other(format!("endpoint projection read error: {}", e)))?;
    let doc: EndpointProjectionDocument = serde_json::from_str(&raw)
        .map_err(|e| ILCConsensusError::Other(format!("endpoint projection parse error: {}", e)))?;
    EndpointProjection::rebuild_from_signed_edges(
        doc.topology_epoch,
        doc.source_snapshot_hash,
        doc.signed_edges,
    )
}

fn validate_signed_endpoint_edge(
    topology_epoch: u64,
    edge: &QuicEndpointEdge,
) -> Result<(), ILCConsensusError> {
    if edge.topology_epoch != topology_epoch {
        return Err(ILCConsensusError::Other(format!(
            "stale endpoint edge: edge_epoch={} projection_epoch={}",
            edge.topology_epoch, topology_epoch
        )));
    }
    if edge.protocol_version.trim().is_empty() {
        return Err(ILCConsensusError::Other(
            "endpoint protocol_version is empty".into(),
        ));
    }
    if edge.server_name.trim().is_empty() {
        return Err(ILCConsensusError::Other(
            "endpoint server_name is empty".into(),
        ));
    }
    if edge.signer_agent_id.trim().is_empty() {
        return Err(ILCConsensusError::Other(
            "endpoint signer_agent_id is empty".into(),
        ));
    }
    if edge.signature_ref.trim().is_empty() {
        return Err(ILCConsensusError::Other(
            "endpoint signature_ref is empty".into(),
        ));
    }
    Ok(())
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SessionPath {
    DirectQuic,
    Cdl078RelayFallback,
}

#[derive(Debug, Clone)]
pub struct PersistentQuicSession {
    pub validator_id: ValidatorID,
    pub topology_epoch: u64,
    pub path: SessionPath,
    pub connection: Connection,
}

pub struct PersistentQuicSessionManager {
    network: Arc<PeerNetwork>,
    projection: Arc<EndpointProjection>,
    sessions: Mutex<HashMap<u32, PersistentQuicSession>>,
}

impl PersistentQuicSessionManager {
    pub fn new(network: Arc<PeerNetwork>, projection: EndpointProjection) -> Self {
        Self {
            network,
            projection: Arc::new(projection),
            sessions: Mutex::new(HashMap::new()),
        }
    }

    pub fn topology_epoch(&self) -> u64 {
        self.projection.topology_epoch()
    }

    pub async fn ensure_session(
        &self,
        validator_id: ValidatorID,
    ) -> Result<PersistentQuicSession, ILCConsensusError> {
        {
            let sessions = self.sessions.lock().await;
            if let Some(session) = sessions.get(&validator_id.0) {
                if session.topology_epoch == self.projection.topology_epoch()
                    && session.connection.close_reason().is_none()
                {
                    return Ok(session.clone());
                }
            }
        }

        let mut last_error: Option<ILCConsensusError> = None;

        if let Some(edge) = self.projection.direct_endpoint(validator_id) {
            match self.connect_edge(edge).await {
                Ok(connection) => {
                    let session = PersistentQuicSession {
                        validator_id,
                        topology_epoch: self.projection.topology_epoch(),
                        path: SessionPath::DirectQuic,
                        connection,
                    };
                    self.sessions
                        .lock()
                        .await
                        .insert(validator_id.0, session.clone());
                    return Ok(session);
                }
                Err(e) => {
                    last_error = Some(e);
                }
            }
        }

        if let Some(edge) = self.projection.relay_endpoint(validator_id) {
            match self.connect_edge(edge).await {
                Ok(connection) => {
                    let session = PersistentQuicSession {
                        validator_id,
                        topology_epoch: self.projection.topology_epoch(),
                        path: SessionPath::Cdl078RelayFallback,
                        connection,
                    };
                    self.sessions
                        .lock()
                        .await
                        .insert(validator_id.0, session.clone());
                    return Ok(session);
                }
                Err(e) => {
                    last_error = Some(e);
                }
            }
        }

        Err(last_error.unwrap_or_else(|| {
            ILCConsensusError::Other(format!(
                "no QUIC endpoint projection entry for validator_id={}",
                validator_id.0
            ))
        }))
    }

    pub async fn transmit_persistent(
        &self,
        validator_id: ValidatorID,
        envelope: GossipEnvelope,
    ) -> Result<SessionPath, ILCConsensusError> {
        let session = self.ensure_session(validator_id).await?;
        let (send, _recv) = tokio::time::timeout(
            tokio::time::Duration::from_millis(IO_TIMEOUT_MS),
            session.connection.open_bi(),
        )
        .await
        .map_err(|_| {
            ILCConsensusError::Other(format!(
                "persistent open_bi to validator_id={} timed out",
                validator_id.0
            ))
        })?
        .map_err(|e| ILCConsensusError::Other(format!("persistent open_bi error: {}", e)))?;
        self.network.transmit(send, envelope).await?;
        Ok(session.path)
    }

    async fn connect_edge(&self, edge: &QuicEndpointEdge) -> Result<Connection, ILCConsensusError> {
        let connecting = self
            .network
            .endpoint
            .connect(edge.addr, &edge.server_name)
            .map_err(|e| ILCConsensusError::Other(format!("QUIC connect error: {}", e)))?;

        tokio::time::timeout(
            tokio::time::Duration::from_millis(PHASE_1386C_CONNECT_TIMEOUT_MS),
            connecting,
        )
        .await
        .map_err(|_| {
            ILCConsensusError::Other(format!(
                "QUIC connect to validator_id={} timed out via {:?}",
                edge.validator_id.0, edge.endpoint_kind
            ))
        })?
        .map_err(|e| ILCConsensusError::Other(format!("QUIC connection error: {}", e)))
    }
}

pub fn projection_source_rejects_write_path_1386c(source: &str) -> Result<(), ILCConsensusError> {
    let forbidden = [
        "fn set_",
        "fn update_",
        "fn insert_",
        "fn delete_",
        "fn write_",
        "pub fn set_",
        "pub fn update_",
        "pub fn insert_",
        "pub fn delete_",
        "pub fn write_",
    ];

    for needle in forbidden {
        if source.contains(needle) {
            return Err(ILCConsensusError::Other(format!(
                "write_path_projection_rejected_phase_1386c: forbidden projection method '{}'",
                needle.trim()
            )));
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::network::{GossipEnvelope, GossipMessage};
    use std::collections::HashMap;
    use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
    use tokio::time::Duration;

    fn generate_ephemeral_cert() -> (Vec<u8>, Vec<u8>) {
        let rcgen::CertifiedKey { cert, key_pair } =
            rcgen::generate_simple_self_signed(vec!["localhost".into()]).unwrap();
        (cert.der().to_vec(), key_pair.serialize_der())
    }

    fn mock_socket() -> SocketAddr {
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0))
    }

    fn endpoint_edge(
        validator_id: u32,
        topology_epoch: u64,
        endpoint_kind: EndpointKind,
        addr: SocketAddr,
    ) -> QuicEndpointEdge {
        QuicEndpointEdge {
            validator_id: ValidatorID(validator_id),
            topology_epoch,
            endpoint_kind,
            addr,
            server_name: "localhost".to_string(),
            protocol_version: "ilc-quic-consensus-v1".to_string(),
            signer_agent_id: format!("agent-{}", validator_id),
            signature_ref: format!("sig-ref-{}", validator_id),
        }
    }

    async fn accept_one_missing_epoch_sync(
        server_node: Arc<PeerNetwork>,
    ) -> Result<(), ILCConsensusError> {
        let incoming = server_node
            .endpoint
            .accept()
            .await
            .ok_or_else(|| ILCConsensusError::Other("server endpoint closed".into()))?;
        let connection = incoming
            .await
            .map_err(|e| ILCConsensusError::Other(format!("server accept failed: {}", e)))?;
        let (_send, recv) = connection
            .accept_bi()
            .await
            .map_err(|e| ILCConsensusError::Other(format!("server accept_bi failed: {}", e)))?;
        let envelope = server_node.receive(&connection, recv).await?;
        match envelope.payload {
            GossipMessage::MissingEpochSync {
                latest_contiguous_epoch,
            } if latest_contiguous_epoch == 0 => Ok(()),
            _ => Err(ILCConsensusError::Other("unexpected gossip payload".into())),
        }
    }

    #[tokio::test]
    async fn test_persistent_quic_sessions_1386c() {
        let (server_cert, server_key) = generate_ephemeral_cert();
        let (client_cert, client_key) = generate_ephemeral_cert();

        let mut server_peers = HashMap::new();
        server_peers.insert(2, client_cert.clone());

        let mut client_peers = HashMap::new();
        client_peers.insert(1, server_cert.clone());

        let direct_server = Arc::new(
            PeerNetwork::new_server(
                mock_socket(),
                server_peers.clone(),
                server_cert.clone(),
                server_key.clone(),
            )
            .unwrap(),
        );
        let direct_addr = direct_server.endpoint.local_addr().unwrap();
        let client_node = Arc::new(
            PeerNetwork::new_client(
                mock_socket(),
                client_peers.clone(),
                client_cert.clone(),
                client_key.clone(),
            )
            .unwrap(),
        );

        let projection = EndpointProjection::rebuild_from_signed_edges(
            14,
            "snapshot-direct".to_string(),
            vec![endpoint_edge(1, 14, EndpointKind::Direct, direct_addr)],
        )
        .unwrap();
        let manager = PersistentQuicSessionManager::new(Arc::clone(&client_node), projection);

        let direct_server_task =
            tokio::spawn(accept_one_missing_epoch_sync(Arc::clone(&direct_server)));
        let env = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(2),
            payload: GossipMessage::MissingEpochSync {
                latest_contiguous_epoch: 0,
            },
        };
        let path = manager
            .transmit_persistent(ValidatorID(1), env)
            .await
            .unwrap();
        assert_eq!(path, SessionPath::DirectQuic);
        tokio::time::timeout(Duration::from_secs(2), direct_server_task)
            .await
            .unwrap()
            .unwrap()
            .unwrap();

        let reused = manager.ensure_session(ValidatorID(1)).await.unwrap();
        assert_eq!(reused.path, SessionPath::DirectQuic);
        assert_eq!(reused.topology_epoch, 14);

        let (relay_server_cert, relay_server_key) = generate_ephemeral_cert();
        let (relay_client_cert, relay_client_key) = generate_ephemeral_cert();

        let mut relay_server_peers = HashMap::new();
        relay_server_peers.insert(2, relay_client_cert.clone());

        let mut relay_client_peers = HashMap::new();
        relay_client_peers.insert(1, relay_server_cert.clone());

        let relay_server = Arc::new(
            PeerNetwork::new_server(
                mock_socket(),
                relay_server_peers,
                relay_server_cert,
                relay_server_key,
            )
            .unwrap(),
        );
        let relay_addr = relay_server.endpoint.local_addr().unwrap();
        let relay_client = Arc::new(
            PeerNetwork::new_client(
                mock_socket(),
                relay_client_peers,
                relay_client_cert,
                relay_client_key,
            )
            .unwrap(),
        );
        let unreachable_direct = SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 9));
        let relay_projection = EndpointProjection::rebuild_from_signed_edges(
            15,
            "snapshot-relay".to_string(),
            vec![
                endpoint_edge(1, 15, EndpointKind::Direct, unreachable_direct),
                endpoint_edge(1, 15, EndpointKind::Relay, relay_addr),
            ],
        )
        .unwrap();
        let relay_manager =
            PersistentQuicSessionManager::new(Arc::clone(&relay_client), relay_projection);

        let relay_server_task =
            tokio::spawn(accept_one_missing_epoch_sync(Arc::clone(&relay_server)));
        let relay_env = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(2),
            payload: GossipMessage::MissingEpochSync {
                latest_contiguous_epoch: 0,
            },
        };
        let relay_path = relay_manager
            .transmit_persistent(ValidatorID(1), relay_env)
            .await
            .unwrap();
        assert_eq!(relay_path, SessionPath::Cdl078RelayFallback);
        tokio::time::timeout(Duration::from_secs(2), relay_server_task)
            .await
            .unwrap()
            .unwrap()
            .unwrap();
    }

    #[test]
    fn test_write_path_projection_rejected_1386c() {
        let good_projection_source =
            "impl EndpointProjection { pub fn rebuild_from_signed_edges() {} pub fn direct_endpoint(&self) {} }";
        assert!(projection_source_rejects_write_path_1386c(good_projection_source).is_ok());

        let bad_projection_source =
            "impl EndpointProjection { pub fn update_endpoint(&mut self) {} }";
        let err = projection_source_rejects_write_path_1386c(bad_projection_source)
            .expect_err("write/update/set/insert/delete projection methods must be rejected");
        assert!(format!("{:?}", err).contains("write_path_projection_rejected_phase_1386c"));
    }

    #[test]
    fn test_projection_rebuild_rejects_stale_epoch_1386c() {
        let stale_edge = endpoint_edge(1, 13, EndpointKind::Direct, mock_socket());
        let err = EndpointProjection::rebuild_from_signed_edges(
            14,
            "snapshot-stale".to_string(),
            vec![stale_edge],
        )
        .expect_err("stale topology-epoch projections must be rejected");
        assert!(format!("{:?}", err).contains("stale endpoint edge"));
    }
}
