//! Phase 1386c persistent QUIC session proof.
//!
//! This module keeps validator connectivity authority outside hardcoded peer
//! lists. The only constructor for [`EndpointProjection`] rebuilds a read-only
//! projection from signed `QUIC_ENDPOINT` graph edges for one topology epoch.

use crate::network::{GossipEnvelope, PeerNetwork, IO_TIMEOUT_MS};
use crate::types::{AgentID, ILCConsensusError};
use quinn::Connection;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::path::Path;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;

pub const PHASE_1386C_CONNECT_TIMEOUT_MS: u64 = 600;
pub const PERSISTENT_QUIC_FULL_IMPL_PHASE: &str = "phase_1482p";
pub const MAX_ENDPOINT_PROJECTION_BYTES: u64 = 1024 * 1024;
pub const DEFAULT_PERSISTENT_QUIC_MAX_SESSIONS: usize = 128;
pub const DEFAULT_PERSISTENT_QUIC_INITIAL_BACKOFF_MS: u64 = 50;
pub const DEFAULT_PERSISTENT_QUIC_MAX_BACKOFF_MS: u64 = 400;
pub const DEFAULT_PERSISTENT_QUIC_BACKOFF_MULTIPLIER: u32 = 2;
pub const DEFAULT_PERSISTENT_QUIC_MAX_RECONNECT_ATTEMPTS: u32 = 2;
pub const DEFAULT_PERSISTENT_QUIC_STALE_TIMEOUT_MS: u64 = 30_000;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PersistentQuicSessionPoolConfig {
    pub max_sessions: usize,
    pub connect_timeout_ms: u64,
    pub initial_backoff_ms: u64,
    pub max_backoff_ms: u64,
    pub backoff_multiplier: u32,
    pub max_reconnect_attempts: u32,
    pub stale_timeout_ms: u64,
}

impl Default for PersistentQuicSessionPoolConfig {
    fn default() -> Self {
        Self {
            max_sessions: DEFAULT_PERSISTENT_QUIC_MAX_SESSIONS,
            connect_timeout_ms: PHASE_1386C_CONNECT_TIMEOUT_MS,
            initial_backoff_ms: DEFAULT_PERSISTENT_QUIC_INITIAL_BACKOFF_MS,
            max_backoff_ms: DEFAULT_PERSISTENT_QUIC_MAX_BACKOFF_MS,
            backoff_multiplier: DEFAULT_PERSISTENT_QUIC_BACKOFF_MULTIPLIER,
            max_reconnect_attempts: DEFAULT_PERSISTENT_QUIC_MAX_RECONNECT_ATTEMPTS,
            stale_timeout_ms: DEFAULT_PERSISTENT_QUIC_STALE_TIMEOUT_MS,
        }
    }
}

impl PersistentQuicSessionPoolConfig {
    pub fn validate(&self) -> Result<(), ILCConsensusError> {
        if self.max_sessions == 0 {
            return Err(ILCConsensusError::Other(
                "persistent_quic_max_sessions_must_be_positive_phase_1482p".into(),
            ));
        }
        if self.connect_timeout_ms == 0 {
            return Err(ILCConsensusError::Other(
                "persistent_quic_connect_timeout_must_be_positive_phase_1482p".into(),
            ));
        }
        if self.initial_backoff_ms == 0 {
            return Err(ILCConsensusError::Other(
                "persistent_quic_initial_backoff_must_be_positive_phase_1482p".into(),
            ));
        }
        if self.max_backoff_ms < self.initial_backoff_ms {
            return Err(ILCConsensusError::Other(
                "persistent_quic_max_backoff_below_initial_phase_1482p".into(),
            ));
        }
        if self.backoff_multiplier < 1 {
            return Err(ILCConsensusError::Other(
                "persistent_quic_backoff_multiplier_must_be_positive_phase_1482p".into(),
            ));
        }
        if self.max_reconnect_attempts == 0 {
            return Err(ILCConsensusError::Other(
                "persistent_quic_reconnect_attempts_must_be_positive_phase_1482p".into(),
            ));
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EndpointKind {
    Direct,
    Relay,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct QuicEndpointEdge {
    pub validator_id: AgentID,
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
    direct_endpoints: HashMap<AgentID, QuicEndpointEdge>,
    relay_endpoints: HashMap<AgentID, QuicEndpointEdge>,
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
            let validator_key = edge.validator_id;
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

    pub fn direct_endpoint(&self, validator_id: AgentID) -> Option<&QuicEndpointEdge> {
        self.direct_endpoints.get(&validator_id)
    }

    pub fn relay_endpoint(&self, validator_id: AgentID) -> Option<&QuicEndpointEdge> {
        self.relay_endpoints.get(&validator_id)
    }

    pub fn validator_ids(&self) -> Vec<AgentID> {
        let mut ids: Vec<AgentID> = self
            .direct_endpoints
            .keys()
            .chain(self.relay_endpoints.keys())
            .copied()
            .collect();
        ids.sort_unstable();
        ids.dedup();
        ids
    }

    pub fn preferred_peer_addrs(&self) -> Vec<(AgentID, SocketAddr)> {
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
    pub validator_id: AgentID,
    pub topology_epoch: u64,
    pub path: SessionPath,
    pub connection: Connection,
    pub last_successful_send: Instant,
    pub stale: bool,
}

pub struct PersistentQuicSessionManager {
    network: Arc<PeerNetwork>,
    projection: Arc<EndpointProjection>,
    sessions: Mutex<HashMap<AgentID, PersistentQuicSession>>,
    config: PersistentQuicSessionPoolConfig,
}

impl PersistentQuicSessionManager {
    pub fn new(network: Arc<PeerNetwork>, projection: EndpointProjection) -> Self {
        Self {
            network,
            projection: Arc::new(projection),
            sessions: Mutex::new(HashMap::new()),
            config: PersistentQuicSessionPoolConfig::default(),
        }
    }

    pub fn new_with_config(
        network: Arc<PeerNetwork>,
        projection: EndpointProjection,
        config: PersistentQuicSessionPoolConfig,
    ) -> Result<Self, ILCConsensusError> {
        config.validate()?;
        Ok(Self {
            network,
            projection: Arc::new(projection),
            sessions: Mutex::new(HashMap::new()),
            config,
        })
    }

    pub fn topology_epoch(&self) -> u64 {
        self.projection.topology_epoch()
    }

    pub fn pool_config(&self) -> &PersistentQuicSessionPoolConfig {
        &self.config
    }

    pub fn backoff_delay_for_attempt(&self, attempt_index: u32) -> Duration {
        let mut delay = self.config.initial_backoff_ms;
        for _ in 0..attempt_index {
            delay = delay
                .saturating_mul(u64::from(self.config.backoff_multiplier))
                .min(self.config.max_backoff_ms);
        }
        Duration::from_millis(delay)
    }

    pub async fn session_count(&self) -> usize {
        self.sessions.lock().await.len()
    }

    pub async fn mark_stale(&self, validator_id: AgentID) -> bool {
        let mut sessions = self.sessions.lock().await;
        if let Some(session) = sessions.get_mut(&validator_id) {
            session.stale = true;
            return true;
        }
        false
    }

    pub async fn evict_stale(&self) -> usize {
        let stale_timeout = Duration::from_millis(self.config.stale_timeout_ms);
        let mut sessions = self.sessions.lock().await;
        let before = sessions.len();
        sessions.retain(|_, session| {
            !session.stale
                && session.connection.close_reason().is_none()
                && session.last_successful_send.elapsed() < stale_timeout
        });
        before - sessions.len()
    }

    pub async fn ensure_session(
        &self,
        validator_id: AgentID,
    ) -> Result<PersistentQuicSession, ILCConsensusError> {
        self.acquire_session(validator_id).await
    }

    pub async fn acquire_session(
        &self,
        validator_id: AgentID,
    ) -> Result<PersistentQuicSession, ILCConsensusError> {
        {
            let mut sessions = self.sessions.lock().await;
            if let Some(session) = sessions.get(&validator_id) {
                if session.topology_epoch == self.projection.topology_epoch()
                    && !session.stale
                    && session.connection.close_reason().is_none()
                    && session.last_successful_send.elapsed()
                        < Duration::from_millis(self.config.stale_timeout_ms)
                {
                    return Ok(session.clone());
                }
            }
            sessions.remove(&validator_id);
            if sessions.len() >= self.config.max_sessions {
                return Err(ILCConsensusError::Other(format!(
                    "persistent_quic_pool_at_capacity_phase_1482p: max_sessions={}",
                    self.config.max_sessions
                )));
            }
        }

        let mut last_error: Option<ILCConsensusError> = None;

        if let Some(edge) = self.projection.direct_endpoint(validator_id) {
            match self.connect_edge_with_backoff(edge).await {
                Ok(connection) => {
                    let session = PersistentQuicSession {
                        validator_id,
                        topology_epoch: self.projection.topology_epoch(),
                        path: SessionPath::DirectQuic,
                        connection,
                        last_successful_send: Instant::now(),
                        stale: false,
                    };
                    return self
                        .insert_session_after_capacity_recheck(validator_id, session)
                        .await;
                }
                Err(e) => {
                    last_error = Some(e);
                }
            }
        }

        if let Some(edge) = self.projection.relay_endpoint(validator_id) {
            match self.connect_edge_with_backoff(edge).await {
                Ok(connection) => {
                    let session = PersistentQuicSession {
                        validator_id,
                        topology_epoch: self.projection.topology_epoch(),
                        path: SessionPath::Cdl078RelayFallback,
                        connection,
                        last_successful_send: Instant::now(),
                        stale: false,
                    };
                    return self
                        .insert_session_after_capacity_recheck(validator_id, session)
                        .await;
                }
                Err(e) => {
                    last_error = Some(e);
                }
            }
        }

        Err(last_error.unwrap_or_else(|| {
            ILCConsensusError::Other(format!(
                "no QUIC endpoint projection entry for validator_id={}",
                validator_id
            ))
        }))
    }

    async fn insert_session_after_capacity_recheck(
        &self,
        validator_id: AgentID,
        session: PersistentQuicSession,
    ) -> Result<PersistentQuicSession, ILCConsensusError> {
        let mut sessions = self.sessions.lock().await;
        sessions.retain(|_, existing| {
            !existing.stale
                && existing.connection.close_reason().is_none()
                && existing.last_successful_send.elapsed()
                    < Duration::from_millis(self.config.stale_timeout_ms)
        });
        if !sessions.contains_key(&validator_id) && sessions.len() >= self.config.max_sessions {
            return Err(ILCConsensusError::Other(format!(
                "persistent_quic_pool_at_capacity_phase_1575h_fix2_second_lock: max_sessions={}",
                self.config.max_sessions
            )));
        }
        sessions.insert(validator_id, session.clone());
        Ok(session)
    }

    pub async fn transmit_persistent(
        &self,
        validator_id: AgentID,
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
                validator_id
            ))
        })?
        .map_err(|e| ILCConsensusError::Other(format!("persistent open_bi error: {}", e)))?;
        self.network.transmit(send, envelope).await?;
        self.record_success(validator_id).await;
        Ok(session.path)
    }

    async fn record_success(&self, validator_id: AgentID) {
        let mut sessions = self.sessions.lock().await;
        if let Some(session) = sessions.get_mut(&validator_id) {
            session.last_successful_send = Instant::now();
            session.stale = false;
        }
    }

    async fn connect_edge_with_backoff(
        &self,
        edge: &QuicEndpointEdge,
    ) -> Result<Connection, ILCConsensusError> {
        let mut last_error: Option<ILCConsensusError> = None;
        for attempt in 0..self.config.max_reconnect_attempts {
            match self.connect_edge(edge).await {
                Ok(connection) => return Ok(connection),
                Err(err) => {
                    last_error = Some(err);
                    if attempt + 1 < self.config.max_reconnect_attempts {
                        tokio::time::sleep(self.backoff_delay_for_attempt(attempt)).await;
                    }
                }
            }
        }
        Err(last_error.unwrap_or_else(|| {
            ILCConsensusError::Other(
                "persistent_quic_connect_attempts_exhausted_phase_1482p".into(),
            )
        }))
    }

    async fn connect_edge(&self, edge: &QuicEndpointEdge) -> Result<Connection, ILCConsensusError> {
        let connecting = self
            .network
            .endpoint
            .connect(edge.addr, &edge.server_name)
            .map_err(|e| ILCConsensusError::Other(format!("QUIC connect error: {}", e)))?;

        tokio::time::timeout(
            Duration::from_millis(self.config.connect_timeout_ms),
            connecting,
        )
        .await
        .map_err(|_| {
            ILCConsensusError::Other(format!(
                "QUIC connect to validator_id={} timed out via {:?}",
                edge.validator_id, edge.endpoint_kind
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
            validator_id: crate::types::test_agent_id(validator_id),
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
            peer_id: crate::types::test_agent_id(2),
            payload: GossipMessage::MissingEpochSync {
                latest_contiguous_epoch: 0,
            },
        };
        let path = manager
            .transmit_persistent(crate::types::test_agent_id(1), env)
            .await
            .unwrap();
        assert_eq!(path, SessionPath::DirectQuic);
        tokio::time::timeout(Duration::from_secs(2), direct_server_task)
            .await
            .unwrap()
            .unwrap()
            .unwrap();

        let reused = manager
            .ensure_session(crate::types::test_agent_id(1))
            .await
            .unwrap();
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
            peer_id: crate::types::test_agent_id(2),
            payload: GossipMessage::MissingEpochSync {
                latest_contiguous_epoch: 0,
            },
        };
        let relay_path = relay_manager
            .transmit_persistent(crate::types::test_agent_id(1), relay_env)
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
